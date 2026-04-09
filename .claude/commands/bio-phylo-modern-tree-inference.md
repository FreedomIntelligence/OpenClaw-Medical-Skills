# bio-phylo-modern-tree-inference

> Build maximum likelihood phylogenetic trees using IQ-TREE2 and RAxML-ng. Use when inferring publication-quality trees with model selection, ultrafast bootstrap, or partitioned analyses from sequence alignments.

**Available tools:** Read, Bash

# Modern ML Tree Inference

Build maximum likelihood phylogenetic trees with automatic model selection and ultrafast bootstrap.

## IQ-TREE2 Basic Usage

```bash
# Simple ML tree with automatic model selection
iqtree2 -s alignment.fasta -m MFP -B 1000 -T AUTO

# -s: input alignment
# -m MFP: ModelFinder Plus (automatic model selection + tree inference)
# -B 1000: 1000 ultrafast bootstrap replicates (minimum recommended for publication)
# -T AUTO: automatic thread detection
```

## IQ-TREE2 Output Files

| File | Description |
|------|-------------|
| `.treefile` | Best ML tree in Newick format |
| `.iqtree` | Full analysis report with model parameters |
| `.log` | Run log |
| `.contree` | Consensus tree with bootstrap support |
| `.splits.nex` | Bootstrap splits in Nexus format |
| `.model.gz` | Model parameters |
| `.bionj` | Initial BIONJ tree |
| `.mldist` | ML distance matrix |
| `.ckp.gz` | Checkpoint file for resuming |

## Model Selection

```bash
# ModelFinder only (no tree inference)
iqtree2 -s alignment.fasta -m MF

# Use specific model
iqtree2 -s alignment.fasta -m GTR+G4 -B 1000

# Test only specific models
iqtree2 -s alignment.fasta -m MF -mset GTR,HKY,K2P

# Protein models
iqtree2 -s protein.fasta -m MFP -B 1000 -st AA
```

## Common DNA Substitution Models

| Model | Parameters | Use Case |
|-------|------------|----------|
| JC | Equal rates | Very simple, rarely appropriate |
| K2P/K80 | Ti/Tv ratio | Simple, some rate variation |
| HKY | Ti/Tv + base freq | Moderate complexity |
| GTR | 6 rates + base freq | Most general, recommended default |
| +G4 | Gamma rate variation | 4 discrete rate categories |
| +I | Invariant sites | Sites that never change |
| +R4 | FreeRate model | More flexible than Gamma |

## Ultrafast Bootstrap

```bash
# Standard ultrafast bootstrap (UFBoot2)
# B>=1000: Minimum for publication. Use 10000 for final analyses.
iqtree2 -s alignment.fasta -m GTR+G4 -B 1000

# Standard bootstrap (slower but more accurate for small datasets)
iqtree2 -s alignment.fasta -m GTR+G4 -b 100

# SH-aLRT test (fast approximate likelihood ratio test)
iqtree2 -s alignment.fasta -m GTR+G4 -alrt 1000

# Both UFBoot and SH-aLRT
iqtree2 -s alignment.fasta -m GTR+G4 -B 1000 -alrt 1000
```

## Interpreting Bootstrap Values

| UFBoot | SH-aLRT | Interpretation |
|--------|---------|----------------|
| >= 95 | >= 80 | Strong support |
| 80-94 | 70-79 | Moderate support |
| < 80 | < 70 | Weak support |

## Partitioned Analysis

For multi-gene datasets with different evolutionary rates:

```bash
# Create partition file (partitions.nex)
cat > partitions.nex << 'EOF'
#nexus
begin sets;
    charset gene1 = 1-500;
    charset gene2 = 501-1200;
    charset gene3 = 1201-1800;
    charpartition mine = HKY:gene1, GTR:gene2, GTR+G:gene3;
end;
EOF

# Run partitioned analysis
iqtree2 -s concat.fasta -p partitions.nex -m MFP -B 1000

# Edge-linked partition model (proportional branch lengths)
iqtree2 -s concat.fasta -q partitions.nex -m MFP -B 1000

# Edge-unlinked (independent branch lengths per partition)
iqtree2 -s concat.fasta -Q partitions.nex -m MFP -B 1000
```

## RAxML-ng Basic Usage

