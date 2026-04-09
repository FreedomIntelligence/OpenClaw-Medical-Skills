# boltzgen

> All-atom protein design using BoltzGen diffusion model. Use this skill when: (1) Need side-chain aware design from the start, (2) Designing around small molecules or ligands, (3) Want all-atom diffusion (not just backbone), (4) Require precise binding geometries, (5) Using YAML-based configuration.
For backbone-only generation, use rfdiffusion. For sequence-only design, use proteinmpnn. For structure validation, use boltz.

# BoltzGen All-Atom Design

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.11 |
| CUDA | 12.0+ | 12.1+ |
| GPU VRAM | 24GB | 48GB (L40S) |
| RAM | 32GB | 64GB |

## How to run

> **First time?** See [Installation Guide](../../docs/installation.md) to set up Modal and 
### Option 1: Modal (recommended)
```bash
# Clone git clone https://github.com/hgbrian/
# Run BoltzGen (requires YAML config file)
modal run modal_boltzgen.py \
  --input-yaml binder_config.yaml \
  --protocol protein-anything \
  --num-designs 50

# With custom GPU
GPU=L40S modal run modal_boltzgen.py \
  --input-yaml binder_config.yaml \
  --protocol protein-anything \
  --num-designs 100
```

**GPU**: L40S (48GB) recommended | **Timeout**: 120min default

**Available protocols**: `protein-anything`, `peptide-anything`, `protein-small_molecule`, `nanobody-anything`, `antibody-anything`

### Option 2: Local installation
```bash
git clone https://github.com/HannesStark/boltzgen.git
cd boltzgen
pip install -e .

python sample.py config=config.yaml
```

### Option 3: Python API
```python
from boltzgen import BoltzGen

model = BoltzGen.load_pretrained()
designs = model.sample(
    target_pdb="target.pdb",
    num_samples=50,
    binder_length=80
)
```

**GPU**: L40S (48GB) | **Time**: ~30-60s per design

## Key parameters (CLI)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--input-yaml` | required | Path to YAML design specification |
| `--protocol` | `protein-anything` | Design protocol |
| `--num-designs` | 10 | Number of designs to generate |
| `--steps` | all | Pipeline steps to run (e.g., `design inverse_folding`) |

## YAML configuration

BoltzGen uses an **entity-based YAML format** where you specify designed proteins and target structures as entities.

**Important notes:**
- Residue indices use `label_seq_id` (1-indexed), not author residue numbers
- File paths are relative to the YAML file location
- Target files should be in CIF format (PDB also works but CIF preferred)
- Run `boltzgen check config.yaml` to verify your specification before running

### Basic Binder Config
```yaml
entities:
  # Designed protein (variable length 80-140 residues)
  - protein:
      id: B
      sequence: 80..140

  # Target from structure file
  - file:
      path: target.cif
      include:
        - chain:
            id: A
      # Specify binding site residues (optional but recommended)
      binding_types:
        - chain:
            id: A
            binding: 45,67,89
```

### Binder with Specific Binding Site
```yaml
entities:
  - protein:
      id: G
      sequence: 60..100

  - file:
      path: 5cqg.cif
      include:
        - chain:
            id: A
      binding_types:
        - chain:
            id: A
            binding: 343,344,251
      structure_groups: "all"
```

### Peptide Design (Cyclic)
```yaml
entities:
  - protein:
      id: S
      sequence: 10..14C6C3  # With cysteines for disulfide

  - file:
      path: target.cif
      include:
        - chain:
            id: A

constraints:
  - bond:
      atom1: [S, 11, SG]
      atom2: [S, 18, SG]  # Disulfide bond
```

## Design protocols

| Protocol | Use Case |
|----------|----------|
| `protein-anything` | Design proteins to bind proteins or peptides |
| `peptide-anything` | Design cyclic peptides to bind proteins |
| `protein-small_molecule` | Design proteins to bind small molecules |
| `nanobody-anything` | Design nanobody CDRs |
| `antibody-anything` | Design antibody CDRs |

