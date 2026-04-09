# bio-spatial-transcriptomics-spatial-communication

> Analyze cell-cell communication in spatial transcriptomics data using ligand-receptor analysis with Squidpy. Infer intercellular signaling, identify communication pathways, and visualize interaction networks. Use when analyzing cell-cell communication in spatial context.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, squidpy 1.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Cell-Cell Communication

Analyze ligand-receptor interactions and cell-cell communication in spatial data.

## Required Imports

```python
import squidpy as sq
import scanpy as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```

## Ligand-Receptor Analysis with Squidpy

**Goal:** Identify significant ligand-receptor interactions between spatially proximal cell types.

**Approach:** Build a spatial neighbor graph, then run permutation-based ligand-receptor analysis using Squidpy's built-in database.

**"Find cell-cell communication in my spatial data"** -> Test ligand-receptor co-expression between neighboring cell types with permutation-based significance.

```python
# Requires clustered data with cell type annotations
adata = sc.read_h5ad('clustered_spatial.h5ad')

# Build spatial neighbors if not already done
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)

# Run ligand-receptor analysis
sq.gr.ligrec(
    adata,
    cluster_key='cell_type',  # Column with cell type annotations
    n_perms=100,  # Permutations for significance testing
    threshold=0.01,  # P-value threshold
    copy=False,
)

# Results stored in adata.uns['cell_type_ligrec']
```

## Access Ligand-Receptor Results

```python
# Get results dictionary
ligrec_results = adata.uns['cell_type_ligrec']

# Access different result components
means = ligrec_results['means']  # Mean expression
pvalues = ligrec_results['pvalues']  # P-values from permutation test
metadata = ligrec_results['metadata']  # Ligand-receptor pair annotations

print(f'Tested {len(means.columns)} ligand-receptor pairs')
print(f'Cell type combinations: {len(means.index)}')
```

## Filter Significant Interactions

**Goal:** Extract ligand-receptor pairs that pass significance thresholds from permutation results.

**Approach:** Iterate over all cell-type-pair and LR-pair combinations, collecting those with p-values below threshold into a flat DataFrame.

```python
# Get significant interactions
pval_threshold = 0.05

# Flatten results to DataFrame
interactions = []
for source_target in pvalues.index:
    for lr_pair in pvalues.columns:
        pval = pvalues.loc[source_target, lr_pair]
        mean_expr = means.loc[source_target, lr_pair]
        if pval < pval_threshold and not np.isnan(mean_expr):
            source, target = source_target
            ligand, receptor = lr_pair
            interactions.append({
                'source': source,
                'target': target,
                'ligand': ligand,
                'receptor': receptor,
                'mean': mean_expr,
                'pvalue': pval,
            })

interactions_df = pd.DataFrame(interactions)
print(f'Significant interactions: {len(interactions_df)}')
print(interactions_df.head(10))
```

## Visualize Ligand-Receptor Results

```python
# Dot plot of top interactions
sq.pl.ligrec(
    adata,
    cluster_key='cell_type',
    source_groups=['Macrophage', 'T_cell'],  # Filter source cell types
    target_groups=['Epithelial', 'Fibroblast'],  # Filter target cell types
    pvalue_threshold=0.05,
    remove_empty_interactions=True,
)
```

## Specific Ligand-Receptor Pairs

```python
# Analyze specific pairs of interest
pairs_of_interest = [
    ('CD40LG', 'CD40'),
    ('TGFB1', 'TGFBR1'),
    ('CCL2', 'CCR2'),
]

sq.pl.ligrec(
    adata,
    cluster_key='cell_type',
    means_range=(0.5, 5),  # Filter by expression level
    pvalue_threshold=0.01,
)
```

## Custom Ligand-Receptor Database

```python
# Use custom ligand-receptor pairs
custom_pairs = pd.DataFrame({
    'ligand': ['GENE1', 'GENE2', 'GENE3'],
    'receptor': ['GENE4', 'GENE5', 'GENE6'],
})

sq.gr.ligrec(
    adata,
    cluster_key='cell_type',
    interactions=custom_pairs,
    n_perms=100,
)
```

## Interaction Heatmap

**Goal:** Visualize the number of significant interactions between each pair of cell types as a heatmap.

**Approach:** Count significant interactions per source-target pair, reshape into a matrix, and display with imshow.

