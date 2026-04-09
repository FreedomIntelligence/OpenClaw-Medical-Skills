# bio-workflows-metabolomics-pipeline

> End-to-end metabolomics workflow from raw MS data to pathway analysis. Orchestrates XCMS preprocessing, annotation, normalization, statistical analysis, and pathway mapping. Use when processing LC-MS metabolomics data.

**Available tools:** Read, Bash

# Metabolomics Pipeline

## Pipeline Overview

```
Raw MS Data (mzML/mzXML) ──> Peak Detection ──> Feature Matrix
                                                     │
                                                     ▼
                   ┌─────────────────────────────────────────────┐
                   │          metabolomics-pipeline              │
                   ├─────────────────────────────────────────────┤
                   │  1. Peak Detection (XCMS)                   │
                   │  2. Retention Time Alignment                │
                   │  3. Feature Grouping & Gap Filling          │
                   │  4. QC & Normalization                      │
                   │  5. Statistical Analysis                    │
                   │  6. Metabolite Annotation                   │
                   │  7. Pathway Mapping                         │
                   └─────────────────────────────────────────────┘
                                                     │
                                                     ▼
                       Differential Metabolites + Enriched Pathways
```

## Complete R Workflow

```r
library(xcms)
library(MSnbase)
library(MetaboAnalystR)
library(ggplot2)

# === 1. LOAD DATA ===
mzml_files <- list.files('data/', pattern = '\\.mzML$', full.names = TRUE)
sample_data <- read.csv('sample_metadata.csv')

raw_data <- readMSData(mzml_files, mode = 'onDisk')

# Add sample metadata
pData(raw_data) <- sample_data

cat('Loaded', length(mzml_files), 'samples\n')

# === 2. PEAK DETECTION ===
cwp <- CentWaveParam(
    peakwidth = c(5, 30),
    ppm = 25,
    snthresh = 10,
    prefilter = c(3, 1000),
    mzdiff = 0.01,
    noise = 1000
)

xdata <- findChromPeaks(raw_data, param = cwp)
cat('Detected', nrow(chromPeaks(xdata)), 'peaks\n')

# === 3. RETENTION TIME ALIGNMENT ===
xdata <- adjustRtime(xdata, param = ObiwarpParam(binSize = 0.6))
cat('Aligned retention times\n')

# === 4. FEATURE GROUPING ===
pdp <- PeakDensityParam(
    sampleGroups = pData(xdata)$condition,
    minFraction = 0.5,
    bw = 5,
    binSize = 0.025
)

xdata <- groupChromPeaks(xdata, param = pdp)
cat('Grouped into', nrow(featureDefinitions(xdata)), 'features\n')

# === 5. GAP FILLING ===
xdata <- fillChromPeaks(xdata, param = ChromPeakAreaParam())

# === 6. EXTRACT FEATURE MATRIX ===
feature_matrix <- featureValues(xdata, value = 'into', method = 'maxint')
feature_info <- featureDefinitions(xdata)

# === 7. QC & NORMALIZATION ===
# Log2 transform
feature_matrix[feature_matrix == 0] <- NA
log_matrix <- log2(feature_matrix)

# Filter features (present in >50% of samples)
valid_features <- rowSums(!is.na(log_matrix)) > ncol(log_matrix) * 0.5
filtered_matrix <- log_matrix[valid_features, ]
cat('After filtering:', nrow(filtered_matrix), 'features\n')

# Median normalization
sample_medians <- apply(filtered_matrix, 2, median, na.rm = TRUE)
global_median <- median(sample_medians)
normalized <- sweep(filtered_matrix, 2, sample_medians - global_median)

# === 8. QC PLOTS ===
# PCA
pca <- prcomp(t(normalized), scale. = TRUE)
pca_df <- data.frame(PC1 = pca$x[, 1], PC2 = pca$x[, 2],
                     Sample = rownames(pca$x),
                     Condition = pData(xdata)$condition)

ggplot(pca_df, aes(PC1, PC2, color = Condition)) +
    geom_point(size = 3) +
    theme_bw() +
    labs(title = 'PCA of Metabolomics Data')
ggsave('qc_pca.png', width = 8, height = 6)

# === 9. STATISTICAL ANALYSIS ===
library(limma)

design <- model.matrix(~ 0 + condition, data = pData(xdata))
colnames(design) <- levels(factor(pData(xdata)$condition))

# Impute missing values for limma
imputed <- normalized
imputed[is.na(imputed)] <- min(imputed, na.rm = TRUE) - 1

fit <- lmFit(imputed, design)
contrast <- makeContrasts(Treatment - Control, levels = design)
fit2 <- contrasts.fit(fit, contrast)
fit2 <- eBayes(fit2)

results <- topTable(fit2, number = Inf, adjust.method = 'BH')
results$feature_id <- rownames(results)
results$significant <- abs(results$logFC) > 1 & results$adj.P.Val < 0.05

cat('\nSignificant features:', sum(results$significant), '\n')

# === 10. METABOLITE ANNOTATION ===
# Add m/z and RT to results
results$mz <- feature_info[results$feature_id, 'mzmed']
results$rt <- feature_info[results$feature_id, 'rtmed']

# KEGG annotation (simplified - use CAMERA for adduct annotation)
library(KEGGREST)

annotate_mz <- function(mz, ppm = 10) {
    # Query KEGG for matching compounds
    # This is simplified - real annotation uses databases
    mz_range <- c(mz * (1 - ppm/1e6), mz * (1 + ppm/1e6))
    return(NA)  # Placeholder
}

# === 11. VOLCANO PLOT ===
ggplot(results, aes(x = logFC, y = -log10(adj.P.Val), color = significant)) +
    geom_point(alpha = 0.5) +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed') +
    geom_vline(xintercept = c(-1, 1), linetype = 'dashed') +
    scale_color_manual(values = c('gray', 'red')) +
    theme_bw() +
    labs(title = 'Differential Metabolites', x = 'Log2 Fold Change', y = '-Log10(adj. p-value)')
ggsave('volcano_metabolites.png', width = 8, height = 6)

# === 12. OUTPUT ===
write.csv(results, 'differential_metabolites.csv', row.names = FALSE)
write.csv(normalized, 'normalized_feature_matrix.csv')
cat('Results saved!\n')
```

