# bio-epitranscriptomics-m6a-peak-calling

> Call m6A peaks from MeRIP-seq IP vs input comparisons. Use when identifying m6A modification sites from methylated RNA immunoprecipitation data.

**Available tools:** Read, Bash

# m6A Peak Calling

## exomePeak2 (Recommended)

```r
library(exomePeak2)

# Peak calling with biological replicates
result <- exomePeak2(
    bam_ip = c('IP_rep1.bam', 'IP_rep2.bam'),
    bam_input = c('Input_rep1.bam', 'Input_rep2.bam'),
    gff = 'genes.gtf',
    genome = 'hg38',
    paired_end = TRUE
)

# Export peaks
exportResults(result, format = 'BED')
```

## MACS3 Alternative

```bash
# Call peaks treating input as control
macs3 callpeak \
    -t IP_rep1.bam IP_rep2.bam \
    -c Input_rep1.bam Input_rep2.bam \
    -f BAMPE \
    -g hs \
    -n m6a_peaks \
    --nomodel \
    --extsize 150 \
    -q 0.05
```

## MeTPeak

```r
library(MeTPeak)

# GTF-aware peak calling
metpeak(
    IP_BAM = c('IP_rep1.bam', 'IP_rep2.bam'),
    INPUT_BAM = c('Input_rep1.bam', 'Input_rep2.bam'),
    GENE_ANNO_GTF = 'genes.gtf',
    OUTPUT_DIR = 'metpeak_output'
)
```

## Peak Filtering

```bash
# Filter by fold enrichment and q-value
# FC > 2, q < 0.05 typical thresholds
awk '$7 > 2 && $9 < 0.05' peaks.xls > filtered_peaks.bed
```

## Related Skills

- merip-preprocessing - Prepare data for peak calling
- m6a-differential - Compare peaks between conditions
- chip-seq/peak-calling - Similar concepts
