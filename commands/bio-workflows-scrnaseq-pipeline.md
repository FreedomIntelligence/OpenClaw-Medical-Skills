# bio-workflows-scrnaseq-pipeline

> End-to-end single-cell RNA-seq workflow from 10X Genomics data to annotated cell types. Covers QC, normalization, clustering, marker detection, and cell type annotation. Use when analyzing single-cell RNA-seq data.

**Available tools:** Read, Bash

# Single-Cell RNA-seq Pipeline

Complete workflow from 10X Genomics Cell Ranger output to annotated cell types.

## Workflow Overview

```
10X data (filtered_feature_bc_matrix)
    |
    v
[1. Load Data] ---------> Read10X / read_10x_h5
    |
    v
[2. QC Filtering] ------> nFeature, percent.mt, doublets
    |
    v
[3. Normalization] -----> SCTransform or LogNormalize
    |
    v
[4. HVG Selection] -----> FindVariableFeatures
    |
    v
[5. Dim Reduction] -----> PCA → UMAP
    |
    v
[6. Clustering] --------> FindNeighbors → FindClusters
    |
    v
[7. Markers] -----------> FindAllMarkers
    |
    v
[8. Annotation] --------> Manual or automated
    |
    v
Annotated Seurat/AnnData object
```

## Primary Path: Seurat (R)

### Step 1: Load 10X Data

```r
library(Seurat)
library(ggplot2)
library(dplyr)

# Load from Cell Ranger output
data_dir <- 'cellranger_output/filtered_feature_bc_matrix'
counts <- Read10X(data.dir = data_dir)

# Create Seurat object
seurat_obj <- CreateSeuratObject(counts = counts, project = 'my_project',
                                  min.cells = 3, min.features = 200)
```

### Step 2: Quality Control

```r
# Calculate QC metrics
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
seurat_obj[['percent.ribo']] <- PercentageFeatureSet(seurat_obj, pattern = '^RP[SL]')

# Visualize QC metrics
VlnPlot(seurat_obj, features = c('nFeature_RNA', 'nCount_RNA', 'percent.mt'), ncol = 3)

# Filter cells
seurat_obj <- subset(seurat_obj,
                     nFeature_RNA > 200 &
                     nFeature_RNA < 5000 &
                     percent.mt < 20 &
                     nCount_RNA > 500)

cat('Cells after QC:', ncol(seurat_obj), '\n')
```

**QC Checkpoint 1:** Review QC plots
- Remove cells with very low/high gene counts
- Remove cells with high mitochondrial content (dying cells)

### Step 3: Doublet Detection

```r
library(scDblFinder)

# Convert to SCE for scDblFinder
sce <- as.SingleCellExperiment(seurat_obj)
sce <- scDblFinder(sce)

# Add back to Seurat
seurat_obj$doublet_class <- sce$scDblFinder.class
seurat_obj$doublet_score <- sce$scDblFinder.score

# Remove doublets
seurat_obj <- subset(seurat_obj, doublet_class == 'singlet')
cat('Cells after doublet removal:', ncol(seurat_obj), '\n')
```

### Step 4: Normalization with SCTransform

```r
# SCTransform (recommended for most analyses)
seurat_obj <- SCTransform(seurat_obj, vars.to.regress = 'percent.mt', verbose = FALSE)
```

Alternative: Standard normalization
```r
seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = 'vst', nfeatures = 2000)
seurat_obj <- ScaleData(seurat_obj, vars.to.regress = 'percent.mt')
```

### Step 5: Dimensionality Reduction

```r
# PCA
seurat_obj <- RunPCA(seurat_obj, npcs = 50, verbose = FALSE)

# Determine optimal PCs
ElbowPlot(seurat_obj, ndims = 50)

# UMAP
n_pcs <- 30  # Choose based on elbow plot
seurat_obj <- RunUMAP(seurat_obj, dims = 1:n_pcs, verbose = FALSE)
```

### Step 6: Clustering

```r
# Find neighbors
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:n_pcs, verbose = FALSE)

# Find clusters (try multiple resolutions)
seurat_obj <- FindClusters(seurat_obj, resolution = c(0.2, 0.4, 0.6, 0.8, 1.0), verbose = FALSE)

# Visualize
DimPlot(seurat_obj, reduction = 'umap', group.by = 'SCT_snn_res.0.4', label = TRUE)
```

**QC Checkpoint 2:** Assess clustering
- Clusters should be visually separable on UMAP
- Resolution 0.4-0.8 is often appropriate

### Step 7: Find Marker Genes

