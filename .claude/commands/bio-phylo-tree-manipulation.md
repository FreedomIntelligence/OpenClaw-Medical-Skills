# bio-phylo-tree-manipulation

> Modify phylogenetic tree structure using Biopython Bio.Phylo. Use when rooting trees with outgroups or midpoint, pruning taxa, collapsing clades, ladderizing branches, or extracting subtrees.

**Available tools:** Read, Bash

# Tree Manipulation

Modify phylogenetic tree structure: rooting, pruning, ladderizing, and subtree extraction.

## Required Import

```python
from Bio import Phylo
from io import StringIO
```

## Rooting Trees

### Root with Outgroup

```python
tree = Phylo.read('tree.nwk', 'newick')

# Root with single taxon
tree.root_with_outgroup({'name': 'Outgroup'})

# Root with multiple taxa (must be monophyletic)
outgroup = [{'name': 'TaxonA'}, {'name': 'TaxonB'}]
if tree.is_monophyletic(outgroup):
    tree.root_with_outgroup(*outgroup)
else:
    print('Outgroup is not monophyletic')
```

### Root at Midpoint

```python
tree = Phylo.read('tree.nwk', 'newick')
tree.root_at_midpoint()
```

### Check Rooting Status

```python
# Check if tree is rooted (bifurcating at root)
print(f'Is bifurcating: {tree.is_bifurcating()}')

# Count children of root
root = tree.root
print(f'Root has {len(root.clades)} children')
# 2 children = rooted, 3+ children = unrooted
```

## Ladderizing

Sort clades for consistent visual presentation.

```python
tree = Phylo.read('tree.nwk', 'newick')

# Larger clades at bottom
tree.ladderize()

# Larger clades at top
tree.ladderize(reverse=True)

Phylo.write(tree, 'ladderized.nwk', 'newick')
```

## Pruning Trees

### Remove Specific Taxa

```python
tree = Phylo.read('tree.nwk', 'newick')

# Find and remove a taxon
target = tree.find_any(name='TaxonToRemove')
if target:
    tree.prune(target)

# Remove multiple taxa
for name in ['TaxonA', 'TaxonB', 'TaxonC']:
    target = tree.find_any(name=name)
    if target:
        tree.prune(target)
```

### Keep Only Specified Taxa

```python
tree = Phylo.read('tree.nwk', 'newick')
keep_taxa = {'Human', 'Chimp', 'Gorilla'}

terminals = tree.get_terminals()
for term in terminals:
    if term.name not in keep_taxa:
        tree.prune(term)
```

## Collapsing Clades

Collapse branches below a threshold.

```python
tree = Phylo.read('tree.nwk', 'newick')

# Collapse single clade
target = tree.find_any(name='SomeInternalNode')
if target:
    tree.collapse(target)

# Collapse all clades matching criteria (branch length threshold)
tree.collapse_all(lambda c: c.branch_length and c.branch_length < 0.01)

# Collapse all poorly-supported nodes
tree.collapse_all(lambda c: c.confidence is not None and c.confidence < 70)
```

## Extracting Subtrees

### Get Clade as Subtree

```python
tree = Phylo.read('tree.nwk', 'newick')

# Find common ancestor of taxa
clade = tree.common_ancestor({'name': 'Human'}, {'name': 'Chimp'})

# The clade itself can be treated as a subtree
Phylo.draw_ascii(clade)

# Get all terminals in this clade
subtree_taxa = [t.name for t in clade.get_terminals()]
print(f'Subtree contains: {subtree_taxa}')
```

### Extract Subtree by Common Ancestor

```python
tree = Phylo.read('tree.nwk', 'newick')

# Find MRCA (Most Recent Common Ancestor)
taxa = [{'name': 'Human'}, {'name': 'Chimp'}, {'name': 'Gorilla'}]
mrca = tree.common_ancestor(*taxa)
print(f'MRCA branch length: {mrca.branch_length}')
```

## Tree Traversal

```python
tree = Phylo.read('tree.nwk', 'newick')

# Iterate all clades (preorder by default)
for clade in tree.find_clades():
    print(clade.name, clade.branch_length)

# Level-order traversal (breadth-first)
for clade in tree.find_clades(order='level'):
    print(clade.name)

# Postorder traversal
for clade in tree.find_clades(order='postorder'):
    print(clade.name)

# Only terminal nodes
for term in tree.get_terminals():
    print(term.name)

# Only internal nodes
for internal in tree.get_nonterminals():
    print(internal)
```

## Finding Clades

```python
tree = Phylo.read('tree.nwk', 'newick')

# Find by name
clade = tree.find_any(name='Human')

# Find all matching criteria
matches = tree.find_clades(branch_length=lambda x: x and x > 0.5)
for m in matches:
    print(f'{m.name}: {m.branch_length}')

# Find by terminal status
terminals = list(tree.find_clades(terminal=True))
internals = list(tree.find_clades(terminal=False))
```

