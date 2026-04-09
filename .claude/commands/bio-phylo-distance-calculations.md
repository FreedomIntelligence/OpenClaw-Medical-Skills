# bio-phylo-distance-calculations

> Compute evolutionary distances and build phylogenetic trees using Biopython Bio.Phylo.TreeConstruction. Use when creating distance matrices from alignments, building NJ/UPGMA trees, or generating bootstrap consensus trees.

**Available tools:** Read, Bash

# Distance Calculations and Tree Building

Compute distances from alignments and construct phylogenetic trees.

## Required Import

```python
from Bio import Phylo, AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Phylo.TreeConstruction import DistanceMatrix
from Bio.Phylo.TreeConstruction import ParsimonyScorer, ParsimonyTreeConstructor, NNITreeSearcher
from Bio.Phylo.Consensus import strict_consensus, majority_consensus, bootstrap_trees, bootstrap_consensus
```

## Distance Matrix from Alignment

```python
from Bio import AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator

alignment = AlignIO.read('alignment.fasta', 'fasta')

# Create calculator with distance model
calculator = DistanceCalculator('identity')  # Simple identity-based distance
dm = calculator.get_distance(alignment)
print(dm)

# Available models for DNA
calculator = DistanceCalculator('blastn')  # BLASTN-style distance

# Available models for protein
calculator = DistanceCalculator('blosum62')  # BLOSUM62-based distance
```

## Available Distance Models

| Model | Type | Description |
|-------|------|-------------|
| `identity` | DNA/Protein | 1 - (identical positions / total) |
| `blastn` | DNA | BLASTN scoring distance |
| `trans` | DNA | Transition/transversion weighted |
| `blosum62` | Protein | BLOSUM62 matrix distance |
| `blosum45` | Protein | BLOSUM45 matrix distance |
| `blosum80` | Protein | BLOSUM80 matrix distance |
| `pam250` | Protein | PAM250 matrix distance |
| `pam30` | Protein | PAM30 matrix distance |

## Building Trees with Distance Methods

### Neighbor Joining (NJ)

```python
from Bio import AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

alignment = AlignIO.read('alignment.fasta', 'fasta')
calculator = DistanceCalculator('identity')
dm = calculator.get_distance(alignment)

constructor = DistanceTreeConstructor()
nj_tree = constructor.nj(dm)
Phylo.draw_ascii(nj_tree)
```

### UPGMA

```python
constructor = DistanceTreeConstructor()
upgma_tree = constructor.upgma(dm)
Phylo.draw_ascii(upgma_tree)
```

### One-Step Tree Building

```python
# Build tree directly from alignment
constructor = DistanceTreeConstructor(calculator, 'nj')
tree = constructor.build_tree(alignment)

# Or with UPGMA
constructor = DistanceTreeConstructor(calculator, 'upgma')
tree = constructor.build_tree(alignment)
```

## Pairwise Distances Between Taxa

```python
from Bio import Phylo

tree = Phylo.read('tree.nwk', 'newick')

# Distance between two taxa (sum of branch lengths)
taxon1 = tree.find_any(name='Human')
taxon2 = tree.find_any(name='Mouse')
dist = tree.distance(taxon1, taxon2)
print(f'Distance Human-Mouse: {dist:.4f}')

# All pairwise distances
terminals = tree.get_terminals()
for i, t1 in enumerate(terminals):
    for t2 in terminals[i+1:]:
        d = tree.distance(t1, t2)
        print(f'{t1.name}-{t2.name}: {d:.4f}')
```

## Creating Distance Matrix Manually

```python
from Bio.Phylo.TreeConstruction import DistanceMatrix

names = ['A', 'B', 'C', 'D']
# Lower triangular matrix (including diagonal)
matrix = [
    [0],
    [0.1, 0],
    [0.2, 0.15, 0],
    [0.3, 0.25, 0.2, 0]
]
dm = DistanceMatrix(names, matrix)
print(dm)

# Build tree from custom matrix
constructor = DistanceTreeConstructor()
tree = constructor.nj(dm)
```

## Parsimony Tree Construction

