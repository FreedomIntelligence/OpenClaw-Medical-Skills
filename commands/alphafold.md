# alphafold

> Validate protein designs using AlphaFold2 structure prediction. Use this skill when: (1) Validating designed sequences fold correctly, (2) Predicting binder-target complex structures, (3) Calculating confidence metrics (pLDDT, pTM, ipTM), (4) Self-consistency validation of designs, (5) Multi-chain complex prediction with AlphaFold-Multimer.
For faster single-chain prediction, use esm. For QC thresholds, use protein-qc.

# AlphaFold2 Structure Validation

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10 |
| CUDA | 11.0+ | 12.0+ |
| GPU VRAM | 32GB | 40GB (A100) |
| RAM | 32GB | 64GB |
| Disk | 100GB | 500GB (for databases) |

## How to run

> **First time?** See [Installation Guide](../../docs/installation.md) to set up Modal and 
### Option 1: ColabFold (recommended for multimer)
```bash
cd modal run modal_colabfold.py \
  --input-faa sequences.fasta \
  --out-dir output/
```

**GPU**: A100 (40GB) | **Timeout**: 3600s default

### Option 2: Local installation
```bash
git clone https://github.com/deepmind/alphafold.git
cd alphafold

python run_alphafold.py \
  --fasta_paths=query.fasta \
  --output_dir=output/ \
  --model_preset=monomer \
  --max_template_date=2026-01-01
```

### Option 3: ESMFold (fast single-chain)
```bash
modal run modal_esmfold.py \
  --sequence "MKTAYIAKQRQISFVK..."
```

## Key parameters

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `--model_preset` | monomer | monomer/multimer | Model type |
| `--num_recycle` | 3 | 1-20 | Recycling iterations |
| `--max_template_date` | - | YYYY-MM-DD | Template cutoff |
| `--use_templates` | True | True/False | Use template search |

## Output format

```
output/
├── ranked_0.pdb           # Best model
├── ranked_1.pdb           # Second best
├── ranking_debug.json     # Confidence scores
├── result_model_1.pkl     # Full results
├── msas/                  # MSA files
└── features.pkl           # Input features
```

### Extracting metrics
```python
import pickle

with open('result_model_1.pkl', 'rb') as f:
    result = pickle.load(f)

plddt = result['plddt']
ptm = result['ptm']
iptm = result.get('iptm', None)  # Multimer only
pae = result['predicted_aligned_error']
```

## Sample output

### Successful run
```
$ python run_alphafold.py --fasta_paths complex.fasta --model_preset multimer
[INFO] Running MSA search...
[INFO] Running model 1/5...
[INFO] Running model 5/5...
[INFO] Relaxing structures...

Results:
  ranked_0.pdb:
    pLDDT: 87.3 (mean)
    pTM: 0.78
    ipTM: 0.62
    PAE (interface): 8.5

Saved to output/
```

**What good output looks like:**
- pLDDT: > 85 (mean, on 0-100 scale) or > 0.85 (normalized)
- pTM: > 0.70
- ipTM: > 0.50 for complexes
- PAE_interface: < 10

## Decision tree

```
Should I use AlphaFold?
│
├─ What are you predicting?
│  ├─ Single protein → ESMFold (faster)
│  ├─ Protein-protein complex → AlphaFold/ColabFold ✓
│  ├─ Protein + ligand → Chai or Boltz
│  └─ Batch of sequences → ColabFold ✓
│
├─ What do you need?
│  ├─ Highest accuracy → AlphaFold/ColabFold ✓
│  ├─ Fast screening → ESMFold
│  └─ MSA-free prediction → Chai or ESMFold
│
└─ Which AF2 option?
   ├─ Local installation → Full control, slow setup
   ├─ ColabFold → Easier, MSA server
   └─ Modal → Recommended for batch
```

## Typical performance

| Campaign Size | Time (A100) | Cost (Modal) | Notes |
|---------------|-------------|--------------|-------|
| 100 complexes | 1-2h | ~$8 | With MSA server |
| 500 complexes | 5-10h | ~$40 | Standard campaign |
| 1000 complexes | 10-20h | ~$80 | Large campaign |

**Per-complex**: ~30-60s with MSA server.

---

## Verify

```bash
find output -name "ranked_0.pdb" | wc -l  # Should match input count
```

---

## Troubleshooting

**Low pLDDT regions**: May indicate disorder or poor design
**Low ipTM**: Interface not confident, check hotspots
**High PAE off-diagonal**: Chains may not interact
**OOM errors**: Use ColabFold with MSA server instead

### Error interpretation

| Error | Cause | Fix |
|-------|-------|-----|
| `RuntimeError: CUDA out of memory` | Sequence too long | Use A100 or split prediction |
| `KeyError: 'iptm'` | Running monomer on complex | Use multimer preset |
| `FileNotFoundError: database` | Missing MSA databases | Use ColabFold MSA server |
| `TimeoutError` | MSA search slow | Reduce num_recycles |

---

**Next**: `protein-qc` for filtering and ranking.
