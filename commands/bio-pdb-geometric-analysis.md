# bio-pdb-geometric-analysis

> Perform geometric calculations on protein structures using Biopython Bio.PDB. Use when measuring distances, angles, and dihedrals, superimposing structures, calculating RMSD, or computing solvent accessible surface area (SASA).

## Version Compatibility

Reference examples tested with: BioPython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Geometric Analysis

**"Calculate RMSD between two protein structures"** → Measure atomic distances/angles/dihedrals, superimpose structures, compute RMSD, and find inter-residue contacts.
- Python: `Bio.PDB.Superimposer()` for RMSD, `NeighborSearch` for contacts

Measure distances, angles, and dihedrals. Superimpose structures and calculate RMSD. Find neighbor atoms and contacts.

## Required Imports

```python
from Bio.PDB import PDBParser, NeighborSearch, Superimposer
from Bio.PDB import calc_angle, calc_dihedral
import numpy as np
```

## Distance Between Atoms

```python
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

chain = structure[0]['A']
atom1 = chain[100]['CA']
atom2 = chain[200]['CA']

# Direct subtraction gives distance
distance = atom1 - atom2
print(f'Distance: {distance:.2f} Angstroms')

# Or use numpy
import numpy as np
distance = np.linalg.norm(atom1.coord - atom2.coord)
```

## Distance Matrix

```python
import numpy as np
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

ca_atoms = [r['CA'] for r in structure.get_residues() if r.has_id('CA') and r.id[0] == ' ']
n = len(ca_atoms)

dist_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(i + 1, n):
        dist = ca_atoms[i] - ca_atoms[j]
        dist_matrix[i, j] = dist
        dist_matrix[j, i] = dist

print(f'Distance matrix shape: {dist_matrix.shape}')
```

## Angle Between Three Atoms

```python
from Bio.PDB import PDBParser, calc_angle

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

residue = structure[0]['A'][100]
n = residue['N']
ca = residue['CA']
c = residue['C']

# calc_angle takes Vector objects (atom.coord returns array, use atom.get_vector())
angle_rad = calc_angle(n.get_vector(), ca.get_vector(), c.get_vector())
angle_deg = np.degrees(angle_rad)
print(f'N-CA-C angle: {angle_deg:.1f} degrees')
```

## Dihedral Angles

```python
from Bio.PDB import PDBParser, calc_dihedral
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

chain = structure[0]['A']

# Calculate phi angle (C-N-CA-C)
res_prev = chain[99]
res_curr = chain[100]

phi = calc_dihedral(
    res_prev['C'].get_vector(),
    res_curr['N'].get_vector(),
    res_curr['CA'].get_vector(),
    res_curr['C'].get_vector()
)
print(f'Phi: {np.degrees(phi):.1f} degrees')

# Calculate psi angle (N-CA-C-N)
res_next = chain[101]
psi = calc_dihedral(
    res_curr['N'].get_vector(),
    res_curr['CA'].get_vector(),
    res_curr['C'].get_vector(),
    res_next['N'].get_vector()
)
print(f'Psi: {np.degrees(psi):.1f} degrees')
```

## Ramachandran Angles for All Residues

```python
from Bio.PDB import PDBParser, PPBuilder, calc_dihedral
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

ppb = PPBuilder()
phi_psi = []

for pp in ppb.build_peptides(structure):
    angles = pp.get_phi_psi_list()
    for residue, (phi, psi) in zip(pp, angles):
        if phi is not None and psi is not None:
            phi_psi.append((residue.resname, np.degrees(phi), np.degrees(psi)))

for name, phi, psi in phi_psi[:10]:
    print(f'{name}: phi={phi:.1f}, psi={psi:.1f}')
```

## Finding Neighbor Atoms

```python
from Bio.PDB import PDBParser, NeighborSearch

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Build search tree from all atoms
all_atoms = list(structure.get_atoms())
ns = NeighborSearch(all_atoms)

# Find atoms within radius of a point
center = structure[0]['A'][100]['CA'].coord
radius = 5.0  # Angstroms
neighbors = ns.search(center, radius)
print(f'Found {len(neighbors)} atoms within {radius}A')

# Find atoms within radius of another atom
ca_atom = structure[0]['A'][100]['CA']
neighbors = ns.search(ca_atom.coord, 5.0)
```