## MetaboAnalystR Pathway Analysis

```r
library(MetaboAnalystR)

# Initialize
mSet <- InitDataObjects('conc', 'pathora', FALSE)

# Load compound list (HMDB IDs)
sig_features <- results[results$significant, ]
compound_list <- sig_features$hmdb_id  # Requires annotation

mSet <- Setup.MapData(mSet, compound_list)
mSet <- CrossReferencing(mSet, 'hmdb')
mSet <- CreateMappingResultTable(mSet)

# Pathway analysis
mSet <- SetKEGG.PathLib(mSet, 'hsa')
mSet <- SetMetabolomeFilter(mSet, FALSE)
mSet <- CalculateOraScore(mSet, 'rbc', 'hyperg')

# View results
pathway_results <- mSet$analSet$ora.mat
head(pathway_results)

# Plot
mSet <- PlotPathSummary(mSet, 'pathway_overview', 'png', 300, 10, 10)
```

## Alternative: MS-DIAL Preprocessing

```r
# Load MS-DIAL exported data
msdial_export <- read.csv('msdial_alignment.csv')

# MS-DIAL already provides:
# - Peak detection
# - Alignment
# - Gap filling
# - Annotation attempts

# Continue with normalization and statistics
feature_matrix <- as.matrix(msdial_export[, grep('Area', colnames(msdial_export))])
rownames(feature_matrix) <- msdial_export$`Alignment.ID`

# Proceed with normalization and limma as above
```

## QC Checkpoints

| Stage | Check | Action if Failed |
|-------|-------|------------------|
| Peak detection | >1000 features | Adjust parameters |
| Alignment | RT deviation <30s | Check QC samples |
| Grouping | >60% features grouped | Adjust bw/minFraction |
| Missing values | <30% per sample | Check injection |
| QC RSD | <30% for QC features | Check instrument |
| PCA | Groups separate | Check batch effects |

## Workflow Variants

### Lipidomics
```r
# Adjust peak width for lipids
cwp_lipid <- CentWaveParam(
    peakwidth = c(10, 60),  # Broader peaks
    ppm = 15,
    snthresh = 5
)

# Use LipidMaps for annotation
```

### Targeted Analysis
```r
# Define target compounds
targets <- data.frame(
    name = c('Glucose', 'Lactate', 'Citrate'),
    mz = c(179.0561, 89.0244, 191.0197),
    rt = c(120, 90, 180)
)

# Extract targeted features
extractTargets <- function(xdata, targets, mz_ppm = 10, rt_tol = 30) {
    lapply(1:nrow(targets), function(i) {
        chromPeaks(xdata, mz = targets$mz[i], ppm = mz_ppm,
                   rt = c(targets$rt[i] - rt_tol, targets$rt[i] + rt_tol))
    })
}
```

## Related Skills

- metabolomics/xcms-preprocessing - XCMS parameters
- metabolomics/metabolite-annotation - Compound identification
- metabolomics/normalization-qc - QC and normalization methods
- metabolomics/statistical-analysis - Statistical testing
- metabolomics/pathway-mapping - KEGG/MetaboAnalyst
- metabolomics/lipidomics - Lipid-specific analysis
- metabolomics/targeted-analysis - Absolute quantification
- metabolomics/msdial-preprocessing - MS-DIAL export processing
- multi-omics-integration/mofa-integration - Integrate with other omics
