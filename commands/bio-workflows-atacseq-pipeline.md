# bio-workflows-atacseq-pipeline

> End-to-end ATAC-seq workflow from FASTQ files to differential accessibility and TF footprinting. Covers alignment, peak calling with MACS3, QC metrics, and optional TOBIAS footprinting. Use when running end-to-end ATAC-seq analysis from FASTQ to differential accessibility.

**Available tools:** Read, Bash

# ATAC-seq Pipeline

Complete workflow from raw ATAC-seq FASTQ files to accessibility peaks, differential analysis, and TF footprinting.

## Workflow Overview

```
FASTQ files
    |
    v
[1. QC & Trimming] -----> fastp (Nextera adapters)
    |
    v
[2. Alignment] ---------> Bowtie2
    |
    v
[3. BAM Processing] ----> filter, shift, dedup
    |
    v
[4. Peak Calling] ------> MACS3
    |
    v
[5. QC] ----------------> TSS enrichment, FRiP, fragment size
    |
    v
[6. Differential] ------> DiffBind (optional)
    |
    v
[7. Footprinting] ------> TOBIAS (optional)
    |
    v
Accessibility peaks + TF activity
```

## Primary Path: Bowtie2 + MACS3

### Step 1: Quality Control with fastp

```bash
# ATAC-seq uses Nextera adapters
NEXTERA_R1="CTGTCTCTTATACACATCT"
NEXTERA_R2="CTGTCTCTTATACACATCT"

for sample in sample1 sample2 sample3; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o trimmed/${sample}_R1.fq.gz -O trimmed/${sample}_R2.fq.gz \
        --adapter_sequence ${NEXTERA_R1} \
        --adapter_sequence_r2 ${NEXTERA_R2} \
        --qualified_quality_phred 20 \
        --length_required 25 \
        --html qc/${sample}_fastp.html
done
```

### Step 2: Alignment with Bowtie2

```bash
# Build index (once)
bowtie2-build genome.fa bt2_index/genome

# Align with ATAC-seq specific settings
for sample in sample1 sample2 sample3; do
    bowtie2 -p 8 -x bt2_index/genome \
        -1 trimmed/${sample}_R1.fq.gz \
        -2 trimmed/${sample}_R2.fq.gz \
        --very-sensitive \
        --no-mixed --no-discordant \
        -X 2000 \
        2> aligned/${sample}.log | \
    samtools view -@ 4 -bS -q 30 -f 2 - | \
    samtools sort -@ 4 -o aligned/${sample}.bam
done
```

### Step 3: BAM Processing

ATAC-seq requires special processing: removing mitochondrial reads, shifting reads for Tn5 insertion, and removing duplicates.

```bash
for sample in sample1 sample2 sample3; do
    # Remove mitochondrial reads
    samtools view -h aligned/${sample}.bam | \
        grep -v chrM | \
        samtools view -b - > aligned/${sample}.noMT.bam

    # Mark and remove duplicates
    samtools fixmate -m aligned/${sample}.noMT.bam - | \
    samtools sort - | \
    samtools markdup -r - aligned/${sample}.dedup.bam

    samtools index aligned/${sample}.dedup.bam

    # Shift reads for Tn5 (+ strand +4bp, - strand -5bp)
    alignmentSieve -b aligned/${sample}.dedup.bam \
        -o aligned/${sample}.shifted.bam \
        --ATACshift \
        -p 8

    samtools index aligned/${sample}.shifted.bam
done
```

Alternative manual Tn5 shift with bedtools:
```bash
# Convert to BED and shift
bedtools bamtobed -i aligned/${sample}.dedup.bam | \
    awk 'BEGIN{OFS="\t"} {if($6=="+"){$2=$2+4} else if($6=="-"){$3=$3-5} print}' | \
    sort -k1,1 -k2,2n > aligned/${sample}.shifted.bed
```

### Step 4: Peak Calling with MACS3

```bash
# Call peaks (use --shift and --extsize for shifted reads)
macs3 callpeak \
    -t aligned/sample1.shifted.bam \
    -f BAMPE \
    -g hs \
    -n sample1 \
    --outdir peaks \
    --nomodel \
    --shift -75 \
    --extsize 150 \
    --keep-dup all \
    -q 0.01

# For calling on all samples together
macs3 callpeak \
    -t aligned/*.shifted.bam \
    -f BAMPE \
    -g hs \
    -n consensus \
    --outdir peaks \
    --nomodel \
    --shift -75 \
    --extsize 150 \
    -q 0.01
```

### Step 5: ATAC-seq QC

```bash
# TSS enrichment (using deepTools)
computeMatrix reference-point \
    -S bigwig/sample1.bw \
    -R genes.bed \
    --referencePoint TSS \
    -a 2000 -b 2000 \
    -o tss_matrix.gz

plotProfile -m tss_matrix.gz -o qc/tss_enrichment.pdf

# Fragment size distribution
samtools view aligned/sample1.dedup.bam | \
    awk '{print sqrt($9^2)}' | \
    sort | uniq -c | \
    awk '{print $2"\t"$1}' > qc/fragment_sizes.txt

# FRiP calculation
total=$(samtools view -c aligned/sample1.shifted.bam)
in_peaks=$(bedtools intersect -a aligned/sample1.shifted.bam \
    -b peaks/sample1_peaks.narrowPeak -u | samtools view -c)
echo "FRiP: $(echo "scale=4; $in_peaks/$total" | bc)"
```

