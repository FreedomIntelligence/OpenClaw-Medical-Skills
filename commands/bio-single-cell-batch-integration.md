# bio-single-cell-batch-integration

> Integrate multiple scRNA-seq samples/batches using Harmony, scVI, Seurat anchors, and fastMNN. Remove technical variation while preserving biological differences. Use when integrating multiple scRNA-seq batches or datasets.

## Version Compatibility

Reference examples tested with: anndata 0.10+, scanpy 1.10+, scikit-learn 1.4+, scvi-tools 1.1+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Batch Integration

Integrate multiple scRNA-seq datasets to remove batch effects while preserving biological variation.

## Tool Comparison

| Tool | Speed | Scalability | Best For |
|------|-------|-------------|----------|
| Harmony | Fast | Good | Quick integration, most use cases |
| scVI | Moderate | Excellent | Large datasets, deep learning |
| Seurat CCA/RPCA | Moderate | Good | Conserved biology across batches |
| fastMNN | Fast | Good | MNN-based correction |

## Harmony (R/Python)

**Goal:** Remove batch effects from merged scRNA-seq datasets using Harmony's iterative correction of PCA embeddings.

**Approach:** Run PCA on merged data, iteratively adjust embeddings to mix batches while preserving biological variation, and use corrected embeddings for downstream analysis.

**"Integrate my batches"** → Merge samples, preprocess jointly, correct technical variation in the embedding space, and cluster on corrected coordinates.

### R with Seurat

```r
library(Seurat)
library(harmony)

# Merge datasets first
merged <- merge(sample1, y = list(sample2, sample3), add.cell.ids = c('S1', 'S2', 'S3'))

# Standard preprocessing
merged <- NormalizeData(merged)
merged <- FindVariableFeatures(merged)
merged <- ScaleData(merged)
merged <- RunPCA(merged)

# Run Harmony on PCA embeddings
merged <- RunHarmony(merged, group.by.vars = 'orig.ident', dims.use = 1:30)

# Use harmony embeddings for downstream
merged <- RunUMAP(merged, reduction = 'harmony', dims = 1:30)
merged <- FindNeighbors(merged, reduction = 'harmony', dims = 1:30)
merged <- FindClusters(merged, resolution = 0.5)
```

### Multiple Batch Variables

```r
# Correct for both sample and technology
merged <- RunHarmony(merged, group.by.vars = c('sample', 'technology'),
                     dims.use = 1:30, max.iter.harmony = 20)
```

### Python with Scanpy

```python
import scanpy as sc
import scanpy.external as sce

adata = sc.read_h5ad('merged.h5ad')

# Standard preprocessing
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, batch_key='batch')
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata)
sc.tl.pca(adata)

# Run Harmony
sce.pp.harmony_integrate(adata, key='batch')

# Use corrected embedding
sc.pp.neighbors(adata, use_rep='X_pca_harmony')
sc.tl.umap(adata)
sc.tl.leiden(adata)
```

## scVI (Python)

**Goal:** Integrate batches using a deep generative model that learns a shared latent space.

**Approach:** Train a variational autoencoder (scVI) conditioned on batch to learn batch-invariant latent representations, then use the latent space for clustering and visualization.

```python
import scvi
import scanpy as sc

adata = sc.read_h5ad('merged.h5ad')

# Setup for scVI
scvi.model.SCVI.setup_anndata(adata, batch_key='batch')

# Train model
model = scvi.model.SCVI(adata, n_latent=30, n_layers=2)
model.train(max_epochs=100, early_stopping=True)

# Get latent representation
adata.obsm['X_scVI'] = model.get_latent_representation()

# Use for downstream
sc.pp.neighbors(adata, use_rep='X_scVI')
sc.tl.umap(adata)
sc.tl.leiden(adata)
```

### scVI with Covariates

```python
# Include continuous covariates
scvi.model.SCVI.setup_anndata(adata, batch_key='batch',
                               continuous_covariate_keys=['percent_mito'])

model = scvi.model.SCVI(adata, n_latent=30)
model.train()
```

### scANVI (with cell type labels)

```python
# If you have reference labels for some cells
scvi.model.SCANVI.setup_anndata(adata, batch_key='batch', labels_key='cell_type',
                                 unlabeled_category='Unknown')

model = scvi.model.SCANVI(adata, n_latent=30)
model.train(max_epochs=100)

# Predict labels for unlabeled cells
adata.obs['predicted_type'] = model.predict()
```

## Seurat Integration (R)

**Goal:** Integrate batches using Seurat's anchor-based framework (CCA or RPCA).

**Approach:** Find shared biological anchors between datasets via canonical correlation analysis, then use anchors to correct expression values into a unified space.

### CCA-based Integration

