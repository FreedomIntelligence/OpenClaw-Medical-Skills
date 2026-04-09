# bio-virtual-screening

> Performs structure-based virtual screening using AutoDock Vina 1.2 for molecular docking. Prepares receptor PDBQT files, generates ligand conformers, defines binding site boxes, and ranks compounds by predicted binding affinity. Use when screening chemical libraries against a protein structure to find potential binders.

## Version Compatibility

Reference examples tested with: AutoDock Vina 1.2+, RDKit 2024.03+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Virtual Screening

**"Dock my compound library against a protein target"** → Perform structure-based virtual screening by preparing a receptor PDBQT, generating ligand conformers, defining a binding site box, and scoring each compound by predicted binding affinity using AutoDock Vina.
- Python: `vina.Vina()` for docking, `AllChem.EmbedMolecule()` (RDKit) for conformer generation

Screen compound libraries against protein targets using molecular docking.

## Receptor Preparation

**Goal:** Prepare a protein structure for molecular docking.

**Approach:** Remove waters and heteroatoms from the PDB, add hydrogens at physiological pH, assign Gasteiger charges, and convert to PDBQT format using Open Babel.

```python
from rdkit import Chem
from rdkit.Chem import AllChem
import subprocess

def prepare_receptor(pdb_file, output_pdbqt, remove_waters=True, add_hydrogens=True):
    '''
    Prepare protein for docking.
    Steps: Remove waters -> Add hydrogens -> Assign charges -> PDBQT
    '''
    # Read PDB
    with open(pdb_file) as f:
        lines = f.readlines()

    # Remove waters if requested
    if remove_waters:
        lines = [l for l in lines if not l.startswith(('HETATM', 'CONECT'))
                 or 'HOH' not in l]

    # Write cleaned PDB
    clean_pdb = pdb_file.replace('.pdb', '_clean.pdb')
    with open(clean_pdb, 'w') as f:
        f.writelines(lines)

    # Use Open Babel for conversion (adds hydrogens and charges)
    subprocess.run([
        'obabel', clean_pdb,
        '-O', output_pdbqt,
        '-p', '7.4',  # Add hydrogens at pH 7.4
        '--partialcharge', 'gasteiger'
    ], check=True)

    return output_pdbqt
```

## Ligand Preparation

**Goal:** Convert a SMILES string into a docking-ready 3D ligand file.

**Approach:** Generate a 3D conformer with ETKDGv3, optimize geometry with MMFF, write to MOL, and convert to PDBQT with Gasteiger charges via Open Babel.

```python
from rdkit import Chem
from rdkit.Chem import AllChem

def prepare_ligand(smiles, output_pdbqt):
    '''
    Prepare ligand for docking.
    Steps: Generate 3D -> Minimize -> Assign charges -> PDBQT
    '''
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)

    # Generate 3D conformer (ETKDGv3 is default in modern RDKit)
    AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())

    # Minimize with MMFF
    AllChem.MMFFOptimizeMolecule(mol)

    # Write to MOL file
    mol_file = output_pdbqt.replace('.pdbqt', '.mol')
    Chem.MolToMolFile(mol, mol_file)

    # Convert to PDBQT with Open Babel
    subprocess.run([
        'obabel', mol_file,
        '-O', output_pdbqt,
        '--partialcharge', 'gasteiger'
    ], check=True)

    return output_pdbqt
```

## Docking with Vina

**Goal:** Dock a single ligand into a protein binding site and retrieve predicted binding affinities.

**Approach:** Initialize Vina with the receptor, set the search space around the binding site, dock with specified exhaustiveness, and extract ranked poses with energies.

