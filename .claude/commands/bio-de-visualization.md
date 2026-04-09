# bio-de-visualization

> Visualize differential expression results using DESeq2/edgeR built-in functions. Covers plotMA, plotDispEsts, plotCounts, plotBCV, sample distance heatmaps, and p-value histograms. Use when visualizing differential expression results.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, edgeR 4.0+, ggplot2 3.5+, limma 3.58+, matplotlib 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# DE Visualization

Create visualizations for differential expression analysis using DESeq2 and edgeR built-in plotting functions.

## Scope

This skill covers **DE-specific built-in functions**:
- DESeq2: `plotMA()`, `plotPCA()`, `plotDispEsts()`, `plotCounts()`
- edgeR: `plotMD()`, `plotBCV()`, `plotMDS()`
- Sample distance heatmaps and p-value distributions

**For custom ggplot2/matplotlib implementations** of volcano, MA, and PCA plots, see `data-visualization/specialized-omics-plots`.

## Required Libraries

```r
library(DESeq2)
library(ggplot2)
library(pheatmap)
library(RColorBrewer)
library(ggrepel)  # For labeled points
```

## Installation

```r
install.packages(c('ggplot2', 'pheatmap', 'RColorBrewer', 'ggrepel'))
# Optional: Enhanced volcano plots
BiocManager::install('EnhancedVolcano')
```

## MA Plot

**Goal:** Visualize the relationship between mean expression and log fold change to assess DE results.

**Approach:** Plot log fold change against mean normalized counts, highlighting significant genes.

**"Make an MA plot of my DE results"** → Plot mean expression vs. fold change with significant genes colored, using plotMA or ggplot2.

### DESeq2 MA Plot

```r
# Built-in MA plot
plotMA(res, ylim = c(-5, 5), main = 'MA Plot')

# With custom alpha
plotMA(res, alpha = 0.05, ylim = c(-5, 5))

# Highlight specific genes
plotMA(res, ylim = c(-5, 5))
with(subset(res, padj < 0.01 & abs(log2FoldChange) > 2),
     points(baseMean, log2FoldChange, col = 'red', pch = 20))
```

### Custom ggplot2 MA Plot

```r
res_df <- as.data.frame(res)
res_df$significant <- res_df$padj < 0.05 & !is.na(res_df$padj)

ggplot(res_df, aes(x = log10(baseMean), y = log2FoldChange, color = significant)) +
    geom_point(alpha = 0.5, size = 1) +
    scale_color_manual(values = c('grey60', 'red')) +
    geom_hline(yintercept = 0, linetype = 'dashed') +
    labs(x = 'log10(Mean Expression)', y = 'log2 Fold Change', title = 'MA Plot') +
    theme_bw() +
    theme(legend.position = 'bottom')
```

### edgeR MA Plot

```r
# Using plotMD (mean-difference plot)
plotMD(qlf, main = 'MD Plot')
abline(h = c(-1, 1), col = 'blue', lty = 2)
```

## Volcano Plot

**Goal:** Display statistical significance against fold change magnitude to identify the most important DE genes.

**Approach:** Plot -log10(p-value) vs. log2 fold change with threshold lines and optional gene labels.

**"Create a volcano plot of differentially expressed genes"** → Scatter plot of fold change vs. significance with colored significance regions and labeled top hits.

### Basic Volcano Plot

```r
res_df <- as.data.frame(res)
res_df$significant <- res_df$padj < 0.05 & abs(res_df$log2FoldChange) > 1

ggplot(res_df, aes(x = log2FoldChange, y = -log10(pvalue), color = significant)) +
    geom_point(alpha = 0.5, size = 1) +
    scale_color_manual(values = c('grey60', 'red')) +
    geom_vline(xintercept = c(-1, 1), linetype = 'dashed', color = 'blue') +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed', color = 'blue') +
    labs(x = 'log2 Fold Change', y = '-log10(p-value)', title = 'Volcano Plot') +
    theme_bw()
```

### Volcano with Gene Labels

```r
res_df <- as.data.frame(res)
res_df$gene <- rownames(res_df)
res_df$significant <- res_df$padj < 0.05 & abs(res_df$log2FoldChange) > 1

# Label top genes
top_genes <- head(res_df[order(res_df$padj), ], 10)

ggplot(res_df, aes(x = log2FoldChange, y = -log10(pvalue))) +
    geom_point(aes(color = significant), alpha = 0.5, size = 1) +
    scale_color_manual(values = c('grey60', 'red')) +
    geom_text_repel(data = top_genes, aes(label = gene),
                    size = 3, max.overlaps = 20) +
    geom_vline(xintercept = c(-1, 1), linetype = 'dashed') +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed') +
    labs(x = 'log2 Fold Change', y = '-log10(p-value)') +
    theme_bw()
```

