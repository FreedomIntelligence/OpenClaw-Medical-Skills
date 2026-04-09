# bio-flow-cytometry-doublet-detection

> Detect and remove doublets from flow and mass cytometry data. Covers FSC/SSC gating and computational doublet detection methods. Use when filtering out cell aggregates before clustering or quantitative analysis.

## Version Compatibility

Reference examples tested with: flowCore 2.14+, ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Doublet Detection

**"Remove doublets from my flow cytometry data"** → Detect and filter out cell aggregates using FSC-A/FSC-H gating or computational methods before clustering or quantitative analysis.
- R: `flowCore` rectangular gates on FSC-A vs FSC-H

## FSC-A vs FSC-H Gating (Standard Method)

```r
library(flowCore)
library(ggcyto)

# Load data
fs <- read.flowSet(list.files('data/', pattern = '\\.fcs$', full.names = TRUE))

# FSC-A vs FSC-H for doublet discrimination
# Singlets fall on diagonal, doublets have higher FSC-A for given FSC-H

# Manual rectangular gate
singlet_gate <- rectangleGate(
    filterId = 'singlets',
    'FSC-A' = c(50000, 250000),
    'FSC-H' = c(50000, 250000)
)

# Or use polygon gate for diagonal
singlet_polygon <- polygonGate(
    filterId = 'singlets',
    .gate = data.frame(
        'FSC-A' = c(50000, 250000, 250000, 50000),
        'FSC-H' = c(40000, 200000, 260000, 60000)
    )
)

# Apply gate
singlets <- Subset(fs, singlet_gate)

# Visualize
autoplot(fs[[1]], 'FSC-A', 'FSC-H') + geom_gate(singlet_gate)
```

## Automated Singlet Gating with flowDensity

```r
library(flowDensity)

# Automatic singlet gate
singlet_result <- flowDensity(
    fs[[1]],
    channels = c('FSC-A', 'FSC-H'),
    position = c(TRUE, TRUE),
    gates = c(NA, NA)
)

# Get gated population
singlets <- getflowFrame(singlet_result)

# Percentage singlets
pct_singlets <- nrow(singlets) / nrow(fs[[1]]) * 100
cat('Singlets:', round(pct_singlets, 1), '%\n')
```

## flowAI Quality Control

```r
library(flowAI)

# flowAI performs comprehensive QC including:
# - Flow rate anomaly detection
# - Signal acquisition anomaly detection
# - Dynamic range anomaly detection

# Run flowAI
fs_qc <- flow_auto_qc(
    fs,
    folder_results = 'flowAI_results',
    fcs_QC = TRUE,
    fcs_highQ = TRUE
)

# Results include singlet detection based on flow rate stability
```

## FSC-A/FSC-W Method (Width Parameter)

```r
# Some instruments provide FSC-W (width) instead of FSC-H
# FSC-A = FSC-H × FSC-W
# Doublets have higher width

if ('FSC-W' %in% colnames(fs[[1]])) {
    singlet_gate_w <- rectangleGate(
        filterId = 'singlets',
        'FSC-A' = c(50000, 250000),
        'FSC-W' = c(50000, 100000)  # Lower width = singlets
    )

    singlets <- Subset(fs, singlet_gate_w)
}
```

## Ratio-Based Doublet Detection

```r
# Calculate FSC-A/FSC-H ratio
# Singlets have ratio close to constant (based on pulse geometry)
# Doublets have elevated ratio

calculate_fsc_ratio <- function(ff) {
    fsc_a <- exprs(ff)[, 'FSC-A']
    fsc_h <- exprs(ff)[, 'FSC-H']

    ratio <- fsc_a / (fsc_h + 1)  # Add small value to avoid division by zero
    return(ratio)
}

# Add ratio as derived parameter
for (i in 1:length(fs)) {
    ratio <- calculate_fsc_ratio(fs[[i]])
    fs[[i]] <- cbind2(fs[[i]], ratio)
    colnames(fs[[i]])[ncol(fs[[i]])] <- 'FSC_ratio'
}

# Gate on ratio
ratio_cutoff <- quantile(exprs(fs[[1]])[, 'FSC_ratio'], 0.95)
singlet_gate_ratio <- rectangleGate(filterId = 'singlets', 'FSC_ratio' = c(0, ratio_cutoff))
```

## SSC-Based Doublet Detection

```r
# For cell types where FSC doesn't discriminate well,
# use SSC-A vs SSC-H additionally

ssc_singlet_gate <- rectangleGate(
    filterId = 'ssc_singlets',
    'SSC-A' = c(10000, 200000),
    'SSC-H' = c(10000, 200000)
)

# Combine FSC and SSC gates
combined_gate <- singlet_gate & ssc_singlet_gate
singlets <- Subset(fs, combined_gate)
```

