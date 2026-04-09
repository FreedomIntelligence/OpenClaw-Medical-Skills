# bio-structural-biology-modern-structure-prediction

> Predict protein structures using modern ML models including AlphaFold3, ESMFold, Chai-1, and Boltz-1. Use when predicting structures for novel proteins, protein complexes, or when comparing predictions across multiple methods.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Modern Structure Prediction

**"Predict the structure of my protein"** → Run ML-based structure prediction using ESMFold (single-sequence, fast), AlphaFold3 (MSA-based, highest accuracy), Chai-1, or Boltz-1 and compare predictions across methods.
- Python: ESMFold API via `requests`, local ESMFold with `esm.pretrained`

Predict protein structures using state-of-the-art machine learning models. This covers cloud APIs, local installations, and interpretation of results.

## Model Comparison

| Model | Complexes | Ligands | Speed | Access |
|-------|-----------|---------|-------|--------|
| AlphaFold3 | Yes | Yes | Slow | Server only (2025) |
| ESMFold | No | No | Fast | API or local |
| Chai-1 | Yes | Yes | Moderate | Local or API |
| Boltz-1 | Yes | Yes | Moderate | Local |
| ColabFold | No* | No | Moderate | Colab/local |

*ColabFold can predict complexes with AlphaFold-Multimer.

## ESMFold (Fastest Single-Chain)

**Goal:** Predict a protein's 3D structure from its amino acid sequence using the ESMFold language model, which requires no MSA and runs in seconds.

**Approach:** Submit the sequence to the ESMFold API (or run locally with the esm library), retrieve the predicted PDB coordinates, and assess per-residue confidence via pLDDT scores in the B-factor column.

### Via ESM Atlas API

```python
import requests

def predict_esmfold(sequence):
    '''Predict structure using ESMFold API'''
    url = 'https://api.esmatlas.com/foldSequence/v1/pdb/'
    response = requests.post(url, data=sequence, timeout=300)
    if response.status_code == 200:
        return response.text
    raise Exception(f'ESMFold failed: {response.status_code}')

sequence = 'MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH'
pdb_text = predict_esmfold(sequence)
with open('predicted.pdb', 'w') as f:
    f.write(pdb_text)
```

### Local ESMFold

```python
import torch
import esm

def predict_esmfold_local(sequence, device='cuda'):
    '''Run ESMFold locally (requires ~16GB GPU memory)'''
    model = esm.pretrained.esmfold_v1()
    model = model.eval().to(device)

    with torch.no_grad():
        output = model.infer_pdb(sequence)
    return output

# Extract pLDDT from ESMFold output
def extract_esmfold_plddt(pdb_text):
    plddt = {}
    for line in pdb_text.split('\n'):
        if line.startswith('ATOM') and line[12:16].strip() == 'CA':
            resnum = int(line[22:26])
            bfactor = float(line[60:66])
            plddt[resnum] = bfactor
    return plddt
```

## AlphaFold3 (Server)

AlphaFold3 predictions via the server at alphafoldserver.com.

### Prepare Input JSON

```python
import json

def create_af3_input(sequences, job_name='prediction'):
    '''Create AlphaFold3 server input JSON'''
    entities = []
    for i, seq in enumerate(sequences):
        entities.append({
            'type': 'protein',
            'sequence': seq,
            'count': 1
        })

    job = {
        'name': job_name,
        'modelSeeds': [1],
        'sequences': entities
    }
    return json.dumps(job, indent=2)

# Single protein
input_json = create_af3_input(['MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH'])

# Protein complex
input_json = create_af3_input([
    'MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH',
    'MGHFTEEDKATITSLWGKVNVEDAGGETLGRLLVVYPWTQRFFDSFGNLSS'
])
```

### Process AF3 Results

```python
import json
from Bio.PDB import PDBParser
import numpy as np

def analyze_af3_result(result_dir):
    '''Analyze AlphaFold3 prediction results'''
    # Load summary
    with open(f'{result_dir}/summary_confidences.json') as f:
        summary = json.load(f)

    # Extract confidence metrics
    iptm = summary.get('iptm', None)  # Interface pTM (complexes)
    ptm = summary.get('ptm', None)    # Predicted TM-score
    ranking = summary.get('ranking_score', None)

    print(f'pTM: {ptm:.3f}' if ptm else 'pTM: N/A')
    print(f'ipTM: {iptm:.3f}' if iptm else 'ipTM: N/A')

    return summary
```

### AF3 Confidence Interpretation

| Metric | Range | Interpretation |
|--------|-------|----------------|
| pTM | 0-1 | Overall structure confidence |
| ipTM | 0-1 | Interface prediction quality |
| pLDDT | 0-100 | Per-residue confidence |
| PAE | 0-30A | Position error between residue pairs |

## Chai-1 (Local Open-Source)

### Installation

```bash
pip install chai-lab
```

### Basic Prediction

