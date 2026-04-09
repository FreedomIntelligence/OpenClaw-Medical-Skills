# bio-workflows-multiome-pipeline

> End-to-end multiome workflow for joint scRNA-seq + scATAC-seq analysis. Covers data loading, separate modality processing, and WNN integration with Seurat/Signac. Use when analyzing joint scRNA+scATAC data.

**Available tools:** Read, Bash

# Multiome Pipeline

Complete workflow for 10X Multiome (joint scRNA + scATAC) analysis using Seurat and Signac.

## Workflow Overview

```
10X Multiome data
    |
    v
[1. Load Data] ---------> Read RNA + ATAC
    |
    v
[2. RNA Processing] ----> Standard scRNA workflow
    |
    v
[3. ATAC Processing] ---> Peak calling, LSI
    |
    v
[4. WNN Integration] ---> Weighted nearest neighbors
    |
    v
[5. Joint Analysis] ----> Clustering, markers
    |
    v
[6. Linked Features] ---> Gene-peak links
    |
    v
Integrated multiome object
```

## Step 1: Load Multiome Data

```r
library(Seurat)
library(Signac)
library(EnsDb.Hsapiens.v86)
library(ggplot2)

# Load RNA
rna_counts <- Read10X_h5('filtered_feature_bc_matrix.h5')
# For multiome, this returns a list with 'Gene Expression' and 'Peaks'

# Create Seurat object with RNA
seurat_obj <- CreateSeuratObject(
    counts = rna_counts$`Gene Expression`,
    assay = 'RNA'
)

# Load ATAC
atac_counts <- rna_counts$Peaks
# Or from fragments file
frags <- CreateFragmentObject('atac_fragments.tsv.gz', cells = colnames(seurat_obj))

# Create ChromatinAssay
atac_assay <- CreateChromatinAssay(
    counts = atac_counts,
    sep = c(':', '-'),
    fragments = frags,
    annotation = GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v86)
)

seurat_obj[['ATAC']] <- atac_assay
```

## Step 2: RNA Quality Control and Processing

```r
# QC metrics
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')

# Filter
seurat_obj <- subset(seurat_obj,
    nCount_RNA > 1000 &
    nCount_RNA < 25000 &
    percent.mt < 20
)

# Normalize RNA
seurat_obj <- SCTransform(seurat_obj, assay = 'RNA', verbose = FALSE)

# PCA
seurat_obj <- RunPCA(seurat_obj, assay = 'SCT', verbose = FALSE)
```

## Step 3: ATAC Quality Control and Processing

```r
# ATAC QC metrics
DefaultAssay(seurat_obj) <- 'ATAC'

seurat_obj <- NucleosomeSignal(seurat_obj)
seurat_obj <- TSSEnrichment(seurat_obj)

# Visualize
VlnPlot(seurat_obj, features = c('nCount_ATAC', 'TSS.enrichment', 'nucleosome_signal'),
        pt.size = 0, ncol = 3)

# Filter ATAC
seurat_obj <- subset(seurat_obj,
    nCount_ATAC > 1000 &
    nCount_ATAC < 100000 &
    TSS.enrichment > 2 &
    nucleosome_signal < 4
)

# Normalize ATAC (TF-IDF + SVD = LSI)
seurat_obj <- RunTFIDF(seurat_obj)
seurat_obj <- FindTopFeatures(seurat_obj, min.cutoff = 'q0')
seurat_obj <- RunSVD(seurat_obj)

# Check LSI components (first often correlates with depth)
DepthCor(seurat_obj)
```

## Step 4: Weighted Nearest Neighbors (WNN)

```r
# Build WNN graph using both modalities
seurat_obj <- FindMultiModalNeighbors(
    seurat_obj,
    reduction.list = list('pca', 'lsi'),
    dims.list = list(1:30, 2:30),  # Skip LSI component 1 if depth-correlated
    modality.weight.name = 'RNA.weight'
)

# UMAP on WNN graph
seurat_obj <- RunUMAP(seurat_obj, nn.name = 'weighted.nn',
                       reduction.name = 'wnn.umap', reduction.key = 'wnnUMAP_')

# Cluster on WNN
seurat_obj <- FindClusters(seurat_obj, graph.name = 'wsnn',
                            algorithm = 3, resolution = 0.5, verbose = FALSE)
```

## Step 5: Visualization and Markers