## CyTOF Doublet Detection

```r
library(CATALYST)

# For CyTOF data, use DNA channels or event length

# DNA-based doublet detection (if DNA channels present)
# Doublets have ~2x DNA content
sce <- prepData(fs, panel, md)

# If Event_length channel exists
if ('Event_length' %in% rownames(sce)) {
    event_length <- assay(sce)['Event_length', ]
    singlet_idx <- event_length < quantile(event_length, 0.95)

    sce_singlets <- sce[, singlet_idx]
    cat('Removed', sum(!singlet_idx), 'doublets based on event length\n')
}

# DNA intercalator method
if (all(c('DNA1', 'DNA2') %in% rownames(sce))) {
    dna_total <- assay(sce)['DNA1', ] + assay(sce)['DNA2', ]
    dna_cutoff <- quantile(dna_total, 0.95)

    singlet_idx <- dna_total < dna_cutoff
    sce_singlets <- sce[, singlet_idx]
}
```

## CATALYST Workflow with Doublet Removal

**Goal:** Detect and remove cell doublets from a CyTOF/flow dataset using a regression-based approach on scatter parameters.

**Approach:** Model the expected FSC-A vs FSC-H relationship for singlets with linear regression, classify events with large residuals (above the 95th percentile) as doublets, and filter them out.

```r
library(CATALYST)

# Load and prepare data
sce <- prepData(fs, panel, md, transform = TRUE, cofactor = 5)

# Remove doublets using marker-based method
sce <- filterSCE(sce, !is_doublet(sce))

# Custom doublet detection based on FSC
fsc_a <- colData(sce)$FSC_A
fsc_h <- colData(sce)$FSC_H

# Model expected singlet relationship
fit <- lm(fsc_a ~ fsc_h)
residuals <- abs(fsc_a - predict(fit))
threshold <- quantile(residuals, 0.95)

# Mark doublets
colData(sce)$doublet <- residuals > threshold
sce_singlets <- sce[, !colData(sce)$doublet]

cat('Doublet rate:', round(mean(colData(sce)$doublet) * 100, 1), '%\n')
```

## Batch Processing

```r
# Process all samples
detect_doublets <- function(ff, method = 'fsc') {
    if (method == 'fsc') {
        fsc_a <- exprs(ff)[, 'FSC-A']
        fsc_h <- exprs(ff)[, 'FSC-H']

        fit <- lm(fsc_a ~ fsc_h)
        residuals <- abs(fsc_a - predict(fit))
        threshold <- quantile(residuals, 0.95)

        singlet_idx <- residuals <= threshold
    } else if (method == 'ratio') {
        ratio <- exprs(ff)[, 'FSC-A'] / (exprs(ff)[, 'FSC-H'] + 1)
        singlet_idx <- ratio < quantile(ratio, 0.95)
    }

    return(ff[singlet_idx, ])
}

# Apply to all samples
fs_singlets <- fsApply(fs, detect_doublets, method = 'fsc')

# Report
doublet_rates <- sapply(1:length(fs), function(i) {
    1 - nrow(fs_singlets[[i]]) / nrow(fs[[i]])
})
cat('Mean doublet rate:', round(mean(doublet_rates) * 100, 1), '%\n')
```

## Visualization

```r
library(ggplot2)

# Extract data for plotting
plot_data <- data.frame(
    FSC_A = exprs(fs[[1]])[, 'FSC-A'],
    FSC_H = exprs(fs[[1]])[, 'FSC-H']
)

# Calculate doublet status
fit <- lm(FSC_A ~ FSC_H, data = plot_data)
plot_data$residual <- abs(plot_data$FSC_A - predict(fit))
plot_data$doublet <- plot_data$residual > quantile(plot_data$residual, 0.95)

# Plot
ggplot(plot_data, aes(x = FSC_H, y = FSC_A, color = doublet)) +
    geom_point(alpha = 0.3, size = 0.5) +
    scale_color_manual(values = c('gray', 'red')) +
    theme_bw() +
    labs(title = 'Doublet Detection', x = 'FSC-H', y = 'FSC-A')
ggsave('doublet_detection.png', width = 8, height = 6)
```

## Related Skills

Workflow order: cytometry-qc → doublet-detection → bead-normalization → clustering

- cytometry-qc - Run first: identify flow rate and signal issues
- bead-normalization - Run after: correct remaining instrument drift
- fcs-handling - Load FCS files
- gating-analysis - Manual gating workflows
- clustering-phenotyping - Downstream analysis after doublet removal