### EnhancedVolcano

```r
library(EnhancedVolcano)

EnhancedVolcano(res,
    lab = rownames(res),
    x = 'log2FoldChange',
    y = 'pvalue',
    pCutoff = 0.05,
    FCcutoff = 1,
    title = 'Differential Expression',
    subtitle = 'Treatment vs Control')
```

## PCA Plot

**Goal:** Assess sample clustering and identify batch effects or outliers via dimensionality reduction.

**Approach:** Apply variance-stabilizing transformation then project samples onto principal components, coloring by experimental variables.

**"Show me a PCA plot of my samples"** → Perform PCA on transformed expression data and visualize sample separation by condition and batch.

### DESeq2 PCA

```r
# Variance stabilizing transformation first
vsd <- vst(dds, blind = FALSE)

# Basic PCA
plotPCA(vsd, intgroup = 'condition')

# With more options
plotPCA(vsd, intgroup = c('condition', 'batch'), ntop = 500)
```

### Custom PCA with ggplot2

```r
vsd <- vst(dds, blind = FALSE)
pca_data <- plotPCA(vsd, intgroup = c('condition', 'batch'), returnData = TRUE)
percentVar <- round(100 * attr(pca_data, 'percentVar'))

ggplot(pca_data, aes(x = PC1, y = PC2, color = condition, shape = batch)) +
    geom_point(size = 4) +
    xlab(paste0('PC1: ', percentVar[1], '% variance')) +
    ylab(paste0('PC2: ', percentVar[2], '% variance')) +
    ggtitle('PCA Plot') +
    theme_bw() +
    theme(legend.position = 'right')
```

### edgeR PCA (via limma)

```r
library(limma)
log_cpm <- cpm(y, log = TRUE)
plotMDS(log_cpm, col = as.numeric(group), pch = 16)
legend('topright', legend = levels(group), col = 1:nlevels(group), pch = 16)
```

## Heatmaps

**Goal:** Visualize expression patterns of significant genes across samples to reveal clusters and condition effects.

**Approach:** Z-score normalize VST-transformed counts for significant genes and cluster with pheatmap, annotating by condition.

**"Make a heatmap of the top differentially expressed genes"** → Extract significant genes, z-score normalize, and create a clustered heatmap with sample annotations.

### Top DE Genes Heatmap

```r
library(pheatmap)

# Get top significant genes
sig_genes <- rownames(subset(res, padj < 0.01))

# Get normalized counts
vsd <- vst(dds, blind = FALSE)
mat <- assay(vsd)[sig_genes, ]

# Scale by row (z-score)
mat_scaled <- t(scale(t(mat)))

# Create annotation
annotation_col <- data.frame(
    condition = colData(dds)$condition,
    row.names = colnames(mat)
)

pheatmap(mat_scaled,
         annotation_col = annotation_col,
         show_rownames = FALSE,
         clustering_distance_rows = 'correlation',
         clustering_distance_cols = 'correlation',
         color = colorRampPalette(c('blue', 'white', 'red'))(100),
         main = 'Top DE Genes')
```

### Sample Distance Heatmap

```r
vsd <- vst(dds, blind = FALSE)

# Calculate sample distances
sampleDists <- dist(t(assay(vsd)))
sampleDistMatrix <- as.matrix(sampleDists)

# Annotation
annotation <- data.frame(
    condition = colData(dds)$condition,
    row.names = colnames(dds)
)

pheatmap(sampleDistMatrix,
         annotation_col = annotation,
         annotation_row = annotation,
         clustering_distance_rows = sampleDists,
         clustering_distance_cols = sampleDists,
         color = colorRampPalette(c('white', 'steelblue'))(100),
         main = 'Sample Distance Matrix')
```

### Gene Expression Heatmap

```r
# Select genes of interest
genes_of_interest <- c('gene1', 'gene2', 'gene3', 'gene4', 'gene5')
mat <- assay(vsd)[genes_of_interest, ]

pheatmap(mat,
         scale = 'row',
         annotation_col = annotation_col,
         show_rownames = TRUE,
         cluster_cols = TRUE,
         cluster_rows = TRUE,
         main = 'Genes of Interest')
```

