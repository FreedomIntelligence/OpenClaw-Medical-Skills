# rfdiffusion

> Generate protein backbones using RFdiffusion, a diffusion-based generative model for de novo protein structure generation. Use this skill when: (1) Designing binder scaffolds for a target protein, (2) Generating novel protein backbones from scratch, (3) Scaffolding functional motifs into new proteins, (4) Specifying hotspot residues for interface design, (5) Creating symmetric oligomers.
For sequence design after backbone generation, use proteinmpnn. For structure validation, use alphafold or chai. For QC thresholds, use protein-qc.

# RFdiffusion Backbone Generation

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.9+ | 3.10 |
| CUDA | 11.7+ | 12.0+ |
| GPU VRAM | 16GB | 24GB (A10G) |
| RAM | 16GB | 32GB |

## How to run

> **First time?** See [Installation Guide](../../docs/installation.md) to set up Modal and 
### Option 1: Modal (recommended)
```bash
# Clone git clone https://github.com/hgbrian/
# Basic binder design
modal run modal_rfdiffusion.py \
  --pdb target.pdb \
  --contigs "A1-150/0 70-100" \
  --hotspot "A45,A67,A89" \
  --num-designs 100

# With custom GPU/timeout
GPU=A100 TIMEOUT=60 modal run modal_rfdiffusion.py \
  --pdb target.pdb \
  --contigs "A1-150/0 70-100" \
  --num-designs 100
```

**GPU**: A10G (24GB) | **Timeout**: 30min default

### Option 2: Local installation
```bash
# Clone and install
git clone https://github.com/RosettaCommons/RFdiffusion.git
cd RFdiffusion && pip install -e .

# Download weights
wget http://files.ipd.uw.edu/pub/RFdiffusion/models/Complex_base_ckpt.pt

# Run inference
python run_inference.py \
  inference.input_pdb=target.pdb \
  contigmap.contigs=[A1-150/0 70-100] \
  ppi.hotspot_res=[A45,A67,A89] \
  inference.num_designs=100
```

## Config Schema (Hydra)

### Contigmap Syntax
```bash
# De novo single chain (50-100 residues)
contigmap.contigs=[50-100]

# Binder + target (A = target chain, fixed with /0)
contigmap.contigs=[A1-150/0 70-100]

# Motif scaffolding (preserve residues, /0 = fixed)
contigmap.contigs=[20-40/0 A10-30/0 20-40]

# Multi-chain binder
contigmap.contigs=[A1-100/0 B1-100/0 60-80]

# Variable length ranges
contigmap.contigs=[A1-150/0 50-100]  # Binder 50-100 AA
```

### Hotspot Specification
```bash
# Residues for interface (chain + resnum, no spaces)
ppi.hotspot_res=[A45,A67,A89]
```

## Common mistakes

### Contig Syntax
✅ **Correct**:
```bash
contigmap.contigs=[A1-150/0 70-100]  # Target fixed (/0), binder variable
```

❌ **Wrong**:
```bash
contigmap.contigs=[A1-150 70-100]    # Missing /0 - target will move!
contigmap.contigs="A1-150/0 70-100"  # Quotes break parsing
contigmap.contigs=[A1-150/0, 70-100] # Comma breaks parsing
```

### Hotspot Residues
✅ **Correct**:
```bash
ppi.hotspot_res=[A45,A67,A89]        # Chain letter + residue number
```

❌ **Wrong**:
```bash
ppi.hotspot_res=[45,67,89]           # Missing chain letter
ppi.hotspot_res=[A45, A67, A89]      # Spaces break parsing
ppi.hotspot_res="A45,A67,A89"        # Quotes break parsing
```

### Complete Parameter Reference

#### Core Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `inference.num_designs` | 10 | 1-10000 | Number of designs to generate |
| `inference.input_pdb` | - | path | Target structure file |
| `inference.output_prefix` | output | string | Output filename prefix |
| `diffuser.T` | 50 | 20-200 | Diffusion timesteps |
| `denoiser.noise_scale_ca` | 1.0 | 0.0-2.0 | CA atom noise (0.5-0.8 = conservative) |
| `denoiser.noise_scale_frame` | 1.0 | 0.0-2.0 | Frame noise |
| `inference.ckpt_override_path` | - | path | Model checkpoint |
| `potentials.guide_scale` | 1.0 | 0.1-10 | Guidance strength |
| `potentials.guide_decay` | constant | string | Decay type |

#### Advanced Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `diffuser.partial_T` | None | Start diffusion from timestep T (partial diffusion) |
| `contigmap.inpaint_str` | None | Sequence positions to inpaint |
| `scaffoldguided.scaffoldguided` | false | Enable scaffold-guided generation |
| `scaffoldguided.target_pdb` | None | Scaffold template PDB |
| `ppi.binderlen` | None | Specify exact binder length |

#### Symmetry Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `symmetry.symmetry` | None | Symmetry type (C2, C3, C4, D2, etc.) |
| `symmetry.recenter` | true | Recenter symmetric assembly |
| `symmetry.radius` | None | Radius constraint for symmetric assembly |

