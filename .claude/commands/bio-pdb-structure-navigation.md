# bio-pdb-structure-navigation

> Navigate protein structure hierarchy using Biopython Bio.PDB SMCRA model. Use when accessing models, chains, residues, and atoms, iterating over structure levels, or extracting sequences from PDB files.

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structure Navigation

**"Access residues and atoms in a PDB structure"** → Navigate the Structure-Model-Chain-Residue-Atom hierarchy to iterate over components, extract sequences, and access atomic coordinates.
- Python: `structure[0]['A'][100]['CA'].get_vector()` for direct access

Navigate the Structure-Model-Chain-Residue-Atom (SMCRA) hierarchy to access and iterate over structure components.

## Required Imports

```python
from Bio.PDB import PDBParser, PPBuilder, Selection
from Bio.Data.PDBData import protein_letters_3to1
```

## SMCRA Hierarchy

```
Structure
    |
    +-- Model (0, 1, ...)      # NMR ensembles, crystal asymmetric unit
          |
          +-- Chain (A, B, ...) # Polypeptide chains, ligands
                |
                +-- Residue     # Amino acids, nucleotides, hetero groups
                      |
                      +-- Atom  # Individual atoms
```

## Accessing Hierarchy Levels

```python
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Access by index/ID
model = structure[0]          # First model
chain = model['A']            # Chain A
residue = chain[100]          # Residue 100 (simple numbering)
residue = chain[(' ', 100, ' ')]  # Full residue ID (hetfield, resseq, icode)
atom = residue['CA']          # C-alpha atom
```

## Iterating Over Structure

```python
# Iterate all levels
for model in structure:
    for chain in model:
        for residue in chain:
            for atom in residue:
                print(f'{chain.id}:{residue.id[1]}:{atom.name}')

# Shortcut iterators (all levels below current)
for chain in structure.get_chains():
    print(f'Chain: {chain.id}')

for residue in structure.get_residues():
    print(f'Residue: {residue.resname}')

for atom in structure.get_atoms():
    print(f'Atom: {atom.name} at {atom.coord}')
```

## Residue Identification

```python
# Residue ID is a tuple: (hetfield, resseq, icode)
for residue in chain:
    hetfield, resseq, icode = residue.id
    print(f'Residue {resseq}{icode}: {residue.resname}')

# hetfield values:
#   ' '  - standard amino acid
#   'W'  - water
#   'H_xxx' - hetero residue (ligand, modified residue)

# Filter standard residues only
standard_residues = [r for r in chain if r.id[0] == ' ']

# Filter water
waters = [r for r in chain if r.id[0] == 'W']

# Filter hetero atoms (ligands)
hetero = [r for r in chain if r.id[0].startswith('H_')]
```

## Atom Properties

```python
for atom in residue:
    print(f'Name: {atom.name}')
    print(f'Element: {atom.element}')
    print(f'Coordinates: {atom.coord}')
    print(f'B-factor: {atom.bfactor}')
    print(f'Occupancy: {atom.occupancy}')
    print(f'Full ID: {atom.full_id}')
    print(f'Serial number: {atom.serial_number}')
```

## Getting Full Identifiers

```python
# Full hierarchical ID from any entity
atom = structure[0]['A'][100]['CA']
print(atom.get_full_id())
# ('protein', 0, 'A', (' ', 100, ' '), ('CA', ' '))

# Components: (structure_id, model_id, chain_id, residue_id, atom_id)
```

## Checking for Children

```python
# Check if entity has child
if chain.has_id(100):
    residue = chain[100]

# Check if residue has atom
if residue.has_id('CA'):
    ca = residue['CA']

# Get list of all children
chains = structure[0].get_list()
residues = chain.get_list()
atoms = residue.get_list()
```

## Getting Parent Entity

```python
# Navigate up hierarchy
atom = structure[0]['A'][100]['CA']

residue = atom.get_parent()
chain = residue.get_parent()
model = chain.get_parent()
structure = model.get_parent()
```

## Extracting Polypeptide Sequences

```python
from Bio.PDB import PDBParser, PPBuilder

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

ppb = PPBuilder()
for pp in ppb.build_peptides(structure):
    seq = pp.get_sequence()
    print(f'Polypeptide: {seq}')
    print(f'Length: {len(seq)}')

# Get all sequences as list
sequences = [pp.get_sequence() for pp in ppb.build_peptides(structure)]
```

## Using CaPPBuilder for Broken Chains

