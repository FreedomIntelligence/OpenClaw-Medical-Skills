# bio-atac-seq-motif-deviation

> Analyze transcription factor motif accessibility variability using chromVAR. Use when identifying which TF motifs show variable accessibility across samples or conditions in ATAC-seq data.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+, limma 3.58+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Motif Deviation Analysis

**"Which TF motifs show variable accessibility across my samples?"** → Compute per-sample deviation scores for TF motif accessibility to identify regulators driving chromatin state differences.
- R: `chromVAR::computeDeviations(counts, motifs)`

Measure per-sample variability in transcription factor motif accessibility using chromVAR. This identifies TFs whose binding sites show differential accessibility across conditions.

## Required Packages

```r
library(chromVAR)
library(motifmatchr)
library(BSgenome.Hsapiens.UCSC.hg38)  # or appropriate genome
library(JASPAR2020)
library(TFBSTools)
library(SummarizedExperiment)
```

## Basic Workflow

**Goal:** Run chromVAR to compute per-sample TF motif deviation scores from ATAC-seq peak counts.

**Approach:** Load peak counts into a SummarizedExperiment, correct for GC bias, filter low-quality peaks, match JASPAR motifs, and compute deviation z-scores.

### 1. Load Peak Counts

```r
library(chromVAR)
library(SummarizedExperiment)

# From count matrix and peak ranges
peaks <- read.table('peaks.bed', col.names = c('chr', 'start', 'end'))
peak_ranges <- GRanges(seqnames = peaks$chr, ranges = IRanges(peaks$start, peaks$end))

counts <- read.table('counts.txt', header = TRUE, row.names = 1)
counts_matrix <- as.matrix(counts)

fragment_counts <- SummarizedExperiment(
    assays = list(counts = counts_matrix),
    rowRanges = peak_ranges
)
```

### 2. Add GC Bias Correction

```r
library(BSgenome.Hsapiens.UCSC.hg38)

fragment_counts <- addGCBias(fragment_counts, genome = BSgenome.Hsapiens.UCSC.hg38)
```

### 3. Filter Low-Quality Peaks

```r
# min_depth=1500: Minimum total reads per sample. Adjust based on library size.
# min_in_peaks=0.15: Minimum fraction of reads in peaks (FRiP). 0.15 = 15%.
fragment_counts <- filterSamples(fragment_counts, min_depth = 1500, min_in_peaks = 0.15)

# min_count=10: Require peaks with >=10 reads across samples.
# n_samples_frac=0.1: Peak must be detected in >=10% of samples.
fragment_counts <- filterPeaks(fragment_counts, non_overlapping = TRUE,
                                min_count = 10, n_samples_frac = 0.1)
```

## Get Motif Annotations

### From JASPAR

```r
library(JASPAR2020)
library(TFBSTools)
library(motifmatchr)

# Get vertebrate motifs from JASPAR
pfm <- getMatrixSet(JASPAR2020, opts = list(collection = 'CORE', tax_group = 'vertebrates'))

# Match motifs to peaks
# p.cutoff=5e-5: Motif match p-value threshold. Lower = more stringent.
motif_ix <- matchMotifs(pfm, fragment_counts, genome = BSgenome.Hsapiens.UCSC.hg38, p.cutoff = 5e-5)
```

### From CIS-BP or Custom PWMs

```r
# Load custom motifs from file
library(universalmotif)
motifs <- read_meme('custom_motifs.meme')
pfm_list <- lapply(motifs, function(m) convert_motifs(m, class = 'TFBSTools-PFMatrix'))

motif_ix <- matchMotifs(pfm_list, fragment_counts, genome = BSgenome.Hsapiens.UCSC.hg38)
```

## Compute Deviations

```r
# Compute chromVAR deviation scores
dev <- computeDeviations(object = fragment_counts, annotations = motif_ix)

# Extract deviation scores (z-scores)
deviation_scores <- deviations(dev)

# Extract variability across samples
variability <- computeVariability(dev)
```

## Interpreting Results

### Deviation Scores

```r
# Deviation z-scores: positive = more accessible than expected
# Compare across samples
dev_matrix <- deviations(dev)
print(dim(dev_matrix))  # motifs x samples

# Get top variable motifs
var_df <- variability
var_df <- var_df[order(-var_df$variability), ]
head(var_df, 20)
```

### Variability Interpretation

| Variability | Interpretation |
|-------------|----------------|
| > 2.0 | Highly variable across samples |
| 1.0 - 2.0 | Moderately variable |
| < 1.0 | Low variability |

## Visualization

### Deviation Heatmap

```r
library(pheatmap)

# Get top variable motifs
# n_top=50: Number of top variable motifs to display.
n_top <- 50
top_motifs <- head(rownames(var_df), n_top)
top_dev <- deviation_scores[top_motifs, ]

# Add sample annotations
sample_info <- data.frame(
    Condition = colData(fragment_counts)$condition,
    row.names = colnames(top_dev)
)

pheatmap(top_dev, annotation_col = sample_info, scale = 'row',
         clustering_method = 'ward.D2', show_rownames = TRUE)
```

