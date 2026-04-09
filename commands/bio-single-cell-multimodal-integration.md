# bio-single-cell-multimodal-integration

> Analyze multi-modal single-cell data (CITE-seq, Multiome, spatial). Use when working with data that measures multiple modalities per cell like RNA + protein or RNA + ATAC. Use when analyzing CITE-seq, Multiome, or other multi-modal single-cell data.

## Version Compatibility

Reference examples tested with: numpy 1.26+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Multimodal Integration

**"Integrate RNA and protein data from my CITE-seq experiment"** → Jointly analyze multiple modalities (RNA + protein, RNA + ATAC) measured in the same cells using weighted nearest neighbor or factor analysis.
- R: `Seurat::FindMultiModalNeighbors()` for WNN integration
- Python: `muon` for MuData handling, `scanpy` + `anndata` for multimodal objects

Analyze multi-modal single-cell data where multiple measurements are made per cell.

## Common Modalities

| Technology | Modalities | Package |
|------------|------------|---------|
| CITE-seq | RNA + surface proteins (ADT) | Seurat |
| 10X Multiome | RNA + ATAC | Seurat, Signac, ArchR |
| SHARE-seq | RNA + ATAC | Seurat, Signac |
| Spatial (Visium) | RNA + spatial coordinates | Seurat, Squidpy |

## CITE-seq Analysis (Seurat)

### Load Data

```r
library(Seurat)

# Read 10X data with antibody capture
data <- Read10X('filtered_feature_bc_matrix/')

# Separate RNA and ADT
rna_counts <- data$`Gene Expression`
adt_counts <- data$`Antibody Capture`

# Create Seurat object with both assays
obj <- CreateSeuratObject(counts = rna_counts, assay = 'RNA')
obj[['ADT']] <- CreateAssayObject(counts = adt_counts)
```

### QC and Normalization

```r
# RNA QC (standard)
obj <- PercentageFeatureSet(obj, pattern = '^MT-', col.name = 'percent.mt')
obj <- subset(obj, nFeature_RNA > 200 & percent.mt < 20)

# Normalize RNA
obj <- NormalizeData(obj, assay = 'RNA')
obj <- FindVariableFeatures(obj, assay = 'RNA')
obj <- ScaleData(obj, assay = 'RNA')

# Normalize ADT (CLR normalization)
obj <- NormalizeData(obj, assay = 'ADT', normalization.method = 'CLR', margin = 2)
obj <- ScaleData(obj, assay = 'ADT')
```

### Weighted Nearest Neighbor (WNN) Clustering

**Goal:** Jointly cluster cells using both RNA and protein (or ATAC) modalities, weighting each modality's contribution per cell.

**Approach:** Run PCA separately on each modality, build a weighted nearest neighbor graph that adaptively combines both reductions, then cluster and embed on the combined WNN graph.

```r
# Dimensionality reduction for each modality
obj <- RunPCA(obj, assay = 'RNA', reduction.name = 'pca')
obj <- RunPCA(obj, assay = 'ADT', reduction.name = 'apca',
              features = rownames(obj[['ADT']]))

# WNN graph combining both modalities
obj <- FindMultiModalNeighbors(obj,
    reduction.list = list('pca', 'apca'),
    dims.list = list(1:30, 1:18))

# Cluster on WNN graph
obj <- FindClusters(obj, graph.name = 'wsnn', resolution = 0.5)

# UMAP on WNN
obj <- RunUMAP(obj, nn.name = 'weighted.nn', reduction.name = 'wnn.umap')
```

### Visualize

```r
# UMAP colored by cluster
DimPlot(obj, reduction = 'wnn.umap', label = TRUE)

# ADT expression on UMAP
FeaturePlot(obj, features = c('adt_CD3', 'adt_CD19', 'adt_CD14'),
            reduction = 'wnn.umap')

# Compare modality weights
VlnPlot(obj, features = 'RNA.weight', group.by = 'seurat_clusters')
```

