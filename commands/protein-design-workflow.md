# protein-design-workflow

> End-to-end guidance for protein design pipelines. Use this skill when: (1) Starting a new protein design project, (2) Need step-by-step workflow guidance, (3) Understanding the full design pipeline, (4) Planning compute resources and timelines, (5) Integrating multiple design tools.
For tool selection, use binder-design. For QC thresholds, use protein-qc.

# Protein Design Workflow Guide

## Standard binder design pipeline

### Overview
```
Target Preparation --> Backbone Generation --> Sequence Design
         |                     |                     |
         v                     v                     v
    (pdb skill)          (rfdiffusion)         (proteinmpnn)
                               |                     |
                               v                     v
                        Structure Validation --> Filtering
                               |                     |
                               v                     v
                         (alphafold/chai)      (protein-qc)
```

## Phase 1: Target preparation

### 1.1 Obtain target structure
```bash
# Download from PDB
curl -o target.pdb "https://files.rcsb.org/download/XXXX.pdb"
```

### 1.2 Clean and prepare
```python
# Extract target chain
# Remove waters, ligands if needed
# Trim to binding region + 10A buffer
```

### 1.3 Select hotspots
- Choose 3-6 exposed residues
- Prefer charged/aromatic (K, R, E, D, W, Y, F)
- Check surface accessibility
- Verify residue numbering

**Output**: `target_prepared.pdb`, hotspot list

## Phase 2: Backbone generation

### Option A: RFdiffusion (diverse exploration)
```bash
modal run modal_rfdiffusion.py \
  --pdb target_prepared.pdb \
  --contigs "A1-150/0 70-100" \
  --hotspot "A45,A67,A89" \
  --num-designs 500
```

### Option B: BindCraft (end-to-end)
```bash
modal run modal_bindcraft.py \
  --target-pdb target_prepared.pdb \
  --hotspots "A45,A67,A89" \
  --num-designs 100
```

**Output**: 100-500 backbone PDBs

## Phase 3: Sequence design

### For RFdiffusion backbones
```bash
for backbone in backbones/*.pdb; do
  modal run modal_proteinmpnn.py \
    --pdb-path "$backbone" \
    --num-seq-per-target 8 \
    --sampling-temp 0.1
done
```

**Output**: 8 sequences per backbone (800-4000 total)

## Phase 4: Structure validation

### Predict complexes
```bash
# Prepare FASTA with binder + target
# binder:target format for multimer

modal run modal_colabfold.py \
  --input-faa all_sequences.fasta \
  --out-dir predictions/
```

**Output**: AF2 predictions with pLDDT, ipTM, PAE

## Phase 5: Filtering and selection

### Apply standard thresholds
```python
import pandas as pd

# Load metrics
designs = pd.read_csv('all_metrics.csv')

# Filter
filtered = designs[
    (designs['pLDDT'] > 0.85) &
    (designs['ipTM'] > 0.50) &
    (designs['PAE_interface'] < 10) &
    (designs['scRMSD'] < 2.0) &
    (designs['esm2_pll'] > 0.0)
]

# Rank by composite score
filtered['score'] = (
    0.3 * filtered['pLDDT'] +
    0.3 * filtered['ipTM'] +
    0.2 * (1 - filtered['PAE_interface'] / 20) +
    0.2 * filtered['esm2_pll']
)

top_designs = filtered.nlargest(50, 'score')
```

**Output**: 50-200 filtered candidates

## Resource planning

### Compute requirements

| Stage | GPU | Time (100 designs) |
|-------|-----|-------------------|
| RFdiffusion | A10G | 30 min |
| ProteinMPNN | T4 | 15 min |
| ColabFold | A100 | 4-8 hours |
| Filtering | CPU | 15 min |

### Total timeline
- Small campaign (100 designs): 8-12 hours
- Medium campaign (500 designs): 24-48 hours
- Large campaign (1000+ designs): 2-5 days

## Quality checkpoints

### After backbone generation
- [ ] Visual inspection of diverse backbones
- [ ] Secondary structure present
- [ ] No clashes with target

### After sequence design
- [ ] ESM2 PLL > 0.0 for most sequences
- [ ] No unwanted cysteines (unless intentional)
- [ ] Reasonable sequence diversity

### After validation
- [ ] pLDDT > 0.85
- [ ] ipTM > 0.50
- [ ] PAE_interface < 10
- [ ] Self-consistency RMSD < 2.0 A

### Final selection
- [ ] Diverse sequences (cluster if needed)
- [ ] Manufacturable (no problematic motifs)
- [ ] Reasonable molecular weight

## Common issues

| Problem | Solution |
|---------|----------|
| Low ipTM | Check hotspots, increase designs |
| Poor diversity | Higher temperature, more backbones |
| High scRMSD | Backbone may be unusual |
| Low pLDDT | Check design quality |

## Advanced workflows

### Multi-tool combination
1. RFdiffusion for initial backbones
2. ColabDesign for refinement
3. ProteinMPNN diversification
4. AF2 final validation

### Iterative refinement
1. Run initial campaign
2. Analyze failures
3. Adjust hotspots/parameters
4. Repeat with insights