```r
# Compare modality-specific and joint embeddings
p1 <- DimPlot(seurat_obj, reduction = 'pca', label = TRUE) + ggtitle('RNA PCA')
p2 <- DimPlot(seurat_obj, reduction = 'lsi', label = TRUE) + ggtitle('ATAC LSI')
p3 <- DimPlot(seurat_obj, reduction = 'wnn.umap', label = TRUE) + ggtitle('WNN UMAP')
p1 + p2 + p3

# Modality weights per cell
VlnPlot(seurat_obj, features = 'RNA.weight', group.by = 'seurat_clusters', pt.size = 0)

# Find markers (RNA)
DefaultAssay(seurat_obj) <- 'SCT'
rna_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25)

# Find markers (ATAC - differentially accessible peaks)
DefaultAssay(seurat_obj) <- 'ATAC'
atac_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.05,
                                test.use = 'LR', latent.vars = 'nCount_ATAC')
```

## Step 6: Gene-Peak Linkage

```r
# Link peaks to genes
DefaultAssay(seurat_obj) <- 'ATAC'
seurat_obj <- RegionStats(seurat_obj, genome = BSgenome.Hsapiens.UCSC.hg38)

seurat_obj <- LinkPeaks(
    seurat_obj,
    peak.assay = 'ATAC',
    expression.assay = 'SCT',
    genes.use = c('CD8A', 'CD4', 'MS4A1', 'CD14')  # Example genes
)

# Visualize links
CoveragePlot(seurat_obj, region = 'CD8A', features = 'CD8A',
             expression.assay = 'SCT', extend.upstream = 10000, extend.downstream = 10000)
```

## Complete Workflow Script

```r
library(Seurat)
library(Signac)
library(EnsDb.Hsapiens.v86)
library(BSgenome.Hsapiens.UCSC.hg38)
library(ggplot2)

# Configuration
data_dir <- 'multiome_output'
output_dir <- 'multiome_results'
dir.create(output_dir, showWarnings = FALSE)

# === Load Data ===
cat('Loading data...\n')
counts <- Read10X_h5(file.path(data_dir, 'filtered_feature_bc_matrix.h5'))
frags <- file.path(data_dir, 'atac_fragments.tsv.gz')

seurat_obj <- CreateSeuratObject(counts = counts$`Gene Expression`, assay = 'RNA')
seurat_obj[['ATAC']] <- CreateChromatinAssay(
    counts = counts$Peaks,
    sep = c(':', '-'),
    fragments = frags,
    annotation = GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v86)
)
cat('Cells:', ncol(seurat_obj), '\n')

# === RNA QC ===
cat('RNA QC...\n')
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
seurat_obj <- subset(seurat_obj, nCount_RNA > 1000 & nCount_RNA < 25000 & percent.mt < 20)

# === ATAC QC ===
cat('ATAC QC...\n')
DefaultAssay(seurat_obj) <- 'ATAC'
seurat_obj <- NucleosomeSignal(seurat_obj)
seurat_obj <- TSSEnrichment(seurat_obj)
seurat_obj <- subset(seurat_obj, nCount_ATAC > 1000 & TSS.enrichment > 2 & nucleosome_signal < 4)
cat('After QC:', ncol(seurat_obj), 'cells\n')

# === Process RNA ===
cat('Processing RNA...\n')
DefaultAssay(seurat_obj) <- 'RNA'
seurat_obj <- SCTransform(seurat_obj, verbose = FALSE)
seurat_obj <- RunPCA(seurat_obj, verbose = FALSE)

# === Process ATAC ===
cat('Processing ATAC...\n')
DefaultAssay(seurat_obj) <- 'ATAC'
seurat_obj <- RunTFIDF(seurat_obj)
seurat_obj <- FindTopFeatures(seurat_obj, min.cutoff = 'q0')
seurat_obj <- RunSVD(seurat_obj)

# === WNN Integration ===
cat('WNN integration...\n')
seurat_obj <- FindMultiModalNeighbors(seurat_obj,
    reduction.list = list('pca', 'lsi'),
    dims.list = list(1:30, 2:30),
    modality.weight.name = 'RNA.weight'
)
seurat_obj <- RunUMAP(seurat_obj, nn.name = 'weighted.nn',
    reduction.name = 'wnn.umap', reduction.key = 'wnnUMAP_')
seurat_obj <- FindClusters(seurat_obj, graph.name = 'wsnn', resolution = 0.5, verbose = FALSE)

# === Save ===
saveRDS(seurat_obj, file.path(output_dir, 'multiome_analyzed.rds'))

# === Plots ===
pdf(file.path(output_dir, 'wnn_umap.pdf'), width = 10, height = 8)
DimPlot(seurat_obj, reduction = 'wnn.umap', label = TRUE)
dev.off()

cat('Results saved to:', output_dir, '\n')
cat('Clusters:', length(unique(seurat_obj$seurat_clusters)), '\n')
```

## Related Skills

- single-cell/data-io - Loading 10X data
- single-cell/preprocessing - QC and normalization
- single-cell/multimodal-integration - WNN details
- single-cell/scatac-analysis - ATAC-specific processing
