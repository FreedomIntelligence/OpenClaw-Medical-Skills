# bio-phylo-tree-visualization

> Draw and export phylogenetic trees using Biopython Bio.Phylo with matplotlib. Use when creating publication-quality tree figures, customizing colors and labels, or exporting to image formats.

**Available tools:** Read, Bash

# Tree Visualization

Draw phylogenetic trees using matplotlib integration.

## Required Import

```python
from Bio import Phylo
import matplotlib.pyplot as plt
```

## ASCII Tree Display

```python
tree = Phylo.read('tree.nwk', 'newick')

# Quick text representation
print(tree)

# ASCII art diagram
Phylo.draw_ascii(tree)
```

## Basic Tree Drawing

```python
tree = Phylo.read('tree.nwk', 'newick')

# Simple plot (opens interactive window)
Phylo.draw(tree)
plt.show()

# Save to file
fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(tree, axes=ax)
plt.savefig('tree.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Customizing Tree Appearance

```python
fig, ax = plt.subplots(figsize=(12, 10))
Phylo.draw(tree, axes=ax, do_show=False,
           branch_labels=lambda c: f'{c.branch_length:.2f}' if c.branch_length else '',
           label_func=lambda c: c.name if c.is_terminal() else '')

ax.set_title('Phylogenetic Tree')
plt.savefig('custom_tree.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Label Customization

```python
# Custom label function
def custom_labels(clade):
    if clade.is_terminal():
        return clade.name
    elif clade.confidence:
        return f'{clade.confidence:.0f}'
    return ''

fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(tree, axes=ax, label_func=custom_labels)
plt.savefig('labeled_tree.png', dpi=300)
plt.close()
```

## Branch Labels (Bootstrap, Lengths)

```python
# Show branch lengths
def branch_length_labels(clade):
    if clade.branch_length:
        return f'{clade.branch_length:.3f}'
    return ''

fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(tree, axes=ax, branch_labels=branch_length_labels)
plt.savefig('with_lengths.png', dpi=300)
plt.close()

# Show bootstrap values (stored in clade.confidence or clade.name for internal nodes)
def bootstrap_labels(clade):
    if not clade.is_terminal() and clade.confidence:
        return f'{clade.confidence:.0f}'
    return ''

Phylo.draw(tree, axes=ax, branch_labels=bootstrap_labels)
```

## Coloring Trees

```python
# Color specific clades before drawing
tree = Phylo.read('tree.nwk', 'newick')

# Set colors for specific clades (PhyloXML trees support this natively)
for clade in tree.find_clades():
    if clade.name and 'Human' in clade.name:
        clade.color = 'red'
    elif clade.name and 'Mouse' in clade.name:
        clade.color = 'blue'

fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(tree, axes=ax)
plt.savefig('colored_tree.png', dpi=300)
plt.close()
```

## Highlighting Clades

```python
from Bio.Phylo.PhyloXML import BranchColor

# Convert to PhyloXML for color support
phyloxml_tree = tree.as_phyloxml()

# Color a clade and its descendants
target = phyloxml_tree.find_any(name='Human')
if target:
    target.color = BranchColor.from_name('red')

fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(phyloxml_tree, axes=ax)
plt.savefig('highlighted.png', dpi=300)
plt.close()
```

## Multiple Output Formats

```python
tree = Phylo.read('tree.nwk', 'newick')
tree.ladderize()

fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(tree, axes=ax, do_show=False)

# PNG (raster, good for presentations)
plt.savefig('tree.png', dpi=300, bbox_inches='tight')

# PDF (vector, good for publications)
plt.savefig('tree.pdf', bbox_inches='tight')

# SVG (vector, good for web)
plt.savefig('tree.svg', bbox_inches='tight')

plt.close()
```

## Figure Size and Layout

```python
# Adjust figure size based on tree size
n_taxa = len(tree.get_terminals())
height = max(8, n_taxa * 0.3)  # Scale with number of taxa

fig, ax = plt.subplots(figsize=(10, height))
Phylo.draw(tree, axes=ax, do_show=False)
plt.tight_layout()
plt.savefig('scaled_tree.png', dpi=300)
plt.close()
```

## Phylo.draw() Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `tree` | Tree | Tree object to draw |
| `axes` | Axes | Matplotlib axes (optional) |
| `label_func` | callable | Function to generate tip labels |
| `branch_labels` | callable/dict | Function or dict for branch labels |
| `do_show` | bool | Call plt.show() automatically (default True) |

## Pre-Processing for Better Visualization

```python
tree = Phylo.read('tree.nwk', 'newick')

# Ladderize for cleaner appearance
tree.ladderize(reverse=True)

# Set missing branch lengths to small value
for clade in tree.find_clades():
    if clade.branch_length is None:
        clade.branch_length = 0.001

fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(tree, axes=ax)
plt.savefig('clean_tree.png', dpi=300)
plt.close()
```

## Side-by-Side Tree Comparison

```python
tree1 = Phylo.read('tree1.nwk', 'newick')
tree2 = Phylo.read('tree2.nwk', 'newick')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

Phylo.draw(tree1, axes=ax1, do_show=False)
ax1.set_title('Tree 1')

Phylo.draw(tree2, axes=ax2, do_show=False)
ax2.set_title('Tree 2')

plt.tight_layout()
plt.savefig('comparison.png', dpi=300)
plt.close()
```

## Hide Axis and Frame

```python
fig, ax = plt.subplots(figsize=(10, 8))
Phylo.draw(tree, axes=ax, do_show=False)

ax.axis('off')  # Remove axis
ax.set_frame_on(False)  # Remove frame

plt.savefig('clean_tree.png', dpi=300, bbox_inches='tight', transparent=True)
plt.close()
```

## Deprecated Functions

| Function | Status | Alternative |
|----------|--------|-------------|
| `draw_graphviz()` | Removed (1.79) | Use `Phylo.draw()` for rectangular trees |

For radial (circular) tree layouts, use external tools like ETE3 or DendroPy.

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Labels overlap | Too many taxa | Increase figure height |
| No branch lengths | Missing in file | Set defaults or use cladogram |
| Colors not showing | Wrong tree format | Convert to PhyloXML first |
| Figure not saving | `do_show=True` | Set `do_show=False` before savefig |

## Related Skills

- tree-io - Read and write tree files
- tree-manipulation - Ladderize and reroot before visualization
- distance-calculations - Build trees from alignments for visualization
