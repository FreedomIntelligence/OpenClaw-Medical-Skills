# bio-pdb-structure-io

> Parse and write protein structure files using Biopython Bio.PDB. Use when reading PDB, mmCIF, and MMTF files, downloading structures from RCSB PDB, or writing structures to various formats.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structure I/O

**"Read a PDB file"** → Parse protein structure files (PDB, mmCIF, MMTF), download from RCSB PDB, and write structures to various formats.
- Python: `Bio.PDB.PDBParser().get_structure('id', 'file.pdb')`, `Bio.PDB.MMCIFParser()`

Parse, download, and write protein structure files in PDB, mmCIF, and MMTF formats.

## Required Imports

```python
from Bio.PDB import PDBParser, MMCIFParser, PDBIO, MMCIFIO, PDBList
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
```

## Supported Formats

| Format | Parser | Writer | Description |
|--------|--------|--------|-------------|
| PDB | `PDBParser` | `PDBIO` | Legacy format, limited to 99999 atoms |
| mmCIF | `MMCIFParser` | `MMCIFIO` | Modern standard, full metadata |
| MMTF | `MMTFParser` | - | Compact binary (read-only in Biopython) |
| BinaryCIF | `BinaryCIFParser` | - | Compact binary, RCSB recommended |

## Parsing PDB Files

```python
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('1abc', '1abc.pdb')

print(f'Structure ID: {structure.id}')
print(f'Number of models: {len(list(structure.get_models()))}')
print(f'Number of chains: {len(list(structure.get_chains()))}')
print(f'Number of residues: {len(list(structure.get_residues()))}')
print(f'Number of atoms: {len(list(structure.get_atoms()))}')
```

## Parsing mmCIF Files

```python
from Bio.PDB import MMCIFParser

parser = MMCIFParser(QUIET=True)
structure = parser.get_structure('1abc', '1abc.cif')

# mmCIF is the modern standard - use for new workflows
print(f'Structure: {structure.id}')
```

## Parsing MMTF Files

```python
from Bio.PDB.MMTFParser import MMTFParser

parser = MMTFParser()
structure = parser.get_structure('1abc.mmtf')
```

## Parsing BinaryCIF Files

```python
from Bio.PDB import BinaryCIFParser

parser = BinaryCIFParser()
structure = parser.get_structure('1abc', '1abc.bcif')
```

## Downloading from RCSB PDB

```python
from Bio.PDB import PDBList

pdbl = PDBList()

# Download single structure (mmCIF by default)
file_path = pdbl.retrieve_pdb_file('1ABC', pdir='.', file_format='mmCif')
print(f'Downloaded: {file_path}')

# Download as PDB format
file_path = pdbl.retrieve_pdb_file('1ABC', pdir='.', file_format='pdb')

# Download biological assembly
file_path = pdbl.retrieve_pdb_file('1ABC', pdir='.', file_format='mmCif', assembly_num=1)

# Get list of all PDB entries
all_entries = pdbl.get_all_entries()
print(f'Total PDB entries: {len(all_entries)}')

# Get obsolete entries
obsolete = pdbl.get_all_obsolete()
```

## Batch Downloading

```python
from Bio.PDB import PDBList

pdbl = PDBList()
pdb_ids = ['1ABC', '2XYZ', '3DEF']

for pdb_id in pdb_ids:
    file_path = pdbl.retrieve_pdb_file(pdb_id, pdir='structures/', file_format='mmCif')
    print(f'Downloaded: {pdb_id}')
```

## Writing PDB Files

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('1abc', '1abc.pdb')

io = PDBIO()
io.set_structure(structure)
io.save('output.pdb')
```

## Writing mmCIF Files

```python
from Bio.PDB import MMCIFParser, MMCIFIO

parser = MMCIFParser(QUIET=True)
structure = parser.get_structure('1abc', '1abc.cif')

