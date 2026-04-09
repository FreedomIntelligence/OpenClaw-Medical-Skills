# bio-workflows-merip-pipeline

> End-to-end MeRIP-seq analysis from FASTQ to m6A peaks and differential methylation. Use when analyzing epitranscriptomic m6A modifications from immunoprecipitation data.

**Available tools:** Read, Bash

# MeRIP-seq Pipeline

## Pipeline Overview

```
FASTQ → QC → Align IP+Input → Peak calling → Annotation → Differential → Visualization
```

## Step 1: Quality Control

```bash
fastp -i IP_R1.fq.gz -I IP_R2.fq.gz \
    -o IP_R1_trimmed.fq.gz -O IP_R2_trimmed.fq.gz \
    --json IP_fastp.json --html IP_fastp.html

fastp -i Input_R1.fq.gz -I Input_R2.fq.gz \
    -o Input_R1_trimmed.fq.gz -O Input_R2_trimmed.fq.gz \
    --json Input_fastp.json --html Input_fastp.html
```

## Step 2: Alignment

```bash
STAR --genomeDir star_index \
    --readFilesIn IP_R1_trimmed.fq.gz IP_R2_trimmed.fq.gz \
    --readFilesCommand zcat \
    --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix IP_

STAR --genomeDir star_index \
    --readFilesIn Input_R1_trimmed.fq.gz Input_R2_trimmed.fq.gz \
    --readFilesCommand zcat \
    --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix Input_

samtools index IP_Aligned.sortedByCoord.out.bam
samtools index Input_Aligned.sortedByCoord.out.bam
```

## Step 3: Peak Calling with exomePeak2

```r
library(exomePeak2)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

result <- exomePeak2(
    bam_ip = c('IP_rep1.bam', 'IP_rep2.bam'),
    bam_input = c('Input_rep1.bam', 'Input_rep2.bam'),
    txdb = TxDb.Hsapiens.UCSC.hg38.knownGene,
    genome = 'hg38'
)

peaks <- exomePeaks(result)
exportResults(result, format = 'BED', file = 'm6a_peaks.bed')
```

## Step 4: Alternative Peak Calling with MACS3

```bash
macs3 callpeak -t IP.bam -c Input.bam \
    -f BAM -g hs -n m6a \
    --nomodel --extsize 150 \
    -q 0.05 --keep-dup all

macs3 bdgdiff --t1 IP_treat_pileup.bdg --c1 IP_control_lambda.bdg \
    --t2 Input_treat_pileup.bdg --c2 Input_control_lambda.bdg \
    --outdir diff_peaks -o diff
```

## Step 5: Motif Analysis

```bash
findMotifsGenome.pl m6a_peaks.bed hg38 motif_output/ -size 100 -S 5

bedtools getfasta -fi genome.fa -bed m6a_peaks.bed -fo peak_sequences.fa
homer2 known -i peak_sequences.fa -m DRACH.motif -o motif_scan.txt
```

## Step 6: Differential Methylation

```r
library(exomePeak2)

ip_bams <- c('ctrl_IP_1.bam', 'ctrl_IP_2.bam', 'treat_IP_1.bam', 'treat_IP_2.bam')
input_bams <- c('ctrl_Input_1.bam', 'ctrl_Input_2.bam', 'treat_Input_1.bam', 'treat_Input_2.bam')

design <- data.frame(
    condition = factor(c('ctrl', 'ctrl', 'treat', 'treat')),
    row.names = c('ctrl_1', 'ctrl_2', 'treat_1', 'treat_2')
)

diff_result <- exomePeak2(
    bam_ip = ip_bams,
    bam_input = input_bams,
    txdb = TxDb.Hsapiens.UCSC.hg38.knownGene,
    experiment_design = design,
    test_method = 'DESeq2'
)

diff_peaks <- results(diff_result)
sig_peaks <- diff_peaks[diff_peaks$padj < 0.05, ]
```

## Step 7: Peak Annotation

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

peaks_gr <- import('m6a_peaks.bed')
anno <- annotatePeak(peaks_gr, TxDb = TxDb.Hsapiens.UCSC.hg38.knownGene)
plotAnnoBar(anno)
plotDistToTSS(anno)
```

## Step 8: Metagene Visualization

```r
library(Guitar)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

peaks_gr <- import('m6a_peaks.bed')
GuitarPlot(
    peaks_gr,
    txdb = TxDb.Hsapiens.UCSC.hg38.knownGene,
    saveToPDFprefix = 'm6a_metagene'
)
```

## Complete Bash Pipeline

```bash
#!/bin/bash
set -euo pipefail

GENOME_DIR=$1
GTF=$2
IP_R1=$3
IP_R2=$4
INPUT_R1=$5
INPUT_R2=$6
OUTPUT_DIR=$7

mkdir -p $OUTPUT_DIR/{qc,aligned,peaks,motifs}

echo "=== Step 1: QC ==="
fastp -i $IP_R1 -I $IP_R2 -o $OUTPUT_DIR/qc/IP_R1.fq.gz -O $OUTPUT_DIR/qc/IP_R2.fq.gz
fastp -i $INPUT_R1 -I $INPUT_R2 -o $OUTPUT_DIR/qc/Input_R1.fq.gz -O $OUTPUT_DIR/qc/Input_R2.fq.gz

echo "=== Step 2: Align ==="
STAR --genomeDir $GENOME_DIR --readFilesIn $OUTPUT_DIR/qc/IP_R1.fq.gz $OUTPUT_DIR/qc/IP_R2.fq.gz \
    --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix $OUTPUT_DIR/aligned/IP_
STAR --genomeDir $GENOME_DIR --readFilesIn $OUTPUT_DIR/qc/Input_R1.fq.gz $OUTPUT_DIR/qc/Input_R2.fq.gz \
    --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix $OUTPUT_DIR/aligned/Input_

samtools index $OUTPUT_DIR/aligned/IP_Aligned.sortedByCoord.out.bam
samtools index $OUTPUT_DIR/aligned/Input_Aligned.sortedByCoord.out.bam

echo "=== Step 3: Peak calling ==="
macs3 callpeak -t $OUTPUT_DIR/aligned/IP_Aligned.sortedByCoord.out.bam \
    -c $OUTPUT_DIR/aligned/Input_Aligned.sortedByCoord.out.bam \
    -f BAM -g hs -n m6a -q 0.05 --keep-dup all --nomodel --extsize 150 \
    --outdir $OUTPUT_DIR/peaks

echo "=== Complete ==="
```

## QC Checkpoints

| Checkpoint | Expected | Action if Failed |
|------------|----------|------------------|
| IP/Input alignment rate | >80% | Check adapter contamination |
| IP/Input correlation | r < 0.8 | Verify IP enrichment |
| Peak count | 10,000-50,000 | Adjust -q threshold |
| DRACH motif in peaks | >50% | Check peak calling parameters |
| Stop codon enrichment | Clear peak | Confirm m6A signal |

## Output Files

| File | Description |
|------|-------------|
| `m6a_peaks.bed` | Called m6A peak locations |
| `m6a_peaks_annotated.txt` | Peaks with gene annotations |
| `diff_m6a.csv` | Differential methylation results |
| `metagene.pdf` | Peak distribution across transcripts |
| `motif_output/` | Enriched motifs (expect DRACH) |

## Related Skills

- epitranscriptomics/m6a-peak-calling - Detailed peak calling options
- epitranscriptomics/m6a-differential - Differential analysis methods
- epitranscriptomics/modification-visualization - Visualization techniques
- chip-seq/peak-calling - Similar IP-based peak calling concepts
