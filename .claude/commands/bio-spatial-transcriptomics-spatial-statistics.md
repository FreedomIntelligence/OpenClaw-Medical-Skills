# bio-spatial-transcriptomics-spatial-statistics

> Compute spatial statistics for spatial transcriptomics data using Squidpy. Calculate Moran's I, Geary's C, spatial autocorrelation, co-occurrence analysis, and neighborhood enrichment. Use when computing spatial autocorrelation or co-occurrence statistics.

## Version Compatibility

Reference examples tested with: numpy 1.26+, pandas 2.2+, scanpy 1.10+, scipy 1.12+, squidpy 1.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Statistics

Compute spatial statistics and identify spatially variable features.

## Required Imports

```python
import squidpy as sq
import scanpy as sc
import pandas as pd
import numpy as np
```

## Compute Spatial Autocorrelation (Moran's I)

**Goal:** Identify genes whose expression is spatially autocorrelated across tissue.

**Approach:** Build a spatial neighbor graph, then compute Moran's I statistic per gene to measure clustering of similar values.

**"Find spatially variable genes"** -> Compute Moran's I autocorrelation on the spatial neighbor graph to rank genes by spatial patterning.

```python
# Requires spatial neighbors
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)

# Compute Moran's I for all genes (can be slow)
sq.gr.spatial_autocorr(adata, mode='moran')

# Or for specific genes
sq.gr.spatial_autocorr(adata, mode='moran', genes=['GENE1', 'GENE2', 'GENE3'])

# Results stored in adata.uns['moranI']
moran_results = adata.uns['moranI']
print(moran_results.head(20))
```

## Interpret Moran's I

```python
# Moran's I ranges from -1 to 1
# I > 0: positive spatial autocorrelation (similar values cluster)
# I = 0: random spatial distribution
# I < 0: negative spatial autocorrelation (dissimilar values cluster)

# Get significantly spatially variable genes
svg = moran_results[moran_results['pval_norm'] < 0.05].sort_values('I', ascending=False)
print(f'Found {len(svg)} spatially variable genes (p < 0.05)')
print('\nTop 10 spatially variable genes:')
print(svg.head(10)[['I', 'pval_norm']])
```

## Compute Geary's C

```python
# Alternative spatial autocorrelation measure
sq.gr.spatial_autocorr(adata, mode='geary')

# Results in adata.uns['gearyC']
geary_results = adata.uns['gearyC']
# C < 1: positive spatial autocorrelation
# C = 1: random
# C > 1: negative spatial autocorrelation
```

## Co-occurrence Analysis

**Goal:** Determine whether cell types co-localize or segregate in tissue space.

**Approach:** Compute pairwise co-occurrence probabilities at multiple distance intervals using Squidpy.

```python
# Analyze co-localization of cell types/clusters
# First, ensure you have cluster labels
sc.pp.neighbors(adata)
sc.tl.leiden(adata)

# Compute co-occurrence
sq.gr.co_occurrence(adata, cluster_key='leiden')

# Results in adata.uns['leiden_co_occurrence']
# Visualize co-occurrence
sq.pl.co_occurrence(adata, cluster_key='leiden')
```

## Interpret Co-occurrence

```python
co_occ = adata.uns['leiden_co_occurrence']
occ_matrix = co_occ['occ']  # Occurrence matrix
interval = co_occ['interval']  # Distance intervals

# occ_matrix[i, j, k] = occurrence of cluster j around cluster i at distance interval k
print(f'Occurrence matrix shape: {occ_matrix.shape}')
print(f'Distance intervals: {interval}')
```

## Neighborhood Enrichment

**Goal:** Test whether cell type clusters are enriched or depleted in each other's spatial neighborhoods.

**Approach:** Run permutation-based neighborhood enrichment test, yielding z-scores for each cluster pair.

```python
# Test if clusters are enriched in each other's neighborhoods
sq.gr.nhood_enrichment(adata, cluster_key='leiden')

# Results in adata.uns['leiden_nhood_enrichment']
# zscore > 0: clusters co-localize more than expected
# zscore < 0: clusters avoid each other

# Visualize
sq.pl.nhood_enrichment(adata, cluster_key='leiden')
```

## Extract Enrichment Z-scores

```python
enrichment = adata.uns['leiden_nhood_enrichment']
zscore = enrichment['zscore']
clusters = adata.obs['leiden'].cat.categories

# Convert to DataFrame
zscore_df = pd.DataFrame(zscore, index=clusters, columns=clusters)
print('Neighborhood enrichment z-scores:')
print(zscore_df)
```

## Ripley's Statistics

```python
# Ripley's K/L function for point pattern analysis (single-cell resolution data)
sq.gr.ripley(adata, cluster_key='leiden', mode='L')

# Results in adata.uns['leiden_ripley']
sq.pl.ripley(adata, cluster_key='leiden')
```

## Centrality Scores

```python
# Compute centrality of each cell type
sq.gr.centrality_scores(adata, cluster_key='leiden')

# Results in adata.uns['leiden_centrality_scores']
centrality = adata.uns['leiden_centrality_scores']
print(centrality)
```

## Interaction Matrix

```python
# Build interaction matrix between clusters
sq.gr.interaction_matrix(adata, cluster_key='leiden')

# Results in adata.uns['leiden_interactions']
interactions = adata.uns['leiden_interactions']
print(interactions)
```

## Custom Spatial Statistic

```python
from scipy.stats import pearsonr

def spatial_correlation(adata, gene1, gene2):
    '''Compute spatial correlation between two genes'''
    expr1 = adata[:, gene1].X.toarray().flatten()
    expr2 = adata[:, gene2].X.toarray().flatten()
    r, p = pearsonr(expr1, expr2)
    return r, p

r, p = spatial_correlation(adata, 'GENE1', 'GENE2')
print(f'Spatial correlation: r={r:.3f}, p={p:.2e}')
```

## Local Moran's I (LISA)

**Goal:** Identify local hotspots and coldspots of gene expression in tissue space.

**Approach:** Compute Local Indicators of Spatial Association (LISA) using PySAL, which assigns each spot to a cluster-outlier quadrant (HH, HL, LH, LL).

```python
from esda.moran import Moran_Local
from libpysal.weights import KNN

# Build weights matrix
coords = adata.obsm['spatial']
w = KNN.from_array(coords, k=6)
w.transform = 'r'

# Compute local Moran's I for a gene
gene_expr = adata[:, 'GENE1'].X.toarray().flatten()
lisa = Moran_Local(gene_expr, w)

# Add to adata
adata.obs['GENE1_lisa'] = lisa.Is
adata.obs['GENE1_lisa_q'] = lisa.q  # Quadrant (HH, HL, LH, LL)
```

## Batch Spatial Statistics

**Goal:** Efficiently compute spatial autocorrelation for a large set of genes.

**Approach:** Subset to highly variable genes before running Moran's I to reduce computation time.

```python
# Compute Moran's I for top variable genes only
hvg = adata.var_names[adata.var['highly_variable']][:500]
sq.gr.spatial_autocorr(adata, mode='moran', genes=hvg)

results = adata.uns['moranI']
significant = results[results['pval_norm'] < 0.01]
print(f'{len(significant)} genes with significant spatial autocorrelation')
```

## Related Skills

- spatial-neighbors - Build spatial graphs (prerequisite)
- spatial-domains - Identify spatial domains
- spatial-visualization - Visualize spatial statistics
