# bio-de-deseq2-basics

> Perform differential expression analysis using DESeq2 in R/Bioconductor. Use for analyzing RNA-seq count data, creating DESeqDataSet objects, running the DESeq workflow, and extracting results with log fold change shrinkage. Use when performing DE analysis with DESeq2.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, Salmon 1.10+, edgeR 4.0+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# DESeq2 Basics

Differential expression analysis using DESeq2 for RNA-seq count data.

## Required Libraries

```r
library(DESeq2)
library(apeglm)  # For lfcShrink with type='apeglm'
```

## Installation

```r
if (!require('BiocManager', quietly = TRUE))
    install.packages('BiocManager')
BiocManager::install('DESeq2')
BiocManager::install('apeglm')
```

## Creating DESeqDataSet

**Goal:** Construct a DESeqDataSet object from various input formats for DE analysis.

**Approach:** Wrap count data and sample metadata into the DESeq2 container, specifying the experimental design formula.

**"Load my RNA-seq counts into DESeq2"** → Create a DESeqDataSet from a count matrix, SummarizedExperiment, or tximport object with sample metadata and a design formula.

### From Count Matrix

```r
# counts: matrix with genes as rows, samples as columns
# coldata: data frame with sample metadata (rownames must match colnames of counts)
dds <- DESeqDataSetFromMatrix(countData = counts,
                               colData = coldata,
                               design = ~ condition)
```

### From SummarizedExperiment

```r
library(SummarizedExperiment)
dds <- DESeqDataSet(se, design = ~ condition)
```

### From tximport (Salmon/Kallisto)

```r
library(tximport)
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)
dds <- DESeqDataSetFromTximport(txi, colData = coldata, design = ~ condition)
```

## Standard DESeq2 Workflow

**Goal:** Run the complete DESeq2 pipeline from raw counts to shrunken log fold change estimates.

**Approach:** Create dataset, pre-filter low-count genes, set reference level, run size factor estimation + dispersion estimation + Wald test, then apply LFC shrinkage.

**"Find differentially expressed genes between treated and control"** → Test for significant expression changes between conditions using negative binomial models with empirical Bayes shrinkage.

```r
# Create DESeqDataSet
dds <- DESeqDataSetFromMatrix(countData = counts,
                               colData = coldata,
                               design = ~ condition)

# Pre-filter low count genes (recommended)
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep,]

# Set reference level for condition
dds$condition <- relevel(dds$condition, ref = 'control')

# Run DESeq2 pipeline (estimateSizeFactors, estimateDispersions, nbinomWaldTest)
dds <- DESeq(dds)

# Get results
res <- results(dds)

# Apply log fold change shrinkage (recommended for visualization/ranking)
resLFC <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')
```

## Design Formulas

**Goal:** Specify the experimental design to model biological and nuisance variables.

**Approach:** Build R formula objects that encode condition, batch, and interaction terms for the GLM.

```r
# Simple two-group comparison
design = ~ condition

# Controlling for batch effects
design = ~ batch + condition

# Interaction model
design = ~ genotype + treatment + genotype:treatment

# Multi-factor without interaction
design = ~ genotype + treatment
```

## Specifying Contrasts

**Goal:** Extract results for specific pairwise or complex comparisons from a fitted DESeq2 model.

**Approach:** Use coefficient names or contrast vectors to define which groups to compare.

```r
# See available coefficients
resultsNames(dds)

# Results by coefficient name
res <- results(dds, name = 'condition_treated_vs_control')

# Results by contrast (compare specific levels)
res <- results(dds, contrast = c('condition', 'treated', 'control'))

# Contrast with list format (for complex designs)
res <- results(dds, contrast = list('conditionB', 'conditionA'))
```

## Log Fold Change Shrinkage

**Goal:** Reduce noisy fold change estimates for low-count genes to improve ranking and visualization.

**Approach:** Apply empirical Bayes shrinkage (apeglm, ashr, or normal) to moderate log fold changes toward zero.

```r
# apeglm method (default, recommended)
resLFC <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')

# ashr method (alternative)
resLFC <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'ashr')

# normal method (original, less recommended)
resLFC <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'normal')
```

## Setting Significance Thresholds

**Goal:** Control the stringency of differential expression calls using adjusted p-value and fold change cutoffs.

**Approach:** Set alpha for multiple testing correction and optionally apply a minimum log fold change threshold.

```r
# Default: padj < 0.1
res <- results(dds)

# Custom alpha threshold
res <- results(dds, alpha = 0.05)

# With log fold change threshold
res <- results(dds, lfcThreshold = 1)  # |log2FC| > 1
```

## Accessing DESeq2 Results

**Goal:** Retrieve, filter, and sort DE results for downstream use.

**Approach:** Extract results as a data frame, subset by significance, and order by p-value or fold change.

```r
# Summary of results
summary(res)

# Get significant genes
sig <- subset(res, padj < 0.05)

# Order by adjusted p-value
resOrdered <- res[order(res$padj),]

# Order by log fold change
resOrdered <- res[order(abs(res$log2FoldChange), decreasing = TRUE),]

# Convert to data frame
res_df <- as.data.frame(res)
```

