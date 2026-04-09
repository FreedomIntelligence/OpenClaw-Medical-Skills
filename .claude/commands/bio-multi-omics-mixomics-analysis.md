# bio-multi-omics-mixomics-analysis

> Supervised and unsupervised multi-omics integration with mixOmics. Includes sPLS for pairwise integration and DIABLO for multi-block discriminant analysis. Use when performing supervised multi-omics integration or identifying features that discriminate between groups.

## Version Compatibility

Reference examples tested with: mixOmics 6.26+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion("<pkg>")` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# mixOmics Multi-Omics Analysis

**"Integrate my multi-omics data with supervised analysis"** → Identify cross-omics feature signatures that discriminate between groups using sparse PLS and multi-block discriminant analysis.
- R: `mixOmics::block.splsda()` (DIABLO), `mixOmics::spls()` for pairwise integration

## Setup and Data Preparation

**Goal:** Load and align omics matrices with matching sample labels and phenotype information.

**Approach:** Read each omics layer and phenotype, then intersect to common samples.

```r
library(mixOmics)

# Load omics matrices (samples x features)
X_rna <- as.matrix(read.csv('rnaseq.csv', row.names = 1))
X_protein <- as.matrix(read.csv('proteomics.csv', row.names = 1))
Y <- factor(read.csv('phenotype.csv')$Condition)

# Ensure matching samples
common <- Reduce(intersect, list(rownames(X_rna), rownames(X_protein)))
X_rna <- X_rna[common, ]
X_protein <- X_protein[common, ]
Y <- Y[match(common, read.csv('phenotype.csv')$Sample)]
```

## Pairwise Integration: sPLS

**Goal:** Identify correlated features between two omics layers using sparse partial least squares.

**Approach:** Tune component count, fit sPLS with feature selection (keepX/keepY), and visualize cross-omics correlations.

```r
# Sparse Partial Least Squares for two datasets
# Finds correlated features between omics

# Tune number of components
tune_spls <- perf(spls(X_rna, X_protein, ncomp = 5), validation = 'Mfold', folds = 5)
plot(tune_spls)

# Run sPLS
spls_result <- spls(X_rna, X_protein, ncomp = 3, keepX = c(50, 50, 50), keepY = c(30, 30, 30))

# Visualize correlations
plotIndiv(spls_result, comp = c(1, 2), group = Y, legend = TRUE)
plotVar(spls_result, comp = c(1, 2), var.names = TRUE)

# Correlation circle
plotArrow(spls_result, group = Y)

# Heatmap of selected features
cim(spls_result, comp = 1)
```

## DIABLO: Multi-Block Discriminant Analysis

**Goal:** Find multi-omics feature signatures that discriminate between experimental conditions.

**Approach:** Define block correlation design, tune keepX per block via cross-validation, and fit the supervised DIABLO model.

```r
# DIABLO integrates multiple blocks with supervision
# Finds features discriminating between conditions

# Prepare block list
X_blocks <- list(RNA = X_rna, Protein = X_protein)

# Design matrix (correlation between blocks)
design <- matrix(0.1, ncol = 2, nrow = 2, dimnames = list(names(X_blocks), names(X_blocks)))
diag(design) <- 0

# Tune parameters
tune_diablo <- tune.block.splsda(X_blocks, Y, ncomp = 3,
                                  test.keepX = list(RNA = c(10, 25, 50),
                                                    Protein = c(10, 25, 50)),
                                  design = design, validation = 'Mfold', folds = 5,
                                  nrepeat = 10, cpus = 4)

# Optimal keepX values
optimal_keepX <- tune_diablo$choice.keepX

# Final model
diablo <- block.splsda(X_blocks, Y, ncomp = 3, keepX = optimal_keepX, design = design)

# Performance
perf_diablo <- perf(diablo, validation = 'Mfold', folds = 5, nrepeat = 10)
plot(perf_diablo)
```

## DIABLO Visualization

**Goal:** Visualize DIABLO results including sample separation, inter-block correlations, and feature networks.

**Approach:** Use mixOmics plotting functions for consensus plots, circos plots, and correlation networks.

```r
# Sample plots
plotIndiv(diablo, comp = c(1, 2), blocks = 'consensus', group = Y,
          legend = TRUE, title = 'DIABLO Consensus')

