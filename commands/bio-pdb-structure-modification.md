# bio-pdb-structure-modification

> Modify protein structures using Biopython Bio.PDB. Use when transforming coordinates, removing atoms or residues, adding new entities, modifying B-factors and occupancies, or building structures programmatically.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structure Modification

**"Extract a chain from a PDB file"** → Remove/add atoms, residues, or chains; transform coordinates; modify B-factors and occupancies; build structures programmatically.
- Python: `Bio.PDB.PDBIO()` with `Select` subclass for filtering, `Bio.PDB.Superimposer()` for transforms

Transform coordinates, remove/add entities, modify properties, and build structures programmatically.

## Required Imports

```python
from Bio.PDB import PDBParser, PDBIO, StructureBuilder
from Bio.PDB.Structure import Structure
from Bio.PDB.Model import Model
from Bio.PDB.Chain import Chain
from Bio.PDB.Residue import Residue
from Bio.PDB.Atom import Atom
import numpy as np
```

## Transforming Coordinates

```python
from Bio.PDB import PDBParser, PDBIO
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Translate all atoms
translation = np.array([10.0, 0.0, 0.0])
for atom in structure.get_atoms():
    atom.coord = atom.coord + translation

# Save transformed structure
io = PDBIO()
io.set_structure(structure)
io.save('translated.pdb')
```

## Rotation Around Axis

```python
from Bio.PDB import PDBParser
from Bio.PDB.vectors import rotaxis
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Rotate around Z axis by 90 degrees
angle = np.radians(90)
axis = np.array([0, 0, 1])

# Get center of mass for rotation origin
coords = np.array([a.coord for a in structure.get_atoms()])
center = coords.mean(axis=0)

# Rotation matrix
cos_a = np.cos(angle)
sin_a = np.sin(angle)
rot_matrix = np.array([
    [cos_a, -sin_a, 0],
    [sin_a, cos_a, 0],
    [0, 0, 1]
])

# Apply rotation around center
for atom in structure.get_atoms():
    atom.coord = np.dot(rot_matrix, atom.coord - center) + center
```

## Applying Transformation Matrix

```python
from Bio.PDB import PDBParser
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# 4x4 transformation matrix (rotation + translation)
# From superimposition or external source
transform = np.array([
    [1.0, 0.0, 0.0, 10.0],
    [0.0, 1.0, 0.0, 5.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0]
])

rotation = transform[:3, :3]
translation = transform[:3, 3]

for atom in structure.get_atoms():
    atom.coord = np.dot(rotation, atom.coord) + translation
```

## Center Structure at Origin

```python
from Bio.PDB import PDBParser
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Calculate center
coords = np.array([a.coord for a in structure.get_atoms()])
center = coords.mean(axis=0)

# Translate to origin
for atom in structure.get_atoms():
    atom.coord = atom.coord - center
```

## Removing Atoms

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Remove hydrogens
for residue in structure.get_residues():
    atoms_to_remove = [a.id for a in residue if a.element == 'H']
    for atom_id in atoms_to_remove:
        residue.detach_child(atom_id)

io = PDBIO()
io.set_structure(structure)
io.save('no_hydrogens.pdb')
```

## Removing Residues

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Remove water molecules
for model in structure:
    for chain in model:
        residues_to_remove = [r.id for r in chain if r.id[0] == 'W']
        for res_id in residues_to_remove:
            chain.detach_child(res_id)

io = PDBIO()
io.set_structure(structure)
io.save('no_water.pdb')
```

## Removing a Chain

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Remove chain B
model = structure[0]
if model.has_id('B'):
    model.detach_child('B')

io = PDBIO()
io.set_structure(structure)
io.save('without_chain_B.pdb')
```

## Modifying B-factors

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Set all B-factors to same value
for atom in structure.get_atoms():
    atom.bfactor = 20.0

# Or set based on residue property (e.g., conservation score)
conservation_scores = {100: 9.0, 101: 5.0, 102: 3.0}  # resnum -> score
for residue in structure.get_residues():
    resnum = residue.id[1]
    score = conservation_scores.get(resnum, 5.0)
    for atom in residue:
        atom.bfactor = score * 10  # Scale to B-factor range

io = PDBIO()
io.set_structure(structure)
io.save('modified_bfactor.pdb')
```

## Modifying Occupancy

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Set occupancy for specific chain
for atom in structure[0]['A'].get_atoms():
    atom.occupancy = 0.5

io = PDBIO()
io.set_structure(structure)
io.save('modified_occupancy.pdb')
```

## Renumbering Residues

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

chain = structure[0]['A']

# Renumber sequentially starting from 1
new_residues = []
for i, residue in enumerate(chain, start=1):
    hetfield, _, icode = residue.id
    new_id = (hetfield, i, icode)
    residue.id = new_id
    new_residues.append(residue)

io = PDBIO()
io.set_structure(structure)
io.save('renumbered.pdb')
```

## Changing Chain ID

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Rename chain A to X
model = structure[0]
chain = model['A']
chain.id = 'X'

io = PDBIO()
io.set_structure(structure)
io.save('renamed_chain.pdb')
```

## Building Structure from Scratch

```python
from Bio.PDB.Structure import Structure
from Bio.PDB.Model import Model
from Bio.PDB.Chain import Chain
from Bio.PDB.Residue import Residue
from Bio.PDB.Atom import Atom
from Bio.PDB import PDBIO
import numpy as np

