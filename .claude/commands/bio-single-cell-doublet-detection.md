# bio-single-cell-doublet-detection

> Detect and remove doublets (multiple cells captured in one droplet) from single-cell RNA-seq data. Uses Scrublet (Python), DoubletFinder (R), and scDblFinder (R). Essential QC step before clustering to avoid artificial cell populations. Use when identifying and removing doublets from scRNA-seq data.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Doublet Detection

Doublets are droplets containing two or more cells. They appear as artificial intermediate cell populations and must be removed before analysis.

## Scrublet (Python)

**Goal:** Detect and score doublets in scRNA-seq data using simulated doublet profiles.

**Approach:** Simulate artificial doublets by combining random cell pairs, embed real and simulated cells together, and score each cell's similarity to simulated doublets.

**"Remove doublets from my data"** → Identify droplets containing multiple cells by comparing each cell's profile to computationally simulated doublets, then filter flagged cells.

### Basic Usage

```python
import scrublet as scr
import scanpy as sc
import numpy as np

adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')

scrub = scr.Scrublet(adata.X, expected_doublet_rate=0.06)
doublet_scores, predicted_doublets = scrub.scrub_doublets()

adata.obs['doublet_score'] = doublet_scores
adata.obs['predicted_doublet'] = predicted_doublets

print(f'Detected {predicted_doublets.sum()} doublets ({100*predicted_doublets.mean():.1f}%)')
```

### Adjust Parameters

```python
scrub = scr.Scrublet(adata.X, expected_doublet_rate=0.06)
doublet_scores, predicted_doublets = scrub.scrub_doublets(
    min_counts=2,
    min_cells=3,
    min_gene_variability_pctl=85,
    n_prin_comps=30,
    synthetic_doublet_umi_subsampling=1.0
)
```

### Visualize Doublet Scores

```python
import matplotlib.pyplot as plt

scrub.plot_histogram()
plt.savefig('doublet_histogram.pdf')

# UMAP with doublet scores
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)

sc.pl.umap(adata, color=['doublet_score', 'predicted_doublet'], save='_doublets.pdf')
```

### Filter Doublets

```python
adata_filtered = adata[~adata.obs['predicted_doublet']].copy()
print(f'Kept {adata_filtered.n_obs} cells after doublet removal')
```

### Set Manual Threshold

```python
scrub = scr.Scrublet(adata.X)
doublet_scores, _ = scrub.scrub_doublets()

threshold = 0.25
predicted_doublets = doublet_scores > threshold
adata.obs['predicted_doublet'] = predicted_doublets
```

## DoubletFinder (R)

**Goal:** Detect doublets in Seurat objects using DoubletFinder's pANN-based classification.

**Approach:** Optimize the pK neighborhood parameter via parameter sweep, compute artificial nearest neighbor proportions, and classify cells as singlets or doublets.

### Basic Usage

```r
library(Seurat)
library(DoubletFinder)

seurat_obj <- Read10X(data.dir = 'filtered_feature_bc_matrix/')
seurat_obj <- CreateSeuratObject(counts = seurat_obj, min.cells = 3, min.features = 200)

seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj)
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:20)
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:20)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

sweep.res <- paramSweep(seurat_obj, PCs = 1:20, sct = FALSE)
sweep.stats <- summarizeSweep(sweep.res, GT = FALSE)
bcmvn <- find.pK(sweep.stats)

optimal_pk <- as.numeric(as.character(bcmvn$pK[which.max(bcmvn$BCmetric)]))

nExp_poi <- round(0.06 * nrow(seurat_obj@meta.data))
seurat_obj <- doubletFinder(seurat_obj, PCs = 1:20, pN = 0.25, pK = optimal_pk,
                             nExp = nExp_poi, reuse.pANN = FALSE, sct = FALSE)

colnames(seurat_obj@meta.data)
```

### With SCTransform

```r
seurat_obj <- SCTransform(seurat_obj)
seurat_obj <- RunPCA(seurat_obj)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

sweep.res <- paramSweep(seurat_obj, PCs = 1:30, sct = TRUE)
sweep.stats <- summarizeSweep(sweep.res, GT = FALSE)
bcmvn <- find.pK(sweep.stats)

optimal_pk <- as.numeric(as.character(bcmvn$pK[which.max(bcmvn$BCmetric)]))
nExp_poi <- round(0.06 * nrow(seurat_obj@meta.data))

seurat_obj <- doubletFinder(seurat_obj, PCs = 1:30, pN = 0.25, pK = optimal_pk,
                             nExp = nExp_poi, reuse.pANN = FALSE, sct = TRUE)
```

### Filter Doublets

```r
df_col <- grep('DF.classifications', colnames(seurat_obj@meta.data), value = TRUE)
seurat_obj$doublet <- seurat_obj@meta.data[[df_col]]

DimPlot(seurat_obj, group.by = 'doublet')

seurat_obj <- subset(seurat_obj, subset = doublet == 'Singlet')
```

### Adjust Expected Doublet Rate

```r
n_cells <- ncol(seurat_obj)
doublet_rate <- n_cells / 1000 * 0.008
nExp_poi <- round(doublet_rate * n_cells)
```

