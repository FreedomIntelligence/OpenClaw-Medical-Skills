# bio-single-cell-scatac-analysis

> Single-cell ATAC-seq analysis with Signac (R/Seurat) and ArchR. Process 10X Genomics scATAC data, perform QC, dimensionality reduction, clustering, peak calling, and motif activity scoring with chromVAR. Use when analyzing single-cell ATAC-seq data.

## Version Compatibility

Reference examples tested with: MACS2 2.2+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# scATAC-seq Analysis

**"Analyze my single-cell ATAC-seq data"** → Process peak-barcode matrices, perform QC/filtering, reduce dimensions with LSI, cluster cells, call peaks per cluster, and score motif activity.
- R: `Signac::CreateChromatinAssay()` → `RunTFIDF()` → `FindTopFeatures()` → `RunSVD()`
- R: `ArchR::createArrowFiles()` for large datasets

Analyze single-cell chromatin accessibility data to identify cell types and regulatory elements.

## Tool Comparison

| Tool | Ecosystem | Strengths |
|------|-----------|-----------|
| Signac | Seurat | Integration with scRNA-seq, familiar API |
| ArchR | Standalone | Memory efficient, comprehensive |
| chromVAR | Bioconductor | TF motif deviation scoring |
| SnapATAC2 | Python | Fast, scalable |

## Signac (R/Seurat)

**Goal:** Process scATAC-seq data through QC, normalization, dimensionality reduction, and clustering to identify cell types by chromatin accessibility.

**Approach:** Create a ChromatinAssay from a peak-barcode matrix with fragment files, compute QC metrics (TSS enrichment, nucleosome signal), normalize with TF-IDF, reduce dimensions with LSI (SVD), then cluster and annotate using gene activity scores.

### Installation

```r
install.packages('Signac')
BiocManager::install(c('EnsDb.Hsapiens.v86', 'biovizBase', 'motifmatchr', 'chromVAR', 'JASPAR2020', 'TFBSTools'))
```

### Load 10X Data

```r
library(Signac)
library(Seurat)
library(EnsDb.Hsapiens.v86)

counts <- Read10X_h5('filtered_peak_bc_matrix.h5')
metadata <- read.csv('singlecell.csv', header = TRUE, row.names = 1)

chrom_assay <- CreateChromatinAssay(
    counts = counts,
    sep = c(':', '-'),
    genome = 'hg38',
    fragments = 'fragments.tsv.gz',
    min.cells = 10,
    min.features = 200
)

obj <- CreateSeuratObject(counts = chrom_assay, assay = 'peaks', meta.data = metadata)
```

### Add Gene Annotations

```r
annotations <- GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v86)
seqlevelsStyle(annotations) <- 'UCSC'
Annotation(obj) <- annotations
```

### QC Metrics

```r
obj <- NucleosomeSignal(obj)
obj <- TSSEnrichment(obj, fast = FALSE)

obj$pct_reads_in_peaks <- obj$peak_region_fragments / obj$passed_filters * 100
obj$blacklist_ratio <- obj$blacklist_region_fragments / obj$peak_region_fragments

VlnPlot(obj, features = c('pct_reads_in_peaks', 'peak_region_fragments', 'TSS.enrichment', 'blacklist_ratio', 'nucleosome_signal'), pt.size = 0.1, ncol = 5)
```

### QC Filtering

```r
obj <- subset(obj,
    peak_region_fragments > 3000 &
    peak_region_fragments < 20000 &
    pct_reads_in_peaks > 15 &
    blacklist_ratio < 0.05 &
    nucleosome_signal < 4 &
    TSS.enrichment > 2
)
```

### Normalization and Dimensionality Reduction

```r
obj <- RunTFIDF(obj)
obj <- FindTopFeatures(obj, min.cutoff = 'q0')
obj <- RunSVD(obj)

DepthCor(obj)  # Check correlation with sequencing depth
```

### Clustering

```r
obj <- RunUMAP(obj, reduction = 'lsi', dims = 2:30)
obj <- FindNeighbors(obj, reduction = 'lsi', dims = 2:30)
obj <- FindClusters(obj, algorithm = 3, resolution = 0.5)

DimPlot(obj, label = TRUE) + NoLegend()
```

### Gene Activity Scores