```python
# Create heatmap of interaction counts per cell type pair
def count_interactions_per_pair(pvalues, threshold=0.05):
    counts = {}
    for source_target in pvalues.index:
        sig_count = (pvalues.loc[source_target] < threshold).sum()
        counts[source_target] = sig_count
    return counts

counts = count_interactions_per_pair(pvalues)

# Convert to matrix
cell_types = adata.obs['cell_type'].unique()
count_matrix = pd.DataFrame(0, index=cell_types, columns=cell_types)
for (source, target), count in counts.items():
    count_matrix.loc[source, target] = count

plt.figure(figsize=(8, 8))
plt.imshow(count_matrix.values, cmap='Reds')
plt.xticks(range(len(cell_types)), cell_types, rotation=45, ha='right')
plt.yticks(range(len(cell_types)), cell_types)
plt.colorbar(label='Number of significant interactions')
plt.title('Cell-cell communication strength')
plt.tight_layout()
plt.savefig('interaction_heatmap.png', dpi=150)
```

## Network Visualization

**Goal:** Display cell-cell communication as a directed network graph with edge weights proportional to interaction strength.

**Approach:** Build a NetworkX DiGraph from significant interactions, with cell types as nodes and interaction counts as edge weights.

```python
import networkx as nx

# Build interaction network
G = nx.DiGraph()

# Add nodes (cell types)
for ct in adata.obs['cell_type'].unique():
    G.add_node(ct)

# Add edges (interactions)
for _, row in interactions_df.iterrows():
    if G.has_edge(row['source'], row['target']):
        G[row['source']][row['target']]['weight'] += 1
    else:
        G.add_edge(row['source'], row['target'], weight=1)

# Draw network
pos = nx.spring_layout(G, k=2, seed=42)
weights = [G[u][v]['weight'] for u, v in G.edges()]

plt.figure(figsize=(10, 10))
nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='lightblue')
nx.draw_networkx_labels(G, pos, font_size=10)
nx.draw_networkx_edges(G, pos, width=[w/max(weights)*5 for w in weights],
                        edge_color='gray', arrows=True, arrowsize=20)
plt.title('Cell-cell communication network')
plt.axis('off')
plt.savefig('communication_network.png', dpi=150)
```

## Spatial Visualization of Communication

```python
# Visualize ligand and receptor expression spatially
ligand = 'CCL2'
receptor = 'CCR2'

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Ligand expression
sc.pl.spatial(adata, color=ligand, ax=axes[0], show=False, title=f'{ligand} (ligand)')

# Receptor expression
sc.pl.spatial(adata, color=receptor, ax=axes[1], show=False, title=f'{receptor} (receptor)')

# Cell types
sc.pl.spatial(adata, color='cell_type', ax=axes[2], show=False, title='Cell types')

plt.tight_layout()
plt.savefig('ligand_receptor_spatial.png', dpi=150)
```

## Compare Communication Between Conditions

**Goal:** Identify differences in cell-cell communication between experimental conditions.

**Approach:** Run ligand-receptor analysis independently per condition, then compare counts of significant interactions.

```python
# Run separately for each condition
for condition in adata.obs['condition'].unique():
    adata_cond = adata[adata.obs['condition'] == condition].copy()
    sq.gr.spatial_neighbors(adata_cond, coord_type='generic', n_neighs=6)
    sq.gr.ligrec(adata_cond, cluster_key='cell_type', n_perms=100)
    adata_cond.uns[f'ligrec_{condition}'] = adata_cond.uns['cell_type_ligrec']

# Compare interaction counts
for condition in ['control', 'treated']:
    results = adata.uns[f'ligrec_{condition}']
    n_sig = (results['pvalues'] < 0.05).sum().sum()
    print(f'{condition}: {n_sig} significant interactions')
```

## Pathway Enrichment of Communication Partners

```python
# Get genes involved in significant interactions
ligands = interactions_df['ligand'].unique()
receptors = interactions_df['receptor'].unique()
comm_genes = list(set(ligands) | set(receptors))

print(f'Genes involved in communication: {len(comm_genes)}')

# Use for pathway enrichment with pathway-analysis skills
# genes_for_enrichment = comm_genes
```

## Export Results

```python
# Save significant interactions
interactions_df.to_csv('significant_interactions.csv', index=False)

# Save as edge list for network tools
edges = interactions_df[['source', 'target', 'ligand', 'receptor', 'mean', 'pvalue']]
edges.to_csv('communication_edges.csv', index=False)
```

## Related Skills

- spatial-neighbors - Build spatial graphs (prerequisite)
- spatial-domains - Identify cell types for communication analysis
- pathway-analysis - Enrich communication genes for pathways
- single-cell/markers-annotation - Annotate cell types