```r
# Set identity to chosen resolution
Idents(seurat_obj) <- 'SCT_snn_res.0.4'

# Find markers for all clusters
markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)

# Top markers per cluster
top_markers <- markers %>%
    group_by(cluster) %>%
    slice_max(n = 10, order_by = avg_log2FC)

# Visualize top markers
DoHeatmap(seurat_obj, features = top_markers$gene) + NoLegend()
```

### Step 8: Cell Type Annotation

```r
# Manual annotation based on known markers
# Example for PBMC data:
cluster_annotations <- c(
    '0' = 'CD4 T cells',
    '1' = 'CD14 Monocytes',
    '2' = 'B cells',
    '3' = 'CD8 T cells',
    '4' = 'NK cells',
    '5' = 'CD16 Monocytes',
    '6' = 'Dendritic cells'
)

seurat_obj$cell_type <- cluster_annotations[as.character(Idents(seurat_obj))]

# Final UMAP
DimPlot(seurat_obj, reduction = 'umap', group.by = 'cell_type', label = TRUE)

# Save object
saveRDS(seurat_obj, 'seurat_annotated.rds')
```

## Alternative Path: Scanpy (Python)

```python
import scanpy as sc
import numpy as np

# Load 10X data
adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
adata.var_names_make_unique()

# QC metrics
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# Filter
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata = adata[adata.obs.n_genes_by_counts < 5000, :]
adata = adata[adata.obs.pct_counts_mt < 20, :]

# Doublet detection
sc.pp.scrublet(adata)
adata = adata[~adata.obs['predicted_doublet'], :]

# Normalize and HVGs
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# PCA, neighbors, UMAP
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)

# Clustering
sc.tl.leiden(adata, resolution=0.5)

# Markers
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=10, sharey=False)

# Save
adata.write('scanpy_annotated.h5ad')
```

## Parameter Recommendations

| Step | Parameter | Recommendation |
|------|-----------|----------------|
| QC | min.features | 200-500 |
| QC | max.features | 2500-5000 (depends on data) |
| QC | percent.mt | <10-20% |
| SCTransform | vars.to.regress | percent.mt |
| PCA | npcs | 30-50 |
| UMAP | dims | 15-30 (check elbow plot) |
| Clustering | resolution | 0.4-0.8 (start with 0.5) |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| All cells filtered | QC too strict | Relax thresholds |
| Poor UMAP separation | Too few HVGs or PCs | Increase nfeatures, check n_pcs |
| Too many/few clusters | Wrong resolution | Adjust resolution parameter |
| Unknown cell types | Missing markers | Check known marker genes manually |

## Complete R Workflow

```r
library(Seurat)
library(scDblFinder)
library(ggplot2)
library(dplyr)

# Configuration
data_dir <- 'filtered_feature_bc_matrix'
output_dir <- 'results'
dir.create(output_dir, showWarnings = FALSE)

# Load
counts <- Read10X(data.dir = data_dir)
seurat_obj <- CreateSeuratObject(counts = counts, min.cells = 3, min.features = 200)
cat('Initial cells:', ncol(seurat_obj), '\n')

# QC
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
seurat_obj <- subset(seurat_obj, nFeature_RNA > 200 & nFeature_RNA < 5000 & percent.mt < 20)
cat('After QC:', ncol(seurat_obj), '\n')

# Doublets
sce <- as.SingleCellExperiment(seurat_obj)
sce <- scDblFinder(sce)
seurat_obj$doublet <- sce$scDblFinder.class
seurat_obj <- subset(seurat_obj, doublet == 'singlet')
cat('After doublet removal:', ncol(seurat_obj), '\n')

# Normalize
seurat_obj <- SCTransform(seurat_obj, vars.to.regress = 'percent.mt', verbose = FALSE)

# Dimension reduction
seurat_obj <- RunPCA(seurat_obj, npcs = 50, verbose = FALSE)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30, verbose = FALSE)

# Cluster
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30, verbose = FALSE)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5, verbose = FALSE)

# Markers
markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)
write.csv(markers, file.path(output_dir, 'markers.csv'))

# Save
saveRDS(seurat_obj, file.path(output_dir, 'seurat_object.rds'))

# Plots
pdf(file.path(output_dir, 'umap.pdf'), width = 10, height = 8)
DimPlot(seurat_obj, reduction = 'umap', label = TRUE)
dev.off()

cat('Pipeline complete. Object saved to:', output_dir, '\n')
```

## Related Skills

- single-cell/data-io - Loading different formats
- single-cell/preprocessing - QC details
- single-cell/doublet-detection - Doublet methods comparison
- single-cell/clustering - Clustering parameters
- single-cell/markers-annotation - Annotation strategies
- single-cell/multimodal-integration - CITE-seq, multiome
