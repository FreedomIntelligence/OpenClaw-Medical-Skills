# chai

> Structure prediction using Chai-1, a foundation model for molecular structure. Use this skill when: (1) Predicting protein-protein complex structures, (2) Validating designed binders, (3) Predicting protein-ligand complexes, (4) Using the Chai API for high-throughput prediction, (5) Need an alternative to AlphaFold2.
For QC thresholds, use protein-qc. For AlphaFold2 prediction, use alphafold. For ESM-based analysis, use esm.

# Chai-1 Structure Prediction

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.11 |
| CUDA | 12.0+ | 12.1+ |
| GPU VRAM | 24GB | 40GB (A100) |
| RAM | 32GB | 64GB |

## How to run

> **First time?** See [Installation Guide](../../docs/installation.md) to set up Modal and 
### Option 1: Modal
```bash
cd modal run modal_chai1.py \
  --input-faa complex.fasta \
  --out-dir predictions/
```

**GPU**: A100 (40GB) | **Timeout**: 30min default

### Option 2: Chai API (recommended)
```bash
pip install chai_lab

python -c "
import chai_lab
from chai_lab.chai1 import run_inference

# Run prediction
run_inference(
    fasta_file='complex.fasta',
    output_dir='predictions/',
    num_trunk_recycles=3
)
"
```

### Option 3: Local installation
```bash
git clone https://github.com/chaidiscovery/chai-lab.git
cd chai-lab
pip install -e .

chai-lab predict \
  --fasta complex.fasta \
  --output predictions/
```

## FASTA Format

### Protein complex
```
>binder
MKTAYIAKQRQISFVKSHFSRQLE...
>target
MVLSPADKTNVKAAWGKVGAHAGE...
```

### Protein + ligand
```
>protein
MKTAYIAKQRQISFVKSHFSRQLE...
>ligand|smiles
CCO
```

### Protein + DNA/RNA
```
>protein
MKTAYIAKQRQISFVKSHFSRQLE...
>dna
ATCGATCGATCG
```

## Key parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `num_trunk_recycles` | 3 | 1-10 | Recycles (more = better) |
| `num_diffn_timesteps` | 200 | 50-500 | Diffusion steps |
| `seed` | 0 | int | Random seed |

## Output format

```
predictions/
├── pred.model_idx_0.cif    # Best model (CIF format)
├── pred.model_idx_1.cif    # Second model
├── scores.json             # Confidence scores
├── pae.npy                 # PAE matrix
└── plddt.npy               # pLDDT values
```

**Note**: Chai-1 outputs CIF format. Convert to PDB if needed:
```python
from Bio.PDB import MMCIFParser, PDBIO
parser = MMCIFParser()
structure = parser.get_structure("pred", "pred.model_idx_0.cif")
io = PDBIO()
io.set_structure(structure)
io.save("pred.model_idx_0.pdb")
```

### Extracting metrics
```python
import numpy as np
import json

# Load scores
with open('predictions/scores.json') as f:
    scores = json.load(f)

plddt = np.load('predictions/plddt.npy')
pae = np.load('predictions/pae.npy')

print(f"pLDDT: {plddt.mean():.3f}")
print(f"pTM: {scores['ptm']:.3f}")
print(f"ipTM: {scores.get('iptm', 'N/A')}")
```

## Use cases

### Binder validation
```python
# Predict complex with Chai
chai-lab predict --fasta binder_target.fasta --output val/

# Check ipTM > 0.5
scores = json.load(open('val/scores.json'))
if scores['iptm'] > 0.5:
    print("Design passes validation")
```

### Protein-ligand complex
```python
# FASTA with SMILES
fasta = """
>protein
MKTA...
>ligand|smiles
CCO
"""

# Chai handles both protein and small molecules
```

### Batch prediction
```bash
# Multiple sequences
for fasta in sequences/*.fasta; do
    chai-lab predict \
        --fasta "$fasta" \
        --output "predictions/$(basename $fasta .fasta)"
done
```

## Comparison with AF2

| Aspect | Chai-1 | AlphaFold2 |
|--------|--------|------------|
| MSA required | No | Yes |
| Small molecules | Yes | No |
| DNA/RNA | Yes | Limited |
| Speed | Faster | Slower |
| Accuracy | Comparable | Reference |

## Sample output

### Successful run
```
$ chai-lab predict --fasta complex.fasta --output predictions/
[INFO] Loading Chai-1 model...
[INFO] Running inference...
[INFO] Saved 5 models to predictions/

predictions/scores.json:
{
  "ptm": 0.82,
  "iptm": 0.71,
  "ranking_score": 0.76
}
```

**What good output looks like:**
- pTM: > 0.7 (confident global structure)
- ipTM: > 0.5 (confident interface, > 0.7 for high confidence)
- CIF files with reasonable atom positions

## Decision tree

```
Should I use Chai?
│
├─ What are you predicting?
│  ├─ Protein-protein complex → Chai ✓ or ColabFold
│  ├─ Protein + small molecule → Chai ✓
│  ├─ Protein + DNA/RNA → Chai ✓
│  └─ Single protein only → Use ESMFold (faster)
│
├─ Need MSA?
│  ├─ No / want speed → Chai ✓
│  └─ Yes / want accuracy → ColabFold
│
└─ Priority?
   ├─ Highest accuracy → ColabFold with MSA
   ├─ Speed / no MSA → Chai ✓
   └─ Ligand binding → Chai ✓
```

## Typical performance

| Campaign Size | Time (A100) | Cost (Modal) | Notes |
|---------------|-------------|--------------|-------|
| 100 complexes | 30-60 min | ~$10 | Standard validation |
| 500 complexes | 2-4h | ~$45 | Large campaign |
| 1000 complexes | 5-8h | ~$90 | Comprehensive |

**Per-complex**: ~20-40s for typical binder-target complex.

---

## Verify

```bash
find predictions -name "*.cif" | wc -l  # Should match input count
```

---

## Troubleshooting

**Low pLDDT**: Increase num_trunk_recycles
**Low ipTM**: Check chain order, interface region
**OOM errors**: Use A100-80GB or reduce batch
**Slow prediction**: Reduce num_diffn_timesteps

### Error interpretation

| Error | Cause | Fix |
|-------|-------|-----|
| `RuntimeError: CUDA out of memory` | Complex too large | Use A100-80GB or split prediction |
| `KeyError: 'iptm'` | Single chain predicted | Ensure FASTA has multiple chains |
| `ValueError: invalid SMILES` | Malformed ligand | Validate SMILES with RDKit |
| `torch.cuda.OutOfMemoryError` | GPU exhausted | Reduce num_diffn_timesteps to 100 |

---

**Next**: `protein-qc` for filtering and ranking.
