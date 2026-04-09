# bio-structural-biology-alphafold-predictions

> Access and analyze AlphaFold protein structure predictions. Use when predicted structures are needed for proteins without experimental structures, or for confidence scores (pLDDT).

## Version Compatibility

Reference examples tested with: BioPython 1.83+, matplotlib 3.8+, numpy 1.26+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# AlphaFold Predictions

**"Get the AlphaFold predicted structure for my protein"** → Download pre-computed AlphaFold structures by UniProt ID and assess prediction quality via per-residue pLDDT confidence scores.
- Python: `requests.get(f'https://alphafold.ebi.ac.uk/files/AF-{uniprot}-F1-model_v4.pdb')`

Download and analyze AlphaFold predicted protein structures from the AlphaFold Protein Structure Database.

## Download Structures

**Goal:** Retrieve pre-computed AlphaFold protein structure predictions and assess prediction quality via pLDDT confidence scores.

**Approach:** Query the AlphaFold Protein Structure Database API by UniProt accession to download PDB/CIF files, then extract per-residue pLDDT scores from B-factor columns to identify high-confidence and disordered regions.

### Single Structure by UniProt ID

```python
import requests

def download_alphafold(uniprot_id, output_dir='.'):
    '''Download AlphaFold structure for UniProt accession'''
    base_url = 'https://alphafold.ebi.ac.uk/files'
    pdb_url = f'{base_url}/AF-{uniprot_id}-F1-model_v4.pdb'
    cif_url = f'{base_url}/AF-{uniprot_id}-F1-model_v4.cif'

    response = requests.get(pdb_url)
    if response.status_code == 200:
        output_path = f'{output_dir}/AF-{uniprot_id}-F1-model_v4.pdb'
        with open(output_path, 'w') as f:
            f.write(response.text)
        return output_path
    return None

pdb_file = download_alphafold('P04637')  # Human p53
```

### Check Availability

```python
def check_alphafold_exists(uniprot_id):
    '''Check if AlphaFold prediction exists'''
    url = f'https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}'
    response = requests.get(url)
    return response.status_code == 200

if check_alphafold_exists('P04637'):
    print('AlphaFold structure available')
```

### Get Metadata

```python
def get_alphafold_info(uniprot_id):
    '''Get AlphaFold prediction metadata'''
    url = f'https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[0]
    return None

info = get_alphafold_info('P04637')
print(f"Gene: {info['gene']}")
print(f"Organism: {info['organismScientificName']}")
print(f"Model version: {info['latestVersion']}")
```

## File Types Available

Database version v4 (current as of 2025). The version number refers to the database release, not the AlphaFold model version.

| File | URL Pattern | Description |
|------|-------------|-------------|
| PDB | `AF-{id}-F1-model_v4.pdb` | Structure coordinates |
| mmCIF | `AF-{id}-F1-model_v4.cif` | Structure with metadata |
| PAE JSON | `AF-{id}-F1-predicted_aligned_error_v4.json` | Predicted aligned error |

```python
def download_pae(uniprot_id, output_dir='.'):
    '''Download PAE (predicted aligned error) matrix'''
    url = f'https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-predicted_aligned_error_v4.json'
    response = requests.get(url)
    if response.status_code == 200:
        output_path = f'{output_dir}/AF-{uniprot_id}-F1-pae.json'
        with open(output_path, 'w') as f:
            f.write(response.text)
        return output_path
    return None
```

## Analyze pLDDT Confidence Scores

### Extract from PDB B-factors

AlphaFold stores pLDDT scores in the B-factor column.

```python
from Bio.PDB import PDBParser

def extract_plddt(pdb_file):
    '''Extract pLDDT confidence scores from AlphaFold PDB'''
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('protein', pdb_file)

    residue_plddt = {}
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.id[0] == ' ':  # Standard residue
                    ca = residue['CA'] if 'CA' in residue else list(residue.get_atoms())[0]
                    residue_plddt[residue.id[1]] = ca.get_bfactor()
    return residue_plddt

plddt = extract_plddt('AF-P04637-F1-model_v4.pdb')
avg_plddt = sum(plddt.values()) / len(plddt)
print(f'Average pLDDT: {avg_plddt:.1f}')
```

