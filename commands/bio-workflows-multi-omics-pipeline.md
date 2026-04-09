# bio-workflows-multi-omics-pipeline

> End-to-end multi-omics integration workflow. Orchestrates data harmonization, MOFA/mixOmics integration, factor interpretation, and downstream analysis across transcriptomics, proteomics, metabolomics, and other modalities. Use when integrating multiple omics datasets.

**Available tools:** Read, Bash

# Multi-omics Integration Pipeline

## Pipeline Overview

```
RNA-seq Data ─────┐
                  │
Proteomics Data ──┼──> Data Harmonization ──> Integration ──> Factors/Components
                  │                                                    │
Metabolomics ─────┘                                                    ▼
                        ┌─────────────────────────────────────────────────────┐
                        │           multi-omics-pipeline                      │
                        ├─────────────────────────────────────────────────────┤
                        │  1. Data Preprocessing per Modality                 │
                        │  2. Sample Harmonization (matching samples)         │
                        │  3. Feature Selection/Filtering                     │
                        │  4. Integration (MOFA2 / mixOmics / SNF)            │
                        │  5. Factor/Component Interpretation                 │
                        │  6. Downstream Analysis                             │
                        └─────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                              Integrated Factors + Biomarker Signatures
```

## Complete MOFA2 Workflow

