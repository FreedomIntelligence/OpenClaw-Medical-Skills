# bio-metabolomics-xcms-preprocessing

> XCMS3 workflow for LC-MS/MS metabolomics preprocessing. Covers peak detection, retention time alignment, correspondence (grouping), and gap filling. Use when processing raw LC-MS data into a feature table for untargeted metabolomics.

## Version Compatibility

Reference examples tested with: MSnbase 2.28+, scanpy 1.10+, xcms 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# XCMS Metabolomics Preprocessing

Requires Bioconductor 3.18+ with xcms 4.0+ and MSnbase 2.28+.

## Load Raw Data

**Goal:** Import raw LC-MS files into R for downstream peak detection and alignment.

**Approach:** Read mzML/mzXML files into an OnDiskMSnExp object using MSnbase for memory-efficient access.

**"Process my raw LC-MS data into a feature table"** → Detect chromatographic peaks, align retention times across samples, group corresponding peaks, and fill missing values to produce a sample-by-feature intensity matrix.

```r
library(xcms)
library(MSnbase)

# Read mzML/mzXML files
raw_files <- list.files('raw_data', pattern = '\\.(mzML|mzXML)$', full.names = TRUE)

# Create OnDiskMSnExp object
raw_data <- readMSData(raw_files, mode = 'onDisk')

# Check data
raw_data
table(msLevel(raw_data))
```

## Define Sample Groups

**Goal:** Attach sample metadata (group labels, injection order) to the raw data object.

**Approach:** Create a data frame of sample information and assign it to the phenoData slot.

```r
# Sample metadata
sample_info <- data.frame(
    sample_name = basename(raw_files),
    sample_group = c(rep('Control', 5), rep('Treatment', 5), rep('QC', 3)),
    injection_order = 1:length(raw_files)
)

# Assign to phenoData
pData(raw_data) <- sample_info
```

## Peak Detection (Centroided)

**Goal:** Identify chromatographic peaks in centroided LC-MS data.

**Approach:** Use the CentWave algorithm which detects peaks by continuous wavelet transform on regions of interest defined by m/z and RT.

```r
# CentWave algorithm for centroided data
cwp <- CentWaveParam(
    peakwidth = c(5, 30),       # Peak width range in seconds
    ppm = 15,                    # m/z tolerance
    snthresh = 10,               # Signal-to-noise threshold
    prefilter = c(3, 1000),      # Min peaks and intensity
    mzdiff = 0.01,               # Minimum m/z difference
    noise = 1000,                # Noise level
    integrate = 1                # Integration method
)

# Run peak detection
xdata <- findChromPeaks(raw_data, param = cwp)

# Summary
head(chromPeaks(xdata))
cat('Peaks found:', nrow(chromPeaks(xdata)), '\n')
```

## Peak Detection (Profile Data)

**Goal:** Detect peaks in profile (non-centroided) LC-MS data.

**Approach:** Use the MatchedFilter algorithm designed for continuum data, which convolves with a Gaussian model peak.

```r
# MatchedFilter for profile/continuum data
mfp <- MatchedFilterParam(
    binSize = 0.1,
    fwhm = 30,
    snthresh = 10,
    step = 0.1,
    mzdiff = 0.8
)

xdata_profile <- findChromPeaks(raw_data, param = mfp)
```

## Retention Time Alignment

**Goal:** Correct retention time drift across samples to enable peak correspondence.

**Approach:** Apply Obiwarp alignment which uses dynamic time warping on the TIC profiles to compute sample-wise RT corrections.

```r
# Obiwarp alignment (recommended)
obp <- ObiwarpParam(
    binSize = 0.5,
    response = 1,
    distFun = 'cor_opt',
    gapInit = 0.3,
    gapExtend = 2.4
)

xdata <- adjustRtime(xdata, param = obp)

# Check alignment
plotAdjustedRtime(xdata)
```

## Peak Correspondence (Grouping)

**Goal:** Group corresponding chromatographic peaks across samples into consensus features.

**Approach:** Use peak density-based grouping which models the RT distribution of peaks in m/z slices to identify features present across samples.

