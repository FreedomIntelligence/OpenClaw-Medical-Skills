# bio-phylo-tree-io

> Read, write, and convert phylogenetic tree files using Biopython Bio.Phylo. Use when parsing Newick, Nexus, PhyloXML, or NeXML tree formats, converting between formats, or handling multiple trees.

**Available tools:** Read, Bash

# Tree I/O

Parse, write, and convert phylogenetic tree files in various formats.

## Required Import

```python
from Bio import Phylo
from io import StringIO
```

## Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| `newick` | .nwk, .tre, .tree | Standard format with branch lengths |
| `nexus` | .nex, .nxs | Rich format with annotations (PAUP, MrBayes) |
| `phyloxml` | .xml | XML format with metadata support |
| `nexml` | .nexml | Modern XML format |
| `cdao` | .rdf | RDF format (limited use) |

## Reading Trees

```python
# Read single tree
tree = Phylo.read('tree.nwk', 'newick')

# Read multiple trees from file
trees = list(Phylo.parse('bootstrap_trees.nwk', 'newick'))
print(f'Loaded {len(trees)} trees')

# Read from string
tree_string = '((A:0.1,B:0.2):0.3,(C:0.4,D:0.5):0.6);'
tree = Phylo.read(StringIO(tree_string), 'newick')

# Read PhyloXML with metadata
tree = Phylo.read('annotated.xml', 'phyloxml')

# Read Nexus (often contains multiple trees)
trees = list(Phylo.parse('mrbayes.nex', 'nexus'))
```

## Writing Trees

```python
# Write single tree
Phylo.write(tree, 'output.nwk', 'newick')

# Write multiple trees
Phylo.write(trees, 'all_trees.nwk', 'newick')

# Write to PhyloXML (preserves metadata)
Phylo.write(tree, 'output.xml', 'phyloxml')

# Write to Nexus
Phylo.write(tree, 'output.nex', 'nexus')
```

## Serialize to String

```python
tree = Phylo.read('tree.nwk', 'newick')

# Get tree as string (useful for embedding, logging, or API responses)
newick_string = format(tree, 'newick')
print(newick_string)  # ((A:0.1,B:0.2):0.3,(C:0.4,D:0.5):0.6);

# Alternative method
newick_string = tree.format('newick')

# Other formats work too
phyloxml_string = format(tree, 'phyloxml')
```

## Format Conversion

```python
# Direct file conversion
Phylo.convert('input.nwk', 'newick', 'output.xml', 'phyloxml')
Phylo.convert('mrbayes.nex', 'nexus', 'trees.nwk', 'newick')

# Convert with processing
tree = Phylo.read('input.nwk', 'newick')
tree.ladderize()  # Sort branches
Phylo.write(tree, 'sorted.nwk', 'newick')
```

## Quick Tree Inspection

```python
tree = Phylo.read('tree.nwk', 'newick')

# Print ASCII representation
print(tree)

# ASCII tree diagram
Phylo.draw_ascii(tree)

# Basic tree properties
print(f'Total branch length: {tree.total_branch_length()}')
print(f'Number of terminals: {len(tree.get_terminals())}')
print(f'Is bifurcating: {tree.is_bifurcating()}')
```

## Accessing Tree Structure

```python
# Get all terminal (leaf) nodes
terminals = tree.get_terminals()
for term in terminals:
    print(f'{term.name}: branch_length={term.branch_length}')

# Get all internal nodes
nonterminals = tree.get_nonterminals()

# Get all clades (nodes)
all_clades = list(tree.find_clades())

# Find specific clade by name
clade = tree.find_any(name='Human')
```

## Tree from Newick String Patterns

```python
# Simple tree (no branch lengths)
tree = Phylo.read(StringIO('((A,B),(C,D));'), 'newick')

# With branch lengths
tree = Phylo.read(StringIO('((A:0.1,B:0.2):0.3,(C:0.4,D:0.5):0.6);'), 'newick')

# With internal node names
tree = Phylo.read(StringIO('((A,B)AB,(C,D)CD)root;'), 'newick')

# With bootstrap values (internal node names)
tree = Phylo.read(StringIO('((A:0.1,B:0.2)95:0.3,(C:0.4,D:0.5)80:0.6);'), 'newick')
```

## Working with PhyloXML Metadata

```python
# PhyloXML supports rich annotations
tree = Phylo.read('annotated.xml', 'phyloxml')

for clade in tree.find_clades():
    if clade.confidences:
        print(f'{clade.name}: confidence={clade.confidences[0].value}')
    if hasattr(clade, 'taxonomy') and clade.taxonomy:
        print(f'{clade.name}: taxonomy={clade.taxonomy.scientific_name}')

# Convert Newick to PhyloXML (adds metadata capabilities)
newick_tree = Phylo.read('simple.nwk', 'newick')
phyloxml_tree = newick_tree.as_phyloxml()
```

## Handling Multiple Trees

```python
# Parse bootstrap or posterior trees
trees = list(Phylo.parse('bootstrap.nwk', 'newick'))
print(f'Loaded {len(trees)} bootstrap trees')

# Process each tree
for i, tree in enumerate(trees):
    print(f'Tree {i}: {len(tree.get_terminals())} taxa')

# Write subset of trees
Phylo.write(trees[:100], 'first_100.nwk', 'newick')
```

## Iterating Over Large Tree Files

```python
# Memory-efficient iteration (doesn't load all trees at once)
for tree in Phylo.parse('large_file.nwk', 'newick'):
    if tree.total_branch_length() > 1.0:
        print(f'Long tree: {tree.total_branch_length()}')
```

## Common Newick Format Variations

| Input | Description |
|-------|-------------|
| `(A,B,C);` | Unrooted, no lengths |
| `((A,B),C);` | Rooted topology |
| `(A:0.1,B:0.2);` | With branch lengths |
| `((A,B)X,C);` | Internal node named X |
| `((A,B):0.5[90],C);` | Branch with bootstrap |

## Error Handling

```python
from Bio import Phylo
from io import StringIO

# Check for valid newick
tree_string = '((A,B),(C,D));'
try:
    tree = Phylo.read(StringIO(tree_string), 'newick')
    print('Valid tree')
except Exception as e:
    print(f'Parse error: {e}')

# Handle missing branch lengths
tree = Phylo.read('tree.nwk', 'newick')
for clade in tree.find_clades():
    if clade.branch_length is None:
        clade.branch_length = 0.0  # Set default
```

## Format-Specific Notes

| Format | Strengths | Limitations |
|--------|-----------|-------------|
| Newick | Universal, simple | No metadata |
| Nexus | PAUP/MrBayes compatible | Complex syntax |
| PhyloXML | Rich metadata, colors | Verbose |
| NeXML | Modern, extensible | Less common |

## Related Skills

- tree-visualization - Draw and export tree figures
- tree-manipulation - Root, prune, and modify tree structure
- distance-calculations - Compute distances and build trees from alignments
- alignment/alignment-io - Read MSA files for tree construction
