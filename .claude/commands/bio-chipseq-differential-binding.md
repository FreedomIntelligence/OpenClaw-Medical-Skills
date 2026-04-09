# bio-chipseq-differential-binding

> Differential binding analysis using DiffBind. Compare ChIP-seq peaks between conditions with statistical rigor. Requires replicate samples. Outputs differentially bound regions with fold changes and p-values. Use when comparing ChIP-seq binding between conditions.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, edgeR 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Differential Binding with DiffBind

**"Compare ChIP-seq binding between conditions"** → Identify genomic regions with statistically significant differences in transcription factor or histone mark occupancy between experimental groups.
- R: `DiffBind::dba()` → `dba.count()` → `dba.contrast()` → `dba.analyze()`

## Create Sample Sheet

**Goal:** Define the experimental design linking BAM files, peak files, and sample metadata for DiffBind.

**Approach:** Build a data frame (or CSV) with required columns mapping each sample to its files and conditions.

```r
# Create sample sheet as data frame or CSV
samples <- data.frame(
    SampleID = c('ctrl_1', 'ctrl_2', 'treat_1', 'treat_2'),
    Tissue = c('cell', 'cell', 'cell', 'cell'),
    Factor = c('H3K4me3', 'H3K4me3', 'H3K4me3', 'H3K4me3'),
    Condition = c('control', 'control', 'treatment', 'treatment'),
    Replicate = c(1, 2, 1, 2),
    bamReads = c('ctrl1.bam', 'ctrl2.bam', 'treat1.bam', 'treat2.bam'),
    Peaks = c('ctrl1_peaks.narrowPeak', 'ctrl2_peaks.narrowPeak',
              'treat1_peaks.narrowPeak', 'treat2_peaks.narrowPeak'),
    PeakCaller = c('macs', 'macs', 'macs', 'macs')
)

write.csv(samples, 'samples.csv', row.names = FALSE)
```

## Load Data

**Goal:** Initialize a DiffBind object from the sample sheet containing all samples and peaks.

**Approach:** Read the sample sheet CSV into a DBA object that identifies overlapping peaks across samples.

```r
library(DiffBind)

# From sample sheet
dba_obj <- dba(sampleSheet = 'samples.csv')

# View summary
dba_obj
```

## Count Reads in Peaks

**Goal:** Quantify read coverage at consensus peak regions across all samples.

**Approach:** Count reads in summit-centered windows using dba.count, creating a count matrix for statistical testing.

```r
# Count reads in consensus peaks
# summits=250 and bUseSummarizeOverlaps=TRUE are now defaults
dba_obj <- dba.count(dba_obj)

# With specific parameters
dba_obj <- dba.count(
    dba_obj,
    summits = 250,         # Re-center peaks around summits (default in 3.0)
    minOverlap = 2         # Peak must be in at least 2 samples
)
```

## Normalize Data

**Goal:** Apply normalization to account for library size and composition differences between samples.

**Approach:** Use dba.normalize which applies DESeq2/edgeR normalization factors to the count matrix.

```r
# Normalize (required before analysis)
dba_obj <- dba.normalize(dba_obj)

# Check normalization
dba.normalize(dba_obj, bRetrieve = TRUE)
```

## Set Up Contrast

**Goal:** Define the comparison between experimental conditions for differential testing.

**Approach:** Specify a design formula or category-based contrast that tells DiffBind which groups to compare.

```r
# Recommended: design formula approach
dba_obj <- dba.contrast(dba_obj, design = '~ Condition')

# Or use categories for automatic contrast
dba_obj <- dba.contrast(dba_obj, categories = DBA_CONDITION)

# Legacy approach (retained for backward compatibility, not recommended)
# dba_obj <- dba.contrast(dba_obj, group1 = dba_obj$masks$control,
#                         group2 = dba_obj$masks$treatment)
```

## Run Differential Analysis

**Goal:** Identify peaks with statistically significant binding differences between conditions.

**Approach:** Apply DESeq2 or edgeR negative binomial models to the normalized count matrix.

