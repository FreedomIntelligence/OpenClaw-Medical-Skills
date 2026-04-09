# bio-differential-expression-batch-correction

> Remove batch effects from RNA-seq data using ComBat, ComBat-Seq, limma removeBatchEffect, and SVA for unknown batch variables. Use when correcting batch effects in expression data.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, ggplot2 3.5+, limma 3.58+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Batch Effect Correction

## ComBat-Seq (Count Data)

**Goal:** Remove batch effects from raw count data while preserving biological group differences.

**Approach:** Apply ComBat-Seq's negative binomial regression to adjust counts, keeping the integer nature of the data.

**"Remove batch effects from my RNA-seq counts"** → Adjust raw count matrix for known batch labels using negative binomial modeling, preserving biological condition effects.

```r
library(sva)

# counts: raw count matrix (genes x samples)
# batch: vector of batch labels
# group: vector of biological condition (optional, to preserve)

corrected_counts <- ComBat_seq(counts = as.matrix(counts),
                                batch = batch,
                                group = condition,
                                full_mod = TRUE)

# Result is batch-corrected count matrix
# Use for visualization, clustering, but NOT for DE (use design formula instead)
```

## ComBat (Normalized Data)

**Goal:** Remove batch effects from normalized (log-transformed or TPM) expression data.

**Approach:** Apply parametric empirical Bayes adjustment to normalized expression while protecting biological covariates.

```r
library(sva)

# For normalized expression (log-transformed, TPM, etc.)
# NOT for raw counts

# Create model matrix
mod <- model.matrix(~ condition, data = metadata)
mod0 <- model.matrix(~ 1, data = metadata)

# Run ComBat
corrected_expr <- ComBat(dat = as.matrix(normalized_expr),
                          batch = metadata$batch,
                          mod = mod,
                          par.prior = TRUE)
```

## limma removeBatchEffect

**Goal:** Produce batch-corrected expression values for visualization while preserving group differences.

**Approach:** Regress out the batch effect from normalized expression using limma's linear model.

```r
library(limma)

# For visualization/clustering only
# Preserves group differences while removing batch

design <- model.matrix(~ condition, data = metadata)
corrected_expr <- removeBatchEffect(normalized_expr,
                                     batch = metadata$batch,
                                     design = design)

# For PCA, heatmaps, etc.
```

## DESeq2 Design Formula (Recommended for DE)

**Goal:** Account for batch effects during DE testing without modifying the count data.

**Approach:** Include batch as a covariate in the DESeq2 design formula so batch variance is modeled, not removed.

```r
library(DESeq2)

# Include batch in design formula - preferred for DE analysis
dds <- DESeqDataSetFromMatrix(countData = counts,
                               colData = metadata,
                               design = ~ batch + condition)

# Batch is modeled, not removed
# DE results are adjusted for batch
dds <- DESeq(dds)
res <- results(dds, contrast = c('condition', 'treatment', 'control'))
```

## Surrogate Variable Analysis (SVA)

**Goal:** Discover and correct for unknown sources of variation (hidden batch effects).

**Approach:** Estimate surrogate variables from the residual variation not explained by the biological model.

**"Correct for unknown batch effects in my expression data"** → Estimate latent surrogate variables capturing unwanted variation, then include them as covariates in the DE model.

```r
library(sva)

# When batch is unknown, estimate surrogate variables
mod <- model.matrix(~ condition, data = metadata)
mod0 <- model.matrix(~ 1, data = metadata)

# Estimate number of surrogate variables
n_sv <- num.sv(normalized_expr, mod, method = 'leek')

# Estimate surrogate variables
svobj <- sva(normalized_expr, mod, mod0, n.sv = n_sv)

# Add SVs to design for DE
design_with_sv <- cbind(mod, svobj$sv)
```

## SVA with DESeq2

**Goal:** Integrate surrogate variables into DESeq2 to adjust for hidden confounders during DE testing.

**Approach:** Estimate SVs from normalized counts, add them to colData, and update the design formula.

