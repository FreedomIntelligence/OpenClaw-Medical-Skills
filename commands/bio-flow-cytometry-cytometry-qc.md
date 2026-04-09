# bio-flow-cytometry-cytometry-qc

> Comprehensive quality control for flow cytometry and CyTOF data. Covers flow rate stability, signal drift, margin events, dead cell exclusion, and batch QC. Use when assessing acquisition quality or identifying problematic samples before analysis.

## Version Compatibility

Reference examples tested with: flowCore 2.14+, ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Cytometry QC

**"Run quality control on my flow cytometry data"** → Assess acquisition quality by checking flow rate stability, signal drift, margin events, and dead cell frequencies to identify problematic samples.
- R: `flowAI::flow_auto_qc()` for automated anomaly detection

## Automated QC with flowAI

```r
library(flowAI)
library(flowCore)

# Load FCS file
ff <- read.FCS('sample.fcs')

# Run automated QC
# Checks: flow rate, signal stability, dynamic range
qc_result <- flow_auto_qc(
    ff,
    folder_results = 'qc_output/',
    fcs_QC = TRUE,       # Export QC'd FCS
    html_report = TRUE,  # Generate HTML report
    mini_report = TRUE   # Also make summary
)

# Get cleaned data
ff_clean <- qc_result$fcs

# QC metrics
cat('Original events:', nrow(ff), '\n')
cat('After QC:', nrow(ff_clean), '\n')
cat('Removed:', nrow(ff) - nrow(ff_clean), '(',
    round((1 - nrow(ff_clean)/nrow(ff)) * 100, 1), '%)\n')
```

## Flow Rate Stability

```r
# Check for acquisition issues via flow rate
check_flow_rate <- function(ff, time_channel = 'Time') {
    expr <- exprs(ff)
    time <- expr[, time_channel]

    # Bin by time
    n_bins <- 50
    bins <- cut(time, breaks = n_bins, labels = FALSE)

    # Events per bin (flow rate proxy)
    events_per_bin <- table(bins)
    flow_rate <- as.numeric(events_per_bin)

    # Calculate metrics
    cv <- sd(flow_rate) / mean(flow_rate) * 100

    # Detect anomalies (>2 SD from mean)
    z_scores <- abs(scale(flow_rate))
    anomalies <- which(z_scores > 2)

    list(
        mean_rate = mean(flow_rate),
        cv_percent = cv,
        anomaly_bins = anomalies,
        stable = cv < 20 && length(anomalies) < 3
    )
}

flow_qc <- check_flow_rate(ff)
cat('Flow rate CV:', round(flow_qc$cv_percent, 1), '%\n')
cat('Stable:', flow_qc$stable, '\n')
```

## Signal Drift Detection

```r
# Detect signal drift over acquisition time
detect_signal_drift <- function(ff, channels, time_channel = 'Time') {
    expr <- exprs(ff)
    time <- expr[, time_channel]

    n_bins <- 20
    bins <- cut(time, breaks = n_bins, labels = FALSE)

    drift_results <- lapply(channels, function(ch) {
        bin_medians <- tapply(expr[, ch], bins, median, na.rm = TRUE)

        # Linear trend
        trend <- lm(bin_medians ~ seq_along(bin_medians))
        slope <- coef(trend)[2]
        r_squared <- summary(trend)$r.squared

        # Percent change over acquisition
        pct_change <- (tail(bin_medians, 1) - head(bin_medians, 1)) / head(bin_medians, 1) * 100

        list(
            channel = ch,
            slope = slope,
            r_squared = r_squared,
            percent_change = pct_change,
            drift_detected = abs(pct_change) > 10 && r_squared > 0.5
        )
    })

    names(drift_results) <- channels
    drift_results
}

marker_channels <- c('CD45', 'CD3', 'CD4', 'CD8')
drift <- detect_signal_drift(ff, marker_channels)
for (ch in names(drift)) {
    if (drift[[ch]]$drift_detected) {
        cat('DRIFT DETECTED:', ch, '(', round(drift[[ch]]$percent_change, 1), '%)\n')
    }
}
```

## Margin Events Removal