## scDblFinder (R/Bioconductor)

**Goal:** Detect doublets using scDblFinder's gradient-boosted classifier for fast, accurate identification.

**Approach:** Simulate doublets, train a gradient boosting classifier on real vs simulated profiles, and score each cell.

### Basic Usage

```r
library(scDblFinder)
library(SingleCellExperiment)

sce <- SingleCellExperiment(assays = list(counts = counts_matrix))
sce <- scDblFinder(sce)

table(sce$scDblFinder.class)
```

### From Seurat Object

```r
library(scDblFinder)
library(Seurat)

sce <- as.SingleCellExperiment(seurat_obj)

sce <- scDblFinder(sce)

seurat_obj$scDblFinder_class <- sce$scDblFinder.class
seurat_obj$scDblFinder_score <- sce$scDblFinder.score

DimPlot(seurat_obj, group.by = 'scDblFinder_class')

seurat_obj <- subset(seurat_obj, subset = scDblFinder_class == 'singlet')
```

### Multi-Sample Processing

```r
sce <- scDblFinder(sce, samples = 'sample_id')
```

### Adjust Parameters

```r
sce <- scDblFinder(sce,
    dbr = 0.06,
    dbr.sd = 0.015,
    nfeatures = 1500,
    dims = 20,
    k = 30
)
```

## Expected Doublet Rates

| Cells Loaded | Expected Rate |
|--------------|---------------|
| 1,000 | ~0.8% |
| 2,000 | ~1.6% |
| 5,000 | ~4.0% |
| 10,000 | ~8.0% |
| 15,000 | ~12% |

Formula: `rate ≈ cells_loaded / 1000 * 0.008`

## Compare Methods

```r
library(scDblFinder)

seurat_obj$scrublet <- scrublet_results
sce <- as.SingleCellExperiment(seurat_obj)
sce <- scDblFinder(sce)
seurat_obj$scDblFinder <- sce$scDblFinder.class

DimPlot(seurat_obj, group.by = c('doublet', 'scDblFinder', 'scrublet'), ncol = 3)

table(seurat_obj$doublet, seurat_obj$scDblFinder)
```

## Handling Heterotypic vs Homotypic Doublets

### Heterotypic Doublets
- Two different cell types
- Easier to detect (intermediate expression)
- All methods handle well

### Homotypic Doublets
- Same cell type
- Harder to detect (no intermediate signature)
- May have higher total counts

```python
adata.obs['log_counts'] = np.log1p(adata.obs['total_counts'])
sc.pl.violin(adata, 'log_counts', groupby='predicted_doublet')
```

## Scanpy Integration Pipeline

**Goal:** Run doublet detection as part of a complete Scanpy preprocessing workflow.

**Approach:** Detect and remove doublets with Scrublet before QC filtering, then proceed through normalization, HVG selection, and clustering.

```python
import scanpy as sc
import scrublet as scr

adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')

adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

scrub = scr.Scrublet(adata.X, expected_doublet_rate=0.06)
doublet_scores, predicted_doublets = scrub.scrub_doublets()
adata.obs['doublet_score'] = doublet_scores
adata.obs['is_doublet'] = predicted_doublets

print(f'Before filtering: {adata.n_obs} cells')
adata = adata[~adata.obs['is_doublet']].copy()
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()
print(f'After filtering: {adata.n_obs} cells')

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
sc.tl.leiden(adata)
```

## Seurat Integration Pipeline

**Goal:** Run DoubletFinder as part of a complete Seurat preprocessing workflow.

**Approach:** Preprocess and cluster, run DoubletFinder parameter sweep and classification, filter doublets, then re-preprocess clean singlets.

```r
library(Seurat)
library(DoubletFinder)

seurat_obj <- Read10X('filtered_feature_bc_matrix/')
seurat_obj <- CreateSeuratObject(counts = seurat_obj, min.cells = 3, min.features = 200)

seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')

seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj)
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:20)
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:20)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

sweep.res <- paramSweep(seurat_obj, PCs = 1:20)
sweep.stats <- summarizeSweep(sweep.res)
bcmvn <- find.pK(sweep.stats)
pk <- as.numeric(as.character(bcmvn$pK[which.max(bcmvn$BCmetric)]))
nExp <- round(0.06 * ncol(seurat_obj))

seurat_obj <- doubletFinder(seurat_obj, PCs = 1:20, pN = 0.25, pK = pk, nExp = nExp)

df_col <- grep('DF.classifications', colnames(seurat_obj@meta.data), value = TRUE)
seurat_obj <- subset(seurat_obj, cells = colnames(seurat_obj)[seurat_obj@meta.data[[df_col]] == 'Singlet'])
seurat_obj <- subset(seurat_obj, subset = percent.mt < 20)

seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj)
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:20)
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:20)
seurat_obj <- FindClusters(seurat_obj)
```

## Method Comparison

| Method | Speed | Accuracy | Language |
|--------|-------|----------|----------|
| Scrublet | Fast | Good | Python |
| DoubletFinder | Slow | Good | R |
| scDblFinder | Fast | Excellent | R |

## Related Skills

- preprocessing - QC before doublet detection
- clustering - Run after filtering doublets
- data-io - Load data before processing
