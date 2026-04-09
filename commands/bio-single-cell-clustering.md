# bio-single-cell-clustering

> Dimensionality reduction and clustering for single-cell RNA-seq using Seurat (R) and Scanpy (Python). Use for running PCA, computing neighbors, clustering with Leiden/Louvain algorithms, generating UMAP/tSNE embeddings, and visualizing clusters. Use when performing dimensionality reduction and clustering on single-cell data.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+, matplotlib 3.8+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Single-Cell Clustering

Dimensionality reduction, neighbor graph construction, and clustering.

## Scanpy (Python)

**Goal:** Reduce dimensions, build neighbor graphs, cluster cells, and visualize with UMAP/tSNE using Scanpy.

**Approach:** Run PCA for dimensionality reduction, construct a k-NN graph, apply Leiden community detection, and compute UMAP embedding.

**"Cluster cells and find groups"** → Reduce dimensionality with PCA, build a neighborhood graph, partition cells into clusters, and embed in 2D for visualization.

### Required Imports

```python
import scanpy as sc
import matplotlib.pyplot as plt
```

### PCA

```python
# Run PCA
sc.tl.pca(adata, n_comps=50, svd_solver='arpack')

# Visualize variance explained
sc.pl.pca_variance_ratio(adata, n_pcs=50)

# Visualize PCA
sc.pl.pca(adata, color='n_genes_by_counts')
```

### Determine Number of PCs

```python
# Elbow plot to choose number of PCs
sc.pl.pca_variance_ratio(adata, n_pcs=50, log=True)

# Typically use 10-50 PCs based on elbow
n_pcs = 30
```

### Compute Neighbors

```python
# Build k-nearest neighbor graph
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
```

### Clustering (Leiden - Recommended)

```python
# Leiden clustering (preferred over Louvain)
sc.tl.leiden(adata, resolution=0.5)

# Higher resolution = more clusters
sc.tl.leiden(adata, resolution=1.0, key_added='leiden_r1')

# View cluster sizes
adata.obs['leiden'].value_counts()
```

### Clustering (Louvain)

```python
# Louvain clustering (alternative)
sc.tl.louvain(adata, resolution=0.5)
```

### UMAP

```python
# Compute UMAP embedding
sc.tl.umap(adata, min_dist=0.3, spread=1.0)

# Visualize clusters on UMAP
sc.pl.umap(adata, color='leiden')

# Color by gene expression
sc.pl.umap(adata, color=['leiden', 'CD3D', 'MS4A1', 'CD14'])
```

### tSNE

```python
# Compute tSNE (slower than UMAP)
sc.tl.tsne(adata, n_pcs=30, perplexity=30)

# Visualize
sc.pl.tsne(adata, color='leiden')
```

### Complete Clustering Pipeline

**Goal:** Run end-to-end clustering from preprocessed data to UMAP visualization.

**Approach:** Chain PCA, neighbor computation, Leiden clustering, and UMAP into a single pipeline.

```python
import scanpy as sc

# Assumes preprocessed data
adata = sc.read_h5ad('preprocessed.h5ad')

# PCA
sc.tl.pca(adata, n_comps=50)

# Neighbors
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Cluster
sc.tl.leiden(adata, resolution=0.5)

# UMAP
sc.tl.umap(adata)

# Visualize
sc.pl.umap(adata, color='leiden')
```

### Exploring Different Resolutions

**Goal:** Evaluate clustering at multiple resolutions to find the appropriate granularity.

**Approach:** Iterate over resolution values, cluster at each, and compare cluster counts on UMAP.

```python
# Try multiple resolutions
for res in [0.2, 0.5, 0.8, 1.0, 1.5]:
    sc.tl.leiden(adata, resolution=res, key_added=f'leiden_r{res}')
    n_clusters = adata.obs[f'leiden_r{res}'].nunique()
    print(f'Resolution {res}: {n_clusters} clusters')

# Compare on UMAP
sc.pl.umap(adata, color=['leiden_r0.2', 'leiden_r0.5', 'leiden_r1.0'], ncols=3)
```

### PAGA (Trajectory Inference)

```python
# Partition-based graph abstraction
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, color='leiden')

# Use PAGA for UMAP initialization
sc.tl.umap(adata, init_pos='paga')
```