### Variability Plot

```r
plotVariability(variability, use_plotly = FALSE)
```

### PCA of Deviation Scores

```r
library(ggplot2)

# PCA on deviation scores
pca <- prcomp(t(deviation_scores), scale. = TRUE)
pca_df <- data.frame(PC1 = pca$x[,1], PC2 = pca$x[,2],
                     Condition = colData(fragment_counts)$condition)

ggplot(pca_df, aes(x = PC1, y = PC2, color = Condition)) +
    geom_point(size = 3) +
    theme_minimal() +
    labs(title = 'PCA of chromVAR Deviations')
```

## Differential Motif Accessibility

**Goal:** Identify TF motifs with significantly different accessibility between experimental groups.

**Approach:** Fit a linear model (limma) to deviation z-scores across groups and extract significant motifs with empirical Bayes moderation.

### Compare Two Groups

```r
library(limma)

# Get sample groups
groups <- factor(colData(fragment_counts)$condition)

# Design matrix
design <- model.matrix(~ groups)

# Fit linear model to deviation scores
fit <- lmFit(deviation_scores, design)
fit <- eBayes(fit)

# Get differential motifs
# p.value=0.05: FDR threshold for significance.
diff_motifs <- topTable(fit, coef = 2, number = Inf, p.value = 0.05)
print(head(diff_motifs, 20))
```

### Volcano Plot

```r
library(ggplot2)

all_results <- topTable(fit, coef = 2, number = Inf)
all_results$significant <- all_results$adj.P.Val < 0.05

ggplot(all_results, aes(x = logFC, y = -log10(adj.P.Val), color = significant)) +
    geom_point(alpha = 0.6) +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed') +
    scale_color_manual(values = c('grey', 'red')) +
    theme_minimal() +
    labs(title = 'Differential Motif Accessibility',
         x = 'Log2 Fold Change', y = '-log10(adjusted p-value)')
```

## Working with Single-Cell ATAC-seq

```r
# For scATAC-seq, aggregate cells by cluster first
# Then run chromVAR on pseudo-bulk profiles

# Or use chromVAR with sparse matrices
library(Matrix)

# Create SummarizedExperiment with sparse counts
sparse_counts <- Matrix(counts_matrix, sparse = TRUE)
fragment_counts <- SummarizedExperiment(
    assays = list(counts = sparse_counts),
    rowRanges = peak_ranges
)

# Proceed with standard workflow
fragment_counts <- addGCBias(fragment_counts, genome = BSgenome.Hsapiens.UCSC.hg38)
```

## Background Peaks Strategy

```r
# Custom background for better bias correction
# n_iterations=50: Number of background sets. Higher = more stable but slower.
bg <- getBackgroundPeaks(object = fragment_counts, niterations = 50)

# Use custom background in deviation calculation
dev <- computeDeviations(object = fragment_counts, annotations = motif_ix, background_peaks = bg)
```

## Export Results

```r
# Save deviation scores
write.csv(as.data.frame(deviation_scores), 'chromvar_deviations.csv')

# Save variability
write.csv(variability, 'chromvar_variability.csv')

# Save differential results
write.csv(diff_motifs, 'differential_motifs.csv')
```

## Complete Workflow

**Goal:** Run end-to-end chromVAR analysis from peak counts to motif variability scores.

**Approach:** Load counts, correct GC bias, filter peaks, match JASPAR motifs, compute deviations, and plot variability.

```r
library(chromVAR)
library(motifmatchr)
library(BSgenome.Hsapiens.UCSC.hg38)
library(JASPAR2020)
library(TFBSTools)

# 1. Load data
fragment_counts <- getCounts('peaks.bed', c('sample1.bam', 'sample2.bam', 'sample3.bam'))

# 2. Add GC bias
fragment_counts <- addGCBias(fragment_counts, genome = BSgenome.Hsapiens.UCSC.hg38)

# 3. Filter
fragment_counts <- filterPeaks(fragment_counts)

# 4. Get motifs
pfm <- getMatrixSet(JASPAR2020, opts = list(collection = 'CORE', tax_group = 'vertebrates'))
motif_ix <- matchMotifs(pfm, fragment_counts, genome = BSgenome.Hsapiens.UCSC.hg38)

# 5. Compute deviations
dev <- computeDeviations(fragment_counts, motif_ix)

# 6. Analyze variability
variability <- computeVariability(dev)
plotVariability(variability)
```

## Related Skills

- differential-accessibility - Peak-level differential analysis with DiffBind
- footprinting - TF footprinting with TOBIAS
- atac-qc - Quality control before chromVAR
- chip-seq/motif-analysis - Alternative motif enrichment approaches