```r
# Remove events at detector saturation limits
remove_margin_events <- function(ff, channels = NULL) {
    expr <- exprs(ff)

    if (is.null(channels)) {
        channels <- colnames(expr)
    }

    # Get channel ranges from FCS parameters
    params <- parameters(ff)

    margin_mask <- rep(FALSE, nrow(expr))

    for (ch in channels) {
        if (ch %in% colnames(expr)) {
            # Get max range from parameters
            idx <- match(ch, params@data$name)
            if (!is.na(idx)) {
                max_val <- params@data$range[idx]
                # Events at max or min are margin events
                margin_mask <- margin_mask | (expr[, ch] >= max_val * 0.99) | (expr[, ch] <= 0)
            }
        }
    }

    cat('Margin events:', sum(margin_mask), '(', round(mean(margin_mask) * 100, 2), '%)\n')
    ff[!margin_mask, ]
}

ff_no_margin <- remove_margin_events(ff, c('FSC-A', 'SSC-A'))
```

## Dead Cell Exclusion

```r
# Exclude dead cells using viability marker
exclude_dead_cells <- function(ff, viability_channel, threshold = NULL) {
    expr <- exprs(ff)
    viability <- expr[, viability_channel]

    if (is.null(threshold)) {
        # Auto-threshold using bimodal distribution
        # Dead cells have higher viability dye uptake
        threshold <- quantile(viability, 0.9)
    }

    live_mask <- viability < threshold

    cat('Total events:', length(live_mask), '\n')
    cat('Live cells:', sum(live_mask), '(', round(mean(live_mask) * 100, 1), '%)\n')
    cat('Dead cells:', sum(!live_mask), '(', round(mean(!live_mask) * 100, 1), '%)\n')

    ff[live_mask, ]
}

# Example with zombie dye
ff_live <- exclude_dead_cells(ff, 'Zombie-Aqua')
```

## CyTOF-Specific QC

```r
# CyTOF-specific quality metrics
cytof_qc <- function(ff) {
    expr <- exprs(ff)

    # Event length check (cell size proxy)
    if ('Event_length' %in% colnames(expr)) {
        event_length <- expr[, 'Event_length']

        # Typical single cells: 15-45
        good_length <- event_length >= 15 & event_length <= 45
        cat('Event length filter:', sum(good_length), '/', length(good_length),
            '(', round(mean(good_length) * 100, 1), '%)\n')
    }

    # DNA intercalator check (nucleated cells)
    dna_channels <- grep('(Ir191|Ir193|DNA)', colnames(expr), value = TRUE)
    if (length(dna_channels) > 0) {
        dna_signal <- rowMeans(expr[, dna_channels, drop = FALSE])

        # Cells should have DNA signal
        has_dna <- dna_signal > quantile(dna_signal, 0.1)
        cat('DNA+ events:', sum(has_dna), '(', round(mean(has_dna) * 100, 1), '%)\n')
    }

    # Gaussian parameters (if present)
    gauss_channels <- grep('(Center|Offset|Width|Residual)', colnames(expr), value = TRUE)
    if (length(gauss_channels) > 0) {
        cat('Gaussian parameters available for additional QC\n')
    }
}

cytof_qc(ff)
```

## Batch QC Summary

**Goal:** Generate a per-sample QC summary table for an entire experiment batch, flagging outlier samples that may need exclusion.

**Approach:** Loop through FCS files, compute event counts, flow rate CV, and median signal intensity for each, then flag samples with abnormal event counts or unstable flow rates.

