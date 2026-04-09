# foldseek

> Structure similarity search with Foldseek. Use this skill when: (1) Finding similar structures in PDB/AFDB databases, (2) Structural homology search, (3) Database queries by 3D structure, (4) Finding remote homologs not detected by sequence, (5) Clustering structures by similarity.
For sequence similarity, use uniprot BLAST. For structure prediction, use chai or boltz.

# Foldseek Structure Search

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10 |
| RAM | 8GB | 16GB |
| Disk | 10GB | 50GB (for local databases) |

## How to run

**Note**: Foldseek can run locally or via web server. No GPU required.

### Option 1: Web Server (Quick; rate-limited, use sparingly)
```bash
# Upload structure to web server
curl -X POST "https://search.foldseek.com/api/ticket" \
  -F "q=@query.pdb" \
  -F "database[]=afdb50" \
  -F "database[]=pdb100"
```

### Option 2: Local installation
```bash
# Install Foldseek
conda install -c conda-forge -c bioconda foldseek

# Search PDB
foldseek easy-search query.pdb /path/to/pdb100 results.m8 tmp/

# Search AlphaFold DB
foldseek easy-search query.pdb /path/to/afdb50 results.m8 tmp/
```

### Option 3: Python API
```python
import subprocess
import pandas as pd

def foldseek_search(query_pdb, database, output="results.m8"):
    """Run Foldseek search."""
    subprocess.run([
        "foldseek", "easy-search",
        query_pdb, database, output, "tmp/",
        "--format-output", "query,target,pident,alnlen,evalue,bits"
    ])
    return pd.read_csv(output, sep="\t",
                       names=["query", "target", "pident", "alnlen", "evalue", "bits"])
```

## Key parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--min-seq-id` | 0.0 | Minimum sequence identity |
| `-e` | 0.001 | E-value threshold |
| `--alignment-type` | 2 | 0=3Di, 1=TM, 2=3Di+AA |
| `--max-seqs` | 300 | Max hits to pass through prefilter; reducing this affects sensitivity |

## Databases

| Database | Description | Size |
|----------|-------------|------|
| `pdb100` | PDB clustered at 100% | ~200K structures |
| `afdb50` | AlphaFold DB at 50% | ~67M structures |
| `swissprot` | SwissProt structures | ~500K structures |
| `cath50` | CATH domains | ~50K domains |

## Output format

```
# results.m8 (tabular)
query   target          pident  alnlen  evalue  bits
query   1abc_A          85.2    120     1e-45   180.5
query   2def_B          72.1    115     1e-32   145.2
```

## Sample output

### Successful run
```
$ foldseek easy-search query.pdb pdb100 results.m8 tmp/
[INFO] Loading database: pdb100 (194,527 entries)
[INFO] Searching...
[INFO] Found 127 hits

Top 5 hits:
1. 1abc_A - 85.2% identity, E=1e-45
2. 2def_B - 72.1% identity, E=1e-32
3. 3ghi_C - 68.5% identity, E=1e-28
4. 4jkl_A - 55.3% identity, E=1e-18
5. 5mno_B - 42.1% identity, E=1e-10
```

## Decision tree

```
Should I use Foldseek?
│
├─ What are you searching?
│  ├─ By 3D structure → Foldseek ✓
│  ├─ By sequence → Use BLAST (uniprot skill)
│  └─ Both → Run both, compare results
│
└─ What do you need?
   ├─ Find structural homologs → Foldseek ✓
   ├─ Remote homolog detection → Foldseek ✓
   ├─ Structural clustering → Foldseek ✓
   └─ Functional annotation → Cross-reference with UniProt
```

## Common use cases

### Find similar designs
```bash
# Compare your design to PDB
foldseek easy-search design.pdb pdb100 similar_natural.m8 tmp/
```

### Novelty check
```bash
# Ensure design is novel (low similarity to known)
foldseek easy-search design.pdb afdb50 novelty.m8 tmp/

# Novel if: top hit identity < 30%
```

### Scaffold search
```bash
# Find scaffolds for motif grafting
foldseek easy-search motif.pdb pdb100 scaffolds.m8 tmp/ \
  --min-seq-id 0.0 -e 10
```

---

## Verify

```bash
wc -l results.m8  # Number of hits
```

---

## Troubleshooting

**No hits**: Lower e-value threshold, try larger database
**Too many hits**: Increase min-seq-id threshold
**Slow search**: Use smaller database

### Error interpretation

| Error | Cause | Fix |
|-------|-------|-----|
| `Database not found` | Wrong path | Check database location |
| `Invalid PDB` | Malformed structure | Validate PDB format |
| `Out of memory` | Large database | Use more RAM or web server |

---

**Next**: Download hits with `pdb` skill → use for scaffold design.
