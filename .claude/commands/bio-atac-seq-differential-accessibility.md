# bio-atac-seq-differential-accessibility

> Find differentially accessible chromatin regions between conditions using DiffBind or DESeq2. Use when comparing chromatin accessibility between treatment groups, cell types, or developmental stages in ATAC-seq experiments.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, GenomicRanges 1.54+, Subread 2.0+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Differential Accessibility

**"Find differentially accessible regions between my conditions"** → Identify chromatin regions with statistically significant changes in accessibility between treatment groups, cell types, or timepoints.
- R: `DiffBind` or `DESeq2` on a peak-by-sample count matrix

## DiffBind Workflow

**Goal:** Identify differentially accessible chromatin regions between experimental conditions.

**Approach:** Load sample metadata and peak files into DiffBind, count reads in consensus peaks, normalize, define contrasts, and run differential analysis with DESeq2 backend.

```r
library(DiffBind)

# 1. Create sample sheet
samples <- data.frame(
    SampleID = c('ctrl_1', 'ctrl_2', 'treat_1', 'treat_2'),
    Condition = c('control', 'control', 'treated', 'treated'),
    Replicate = c(1, 2, 1, 2),
    bamReads = c('ctrl_1.bam', 'ctrl_2.bam', 'treat_1.bam', 'treat_2.bam'),
    Peaks = c('ctrl_1.narrowPeak', 'ctrl_2.narrowPeak', 'treat_1.narrowPeak', 'treat_2.narrowPeak')
)
write.csv(samples, 'samples.csv', row.names=FALSE)

# 2. Load data
dba <- dba(sampleSheet='samples.csv')

# 3. Count reads
dba <- dba.count(dba)

# 4. Normalize
dba <- dba.normalize(dba)

# 5. Set up contrasts
dba <- dba.contrast(dba, contrast=c('Condition', 'treated', 'control'))

# 6. Differential analysis
dba <- dba.analyze(dba)

# 7. Get results
results <- dba.report(dba)
```

## DiffBind with Consensus Peaks

```r
library(DiffBind)

# Load samples
dba <- dba(sampleSheet='samples.csv')

# Count with specific parameters
dba <- dba.count(dba,
    summits=250,           # Re-center peaks on summit
    minOverlap=2,          # Peak in at least 2 samples
    score=DBA_SCORE_NORMALIZED)

# Normalize
dba <- dba.normalize(dba, normalize=DBA_NORM_NATIVE)

# Analyze
dba <- dba.contrast(dba, contrast=c('Condition', 'treated', 'control'))
dba <- dba.analyze(dba, method=DBA_DESEQ2)

# Extract results
results <- dba.report(dba, th=0.05, bCounts=TRUE)

# Save
write.csv(as.data.frame(results), 'differential_peaks.csv')
```

## DiffBind Visualizations

```r
# PCA plot
dba.plotPCA(dba, attributes=DBA_CONDITION)

# MA plot
dba.plotMA(dba)

# Volcano plot
dba.plotVolcano(dba)

# Heatmap of differential peaks
dba.plotHeatmap(dba, contrast=1, correlations=FALSE)

# Venn diagram of overlapping peaks
dba.plotVenn(dba, contrast=1, bDB=TRUE, bGain=TRUE, bLoss=TRUE)
```

## Using DESeq2 Directly

**Goal:** Run differential accessibility analysis using DESeq2 on a peak count matrix without DiffBind.

**Approach:** Load peak-by-sample counts into a DESeqDataSet, filter low counts, run the DESeq2 pipeline, and extract significant differential peaks.

