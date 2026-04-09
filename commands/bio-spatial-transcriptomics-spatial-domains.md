# bio-spatial-transcriptomics-spatial-domains

> Identify spatial domains and tissue regions in spatial transcriptomics data using Squidpy and Scanpy. Cluster spots considering both expression and spatial context to define anatomical regions. Use when identifying tissue domains or spatial regions.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, scikit-learn 1.4+, scipy 1.12+, squidpy 1.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Domain Detection

**"Identify tissue domains in my spatial data"** → Cluster spots/cells considering both gene expression and physical proximity to define anatomically coherent spatial domains.
- Python: `squidpy.gr.spatial_neighbors()` → Leiden clustering with spatial graph, or BayesSpace/SpaGCN

Identify spatial domains and tissue regions by combining expression and spatial information.

## Required Imports

```python
import squidpy as sq
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt
```

## Standard Clustering (Expression Only)

**Goal:** Cluster spots based purely on gene expression, ignoring spatial location.

**Approach:** Build an expression-based neighbor graph, then apply Leiden community detection.

```python
# Standard Leiden clustering (ignores spatial context)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.leiden(adata, resolution=0.5, key_added='leiden')

# Visualize on tissue
sq.pl.spatial_scatter(adata, color='leiden', size=1.3)
```

## Spatial-Aware Clustering with Squidpy

**Goal:** Cluster spots using only spatial proximity to identify contiguous tissue regions.

**Approach:** Build a spatial neighbor graph, then run Leiden clustering on the spatial graph.

```python
# Build spatial neighbors
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)

# Run Leiden on spatial graph
sc.tl.leiden(adata, resolution=0.5, key_added='spatial_leiden', neighbors_key='spatial_neighbors')

sq.pl.spatial_scatter(adata, color='spatial_leiden', size=1.3)
```

## Combined Expression + Spatial Graph

**Goal:** Integrate both expression similarity and spatial proximity for domain detection.

**Approach:** Build separate expression and spatial graphs, normalize each, then combine as a weighted average for clustering.

```python
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize

# Build both graphs
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Combine graphs (weighted average)
spatial_weight = 0.3
spatial_conn = adata.obsp['spatial_connectivities']
expr_conn = adata.obsp['connectivities']

# Normalize
spatial_norm = normalize(spatial_conn, norm='l1', axis=1)
expr_norm = normalize(expr_conn, norm='l1', axis=1)

# Combine
combined = spatial_weight * spatial_norm + (1 - spatial_weight) * expr_norm
adata.obsp['combined_connectivities'] = csr_matrix(combined)

# Cluster on combined graph
sc.tl.leiden(adata, resolution=0.5, key_added='combined_leiden', adjacency=adata.obsp['combined_connectivities'])
```

## BayesSpace (R Integration)

```python
# BayesSpace provides spatial smoothing for domain detection
# Run in R, then import results

# R code (run separately):
# library(BayesSpace)
# sce <- readRDS("sce.rds")
# sce <- spatialPreprocess(sce, platform="Visium")
# sce <- spatialCluster(sce, q=7, nrep=10000)
# saveRDS(sce, "sce_bayesspace.rds")

# Import BayesSpace results
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
pandas2ri.activate()

ro.r('sce <- readRDS("sce_bayesspace.rds")')
spatial_clusters = ro.r('colData(sce)$spatial.cluster')
adata.obs['bayesspace'] = list(spatial_clusters)
```

## STAGATE for Spatial Domains

**Goal:** Detect spatial domains using deep learning with graph attention networks.

**Approach:** Build a spatial graph with STAGATE, train the model to learn spatially-aware embeddings, then cluster on those embeddings.

```python
# STAGATE uses graph attention for spatial domain detection
import STAGATE

# Build graph
STAGATE.Cal_Spatial_Net(adata, rad_cutoff=150)
STAGATE.Stats_Spatial_Net(adata)

# Train STAGATE
adata = STAGATE.train_STAGATE(adata, alpha=0)

# Cluster on STAGATE embeddings
sc.pp.neighbors(adata, use_rep='STAGATE')
sc.tl.leiden(adata, resolution=0.5, key_added='stagate_leiden')
```

