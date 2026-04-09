# bio-metabolomics-normalization-qc

> Quality control and normalization for metabolomics data. Covers QC-based correction, batch effect removal, and data transformation methods. Use when correcting technical variation in metabolomics data before statistical analysis.

## Version Compatibility

Reference examples tested with: xcms 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolomics Normalization and QC

## Load and Inspect Data

**Goal:** Load the feature table and sample metadata, separating QC and biological samples for downstream processing.

**Approach:** Read CSV files, partition by sample type, and assess missing value prevalence.

**"Normalize my metabolomics data and correct for batch effects"** → Apply QC-based signal correction, handle missing values, transform intensities, and assess normalization quality via RSD and PCA.

```r
library(tidyverse)
library(pcaMethods)

# Load feature table (samples x features)
data <- read.csv('feature_table.csv', row.names = 1)
sample_info <- read.csv('sample_info.csv')

# Separate QC samples
qc_samples <- sample_info$sample_name[sample_info$sample_type == 'QC']
bio_samples <- sample_info$sample_name[sample_info$sample_type != 'QC']

data_qc <- data[qc_samples, ]
data_bio <- data[bio_samples, ]

# Missing value summary
missing_pct <- colMeans(is.na(data)) * 100
cat('Features with >50% missing:', sum(missing_pct > 50), '\n')
```

## QC-Based Normalization (QC-RSC)

**Goal:** Remove injection-order-dependent signal drift using QC sample trends.

**Approach:** Fit a LOESS curve to QC sample intensities over injection order, then correct all samples by dividing by the predicted drift and rescaling to the QC median.

```r
# QC-based Robust Spline Correction
library(statTarget)

qc_rsc_normalize <- function(data, sample_info) {
    # Fit LOESS to QC samples over injection order
    # Correct biological samples based on QC trend

    injection_order <- sample_info$injection_order
    is_qc <- sample_info$sample_type == 'QC'

    normalized <- data

    for (feature in colnames(data)) {
        qc_values <- data[is_qc, feature]
        qc_order <- injection_order[is_qc]

        # Fit LOESS
        fit <- loess(qc_values ~ qc_order, span = 0.75)

        # Predict for all samples
        predicted <- predict(fit, injection_order)

        # Correct: divide by trend, multiply by median
        median_val <- median(qc_values, na.rm = TRUE)
        normalized[, feature] <- data[, feature] / predicted * median_val
    }

    return(normalized)
}

data_corrected <- qc_rsc_normalize(data, sample_info)
```

## Total Ion Current (TIC) Normalization

**Goal:** Correct for differences in total signal intensity across samples.

**Approach:** Divide each sample by its total intensity sum, then rescale to the median total intensity.

```r
# Simple sum normalization
tic_normalize <- function(data) {
    row_sums <- rowSums(data, na.rm = TRUE)
    normalized <- data / row_sums * median(row_sums)
    return(normalized)
}

data_tic <- tic_normalize(data)
```

## Probabilistic Quotient Normalization (PQN)

**Goal:** Normalize samples while being robust to large fold changes in individual features.

**Approach:** Compute a reference spectrum from sample medians, calculate per-sample quotients, and divide each sample by its median quotient.

```r
pqn_normalize <- function(data) {
    # Calculate reference spectrum (median of all samples)
    reference <- apply(data, 2, median, na.rm = TRUE)

    # Calculate quotients
    quotients <- data / reference

    # Normalization factor = median of quotients per sample
    factors <- apply(quotients, 1, median, na.rm = TRUE)

    # Normalize
    normalized <- data / factors
    return(normalized)
}

data_pqn <- pqn_normalize(data)
```

## Batch Correction (ComBat)

**Goal:** Remove systematic technical variation between processing batches while preserving biological effects.

**Approach:** Apply ComBat empirical Bayes batch correction on log-transformed data, using a design matrix to protect the biological variable of interest.

```r
library(sva)

# ComBat for batch correction
batch <- sample_info$batch
mod <- model.matrix(~ sample_info$group)  # Keep biological effect

# Log transform first
data_log <- log2(data + 1)

# Apply ComBat
data_combat <- ComBat(dat = t(data_log), batch = batch, mod = mod)
data_combat <- t(data_combat)
```

## Missing Value Handling

**Goal:** Filter features with excessive missing values and impute remaining gaps for complete-case analysis.

**Approach:** Remove features missing in more than 20% of samples (optionally per group), then impute via KNN or minimum-value replacement for left-censored data.

