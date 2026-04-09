# bio-workflows-chipseq-pipeline

> End-to-end ChIP-seq workflow from FASTQ files to annotated peaks. Covers QC, alignment, peak calling with MACS3, and peak annotation with ChIPseeker. Use when processing ChIP-seq data from alignment through peak annotation.

**Available tools:** Read, Bash

# ChIP-seq Pipeline

Complete workflow from raw ChIP-seq FASTQ files to annotated peaks.

## Workflow Overview

```
FASTQ files (IP + Input)
    |
    v
[1. QC & Trimming] -----> fastp
    |
    v
[2. Alignment] ---------> Bowtie2
    |
    v
[3. BAM Processing] ----> sort, markdup, filter
    |
    v
[4. Peak Calling] ------> MACS3
    |
    v
[5. QC] ----------------> FRiP, fingerprint plots
    |
    v
[6. Annotation] --------> ChIPseeker
    |
    v
Annotated peaks + QC report
```

## Primary Path: Bowtie2 + MACS3 + ChIPseeker

### Step 1: Quality Control with fastp

```bash
# Process both IP and Input samples
for sample in IP_rep1 IP_rep2 Input_rep1 Input_rep2; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o trimmed/${sample}_R1.fq.gz -O trimmed/${sample}_R2.fq.gz \
        --detect_adapter_for_pe \
        --qualified_quality_phred 20 \
        --length_required 25 \
        --html qc/${sample}_fastp.html
done
```

### Step 2: Alignment with Bowtie2

```bash
# Build index (once)
bowtie2-build genome.fa bt2_index/genome

# Align
for sample in IP_rep1 IP_rep2 Input_rep1 Input_rep2; do
    bowtie2 -p 8 -x bt2_index/genome \
        -1 trimmed/${sample}_R1.fq.gz \
        -2 trimmed/${sample}_R2.fq.gz \
        --no-mixed --no-discordant \
        --maxins 1000 \
        2> aligned/${sample}.log | \
    samtools view -@ 4 -bS -q 30 - | \
    samtools sort -@ 4 -o aligned/${sample}.bam
done
```

**QC Checkpoint:** Check alignment rate
- Overall alignment >80%
- Unique mapping >70%

### Step 3: BAM Processing

```bash
for sample in IP_rep1 IP_rep2 Input_rep1 Input_rep2; do
    # Mark and remove duplicates
    samtools fixmate -m aligned/${sample}.bam - | \
    samtools sort - | \
    samtools markdup -r - aligned/${sample}.dedup.bam

    # Index
    samtools index aligned/${sample}.dedup.bam

    # Remove chrM reads (high mitochondrial is common)
    samtools view -h aligned/${sample}.dedup.bam | \
        grep -v chrM | \
        samtools view -b - > aligned/${sample}.final.bam
    samtools index aligned/${sample}.final.bam
done
```

### Step 4: Peak Calling with MACS3

```bash
# Narrow peaks (TFs, sharp histone marks like H3K4me3)
macs3 callpeak \
    -t aligned/IP_rep1.final.bam aligned/IP_rep2.final.bam \
    -c aligned/Input_rep1.final.bam aligned/Input_rep2.final.bam \
    -f BAMPE \
    -g hs \
    -n experiment \
    --outdir peaks \
    -q 0.01

# Broad peaks (H3K27me3, H3K36me3)
macs3 callpeak \
    -t aligned/IP_rep1.final.bam aligned/IP_rep2.final.bam \
    -c aligned/Input_rep1.final.bam aligned/Input_rep2.final.bam \
    -f BAMPE \
    -g hs \
    -n experiment_broad \
    --outdir peaks \
    --broad \
    --broad-cutoff 0.1
```

### Step 5: QC Metrics

```bash
# Calculate FRiP (Fraction of Reads in Peaks)
total_reads=$(samtools view -c aligned/IP_rep1.final.bam)
reads_in_peaks=$(bedtools intersect -a aligned/IP_rep1.final.bam -b peaks/experiment_peaks.narrowPeak -u | samtools view -c)
frip=$(echo "scale=4; $reads_in_peaks / $total_reads" | bc)
echo "FRiP: $frip"

# Generate bigWig for visualization
bamCoverage -b aligned/IP_rep1.final.bam \
    -o bigwig/IP_rep1.bw \
    --normalizeUsing RPKM \
    -p 8

# Fingerprint plot (assess enrichment)
plotFingerprint \
    -b aligned/IP_rep1.final.bam aligned/Input_rep1.final.bam \
    --labels IP Input \
    -o qc/fingerprint.pdf
```

