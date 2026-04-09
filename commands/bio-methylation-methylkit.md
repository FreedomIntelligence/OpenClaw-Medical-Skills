# bio-methylation-methylkit

> DNA methylation analysis with methylKit in R. Import Bismark coverage files, filter by coverage, normalize samples, and perform statistical comparisons. Use when analyzing single-base methylation patterns, comparing samples, or preparing data for DMR detection.

## Version Compatibility

Reference examples tested with: Bismark 0.24+, methylKit 1.28+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# methylKit Analysis

**"Analyze methylation patterns across my samples"** → Import per-cytosine methylation data, filter by coverage, normalize across samples, and test for differential methylation at individual CpG sites.
- R: `methylKit::methRead()` → `filterByCoverage()` → `normalizeCoverage()` → `calculateDiffMeth()`

## Read Bismark Coverage Files

```r
library(methylKit)

file_list <- list('sample1.bismark.cov.gz', 'sample2.bismark.cov.gz',
                   'sample3.bismark.cov.gz', 'sample4.bismark.cov.gz')
sample_ids <- c('ctrl_1', 'ctrl_2', 'treat_1', 'treat_2')
treatment <- c(0, 0, 1, 1)  # 0 = control, 1 = treatment

meth_obj <- methRead(
    location = as.list(file_list),
    sample.id = as.list(sample_ids),
    treatment = treatment,
    assembly = 'hg38',
    context = 'CpG',
    pipeline = 'bismarkCoverage'
)
```

## Read Bismark cytosine Report

```r
meth_obj <- methRead(
    location = as.list(file_list),
    sample.id = as.list(sample_ids),
    treatment = treatment,
    assembly = 'hg38',
    context = 'CpG',
    pipeline = 'bismarkCytosineReport'
)
```

## Basic Statistics

```r
# Coverage statistics
getMethylationStats(meth_obj[[1]], plot = TRUE, both.strands = FALSE)

# Coverage per sample
getCoverageStats(meth_obj[[1]], plot = TRUE, both.strands = FALSE)
```

## Filter by Coverage

```r
# Remove CpGs with very low or very high coverage
meth_filtered <- filterByCoverage(
    meth_obj,
    lo.count = 10,        # Minimum 10 reads
    lo.perc = NULL,
    hi.count = NULL,
    hi.perc = 99.9        # Remove top 0.1% (likely PCR artifacts)
)
```

## Normalize Coverage

```r
# Normalize coverage between samples (recommended)
meth_norm <- normalizeCoverage(meth_filtered, method = 'median')
```

## Merge Samples (Unite)

```r
# Find common CpGs across all samples
meth_united <- unite(meth_norm, destrand = TRUE)  # Combine strands

# Allow some missing data
meth_united <- unite(meth_norm, destrand = TRUE, min.per.group = 2L)
```

## Visualize Samples

```r
# Correlation between samples
getCorrelation(meth_united, plot = TRUE)

# PCA of samples
PCASamples(meth_united, screeplot = TRUE)
PCASamples(meth_united)

# Clustering
clusterSamples(meth_united, dist = 'correlation', method = 'ward.D', plot = TRUE)
```

## Differential Methylation (Single CpGs)

```r
# Calculate differential methylation
diff_meth <- calculateDiffMeth(
    meth_united,
    overdispersion = 'MN',     # Use shrinkage
    test = 'Chisq',
    mc.cores = 4
)

# Get significant differentially methylated CpGs
dmcs <- getMethylDiff(diff_meth, difference = 25, qvalue = 0.01)

# Hyper vs hypomethylated
dmcs_hyper <- getMethylDiff(diff_meth, difference = 25, qvalue = 0.01, type = 'hyper')
dmcs_hypo <- getMethylDiff(diff_meth, difference = 25, qvalue = 0.01, type = 'hypo')
```

## Tile-Based Analysis (Regions)

**Goal:** Detect differentially methylated regions by aggregating single CpG data into fixed-size genomic windows.

**Approach:** Tile individual CpG measurements into 1kb windows, unite common tiles across samples, and run differential methylation testing on the aggregated tiles.

```r
# Aggregate CpGs into tiles/windows
tiles <- tileMethylCounts(meth_obj, win.size = 1000, step.size = 1000)
tiles_united <- unite(tiles, destrand = TRUE)

# Differential methylation on tiles
diff_tiles <- calculateDiffMeth(tiles_united, overdispersion = 'MN', mc.cores = 4)
dmrs <- getMethylDiff(diff_tiles, difference = 25, qvalue = 0.01)
```

## Export Results

```r
# To data frame
diff_df <- getData(dmcs)
write.csv(diff_df, 'dmcs_results.csv', row.names = FALSE)

# To BED file
library(genomation)
dmcs_gr <- as(dmcs, 'GRanges')
export(dmcs_gr, 'dmcs.bed', format = 'BED')
```

## Annotate with Genomic Features

```r
library(genomation)

gene_obj <- readTranscriptFeatures('genes.bed')

annotated <- annotateWithGeneParts(as(dmcs, 'GRanges'), gene_obj)

# Or with annotatr
library(annotatr)
annotations <- build_annotations(genome = 'hg38', annotations = 'hg38_basicgenes')
dmcs_annotated <- annotate_regions(regions = as(dmcs, 'GRanges'), annotations = annotations)
```

## Reorganize for Multi-Group Comparison

```r
# For more than 2 groups
meth_obj <- reorganize(
    meth_united,
    sample.ids = c('A1', 'A2', 'B1', 'B2', 'C1', 'C2'),
    treatment = c(0, 0, 1, 1, 2, 2)
)
```

## Pool Replicates

```r
# Combine biological replicates
meth_pooled <- pool(meth_united, sample.ids = c('control', 'treatment'))
```

## Key Functions

| Function | Purpose |
|----------|---------|
| methRead | Read methylation files |
| filterByCoverage | Remove low/high coverage |
| normalizeCoverage | Normalize between samples |
| unite | Find common CpGs |
| calculateDiffMeth | Statistical test |
| getMethylDiff | Filter significant results |
| tileMethylCounts | Region-level analysis |
| PCASamples | PCA visualization |
| getCorrelation | Sample correlation |

## Key Parameters for calculateDiffMeth

| Parameter | Default | Description |
|-----------|---------|-------------|
| overdispersion | none | MN (shrinkage) or shrinkMN |
| test | Chisq | Chisq, F, fast.fisher |
| mc.cores | 1 | Parallel cores |
| slim | TRUE | Remove unused columns |

## Related Skills

- bismark-alignment - Generate input BAM files
- methylation-calling - Extract coverage files
- dmr-detection - Advanced DMR methods
- pathway-analysis/go-enrichment - Functional annotation