```r
# Filter features with too many missing values
filter_missing <- function(data, max_missing = 0.2, by_group = TRUE, groups = NULL) {
    if (by_group && !is.null(groups)) {
        # Keep if present in >80% of samples in at least one group
        keep <- sapply(colnames(data), function(f) {
            any(sapply(unique(groups), function(g) {
                group_data <- data[groups == g, f]
                mean(is.na(group_data)) <= max_missing
            }))
        })
    } else {
        keep <- colMeans(is.na(data)) <= max_missing
    }

    return(data[, keep])
}

data_filtered <- filter_missing(data, max_missing = 0.2, by_group = TRUE,
                                  groups = sample_info$group)

# Impute remaining missing values
# KNN imputation
library(impute)
data_imputed <- impute.knn(as.matrix(data_filtered), k = 5)$data

# Or minimum value imputation (for left-censored data)
min_impute <- function(data) {
    data_imp <- data
    for (col in colnames(data)) {
        min_val <- min(data[, col], na.rm = TRUE) / 2
        data_imp[is.na(data_imp[, col]), col] <- min_val
    }
    return(data_imp)
}
```

## Data Transformation

**Goal:** Transform and scale feature intensities to approximate normality and equalize feature variance.

**Approach:** Apply log2 transformation followed by Pareto scaling (divide by sqrt of SD) or auto-scaling (z-score).

```r
# Log transformation
data_log <- log2(data + 1)

# Pareto scaling (mean-centered, divided by sqrt of SD)
pareto_scale <- function(data) {
    centered <- scale(data, center = TRUE, scale = FALSE)
    scaled <- centered / sqrt(apply(data, 2, sd, na.rm = TRUE))
    return(scaled)
}

data_pareto <- pareto_scale(data_log)

# Auto-scaling (z-score)
data_auto <- scale(data_log)
```

## QC Assessment

**Goal:** Evaluate normalization success by measuring QC sample reproducibility and visualizing sample clustering.

**Approach:** Calculate relative standard deviation (RSD) across QC samples (target <30%) and compare PCA before and after correction.

```r
# RSD in QC samples (should be <30%)
qc_rsd <- function(data, qc_samples) {
    qc_data <- data[qc_samples, ]
    rsd <- apply(qc_data, 2, function(x) sd(x, na.rm = TRUE) / mean(x, na.rm = TRUE) * 100)
    return(rsd)
}

rsd_before <- qc_rsd(data, qc_samples)
rsd_after <- qc_rsd(data_corrected, qc_samples)

cat('Features with RSD <30% before:', sum(rsd_before < 30, na.rm = TRUE), '\n')
cat('Features with RSD <30% after:', sum(rsd_after < 30, na.rm = TRUE), '\n')

# PCA to check correction
pca_before <- prcomp(t(na.omit(data)), scale. = TRUE)
pca_after <- prcomp(t(na.omit(data_corrected)), scale. = TRUE)

# Plot
par(mfrow = c(1, 2))
plot(pca_before$rotation[, 1:2], col = ifelse(rownames(pca_before$rotation) %in% qc_samples, 'red', 'blue'),
     main = 'Before correction', pch = 16)
plot(pca_after$rotation[, 1:2], col = ifelse(rownames(pca_after$rotation) %in% qc_samples, 'red', 'blue'),
     main = 'After correction', pch = 16)
```

## Quality Report

**Goal:** Generate a summary report of key QC metrics for the processed dataset.

**Approach:** Compute feature count, sample count, missing percentage, median RSD, and features passing RSD threshold.

```r
generate_qc_report <- function(data, sample_info) {
    qc_samples <- sample_info$sample_name[sample_info$sample_type == 'QC']

    report <- list(
        n_features = ncol(data),
        n_samples = nrow(data),
        n_qc = length(qc_samples),
        missing_pct = mean(is.na(data)) * 100,
        qc_rsd_median = median(qc_rsd(data, qc_samples), na.rm = TRUE),
        features_rsd_lt30 = sum(qc_rsd(data, qc_samples) < 30, na.rm = TRUE)
    )

    cat('=== QC Report ===\n')
    for (name in names(report)) {
        cat(sprintf('%s: %s\n', name, round(report[[name]], 2)))
    }

    return(report)
}

report <- generate_qc_report(data_corrected, sample_info)
```

## Related Skills

- xcms-preprocessing - Generate feature table
- statistical-analysis - Downstream analysis
- differential-expression/batch-correction - Similar concepts