```r
# Group peaks across samples
pdp <- PeakDensityParam(
    sampleGroups = pData(xdata)$sample_group,
    bw = 5,                      # RT bandwidth
    minFraction = 0.5,           # Min fraction of samples
    minSamples = 1,              # Min samples per group
    binSize = 0.025              # m/z bin size
)

xdata <- groupChromPeaks(xdata, param = pdp)

# Check feature definitions
featureDefinitions(xdata)
cat('Features:', nrow(featureDefinitions(xdata)), '\n')
```

## Gap Filling

**Goal:** Recover signal for features that were missed during initial peak detection in some samples.

**Approach:** Integrate intensity in the expected m/z-RT region for features with missing values using ChromPeakAreaParam.

```r
# Fill in missing peaks
fpp <- ChromPeakAreaParam()
xdata <- fillChromPeaks(xdata, param = fpp)

# Alternative: FillChromPeaksParam for more control
fpp2 <- FillChromPeaksParam(
    expandMz = 0,
    expandRt = 0,
    ppm = 0
)
```

## Extract Feature Table

**Goal:** Generate a samples-by-features intensity matrix with m/z and RT annotations for downstream analysis.

**Approach:** Extract feature values and definitions from the processed XCMSnExp object and combine into an exportable table.

```r
# Get feature values (intensity matrix)
feature_values <- featureValues(xdata, method = 'maxint', value = 'into')

# Feature definitions (m/z, RT)
feature_defs <- featureDefinitions(xdata)
feature_defs <- as.data.frame(feature_defs)
feature_defs$feature_id <- rownames(feature_defs)

# Combine
feature_table <- cbind(feature_defs[, c('feature_id', 'mzmed', 'rtmed')], feature_values)
rownames(feature_table) <- feature_table$feature_id

# Save
write.csv(feature_table, 'feature_table.csv', row.names = FALSE)
```

## Quality Control

**Goal:** Assess preprocessing quality through TIC plots, peak counts, RT correction, and PCA.

**Approach:** Visualize total ion chromatograms, per-sample peak counts, RT adjustment, and PCA of the feature matrix.

```r
# TIC for each sample
tic <- chromatogram(raw_data, aggregationFun = 'sum')
plot(tic)

# Peak count per sample
peak_counts <- table(chromPeaks(xdata)[, 'sample'])
barplot(peak_counts, main = 'Peaks per sample')

# Check RT correction
par(mfrow = c(1, 2))
plotAdjustedRtime(xdata, col = pData(xdata)$sample_group)

# PCA of features
library(pcaMethods)
log_values <- log2(feature_values + 1)
log_values[is.na(log_values)] <- 0
pca <- pca(t(log_values), nPcs = 3, method = 'ppca')
plotPcs(pca, col = as.factor(pData(xdata)$sample_group))
```

## CAMERA Annotation (Isotopes/Adducts)

**Goal:** Identify isotope patterns and adduct groups among detected peaks to reduce feature redundancy.

**Approach:** Use CAMERA to group peaks by RT correlation, assign isotope clusters, and annotate adduct types.

```r
library(CAMERA)

# Create CAMERA object
xsa <- xsAnnotate(as(xdata, 'xcmsSet'))

# Group by RT
xsa <- groupFWHM(xsa, perfwhm = 0.6)

# Find isotopes
xsa <- findIsotopes(xsa, mzabs = 0.01, ppm = 10)

# Find adducts
xsa <- findAdducts(xsa, polarity = 'positive')

# Get annotated peak list
camera_results <- getPeaklist(xsa)
```

## Export for MetaboAnalyst

**Goal:** Format the XCMS feature table for import into MetaboAnalyst web or R package.

**Approach:** Transpose the matrix, create M/Z-RT feature names, and prepend sample group information.

```r
# Format for MetaboAnalyst web or R package
export_data <- t(feature_values)
colnames(export_data) <- paste0('M', round(feature_defs$mzmed, 4), 'T', round(feature_defs$rtmed, 1))

# Add sample info
export_df <- data.frame(Sample = rownames(export_data), Group = pData(xdata)$sample_group, export_data)

write.csv(export_df, 'metaboanalyst_input.csv', row.names = FALSE)
```

## Related Skills

- metabolite-annotation - Identify metabolites
- normalization-qc - Normalize feature table
- statistical-analysis - Differential analysis
