# bio-single-cell-lineage-tracing

> Reconstruct cell lineage trees from CRISPR barcode tracing or mitochondrial mutations. Use when studying clonal dynamics, cell fate decisions, or developmental trajectories.

## Version Compatibility

Reference examples tested with: Cassiopeia 2.0+, matplotlib 3.8+, numpy 1.26+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Lineage Tracing Analysis

**"Reconstruct cell lineage trees from CRISPR barcodes"** → Build phylogenetic trees of cell relationships from lineage barcode mutations to study clonal dynamics and cell fate decisions.
- Python: `cassiopeia.tl.ILPSolver(cas_tree)` or `GreedySolver` for tree reconstruction

## Cassiopeia Tree Reconstruction

**Goal:** Reconstruct a cell lineage tree from CRISPR barcode character matrices to reveal clonal relationships among single cells.

**Approach:** Load a character matrix (cells x barcode sites with mutation states), create a CassiopeiaTree object, then solve with a greedy or ILP maximum parsimony solver.

```python
import cassiopeia as cas
import numpy as np

# Load character matrix (cells x barcode sites)
# Values: mutation states at each editing site
# -1 = missing, 0 = unedited, 1+ = mutation states
tree = cas.data.CassiopeiaTree(
    character_matrix=char_matrix,
    cell_meta=cell_metadata
)

# Check data quality
print(f'Cells: {tree.n_cell}')
print(f'Characters: {tree.n_character}')
print(f'Missing fraction: {(char_matrix == -1).mean():.2%}')

# Reconstruct tree with greedy solver
solver = cas.solver.VanillaGreedySolver()
solver.solve(tree)

# Alternative: maximum parsimony
solver = cas.solver.ILPSolver()
solver.solve(tree, convergence_time_limit=600)
```

## Hybrid Solvers

```python
# Hybrid approach: greedy for large trees, ILP refinement
solver = cas.solver.HybridSolver(
    top_solver=cas.solver.VanillaGreedySolver(),
    bottom_solver=cas.solver.ILPSolver(),
    cell_cutoff=200
)
solver.solve(tree)

# Neighbor-joining for comparison
nj_solver = cas.solver.NeighborJoiningSolver(
    dissimilarity_function=cas.solver.dissimilarity_functions.weighted_hamming_distance
)
nj_solver.solve(tree)
```

## From CRISPR Barcodes

```python
# Parse barcode sequences from alignment
barcodes = cas.pp.call_alleles(
    alignment_file='aligned_barcodes.bam',
    reference='barcode_reference.fa',
    min_base_quality=20,
    min_read_quality=10
)

# Filter low-quality calls
barcodes = cas.pp.filter_cells(barcodes, min_umi_per_cell=10)
barcodes = cas.pp.filter_alleles(barcodes, min_cells_per_allele=3)

# Build character matrix
char_matrix = cas.pp.convert_alleles_to_character_matrix(
    barcodes,
    missing_state_indicator=-1
)
```

## Character Matrix QC

```python
# Assess barcode diversity
n_states = (char_matrix > 0).sum(axis=0)
print(f'Mean states per site: {n_states.mean():.1f}')

# Filter uninformative characters
informative = (char_matrix > 0).sum(axis=0) > 1
char_matrix = char_matrix[:, informative]

# Missing data analysis
missing_per_cell = (char_matrix == -1).mean(axis=1)
missing_per_site = (char_matrix == -1).mean(axis=0)

# Remove cells with too much missing data
keep_cells = missing_per_cell < 0.5
char_matrix = char_matrix[keep_cells]
```

## CoSpar for Clonal Dynamics

**Goal:** Infer cell fate transition maps and clonal dynamics from time-series lineage tracing data.

**Approach:** Load lineage-traced AnnData with clone annotations, compute a transition map using intraclone smoothing, then estimate fate probabilities from source to sink populations.

```python
import cospar as cs

adata = cs.read_h5ad('lineage_traced.h5ad')

# Clone information in obs
# 'clone_id' or 'barcode' column required

# Infer transition map
cs.tl.infer_Tmap(
    adata,
    smooth_array=[15, 10, 5],
    intraclone_threshold=0.2,
    neighbor_method='embedding'
)

# Visualize clonal structure
cs.pl.clonal_embedding(adata, color='clone_id')

# Fate probabilities from source to sink
cs.tl.fate_map(
    adata,
    source='HSC',
    sink='Monocyte',
    method='norm-sum'
)

# Plot fate map
cs.pl.fate_map(adata, source='HSC')
```