## Output format

```
output/
├── sample_0/
│   ├── design.cif         # All-atom structure (CIF format)
│   ├── metrics.json       # Confidence scores
│   └── sequence.fasta     # Sequence
├── sample_1/
│   └── ...
└── summary.csv
```

**Note**: BoltzGen outputs CIF format. Convert to PDB if needed:
```python
from Bio.PDB import MMCIFParser, PDBIO
parser = MMCIFParser()
structure = parser.get_structure("design", "design.cif")
io = PDBIO()
io.set_structure(structure)
io.save("design.pdb")
```

## Sample output

### Successful run
```
$ modal run modal_boltzgen.py --input-yaml binder.yaml --protocol protein-anything --num-designs 10
Running: boltzgen run binder.yaml --output /tmp/out --protocol protein-anything --num_designs 10
[INFO] Loading BoltzGen model...
[INFO] Generating designs...
[INFO] Running inverse folding...
[INFO] Running structure prediction...
[INFO] Filtering and ranking...
[INFO] Pipeline complete

Results saved to: ./out/boltzgen/2501161234/
```

**Output directory structure:**
```
out/boltzgen/2501161234/
├── intermediate_designs/           # Raw diffusion outputs
│   ├── design_0.cif
│   └── design_0.npz
├── intermediate_designs_inverse_folded/
│   ├── refold_cif/                 # Refolded complexes
│   └── aggregate_metrics_analyze.csv
└── final_ranked_designs/
    ├── final_10_designs/           # Top designs
    └── results_overview.pdf        # Summary plots
```

**What good output looks like:**
- Refolding RMSD < 2.0A (design folds as predicted)
- ipTM > 0.5 (confident interface)
- All designs complete pipeline without errors

## Decision tree

```
Should I use BoltzGen?
│
├─ What type of design?
│  ├─ All-atom precision needed → BoltzGen ✓
│  ├─ Ligand binding pocket → BoltzGen ✓
│  └─ Standard miniprotein → RFdiffusion (faster)
│
├─ What matters most?
│  ├─ Side-chain packing → BoltzGen ✓
│  ├─ Speed / diversity → RFdiffusion
│  ├─ Highest success rate → BindCraft
│  └─ AF2 optimization → ColabDesign
│
└─ Compute resources?
   ├─ Have L40S/A100 (48GB+) → BoltzGen ✓
   └─ Only A10G (24GB) → Consider RFdiffusion
```

## Typical performance

| Campaign Size | Time (L40S) | Cost (Modal) | Notes |
|---------------|-------------|--------------|-------|
| 50 designs | 30-45 min | ~$8 | Quick exploration |
| 100 designs | 1-1.5h | ~$15 | Standard campaign |
| 500 designs | 5-8h | ~$70 | Large campaign |

**Per-design**: ~30-60s for typical binder.

---

## Verify

```bash
find output -name "*.cif" | wc -l  # Should match num_samples
```

---

## Troubleshooting

**Verify config first**: Always run `boltzgen check config.yaml` before running the full pipeline
**Slow generation**: Use fewer designs for initial testing, then scale up
**OOM errors**: Use A100-80GB or reduce `--num-designs`
**Wrong binding site**: Residue indices use `label_seq_id` (1-indexed), check in Molstar viewer

### Error interpretation

| Error | Cause | Fix |
|-------|-------|-----|
| `RuntimeError: CUDA out of memory` | Large design or long protein | Use A100-80GB or reduce designs |
| `FileNotFoundError: *.cif` | Target file not found | File paths are relative to YAML location |
| `ValueError: invalid chain` | Chain not in target | Verify chain IDs with Molstar or PyMOL |
| `modal: command not found` | Modal CLI not installed | Run `pip install modal && modal setup` |

---

**Next**: Validate with `boltz` or `chai` → `protein-qc` for filtering.