```r
library(Seurat)

# Split by batch
obj_list <- SplitObject(merged, split.by = 'batch')

# Normalize each
obj_list <- lapply(obj_list, function(x) {
    x <- NormalizeData(x)
    x <- FindVariableFeatures(x, selection.method = 'vst', nfeatures = 2000)
    return(x)
})

# Find integration anchors
anchors <- FindIntegrationAnchors(object.list = obj_list, dims = 1:30)

# Integrate
integrated <- IntegrateData(anchorset = anchors, dims = 1:30)

# Switch to integrated assay for downstream
DefaultAssay(integrated) <- 'integrated'
integrated <- ScaleData(integrated)
integrated <- RunPCA(integrated)
integrated <- RunUMAP(integrated, dims = 1:30)
```

### RPCA (Faster for Large Datasets)

```r
# Use reciprocal PCA for faster integration
anchors <- FindIntegrationAnchors(object.list = obj_list, dims = 1:30,
                                   reduction = 'rpca')
integrated <- IntegrateData(anchorset = anchors, dims = 1:30)
```

### Seurat v5 Integration

```r
# Seurat v5 uses layers
merged[['RNA']] <- split(merged[['RNA']], f = merged$batch)
merged <- IntegrateLayers(merged, method = CCAIntegration, orig.reduction = 'pca',
                          new.reduction = 'integrated.cca')
merged <- JoinLayers(merged)
```

## fastMNN (R)

```r
library(batchelor)
library(SingleCellExperiment)

# Convert Seurat to SCE
sce <- as.SingleCellExperiment(merged)

# Run fastMNN
corrected <- fastMNN(sce, batch = sce$batch, d = 30, k = 20)

# Extract corrected values
reducedDim(sce, 'MNN') <- reducedDim(corrected, 'corrected')
```

## Evaluate Integration

**Goal:** Assess whether integration successfully removed batch effects while preserving biological variation.

**Approach:** Compute mixing metrics (LISI, silhouette scores) and visualize batch versus cell-type separation before and after integration.

### Mixing Metrics (R)

```r
# LISI score (lower = more mixed)
library(lisi)
lisi_scores <- compute_lisi(Embeddings(merged, 'harmony'),
                            merged@meta.data, c('batch', 'cell_type'))

# Batch mixing should be high, cell type separation preserved
mean(lisi_scores$batch)      # Want high
mean(lisi_scores$cell_type)  # Want low (preserved)
```

### Visual Assessment

```r
# Before integration
DimPlot(merged, reduction = 'pca', group.by = 'batch')
DimPlot(merged, reduction = 'pca', group.by = 'cell_type')

# After integration
DimPlot(merged, reduction = 'harmony', group.by = 'batch')
DimPlot(merged, reduction = 'harmony', group.by = 'cell_type')
```

### Silhouette Score (Python)

```python
from sklearn.metrics import silhouette_score

# Batch silhouette (want low - batches mixed)
batch_sil = silhouette_score(adata.obsm['X_scVI'], adata.obs['batch'])

# Cell type silhouette (want high - types separated)
celltype_sil = silhouette_score(adata.obsm['X_scVI'], adata.obs['cell_type'])
```

## Complete Workflow

**Goal:** Run end-to-end multi-sample integration from raw 10X files to clustered, integrated UMAP.

**Approach:** Load and merge samples, preprocess jointly, integrate with Harmony, and perform downstream clustering on corrected embeddings.

```r
library(Seurat)
library(harmony)

# Load and merge samples
samples <- list.files('data/', pattern = '*.h5', full.names = TRUE)
obj_list <- lapply(samples, Read10X_h5)
names(obj_list) <- gsub('.h5', '', basename(samples))

merged <- merge(CreateSeuratObject(obj_list[[1]], project = names(obj_list)[1]),
                y = lapply(2:length(obj_list), function(i)
                    CreateSeuratObject(obj_list[[i]], project = names(obj_list)[i])))

# QC
merged[['percent.mt']] <- PercentageFeatureSet(merged, pattern = '^MT-')
merged <- subset(merged, nFeature_RNA > 200 & nFeature_RNA < 5000 & percent.mt < 20)

# Preprocess
merged <- NormalizeData(merged)
merged <- FindVariableFeatures(merged, nfeatures = 2000)
merged <- ScaleData(merged, vars.to.regress = 'percent.mt')
merged <- RunPCA(merged, npcs = 50)

# Integrate with Harmony
merged <- RunHarmony(merged, group.by.vars = 'orig.ident')

# Downstream analysis on integrated data
merged <- RunUMAP(merged, reduction = 'harmony', dims = 1:30)
merged <- FindNeighbors(merged, reduction = 'harmony', dims = 1:30)
merged <- FindClusters(merged, resolution = 0.5)

DimPlot(merged, group.by = c('orig.ident', 'seurat_clusters'), ncol = 2)
```

## When to Use Each Method

| Scenario | Recommended |
|----------|-------------|
| Quick integration, most cases | Harmony |
| Large datasets (>500k cells) | scVI or Harmony |
| Strong batch effects | scVI |
| Reference mapping | Seurat anchors or scANVI |
| Preserving rare populations | fastMNN |

## Related Skills

- single-cell/preprocessing - QC before integration
- single-cell/clustering - Clustering after integration
- single-cell/cell-annotation - Annotation after integration
- single-cell/multimodal-integration - Multi-omic integration (different from batch)