```r
library(DESeq2)
library(GenomicRanges)

# Load peak counts (from featureCounts or custom counting)
counts <- read.delim('peak_counts.txt', row.names=1)

# Sample metadata
coldata <- data.frame(
    row.names = colnames(counts),
    condition = factor(c('control', 'control', 'treated', 'treated'))
)

# Create DESeq object
dds <- DESeqDataSetFromMatrix(countData=counts, colData=coldata, design=~condition)

# Filter low counts
dds <- dds[rowSums(counts(dds)) >= 10, ]

# Run DESeq2
dds <- DESeq(dds)

# Results
res <- results(dds, contrast=c('condition', 'treated', 'control'))
res <- res[order(res$padj), ]

# Significant peaks
sig <- subset(res, padj < 0.05 & abs(log2FoldChange) > 1)
```

## Count Reads in Peaks

**Goal:** Generate a peak-by-sample count matrix as input for differential analysis.

**Approach:** Convert consensus peaks to SAF format and run featureCounts to count reads from all BAM files in each peak region.

```bash
# Using featureCounts
# First convert peaks to SAF format
awk 'BEGIN{OFS="\t"; print "GeneID\tChr\tStart\tEnd\tStrand"}
     {print $1"_"$2"_"$3, $1, $2, $3, "."}' consensus_peaks.bed > peaks.saf

featureCounts \
    -a peaks.saf \
    -F SAF \
    -o peak_counts.txt \
    -p \
    --countReadPairs \
    -T 8 \
    *.bam
```

## Python Alternative

```python
import pandas as pd
import numpy as np
from scipy import stats

def simple_differential(counts_file, groups):
    '''Simple differential accessibility test.'''
    counts = pd.read_csv(counts_file, sep='\t', index_col=0, comment='#')

    # Normalize to CPM
    cpm = counts.div(counts.sum()) * 1e6

    # Log transform
    log_cpm = np.log2(cpm + 1)

    # Separate groups
    group1 = [c for c in counts.columns if groups[c] == 'control']
    group2 = [c for c in counts.columns if groups[c] == 'treated']

    results = []
    for peak in counts.index:
        g1_vals = log_cpm.loc[peak, group1]
        g2_vals = log_cpm.loc[peak, group2]

        log2fc = g2_vals.mean() - g1_vals.mean()
        t_stat, pval = stats.ttest_ind(g1_vals, g2_vals)

        results.append({
            'peak': peak,
            'log2FoldChange': log2fc,
            'pvalue': pval
        })

    df = pd.DataFrame(results)
    df['padj'] = stats.false_discovery_control(df['pvalue'])

    return df
```

## Annotate Differential Peaks

**Goal:** Map differential peaks to nearby genes and genomic features for biological interpretation.

**Approach:** Use ChIPseeker to annotate peaks with promoter/intron/intergenic classification and distance to nearest TSS.

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

# Annotate differential peaks
diff_peaks <- dba.report(dba)
peakAnno <- annotatePeak(diff_peaks, TxDb=TxDb.Hsapiens.UCSC.hg38.knownGene)

# Plot annotation
plotAnnoPie(peakAnno)
plotDistToTSS(peakAnno)

# Get genes
genes <- as.data.frame(peakAnno)$geneId
```

## Filter Results

```r
# Get significant results
sig_peaks <- dba.report(dba, th=0.05, fold=1)

# Opened in treatment
opened <- sig_peaks[sig_peaks$Fold > 0]

# Closed in treatment
closed <- sig_peaks[sig_peaks$Fold < 0]

# Export as BED
export.bed(opened, 'opened_peaks.bed')
export.bed(closed, 'closed_peaks.bed')
```

## Multi-factor Designs

```r
# Complex design with batch correction
samples$Batch <- factor(c('A', 'B', 'A', 'B'))

dba <- dba(sampleSheet=samples)
dba <- dba.count(dba)
dba <- dba.normalize(dba)

# Design formula approach
dba <- dba.contrast(dba, design='~Batch + Condition')
dba <- dba.analyze(dba)
```

## Related Skills

- atac-seq/atac-peak-calling - Generate input peaks
- differential-expression/deseq2-basics - DESeq2 methods
- chip-seq/differential-binding - Similar DiffBind workflow
- pathway-analysis/go-enrichment - Analyze differential genes
