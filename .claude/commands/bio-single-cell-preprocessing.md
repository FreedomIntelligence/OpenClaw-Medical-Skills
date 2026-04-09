# bio-single-cell-preprocessing

> Quality control, filtering, and normalization for single-cell RNA-seq using Seurat (R) and Scanpy (Python). Use for calculating QC metrics, filtering cells and genes, normalizing counts, identifying highly variable genes, and scaling data. Use when filtering, normalizing, and selecting features in single-cell data.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+, matplotlib 3.8+, numpy 1.26+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Single-Cell Preprocessing

**"Preprocess my scRNA-seq data"** → Filter low-quality cells/genes, normalize counts, identify highly variable genes, and prepare data for dimensionality reduction and clustering.
- Python: `scanpy.pp.filter_cells()` → `normalize_total()` → `log1p()` → `highly_variable_genes()`
- R: `Seurat::NormalizeData()` → `FindVariableFeatures()` → `ScaleData()`

Quality control, filtering, normalization, and feature selection for scRNA-seq data.

## Scanpy (Python)

**Goal:** Preprocess scRNA-seq data through QC filtering, normalization, and feature selection using Scanpy.

**Approach:** Calculate per-cell quality metrics, filter low-quality cells/genes, normalize library sizes, identify highly variable genes, and scale for downstream analysis.

### Required Imports

```python
import scanpy as sc
import numpy as np
```

### Calculate QC Metrics

```python
# Calculate mitochondrial gene percentage
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# Key metrics added to adata.obs:
# - n_genes_by_counts: genes detected per cell
# - total_counts: total UMI counts per cell
# - pct_counts_mt: percentage mitochondrial
```

### Visualize QC Metrics

```python
import matplotlib.pyplot as plt

sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'], jitter=0.4, multi_panel=True)
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')
```

### Filter Cells and Genes

```python
# Filter cells by QC metrics
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_cells(adata, max_genes=5000)

# Filter by mitochondrial percentage
adata = adata[adata.obs['pct_counts_mt'] < 20, :].copy()

# Filter genes
sc.pp.filter_genes(adata, min_cells=3)

print(f'After filtering: {adata.n_obs} cells, {adata.n_vars} genes')
```

### Store Raw Counts

```python
# Store raw counts before normalization
adata.raw = adata.copy()
# Or use layers
adata.layers['counts'] = adata.X.copy()
```

### Normalization

```python
# Library size normalization (normalize to 10,000 counts per cell)
sc.pp.normalize_total(adata, target_sum=1e4)

# Log transform
sc.pp.log1p(adata)
```

### Highly Variable Genes

```python
# Identify highly variable genes (default: top 2000)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3', layer='counts')

# Visualize
sc.pl.highly_variable_genes(adata)

# Check results
print(f'Highly variable genes: {adata.var.highly_variable.sum()}')
```

### Subset to HVGs (Optional)

```python
# Keep only highly variable genes for downstream analysis
adata_hvg = adata[:, adata.var.highly_variable].copy()
```

### Scaling (Z-score)

```python
# Scale to unit variance and zero mean
sc.pp.scale(adata, max_value=10)
```

### Regress Out Confounders

```python
# Regress out unwanted variation (e.g., cell cycle, mitochondrial)
sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])
```

### Complete Preprocessing Pipeline

**Goal:** Run end-to-end preprocessing from raw 10X counts to analysis-ready data.

**Approach:** Chain QC, filtering, normalization, HVG selection, and scaling into a single pipeline.

```python
import scanpy as sc

adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')

# QC
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

# Filter
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata = adata[adata.obs['pct_counts_mt'] < 20, :].copy()

# Store raw
adata.raw = adata.copy()

# Normalize
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# HVGs
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# Scale
adata = adata[:, adata.var.highly_variable].copy()
sc.pp.scale(adata, max_value=10)
```

---

## Seurat (R)

**Goal:** Preprocess scRNA-seq data through QC filtering, normalization, and feature selection using Seurat.

**Approach:** Calculate mitochondrial percentages, filter cells by QC thresholds, normalize with log or SCTransform, identify variable features, and scale for PCA.

### Required Libraries

```r
library(Seurat)
library(ggplot2)
```

### Calculate QC Metrics

```r
# Calculate mitochondrial percentage
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')

# View QC metrics
head(seurat_obj@meta.data)
```

### Visualize QC Metrics