## CoSpar Trajectory Analysis

```python
# Fate coupling between cell types
cs.tl.fate_coupling(adata, source='HSC')
cs.pl.fate_coupling(adata, source='HSC')

# Transition probabilities over time
cs.tl.transition_map(adata, time_key='day')
cs.pl.transition_map(adata)

# Clone size dynamics
cs.tl.clone_size(adata, time_key='day')
cs.pl.clone_size(adata)
```

## Mitochondrial Lineage (MitoTracing)

```python
# Use mtDNA mutations as natural barcodes
# No engineering required, works on any scRNA-seq

import mito_utils as mu

# Call mtDNA variants from scRNA-seq BAM
variants = mu.call_variants(
    adata,
    bam_path='possorted_genome_bam.bam',
    min_cell_quality=0.9,
    min_coverage=10
)

# Filter variants by quality
variants = mu.filter_variants(
    variants,
    min_cells=10,
    max_af=0.9,
    min_af=0.01
)

# Build distance matrix
distances = mu.compute_distances(variants, method='jaccard')

# Infer tree
tree = mu.build_tree(distances, method='nj')
```

## LARRY Barcode Processing

```python
# For LARRY lentiviral barcoding
import larry

# Parse LARRY barcodes from FASTQ
barcodes = larry.parse_barcodes(
    r1='barcodes_R1.fastq.gz',
    r2='barcodes_R2.fastq.gz',
    whitelist='cell_barcodes.txt'
)

# Match to expression data
adata.obs['clone_id'] = barcodes.loc[adata.obs_names, 'clone_id']

# Clone analysis
clone_sizes = adata.obs['clone_id'].value_counts()
print(f'Number of clones: {len(clone_sizes)}')
print(f'Median clone size: {clone_sizes.median():.0f}')
```

## Tree Visualization

```python
# Plot tree with cell type colors
cas.pl.local.plot_matplotlib(
    tree,
    meta_data=['cell_type'],
    clade_colors=cell_type_colors,
    orient='down',
    figsize=(15, 10)
)

# Interactive tree with itol
cas.pl.local.export_to_itol(tree, 'tree_for_itol.txt')

# ETE3 visualization
cas.pl.local.plot_ete3(
    tree,
    meta_data='cell_type',
    show_internal=False
)
```

## Tree Quality Metrics

```python
# Robinson-Foulds distance between trees
from cassiopeia.critique import compare

rf_distance = compare.robinson_foulds(tree1, tree2)

# Triplet accuracy
triplet_acc = compare.triplets_correct(tree, ground_truth_tree)

# Bootstrap support
bootstrapped_trees = cas.solver.bootstrap(
    tree,
    solver=solver,
    n_replicates=100
)
support = cas.critique.bootstrap_support(tree, bootstrapped_trees)
```

## Integrate with scRNA-seq

```python
import scanpy as sc

# Match tree leaves to expression data
common_cells = set(tree.leaves).intersection(adata.obs_names)
adata_matched = adata[list(common_cells)]
tree_matched = tree.copy()
tree_matched.subset_leaves(list(common_cells))

# Add tree distances to adata
for i, cell in enumerate(adata_matched.obs_names):
    for j, cell2 in enumerate(adata_matched.obs_names):
        if i < j:
            dist = tree_matched.get_distance(cell, cell2)
            # Store in obsp sparse matrix

# Correlate clonal relatedness with transcriptomic similarity
```

## Clonal Expansion Analysis

```python
# Find expanded clones
clone_sizes = adata.obs['clone_id'].value_counts()
expanded = clone_sizes[clone_sizes > 10].index

# Differential expression: expanded vs non-expanded
sc.tl.rank_genes_groups(
    adata,
    groupby='is_expanded',
    method='wilcoxon'
)

# Clone-specific signatures
for clone in expanded[:5]:
    clone_cells = adata[adata.obs['clone_id'] == clone]
    sc.tl.score_genes(clone_cells, gene_list=signature_genes)
```

## Tree Statistics

| Metric | Description | Typical Range |
|--------|-------------|---------------|
| Tree depth | Max root-to-leaf distance | 10-50 |
| Balance (Colless) | Tree asymmetry | 0-1 |
| Sackin index | Sum of root-leaf depths | Varies |
| Gamma statistic | Tempo of diversification | -3 to 3 |

## Related Skills

- single-cell/trajectory-inference - Pseudotime inference
- single-cell/preprocessing - Preprocessing
- phylogenetics/modern-tree-inference - Tree inference concepts
- single-cell/clustering - Cell type assignment
