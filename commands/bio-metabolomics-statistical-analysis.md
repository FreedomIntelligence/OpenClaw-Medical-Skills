# bio-metabolomics-statistical-analysis

> Statistical analysis for metabolomics data. Covers univariate testing, multivariate methods (PCA, PLS-DA), and biomarker discovery. Use when identifying differentially abundant metabolites or building classification models.

## Version Compatibility

Reference examples tested with: R stats (base), ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolomics Statistical Analysis

## Univariate Analysis

**Goal:** Identify differentially abundant metabolites between experimental groups using feature-wise statistical tests.

**Approach:** Apply t-tests to each feature independently, then correct for multiple testing with Benjamini-Hochberg FDR.

**"Find the differentially abundant metabolites between my groups"** → Apply univariate and multivariate statistical methods to identify metabolites with significant abundance differences.

```r
library(tidyverse)

# Load normalized data
data <- read.csv('normalized_data.csv', row.names = 1)
groups <- factor(read.csv('sample_info.csv')$group)

# T-test for each feature
ttest_results <- apply(data, 2, function(x) {
    test <- t.test(x ~ groups)
    c(pvalue = test$p.value,
      fc = mean(x[groups == levels(groups)[2]]) - mean(x[groups == levels(groups)[1]]))
})
ttest_results <- as.data.frame(t(ttest_results))
ttest_results$fdr <- p.adjust(ttest_results$pvalue, method = 'BH')

# Significant features
sig_features <- ttest_results[ttest_results$fdr < 0.05, ]
cat('Significant features (FDR<0.05):', nrow(sig_features), '\n')
```

## Fold Change Calculation

**Goal:** Quantify the magnitude and direction of abundance changes between groups.

**Approach:** Compute group means for each feature and calculate log2 fold change as the ratio of group means.

```r
# Calculate fold change between groups
calculate_fc <- function(data, groups) {
    group_means <- aggregate(data, by = list(groups), FUN = mean, na.rm = TRUE)
    rownames(group_means) <- group_means$Group.1
    group_means <- group_means[, -1]

    fc <- as.numeric(group_means[2, ]) / as.numeric(group_means[1, ])
    log2fc <- log2(fc)

    return(data.frame(feature = colnames(data), fold_change = fc, log2fc = log2fc))
}

fc_results <- calculate_fc(data, groups)
```

## Volcano Plot

**Goal:** Visualize both statistical significance and effect size for all features in a single plot.

**Approach:** Plot log2 fold change (x-axis) vs -log10 p-value (y-axis), highlighting features passing both thresholds.

```r
library(ggplot2)

# Combine statistics
results <- merge(ttest_results, fc_results, by.x = 'row.names', by.y = 'feature')
results$significant <- results$fdr < 0.05 & abs(results$log2fc) > 1

# Plot
ggplot(results, aes(x = log2fc, y = -log10(pvalue), color = significant)) +
    geom_point(alpha = 0.6) +
    scale_color_manual(values = c('gray', 'red')) +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed') +
    geom_vline(xintercept = c(-1, 1), linetype = 'dashed') +
    labs(x = 'Log2 Fold Change', y = '-log10(p-value)', title = 'Metabolomics Volcano Plot') +
    theme_bw()

ggsave('volcano_plot.png', width = 8, height = 6)
```

## PCA

**Goal:** Explore overall sample variation and detect outliers or batch effects in an unsupervised manner.

**Approach:** Perform PCA on the feature matrix and plot the first two principal components colored by experimental group.

```r
library(pcaMethods)

# PCA
pca_result <- pca(data, nPcs = 5, method = 'ppca')

# Scores plot
scores <- as.data.frame(scores(pca_result))
scores$group <- groups

ggplot(scores, aes(x = PC1, y = PC2, color = group)) +
    geom_point(size = 3) +
    stat_ellipse(level = 0.95) +
    labs(x = paste0('PC1 (', round(pca_result@R2[1] * 100, 1), '%)'),
         y = paste0('PC2 (', round(pca_result@R2[2] * 100, 1), '%)')) +
    theme_bw()

ggsave('pca_plot.png', width = 8, height = 6)

# Loadings
loadings <- as.data.frame(loadings(pca_result))
top_pc1 <- loadings[order(abs(loadings$PC1), decreasing = TRUE)[1:20], ]
```

## PLS-DA

**Goal:** Build a supervised classification model that maximizes separation between experimental groups.

**Approach:** Fit a PLS-DA model with cross-validation to determine optimal components, then extract VIP scores to rank discriminatory features.