```r
# Violin plots
VlnPlot(seurat_obj, features = c('nFeature_RNA', 'nCount_RNA', 'percent.mt'), ncol = 3)

# Scatter plots
plot1 <- FeatureScatter(seurat_obj, feature1 = 'nCount_RNA', feature2 = 'percent.mt')
plot2 <- FeatureScatter(seurat_obj, feature1 = 'nCount_RNA', feature2 = 'nFeature_RNA')
plot1 + plot2
```

### Filter Cells

```r
# Filter by QC metrics
seurat_obj <- subset(seurat_obj,
    subset = nFeature_RNA > 200 &
             nFeature_RNA < 5000 &
             percent.mt < 20)

cat('After filtering:', ncol(seurat_obj), 'cells\n')
```

### Normalization (Log Normalization)

```r
# Standard log normalization
seurat_obj <- NormalizeData(seurat_obj, normalization.method = 'LogNormalize', scale.factor = 10000)
```

### Normalization (SCTransform)

```r
# SCTransform - recommended for most workflows
# Combines normalization, scaling, and HVG selection
seurat_obj <- SCTransform(seurat_obj, vars.to.regress = 'percent.mt', verbose = FALSE)
```

### Find Variable Features

```r
# Identify highly variable features (if not using SCTransform)
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = 'vst', nfeatures = 2000)

# Visualize
top10 <- head(VariableFeatures(seurat_obj), 10)
plot1 <- VariableFeaturePlot(seurat_obj)
plot2 <- LabelPoints(plot = plot1, points = top10, repel = TRUE)
plot2
```

### Scaling

```r
# Scale data (if not using SCTransform)
all.genes <- rownames(seurat_obj)
seurat_obj <- ScaleData(seurat_obj, features = all.genes)

# Or scale only variable features (faster)
seurat_obj <- ScaleData(seurat_obj)
```

### Regress Out Confounders

```r
# Regress out unwanted variation during scaling
seurat_obj <- ScaleData(seurat_obj, vars.to.regress = c('percent.mt', 'nCount_RNA'))
```

### Complete Preprocessing Pipeline (Log Normalization)

**Goal:** Run end-to-end Seurat preprocessing with standard log normalization.

**Approach:** Load 10X data, compute QC metrics, filter, normalize with LogNormalize, select variable features, and scale.

```r
library(Seurat)

counts <- Read10X(data.dir = 'filtered_feature_bc_matrix/')
seurat_obj <- CreateSeuratObject(counts = counts, min.cells = 3, min.features = 200)

# QC
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')

# Filter
seurat_obj <- subset(seurat_obj,
    subset = nFeature_RNA > 200 & nFeature_RNA < 5000 & percent.mt < 20)

# Normalize
seurat_obj <- NormalizeData(seurat_obj)

# HVGs
seurat_obj <- FindVariableFeatures(seurat_obj, nfeatures = 2000)

# Scale
seurat_obj <- ScaleData(seurat_obj)
```

### Complete Preprocessing Pipeline (SCTransform)

**Goal:** Run end-to-end Seurat preprocessing with SCTransform for variance-stabilized normalization.

**Approach:** Load 10X data, compute QC metrics, filter, and apply SCTransform which jointly normalizes, selects HVGs, and scales.

```r
library(Seurat)

counts <- Read10X(data.dir = 'filtered_feature_bc_matrix/')
seurat_obj <- CreateSeuratObject(counts = counts, min.cells = 3, min.features = 200)

# QC
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')

# Filter
seurat_obj <- subset(seurat_obj,
    subset = nFeature_RNA > 200 & nFeature_RNA < 5000 & percent.mt < 20)

# SCTransform (does normalization, HVG, and scaling)
seurat_obj <- SCTransform(seurat_obj, vars.to.regress = 'percent.mt', verbose = FALSE)
```

---

## QC Thresholds Reference

| Metric | Typical Range | Notes |
|--------|---------------|-------|
| min_genes | 200-500 | Remove empty droplets |
| max_genes | 2500-5000 | Remove doublets |
| max_mt | 5-20% | Remove dying cells (tissue-dependent) |
| min_cells | 3-10 | Remove rarely detected genes |

## Method Comparison

| Step | Scanpy | Seurat (Standard) | Seurat (SCTransform) |
|------|--------|-------------------|---------------------|
| Normalize | `normalize_total` + `log1p` | `NormalizeData` | `SCTransform` |
| HVGs | `highly_variable_genes` | `FindVariableFeatures` | (included) |
| Scale | `scale` | `ScaleData` | (included) |
| Regress | `regress_out` | `ScaleData(vars.to.regress)` | `SCTransform(vars.to.regress)` |

## Related Skills

- data-io - Load data before preprocessing
- clustering - PCA and clustering after preprocessing
- markers-annotation - Find markers after clustering