```r
library(MOFA2)
library(MOFAdata)
library(ggplot2)
library(tidyverse)

# === 1. LOAD AND HARMONIZE DATA ===
# RNA-seq data (samples x genes)
rna <- read.csv('rnaseq_normalized.csv', row.names = 1)
cat('RNA:', nrow(rna), 'samples,', ncol(rna), 'genes\n')

# Proteomics data (samples x proteins)
protein <- read.csv('proteomics_normalized.csv', row.names = 1)
cat('Protein:', nrow(protein), 'samples,', ncol(protein), 'proteins\n')

# Metabolomics data (samples x metabolites)
metab <- read.csv('metabolomics_normalized.csv', row.names = 1)
cat('Metabolites:', nrow(metab), 'samples,', ncol(metab), 'metabolites\n')

# Find common samples
common_samples <- Reduce(intersect, list(rownames(rna), rownames(protein), rownames(metab)))
cat('Common samples:', length(common_samples), '\n')

# Subset to common samples
rna <- rna[common_samples, ]
protein <- protein[common_samples, ]
metab <- metab[common_samples, ]

# === 2. FEATURE SELECTION ===
# Select most variable features per modality
select_variable <- function(data, n = 2000) {
    vars <- apply(data, 2, var, na.rm = TRUE)
    top_features <- names(sort(vars, decreasing = TRUE))[1:min(n, ncol(data))]
    data[, top_features]
}

rna_var <- select_variable(rna, n = 2000)
protein_var <- select_variable(protein, n = 1000)
metab_var <- select_variable(metab, n = 500)

# === 3. CREATE MOFA OBJECT ===
# Prepare data as list of matrices (features x samples)
data_list <- list(
    RNA = t(as.matrix(rna_var)),
    Protein = t(as.matrix(protein_var)),
    Metabolome = t(as.matrix(metab_var))
)

# Create MOFA object
mofa <- create_mofa(data_list)

# Add sample metadata
sample_metadata <- read.csv('sample_metadata.csv')
rownames(sample_metadata) <- sample_metadata$sample_id
samples_metadata(mofa) <- sample_metadata[common_samples, ]

# === 4. CONFIGURE AND TRAIN MODEL ===
# Data options
data_opts <- get_default_data_options(mofa)
data_opts$scale_views <- TRUE  # Scale each view

# Model options
model_opts <- get_default_model_options(mofa)
model_opts$num_factors <- 15  # Number of factors to learn

# Training options
train_opts <- get_default_training_options(mofa)
train_opts$maxiter <- 1000
train_opts$convergence_mode <- 'slow'
train_opts$seed <- 42

# Prepare and train
mofa <- prepare_mofa(mofa, data_options = data_opts,
                      model_options = model_opts,
                      training_options = train_opts)

cat('Training MOFA model...\n')
mofa <- run_mofa(mofa, outfile = 'mofa_model.hdf5', use_basilisk = TRUE)

# === 5. ANALYZE FACTORS ===
# Variance explained per factor per view
plot_variance_explained(mofa, max_r2 = 15)
ggsave('variance_explained.png', width = 10, height = 6)

# Factor values
factor_values <- get_factors(mofa)[[1]]

# Correlate factors with phenotypes
plot_factor_cor(mofa, color_by = 'condition')
ggsave('factor_phenotype_correlation.png', width = 8, height = 6)

# Factor plots
plot_factor(mofa, factors = 1:4, color_by = 'condition', dot_size = 3)
ggsave('factor_scatter.png', width = 12, height = 10)

# === 6. INTERPRET FACTORS ===
# Get top weights per factor per view
for (f in 1:5) {
    cat('\nFactor', f, ':\n')
    weights <- get_weights(mofa, factors = f, as.data.frame = TRUE)

    for (view in unique(weights$view)) {
        view_weights <- weights[weights$view == view, ]
        view_weights <- view_weights[order(abs(view_weights$value), decreasing = TRUE), ]
        cat('  ', view, ':', paste(head(view_weights$feature, 5), collapse = ', '), '\n')
    }
}

# Heatmap of top features per factor
plot_top_weights(mofa, view = 'RNA', factors = 1:5, nfeatures = 10)
ggsave('top_weights_rna.png', width = 10, height = 8)

# === 7. ENRICHMENT ANALYSIS ===
library(clusterProfiler)
library(org.Hs.eg.db)

# Get RNA weights for factor 1
rna_weights <- get_weights(mofa, views = 'RNA', factors = 1)[[1]][, 1]
top_genes <- names(sort(abs(rna_weights), decreasing = TRUE))[1:200]

# GO enrichment
ego <- enrichGO(gene = top_genes,
                OrgDb = org.Hs.eg.db,
                keyType = 'SYMBOL',
                ont = 'BP',
                pvalueCutoff = 0.05)

dotplot(ego, showCategory = 15)
ggsave('factor1_enrichment.png', width = 8, height = 10)

# === 8. DOWNSTREAM: SURVIVAL ANALYSIS ===
library(survival)
library(survminer)

# Add factor values to metadata
surv_data <- data.frame(
    sample = rownames(factor_values),
    factor1 = factor_values[, 1],
    time = sample_metadata[rownames(factor_values), 'survival_time'],
    status = sample_metadata[rownames(factor_values), 'survival_status']
)

# Median split
surv_data$factor1_group <- ifelse(surv_data$factor1 > median(surv_data$factor1), 'High', 'Low')

# Kaplan-Meier
fit <- survfit(Surv(time, status) ~ factor1_group, data = surv_data)
ggsurvplot(fit, data = surv_data, pval = TRUE, risk.table = TRUE)
ggsave('survival_factor1.png', width = 8, height = 8)

# === 9. EXPORT RESULTS ===
# Factor values
write.csv(factor_values, 'mofa_factor_values.csv')

# Weights
all_weights <- get_weights(mofa, as.data.frame = TRUE)
write.csv(all_weights, 'mofa_weights.csv', row.names = FALSE)

cat('\nMOFA analysis complete!\n')
```

## mixOmics DIABLO Workflow

