# bio-flow-cytometry-bead-normalization

> Bead-based normalization for CyTOF and high-parameter flow cytometry. Covers EQ bead normalization, signal drift correction, and batch normalization. Use when correcting instrument drift in CyTOF or harmonizing data across batches.

## Version Compatibility

Reference examples tested with: flowCore 2.14+, ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Bead Normalization

**"Normalize my CyTOF data using beads"** → Correct instrument signal drift over acquisition time using EQ calibration bead intensities for consistent measurements across runs.
- R: `CATALYST::normCytof()` for EQ bead normalization

## CyTOF EQ Bead Normalization

**Goal:** Identify EQ normalization bead events in CyTOF data for signal calibration.

**Approach:** Score events by mean scaled intensity in known bead channels (Ce140, Eu151, Eu153, Ho165, Lu175) and threshold at the 99th percentile.

```r
library(CATALYST)
library(flowCore)

# CyTOF data typically includes EQ normalization beads
# Fluidigm provides normalizer software, but can also do in R

# Load FCS with beads
ff <- read.FCS('cytof_with_beads.fcs')

# EQ beads contain known amounts of: Ce140, Eu151, Eu153, Ho165, Lu175
bead_channels <- c('Ce140Di', 'Eu151Di', 'Eu153Di', 'Ho165Di', 'Lu175Di')

# Identify bead events (high signal in bead channels)
bead_data <- exprs(ff)[, bead_channels]
bead_scores <- rowMeans(scale(bead_data))

# Beads typically have very high intensity
bead_threshold <- quantile(bead_scores, 0.99)
is_bead <- bead_scores > bead_threshold

cat('Identified', sum(is_bead), 'bead events (', round(mean(is_bead) * 100, 2), '%)\n')
```

## Calculate Normalization Factors

**Goal:** Compute per-channel normalization factors by comparing sample bead intensities to a reference.

**Approach:** Calculate median bead intensity per channel, then divide reference values by sample values to obtain correction factors.

```r
# For each acquisition, calculate median bead intensity
# Compare to reference to get normalization factor

calculate_norm_factors <- function(ff, bead_channels, bead_idx) {
    bead_intensities <- exprs(ff)[bead_idx, bead_channels]

    # Median intensity per channel
    medians <- apply(bead_intensities, 2, median)

    return(medians)
}

# Reference values (from first file or known standards)
reference_beads <- c(Ce140 = 500, Eu151 = 600, Eu153 = 550, Ho165 = 450, Lu175 = 400)

# Calculate factors
sample_beads <- calculate_norm_factors(ff, bead_channels, is_bead)
norm_factors <- reference_beads / sample_beads

cat('Normalization factors:\n')
print(round(norm_factors, 3))
```

## Apply Normalization

**Goal:** Correct marker intensities using bead-derived normalization factors and remove bead events.

**Approach:** Multiply marker channels by the geometric mean of bead factors, then filter out bead events from the flowFrame.

```r
# Apply normalization to all marker channels (not scatter)
marker_channels <- setdiff(colnames(ff), c('Time', 'Event_length', bead_channels))

normalize_cytof <- function(ff, norm_factors, channels) {
    # Get expression matrix
    expr <- exprs(ff)

    # Apply geometric mean of bead factors to all channels
    global_factor <- exp(mean(log(norm_factors)))

    # Or apply per-channel if you have channel-specific factors
    expr[, channels] <- expr[, channels] * global_factor

    exprs(ff) <- expr
    return(ff)
}

ff_normalized <- normalize_cytof(ff, norm_factors, marker_channels)

# Remove bead events
ff_clean <- ff_normalized[!is_bead, ]
cat('Final cell count:', nrow(ff_clean), '\n')
```

## Time-Based Drift Correction

**Goal:** Remove signal drift that accumulates during long CyTOF acquisitions.

**Approach:** Bin bead events by acquisition time, fit LOESS to per-bin median intensities, and scale all events to a reference level.

```r
# Correct for signal drift over acquisition time

correct_drift <- function(ff, time_channel = 'Time') {
    expr <- exprs(ff)
    time <- expr[, time_channel]

    # Bin by time
    n_bins <- 20
    time_bins <- cut(time, breaks = n_bins, labels = FALSE)

    # For each marker, fit LOESS to bead signal over time
    corrected <- expr

    marker_cols <- setdiff(colnames(expr), c(time_channel, 'Event_length'))

    for (marker in marker_cols) {
        bin_medians <- tapply(expr[is_bead, marker], time_bins[is_bead], median)

        if (length(unique(time_bins[is_bead])) > 3) {
            # Fit smooth curve to drift
            drift_data <- data.frame(
                time = as.numeric(names(bin_medians)),
                intensity = as.numeric(bin_medians)
            )

            loess_fit <- loess(intensity ~ time, data = drift_data, span = 0.5)

            # Predict correction factor for all events
            correction <- predict(loess_fit, newdata = data.frame(time = time_bins))
            reference <- median(drift_data$intensity)

            corrected[, marker] <- expr[, marker] * (reference / correction)
        }
    }

    exprs(ff) <- corrected
    return(ff)
}

ff_drift_corrected <- correct_drift(ff)
```