## Dispersion Plot

**Goal:** Assess the fit of the dispersion model to verify DE analysis assumptions.

**Approach:** Plot gene-wise, fitted, and final dispersion estimates against mean expression.

### DESeq2

```r
plotDispEsts(dds, main = 'Dispersion Estimates')
```

### edgeR

```r
plotBCV(y, main = 'Biological Coefficient of Variation')
```

## Counts Plot for Individual Genes

**Goal:** Visualize expression of a specific gene across samples and conditions.

**Approach:** Extract per-sample counts for a gene and plot by condition using plotCounts or ggplot2.

### DESeq2

```r
# Plot counts for a specific gene
plotCounts(dds, gene = 'GENE_NAME', intgroup = 'condition')

# With ggplot2
d <- plotCounts(dds, gene = 'GENE_NAME', intgroup = 'condition', returnData = TRUE)
ggplot(d, aes(x = condition, y = count, color = condition)) +
    geom_point(position = position_jitter(width = 0.1), size = 3) +
    scale_y_log10() +
    ggtitle('GENE_NAME Expression') +
    theme_bw()
```

### edgeR

```r
# Get CPM for a gene
gene_idx <- which(rownames(y) == 'GENE_NAME')
cpm_gene <- cpm(y)[gene_idx, ]

# Plot
df <- data.frame(cpm = cpm_gene, group = group)
ggplot(df, aes(x = group, y = cpm, color = group)) +
    geom_point(position = position_jitter(width = 0.1), size = 3) +
    scale_y_log10() +
    labs(y = 'CPM', title = 'GENE_NAME Expression') +
    theme_bw()
```

## P-value Histogram

**Goal:** Diagnose the quality of the DE analysis by examining the raw p-value distribution.

**Approach:** Histogram of raw p-values; a uniform distribution with a peak near zero indicates a well-calibrated test.

```r
# Check p-value distribution (should be uniform under null with peak near 0)
res_df <- as.data.frame(res)
ggplot(res_df, aes(x = pvalue)) +
    geom_histogram(bins = 50, fill = 'steelblue', color = 'white') +
    labs(x = 'P-value', y = 'Frequency', title = 'P-value Distribution') +
    theme_bw()
```

## Saving Plots

**Goal:** Export publication-quality plots in vector or raster formats.

**Approach:** Use pdf/png devices or ggsave with appropriate resolution and dimensions.

```r
# Save as PDF (vector)
pdf('volcano_plot.pdf', width = 8, height = 6)
# ... plot code ...
dev.off()

# Save as PNG (raster)
png('volcano_plot.png', width = 800, height = 600, res = 150)
# ... plot code ...
dev.off()

# Using ggsave for ggplot objects
p <- ggplot(...) + ...
ggsave('plot.pdf', p, width = 8, height = 6)
ggsave('plot.png', p, width = 8, height = 6, dpi = 300)
```

## Color Palettes

**Goal:** Select appropriate color schemes for heatmaps and categorical data.

**Approach:** Use RColorBrewer palettes -- diverging for expression, sequential for distances, qualitative for groups.

```r
# For heatmaps
library(RColorBrewer)

# Diverging (for expression: blue-white-red)
colorRampPalette(rev(brewer.pal(n = 7, name = 'RdBu')))(100)

# Sequential (for distances)
colorRampPalette(brewer.pal(n = 9, name = 'Blues'))(100)

# For categorical groups
brewer.pal(n = 8, name = 'Set1')
```

## Quick Reference: Common Plots

| Plot | Purpose | Function |
|------|---------|----------|
| MA plot | LFC vs mean expression | `plotMA()`, `plotMD()` |
| Volcano | LFC vs significance | ggplot2, EnhancedVolcano |
| PCA | Sample clustering | `plotPCA()`, `plotMDS()` |
| Heatmap | Gene patterns | `pheatmap()` |
| Dispersion | Model fit | `plotDispEsts()`, `plotBCV()` |
| Counts | Individual genes | `plotCounts()` |

## Related Skills

- deseq2-basics - Generate DESeq2 results for visualization
- edger-basics - Generate edgeR results for visualization
- de-results - Filter genes before visualization
- data-visualization/specialized-omics-plots - Custom ggplot2 volcano/MA/PCA functions
- data-visualization/heatmaps-clustering - Advanced heatmap customization