```r
library(mixOmics)

# PLS-DA
plsda_result <- plsda(as.matrix(data), groups, ncomp = 3)

# Cross-validation
perf_plsda <- perf(plsda_result, validation = 'Mfold', folds = 5, nrepeat = 50)
plot(perf_plsda, col = color.mixo(5:7))

# Optimal components
ncomp_opt <- perf_plsda$choice.ncomp['BER', 'centroids.dist']
cat('Optimal components:', ncomp_opt, '\n')

# Final model
final_plsda <- plsda(as.matrix(data), groups, ncomp = ncomp_opt)

# Plot
plotIndiv(final_plsda, group = groups, ellipse = TRUE, legend = TRUE)

# VIP scores
vip <- vip(final_plsda)
top_vip <- sort(vip[, ncomp_opt], decreasing = TRUE)[1:20]
print(top_vip)
```

## sPLS-DA (Sparse)

**Goal:** Perform feature selection simultaneously with classification to identify a minimal discriminatory feature set.

**Approach:** Tune the number of features to retain per component via cross-validation, then fit a sparse PLS-DA model.

```r
# Tune number of features to select
tune_splsda <- tune.splsda(as.matrix(data), groups, ncomp = 3,
                            validation = 'Mfold', folds = 5, nrepeat = 50,
                            test.keepX = c(5, 10, 20, 50, 100))

optimal_keepX <- tune_splsda$choice.keepX

# Final sparse model
splsda_result <- splsda(as.matrix(data), groups, ncomp = ncomp_opt, keepX = optimal_keepX)

# Selected features
selected_features <- selectVar(splsda_result, comp = 1)$name
cat('Selected features (comp 1):', length(selected_features), '\n')
```

## OPLS-DA (Orthogonal PLS-DA)

**Goal:** Separate group-predictive variation from orthogonal (within-group) variation for cleaner class separation.

**Approach:** Fit an OPLS-DA model using ropls, then use the S-plot to identify features with high predictive weight and correlation.

```r
library(ropls)

# OPLS-DA
oplsda <- opls(data, groups, predI = 1, orthoI = NA)

# Summary
print(oplsda)

# Scores plot
plot(oplsda, typeVc = 'x-score')

# S-plot (loadings vs correlation)
plot(oplsda, typeVc = 'x-loading')

# VIP
vip_scores <- getVipVn(oplsda)
top_vip <- sort(vip_scores, decreasing = TRUE)[1:20]
```

## Random Forest

**Goal:** Rank features by importance using a non-linear ensemble classifier.

**Approach:** Train a Random Forest on the feature matrix, then extract MeanDecreaseAccuracy to identify the most discriminatory features.

```r
library(randomForest)

# Random Forest classification
rf_model <- randomForest(x = data, y = groups, importance = TRUE, ntree = 500)

# Importance
importance <- importance(rf_model)
top_features <- rownames(importance)[order(importance[, 'MeanDecreaseAccuracy'], decreasing = TRUE)[1:20]]

# Plot importance
varImpPlot(rf_model, n.var = 20)
```

## ROC Analysis

**Goal:** Evaluate the diagnostic performance of candidate biomarker metabolites.

**Approach:** Generate ROC curves and compute AUC for individual features using pROC.

```r
library(pROC)

# ROC for top biomarker
top_feature <- 'feature_123'  # Replace with actual feature name
roc_result <- roc(groups, data[, top_feature])

# Plot
plot(roc_result, main = paste('AUC =', round(auc(roc_result), 3)))

# Multiple features
biomarkers <- c('feature_1', 'feature_2', 'feature_3')
for (feat in biomarkers) {
    roc_i <- roc(groups, data[, feat])
    cat(feat, ': AUC =', round(auc(roc_i), 3), '\n')
}
```

## Heatmap

**Goal:** Visualize abundance patterns of top differential features across all samples.

**Approach:** Select top significant features, create an annotated heatmap with hierarchical clustering using pheatmap.

```r
library(pheatmap)

# Top differential features
top_features <- rownames(sig_features)[1:50]
data_top <- data[, top_features]

# Annotation
annotation_row <- data.frame(Group = groups)
rownames(annotation_row) <- rownames(data)

pheatmap(t(data_top), annotation_col = annotation_row,
         scale = 'row', clustering_method = 'ward.D2',
         filename = 'heatmap.png', width = 10, height = 12)
```

## Related Skills

- normalization-qc - Data preparation
- pathway-mapping - Functional interpretation
- multi-omics-integration/mixomics-analysis - Advanced multivariate methods