```python
from vina import Vina

def dock_ligand(receptor_pdbqt, ligand_pdbqt, center, box_size, exhaustiveness=8):
    '''
    Dock a single ligand using AutoDock Vina 1.2.

    Args:
        receptor_pdbqt: Prepared receptor file
        ligand_pdbqt: Prepared ligand file
        center: (x, y, z) center of binding site
        box_size: (x, y, z) box dimensions (Angstroms)
        exhaustiveness: Search thoroughness (8=quick, 32=production, 64=thorough)
    '''
    v = Vina(sf_name='vina')
    v.set_receptor(receptor_pdbqt)
    v.set_ligand_from_file(ligand_pdbqt)

    # Define search space
    # Box size generally < 30x30x30 Angstroms
    v.compute_vina_maps(center=center, box_size=box_size)

    # Dock
    v.dock(exhaustiveness=exhaustiveness, n_poses=10)

    # Get results
    energies = v.energies()  # List of (affinity, rmsd_lb, rmsd_ub)
    poses = v.poses()  # PDBQT string of all poses

    return energies, poses

# Example usage
# center = (10.0, 20.0, 30.0)  # Binding site center
# box = (20, 20, 20)  # Box size in Angstroms
# energies, poses = dock_ligand('receptor.pdbqt', 'ligand.pdbqt', center, box)
```

## Virtual Screening Pipeline

**Goal:** Screen an entire compound library against a protein target and rank by binding affinity.

**Approach:** Prepare each ligand from SMILES, dock against the pre-computed receptor maps, save top poses, and compile results into a sorted DataFrame.

```python
import os
from pathlib import Path
from vina import Vina
import pandas as pd

def virtual_screen(receptor_pdbqt, ligand_smiles_dict, center, box_size,
                   output_dir, exhaustiveness=8, n_poses=3):
    '''
    Screen compound library against receptor.

    Args:
        receptor_pdbqt: Prepared receptor
        ligand_smiles_dict: Dict of {name: smiles}
        center: Binding site center
        box_size: Search box size
        output_dir: Directory for output files
        exhaustiveness: Search thoroughness
        n_poses: Number of poses to save per ligand
    '''
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    v = Vina(sf_name='vina')
    v.set_receptor(receptor_pdbqt)
    v.compute_vina_maps(center=center, box_size=box_size)

    results = []

    for name, smiles in ligand_smiles_dict.items():
        try:
            # Prepare ligand
            ligand_pdbqt = f'{output_dir}/{name}.pdbqt'
            prepare_ligand(smiles, ligand_pdbqt)

            # Dock
            v.set_ligand_from_file(ligand_pdbqt)
            v.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)

            energies = v.energies()
            best_affinity = energies[0][0] if energies else None

            # Save poses
            if energies:
                pose_file = f'{output_dir}/{name}_poses.pdbqt'
                v.write_poses(pose_file, n_poses=n_poses)

            results.append({
                'name': name,
                'smiles': smiles,
                'affinity_kcal_mol': best_affinity,
                'poses_file': pose_file if energies else None
            })

        except Exception as e:
            print(f'Failed for {name}: {e}')
            results.append({
                'name': name,
                'smiles': smiles,
                'affinity_kcal_mol': None,
                'error': str(e)
            })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('affinity_kcal_mol')

    return results_df
```

## Binding Site Definition

**Goal:** Define the docking search box around a protein binding site.

**Approach:** If a co-crystallized ligand is available, compute its centroid and bounding box with padding; otherwise fall back to the protein center with a default box size.

```python
def find_binding_site(receptor_pdb, ligand_pdb=None, padding=5.0):
    '''
    Define binding site from co-crystallized ligand or protein center.

    Args:
        receptor_pdb: Protein PDB file
        ligand_pdb: Optional co-crystallized ligand
        padding: Angstroms to add around ligand
    '''
    if ligand_pdb:
        # Center on ligand
        from rdkit import Chem
        mol = Chem.MolFromPDBFile(ligand_pdb)
        conf = mol.GetConformer()
        coords = [conf.GetAtomPosition(i) for i in range(mol.GetNumAtoms())]

        x = [c.x for c in coords]
        y = [c.y for c in coords]
        z = [c.z for c in coords]

        center = (sum(x)/len(x), sum(y)/len(y), sum(z)/len(z))
        box_size = (max(x)-min(x)+2*padding, max(y)-min(y)+2*padding, max(z)-min(z)+2*padding)
    else:
        # Use protein center (not recommended)
        center = (0, 0, 0)
        box_size = (30, 30, 30)

    return center, box_size
```

## Related Skills

- molecular-io - Load and convert molecules
- admet-prediction - Filter before docking
- structural-biology/structure-io - Protein structure handling
- structural-biology/modern-structure-prediction - Generate targets
