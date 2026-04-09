# ligandmpnn

> Ligand-aware protein sequence design using LigandMPNN. Use this skill when: (1) Designing sequences around small molecules, (2) Enzyme active site design, (3) Ligand binding pocket optimization, (4) Metal coordination site design, (5) Cofactor binding proteins.
For standard protein design, use proteinmpnn. For solubility optimization, use solublempnn.

# LigandMPNN Ligand-Aware Design

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10 |
| CUDA | 11.0+ | 11.7+ |
| GPU VRAM | 8GB | 16GB (T4) |
| RAM | 8GB | 16GB |

## How to run

> **First time?** See [Installation Guide](../../docs/installation.md) to set up Modal and 
### Option 1: Modal (recommended)
```bash
cd modal run modal_ligandmpnn.py \
  --pdb-path protein_ligand.pdb \
  --num-seq-per-target 16 \
  --sampling-temp 0.1
```

**GPU**: T4 (16GB) | **Timeout**: 600s default

### Option 2: Local installation
```bash
git clone https://github.com/dauparas/LigandMPNN.git
cd LigandMPNN

python run.py \
  --pdb_path protein_ligand.pdb \
  --out_folder output/ \
  --num_seq_per_target 16
```

## Key parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `--pdb_path` | required | path | PDB with ligand |
| `--num_seq_per_target` | 1 | 1-1000 | Sequences per structure |
| `--sampling_temp` | "0.1" | "0.0001-1.0" | Temperature (string!) |
| `--ligand_mpnn_use_side_chain_context` | true | bool | Use ligand context |

## Ligand Specification

### In PDB File
Ligand must be present as HETATM records:
```
ATOM    ...protein atoms...
HETATM  1  C1  LIG A 999      x.xxx  y.yyy  z.zzz  1.00  0.00           C
```

### Supported Ligand Types
- Small molecules (HETATM)
- Metals (Zn, Fe, Mg, Ca, etc.)
- Cofactors (NAD, FAD, ATP)
- DNA/RNA

## Output format

```
output/
├── seqs/
│   └── protein.fa          # FASTA sequences
└── protein_pdb/
    └── protein_0001.pdb    # PDBs with designed sequence
```

## Sample output

### Successful run
```
$ python run.py --pdb_path enzyme_substrate.pdb --out_folder output/ --num_seq_per_target 8
Loading LigandMPNN model weights...
Processing enzyme_substrate.pdb
Found ligand: LIG (12 atoms)
Generated 8 sequences in 3.1 seconds

output/seqs/enzyme_substrate.fa:
>enzyme_substrate_0001, score=1.45, global_score=1.38
MKTAYIAKQRQISFVKSHFSRQLE...
>enzyme_substrate_0002, score=1.52, global_score=1.41
MKTAYIAKQRQISFVKSQFSRQLD...
```

**What good output looks like:**
- Score: 1.0-2.0 (lower = more confident)
- Ligand detected and incorporated in context
- Active site residues preserved or optimized

## Decision tree

```
Should I use LigandMPNN?
│
├─ What's in your binding site?
│  ├─ Small molecule / ligand → LigandMPNN ✓
│  ├─ Metal ion (Zn, Fe, etc.) → LigandMPNN ✓
│  ├─ Cofactor (NAD, FAD, ATP) → LigandMPNN ✓
│  ├─ DNA/RNA → LigandMPNN ✓
│  └─ Nothing / protein only → Use ProteinMPNN
│
├─ What type of design?
│  ├─ Enzyme active site → LigandMPNN ✓
│  ├─ Metal binding site → LigandMPNN ✓
│  ├─ Protein-protein binder → Use ProteinMPNN
│  └─ De novo scaffold → Use ProteinMPNN
│
└─ Priority?
   ├─ Solubility/expression → Consider SolubleMPNN
   └─ Ligand context accuracy → LigandMPNN ✓
```

## Typical performance

| Campaign Size | Time (T4) | Cost (Modal) | Notes |
|---------------|-----------|--------------|-------|
| 100 backbones × 8 seq | 15-20 min | ~$2 | Standard |
| 500 backbones × 8 seq | 1-1.5h | ~$8 | Large campaign |

**Throughput**: ~50-100 sequences/minute on T4 GPU.

---

## Verify

```bash
grep -c "^>" output/seqs/*.fa  # Should match backbone_count × num_seq_per_target
```

---

## Troubleshooting

**Ligand not recognized**: Check HETATM format, verify ligand residue name
**Poor binding residues**: Increase sampling around active site
**Missing contacts**: Verify ligand coordinates in PDB

### Error interpretation

| Error | Cause | Fix |
|-------|-------|-----|
| `RuntimeError: CUDA out of memory` | Long protein or large batch | Reduce batch_size |
| `KeyError: 'LIG'` | Ligand not found in PDB | Check HETATM records |
| `ValueError: no ligand atoms` | Empty ligand | Verify ligand has atoms in PDB |

---

**Next**: Structure prediction for validation → `protein-qc` for filtering.