**QC Checkpoint:** Assess enrichment quality
- FRiP >1% (ideally >5% for good enrichment)
- Fingerprint shows clear separation between IP and Input

### Step 6: Peak Annotation with ChIPseeker

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)

txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

# Read peaks
peaks <- readPeakFile('peaks/experiment_peaks.narrowPeak')

# Annotate
peak_anno <- annotatePeak(peaks, TxDb = txdb, annoDb = 'org.Hs.eg.db',
                          tssRegion = c(-3000, 3000))

# Visualize
plotAnnoPie(peak_anno)
plotDistToTSS(peak_anno)

# Export
write.csv(as.data.frame(peak_anno), 'peaks/annotated_peaks.csv')

# Get genes with peaks in promoter
promoter_peaks <- as.data.frame(peak_anno)
promoter_genes <- unique(promoter_peaks$SYMBOL[grepl('Promoter', promoter_peaks$annotation)])
write.table(promoter_genes, 'peaks/promoter_genes.txt', row.names = FALSE, col.names = FALSE, quote = FALSE)
```

## Parameter Recommendations

| Step | Parameter | Narrow Peaks | Broad Peaks |
|------|-----------|--------------|-------------|
| MACS3 | --broad | No | Yes |
| MACS3 | -q | 0.01 | - |
| MACS3 | --broad-cutoff | - | 0.1 |
| MACS3 | -g | hs/mm/ce/dm | Same |
| Bowtie2 | -q (samtools) | 30 | 30 |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Few peaks | Low enrichment, wrong parameters | Check fingerprint, adjust -q threshold |
| Many peaks | High noise, PCR duplicates | Remove duplicates, use stricter -q |
| Low FRiP | Poor antibody, low enrichment | Check antibody, increase sequencing |
| Peaks in blacklist | Technical artifacts | Filter against ENCODE blacklist |

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

THREADS=8
GENOME="genome.fa"
INDEX="bt2_index/genome"
IP_SAMPLES="IP_rep1 IP_rep2"
INPUT_SAMPLES="Input_rep1 Input_rep2"
OUTDIR="results"

mkdir -p ${OUTDIR}/{trimmed,aligned,peaks,qc,bigwig}

# Step 1: QC
for sample in $IP_SAMPLES $INPUT_SAMPLES; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -O ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        --html ${OUTDIR}/qc/${sample}_fastp.html -w ${THREADS}
done

# Step 2-3: Align and process
for sample in $IP_SAMPLES $INPUT_SAMPLES; do
    bowtie2 -p ${THREADS} -x ${INDEX} \
        -1 ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -2 ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        --no-mixed --no-discordant 2> ${OUTDIR}/qc/${sample}_align.log | \
    samtools view -@ ${THREADS} -bS -q 30 - | \
    samtools fixmate -m - - | \
    samtools sort -@ ${THREADS} - | \
    samtools markdup -r - ${OUTDIR}/aligned/${sample}.bam
    samtools index ${OUTDIR}/aligned/${sample}.bam
done

# Step 4: Peak calling
ip_bams=$(for s in $IP_SAMPLES; do echo "${OUTDIR}/aligned/${s}.bam"; done | tr '\n' ' ')
input_bams=$(for s in $INPUT_SAMPLES; do echo "${OUTDIR}/aligned/${s}.bam"; done | tr '\n' ' ')

macs3 callpeak -t ${ip_bams} -c ${input_bams} \
    -f BAMPE -g hs -n experiment \
    --outdir ${OUTDIR}/peaks -q 0.01

echo "Pipeline complete. Peaks: ${OUTDIR}/peaks/experiment_peaks.narrowPeak"
```

## Related Skills

- chip-seq/peak-calling - MACS3 parameters and options
- chip-seq/peak-annotation - ChIPseeker annotation details
- chip-seq/differential-binding - Compare conditions with DiffBind
- chip-seq/chipseq-qc - Comprehensive QC metrics
- chip-seq/motif-analysis - Find enriched motifs in peaks