# Per-block sample plots
plotIndiv(diablo, comp = c(1, 2), blocks = 'RNA', group = Y)

# Variable plots
plotVar(diablo, comp = c(1, 2), blocks = c('RNA', 'Protein'),
        var.names = list(RNA = FALSE, Protein = FALSE))

# Circos plot showing inter-block correlations
circosPlot(diablo, cutoff = 0.7, line = TRUE)

# Network of correlated features
network(diablo, blocks = c('RNA', 'Protein'), cutoff = 0.6)

# Heatmap
cimDiablo(diablo, margin = c(8, 20))
```

## Extract Selected Features

**Goal:** Retrieve the discriminant features selected by DIABLO for each omics block and export for pathway analysis.

**Approach:** Use selectVar() to get selected variable names and plotLoadings() for contribution plots, then write to CSV.

```r
# Get selected variables per block
selected_rna <- selectVar(diablo, block = 'RNA', comp = 1)$RNA$name
selected_protein <- selectVar(diablo, block = 'Protein', comp = 1)$Protein$name

# Loadings
loadings_rna <- plotLoadings(diablo, block = 'RNA', comp = 1, contrib = 'max')
loadings_protein <- plotLoadings(diablo, block = 'Protein', comp = 1, contrib = 'max')

# Export for pathway analysis
write.csv(data.frame(gene = selected_rna), 'diablo_rna_features.csv', row.names = FALSE)
write.csv(data.frame(protein = selected_protein), 'diablo_protein_features.csv', row.names = FALSE)
```

## MINT: Multi-Study Integration

**Goal:** Integrate data from multiple studies while accounting for study-specific batch effects.

**Approach:** Fit MINT model with study indicator, then visualize global and per-study sample projections.

```r
# MINT for integrating multiple studies
# Accounts for study-specific effects

study <- factor(c(rep('Study1', 50), rep('Study2', 50)))

mint_result <- mint.splsda(X = X_rna, Y = Y, study = study, ncomp = 3, keepX = c(50, 50, 50))

# Visualize
plotIndiv(mint_result, study = 'global', group = Y, legend = TRUE)
plotIndiv(mint_result, study = 'all.partial', group = Y)

# Performance
perf_mint <- perf(mint_result, validation = 'Mfold', folds = 5)
```

## Unsupervised: sPCA and sPLS-DA Single Omics

**Goal:** Perform sparse dimensionality reduction or classification on a single omics dataset.

**Approach:** Apply sPCA for unsupervised exploration or sPLS-DA for supervised classification with feature selection.

```r
# Sparse PCA (single omics)
spca_result <- spca(X_rna, ncomp = 3, keepX = c(50, 50, 50))
plotIndiv(spca_result, group = Y)
plotVar(spca_result)

# sPLS-DA (single omics with supervision)
splsda_result <- splsda(X_rna, Y, ncomp = 3, keepX = c(50, 50, 50))
plotIndiv(splsda_result, group = Y, legend = TRUE)

# Background prediction
background <- background.predict(splsda_result, comp.predicted = 2, dist = 'max.dist')
plotIndiv(splsda_result, group = Y, background = background)
```

## Model Performance and Validation

**Goal:** Assess DIABLO classification performance via cross-validation error rates and AUC.

**Approach:** Run repeated M-fold cross-validation and compute AUC per block and component.

```r
# Cross-validation performance
perf_result <- perf(diablo, validation = 'Mfold', folds = 5, nrepeat = 50, cpus = 4)

# Error rates
plot(perf_result)
perf_result$error.rate

# AUC
auc_diablo <- auroc(diablo, roc.block = 'RNA', roc.comp = 1)
```

## Related Skills

- mofa-integration - Unsupervised multi-omics
- data-harmonization - Preprocess before integration
- differential-expression/de-results - Single-omics analysis
- pathway-analysis/go-enrichment - Interpret selected features