```python
from Bio.PDB import CaPPBuilder

# Use when backbone is incomplete
# Connects residues if CA atoms are within 4.3 Angstroms
ppb = CaPPBuilder()
for pp in ppb.build_peptides(structure):
    print(f'Fragment: {pp.get_sequence()}')
```

## Converting Residue Names

```python
from Bio.Data.PDBData import protein_letters_3to1

# Three-letter to one-letter conversion
three_letter = 'ALA'
one_letter = protein_letters_3to1.get(three_letter, 'X')
print(f'{three_letter} -> {one_letter}')  # ALA -> A

# Build sequence manually
sequence = ''
for residue in chain:
    if residue.id[0] == ' ':  # Standard residue
        code = protein_letters_3to1.get(residue.resname, 'X')
        sequence += code
print(f'Sequence: {sequence}')
```

## Using Selection.unfold_entities

```python
from Bio.PDB import Selection

# Extract entities at specific level
# Codes: S=structure, M=model, C=chain, R=residue, A=atom

# Get all residues from structure
residues = Selection.unfold_entities(structure, 'R')
print(f'Total residues: {len(residues)}')

# Get all atoms from a chain
atoms = Selection.unfold_entities(chain, 'A')
print(f'Atoms in chain: {len(atoms)}')

# Get all chains from model
chains = Selection.unfold_entities(model, 'C')
```

## Handling Disordered Atoms

```python
# Check for disorder
if atom.is_disordered():
    print(f'Atom {atom.name} has multiple conformations')
    print(f'Alt locations: {atom.disordered_get_id_list()}')

    # Select specific conformation
    atom.disordered_select('A')
    print(f'Coord for alt A: {atom.coord}')

    # Get all conformations
    for altloc in atom.disordered_get_id_list():
        atom.disordered_select(altloc)
        print(f'  {altloc}: {atom.coord}')

# Get unpacked list (all conformations)
all_atoms = atom.disordered_get_list()
```

## Handling Disordered Residues

```python
# Point mutations at same position
if residue.is_disordered():
    print(f'Disordered residue at {residue.id}')
    names = residue.disordered_get_id_list()
    print(f'Alternative residues: {names}')

    # Select specific residue type
    residue.disordered_select('ALA')
```

## Finding Specific Atoms

```python
# Get backbone atoms
backbone_names = ['N', 'CA', 'C', 'O']
for residue in chain:
    backbone = [residue[name] for name in backbone_names if residue.has_id(name)]

# Get all C-alpha atoms
ca_atoms = [r['CA'] for r in structure.get_residues() if r.has_id('CA')]
print(f'Found {len(ca_atoms)} CA atoms')

# Get sidechain atoms
for residue in chain:
    sidechain = [a for a in residue if a.name not in ['N', 'CA', 'C', 'O']]
```

## Filtering by Residue Type

```python
# Get only amino acids
amino_acids = [r for r in chain if r.id[0] == ' ']

# Get specific amino acid types
arginines = [r for r in chain if r.resname == 'ARG']
charged = [r for r in chain if r.resname in ['ARG', 'LYS', 'ASP', 'GLU']]

# Get hetero atoms
ligands = [r for r in chain if r.id[0].startswith('H_')]
for lig in ligands:
    print(f'Ligand: {lig.resname} at position {lig.id[1]}')
```

## Counting Entities

```python
# Count at each level
n_models = len(list(structure.get_models()))
n_chains = len(list(structure.get_chains()))
n_residues = len(list(structure.get_residues()))
n_atoms = len(list(structure.get_atoms()))

print(f'Models: {n_models}, Chains: {n_chains}')
print(f'Residues: {n_residues}, Atoms: {n_atoms}')

# Count per chain
for chain in structure.get_chains():
    n_res = len([r for r in chain if r.id[0] == ' '])
    print(f'Chain {chain.id}: {n_res} amino acids')
```

## Working with NMR Ensembles

```python
# NMR structures have multiple models
parser = PDBParser(QUIET=True)
structure = parser.get_structure('nmr', 'nmr_structure.pdb')

n_models = len(list(structure.get_models()))
print(f'NMR ensemble with {n_models} conformers')

# Iterate over models
for model in structure:
    # Each model is a separate conformation
    ca_coords = [r['CA'].coord for r in model.get_residues() if r.has_id('CA')]
    print(f'Model {model.id}: {len(ca_coords)} CA atoms')
```

## Related Skills

- structure-io - Parse and write structure files
- geometric-analysis - Measure distances, angles, RMSD
- structure-modification - Modify coordinates and properties
- sequence-manipulation/seq-objects - Work with extracted sequences