# Create hierarchy
structure = Structure('new_struct')
model = Model(0)
chain = Chain('A')
residue = Residue((' ', 1, ' '), 'ALA', '')

# Add atoms
ca = Atom('CA', np.array([0.0, 0.0, 0.0]), 20.0, 1.0, ' ', 'CA', 1, 'C')
cb = Atom('CB', np.array([1.5, 0.0, 0.0]), 20.0, 1.0, ' ', 'CB', 2, 'C')

residue.add(ca)
residue.add(cb)
chain.add(residue)
model.add(chain)
structure.add(model)

io = PDBIO()
io.set_structure(structure)
io.save('new_structure.pdb')
```

## Using StructureBuilder

```python
from Bio.PDB import StructureBuilder, PDBIO
import numpy as np

sb = StructureBuilder.StructureBuilder()
sb.init_structure('built')
sb.init_model(0)
sb.init_chain('A')
sb.init_seg(' ')

# Add residue with atoms
sb.init_residue('ALA', ' ', 1, ' ')
sb.init_atom('N', np.array([-1.0, 0.0, 0.0]), 20.0, 1.0, ' ', 'N', 1, 'N')
sb.init_atom('CA', np.array([0.0, 0.0, 0.0]), 20.0, 1.0, ' ', 'CA', 2, 'C')
sb.init_atom('C', np.array([1.0, 0.0, 0.0]), 20.0, 1.0, ' ', 'C', 3, 'C')
sb.init_atom('O', np.array([1.5, 1.0, 0.0]), 20.0, 1.0, ' ', 'O', 4, 'O')

sb.init_residue('GLY', ' ', 2, ' ')
sb.init_atom('N', np.array([1.5, -1.0, 0.0]), 20.0, 1.0, ' ', 'N', 5, 'N')
sb.init_atom('CA', np.array([2.5, -1.0, 0.0]), 20.0, 1.0, ' ', 'CA', 6, 'C')
sb.init_atom('C', np.array([3.5, -1.0, 0.0]), 20.0, 1.0, ' ', 'C', 7, 'C')
sb.init_atom('O', np.array([4.0, 0.0, 0.0]), 20.0, 1.0, ' ', 'O', 8, 'O')

structure = sb.get_structure()

io = PDBIO()
io.set_structure(structure)
io.save('built_structure.pdb')
```

## Adding a Residue to Existing Chain

```python
from Bio.PDB import PDBParser, PDBIO
from Bio.PDB.Residue import Residue
from Bio.PDB.Atom import Atom
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

chain = structure[0]['A']

# Create new residue
new_residue = Residue((' ', 999, ' '), 'ALA', '')
ca = Atom('CA', np.array([50.0, 50.0, 50.0]), 20.0, 1.0, ' ', 'CA', 9999, 'C')
new_residue.add(ca)

# Add to chain
chain.add(new_residue)

io = PDBIO()
io.set_structure(structure)
io.save('with_new_residue.pdb')
```

## Copying a Chain

```python
from Bio.PDB import PDBParser, PDBIO
from Bio.PDB.Chain import Chain
from Bio.PDB.Residue import Residue
from Bio.PDB.Atom import Atom
import copy

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Deep copy chain A as chain B
original_chain = structure[0]['A']
new_chain = Chain('B')

for residue in original_chain:
    new_residue = Residue(residue.id, residue.resname, residue.segid)
    for atom in residue:
        new_atom = Atom(
            atom.name, atom.coord.copy(), atom.bfactor, atom.occupancy,
            atom.altloc, atom.fullname, atom.serial_number, atom.element
        )
        new_residue.add(new_atom)
    new_chain.add(new_residue)

structure[0].add(new_chain)

io = PDBIO()
io.set_structure(structure)
io.save('duplicated_chain.pdb')
```

## Extract and Save Specific Residues

```python
from Bio.PDB import PDBParser, PDBIO
from Bio.PDB.Structure import Structure
from Bio.PDB.Model import Model
from Bio.PDB.Chain import Chain

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Extract residues 50-100
new_structure = Structure('subset')
new_model = Model(0)
new_chain = Chain('A')

for residue in structure[0]['A']:
    if 50 <= residue.id[1] <= 100 and residue.id[0] == ' ':
        new_chain.add(residue.copy())

new_model.add(new_chain)
new_structure.add(new_model)

io = PDBIO()
io.set_structure(new_structure)
io.save('residues_50_100.pdb')
```

## Merge Two Structures

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
struct1 = parser.get_structure('s1', 'structure1.pdb')
struct2 = parser.get_structure('s2', 'structure2.pdb')

# Add chains from struct2 to struct1 (rename to avoid conflicts)
for chain in struct2[0]:
    new_id = chr(ord(chain.id) + 10)  # Offset chain ID
    chain.id = new_id
    struct1[0].add(chain)

io = PDBIO()
io.set_structure(struct1)
io.save('merged.pdb')
```

## Related Skills

- structure-io - Parse and write structure files
- structure-navigation - Access chains, residues, atoms
- geometric-analysis - Calculate distances, angles, RMSD
- sequence-manipulation/seq-objects - Generate sequences from modified structures
