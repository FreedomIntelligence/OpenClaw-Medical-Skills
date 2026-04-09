# bio-spatial-transcriptomics-spatial-preprocessing

> Quality control, filtering, normalization, and feature selection for spatial transcriptomics data. Calculate QC metrics, filter spots/cells, normalize counts, and identify highly variable genes. Use when filtering and normalizing spatial transcriptomics data.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, scanpy 1.10+, squidpy 1.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Preprocessing

**"Preprocess my spatial transcriptomics data"** → Calculate spatial QC metrics (genes/spot, mitochondrial fraction), filter spots by expression and tissue coverage, normalize, and select variable genes.
- Python: `scanpy.pp.calculate_qc_metrics()` → `filter_cells()` → `normalize_total()` on spatial AnnData

QC, filtering, normalization, and feature selection for spatial data.

## Required Imports

```python
import squidpy as sq
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt
```

## Calculate QC Metrics

**Goal:** Compute per-spot and per-gene quality control statistics.

**Approach:** Use Scanpy's `calculate_qc_metrics` to generate total counts, gene counts, and other summary statistics.

```python
# Calculate standard QC metrics
sc.pp.calculate_qc_metrics(adata, inplace=True)

# View QC columns
print(adata.obs[['total_counts', 'n_genes_by_counts']].describe())
print(adata.var[['total_counts', 'n_cells_by_counts']].describe())
```

## Calculate Mitochondrial Content

**Goal:** Quantify mitochondrial gene expression as a quality indicator.

**Approach:** Flag MT-prefixed genes, then compute percentage of counts from mitochondrial genes per spot.

```python
# Mark mitochondrial genes
adata.var['mt'] = adata.var_names.str.startswith('MT-')

# Calculate percent mitochondrial
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
print(f"Mean MT%: {adata.obs['pct_counts_mt'].mean():.1f}")
```

## Visualize QC Metrics on Tissue

**Goal:** Display QC metrics overlaid on tissue coordinates to identify spatial patterns in data quality.

**Approach:** Use Squidpy or Scanpy spatial plots with QC metric columns as color variables.

```python
# Plot QC metrics spatially
sq.pl.spatial_scatter(adata, color=['total_counts', 'n_genes_by_counts', 'pct_counts_mt'], ncols=3)

# Or with Scanpy
sc.pl.spatial(adata, color=['total_counts', 'n_genes_by_counts'], spot_size=1.5)
```

## QC Metric Distributions

```python
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
axes[0].hist(adata.obs['total_counts'], bins=50)
axes[0].set_xlabel('Total counts')
axes[1].hist(adata.obs['n_genes_by_counts'], bins=50)
axes[1].set_xlabel('Genes detected')
axes[2].hist(adata.obs['pct_counts_mt'], bins=50)
axes[2].set_xlabel('MT %')
plt.tight_layout()
```

## Filter Spots

**Goal:** Remove low-quality spots based on count, gene, and mitochondrial thresholds.

**Approach:** Apply sequential filters for minimum counts, minimum genes, and maximum mitochondrial percentage.

```python
# Filter based on QC metrics
print(f'Before filtering: {adata.n_obs} spots')

# Minimum counts and genes
sc.pp.filter_cells(adata, min_counts=500)
sc.pp.filter_cells(adata, min_genes=200)

# Maximum mitochondrial content
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()

print(f'After filtering: {adata.n_obs} spots')
```

## Filter Genes

**Goal:** Remove lowly expressed genes detected in very few spots.

**Approach:** Apply a minimum cell count threshold to drop genes with negligible spatial coverage.

```python
# Remove genes detected in few spots
print(f'Before filtering: {adata.n_vars} genes')
sc.pp.filter_genes(adata, min_cells=10)
print(f'After filtering: {adata.n_vars} genes')
```

## Normalization

**Goal:** Normalize count data to remove library size effects and prepare for downstream analysis.

**Approach:** Store raw counts as a layer, normalize to median total counts, then log-transform.

```python
# Store raw counts
adata.layers['counts'] = adata.X.copy()

# Normalize to median total counts
sc.pp.normalize_total(adata, target_sum=1e4)

# Log transform
sc.pp.log1p(adata)
```

## SCTransform-like Normalization

**Goal:** Apply variance-stabilizing normalization analogous to Seurat's SCTransform.

**Approach:** Compute Pearson residuals from raw counts using Scanpy's experimental module.

```python
# Pearson residuals normalization (similar to SCTransform)
# Requires raw counts
adata_raw = adata.copy()
adata_raw.X = adata_raw.layers['counts']

sc.experimental.pp.normalize_pearson_residuals(adata_raw)
adata.layers['pearson'] = adata_raw.X.copy()
```

## Highly Variable Genes

**Goal:** Identify genes with high expression variability for feature selection.

**Approach:** Use Scanpy's HVG detection with the Seurat v3 flavor on raw count data.

```python
# Find HVGs
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3', layer='counts')

# View HVG stats
print(f"Found {adata.var['highly_variable'].sum()} HVGs")
sc.pl.highly_variable_genes(adata)
```

## Spatially Variable Genes

**Goal:** Identify genes whose expression varies significantly across tissue space.

**Approach:** Build a spatial neighbor graph, then compute Moran's I autocorrelation to rank genes by spatial variability.

```python
# Compute spatial neighbors first
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)

# Find spatially variable genes using Moran's I
sq.gr.spatial_autocorr(adata, mode='moran', genes=adata.var_names[:1000])

# Get top spatially variable genes
svg = adata.uns['moranI'].sort_values('I', ascending=False)
print('Top spatially variable genes:')
print(svg.head(20))
```

## Combine HVG and SVG

**Goal:** Create a unified gene set that captures both expression variability and spatial patterning.

**Approach:** Take the union of highly variable genes and top spatially variable genes for downstream analysis.

```python
# Get union of highly variable and spatially variable genes
hvg = set(adata.var_names[adata.var['highly_variable']])
svg_top = set(adata.uns['moranI'].head(500).index)
selected_genes = hvg | svg_top

print(f'HVG: {len(hvg)}, SVG: {len(svg_top)}, Union: {len(selected_genes)}')

# Subset to selected genes for downstream
adata_subset = adata[:, list(selected_genes)].copy()
```

## Scale Data

```python
# Scale for PCA (use log-normalized data)
sc.pp.scale(adata, max_value=10)
```

## PCA

```python
# Run PCA
sc.tl.pca(adata, n_comps=50)

# Variance explained
sc.pl.pca_variance_ratio(adata, n_pcs=50)
```

## Complete Preprocessing Pipeline

**Goal:** Execute a full spatial preprocessing workflow from raw data to PCA-ready AnnData.

**Approach:** Chain QC, filtering, normalization, HVG selection, scaling, and PCA into a single pipeline.

```python
import squidpy as sq
import scanpy as sc

# Load data
adata = sq.read.visium('spaceranger_output/')

# QC
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

# Filter
sc.pp.filter_cells(adata, min_counts=1000)
sc.pp.filter_cells(adata, min_genes=500)
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()
sc.pp.filter_genes(adata, min_cells=10)

# Normalize
adata.layers['counts'] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# HVGs
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3', layer='counts')

# Scale and PCA
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50)

print(f'Preprocessed: {adata.n_obs} spots, {adata.n_vars} genes')
adata.write_h5ad('preprocessed.h5ad')
```

## Related Skills

- spatial-data-io - Load spatial data
- spatial-neighbors - Build spatial graphs
- single-cell/preprocessing - Non-spatial preprocessing