## 10X Multiome (RNA + ATAC)

### Load Data

```r
library(Seurat)
library(Signac)

# Read RNA counts
rna_counts <- Read10X_h5('filtered_feature_bc_matrix.h5')$`Gene Expression`

# Read ATAC fragments
atac_counts <- Read10X_h5('filtered_feature_bc_matrix.h5')$Peaks
fragments <- CreateFragmentObject('atac_fragments.tsv.gz')

# Create multiome object
obj <- CreateSeuratObject(counts = rna_counts, assay = 'RNA')
obj[['ATAC']] <- CreateChromatinAssay(counts = atac_counts, fragments = fragments,
                                       genome = 'hg38', min.cells = 5)
```

### Process ATAC

```r
# ATAC QC
obj <- NucleosomeSignal(obj)
obj <- TSSEnrichment(obj)

# ATAC normalization
obj <- RunTFIDF(obj, assay = 'ATAC')
obj <- FindTopFeatures(obj, assay = 'ATAC', min.cutoff = 'q0')
obj <- RunSVD(obj, assay = 'ATAC')
```

### Joint Analysis

```r
# RNA processing
DefaultAssay(obj) <- 'RNA'
obj <- NormalizeData(obj) %>% FindVariableFeatures() %>% ScaleData() %>% RunPCA()

# WNN integration
obj <- FindMultiModalNeighbors(obj, reduction.list = list('pca', 'lsi'),
                                dims.list = list(1:30, 2:30))
obj <- RunUMAP(obj, nn.name = 'weighted.nn', reduction.name = 'wnn.umap')
obj <- FindClusters(obj, graph.name = 'wsnn')
```

## Scanpy/MuData (Python)

### CITE-seq with MuData

```python
import scanpy as sc
import muon as mu
from muon import prot as pt

# Load multimodal data
mdata = mu.read_10x_h5('filtered_feature_bc_matrix.h5')

# Access modalities
rna = mdata.mod['rna']
prot = mdata.mod['prot']

# Process RNA
sc.pp.filter_cells(rna, min_genes=200)
sc.pp.normalize_total(rna, target_sum=1e4)
sc.pp.log1p(rna)
sc.pp.highly_variable_genes(rna)
sc.tl.pca(rna)

# Process protein (CLR normalization)
pt.pp.clr(prot)

# Multi-omics factor analysis
mu.tl.mofa(mdata, n_factors=20)

# Joint UMAP
mu.tl.umap(mdata)
mu.pl.umap(mdata, color=['rna:leiden', 'prot:CD3'])
```

## Integration Metrics

### Modality Weights

```r
# Check how much each modality contributes per cell
weights <- obj@reductions$wnn@misc$weights

# Average weight by cluster
aggregate(weights, by = list(obj$seurat_clusters), mean)
```

### Correlation Between Modalities

```python
import numpy as np

# Correlate RNA and protein for same genes/proteins
common = set(rna.var_names) & set(prot.var_names)
for gene in common:
    rna_expr = rna[:, gene].X.toarray().flatten()
    prot_expr = prot[:, gene].X.toarray().flatten()
    corr = np.corrcoef(rna_expr, prot_expr)[0, 1]
    print(f'{gene}: r={corr:.3f}')
```

## Marker Discovery

### Multi-Modal Markers

```r
# Find markers using both modalities
DefaultAssay(obj) <- 'RNA'
rna_markers <- FindAllMarkers(obj, only.pos = TRUE)

DefaultAssay(obj) <- 'ADT'
adt_markers <- FindAllMarkers(obj, only.pos = TRUE)

# Combine
all_markers <- rbind(
    transform(rna_markers, modality = 'RNA'),
    transform(adt_markers, modality = 'ADT')
)
```

## Related Skills

- single-cell/data-io - Loading single-cell data
- single-cell/clustering - Clustering methods
- single-cell/markers-annotation - Cell type annotation
- chip-seq/peak-calling - For ATAC peak calling
