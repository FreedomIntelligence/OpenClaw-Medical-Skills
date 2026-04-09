# bio-metabolomics-msdial-preprocessing

> MS-DIAL-based metabolomics preprocessing as alternative to XCMS. Covers peak detection, alignment, annotation, and export for downstream analysis. Use when processing MS-DIAL output files for R/Python analysis or when preferring GUI-based preprocessing.

## Version Compatibility

Reference examples tested with: numpy 1.26+, pandas 2.2+, scanpy 1.10+, xcms 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# MS-DIAL Preprocessing

**"Process my LC-MS data with MS-DIAL"** → Detect chromatographic peaks, align across samples, annotate metabolites, and export a feature table for statistical analysis.
- CLI: MS-DIAL GUI or console mode for peak picking and alignment

## MS-DIAL GUI Workflow

MS-DIAL provides a user-friendly GUI for complete metabolomics preprocessing:

1. **Project Setup** - Create new project, select data type
2. **Data Import** - Load mzML/ABF files
3. **Peak Detection** - Automatic peak picking
4. **Alignment** - Cross-sample alignment
5. **Gap Filling** - Fill missing values
6. **Annotation** - Database matching
7. **Export** - Export for downstream analysis

## Export MS-DIAL Results to R

```r
library(tidyverse)

# Load MS-DIAL alignment result
msdial_data <- read.csv('msdial_alignment_result.csv', check.names = FALSE)

# Typical columns from MS-DIAL export
# Alignment ID, Average Rt(min), Average Mz, Metabolite name, Adduct type,
# Fill %, MS/MS assigned, Reference RT, Reference m/z, Formula, Ontology,
# INCHIKEY, SMILES, Annotation tag (Level), Comment, [Sample columns...]

# Identify sample columns (contain "Area" or sample names)
sample_cols <- grep('Area$|^Sample', colnames(msdial_data), value = TRUE)
meta_cols <- setdiff(colnames(msdial_data), sample_cols)

# Extract feature metadata
feature_info <- msdial_data[, meta_cols]

# Extract intensity matrix
intensity_matrix <- as.matrix(msdial_data[, sample_cols])
rownames(intensity_matrix) <- msdial_data$`Alignment ID`

cat('Loaded', nrow(intensity_matrix), 'features from', ncol(intensity_matrix), 'samples\n')
```

## Filter MS-DIAL Results

```r
# Filter by annotation confidence
# MS-DIAL Annotation tags: Lipid, Metabolite, Unknown, etc.
annotated <- feature_info$`Annotation tag` != 'Unknown'

# Filter by fill percentage (presence across samples)
fill_threshold <- 50  # Present in at least 50% of samples
good_fill <- feature_info$`Fill %` >= fill_threshold

# Filter by MS/MS match
has_msms <- feature_info$`MS/MS assigned` == TRUE

# Apply filters
filtered_idx <- which(good_fill)  # Minimum filter
filtered_matrix <- intensity_matrix[filtered_idx, ]
filtered_info <- feature_info[filtered_idx, ]

cat('After filtering:', nrow(filtered_matrix), 'features\n')
```

## MS-DIAL Data to XCMS-Like Format

```r
library(SummarizedExperiment)

# Create SummarizedExperiment for compatibility with other tools
se <- SummarizedExperiment(
    assays = list(raw = filtered_matrix),
    rowData = filtered_info,
    colData = data.frame(
        sample = colnames(filtered_matrix),
        row.names = colnames(filtered_matrix)
    )
)

# Add sample metadata
sample_metadata <- read.csv('sample_metadata.csv')
colData(se) <- merge(colData(se), sample_metadata, by.x = 'sample', by.y = 'sample_id')
```

## MS-DIAL Batch Processing (Console Mode)

```bash
# MS-DIAL console application for batch processing
# Available on Windows

# Create parameter file (msdial_param.txt)
# See MS-DIAL documentation for all parameters

# Run MS-DIAL console
MsdialConsoleApp.exe lcmsdda -i input_folder -o output_folder -m msdial_param.txt
```

## Parameter File Example

```
# MS-DIAL Parameter File for LC-MS DDA

# Data collection
Data type=Centroid
Ion mode=Positive
MS1 data type=Centroid
MS2 data type=Centroid

# Peak detection
Smoothing method=LinearWeightedMovingAverage
Smoothing level=3
Minimum peak width=5
Minimum peak height=1000
Mass slice width=0.1

# Alignment
Retention time tolerance=0.1
MS1 tolerance=0.01
Retention time factor=0.5
MS1 factor=0.5

# Identification
MSP file path=MassBank-GNPS.msp
Retention time tolerance for identification=0.5
Accurate mass tolerance (MS1)=0.01
Accurate mass tolerance (MS2)=0.05
Identification score cut off=80
```

## Python Processing of MS-DIAL Output

**Goal:** Convert MS-DIAL alignment results into a clean, filtered, log-transformed feature matrix for downstream statistical analysis.

