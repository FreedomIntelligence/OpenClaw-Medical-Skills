# pdb

> Fetch and analyze protein structures from RCSB PDB. Use this skill when: (1) Need to download a structure by PDB ID, (2) Search for similar structures, (3) Prepare target for binder design, (4) Extract specific chains or domains, (5) Get structure metadata.
For sequence lookup, use uniprot. For binder design workflow, use binder-design.

# PDB Database Access

**Note**: This skill uses the RCSB PDB web API directly. No Modal deployment needed - all operations run locally via HTTP requests.

## Fetching Structures

### By PDB ID
```bash
# Download PDB file
curl -o 1alu.pdb "https://files.rcsb.org/download/1ALU.pdb"

# Download mmCIF
curl -o 1alu.cif "https://files.rcsb.org/download/1ALU.cif"
```

### Using Python
```python
from Bio.PDB import PDBList

pdbl = PDBList()
pdbl.retrieve_pdb_file("1ABC", pdir="structures/", file_format="pdb")
```

### Using RCSB API
```python
import requests

def fetch_pdb(pdb_id: str, format: str = "pdb") -> str:
    """Fetch structure from RCSB PDB."""
    url = f"https://files.rcsb.org/download/{pdb_id}.{format}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def fetch_fasta(pdb_id: str) -> str:
    """Fetch sequence in FASTA format."""
    url = f"https://www.rcsb.org/fasta/entry/{pdb_id}"
    return requests.get(url).text

# Example usage
pdb_content = fetch_pdb("1ALU")
with open("1ALU.pdb", "w") as f:
    f.write(pdb_content)
```

## Structure Preparation

### Selecting Chains
```python
from Bio.PDB import PDBParser, PDBIO, Select

class ChainSelect(Select):
    def __init__(self, chain_id):
        self.chain_id = chain_id

    def accept_chain(self, chain):
        return chain.id == self.chain_id

# Extract chain A
parser = PDBParser()
structure = parser.get_structure("protein", "1abc.pdb")
io = PDBIO()
io.set_structure(structure)
io.save("chain_A.pdb", ChainSelect("A"))
```

### Trimming to Binding Region
```python
def trim_around_residues(pdb_file, center_residues, buffer=10.0):
    """Trim structure to region around specified residues."""
    parser = PDBParser()
    structure = parser.get_structure("protein", pdb_file)

    # Get center coordinates
    center_coords = []
    for res in structure.get_residues():
        if res.id[1] in center_residues:
            center_coords.extend([a.coord for a in res.get_atoms()])

    center = np.mean(center_coords, axis=0)

    # Keep residues within buffer
    class RegionSelect(Select):
        def accept_residue(self, res):
            for atom in res.get_atoms():
                if np.linalg.norm(atom.coord - center) < buffer:
                    return True
            return False

    io = PDBIO()
    io.set_structure(structure)
    io.save("trimmed.pdb", RegionSelect())
```

## Searching PDB

### RCSB Search API
```python
import requests

query = {
    "query": {
        "type": "terminal",
        "service": "full_text",
        "parameters": {
            "value": "EGFR kinase domain"
        }
    },
    "return_type": "entry"
}

response = requests.post(
    "https://search.rcsb.org/rcsbsearch/v2/query",
    json=query
)
results = response.json()
```

### By Sequence Similarity
```python
query = {
    "query": {
        "type": "terminal",
        "service": "sequence",
        "parameters": {
            "value": "MKTAYIAKQRQISFVK...",
            "evalue_cutoff": 1e-10,
            "identity_cutoff": 0.9
        }
    }
}
```

## Structure Analysis

### Get Chain Info
```python
def get_structure_info(pdb_file):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)

    info = {
        "chains": [],
        "total_residues": 0
    }

    for model in structure:
        for chain in model:
            residues = list(chain.get_residues())
            info["chains"].append({
                "id": chain.id,
                "length": len(residues),
                "first_res": residues[0].id[1],
                "last_res": residues[-1].id[1]
            })
            info["total_residues"] += len(residues)

    return info
```

### Find Interface Residues
```python
def find_interface_residues(pdb_file, chain_a, chain_b, distance=4.0):
    """Find residues at interface between two chains."""
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("complex", pdb_file)

    interface_a = set()
    interface_b = set()

    for res_a in structure[0][chain_a].get_residues():
        for res_b in structure[0][chain_b].get_residues():
            for atom_a in res_a.get_atoms():
                for atom_b in res_b.get_atoms():
                    if atom_a - atom_b < distance:
                        interface_a.add(res_a.id[1])
                        interface_b.add(res_b.id[1])

    return interface_a, interface_b
```

## Common Tasks for Binder Design

### Target Preparation Checklist
1. Download structure: `curl -o target.pdb "https://files.rcsb.org/download/XXXX.pdb"`
2. Identify target chain
3. Remove waters and ligands (if needed)
4. Trim to binding region + buffer
5. Identify potential hotspots
6. Renumber if needed

## Troubleshooting

**Structure not found**: Check PDB ID format (4 characters)
**Multiple models**: Select first model for design
**Missing residues**: Check for gaps in structure

---

**Next**: Use structure with `boltzgen` (recommended) or `rfdiffusion` for design.