```r
library(dplyr)

# Generate QC summary for batch of files
batch_qc_summary <- function(fcs_files) {
    results <- lapply(fcs_files, function(f) {
        ff <- read.FCS(f)

        # Basic metrics
        n_events <- nrow(ff)

        # Flow rate CV
        flow_qc <- check_flow_rate(ff)

        # Signal range check
        expr <- exprs(ff)
        signal_channels <- grep('(FSC|SSC)', colnames(expr), value = TRUE, invert = TRUE)
        median_signals <- apply(expr[, signal_channels, drop = FALSE], 2, median)

        data.frame(
            file = basename(f),
            events = n_events,
            flow_rate_cv = flow_qc$cv_percent,
            flow_stable = flow_qc$stable,
            median_signal = mean(median_signals, na.rm = TRUE)
        )
    })

    summary_df <- do.call(rbind, results)

    # Flag outliers
    summary_df$outlier <- with(summary_df,
        events < median(events) * 0.5 |
        events > median(events) * 2 |
        flow_rate_cv > 30
    )

    summary_df
}

# Run batch QC
fcs_files <- list.files('data/', pattern = '\\.fcs$', full.names = TRUE)
qc_summary <- batch_qc_summary(fcs_files)
print(qc_summary)

# Flag problematic samples
cat('\nSamples with QC issues:\n')
print(qc_summary[qc_summary$outlier, ])
```

## Visualization

```r
library(ggplot2)

# Flow rate plot
plot_flow_rate <- function(ff, time_channel = 'Time') {
    expr <- exprs(ff)
    time <- expr[, time_channel]

    n_bins <- 100
    bins <- cut(time, breaks = n_bins, labels = FALSE)
    events_per_bin <- table(bins)

    plot_data <- data.frame(
        bin = as.numeric(names(events_per_bin)),
        events = as.numeric(events_per_bin)
    )

    ggplot(plot_data, aes(x = bin, y = events)) +
        geom_line() +
        geom_smooth(method = 'loess', color = 'red', se = FALSE) +
        theme_bw() +
        labs(title = 'Flow Rate Over Acquisition', x = 'Time Bin', y = 'Events per Bin')
}

# Signal stability plot
plot_signal_stability <- function(ff, channel, time_channel = 'Time') {
    expr <- exprs(ff)

    n_bins <- 50
    bins <- cut(expr[, time_channel], breaks = n_bins, labels = FALSE)
    bin_stats <- tapply(expr[, channel], bins, function(x) {
        c(median = median(x), q25 = quantile(x, 0.25), q75 = quantile(x, 0.75))
    })

    plot_data <- data.frame(
        bin = seq_along(bin_stats),
        median = sapply(bin_stats, '[', 'median'),
        q25 = sapply(bin_stats, '[', 'q25'),
        q75 = sapply(bin_stats, '[', 'q75')
    )

    ggplot(plot_data, aes(x = bin)) +
        geom_ribbon(aes(ymin = q25, ymax = q75), alpha = 0.3) +
        geom_line(aes(y = median), color = 'blue') +
        theme_bw() +
        labs(title = paste('Signal Stability:', channel), x = 'Time Bin', y = 'Intensity')
}

# Generate QC plots
p1 <- plot_flow_rate(ff)
ggsave('qc_flow_rate.png', p1, width = 10, height = 4)

p2 <- plot_signal_stability(ff, 'CD45')
ggsave('qc_signal_stability.png', p2, width = 10, height = 4)
```

## QC Report Generation

```r
# Generate comprehensive QC report
generate_qc_report <- function(ff, output_file = 'qc_report.txt') {
    sink(output_file)

    cat('=== FLOW CYTOMETRY QC REPORT ===\n\n')
    cat('File:', description(ff)$`$FIL`, '\n')
    cat('Date:', description(ff)$`$DATE`, '\n')
    cat('Total events:', nrow(ff), '\n\n')

    cat('--- Flow Rate ---\n')
    flow_qc <- check_flow_rate(ff)
    cat('CV:', round(flow_qc$cv_percent, 1), '%\n')
    cat('Status:', ifelse(flow_qc$stable, 'PASS', 'FAIL'), '\n\n')

    cat('--- Signal Channels ---\n')
    expr <- exprs(ff)
    for (ch in colnames(expr)[1:min(10, ncol(expr))]) {
        cat(ch, ': median =', round(median(expr[, ch]), 1), '\n')
    }

    sink()
    cat('Report saved to', output_file, '\n')
}

generate_qc_report(ff)
```

## Related Skills

Workflow order: cytometry-qc → doublet-detection → bead-normalization → clustering

- compensation-transformation - Data preprocessing before QC
- doublet-detection - Run after QC: remove doublet events
- bead-normalization - Run after doublet removal: correct signal drift
- clustering-phenotyping - Analysis after all preprocessing