## Batch Normalization with CytoNorm

**Goal:** Harmonize marker distributions across batches using shared reference samples.

**Approach:** Train spline-based CytoNorm models on reference samples run in all batches, then apply the learned transformations to normalize new samples.

```r
# CytoNorm for cross-batch normalization using reference samples

library(CytoNorm)

# Requires: training samples run on all batches (e.g., same PBMC reference)
# Creates spline-based transformation

# Prepare training data
train_files <- list.files('batch1_reference/', pattern = '\\.fcs$', full.names = TRUE)
train_data <- lapply(train_files, read.FCS)

# Define model
model <- CytoNorm.train(
    files = train_files,
    labels = rep('Reference', length(train_files)),
    channels = marker_channels,
    transformList = NULL,  # If already transformed
    nQ = 100,  # Number of quantiles
    seed = 42
)

# Apply to new batch
test_files <- list.files('batch2/', pattern = '\\.fcs$', full.names = TRUE)
normalized_files <- CytoNorm.normalize(
    model = model,
    files = test_files,
    labels = rep('Test', length(test_files)),
    outputDir = 'batch2_normalized/'
)
```

## Quantile Normalization

**Goal:** Align marker distributions across samples by mapping to a common reference distribution.

**Approach:** Rank-order values per channel per sample and replace with interpolated reference quantiles computed from all samples.

```r
# Simple quantile normalization across samples

quantile_normalize <- function(fs, channels) {
    # Extract expression matrices
    expr_list <- lapply(fs, function(ff) exprs(ff)[, channels])

    # Get reference distribution (mean of all samples)
    all_values <- do.call(rbind, expr_list)
    reference_quantiles <- apply(all_values, 2, function(x) sort(x))
    reference <- colMeans(reference_quantiles)

    # Normalize each sample
    normalized_fs <- fs
    for (i in 1:length(fs)) {
        expr <- exprs(fs[[i]])
        for (ch in channels) {
            ranks <- rank(expr[, ch], ties.method = 'average')
            normalized_values <- approx(1:length(reference), sort(reference),
                                        xout = ranks)$y
            expr[, ch] <- normalized_values
        }
        exprs(normalized_fs[[i]]) <- expr
    }

    return(normalized_fs)
}
```

## CATALYST-Based Normalization

**Goal:** Normalize CyTOF data using CATALYST's built-in bead handling and time-drift correction.

**Approach:** Use prepData with by_time=TRUE to automatically correct time-dependent drift during SCE construction.

```r
library(CATALYST)

# CATALYST provides bead-based normalization for CyTOF

# Load data with prepData (handles bead removal)
sce <- prepData(fs, panel, md,
                transform = TRUE,
                cofactor = 5,
                by_time = TRUE)  # Correct time-dependent drift

# Or manual bead gating in CATALYST
# sce <- prepData(fs, panel, md, FACS = FALSE)
# sce <- filterSCE(sce, !sce$is_bead)
```

## Visualization

**Goal:** Visualize bead signal drift and assess normalization effects.

**Approach:** Plot bead channel intensity over acquisition time with LOESS trend, and compare marker distributions before and after normalization.

```r
library(ggplot2)

# Plot bead signal over time
bead_plot_data <- data.frame(
    Time = exprs(ff)[is_bead, 'Time'],
    Ce140 = exprs(ff)[is_bead, 'Ce140Di'],
    Eu151 = exprs(ff)[is_bead, 'Eu151Di']
)

ggplot(bead_plot_data, aes(x = Time, y = Ce140)) +
    geom_point(alpha = 0.1, size = 0.5) +
    geom_smooth(method = 'loess', color = 'red') +
    theme_bw() +
    labs(title = 'Bead Signal Over Time (Ce140)', x = 'Time', y = 'Intensity')
ggsave('bead_drift.png', width = 10, height = 4)

# Before/after normalization
compare_df <- data.frame(
    Value = c(exprs(ff)[, 'CD45'], exprs(ff_normalized)[, 'CD45']),
    Status = rep(c('Before', 'After'), each = nrow(ff))
)

ggplot(compare_df, aes(x = Value, fill = Status)) +
    geom_histogram(bins = 100, alpha = 0.5, position = 'identity') +
    theme_bw() +
    labs(title = 'Normalization Effect on CD45')
```

## Export Normalized Data

**Goal:** Save normalized and bead-free data for downstream analysis.

**Approach:** Write the cleaned flowFrame to a new FCS file using write.FCS.

```r
# Save normalized FCS files
write.FCS(ff_clean, 'normalized_sample.fcs')

# For CATALYST object
# saveRDS(sce, 'normalized_sce.rds')
```

## Related Skills

Workflow order: cytometry-qc → doublet-detection → bead-normalization → clustering

- cytometry-qc - Run first: identify drift and quality issues
- doublet-detection - Run before: remove doublets prior to normalization
- compensation-transformation - Initial data preprocessing
- clustering-phenotyping - Analysis after normalization
- differential-analysis - Batch-aware statistical testing
