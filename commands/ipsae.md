# ipsae

> Binder design ranking using ipSAE (interprotein Score from Aligned Errors). Use this skill when: (1) Ranking binder designs for experimental testing, (2) Filtering BindCraft or RFdiffusion outputs, (3) Comparing AF2/AF3/Boltz predictions, (4) Predicting binding success rates, (5) Need better ranking than ipTM or iPAE.
For structure prediction, use chai or alphafold. For QC thresholds, use protein-qc.

# ipSAE Binder Ranking

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10 |
| NumPy | 1.20+ | Latest |
| RAM | 8GB | 16GB |

## Overview

ipSAE (interprotein Score from Aligned Errors) is a scoring function for ranking protein-protein interactions predicted by AlphaFold2, AlphaFold3, and Boltz1. It outperforms ipTM and iPAE for binder design ranking with **1.4x higher precision** in identifying true binders.

**Paper**: [What's wrong with AlphaFold's ipTM score](https://www.biorxiv.org/content/10.1101/2025.02.10.637595v2)

## How to run

### Installation
```bash
git clone https://github.com/DunbrackLab/IPSAE.git
cd IPSAE
pip install numpy
```

### AlphaFold2
```bash
python ipsae.py scores_rank_001.json unrelaxed_rank_001.pdb 15 15
```

### AlphaFold3
```bash
python ipsae.py fold_model_full_data_0.json fold_model_0.cif 10 10
```

### Boltz1
```bash
python ipsae.py pae_model_0.npz model_0.cif 10 10
```

## Key parameters

| Parameter | Description | Recommended |
|-----------|-------------|-------------|
| PAE file | JSON (AF2/AF3) or NPZ (Boltz) | Match predictor |
| Structure file | PDB or CIF structure | Match PAE |
| PAE cutoff | Threshold for contacts | 10-15 |
| Distance cutoff | Max CA-CA distance (A) | 10-15 |

## Output format

Two output files are generated:

**Chain-pair scores** (`_chains.csv`):
```
chain_A,chain_B,ipSAE_min,pDockQ,pDockQ2,LIS,n_contacts,interface_dist
A,B,0.72,0.65,0.58,0.45,42,8.5
```

**Residue-level scores** (`_residues.csv`):
```
chain,resnum,pSAE,pLDDT
A,45,0.85,92.3
A,67,0.78,88.1
```

## Sample output

### Successful run
```
$ python ipsae.py scores_rank_001.json design_0.pdb 10 10
Processing design_0...
Found 2 chains: A, B
Computing ipSAE scores...

Results written to:
  design_0_chains.csv
  design_0_residues.csv

Summary:
  ipSAE_min: 0.72
  pDockQ: 0.65
  LIS: 0.45
  Interface contacts: 42
```

**What good output looks like:**
- ipSAE_min > 0.61 (primary filter)
- pDockQ > 0.5 (supporting metric)
- Reasonable number of interface contacts (20-100)

## Decision tree

```
Should I use ipSAE?
│
├─ What are you ranking?
│  ├─ Designed binders → ipSAE ✓
│  ├─ Natural complexes → ipTM is fine
│  └─ Single proteins → Not applicable
│
├─ What predictor did you use?
│  ├─ AlphaFold2 → ipSAE ✓
│  ├─ AlphaFold3 → ipSAE ✓
│  ├─ Boltz1 → ipSAE ✓
│  ├─ Chai → ipSAE (use PAE output)
│  └─ ESMFold → Not applicable (no PAE)
│
└─ Why ipSAE over ipTM?
   ├─ Different length constructs → ipSAE ✓
   ├─ Designs with disordered regions → ipSAE ✓
   └─ Standard complexes → Either works
```

## Recommended thresholds

| Metric | Standard | Stringent | Use Case |
|--------|----------|-----------|----------|
| ipSAE_min | > 0.61 | > 0.70 | Primary filter |
| LIS | > 0.35 | > 0.45 | Interface quality |
| pDockQ | > 0.5 | > 0.6 | Supporting |

## Batch processing

```python
import subprocess
import os
from pathlib import Path

def score_designs(pae_dir, struct_dir, output_dir):
    """Score all designs in a directory."""
    Path(output_dir).mkdir(exist_ok=True)

    for pae_file in Path(pae_dir).glob("*_scores*.json"):
        name = pae_file.stem.replace("_scores_rank_001", "")
        struct_file = Path(struct_dir) / f"{name}.pdb"

        if struct_file.exists():
            subprocess.run([
                "python", "ipsae.py",
                str(pae_file),
                str(struct_file),
                "10", "10"
            ])
```

---

## Verify

```bash
ls *_chains.csv | wc -l  # Should match number of predictions
```

---

## Troubleshooting

**Low scores for good designs**: Check PAE/distance cutoffs
**Missing output**: Verify PAE file format matches predictor
**Inconsistent scores**: Use same cutoffs across all designs

### Error interpretation

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: 'pae'` | Wrong PAE format | Check if AF2/AF3/Boltz format |
| `FileNotFoundError` | Structure not found | Verify file paths |
| `ValueError: no contacts` | No interface detected | Check chain IDs, reduce cutoffs |

---

**Next**: Select top designs (ipSAE_min > 0.61) → experimental validation.