```r
gene_activities <- GeneActivity(obj)

obj[['RNA']] <- CreateAssayObject(counts = gene_activities)
obj <- NormalizeData(obj, assay = 'RNA', normalization.method = 'LogNormalize', scale.factor = median(obj$nCount_RNA))

DefaultAssay(obj) <- 'RNA'
FeaturePlot(obj, features = c('CD34', 'MS4A1', 'CD3D', 'CD14'), pt.size = 0.1, max.cutoff = 'q95')
```

### Peak Calling per Cluster

```r
peaks <- CallPeaks(obj, group.by = 'seurat_clusters', macs2.path = '/path/to/macs2')

# Quantify peaks
peak_counts <- FeatureMatrix(fragments = Fragments(obj), features = peaks, cells = colnames(obj))

obj[['peaks_called']] <- CreateChromatinAssay(counts = peak_counts, fragments = Fragments(obj), annotation = Annotation(obj))
```

### Differential Accessibility

```r
DefaultAssay(obj) <- 'peaks'
da_peaks <- FindMarkers(obj, ident.1 = 'cluster1', ident.2 = 'cluster2', test.use = 'LR', latent.vars = 'peak_region_fragments')

# Top differentially accessible peaks
head(da_peaks[order(da_peaks$avg_log2FC, decreasing = TRUE), ], 10)
```

### Motif Analysis with chromVAR

```r
library(JASPAR2020)
library(TFBSTools)
library(motifmatchr)

pfm <- getMatrixSet(JASPAR2020, opts = list(collection = 'CORE', tax_group = 'vertebrates', all_versions = FALSE))
obj <- AddMotifs(obj, genome = BSgenome.Hsapiens.UCSC.hg38, pfm = pfm)

obj <- RunChromVAR(obj, genome = BSgenome.Hsapiens.UCSC.hg38)

DefaultAssay(obj) <- 'chromvar'
FeaturePlot(obj, features = 'MA0139.1', min.cutoff = 'q10', max.cutoff = 'q90')  # CTCF

# Differential motif activity
differential_activity <- FindMarkers(obj, ident.1 = 'cluster1', ident.2 = 'cluster2', only.pos = TRUE, mean.fxn = rowMeans, fc.name = 'avg_diff')
```

### Coverage Plots

```r
CoveragePlot(obj, region = 'chr1-1000000-1050000', group.by = 'seurat_clusters', annotation = TRUE)

# Gene track
CoveragePlot(obj, region = 'MS4A1', group.by = 'seurat_clusters', extend.upstream = 10000, extend.downstream = 5000)
```

### Integration with scRNA-seq

```r
transfer_anchors <- FindTransferAnchors(reference = rna_obj, query = obj, features = VariableFeatures(rna_obj), reference.assay = 'RNA', query.assay = 'RNA', reduction = 'cca')

predicted_labels <- TransferData(anchorset = transfer_anchors, refdata = rna_obj$celltype, weight.reduction = obj[['lsi']], dims = 2:30)

obj <- AddMetaData(obj, metadata = predicted_labels)
```

## ArchR

### Installation

```r
devtools::install_github('GreenleafLab/ArchR', ref = 'master', repos = BiocManager::repositories())
library(ArchR)
addArchRGenome('hg38')
```

### Create Arrow Files

```r
inputFiles <- c('sample1_fragments.tsv.gz', 'sample2_fragments.tsv.gz')
names(inputFiles) <- c('sample1', 'sample2')

ArrowFiles <- createArrowFiles(inputFiles = inputFiles, sampleNames = names(inputFiles), filterTSS = 4, filterFrags = 1000, addTileMat = TRUE, addGeneScoreMat = TRUE)
```

### Create ArchRProject

```r
proj <- ArchRProject(ArrowFiles = ArrowFiles, outputDirectory = 'ArchR_output', copyArrows = TRUE)
```

### QC and Filtering

```r
df <- getCellColData(proj, select = c('log10(nFrags)', 'TSSEnrichment'))
p <- ggPoint(x = df[,1], y = df[,2], colorDensity = TRUE, continuousSet = 'sambaNight', xlabel = 'Log10 Unique Fragments', ylabel = 'TSS Enrichment', xlim = c(log10(500), quantile(df[,1], probs = 0.99)), ylim = c(0, quantile(df[,2], probs = 0.99)))

proj <- filterDoublets(proj)
```