**QC Checkpoint:** Assess ATAC quality
- TSS enrichment score >5 (ideally >10)
- FRiP >20%
- Nucleosome-free (<100bp) and mono/di-nucleosome peaks visible

### Step 6: Differential Accessibility with DiffBind

```r
library(DiffBind)

# Create sample sheet
samples <- data.frame(
    SampleID = c('control_1', 'control_2', 'treated_1', 'treated_2'),
    Condition = c('control', 'control', 'treated', 'treated'),
    Replicate = c(1, 2, 1, 2),
    bamReads = c('aligned/control_1.shifted.bam', 'aligned/control_2.shifted.bam',
                 'aligned/treated_1.shifted.bam', 'aligned/treated_2.shifted.bam'),
    Peaks = c('peaks/control_1_peaks.narrowPeak', 'peaks/control_2_peaks.narrowPeak',
              'peaks/treated_1_peaks.narrowPeak', 'peaks/treated_2_peaks.narrowPeak')
)

# Create DBA object
dba <- dba(sampleSheet = samples)

# Count reads in peaks
dba <- dba.count(dba)

# Normalize
dba <- dba.normalize(dba)

# Contrast
dba <- dba.contrast(dba, categories = DBA_CONDITION)

# Differential analysis
dba <- dba.analyze(dba)

# Report
report <- dba.report(dba)
write.csv(as.data.frame(report), 'differential_peaks.csv')

# Visualization
dba.plotMA(dba)
dba.plotVolcano(dba)
```

### Step 7: TF Footprinting with TOBIAS

```bash
# Correct Tn5 bias
TOBIAS ATACorrect \
    -b aligned/sample1.shifted.bam \
    -g genome.fa \
    -p peaks/consensus_peaks.narrowPeak \
    --outdir footprinting \
    --cores 8

# Score footprints
TOBIAS ScoreBigwig \
    --signal footprinting/sample1_corrected.bw \
    --regions peaks/consensus_peaks.narrowPeak \
    --output footprinting/sample1_footprints.bw \
    --cores 8

# Bind detection
TOBIAS BINDetect \
    --motifs motifs.jaspar \
    --signals footprinting/sample1_footprints.bw \
    --genome genome.fa \
    --peaks peaks/consensus_peaks.narrowPeak \
    --outdir footprinting/bindetect \
    --cores 8

# Differential footprinting (two conditions)
TOBIAS BINDetect \
    --motifs motifs.jaspar \
    --signals footprinting/control_footprints.bw footprinting/treated_footprints.bw \
    --genome genome.fa \
    --peaks peaks/consensus_peaks.narrowPeak \
    --outdir footprinting/differential \
    --cores 8
```

## Parameter Recommendations

| Step | Parameter | Value |
|------|-----------|-------|
| fastp | adapter | Nextera (CTGTCTCTTATACACATCT) |
| Bowtie2 | -X | 2000 (max insert size) |
| samtools | -q | 30 (MAPQ filter) |
| MACS3 | --shift | -75 (for Tn5 shift) |
| MACS3 | --extsize | 150 |
| MACS3 | -q | 0.01-0.05 |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| High mitochondrial | Normal for ATAC | Filter chrM reads |
| Low TSS enrichment | Poor library, overdigestion | Check Tn5 concentration |
| Many small peaks | Tn5 insertion noise | Increase -q threshold |
| No nucleosome periodicity | Overdigestion | Adjust Tn5:DNA ratio |

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

THREADS=8
INDEX="bt2_index/genome"
GENOME="genome.fa"
SAMPLES="sample1 sample2 sample3"
OUTDIR="atac_results"

mkdir -p ${OUTDIR}/{trimmed,aligned,peaks,qc,bigwig}

# Step 1: QC
for sample in $SAMPLES; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -O ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        --adapter_sequence CTGTCTCTTATACACATCT \
        --html ${OUTDIR}/qc/${sample}_fastp.html -w ${THREADS}
done

# Step 2-3: Align and process
for sample in $SAMPLES; do
    bowtie2 -p ${THREADS} -x ${INDEX} \
        -1 ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -2 ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        --very-sensitive --no-mixed --no-discordant -X 2000 \
        2> ${OUTDIR}/qc/${sample}_bowtie2.log | \
    samtools view -@ ${THREADS} -bS -q 30 -f 2 - | \
    grep -v chrM | \
    samtools fixmate -m - - | \
    samtools sort -@ ${THREADS} - | \
    samtools markdup -r - - | \
    alignmentSieve --ATACshift -b /dev/stdin -o ${OUTDIR}/aligned/${sample}.bam
    samtools index ${OUTDIR}/aligned/${sample}.bam
done

# Step 4: Peak calling
macs3 callpeak -t ${OUTDIR}/aligned/*.bam -f BAMPE -g hs \
    -n consensus --outdir ${OUTDIR}/peaks \
    --nomodel --shift -75 --extsize 150 -q 0.01

echo "Pipeline complete. Peaks: ${OUTDIR}/peaks/consensus_peaks.narrowPeak"
```

## Related Skills

- atac-seq/atac-peak-calling - MACS3 ATAC parameters
- atac-seq/atac-qc - TSS enrichment, FRiP details
- atac-seq/differential-accessibility - DiffBind for ATAC
- atac-seq/footprinting - TOBIAS and HINT details
- chip-seq/peak-annotation - Annotate ATAC peaks to genes
