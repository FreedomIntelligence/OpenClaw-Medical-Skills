# bio-workflows-methylation-pipeline

> End-to-end bisulfite sequencing workflow from FASTQ to differentially methylated regions. Covers Bismark alignment, methylation calling, and DMR detection with methylKit. Use when analyzing bisulfite sequencing data.

**Available tools:** Read, Bash

# Methylation Pipeline

Complete workflow from bisulfite sequencing FASTQ to differentially methylated regions.

## Workflow Overview

```
FASTQ files
    |
    v
[1. QC & Trimming] -----> fastp/Trim Galore
    |
    v
[2. Alignment] ---------> Bismark
    |
    v
[3. Deduplication] -----> deduplicate_bismark
    |
    v
[4. Methylation Calling] -> bismark_methylation_extractor
    |
    v
[5. Analysis] -----------> methylKit (R)
    |
    v
[6. DMR Detection] ------> methylKit/DSS
    |
    v
Differentially methylated regions
```

## Primary Path: Bismark + methylKit

### Step 1: Quality Control

```bash
# Trim Galore recommended for bisulfite data (handles adapter bias)
trim_galore --paired --fastqc \
    -o trimmed/ \
    sample_R1.fastq.gz sample_R2.fastq.gz

# Or fastp with conservative settings
fastp -i sample_R1.fastq.gz -I sample_R2.fastq.gz \
    -o trimmed/sample_R1.fq.gz -O trimmed/sample_R2.fq.gz \
    --detect_adapter_for_pe \
    --qualified_quality_phred 20 \
    --length_required 35 \
    --html qc/sample_fastp.html
```

### Step 2: Bismark Alignment

```bash
# Prepare genome (once)
bismark_genome_preparation --bowtie2 genome/

# Align
bismark --genome genome/ \
    -1 trimmed/sample_R1_val_1.fq.gz \
    -2 trimmed/sample_R2_val_2.fq.gz \
    -o aligned/ \
    --parallel 4 \
    --temp_dir tmp/

# Output: sample_R1_val_1_bismark_bt2_pe.bam
```

**QC Checkpoint:** Check Bismark report
- Mapping efficiency >50% (BS-seq has lower rates)
- Bisulfite conversion rate >99%

### Step 3: Deduplication

```bash
deduplicate_bismark \
    --bam \
    -p \
    -o deduplicated/ \
    aligned/sample_R1_val_1_bismark_bt2_pe.bam
```

### Step 4: Methylation Calling

```bash
bismark_methylation_extractor \
    --paired-end \
    --comprehensive \
    --bedGraph \
    --cytosine_report \
    --genome_folder genome/ \
    -o methylation/ \
    deduplicated/sample_R1_val_1_bismark_bt2_pe.deduplicated.bam

# Generate summary report
bismark2report
bismark2summary
```

### Step 5: Analysis with methylKit

```r
library(methylKit)

# Read methylation calls
files <- list(
    'methylation/control_1.CpG_report.txt',
    'methylation/control_2.CpG_report.txt',
    'methylation/treated_1.CpG_report.txt',
    'methylation/treated_2.CpG_report.txt'
)

sample_ids <- c('control_1', 'control_2', 'treated_1', 'treated_2')
treatment <- c(0, 0, 1, 1)

# Read cytosine reports
meth_obj <- methRead(
    location = as.list(files),
    sample.id = as.list(sample_ids),
    assembly = 'hg38',
    treatment = treatment,
    context = 'CpG',
    pipeline = 'bismarkCytosineReport'
)

# Filter by coverage
meth_filtered <- filterByCoverage(meth_obj, lo.count = 10, hi.perc = 99.9)

# Normalize coverage
meth_norm <- normalizeCoverage(meth_filtered)

# Merge samples (keep sites covered in all)
meth_merged <- unite(meth_norm, destrand = TRUE)

# Sample statistics
getMethylationStats(meth_obj[[1]], plot = TRUE)
getCoverageStats(meth_obj[[1]], plot = TRUE)
```

### Step 6: DMR Detection

```r
# Calculate differential methylation (per CpG)
diff_meth <- calculateDiffMeth(meth_merged)

# Get significant DMCs
dmc <- getMethylDiff(diff_meth, difference = 25, qvalue = 0.01)

# Tile into regions (DMRs)
tiles <- tileMethylCounts(meth_merged, win.size = 1000, step.size = 1000)
diff_tiles <- calculateDiffMeth(tiles)
dmr <- getMethylDiff(diff_tiles, difference = 25, qvalue = 0.01)

# Export
write.csv(as.data.frame(dmc), 'dmc_results.csv')
write.csv(as.data.frame(dmr), 'dmr_results.csv')

# Annotate with genomic features
library(genomation)
gene_obj <- readTranscriptFeatures('genes.bed')
annotateWithGeneParts(as(dmr, 'GRanges'), gene_obj)
```

## Parameter Recommendations

| Step | Parameter | Value |
|------|-----------|-------|
| Trim Galore | default | Recommended for BS-seq |
| Bismark | --parallel | 4 (per sample parallelization) |
| methylKit | lo.count | 10 (minimum coverage) |
| methylKit | difference | 25 (% methylation difference) |
| methylKit | qvalue | 0.01 |
| DMR tiles | win.size | 500-1000 bp |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Low mapping rate | Normal for BS-seq | Expect 40-70% |
| Low conversion | Failed bisulfite treatment | Check spike-in controls |
| Few DMRs | Low coverage, small differences | Increase sequencing, relax thresholds |
| Biased positions | M-bias | Trim 10bp from read ends |

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

THREADS=4
GENOME="genome/"
SAMPLES="control_1 control_2 treated_1 treated_2"
OUTDIR="methylation_results"

mkdir -p ${OUTDIR}/{trimmed,aligned,deduplicated,methylation,qc}

# Step 1: QC
for sample in $SAMPLES; do
    trim_galore --paired --fastqc -o ${OUTDIR}/trimmed/ \
        ${sample}_R1.fastq.gz ${sample}_R2.fastq.gz
done

# Step 2: Alignment
for sample in $SAMPLES; do
    bismark --genome ${GENOME} \
        -1 ${OUTDIR}/trimmed/${sample}_R1_val_1.fq.gz \
        -2 ${OUTDIR}/trimmed/${sample}_R2_val_2.fq.gz \
        -o ${OUTDIR}/aligned/ \
        --parallel ${THREADS} --temp_dir tmp/
done

# Step 3: Deduplication
for sample in $SAMPLES; do
    deduplicate_bismark --bam -p \
        -o ${OUTDIR}/deduplicated/ \
        ${OUTDIR}/aligned/${sample}_R1_val_1_bismark_bt2_pe.bam
done

# Step 4: Methylation calling
for sample in $SAMPLES; do
    bismark_methylation_extractor --paired-end --comprehensive \
        --bedGraph --cytosine_report \
        --genome_folder ${GENOME} \
        -o ${OUTDIR}/methylation/ \
        ${OUTDIR}/deduplicated/${sample}_R1_val_1_bismark_bt2_pe.deduplicated.bam
done

bismark2report
echo "Pipeline complete. Run R script for DMR analysis."
```

## Related Skills

- methylation-analysis/bismark-alignment - Bismark parameters
- methylation-analysis/methylation-calling - Calling details
- methylation-analysis/methylkit-analysis - methylKit functions
- methylation-analysis/dmr-detection - DMR algorithms