```python
from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import ParsimonyScorer, NNITreeSearcher, ParsimonyTreeConstructor

alignment = AlignIO.read('alignment.fasta', 'fasta')

# Create scorer and searcher
scorer = ParsimonyScorer()
searcher = NNITreeSearcher(scorer)

# Build parsimony tree (needs starting tree)
constructor = DistanceTreeConstructor(DistanceCalculator('identity'), 'nj')
starting_tree = constructor.build_tree(alignment)

pars_constructor = ParsimonyTreeConstructor(searcher, starting_tree)
pars_tree = pars_constructor.build_tree(alignment)

print(f'Parsimony score: {scorer.get_score(pars_tree, alignment)}')
Phylo.draw_ascii(pars_tree)
```

## Bootstrap Analysis

```python
from Bio import AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Phylo.Consensus import bootstrap_trees, bootstrap_consensus, majority_consensus

alignment = AlignIO.read('alignment.fasta', 'fasta')
calculator = DistanceCalculator('identity')
constructor = DistanceTreeConstructor(calculator, 'nj')

# Generate bootstrap trees
boot_trees = list(bootstrap_trees(alignment, 100, constructor))
print(f'Generated {len(boot_trees)} bootstrap trees')

# Get bootstrap consensus
consensus = bootstrap_consensus(alignment, 100, constructor, majority_consensus)
Phylo.draw_ascii(consensus)
```

## Consensus Tree Methods

```python
from Bio.Phylo.Consensus import strict_consensus, majority_consensus, adam_consensus

trees = list(Phylo.parse('bootstrap.nwk', 'newick'))

# Strict consensus (only clades in ALL trees)
strict = strict_consensus(trees)

# Majority rule consensus (clades in >50% of trees)
majority = majority_consensus(trees, cutoff=0.5)

# Adam consensus
adam = adam_consensus(trees)

Phylo.draw_ascii(majority)
```

## Tree Depths and Total Length

```python
tree = Phylo.read('tree.nwk', 'newick')

# Total branch length
total = tree.total_branch_length()
print(f'Total branch length: {total:.4f}')

# Depths from root to each node
depths = tree.depths()
for clade, depth in depths.items():
    if clade.is_terminal():
        print(f'{clade.name}: {depth:.4f}')

# Maximum depth (tree height)
tree_height = max(depths.values())
print(f'Tree height: {tree_height:.4f}')
```

## Comparing Tree Distances

```python
tree1 = Phylo.read('tree1.nwk', 'newick')
tree2 = Phylo.read('tree2.nwk', 'newick')

# Compare total branch lengths
len1 = tree1.total_branch_length()
len2 = tree2.total_branch_length()
print(f'Tree 1 total: {len1:.4f}')
print(f'Tree 2 total: {len2:.4f}')

# Compare specific pairwise distances
taxa = ['Human', 'Mouse']
t1 = [tree1.find_any(name=t) for t in taxa]
t2 = [tree2.find_any(name=t) for t in taxa]

d1 = tree1.distance(t1[0], t1[1])
d2 = tree2.distance(t2[0], t2[1])
print(f'Human-Mouse distance: Tree1={d1:.4f}, Tree2={d2:.4f}')
```

## Complete Pipeline: Alignment to Bootstrapped Tree

```python
from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Phylo.Consensus import bootstrap_consensus, majority_consensus

alignment = AlignIO.read('sequences.aln', 'clustal')
print(f'Alignment: {len(alignment)} sequences, {alignment.get_alignment_length()} positions')

calculator = DistanceCalculator('identity')
constructor = DistanceTreeConstructor(calculator, 'nj')

# Build simple tree
simple_tree = constructor.build_tree(alignment)
simple_tree.ladderize()

# Build bootstrap consensus (100 replicates)
consensus_tree = bootstrap_consensus(alignment, 100, constructor, majority_consensus)
consensus_tree.ladderize()

Phylo.write(simple_tree, 'nj_tree.nwk', 'newick')
Phylo.write(consensus_tree, 'bootstrap_consensus.nwk', 'newick')
```

## Quick Reference: Distance Models

### DNA Models
| Model | Description |
|-------|-------------|
| `identity` | Simple mismatch counting |
| `blastn` | BLASTN-style scoring |
| `trans` | Weights transitions vs transversions |

### Protein Models
| Model | Description |
|-------|-------------|
| `blosum62` | General proteins |
| `blosum45` | Divergent proteins |
| `blosum80` | Similar proteins |
| `pam250` | Distant homologs |
| `pam30` | Close homologs |

## Related Skills

- tree-io - Save constructed trees to files
- tree-visualization - Draw resulting trees
- tree-manipulation - Root and process built trees
- alignment/alignment-io - Read alignments for tree building
- alignment/msa-statistics - Alignment quality before tree building