## Getting Path Between Nodes

```python
tree = Phylo.read('tree.nwk', 'newick')

# Path from root to a node
target = tree.find_any(name='Human')
path = tree.get_path(target)
print(f'Path from root to Human: {len(path)} nodes')
for clade in path:
    print(f'  {clade.name}: {clade.branch_length}')

# Trace path between any two nodes
human = tree.find_any(name='Human')
mouse = tree.find_any(name='Mouse')
trace = tree.trace(human, mouse)
print(f'Path Human to Mouse: {len(trace)} nodes')
```

## Checking Tree Properties

```python
tree = Phylo.read('tree.nwk', 'newick')

# Check if monophyletic
taxa = [tree.find_any(name='Human'), tree.find_any(name='Chimp')]
taxa = [t for t in taxa if t is not None]
print(f'Is monophyletic: {tree.is_monophyletic(taxa)}')

# Check if bifurcating
print(f'Is bifurcating: {tree.is_bifurcating()}')

# Check if preterminal (parent of only terminals)
for clade in tree.get_nonterminals():
    print(f'{clade}: is_preterminal={clade.is_preterminal()}')
```

## Modifying Branch Lengths

```python
tree = Phylo.read('tree.nwk', 'newick')

# Set missing branch lengths
for clade in tree.find_clades():
    if clade.branch_length is None:
        clade.branch_length = 0.0

# Scale all branch lengths
scale_factor = 100  # Convert to percent divergence
for clade in tree.find_clades():
    if clade.branch_length:
        clade.branch_length *= scale_factor

# Remove branch lengths (convert to cladogram)
for clade in tree.find_clades():
    clade.branch_length = None
```

## Renaming Taxa

```python
tree = Phylo.read('tree.nwk', 'newick')

# Rename individual taxon
target = tree.find_any(name='OldName')
if target:
    target.name = 'NewName'

# Batch rename from mapping
name_map = {'Hsap': 'Human', 'Ptro': 'Chimp', 'Mmus': 'Mouse'}
for term in tree.get_terminals():
    if term.name in name_map:
        term.name = name_map[term.name]

Phylo.write(tree, 'renamed.nwk', 'newick')
```

## Counting Nodes

```python
tree = Phylo.read('tree.nwk', 'newick')

n_terminals = len(tree.get_terminals())
n_internals = len(tree.get_nonterminals())
n_total = tree.count_terminals() + len(tree.get_nonterminals())

print(f'Terminals: {n_terminals}')
print(f'Internal nodes: {n_internals}')
print(f'Total nodes: {n_total}')
```

## Tree Depths

```python
tree = Phylo.read('tree.nwk', 'newick')

# Get depths from root
depths = tree.depths()
for clade, depth in depths.items():
    if clade.is_terminal():
        print(f'{clade.name}: depth={depth:.3f}')

# Get maximum depth (tree height)
max_depth = max(depths.values())
print(f'Tree height: {max_depth:.3f}')
```

## Splitting Clades

```python
tree = Phylo.read('tree.nwk', 'newick')

# Split a terminal into multiple children
target = tree.find_any(name='TaxonA')
if target and target.is_terminal():
    target.split(n=2, branch_length=0.05)  # Creates 2 children

# Split with specific branch lengths
target.split(branch_length=[0.1, 0.2, 0.3])  # Creates 3 children
```

## Generating Random Trees

```python
from Bio.Phylo.BaseTree import Tree

# Generate random bifurcating tree
taxa = ['Human', 'Chimp', 'Gorilla', 'Mouse', 'Rat']
random_tree = Tree.randomized(taxa)
Phylo.draw_ascii(random_tree)

# With branch lengths
random_tree = Tree.randomized(taxa, branch_length=1.0)
```

## Quick Reference: Tree Methods

| Method | Description |
|--------|-------------|
| `root_with_outgroup()` | Reroot using outgroup |
| `root_at_midpoint()` | Reroot at midpoint |
| `ladderize()` | Sort branches by size |
| `prune()` | Remove a clade |
| `collapse()` | Collapse a clade into polytomy |
| `collapse_all()` | Collapse all matching clades |
| `split()` | Split clade into children |
| `trace()` | Get path between two clades |
| `Tree.randomized()` | Generate random tree |
| `common_ancestor()` | Find MRCA of taxa |
| `find_any()` | Find first matching clade |
| `find_clades()` | Find all matching clades |
| `get_path()` | Get path from root to clade |
| `depths()` | Get depth of all clades |
| `is_monophyletic()` | Check if taxa form clade |
| `is_bifurcating()` | Check if tree is binary |

## Related Skills

- tree-io - Read and write tree files
- tree-visualization - Draw modified trees
- distance-calculations - Build trees from alignments