---

## Seurat (R)

**Goal:** Reduce dimensions, build neighbor graphs, cluster cells, and visualize with UMAP/tSNE using Seurat.

**Approach:** Run PCA, determine optimal PC count, construct SNN graph, apply Louvain clustering, and compute UMAP embedding.

### Required Libraries

```r
library(Seurat)
library(ggplot2)
```

### PCA

```r
# Run PCA
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(seurat_obj), npcs = 50)

# Visualize PCA
DimPlot(seurat_obj, reduction = 'pca')
VizDimLoadings(seurat_obj, dims = 1:2, reduction = 'pca')

# Heatmaps of PC genes
DimHeatmap(seurat_obj, dims = 1:6, cells = 500, balanced = TRUE)
```

### Determine Number of PCs

```r
# Elbow plot
ElbowPlot(seurat_obj, ndims = 50)

# JackStraw (more rigorous but slow)
seurat_obj <- JackStraw(seurat_obj, num.replicate = 100)
seurat_obj <- ScoreJackStraw(seurat_obj, dims = 1:20)
JackStrawPlot(seurat_obj, dims = 1:20)
```

### Find Neighbors

```r
# Build KNN graph
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)
```

### Find Clusters

```r
# Louvain clustering (default)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

# View cluster assignments
head(Idents(seurat_obj))
table(Idents(seurat_obj))
```

### Exploring Different Resolutions

```r
# Try multiple resolutions
seurat_obj <- FindClusters(seurat_obj, resolution = c(0.2, 0.5, 0.8, 1.0, 1.5))

# Results stored in metadata
head(seurat_obj@meta.data)

# Compare resolutions
library(clustree)
clustree(seurat_obj, prefix = 'RNA_snn_res.')
```

### UMAP

```r
# Run UMAP
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)

# Visualize
DimPlot(seurat_obj, reduction = 'umap', label = TRUE)

# Split by sample
DimPlot(seurat_obj, reduction = 'umap', split.by = 'sample')
```

### tSNE

```r
# Run tSNE
seurat_obj <- RunTSNE(seurat_obj, dims = 1:30)

# Visualize
DimPlot(seurat_obj, reduction = 'tsne')
```

### Complete Clustering Pipeline

**Goal:** Run end-to-end Seurat clustering from preprocessed data to UMAP visualization.

**Approach:** Chain PCA, neighbor finding, cluster detection, and UMAP into a single pipeline.

```r
library(Seurat)

# Assumes preprocessed data
seurat_obj <- readRDS('preprocessed.rds')

# PCA
seurat_obj <- RunPCA(seurat_obj, npcs = 50, verbose = FALSE)

# Neighbors
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)

# Cluster
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

# UMAP
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)

# Visualize
DimPlot(seurat_obj, reduction = 'umap', label = TRUE)
```

### Access Embeddings

```r
# Get PCA coordinates
pca_coords <- Embeddings(seurat_obj, reduction = 'pca')

# Get UMAP coordinates
umap_coords <- Embeddings(seurat_obj, reduction = 'umap')

# Add to metadata for custom plotting
seurat_obj$UMAP_1 <- umap_coords[, 1]
seurat_obj$UMAP_2 <- umap_coords[, 2]
```

---

## Parameter Reference

| Parameter | Typical Values | Effect |
|-----------|---------------|--------|
| n_pcs | 10-50 | More PCs capture more variance |
| n_neighbors | 10-30 | Higher = smoother, lower = more local |
| resolution | 0.2-2.0 | Higher = more clusters |
| min_dist (UMAP) | 0.1-0.5 | Lower = tighter clusters |

## Method Comparison

| Step | Scanpy | Seurat |
|------|--------|--------|
| PCA | `sc.tl.pca()` | `RunPCA()` |
| Neighbors | `sc.pp.neighbors()` | `FindNeighbors()` |
| Cluster | `sc.tl.leiden()` | `FindClusters()` |
| UMAP | `sc.tl.umap()` | `RunUMAP()` |
| tSNE | `sc.tl.tsne()` | `RunTSNE()` |

## Related Skills

- preprocessing - Data must be preprocessed before clustering
- markers-annotation - Find markers for each cluster
- data-io - Save clustered results