## Evaluate Domain Quality

**Goal:** Assess whether identified domains form spatially and transcriptionally coherent regions.

**Approach:** Compute silhouette scores separately for spatial coordinates and expression PCA to quantify domain separation.

```python
# Check if domains are spatially coherent
from sklearn.metrics import silhouette_score

coords = adata.obsm['spatial']
labels = adata.obs['spatial_leiden'].values

# Spatial silhouette score
spatial_silhouette = silhouette_score(coords, labels)
print(f'Spatial silhouette score: {spatial_silhouette:.3f}')

# Expression silhouette score
expr_silhouette = silhouette_score(adata.obsm['X_pca'], labels)
print(f'Expression silhouette score: {expr_silhouette:.3f}')
```

## Refine Domain Boundaries

**Goal:** Smooth noisy domain assignments to produce cleaner spatial boundaries.

**Approach:** Apply iterative majority-vote smoothing using the spatial neighbor graph to reassign each spot to the most common label among its neighbors.

```python
# Smooth domain assignments using spatial neighbors
from scipy import sparse

def smooth_domains(adata, cluster_key, n_iter=1):
    conn = adata.obsp['spatial_connectivities']
    labels = adata.obs[cluster_key].values
    categories = adata.obs[cluster_key].cat.categories

    for _ in range(n_iter):
        new_labels = []
        for i in range(adata.n_obs):
            neighbors = conn[i].nonzero()[1]
            if len(neighbors) > 0:
                neighbor_labels = labels[neighbors]
                # Majority vote
                unique, counts = np.unique(neighbor_labels, return_counts=True)
                new_labels.append(unique[counts.argmax()])
            else:
                new_labels.append(labels[i])
        labels = np.array(new_labels)

    adata.obs[f'{cluster_key}_smoothed'] = pd.Categorical(labels, categories=categories)

smooth_domains(adata, 'leiden', n_iter=2)
sq.pl.spatial_scatter(adata, color=['leiden', 'leiden_smoothed'], ncols=2)
```

## Compare Domain Methods

```python
# Compare different clustering approaches
from sklearn.metrics import adjusted_rand_score

methods = ['leiden', 'spatial_leiden', 'combined_leiden']
for i, m1 in enumerate(methods):
    for m2 in methods[i+1:]:
        ari = adjusted_rand_score(adata.obs[m1], adata.obs[m2])
        print(f'{m1} vs {m2}: ARI = {ari:.3f}')
```

## Domain Markers

**Goal:** Identify marker genes that distinguish each spatial domain from the rest.

**Approach:** Run Wilcoxon rank-sum tests per domain, then extract and visualize top-ranked differentially expressed genes.

```python
# Find marker genes for each domain
sc.tl.rank_genes_groups(adata, groupby='spatial_leiden', method='wilcoxon')

# Get top markers
markers = sc.get.rank_genes_groups_df(adata, group=None)
print(markers.groupby('group').head(5))

# Plot top markers on tissue
top_markers = markers.groupby('group').head(1)['names'].tolist()
sq.pl.spatial_scatter(adata, color=top_markers[:6], ncols=3)
```

## Annotate Domains

**Goal:** Assign biological labels to spatial domain clusters based on marker gene identity.

**Approach:** Map cluster IDs to anatomical region names using a dictionary and visualize the annotated tissue.

```python
# Manual annotation based on markers
domain_annotations = {
    '0': 'White matter',
    '1': 'Cortex layer 1',
    '2': 'Cortex layer 2/3',
    '3': 'Cortex layer 4',
    '4': 'Cortex layer 5',
    '5': 'Cortex layer 6',
}

adata.obs['domain'] = adata.obs['spatial_leiden'].map(domain_annotations)
sq.pl.spatial_scatter(adata, color='domain', size=1.3)
```

## Related Skills

- spatial-neighbors - Build spatial graphs (prerequisite)
- spatial-statistics - Compute spatial statistics per domain
- single-cell/clustering - Standard clustering methods
