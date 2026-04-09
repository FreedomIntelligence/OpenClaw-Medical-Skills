# bio-imaging-mass-cytometry-phenotyping

> Cell type assignment from marker expression in IMC data. Covers manual gating, clustering, and automated classification approaches. Use when assigning cell types to segmented IMC cells based on protein marker expression or when phenotyping cells in multiplexed imaging data.

## Version Compatibility

Reference examples tested with: FlowSOM 2.10+, anndata 0.10+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, scikit-learn 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Cell Phenotyping for IMC

**"Assign cell types to my segmented IMC cells"** → Classify cells based on protein marker expression using clustering, manual gating, or supervised classification approaches.
- Python: `scanpy.tl.leiden()` for unsupervised clustering, then manual annotation
- R: `FlowSOM` for self-organizing map-based phenotyping

## Load Single-Cell Data

```python
import anndata as ad
import scanpy as sc
import pandas as pd
import numpy as np

# Load from h5ad
adata = ad.read_h5ad('imc_segmented.h5ad')

# Or create from CSVs
intensities = pd.read_csv('cell_intensities.csv')
cell_info = pd.read_csv('cell_info.csv')

adata = ad.AnnData(X=intensities.values)
adata.var_names = intensities.columns
adata.obs = cell_info
```

## Data Transformation

```python
# Arcsinh transformation (standard for cytometry)
def arcsinh_transform(adata, cofactor=5):
    adata.X = np.arcsinh(adata.X / cofactor)
    return adata

adata = arcsinh_transform(adata)

# Z-score normalization
sc.pp.scale(adata, max_value=10)
```

## Clustering-Based Phenotyping

```python
# PCA and neighbors
sc.pp.pca(adata, n_comps=15)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=15)

# Clustering
sc.tl.leiden(adata, resolution=0.5)

# UMAP for visualization
sc.tl.umap(adata)

# Plot
sc.pl.umap(adata, color='leiden', save='_clusters.png')
```

## Manual Gating

```python
def gate_cells(adata, marker, threshold, above=True):
    '''Gate cells based on marker expression'''
    values = adata[:, marker].X.flatten()
    if above:
        return values > threshold
    else:
        return values < threshold

# Example gating strategy for T cells
adata.obs['CD45_pos'] = gate_cells(adata, 'CD45', 1.5)
adata.obs['CD3_pos'] = gate_cells(adata, 'CD3', 1.0)
adata.obs['CD8_pos'] = gate_cells(adata, 'CD8', 0.8)
adata.obs['CD4_pos'] = gate_cells(adata, 'CD4', 0.8)

# Assign cell types
def assign_cell_type(row):
    if not row['CD45_pos']:
        return 'Other'
    if not row['CD3_pos']:
        return 'Non-T immune'
    if row['CD8_pos']:
        return 'CD8 T cell'
    if row['CD4_pos']:
        return 'CD4 T cell'
    return 'T cell (other)'

adata.obs['cell_type'] = adata.obs.apply(assign_cell_type, axis=1)
```

## Cluster Annotation

```python
# Find marker genes per cluster
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups_heatmap(adata, n_genes=5, save='_markers.png')

# Manual annotation based on markers
cluster_annotation = {
    '0': 'Epithelial',
    '1': 'CD8 T cell',
    '2': 'CD4 T cell',
    '3': 'Macrophage',
    '4': 'Stromal',
    '5': 'B cell'
}

adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_annotation)
```

## SOM-Based Clustering (FlowSOM-Style)

**Goal:** Cluster cells into phenotypically distinct populations using a self-organizing map approach analogous to the FlowSOM algorithm used in flow cytometry.

**Approach:** Train a self-organizing map on selected phenotype markers, map each cell to its best-matching unit, then apply agglomerative meta-clustering on the SOM node weights to obtain final cell type clusters.

```python
# FlowSOM-style clustering using minisom
# Note: For authentic FlowSOM, use the R CATALYST package which wraps FlowSOM
# This Python approach approximates the SOM + meta-clustering concept
from minisom import MiniSom
from sklearn.cluster import AgglomerativeClustering

# Markers for clustering
phenotype_markers = ['CD45', 'CD3', 'CD8', 'CD4', 'CD20', 'CD68', 'E-cadherin']
X = adata[:, phenotype_markers].X

# Self-Organizing Map
som = MiniSom(10, 10, X.shape[1], sigma=1.5, learning_rate=0.5)
som.random_weights_init(X)
som.train_random(X, 1000)

# Get cluster assignments
winner_coordinates = np.array([som.winner(x) for x in X])
som_clusters = winner_coordinates[:, 0] * 10 + winner_coordinates[:, 1]

# Meta-clustering
meta_clustering = AgglomerativeClustering(n_clusters=10)
meta_labels = meta_clustering.fit_predict(som.get_weights().reshape(-1, X.shape[1]))

# Assign to cells
adata.obs['som_cluster'] = [meta_labels[c] for c in som_clusters]
```

## Automated Annotation

```python
# Use reference-based annotation (similar to CellTypist)
from sklearn.neighbors import KNeighborsClassifier

# If you have a reference dataset with known labels
ref_data = ad.read_h5ad('reference_imc.h5ad')

# Train classifier
knn = KNeighborsClassifier(n_neighbors=15)
knn.fit(ref_data.X, ref_data.obs['cell_type'])

# Predict
adata.obs['predicted_type'] = knn.predict(adata.X)
adata.obs['prediction_prob'] = knn.predict_proba(adata.X).max(axis=1)
```

## Visualize Phenotypes

```python
import matplotlib.pyplot as plt

# UMAP colored by cell type
sc.pl.umap(adata, color='cell_type', save='_celltypes.png')

# Heatmap of markers by cell type
sc.pl.matrixplot(adata, phenotype_markers, groupby='cell_type',
                  dendrogram=True, cmap='RdBu_r', save='_heatmap.png')

# Spatial plot colored by cell type
fig, ax = plt.subplots(figsize=(10, 10))
spatial = adata.obsm['spatial']
for ct in adata.obs['cell_type'].unique():
    mask = adata.obs['cell_type'] == ct
    ax.scatter(spatial[mask, 0], spatial[mask, 1], s=1, label=ct, alpha=0.7)
ax.legend(markerscale=5)
ax.set_aspect('equal')
plt.savefig('spatial_celltypes.png', dpi=150)
```

## Cell Type Frequencies

```python
# Frequencies per image/ROI
freq = adata.obs.groupby(['image_id', 'cell_type']).size().unstack(fill_value=0)
freq_pct = freq.div(freq.sum(axis=1), axis=0) * 100

# Plot
freq_pct.plot(kind='bar', stacked=True, figsize=(12, 6))
plt.ylabel('Percentage')
plt.title('Cell Type Composition')
plt.tight_layout()
plt.savefig('celltype_frequencies.png')
```

## Save Results

```python
# Add annotations to adata
adata.write('imc_phenotyped.h5ad')

# Export cell types
adata.obs[['cell_id', 'cell_type', 'centroid_x', 'centroid_y']].to_csv('cell_phenotypes.csv', index=False)
```

## Related Skills

- cell-segmentation - Generate single-cell data
- spatial-analysis - Analyze spatial patterns of cell types
- single-cell/cell-annotation - Similar annotation concepts