```python
from chai_lab.chai1 import run_inference
import numpy as np
from pathlib import Path

def predict_chai1(fasta_path, output_dir='chai_output'):
    '''Run Chai-1 structure prediction'''
    Path(output_dir).mkdir(exist_ok=True)

    candidates = run_inference(
        fasta_file=Path(fasta_path),
        output_dir=Path(output_dir),
        num_trunk_recycles=3,        # 3: Standard. Use 5+ for difficult targets.
        num_diffn_timesteps=200,     # 200: Standard. 500 for higher quality.
        seed=42,
        device='cuda:0'
    )
    return candidates

# Candidates are sorted by confidence
# candidates.cif files contain predicted structures
```

### Chai-1 with Ligands

```python
# Chai-1 supports protein-ligand complexes
# Include ligand SMILES in input FASTA with special format

def create_chai_fasta_with_ligand(protein_seq, ligand_smiles, output_file):
    '''Create Chai-1 input with protein and ligand'''
    with open(output_file, 'w') as f:
        f.write('>protein|chain_A\n')
        f.write(f'{protein_seq}\n')
        f.write('>ligand|chain_B\n')
        f.write(f'{ligand_smiles}\n')
```

## Boltz-1 (Open-Source Complex Prediction)

### Installation

```bash
pip install boltz
```

### Basic Prediction

```python
from boltz import Boltz1

def predict_boltz1(sequences, output_dir='boltz_output'):
    '''Run Boltz-1 structure prediction'''
    model = Boltz1()

    result = model.predict(
        sequences=sequences,
        output_dir=output_dir,
        recycling_steps=3,   # 3: Standard. Increase for difficult targets.
        sampling_steps=200   # 200: Standard. 500 for publication quality.
    )
    return result
```

### Boltz-1 for Complexes

```python
# Boltz-1 handles heteromeric complexes
def predict_complex_boltz(chain_sequences):
    '''Predict protein complex with Boltz-1'''
    model = Boltz1()

    result = model.predict(
        sequences=chain_sequences,  # List of sequences for each chain
        output_dir='complex_output'
    )

    # Extract interface metrics
    return result
```

## ColabFold (AlphaFold2 + MMseqs2)

### Command Line

```bash
# Install ColabFold
pip install colabfold

# Run prediction
colabfold_batch input.fasta output_dir/

# With custom templates
colabfold_batch input.fasta output_dir/ --templates

# For complexes (use : to separate chains)
# Create FASTA like: >complex\nSEQUENCE1:SEQUENCE2
```

### Python API

```python
from colabfold.batch import run_colabfold

def predict_colabfold(fasta_file, output_dir, use_templates=False):
    '''Run ColabFold prediction'''
    run_colabfold(
        input_path=fasta_file,
        result_dir=output_dir,
        use_templates=use_templates,
        num_models=5,           # 5: Standard. Use 1 for quick predictions.
        num_recycles=3,         # 3: Standard. Increase for multimers.
        model_order=[1,2,3,4,5]
    )
```

## Comparing Predictions

```python
from Bio.PDB import PDBParser, Superimposer
import numpy as np

def compare_predictions(pdb_files, labels=None):
    '''Compare multiple structure predictions'''
    parser = PDBParser(QUIET=True)
    structures = [parser.get_structure(f'model_{i}', f) for i, f in enumerate(pdb_files)]

    # Extract CA atoms from first chain
    def get_ca_atoms(struct):
        return [r['CA'] for r in struct[0].get_residues() if 'CA' in r]

    all_atoms = [get_ca_atoms(s) for s in structures]

    # Pairwise RMSD
    n = len(structures)
    rmsd_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i+1, n):
            min_len = min(len(all_atoms[i]), len(all_atoms[j]))
            super_imposer = Superimposer()
            super_imposer.set_atoms(all_atoms[i][:min_len], all_atoms[j][:min_len])
            rmsd_matrix[i,j] = rmsd_matrix[j,i] = super_imposer.rms

    return rmsd_matrix

# Compare ESMFold vs AlphaFold3 vs Chai-1
rmsd = compare_predictions(['esmfold.pdb', 'af3.pdb', 'chai1.pdb'])
print('RMSD matrix:')
print(rmsd)
```

## When to Use Each Model

| Scenario | Recommended Model |
|----------|-------------------|
| Quick single-chain prediction | ESMFold (API) |
| Highest accuracy single chain | AlphaFold3 or ColabFold |
| Protein-protein complex | AlphaFold3, Chai-1, or Boltz-1 |
| Protein-ligand complex | AlphaFold3 or Chai-1 |
| No GPU available | ESMFold API or AlphaFold3 server |
| Large-scale screening | ESMFold (local) |
| Open-source requirement | Chai-1 or Boltz-1 |

## Memory Requirements

| Model | GPU Memory | Notes |
|-------|------------|-------|
| ESMFold | ~16 GB | Sequence length dependent |
| ColabFold | ~8-16 GB | Model size dependent |
| Chai-1 | ~24 GB | Complex size dependent |
| Boltz-1 | ~24 GB | Complex size dependent |

## Related Skills

- alphafold-predictions - Download pre-computed AlphaFold structures
- structure-io - Parse and write structure files
- geometric-analysis - RMSD, superimposition, distance calculations
- structure-navigation - Navigate predicted structure hierarchy
