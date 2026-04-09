# bio-workflows-clip-pipeline

> End-to-end CLIP-seq analysis from FASTQ to binding sites and motif enrichment. Use when analyzing protein-RNA interactions from CLIP-based methods.

**Available tools:** Read, Bash

# CLIP-seq Pipeline

## Pipeline Overview

```
FASTQ → QC → UMI extract → Trim adapters → Align → Filter → Dedup → Peak call → Annotate → Motifs
```

## CLIP Method Variants

| Method | UMI | Crosslink Site | Adapter |
|--------|-----|----------------|---------|
| HITS-CLIP | Optional | Deletions | 3' adapter |
| PAR-CLIP | Optional | T→C mutations | 3' adapter |
| iCLIP | Required | 5' of read | 3' adapter |
| eCLIP | Required | 5' of read | 3' adapter |

## Step 1: Quality Control

```bash
# Initial QC
fastqc reads.fastq.gz -o qc_pre/

# Check for adapter contamination and UMI structure
# For eCLIP: expect 10nt UMI at read start
zcat reads.fastq.gz | head -n 100 | cut -c1-15
```

## Step 2: UMI Extraction

```bash
# eCLIP (10nt UMI at 5' end)
umi_tools extract \
    --stdin=reads.fastq.gz \
    --bc-pattern=NNNNNNNNNN \
    --stdout=extracted.fastq.gz \
    --log=umi_extract.log

# iCLIP (5nt experimental barcode + 5nt UMI)
umi_tools extract \
    --stdin=reads.fastq.gz \
    --bc-pattern=NNNNNXXXXX \
    --stdout=extracted.fastq.gz
```

## Step 3: Adapter Trimming

```bash
# Trim 3' adapter (common eCLIP adapter)
cutadapt -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA \
    --minimum-length 20 \
    --quality-cutoff 20 \
    -o trimmed.fastq.gz \
    extracted.fastq.gz

# For paired UMI adapters
cutadapt -a AGATCGGAAGAGCACACGTCT \
    -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
    --minimum-length 20 \
    -o trimmed_R1.fq.gz -p trimmed_R2.fq.gz \
    extracted_R1.fq.gz extracted_R2.fq.gz
```

## Step 4: Alignment

```bash
# Build STAR index (once)
STAR --runMode genomeGenerate \
    --genomeDir star_index \
    --genomeFastaFiles genome.fa \
    --sjdbGTFfile genes.gtf \
    --sjdbOverhang 100

# Align with STAR (optimized for short CLIP reads)
STAR --genomeDir star_index \
    --readFilesIn trimmed.fastq.gz \
    --readFilesCommand zcat \
    --outFilterMismatchNmax 2 \
    --outFilterMultimapNmax 1 \
    --outSAMtype BAM SortedByCoordinate \
    --outSAMattributes All \
    --alignEndsType EndToEnd \
    --outFileNamePrefix clip_
```

## Step 5: Alignment Filtering

```bash
# Remove unmapped and low-quality reads
samtools view -b -F 4 -q 10 clip_Aligned.sortedByCoord.out.bam > filtered.bam
samtools index filtered.bam

# Optional: remove reads mapping to rRNA/tRNA
bedtools intersect -v -abam filtered.bam -b rrna_trna.bed > filtered_norRNA.bam
```

## Step 6: PCR Deduplication

```bash
# UMI-aware deduplication
umi_tools dedup \
    -I filtered.bam \
    -S dedup.bam \
    --output-stats=dedup_stats

samtools index dedup.bam

# Check deduplication rate
echo "Duplication rate:" $(grep "Input Reads" dedup_stats.log | awk '{print $3}')
```

## Step 7: Peak Calling

```bash
# CLIPper (recommended)
clipper -b dedup.bam -s hg38 -o peaks.bed --FDR 0.05 --superlocal

# Alternative: Piranha
Piranha -s dedup.bam -o piranha_peaks.bed -p 0.01

# For PAR-CLIP with T→C mutations
PARalyzer settings.ini

# Strand-specific calling
samtools view -h -F 16 dedup.bam | samtools view -Sb - > plus.bam
samtools view -h -f 16 dedup.bam | samtools view -Sb - > minus.bam
clipper -b plus.bam -s hg38 -o peaks_plus.bed
clipper -b minus.bam -s hg38 -o peaks_minus.bed
cat peaks_plus.bed peaks_minus.bed | sort -k1,1 -k2,2n > peaks_stranded.bed
```

