# bio-rna-quantification-count-matrix-qc

> Quality control and exploration of RNA-seq count matrices before differential expression. Check for outliers, batch effects, and sample relationships. Use when assessing count matrix quality before DE analysis.

**Available tools:** Read, Bash

# Count Matrix QC

Quality control and exploratory analysis of count matrices before differential expression.

## Load and Inspect Counts

### R

```r
library(DESeq2)

# From tximport
dds <- DESeqDataSetFromTximport(txi, colData = coldata, design = ~ condition)

# From count matrix
counts <- read.csv('count_matrix.csv', row.names = 1)
coldata <- data.frame(condition = factor(c('ctrl', 'ctrl', 'treat', 'treat')),
                      row.names = colnames(counts))
dds <- DESeqDataSetFromMatrix(countData = counts, colData = coldata,
                              design = ~ condition)
```

### Python

```python
import pandas as pd
import numpy as np

counts = pd.read_csv('count_matrix.csv', index_col=0)
metadata = pd.read_csv('sample_info.csv', index_col=0)
```

## Basic Statistics

### R

```r
# Total counts per sample
colSums(counts(dds))

# Genes detected per sample
colSums(counts(dds) > 0)

# Counts summary
summary(colSums(counts(dds)))
```

### Python

```python
total_counts = counts.sum()
genes_detected = (counts > 0).sum()

print('Total counts per sample:')
print(total_counts)
print('\nGenes detected:')
print(genes_detected)
```

## Filter Low-Count Genes

### R

```r
# Remove genes with low counts across samples
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep, ]

# More stringent: at least N samples with count >= M
keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep, ]
```

### Python

```python
min_counts = 10
min_samples = 3

gene_filter = (counts >= min_counts).sum(axis=1) >= min_samples
counts_filtered = counts[gene_filter]
```

## Normalize for Visualization

### R (DESeq2 VST)

```r
# Variance stabilizing transformation
vsd <- vst(dds, blind = TRUE)

# Or regularized log (slower, better for small n)
rld <- rlog(dds, blind = TRUE)

# Get transformed values
vst_matrix <- assay(vsd)
```

### Python (log2 CPM)

```python
from sklearn.preprocessing import StandardScaler

cpm = counts * 1e6 / counts.sum()
log_cpm = np.log2(cpm + 1)
```

## Sample Correlation

### R

```r
library(pheatmap)

# Sample correlation heatmap
sample_cor <- cor(assay(vsd))
pheatmap(sample_cor, annotation_col = coldata)

# Sample distance heatmap
sample_dist <- dist(t(assay(vsd)))
pheatmap(as.matrix(sample_dist), annotation_col = coldata)
```

### Python

```python
import seaborn as sns
import matplotlib.pyplot as plt

sample_cor = log_cpm.corr()
sns.clustermap(sample_cor, annot=True, cmap='RdBu_r', center=0.9,
               vmin=0.8, vmax=1.0)
plt.savefig('sample_correlation.png')
```

## PCA Analysis

### R

```r
# PCA plot
plotPCA(vsd, intgroup = 'condition')

# Custom PCA
pca <- prcomp(t(assay(vsd)))
pca_df <- data.frame(PC1 = pca$x[,1], PC2 = pca$x[,2],
                     condition = coldata$condition)

library(ggplot2)
ggplot(pca_df, aes(PC1, PC2, color = condition)) +
    geom_point(size = 3) +
    geom_text(aes(label = rownames(pca_df)), vjust = -0.5)
```

### Python

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
pca_result = pca.fit_transform(log_cpm.T)

plt.figure(figsize=(8, 6))
for condition in metadata['condition'].unique():
    mask = metadata['condition'] == condition
    plt.scatter(pca_result[mask, 0], pca_result[mask, 1], label=condition)
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
plt.legend()
plt.savefig('pca_plot.png')
```

## Detect Outliers

### R

```r
# Cook's distance (after DESeq)
dds <- DESeq(dds)
W <- results(dds)$cooksd
boxplot(W, main = "Cook's Distance")

# Identify outlier samples from PCA
pca <- prcomp(t(assay(vsd)))
outliers <- abs(scale(pca$x[,1])) > 3 | abs(scale(pca$x[,2])) > 3
```

### Python

```python
from scipy import stats

z_scores = stats.zscore(pca_result, axis=0)
outliers = (np.abs(z_scores) > 3).any(axis=1)
print('Potential outliers:', counts.columns[outliers].tolist())
```

## Check for Batch Effects

### R

```r
# Color PCA by batch
plotPCA(vsd, intgroup = c('condition', 'batch'))

# Test for batch effect
design(dds) <- ~ batch + condition
dds <- DESeq(dds)
```

### Python

```python
# Color by batch in PCA
for batch in metadata['batch'].unique():
    mask = metadata['batch'] == batch
    plt.scatter(pca_result[mask, 0], pca_result[mask, 1],
                marker=['o', 's', '^'][list(metadata['batch'].unique()).index(batch)],
                label=f'Batch {batch}')
```

## Library Complexity

### R

```r
# Genes detected vs library size
plot(colSums(counts(dds)), colSums(counts(dds) > 0),
     xlab = 'Library Size', ylab = 'Genes Detected')

# Saturation check
```

### Python

```python
plt.scatter(counts.sum(), (counts > 0).sum())
plt.xlabel('Total Counts')
plt.ylabel('Genes Detected')
plt.savefig('library_complexity.png')
```

## Gene-Level QC

### R

```r
# Most variable genes
rv <- rowVars(assay(vsd))
top_var <- order(rv, decreasing = TRUE)[1:500]

# Expression distribution
boxplot(log2(counts(dds) + 1), las = 2)
```

### Python

```python
gene_var = log_cpm.var(axis=1).sort_values(ascending=False)
top_var_genes = gene_var.head(500).index

counts[top_var_genes].boxplot(figsize=(12, 6))
plt.xticks(rotation=45)
plt.savefig('gene_expression_dist.png')
```

## Summary Report

```r
# Quick summary
cat('Samples:', ncol(dds), '\n')
cat('Genes before filter:', nrow(counts), '\n')
cat('Genes after filter:', nrow(dds), '\n')
cat('Median library size:', median(colSums(counts(dds))), '\n')
cat('Median genes detected:', median(colSums(counts(dds) > 0)), '\n')
```

## Related Skills

- rna-quantification/featurecounts-counting - Generate counts
- rna-quantification/tximport-workflow - Import transcript counts
- differential-expression/de-visualization - Downstream visualization
- differential-expression/deseq2-basics - DE analysis