### Confidence Interpretation

| pLDDT | Confidence | Interpretation |
|-------|------------|----------------|
| >90 | Very high | High accuracy, can be used as experimental |
| 70-90 | Confident | Good backbone, may have sidechain errors |
| 50-70 | Low | Caution, may be disordered |
| <50 | Very low | Likely disordered or wrong |

### Plot pLDDT per Residue

```python
import matplotlib.pyplot as plt

def plot_plddt(plddt_dict, output='plddt_plot.png'):
    residues = sorted(plddt_dict.keys())
    scores = [plddt_dict[r] for r in residues]

    plt.figure(figsize=(12, 4))
    plt.fill_between(residues, scores, alpha=0.3)
    plt.plot(residues, scores)
    plt.axhline(y=70, color='orange', linestyle='--', label='Confident threshold')
    plt.axhline(y=90, color='green', linestyle='--', label='Very high threshold')
    plt.xlabel('Residue')
    plt.ylabel('pLDDT')
    plt.ylim(0, 100)
    plt.legend()
    plt.savefig(output)
    plt.close()

plot_plddt(plddt)
```

## Analyze PAE (Predicted Aligned Error)

```python
import json
import numpy as np
import matplotlib.pyplot as plt

def load_pae(pae_file):
    '''Load PAE matrix from JSON'''
    with open(pae_file) as f:
        data = json.load(f)

    # AlphaFold v4 format
    if 'predicted_aligned_error' in data[0]:
        return np.array(data[0]['predicted_aligned_error'])
    # Older format
    return np.array(data['predicted_aligned_error'])

def plot_pae(pae_matrix, output='pae_plot.png'):
    plt.figure(figsize=(8, 8))
    plt.imshow(pae_matrix, cmap='Greens_r', vmin=0, vmax=30)
    plt.colorbar(label='Expected position error (A)')
    plt.xlabel('Scored residue')
    plt.ylabel('Aligned residue')
    plt.title('Predicted Aligned Error')
    plt.savefig(output)
    plt.close()

pae = load_pae('AF-P04637-F1-pae.json')
plot_pae(pae)
```

### PAE Interpretation

- **Low PAE (green):** Residues have well-defined relative positions
- **High PAE (white):** Uncertain relative positions (flexible linkers, domains)
- **Diagonal blocks:** Distinct structural domains

## Batch Download

```python
def batch_download_alphafold(uniprot_ids, output_dir='.'):
    '''Download multiple AlphaFold structures'''
    import os
    os.makedirs(output_dir, exist_ok=True)

    results = {}
    for uid in uniprot_ids:
        pdb_file = download_alphafold(uid, output_dir)
        results[uid] = pdb_file
        if pdb_file:
            print(f'Downloaded: {uid}')
        else:
            print(f'Not found: {uid}')
    return results

ids = ['P04637', 'P53_HUMAN', 'Q9Y6K9']
files = batch_download_alphafold(ids, 'alphafold_structures')
```

## Compare with Experimental Structure

```python
from Bio.PDB import PDBParser, Superimposer

def compare_structures(alphafold_pdb, experimental_pdb):
    '''Calculate RMSD between AlphaFold and experimental structure'''
    parser = PDBParser(QUIET=True)
    af_struct = parser.get_structure('af', alphafold_pdb)
    exp_struct = parser.get_structure('exp', experimental_pdb)

    # Get CA atoms from first chain
    af_atoms = [r['CA'] for r in af_struct[0].get_residues() if 'CA' in r]
    exp_atoms = [r['CA'] for r in exp_struct[0].get_residues() if 'CA' in r]

    # Align by length (simple approach)
    min_len = min(len(af_atoms), len(exp_atoms))
    af_atoms = af_atoms[:min_len]
    exp_atoms = exp_atoms[:min_len]

    super_imposer = Superimposer()
    super_imposer.set_atoms(exp_atoms, af_atoms)
    rmsd = super_imposer.rms
    return rmsd
```

## Related Skills

- structural-biology/structure-io - Load and parse PDB/mmCIF files
- structural-biology/geometric-analysis - RMSD, superimposition
- database-access/uniprot-access - Get UniProt IDs for proteins
- structural-biology/structure-navigation - Navigate structure hierarchy