## Result Columns

| Column | Description |
|--------|-------------|
| `baseMean` | Mean of normalized counts across all samples |
| `log2FoldChange` | Log2 fold change (treatment vs control) |
| `lfcSE` | Standard error of log2 fold change |
| `stat` | Wald statistic |
| `pvalue` | Raw p-value |
| `padj` | Adjusted p-value (Benjamini-Hochberg) |

## Normalization and Counts

**Goal:** Obtain normalized expression values suitable for visualization and cross-sample comparison.

**Approach:** Extract size-factor-normalized counts or apply variance-stabilizing / rlog transformations.

```r
# Get normalized counts
normalized_counts <- counts(dds, normalized = TRUE)

# Get size factors
sizeFactors(dds)

# Variance stabilizing transformation (for visualization)
vsd <- vst(dds, blind = FALSE)

# Regularized log transformation (alternative, slower)
rld <- rlog(dds, blind = FALSE)
```

## Multi-Factor Designs

**Goal:** Account for batch or other nuisance variables while testing the effect of interest.

**Approach:** Include batch as a covariate in the design formula so DESeq2 adjusts for it during testing.

```r
# Design with batch correction
dds <- DESeqDataSetFromMatrix(countData = counts,
                               colData = coldata,
                               design = ~ batch + condition)
dds <- DESeq(dds)

# Extract condition effect (controlling for batch)
res <- results(dds, name = 'condition_treated_vs_control')
```

## Interaction Models

**Goal:** Identify genes whose response to treatment differs between genotypes (or other factor combinations).

**Approach:** Fit a model with interaction terms and test the interaction coefficient for significance.

```r
# Interaction between genotype and treatment
dds <- DESeqDataSetFromMatrix(countData = counts,
                               colData = coldata,
                               design = ~ genotype + treatment + genotype:treatment)
dds <- DESeq(dds)

# Test interaction term
res_interaction <- results(dds, name = 'genotypeKO.treatmentdrug')

# Or use contrast for difference of differences
res_interaction <- results(dds, contrast = list(
    c('genotypeKO.treatmentdrug'),
    c()
))
```

## Likelihood Ratio Test

**Goal:** Test whether a factor (e.g., condition) explains significant variance compared to a reduced model.

**Approach:** Compare full and reduced GLMs using a likelihood ratio test instead of Wald tests.

```r
# Compare full vs reduced model
dds <- DESeq(dds, test = 'LRT', reduced = ~ batch)

# Results from LRT
res <- results(dds)
```

## Pre-Filtering Strategies

**Goal:** Remove uninformative genes to reduce multiple testing burden and improve statistical power.

**Approach:** Apply count-based filters requiring minimum expression across a threshold number of samples.

```r
# Remove genes with low counts
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep,]

# Keep genes with at least n counts in at least k samples
keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep,]

# Filter by expression level
keep <- rowMeans(counts(dds, normalized = TRUE)) >= 10
dds <- dds[keep,]
```

## Working with Existing Objects

```r
# Update design formula
design(dds) <- ~ batch + condition
dds <- DESeq(dds)

# Subset samples
dds_subset <- dds[, dds$group == 'A']

# Subset genes
dds_genes <- dds[rownames(dds) %in% gene_list,]
```

## Exporting Results

**Goal:** Save DE results and normalized counts to files for sharing or downstream tools.

**Approach:** Convert results to data frames and write as CSV files.

```r
# Write to CSV
write.csv(as.data.frame(resOrdered), file = 'deseq2_results.csv')

# Write normalized counts
write.csv(as.data.frame(normalized_counts), file = 'normalized_counts.csv')
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "design matrix not full rank" | Confounded variables or missing levels | Check coldata for confounding |
| "counts matrix should be integers" | Non-integer counts (e.g., from tximport) | Use DESeqDataSetFromTximport() |
| "all samples have 0 counts" | Gene filtering issue | Check count matrix format |
| "factor levels not in colData" | Typo in design formula | Verify column names in coldata |

## Deprecated Features

| Feature | Status | Alternative |
|---------|--------|-------------|
| No-replicate designs | Removed (v1.22) | Require biological replicates |
| `betaPrior = TRUE` | Deprecated | Use `lfcShrink()` instead |
| `rlog()` for large datasets | Not recommended | Use `vst()` for >100 samples |

## Quick Reference: Workflow Steps

```r
# 1. Create DESeqDataSet
dds <- DESeqDataSetFromMatrix(counts, coldata, design = ~ condition)

# 2. Pre-filter
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep,]

# 3. Set reference level
dds$condition <- relevel(dds$condition, ref = 'control')

# 4. Run DESeq2
dds <- DESeq(dds)

# 5. Get results with shrinkage
res <- lfcShrink(dds, coef = resultsNames(dds)[2], type = 'apeglm')

# 6. Filter significant genes
sig_genes <- subset(res, padj < 0.05 & abs(log2FoldChange) > 1)
```

## Related Skills

- edger-basics - Alternative DE analysis with edgeR
- de-visualization - MA plots, volcano plots, heatmaps
- de-results - Extract and export significant genes