## Finding Residue Contacts

```python
from Bio.PDB import PDBParser, NeighborSearch

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

all_atoms = list(structure.get_atoms())
ns = NeighborSearch(all_atoms)

# Find all atom pairs within distance
contact_distance = 4.0
contacts = ns.search_all(contact_distance, level='R')  # R = residue level

print(f'Found {len(contacts)} residue contacts within {contact_distance}A')
for res1, res2 in contacts[:10]:
    print(f'  {res1.resname}{res1.id[1]} - {res2.resname}{res2.id[1]}')
```

## Contact Levels

```python
from Bio.PDB import NeighborSearch

# search_all returns pairs at specified level
# Level codes: A=atom, R=residue, C=chain, M=model, S=structure

atom_contacts = ns.search_all(4.0, level='A')      # Atom pairs
residue_contacts = ns.search_all(4.0, level='R')  # Residue pairs
chain_contacts = ns.search_all(10.0, level='C')   # Chain pairs
```

## Superimposing Structures

```python
from Bio.PDB import PDBParser, Superimposer

parser = PDBParser(QUIET=True)
ref_structure = parser.get_structure('ref', 'reference.pdb')
mobile_structure = parser.get_structure('mobile', 'mobile.pdb')

# Get CA atoms from both structures
ref_atoms = [r['CA'] for r in ref_structure.get_residues() if r.has_id('CA') and r.id[0] == ' ']
mobile_atoms = [r['CA'] for r in mobile_structure.get_residues() if r.has_id('CA') and r.id[0] == ' ']

# Ensure same number of atoms
n = min(len(ref_atoms), len(mobile_atoms))
ref_atoms = ref_atoms[:n]
mobile_atoms = mobile_atoms[:n]

# Superimpose
sup = Superimposer()
sup.set_atoms(ref_atoms, mobile_atoms)
print(f'RMSD before: {sup.rms:.2f} Angstroms')

# Apply transformation to all atoms in mobile structure
sup.apply(mobile_structure.get_atoms())
```

## Calculating RMSD

```python
from Bio.PDB import PDBParser, Superimposer
import numpy as np

parser = PDBParser(QUIET=True)
struct1 = parser.get_structure('s1', 'structure1.pdb')
struct2 = parser.get_structure('s2', 'structure2.pdb')

atoms1 = [r['CA'] for r in struct1.get_residues() if r.has_id('CA') and r.id[0] == ' ']
atoms2 = [r['CA'] for r in struct2.get_residues() if r.has_id('CA') and r.id[0] == ' ']

# Using Superimposer (with alignment)
sup = Superimposer()
sup.set_atoms(atoms1, atoms2)
rmsd_aligned = sup.rms
print(f'RMSD (aligned): {rmsd_aligned:.2f} A')

# Raw RMSD (no alignment)
coords1 = np.array([a.coord for a in atoms1])
coords2 = np.array([a.coord for a in atoms2])
rmsd_raw = np.sqrt(np.mean(np.sum((coords1 - coords2) ** 2, axis=1)))
print(f'RMSD (raw): {rmsd_raw:.2f} A')
```

## CEAligner for Dissimilar Structures

```python
from Bio.PDB import PDBParser, CEAligner

parser = PDBParser(QUIET=True)
ref = parser.get_structure('ref', 'reference.pdb')
mobile = parser.get_structure('mobile', 'query.pdb')

# CE alignment works for structures with different sequences
aligner = CEAligner()
aligner.set_reference(ref)
aligner.align(mobile)

print(f'RMSD: {aligner.rms:.2f} A')

# CEAligner automatically modifies mobile structure coordinates
```

## Center of Mass

```python
from Bio.PDB import PDBParser
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Unweighted center (geometric center)
coords = np.array([a.coord for a in structure.get_atoms()])
center = coords.mean(axis=0)
print(f'Geometric center: {center}')

# Mass-weighted center (approximate - uses atom count)
# For accurate mass-weighted, use element masses
atoms = list(structure.get_atoms())
masses = {'C': 12.0, 'N': 14.0, 'O': 16.0, 'S': 32.0, 'H': 1.0}
total_mass = 0
weighted_sum = np.zeros(3)
for atom in atoms:
    mass = masses.get(atom.element, 12.0)
    weighted_sum += mass * atom.coord
    total_mass += mass
center_of_mass = weighted_sum / total_mass
print(f'Center of mass: {center_of_mass}')
```