## Step 8: Peak Annotation

```bash
# Annotate with gene features
bedtools intersect -a peaks.bed -b genes.gtf -wo > peaks_annotated.txt

# Or use HOMER
annotatePeaks.pl peaks.bed hg38 > peaks_homer_annotated.txt

# Feature distribution
awk -F'\t' '{print $8}' peaks_homer_annotated.txt | sort | uniq -c | sort -rn
```

## Step 9: Motif Analysis

```bash
# Extract peak sequences
bedtools getfasta -fi genome.fa -bed peaks.bed -s -fo peaks.fa

# HOMER motif finding (RNA mode)
findMotifs.pl peaks.fa fasta motif_output -rna -len 5,6,7,8 -p 8

# MEME-ChIP
meme-chip -oc meme_output -dna peaks.fa -meme-mod zoops -meme-nmotifs 10
```

## Step 10: Cross-link Site Analysis

```bash
# For iCLIP/eCLIP: identify crosslink sites (read 5' ends)
bedtools genomecov -ibam dedup.bam -bg -5 -strand + > crosslinks_plus.bg
bedtools genomecov -ibam dedup.bam -bg -5 -strand - > crosslinks_minus.bg

# For PAR-CLIP: identify T→C conversion sites
# Requires specialized tools like PARpipe
```

## Quality Checkpoints

| Step | Metric | Expected |
|------|--------|----------|
| Raw | Read count | >10M |
| Trimmed | Reads >20bp | >80% |
| Aligned | Mapping rate | >50% |
| Dedup | Unique rate | >20% |
| Peaks | Peak count | 1,000-50,000 |
| Peaks | Median width | 20-100 nt |
| FRiP | Reads in peaks | >10% |

```bash
# Calculate FRiP
reads_in_peaks=$(bedtools intersect -a dedup.bam -b peaks.bed -u | samtools view -c -)
total_reads=$(samtools view -c dedup.bam)
frip=$(echo "scale=4; $reads_in_peaks / $total_reads" | bc)
echo "FRiP: $frip"
```

## Complete Pipeline Script

```bash
#!/bin/bash
set -euo pipefail

SAMPLE=$1
READS=$2
GENOME_DIR=$3
GENOME_FA=$4

mkdir -p qc trimmed aligned peaks motifs

# QC
fastqc $READS -o qc/

# UMI extract
umi_tools extract --stdin=$READS --bc-pattern=NNNNNNNNNN \
    --stdout=trimmed/${SAMPLE}_extracted.fq.gz

# Trim
cutadapt -a AGATCGGAAGAGCACACGTCT --minimum-length 20 \
    -o trimmed/${SAMPLE}_trimmed.fq.gz trimmed/${SAMPLE}_extracted.fq.gz

# Align
STAR --genomeDir $GENOME_DIR --readFilesIn trimmed/${SAMPLE}_trimmed.fq.gz \
    --readFilesCommand zcat --outFilterMismatchNmax 2 --outFilterMultimapNmax 1 \
    --outSAMtype BAM SortedByCoordinate --outFileNamePrefix aligned/${SAMPLE}_

# Filter and dedup
samtools view -b -F 4 -q 10 aligned/${SAMPLE}_Aligned.sortedByCoord.out.bam | \
    samtools sort -o aligned/${SAMPLE}_filtered.bam
samtools index aligned/${SAMPLE}_filtered.bam
umi_tools dedup -I aligned/${SAMPLE}_filtered.bam -S aligned/${SAMPLE}_dedup.bam
samtools index aligned/${SAMPLE}_dedup.bam

# Peaks
clipper -b aligned/${SAMPLE}_dedup.bam -s hg38 -o peaks/${SAMPLE}_peaks.bed

# Motifs
bedtools getfasta -fi $GENOME_FA -bed peaks/${SAMPLE}_peaks.bed -s -fo peaks/${SAMPLE}.fa
findMotifs.pl peaks/${SAMPLE}.fa fasta motifs/${SAMPLE} -rna -len 5,6,7 -p 4

echo "Pipeline complete for $SAMPLE"
```

## Related Skills

- clip-seq/clip-preprocessing - Detailed preprocessing
- clip-seq/clip-alignment - Alignment optimization
- clip-seq/clip-peak-calling - Peak caller comparison
- clip-seq/binding-site-annotation - Feature annotation
- clip-seq/clip-motif-analysis - Motif discovery