io = MMCIFIO()
io.set_structure(structure)
io.save('output.cif')
```

## Selective Output with Select Class

```python
from Bio.PDB import PDBParser, PDBIO, Select

class ChainSelect(Select):
    def __init__(self, chain_id):
        self.chain_id = chain_id

    def accept_chain(self, chain):
        return chain.id == self.chain_id

parser = PDBParser(QUIET=True)
structure = parser.get_structure('1abc', '1abc.pdb')

io = PDBIO()
io.set_structure(structure)
io.save('chain_A.pdb', ChainSelect('A'))
```

## Select Class Methods

```python
from Bio.PDB import Select

class CustomSelect(Select):
    def accept_model(self, model):
        return model.id == 0  # Only first model

    def accept_chain(self, chain):
        return chain.id in ['A', 'B']  # Only chains A and B

    def accept_residue(self, residue):
        return residue.id[0] == ' '  # Exclude hetero residues

    def accept_atom(self, atom):
        return atom.element != 'H'  # Exclude hydrogens
```

## Extracting Header Information

```python
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('1abc', '1abc.pdb')

header = structure.header
print(f"Name: {header.get('name', 'Unknown')}")
print(f"Resolution: {header.get('resolution', 'N/A')}")
print(f"Structure method: {header.get('structure_method', 'Unknown')}")
print(f"Deposition date: {header.get('deposition_date', 'Unknown')}")
```

## mmCIF Metadata with MMCIF2Dict

```python
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

mmcif_dict = MMCIF2Dict('1abc.cif')

# Access any mmCIF field
print(f"Entry ID: {mmcif_dict['_entry.id']}")
print(f"Resolution: {mmcif_dict.get('_refine.ls_d_res_high', ['N/A'])[0]}")
print(f"Method: {mmcif_dict.get('_exptl.method', ['Unknown'])[0]}")

# List all available fields
print(f"Available fields: {len(mmcif_dict.keys())}")
```

## Quick Structure Inspection

```python
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
structure = parser.get_structure('1abc', '1abc.pdb')

print(f'Models: {[m.id for m in structure]}')
for model in structure:
    print(f'  Model {model.id}:')
    for chain in model:
        residues = list(chain.get_residues())
        atoms = list(chain.get_atoms())
        print(f'    Chain {chain.id}: {len(residues)} residues, {len(atoms)} atoms')
```

## Format Conversion

```python
from Bio.PDB import PDBParser, MMCIFParser, PDBIO, MMCIFIO

# PDB to mmCIF
parser = PDBParser(QUIET=True)
structure = parser.get_structure('prot', 'protein.pdb')
io = MMCIFIO()
io.set_structure(structure)
io.save('protein.cif')

# mmCIF to PDB
parser = MMCIFParser(QUIET=True)
structure = parser.get_structure('prot', 'protein.cif')
io = PDBIO()
io.set_structure(structure)
io.save('protein.pdb')
```

## Writing PQR Files

```python
from Bio.PDB import PDBParser, PDBIO

parser = PDBParser(QUIET=True)
structure = parser.get_structure('1abc', '1abc.pdb')

# PQR format includes charge and radius instead of occupancy and B-factor
io = PDBIO(is_pqr=True)
io.set_structure(structure)
io.save('output.pqr')
```

## Handling Parser Warnings

```python
from Bio.PDB import PDBParser
import warnings

# Suppress warnings
parser = PDBParser(QUIET=True)

# Or capture warnings
parser = PDBParser(QUIET=False)
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    structure = parser.get_structure('1abc', '1abc.pdb')
    if w:
        print(f'Warnings: {len(w)}')
        for warning in w:
            print(f'  {warning.message}')
```

## Related Skills

- structure-navigation - Traverse SMCRA hierarchy to access chains, residues, atoms
- geometric-analysis - Measure distances, angles, and superimpose structures
- structure-modification - Modify coordinates and properties before writing
- database-access/entrez-fetch - Fetch structure metadata from NCBI/UniProt