### Dimensionality Reduction and Clustering

```r
proj <- addIterativeLSI(proj, useMatrix = 'TileMatrix', name = 'IterativeLSI', iterations = 2, clusterParams = list(resolution = c(0.2), sampleCells = 10000, n.start = 10), varFeatures = 25000, dimsToUse = 1:30)

proj <- addClusters(proj, reducedDims = 'IterativeLSI', method = 'Seurat', name = 'Clusters', resolution = 0.8)

proj <- addUMAP(proj, reducedDims = 'IterativeLSI', name = 'UMAP', nNeighbors = 30, minDist = 0.5, metric = 'cosine')

plotEmbedding(proj, colorBy = 'cellColData', name = 'Clusters', embedding = 'UMAP')
```

### Gene Scores

```r
markersGS <- getMarkerFeatures(proj, useMatrix = 'GeneScoreMatrix', groupBy = 'Clusters', bias = c('TSSEnrichment', 'log10(nFrags)'), testMethod = 'wilcoxon')

markerList <- getMarkers(markersGS, cutOff = 'FDR <= 0.01 & Log2FC >= 1.25')

heatmapGS <- plotMarkerHeatmap(seMarker = markersGS, cutOff = 'FDR <= 0.01 & Log2FC >= 1.25', labelMarkers = c('CD34', 'MS4A1', 'CD3D', 'CD14'))
```

### Peak Calling

```r
proj <- addGroupCoverages(proj, groupBy = 'Clusters')
proj <- addReproduciblePeakSet(proj, groupBy = 'Clusters', pathToMacs2 = '/path/to/macs2')
proj <- addPeakMatrix(proj)
```

### Motif Enrichment

```r
proj <- addMotifAnnotations(proj, motifSet = 'cisbp', name = 'Motif')

enrichMotifs <- peakAnnoEnrichment(seMarker = markersPeaks, ArchRProj = proj, peakAnnotation = 'Motif', cutOff = 'FDR <= 0.1 & Log2FC >= 0.5')

heatmapEM <- plotEnrichHeatmap(enrichMotifs, n = 7, transpose = TRUE)
```

### chromVAR Deviations

```r
proj <- addBgdPeaks(proj)
proj <- addDeviationsMatrix(proj, peakAnnotation = 'Motif', force = TRUE)

plotVarDev <- getVarDeviations(proj, name = 'MotifMatrix', plot = TRUE)

motifs <- c('GATA1', 'CEBPA', 'EBF1', 'IRF8', 'PAX5')
markerMotifs <- getFeatures(proj, select = paste(motifs, collapse = '|'), useMatrix = 'MotifMatrix')

p <- plotEmbedding(proj, colorBy = 'MotifMatrix', name = sort(markerMotifs), embedding = 'UMAP', imputeWeights = getImputeWeights(proj))
```

## chromVAR Standalone

### Installation

```r
BiocManager::install('chromVAR')
```

### Basic Workflow

```r
library(chromVAR)
library(motifmatchr)
library(BSgenome.Hsapiens.UCSC.hg38)

counts <- readRDS('peak_counts.rds')  # SummarizedExperiment
counts <- addGCBias(counts, genome = BSgenome.Hsapiens.UCSC.hg38)

motifs <- getJasparMotifs()
motif_ix <- matchMotifs(motifs, counts, genome = BSgenome.Hsapiens.UCSC.hg38)

bg <- getBackgroundPeaks(counts)
dev <- computeDeviations(counts, motif_ix, background_peaks = bg)

variability <- computeVariability(dev)
plotVariability(variability, use_plotly = FALSE)
```

## QC Thresholds

| Metric | Typical Range | Filter |
|--------|---------------|--------|
| Unique fragments | 1,000-100,000 | > 1,000-3,000 |
| TSS enrichment | 2-30 | > 2-4 |
| Fraction in peaks | 20-70% | > 15-20% |
| Nucleosome signal | 0.5-2 | < 4 |
| Blacklist ratio | 0-0.05 | < 0.05 |

## Related Skills

- preprocessing - scRNA-seq QC (similar concepts)
- clustering - Clustering approaches (shared with scRNA-seq)
- multimodal-integration - Joint scRNA+scATAC analysis
- atac-seq - Bulk ATAC-seq methods
- chip-seq/motif-analysis - Motif databases and analysis