```r
library(mixOmics)

# === 1. PREPARE DATA ===
# Same preprocessing as above
X <- list(
    RNA = as.matrix(rna_var),
    Protein = as.matrix(protein_var),
    Metabolome = as.matrix(metab_var)
)

# Outcome variable
Y <- factor(sample_metadata[common_samples, 'condition'])

# === 2. DESIGN MATRIX ===
# Define connections between blocks
design <- matrix(0.1, ncol = length(X), nrow = length(X),
                 dimnames = list(names(X), names(X)))
diag(design) <- 0

# === 3. TUNE MODEL ===
# Tune number of components
perf.diablo <- perf(block.splsda(X, Y, ncomp = 5, design = design),
                    validation = 'Mfold', folds = 5, nrepeat = 10)

ncomp <- perf.diablo$choice.ncomp$WeightedVote['Overall.BER', 'max.dist']
cat('Optimal components:', ncomp, '\n')

# Tune number of variables per component
test.keepX <- list(
    RNA = c(10, 25, 50, 100),
    Protein = c(5, 10, 25, 50),
    Metabolome = c(5, 10, 25)
)

tune.diablo <- tune.block.splsda(X, Y, ncomp = ncomp, test.keepX = test.keepX,
                                  design = design, validation = 'Mfold', folds = 5)

optimal.keepX <- tune.diablo$choice.keepX

# === 4. FINAL MODEL ===
diablo.model <- block.splsda(X, Y, ncomp = ncomp,
                              keepX = optimal.keepX, design = design)

# === 5. VISUALIZATION ===
# Sample plot
plotIndiv(diablo.model, ind.names = FALSE, legend = TRUE, title = 'DIABLO Sample Plot')

# Variable plot
plotVar(diablo.model, var.names = FALSE, style = 'graphics', legend = TRUE)

# Circos plot
circosPlot(diablo.model, cutoff = 0.7, line = TRUE,
           color.blocks = c('darkorchid', 'brown1', 'lightgreen'))

# Heatmap
cimDiablo(diablo.model, color.blocks = c('darkorchid', 'brown1', 'lightgreen'),
          margins = c(10, 5))

# === 6. PERFORMANCE ===
perf.final <- perf(diablo.model, validation = 'Mfold', folds = 5, nrepeat = 10)
cat('Classification error rate:', perf.final$WeightedVote.error.rate, '\n')

# ROC curves
auc.diablo <- auroc(diablo.model, roc.block = 'RNA', roc.comp = 1)
```

## Similarity Network Fusion (SNF)

```r
library(SNFtool)

# === 1. CREATE SIMILARITY MATRICES ===
# Distance matrices per modality
dist_rna <- dist2(as.matrix(rna_var), as.matrix(rna_var))
dist_protein <- dist2(as.matrix(protein_var), as.matrix(protein_var))
dist_metab <- dist2(as.matrix(metab_var), as.matrix(metab_var))

# Affinity matrices
K <- 20  # Number of neighbors
alpha <- 0.5  # Hyperparameter

aff_rna <- affinityMatrix(dist_rna, K = K, sigma = alpha)
aff_protein <- affinityMatrix(dist_protein, K = K, sigma = alpha)
aff_metab <- affinityMatrix(dist_metab, K = K, sigma = alpha)

# === 2. FUSE NETWORKS ===
W <- SNF(list(aff_rna, aff_protein, aff_metab), K = K, t = 20)

# === 3. CLUSTER ON FUSED NETWORK ===
clusters <- spectralClustering(W, K = 3)  # K = number of clusters
cat('Cluster distribution:', table(clusters), '\n')

# === 4. VISUALIZATION ===
# Plot fused network
displayClustersWithHeatmap(W, clusters)
```

## QC Checkpoints

| Stage | Check | Action if Failed |
|-------|-------|------------------|
| Sample matching | >80% samples shared | Check sample IDs |
| Missing values | <20% per modality | Impute or remove |
| Feature variance | Features vary | Filter low variance |
| Model convergence | ELBO plateau | Increase iterations |
| Factor variance | >5% per factor | Keep fewer factors |

## Workflow Variants

### With Missing Samples
```r
# MOFA2 handles missing views gracefully
# Use create_mofa_from_df for unbalanced data
data_long <- rbind(
    data.frame(sample = rownames(rna), view = 'RNA',
               feature = colnames(rna), value = unlist(rna)),
    data.frame(sample = rownames(protein), view = 'Protein',
               feature = colnames(protein), value = unlist(protein))
)
mofa <- create_mofa_from_df(data_long)
```

### Single-cell Multi-omics
```r
# MOFA+ for single-cell
library(MOFA2)
mofa <- create_mofa_from_Seurat(seurat_obj, groups = 'cell_type',
                                 assays = c('RNA', 'ATAC'))
```

## Related Skills

- multi-omics-integration/mofa-integration - MOFA2 details
- multi-omics-integration/mixomics-analysis - mixOmics methods
- multi-omics-integration/similarity-network - SNF method
- multi-omics-integration/data-harmonization - Preprocessing
- pathway-analysis/go-enrichment - Factor interpretation
- differential-expression/batch-correction - Batch effects
