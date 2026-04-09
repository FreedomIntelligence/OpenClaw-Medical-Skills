# bio-small-rna-seq-differential-mirna

> Perform differential expression analysis of miRNAs between conditions using DESeq2 or edgeR with small RNA-specific considerations. Use when identifying miRNAs that change between treatment groups, disease states, or developmental stages.

**Available tools:** Read, Bash

# Differential miRNA Expression

## Load miRNA Count Data

```r
library(DESeq2)

# Load miRge3 or miRDeep2 counts
counts <- read.csv('miR.Counts.csv', row.names = 1)

# Create sample metadata
coldata <- data.frame(
    sample = colnames(counts),
    condition = factor(c('control', 'control', 'treated', 'treated')),
    row.names = colnames(counts)
)
```

## DESeq2 Analysis

```r
# Create DESeq2 dataset
dds <- DESeqDataSetFromMatrix(
    countData = round(counts),  # DESeq2 requires integers
    colData = coldata,
    design = ~ condition
)

# Filter low-expressed miRNAs
# miRNAs typically have fewer total counts than mRNAs
# Keep miRNAs with at least 10 reads across samples
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep, ]

# Run DESeq2
dds <- DESeq(dds)

# Get results
res <- results(dds, contrast = c('condition', 'treated', 'control'))
res <- res[order(res$padj), ]
```

## Apply Shrinkage for Effect Sizes

```r
# apeglm shrinkage for more accurate log2 fold changes
# Particularly important for low-count miRNAs
library(apeglm)

res_shrunk <- lfcShrink(
    dds,
    coef = 'condition_treated_vs_control',
    type = 'apeglm'
)
```

## Filter Significant miRNAs

```r
# Standard thresholds for miRNA DE
# padj < 0.05: FDR-corrected significance
# |log2FC| > 1: 2-fold change minimum
sig <- subset(res_shrunk, padj < 0.05 & abs(log2FoldChange) > 1)
sig <- sig[order(sig$padj), ]

# Separate up and down-regulated
up <- subset(sig, log2FoldChange > 0)
down <- subset(sig, log2FoldChange < 0)

cat('Upregulated:', nrow(up), '\n')
cat('Downregulated:', nrow(down), '\n')
```

## edgeR Alternative

```r
library(edgeR)

# Create DGEList
dge <- DGEList(counts = counts, group = coldata$condition)

# Filter low expression
keep <- filterByExpr(dge)
dge <- dge[keep, , keep.lib.sizes = FALSE]

# Normalize
dge <- calcNormFactors(dge)

# Design matrix
design <- model.matrix(~ condition, data = coldata)

# Estimate dispersion
dge <- estimateDisp(dge, design)

# Fit model and test
fit <- glmQLFit(dge, design)
qlf <- glmQLFTest(fit, coef = 2)

# Get results
res_edger <- topTags(qlf, n = Inf)$table
```

## Visualization

```r
library(ggplot2)
library(EnhancedVolcano)

# Volcano plot
EnhancedVolcano(
    res_shrunk,
    lab = rownames(res_shrunk),
    x = 'log2FoldChange',
    y = 'padj',
    pCutoff = 0.05,
    FCcutoff = 1,
    title = 'Differential miRNA Expression'
)

# MA plot
plotMA(res_shrunk, ylim = c(-4, 4))
```

## Heatmap of DE miRNAs

```r
library(pheatmap)

# Get normalized counts
vsd <- vst(dds, blind = FALSE)

# Select significant miRNAs
sig_mirnas <- rownames(sig)
mat <- assay(vsd)[sig_mirnas, ]

# Z-score scale rows
mat_scaled <- t(scale(t(mat)))

pheatmap(
    mat_scaled,
    annotation_col = coldata['condition'],
    cluster_rows = TRUE,
    cluster_cols = TRUE,
    show_rownames = nrow(mat) < 50
)
```

## Export Results

```r
# Full results with normalized counts
res_df <- as.data.frame(res_shrunk)
res_df$miRNA <- rownames(res_df)
res_df$baseMean_norm <- rowMeans(counts(dds, normalized = TRUE)[rownames(res_df), ])

write.csv(res_df, 'DE_miRNAs_full.csv', row.names = FALSE)

# Significant only
write.csv(as.data.frame(sig), 'DE_miRNAs_significant.csv')
```

## Related Skills

- mirge3-analysis - Get miRNA counts
- mirdeep2-analysis - Alternative quantification
- target-prediction - Predict targets of DE miRNAs
- differential-expression/deseq2-basics - General DE analysis concepts