```r
library(DESeq2)
library(sva)

# Normalize for SV estimation
dds <- DESeqDataSetFromMatrix(countData = counts, colData = metadata, design = ~ condition)
dds <- estimateSizeFactors(dds)
norm_counts <- counts(dds, normalized = TRUE)

# Estimate SVs
mod <- model.matrix(~ condition, data = metadata)
mod0 <- model.matrix(~ 1, data = metadata)
svobj <- sva(norm_counts, mod, mod0)

# Add SVs to colData
for (i in seq_len(ncol(svobj$sv))) {
    colData(dds)[[paste0('SV', i)]] <- svobj$sv[, i]
}

# Update design
sv_formula <- as.formula(paste('~', paste(paste0('SV', 1:ncol(svobj$sv)), collapse = ' + '), '+ condition'))
design(dds) <- sv_formula

# Run DESeq2
dds <- DESeq(dds)
```

## Visualize Batch Effects

**Goal:** Confirm batch effect removal by comparing PCA plots before and after correction.

**Approach:** Run PCA on pre- and post-correction expression, coloring points by batch and condition.

```r
library(ggplot2)

# PCA before correction
pca_before <- prcomp(t(normalized_expr), scale. = TRUE)
pca_df <- data.frame(PC1 = pca_before$x[, 1], PC2 = pca_before$x[, 2],
                     batch = metadata$batch, condition = metadata$condition)

p1 <- ggplot(pca_df, aes(PC1, PC2, color = batch, shape = condition)) +
    geom_point(size = 3) + ggtitle('Before Correction')

# PCA after correction
pca_after <- prcomp(t(corrected_expr), scale. = TRUE)
pca_df_after <- data.frame(PC1 = pca_after$x[, 1], PC2 = pca_after$x[, 2],
                           batch = metadata$batch, condition = metadata$condition)

p2 <- ggplot(pca_df_after, aes(PC1, PC2, color = batch, shape = condition)) +
    geom_point(size = 3) + ggtitle('After Correction')

library(patchwork)
p1 + p2
```

## Quantify Batch Effect

**Goal:** Measure the proportion of variance attributable to batch versus biological condition.

**Approach:** Correlate principal components with batch and condition labels, or use PVCA.

```r
# PVCA - Principal Variance Component Analysis
library(pvca)

# Proportion of variance explained by batch vs condition
pvcaObj <- pvcaBatchAssess(normalized_expr, metadata, threshold = 0.6,
                            theInteractionTerms = c('batch', 'condition'))

# Or manual approach
pca <- prcomp(t(normalized_expr), scale. = TRUE)
variance_explained <- summary(pca)$importance[2, 1:5]

# Correlation of PCs with batch
cor(pca$x[, 1], as.numeric(as.factor(metadata$batch)))
```

## Harmony (Single-Cell Integration)

**Goal:** Integrate single-cell data from multiple batches into a shared embedding.

**Approach:** Apply Harmony to PCA embeddings to iteratively remove batch effects while preserving cell-type structure.

```r
library(harmony)
library(Seurat)

# For single-cell data with multiple batches
seurat_obj <- RunHarmony(seurat_obj, group.by.vars = 'batch', reduction = 'pca',
                          dims.use = 1:30)

# Use harmony reduction for downstream
seurat_obj <- RunUMAP(seurat_obj, reduction = 'harmony', dims = 1:30)
seurat_obj <- FindNeighbors(seurat_obj, reduction = 'harmony', dims = 1:30)
```

## When NOT to Correct

```r
# DON'T use batch-corrected values for:
# - Differential expression (use design formula instead)
# - Count-based methods expecting raw/normalized counts

# DO use batch-corrected values for:
# - Visualization (PCA, UMAP, heatmaps)
# - Clustering
# - Machine learning features
# - Cross-study comparisons
```

## Related Skills

- differential-expression/deseq2-basics - DE with batch in design
- single-cell/clustering - Integration methods
- expression-matrix/matrix-operations - Data transformation
