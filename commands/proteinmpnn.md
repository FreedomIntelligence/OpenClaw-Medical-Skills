# proteinmpnn

> Design protein sequences using ProteinMPNN inverse folding. Use this skill when: (1) Designing sequences for RFdiffusion backbones, (2) Redesigning existing protein sequences, (3) Fixing specific residues while designing others, (4) Optimizing sequences for expression or stability, (5) Multi-state or negative design.
For backbone generation, use rfdiffusion or bindcraft. For ligand-aware design, use ligandmpnn. For solubility optimization, use solublempnn.

# ProteinMPNN Sequence Design

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10 |
| CUDA | 11.0+ | 11.7+ |
| GPU VRAM | 8GB | 16GB (T4) |
| RAM | 8GB | 16GB |

## How to run

> **First time?** See [Installation Guide](../../docs/installation.md) to set up Modal and 
### Option 1: Local installation (recommended)
```bash
git clone https://github.com/dauparas/ProteinMPNN.git
cd ProteinMPNN

python protein_mpnn_run.py \
  --pdb_path backbone.pdb \
  --out_folder output/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1"
```

**GPU**: T4 (16GB) sufficient | **Time**: ~50-100 sequences/minute

### Option 2: Modal (via LigandMPNN wrapper)
```bash
cd modal run modal_ligandmpnn.py \
  --pdb-path backbone.pdb \
  --num-seq-per-target 16
```

Note: LigandMPNN includes ProteinMPNN functionality.

## Config Schema

### Core Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `--pdb_path` | required | path | Single PDB input |
| `--pdb_path_chains` | all | A,B | Chains to design (comma-sep) |
| `--out_folder` | required | path | Output directory |
| `--num_seq_per_target` | 1 | 1-1000 | Sequences per structure |
| `--sampling_temp` | "0.1" | "0.0001-1.0" | Temperature (string!) |
| `--seed` | 0 | int | Random seed |
| `--batch_size` | 1 | 1-32 | Batch size |

### Temperature Guide
```
0.1  -> Low diversity, high recovery (production)
0.2  -> Moderate diversity (default)
0.3  -> Higher diversity (exploration)
0.5+ -> Very diverse, lower quality
```

**IMPORTANT**: Temperature must be passed as a string, not float.

## Common mistakes

### Temperature Parameter
✅ **Correct**:
```bash
--sampling_temp "0.1"    # String with quotes
```

❌ **Wrong**:
```bash
--sampling_temp 0.1      # Float without quotes - may cause errors
--sampling_temp 0.1,0.2  # Multiple temps need proper format
```

### Fixed Positions JSONL
✅ **Correct**:
```json
{"A": [1, 2, 3, 10, 11], "B": [5, 6]}
```

❌ **Wrong**:
```json
{"A": "1,2,3,10,11"}     # String instead of list
{A: [1, 2, 3]}           # Missing quotes on key
{"A": [1,2,3,]}          # Trailing comma
```

### Chain Selection
✅ **Correct**:
```bash
--pdb_path_chains A,B    # No spaces
```

❌ **Wrong**:
```bash
--pdb_path_chains A, B   # Space after comma
--pdb_path_chains "A,B"  # Quotes may cause issues
```

### Amino Acid Biases
```bash
# Bias toward certain AAs (positive = favor)
--bias_AA_jsonl '{"A": {"A": 1.5, "W": -2.0}}'

# Omit specific AAs globally
--omit_AAs "CM"  # No cysteine or methionine

# Per-position omission
--omit_AA_jsonl '{"A": {"1": "C", "2": "CM"}}'
```

### Multi-Chain Design
```bash
# Design chains A and B together
--pdb_path_chains A,B

# Tie chains (same sequence)
--tied_positions_jsonl tied.jsonl
```

## Variants Comparison

| Variant | Use Case | Key Difference |
|---------|----------|----------------|
| ProteinMPNN | General | Original model |
| SolubleMPNN | Expression | Trained on soluble proteins |
| LigandMPNN | Small molecules | Ligand-aware context |

## Output format