```r
# Analyze with DESeq2 (default)
dba_obj <- dba.analyze(dba_obj, method = DBA_DESEQ2)

# Or with edgeR
dba_obj <- dba.analyze(dba_obj, method = DBA_EDGER)
```

## View Results

**Goal:** Retrieve and inspect differentially bound regions with fold changes and significance values.

**Approach:** Extract results as a GRanges object with dba.report, sorted by significance.

```r
# Summary of differential peaks
dba.show(dba_obj, bContrasts = TRUE)

# Retrieve differential binding results
db_results <- dba.report(dba_obj)
db_results
```

## Filter Results

**Goal:** Subset differential peaks by significance and fold-change thresholds.

**Approach:** Apply FDR and fold-change cutoffs to dba.report output.

```r
# Get significant peaks (FDR < 0.05, |FC| > 2)
db_sig <- dba.report(dba_obj, th = 0.05, fold = 2)

# Get all results for custom filtering
db_all <- dba.report(dba_obj, th = 1)
```

## Export Results

```r
# To data frame
results_df <- as.data.frame(dba.report(dba_obj, th = 1))

# Export to CSV
write.csv(results_df, 'differential_binding.csv', row.names = FALSE)

# Export to BED
library(rtracklayer)
export(db_sig, 'diff_peaks.bed', format = 'BED')
```

## Visualization

```r
# PCA plot
dba.plotPCA(dba_obj, DBA_CONDITION, label = DBA_ID)

# Correlation heatmap
dba.plotHeatmap(dba_obj)

# MA plot
dba.plotMA(dba_obj)

# Volcano plot
dba.plotVolcano(dba_obj)

# Heatmap of differential peaks
dba.plotHeatmap(dba_obj, contrast = 1, correlations = FALSE)
```

## Venn Diagram of Peaks

```r
# Overlap between conditions
dba.plotVenn(dba_obj, dba_obj$masks$control)
dba.plotVenn(dba_obj, dba_obj$masks$treatment)
```

## Profile Plots

```r
# Average signal profile
profiles <- dba.plotProfile(dba_obj)
```

## Get Consensus Peaks

```r
# Export consensus peakset
consensus <- dba.peakset(dba_obj, bRetrieve = TRUE)
export(consensus, 'consensus_peaks.bed', format = 'BED')
```

## Multi-Factor Design

```r
# With blocking factor (e.g., batch correction)
dba_obj <- dba.contrast(dba_obj, design = '~ Batch + Condition')
dba_obj <- dba.analyze(dba_obj)
```

## DiffBind 3.0 Notes

DiffBind 3.0+ introduced significant changes:
- `dba.normalize()` is now required before analysis
- Default `summits=250` recenters peaks (was FALSE in older versions)
- Use design formulas instead of group1/group2 for contrasts
- Blacklist filtering is applied by default

## Sample Sheet Columns

| Column | Required | Description |
|--------|----------|-------------|
| SampleID | Yes | Unique identifier |
| Tissue | No | Tissue/cell type |
| Factor | No | ChIP target |
| Condition | Yes | Experimental condition |
| Treatment | No | Additional grouping |
| Replicate | Yes | Replicate number |
| bamReads | Yes | Path to BAM file |
| Peaks | Yes | Path to peak file |
| PeakCaller | Yes | macs, bed, narrow |
| bamControl | No | Path to input BAM |

## Key Functions

| Function | Purpose |
|----------|---------|
| dba | Create DBA object |
| dba.count | Count reads in peaks |
| dba.normalize | Normalize counts |
| dba.contrast | Set up comparison |
| dba.analyze | Run differential analysis |
| dba.report | Get results |
| dba.plotPCA | PCA visualization |
| dba.plotMA | MA plot |
| dba.plotHeatmap | Heatmap |

## Related Skills

- peak-calling - Generate input peak files
- peak-annotation - Annotate differential peaks
- differential-expression - Compare with RNA-seq
- pathway-analysis - Functional enrichment
