# bindcraft

> End-to-end binder design using BindCraft hallucination. Use this skill when: (1) Designing protein binders with built-in AF2 validation, (2) Running production-quality binder campaigns, (3) Using different design protocols (fast, default, slow), (4) Need joint backbone and sequence optimization, (5) Want high experimental success rate.
For backbone-only generation, use rfdiffusion. For QC thresholds, use protein-qc. For tool selection guidance, use binder-design.

# BindCraft Binder Design

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.9+ | 3.10 |
| CUDA | 11.7+ | 12.0+ |
| GPU VRAM | 32GB | 48GB (L40S) |
| RAM | 32GB | 64GB |

## How to run

> **First time?** See [Installation Guide](../../docs/installation.md) to set up Modal and 
### Option 1: Modal (recommended)
```bash
cd modal run modal_bindcraft.py \
  --target-pdb target.pdb \
  --target-chain A \
  --binder-lengths 70-100 \
  --hotspots "A45,A67,A89" \
  --num-designs 50
```

**GPU**: L40S (48GB) | **Timeout**: 3600s default

### Option 2: Local installation
```bash
git clone https://github.com/martinpacesa/BindCraft.git
cd BindCraft
pip install -r requirements.txt

python bindcraft.py \
  --target target.pdb \
  --target_chains A \
  --binder_lengths 70-100 \
  --hotspots A45,A67,A89 \
  --num_designs 50
```

## Key parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `--target-pdb` | required | path | Target structure |
| `--target-chain` | required | A-Z | Target chain(s) |
| `--binder-lengths` | 70-100 | 40-150 | Length range |
| `--hotspots` | None | residues | Target hotspots |
| `--num-designs` | 50 | 1-500 | Number of designs |
| `--protocol` | default | fast/default/slow | Quality vs speed |

## Protocols

| Protocol | Speed | Quality | Use Case |
|----------|-------|---------|----------|
| fast | Fast | Lower | Initial screening |
| default | Medium | Good | Standard campaigns |
| slow | Slow | High | Final production |

## Output format

```
output/
├── design_0/
│   ├── binder.pdb         # Final design
│   ├── complex.pdb        # Binder + target
│   ├── metrics.json       # QC scores
│   └── trajectory/        # Optimization trajectory
├── design_1/
│   └── ...
└── summary.csv            # All metrics
```

### Metrics Output
```json
{
  "plddt": 0.89,
  "ptm": 0.78,
  "iptm": 0.62,
  "pae": 8.5,
  "rmsd": 1.2,
  "sequence": "MKTAYIAK..."
}
```

## Sample output

### Successful run
```
$ modal run modal_bindcraft.py --target-pdb target.pdb --num-designs 50
[INFO] Loading BindCraft model...
[INFO] Target: target.pdb (chain A)
[INFO] Hotspots: A45, A67, A89
[INFO] Protocol: default
[INFO] Generating 50 designs...

Design 1/50:
  Length: 78 AA
  pLDDT: 0.89, ipTM: 0.62
  Saved: output/design_0/

Design 50/50:
  Length: 85 AA
  pLDDT: 0.86, ipTM: 0.58
  Saved: output/design_49/

[INFO] Campaign complete. Summary: output/summary.csv
Pass rate: 32/50 (64%) with ipTM > 0.5
```

**What good output looks like:**
- pLDDT: > 0.85 for most designs
- ipTM: > 0.5 for passing designs
- Pass rate: 30-70% depending on target
- Diverse sequences across designs

## Decision tree

```
Should I use BindCraft?
│
├─ What type of design?
│  ├─ Production-quality binders → BindCraft ✓
│  ├─ High diversity exploration → RFdiffusion
│  └─ All-atom precision → BoltzGen
│
├─ What matters most?
│  ├─ Experimental success rate → BindCraft ✓
│  ├─ Speed / diversity → RFdiffusion + ProteinMPNN
│  ├─ AF2 gradient optimization → ColabDesign
│  └─ All-atom control → BoltzGen
│
└─ Compute resources?
   ├─ Have L40S/A100 → BindCraft ✓
   └─ Only A10G → RFdiffusion + ProteinMPNN
```

## Typical performance

| Campaign Size | Time (L40S) | Cost (Modal) | Notes |
|---------------|-------------|--------------|-------|
| 50 designs | 2-4h | ~$15 | Quick campaign |
| 100 designs | 4-8h | ~$30 | Standard |
| 200 designs | 8-16h | ~$60 | Large campaign |

**Expected pass rate**: 30-70% with ipTM > 0.5 (target-dependent).

---

## Verify

```bash
find output -name "binder.pdb" | wc -l  # Should match num_designs
```

---

## Troubleshooting

**Low ipTM scores**: Check hotspot selection, increase designs
**Slow convergence**: Use fast protocol for screening
**OOM errors**: Reduce num_models, use L40S GPU
**Poor diversity**: Lower sampling_temp, run multiple seeds

### Error interpretation

| Error | Cause | Fix |
|-------|-------|-----|
| `RuntimeError: CUDA out of memory` | Large target or long binder | Use L40S/A100, reduce binder length |
| `ValueError: no hotspots` | Hotspots not found | Check residue numbering |
| `TimeoutError` | Design taking too long | Use fast protocol |

---

**Next**: Rank by `ipsae` → experimental validation.