```
output/
├── seqs/
│   └── backbone.fa          # FASTA sequences
└── backbone_pdb/
    └── backbone_0001.pdb    # PDBs with designed sequence
```

### FASTA Header Format
```
>backbone_0001, score=1.234, global_score=1.234, seq_recovery=0.85
MKTAYIAKQRQISFVKSHFSRQLE...
```

## Common workflows

### Binder Sequence Design
```bash
python protein_mpnn_run.py \
  --pdb_path binder_backbone.pdb \
  --out_folder output/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1" \
  --pdb_path_chains B  # Design binder chain only
```

### Interface Redesign
```bash
# Fix core, design interface
python protein_mpnn_run.py \
  --pdb_path complex.pdb \
  --fixed_positions_jsonl core_positions.jsonl \
  --num_seq_per_target 32
```

### Multi-State Design
```bash
# Design for multiple conformations
python protein_mpnn_run.py \
  --pdb_path_multi state1.pdb,state2.pdb \
  --num_seq_per_target 16
```

## Sample output

### Successful run
```
$ python protein_mpnn_run.py --pdb_path backbone.pdb --out_folder output/ --num_seq_per_target 8
Loading model weights...
Designing sequences for backbone.pdb
Generated 8 sequences in 2.3 seconds

output/seqs/backbone.fa:
>backbone_0001, score=1.234, global_score=1.189, seq_recovery=0.82
MKTAYIAKQRQISFVKSHFSRQLEERGLTKE...
>backbone_0002, score=1.198, global_score=1.156, seq_recovery=0.79
MKTAYIAKQRQISFVKSQFSRQLDERGLTKE...
```

**What good output looks like:**
- Score: 1.0-2.0 (lower = more confident)
- Seq recovery: 0.3-0.6 for de novo, 0.7-0.9 for redesign
- Diverse sequences (not all identical) when temp > 0.1

## Decision tree

```
Should I use ProteinMPNN?
│
├─ Have a backbone structure?
│  ├─ Yes → Continue below
│  └─ No → Use RFdiffusion first
│
├─ What's in the binding site?
│  ├─ Nothing / protein only → ProteinMPNN ✓
│  ├─ Small molecule / ligand → Use LigandMPNN
│  └─ Metal / cofactor → Use LigandMPNN
│
├─ Priority?
│  ├─ Solubility/expression → Consider SolubleMPNN
│  ├─ Speed → ProteinMPNN ✓
│  └─ AF2 optimization → Consider ColabDesign
│
└─ Need fixed positions?
   ├─ Yes → Use --fixed_positions_jsonl
   └─ No → ProteinMPNN ✓ (design all)
```

## Typical performance

| Campaign Size | Time (T4) | Cost (Modal) | Notes |
|---------------|-----------|--------------|-------|
| 100 backbones × 8 seq | 15-20 min | ~$2 | Standard |
| 500 backbones × 8 seq | 1-1.5h | ~$8 | Large campaign |
| 1000 backbones × 16 seq | 3-4h | ~$18 | Comprehensive |

**Throughput**: ~50-100 sequences/minute on T4 GPU.

---

## Verify

```bash
grep -c "^>" output/seqs/*.fa  # Should match backbone_count × num_seq_per_target
```

---

## Troubleshooting

**Low sequence diversity**: Increase sampling_temp to 0.2-0.3
**Poor recovery**: Decrease sampling_temp to 0.1
**OOM errors**: Reduce batch_size
**Unwanted cysteines**: Use --omit_AAs "C"

### Error interpretation

| Error | Cause | Fix |
|-------|-------|-----|
| `RuntimeError: CUDA out of memory` | Long protein or large batch | Reduce batch_size or use larger GPU |
| `KeyError: 'A'` | Chain not in PDB | Check chain IDs in your PDB file |
| `JSONDecodeError` | Invalid JSONL format | Validate JSON syntax (see Common Mistakes) |
| `IndexError: list index` | Empty chain or residue list | Check PDB has atoms, not just HEADER |

---

**Next**: Structure prediction for validation → `protein-qc` for filtering.