**Approach:** Parse MS-DIAL CSV export to separate feature metadata from intensity values, filter by fill percentage, log2-transform, and export as a tidy matrix.

```python
import pandas as pd
import numpy as np

# Load MS-DIAL alignment results
df = pd.read_csv('msdial_alignment_result.csv')

# Identify sample columns
sample_cols = [c for c in df.columns if 'Area' in c or c.startswith('Sample')]
meta_cols = [c for c in df.columns if c not in sample_cols]

# Create feature info and intensity matrix
feature_info = df[meta_cols].copy()
intensities = df[sample_cols].values

# Clean column names (remove 'Area' suffix)
sample_names = [c.replace(' Area', '').strip() for c in sample_cols]

# Filter by fill percentage
fill_pct = df['Fill %'].values
good_features = fill_pct >= 50

intensities_filtered = intensities[good_features]
feature_info_filtered = feature_info[good_features].reset_index(drop=True)

print(f'Filtered: {sum(good_features)} / {len(good_features)} features')

# Log transform
intensities_log = np.log2(intensities_filtered + 1)

# Export for downstream analysis
result_df = pd.DataFrame(
    intensities_log,
    columns=sample_names,
    index=feature_info_filtered['Alignment ID']
)
result_df.to_csv('msdial_processed.csv')
```

## MS-DIAL Annotation Levels

```r
# MS-DIAL uses different annotation confidence levels
annotation_levels <- data.frame(
    level = c('Lipid', 'Metabolite', 'SuggestedLipid', 'SuggestedMetabolite', 'Unknown'),
    confidence = c('High', 'High', 'Medium', 'Medium', 'None'),
    description = c(
        'MS/MS match to lipid database',
        'MS/MS match to metabolite database',
        'Mass match to lipid (no MS/MS)',
        'Mass match to metabolite (no MS/MS)',
        'No database match'
    )
)

# Count by annotation level
table(feature_info$`Annotation tag`)
```

## Compare MS-DIAL vs XCMS Results

```r
# Load both preprocessing results
msdial_features <- read.csv('msdial_alignment_result.csv')
xcms_features <- read.csv('xcms_features.csv')

# Compare feature counts
cat('MS-DIAL features:', nrow(msdial_features), '\n')
cat('XCMS features:', nrow(xcms_features), '\n')

# Match features by m/z and RT
match_features <- function(mz1, rt1, mz2, rt2, mz_tol = 0.01, rt_tol = 0.5) {
    matches <- data.frame()
    for (i in 1:length(mz1)) {
        mz_match <- abs(mz2 - mz1[i]) < mz_tol
        rt_match <- abs(rt2 - rt1[i]) < rt_tol
        both_match <- which(mz_match & rt_match)
        if (length(both_match) > 0) {
            matches <- rbind(matches, data.frame(idx1 = i, idx2 = both_match[1]))
        }
    }
    return(matches)
}

matched <- match_features(
    msdial_features$`Average Mz`, msdial_features$`Average Rt(min)`,
    xcms_features$mzmed, xcms_features$rtmed / 60
)

cat('Matched features:', nrow(matched), '\n')
```

## Export for MetaboAnalyst

```r
# MS-DIAL output to MetaboAnalyst format
# MetaboAnalyst expects: rows = samples, columns = features

# Transpose matrix
metaboanalyst_format <- t(filtered_matrix)

# Add sample metadata as first columns
sample_info <- colData(se)
metaboanalyst_df <- cbind(
    Sample = rownames(metaboanalyst_format),
    Group = sample_info$condition,
    as.data.frame(metaboanalyst_format)
)

write.csv(metaboanalyst_df, 'for_metaboanalyst.csv', row.names = FALSE)
```

## Normalization Options

```r
# MS-DIAL provides several normalization options during export
# Or apply post-hoc:

# Internal standard normalization
normalize_istd <- function(data, istd_idx) {
    istd_values <- data[istd_idx, ]
    sweep(data[-istd_idx, ], 2, istd_values, '/')
}

# LOWESS normalization (QC-based)
normalize_loess <- function(data, qc_idx, span = 0.75) {
    qc_data <- data[, qc_idx]
    qc_median <- apply(qc_data, 1, median)

    normalized <- data
    for (i in 1:ncol(data)) {
        loess_fit <- loess(data[, i] ~ qc_median, span = span)
        normalized[, i] <- data[, i] / predict(loess_fit)
    }
    return(normalized)
}

# Probabilistic Quotient Normalization
normalize_pqn <- function(data) {
    reference <- apply(data, 1, median)
    quotients <- sweep(data, 1, reference, '/')
    sample_medians <- apply(quotients, 2, median, na.rm = TRUE)
    sweep(data, 2, sample_medians, '/')
}
```

## Related Skills

- xcms-preprocessing - Alternative preprocessing with XCMS
- metabolite-annotation - Additional annotation methods
- normalization-qc - Detailed normalization approaches
- lipidomics - Lipid-specific MS-DIAL workflows