```bash
# Simple ML tree with GTR+G
raxml-ng --all --msa alignment.fasta --model GTR+G --bs-trees 100

# --all: ML search + bootstrapping
# --msa: input alignment
# --model: substitution model
# --bs-trees: number of bootstrap replicates
```

## RAxML-ng Model Specification

```bash
# DNA models
raxml-ng --msa alignment.fasta --model GTR+G4+I

# Protein models (automatic detection)
raxml-ng --msa protein.fasta --model LG+G8+F

# Check alignment and determine model
raxml-ng --check --msa alignment.fasta --model GTR+G
```

## RAxML-ng Output Files

| File | Description |
|------|-------------|
| `.raxml.bestTree` | Best ML tree |
| `.raxml.support` | Tree with bootstrap support values |
| `.raxml.bootstraps` | All bootstrap trees |
| `.raxml.mlTrees` | All ML trees from search |
| `.raxml.log` | Analysis log |
| `.raxml.rba` | Binary alignment (for restart) |

## RAxML-ng Advanced Options

```bash
# Multiple ML searches (find global optimum)
# --tree pars{10}: 10 starting parsimony trees recommended for thorough search
raxml-ng --msa alignment.fasta --model GTR+G --tree pars{10} --prefix ml_search

# Constrained tree search
raxml-ng --msa alignment.fasta --model GTR+G --tree-constraint constraint.tre

# Site likelihoods for topology tests
raxml-ng --sitelh --msa alignment.fasta --model GTR+G --tree candidate.tre
```

## Comparing IQ-TREE2 vs RAxML-ng

| Feature | IQ-TREE2 | RAxML-ng |
|---------|----------|----------|
| Model selection | Built-in ModelFinder | External (ModelTest-NG) |
| Ultrafast bootstrap | Yes (UFBoot2) | No |
| Standard bootstrap | Yes | Yes |
| Partition models | Extensive | Good |
| Speed | Faster for UFBoot | Faster for standard BS |
| Memory | Lower | Higher |
| Checkpointing | Yes | Yes |

## Large Dataset Strategies

```bash
# IQ-TREE2 with reduced memory
iqtree2 -s large.fasta -m GTR+G -B 1000 -T 4 -mem 8G

# Use approximate NNI search
iqtree2 -s large.fasta -m GTR+G -B 1000 -fast

# RAxML-ng with parsimony starting trees
raxml-ng --msa large.fasta --model GTR+G --tree pars{5} --threads 8
```

## Tree Topology Tests

```bash
# IQ-TREE2: AU test comparing trees
iqtree2 -s alignment.fasta -m GTR+G -z trees.nwk -n 0 -zb 10000 -au

# Output interpretation:
# p-AU < 0.05: Reject tree
# p-AU >= 0.05: Cannot reject tree
```

## Constrained Analysis

```bash
# IQ-TREE2: Enforce monophyly constraint
iqtree2 -s alignment.fasta -m GTR+G -g constraint.tre -B 1000

# Constraint file format (Newick with taxa to constrain):
# ((Human,Chimp),Gorilla);
```

## Complete Workflow Example

```bash
# 1. Check alignment
iqtree2 -s alignment.fasta -m GTR+G -n 0

# 2. Find best model
iqtree2 -s alignment.fasta -m MF -T AUTO

# 3. Full analysis with best model
iqtree2 -s alignment.fasta -m GTR+I+G4 -B 1000 -alrt 1000 -T AUTO

# 4. Visualize result
cat alignment.fasta.treefile
```

## Resuming Interrupted Runs

```bash
# IQ-TREE2: Resume from checkpoint
iqtree2 -s alignment.fasta -m GTR+G -B 1000 --redo-tree

# RAxML-ng: Resume
raxml-ng --msa alignment.fasta --model GTR+G --redo
```

## Reproducibility

```bash
# Set random seed for reproducible results
# seed=12345: Any fixed seed ensures reproducibility across runs
iqtree2 -s alignment.fasta -m GTR+G -B 1000 --seed 12345

raxml-ng --msa alignment.fasta --model GTR+G --seed 12345 --bs-trees 100
```

## Related Skills

- tree-io - Read and convert output tree files
- tree-visualization - Visualize trees with bootstrap support
- distance-calculations - Compare with distance-based methods
- alignment/alignment-io - Prepare alignments for tree inference