## Radius of Gyration

```python
import numpy as np
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

coords = np.array([a.coord for a in structure.get_atoms()])
center = coords.mean(axis=0)

# Radius of gyration
rg = np.sqrt(np.mean(np.sum((coords - center) ** 2, axis=1)))
print(f'Radius of gyration: {rg:.2f} A')
```

## Finding Surface Residues

```python
from Bio.PDB import PDBParser, NeighborSearch

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Simple approach: residues with few neighbors
all_atoms = list(structure.get_atoms())
ns = NeighborSearch(all_atoms)

surface_residues = []
for residue in structure.get_residues():
    if residue.id[0] != ' ':
        continue
    if not residue.has_id('CA'):
        continue

    ca = residue['CA']
    neighbors = ns.search(ca.coord, 10.0, level='R')
    if len(neighbors) < 15:  # Threshold for surface
        surface_residues.append(residue)

print(f'Surface residues: {len(surface_residues)}')
```

## Vector Operations

```python
from Bio.PDB import PDBParser
from Bio.PDB.vectors import Vector, rotaxis

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Get vectors from atoms
atom1 = structure[0]['A'][100]['CA']
atom2 = structure[0]['A'][101]['CA']

v1 = atom1.get_vector()
v2 = atom2.get_vector()

# Vector operations
diff = v2 - v1
print(f'Distance vector: {diff}')
print(f'Length: {diff.norm():.2f}')

# Normalize
unit = diff.normalized()

# Cross product
cross = v1 ** v2

# Dot product
dot = v1 * v2
```

## Chi Angles (Sidechain Dihedrals)

```python
from Bio.PDB import PDBParser, calc_dihedral
import numpy as np

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Chi1 angle for a residue (N-CA-CB-CG)
residue = structure[0]['A'][100]

if residue.has_id('CB') and residue.has_id('CG'):
    chi1 = calc_dihedral(
        residue['N'].get_vector(),
        residue['CA'].get_vector(),
        residue['CB'].get_vector(),
        residue['CG'].get_vector()
    )
    print(f'Chi1: {np.degrees(chi1):.1f} degrees')
```

## Solvent Accessible Surface Area (SASA)

```python
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Calculate SASA using Shrake-Rupley algorithm
sr = ShrakeRupley()
sr.compute(structure, level='S')  # S=structure, M=model, C=chain, R=residue, A=atom

# Access total SASA
print(f'Total SASA: {structure.sasa:.2f} A^2')

# Access per-residue SASA
for residue in structure.get_residues():
    if hasattr(residue, 'sasa'):
        print(f'{residue.resname}{residue.id[1]}: {residue.sasa:.2f} A^2')
```

## SASA with Custom Parameters

```python
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

# Higher precision (more points = slower but more accurate)
sr = ShrakeRupley(probe_radius=1.4, n_points=960)
sr.compute(structure, level='R')

# Per-atom SASA
for atom in structure.get_atoms():
    print(f'{atom.name}: {atom.sasa:.2f} A^2')
```

## Identifying Buried vs Exposed Residues

```python
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

parser = PDBParser(QUIET=True)
structure = parser.get_structure('protein', 'protein.pdb')

sr = ShrakeRupley()
sr.compute(structure, level='R')

buried = []
exposed = []
for residue in structure.get_residues():
    if residue.id[0] != ' ':
        continue
    if hasattr(residue, 'sasa'):
        if residue.sasa < 10.0:  # Threshold in A^2
            buried.append(residue)
        else:
            exposed.append(residue)

print(f'Buried: {len(buried)}, Exposed: {len(exposed)}')
```

## Related Skills

- structure-io - Parse and write structure files
- structure-navigation - Access chains, residues, atoms
- structure-modification - Transform coordinates, modify structures
- alignment/pairwise-alignment - Sequence alignment for structure comparison