#### Fold Conditioning
| Parameter | Default | Description |
|-----------|---------|-------------|
| `contigmap.provide_seq` | None | Provide sequence for fold conditioning |
| `contigmap.inpaint_seq` | None | Positions for sequence inpainting |

### Model Checkpoints
| Checkpoint | Use Case |
|------------|----------|
| `Complex_base_ckpt.pt` | Binder design (default) |
| `Base_ckpt.pt` | De novo monomers |
| `ActiveSite_ckpt.pt` | Active site scaffolding |
| `InpaintSeq_ckpt.pt` | Sequence inpainting |

## Common workflows

### Binder Design
1. Prepare target PDB (trim to binding region + 10A buffer)
2. Identify 3-6 hotspot residues (exposed, conserved)
3. Generate 100-500 backbones
4. Pass to proteinmpnn for sequence design

### Motif Scaffolding
1. Extract motif coordinates
2. Use `/0` to fix motif in contigmap
3. Generate surrounding scaffold
4. Validate motif preservation (RMSD < 1.5A)

### Symmetric Oligomers
```bash
# C3 symmetric trimer
python run_inference.py \
  symmetry.symmetry=C3 \
  contigmap.contigs=[100-150] \
  inference.num_designs=50

# D2 symmetric tetramer
python run_inference.py \
  symmetry.symmetry=D2 \
  contigmap.contigs=[80-120] \
  symmetry.radius=25

# Supported symmetries: C2, C3, C4, C5, C6, D2, D3, D4, tetrahedral, octahedral
```

### Partial Diffusion (Refinement)
```bash
# Start from existing structure, diffuse from timestep 10
python run_inference.py \
  inference.input_pdb=initial.pdb \
  diffuser.partial_T=10 \
  contigmap.contigs=[A1-100]
```

## Output format

```
output/
├── output_0.pdb       # Generated backbone
├── output_1.pdb
├── ...
└── output_99.pdb
```

Each PDB contains polyalanine backbone - use proteinmpnn for sequence.

## Sample output

### Successful run
```
$ python run_inference.py inference.input_pdb=target.pdb contigmap.contigs=[A1-150/0 70-100] inference.num_designs=100
[INFO] Loading model from Complex_base_ckpt.pt
[INFO] Generating design 1/100...
[INFO] Generating design 50/100...
[INFO] Generating design 100/100...
[INFO] Saved 100 designs to output/

Generated:
output/output_0.pdb (85 residues)
output/output_1.pdb (92 residues)
...
```

**What good output looks like:**
- File size: 3-8 KB per PDB (backbone only)
- Residue count within specified range
- Secondary structure visible in PyMOL (helices/sheets, not random coil)

## Decision tree

```
Should I use RFdiffusion?
│
├─ Need to generate protein backbone?
│  ├─ Yes → Continue below
│  └─ No, already have backbone → Use ProteinMPNN
│
├─ What type of design?
│  ├─ Binder for protein target → RFdiffusion ✓
│  ├─ De novo monomer → RFdiffusion ✓
│  ├─ Motif scaffolding → RFdiffusion ✓
│  └─ Symmetric assembly → RFdiffusion ✓
│
└─ Priority?
   ├─ Need highest success rate → Consider BindCraft
   ├─ Need diversity/exploration → RFdiffusion ✓
   └─ Need all-atom precision → Consider BoltzGen
```

## Typical performance

| Campaign Size | Time (A10G) | Cost (Modal) | Notes |
|---------------|-------------|--------------|-------|
| 100 backbones | 20-30 min | ~$3 | Quick exploration |
| 500 backbones | 1.5-2h | ~$12 | Standard campaign |
| 1000 backbones | 3-4h | ~$25 | Large campaign |

**Expected downstream yield**: ~10-15% of backbones pass full QC after sequence design + validation.

---

## Verify

```bash
ls output/*.pdb | wc -l  # Should match num_designs
```

## Troubleshooting

**Designs lack secondary structure**: Decrease noise_scale to 0.5-0.8
**Binder not contacting hotspots**: Verify residue numbering, increase num_designs
**OOM errors**: Reduce batch size or use A100 GPU
**Slow generation**: Reduce diffuser.T to 25-35

### Error interpretation

| Error | Cause | Fix |
|-------|-------|-----|
| `RuntimeError: CUDA out of memory` | GPU VRAM exceeded | Use A100 or reduce designs per batch |
| `KeyError: 'A'` | Chain not found in PDB | Check chain IDs with `grep ^ATOM target.pdb \| cut -c22 \| sort -u` |
| `ValueError: invalid contig` | Syntax error in contigs | Check for spaces, quotes, commas (see Common Mistakes) |
| `FileNotFoundError: ckpt` | Missing model weights | Download from IPD website |

---

**Next**: `proteinmpnn` for sequence design → structure prediction for validation → `protein-qc` for filtering.
