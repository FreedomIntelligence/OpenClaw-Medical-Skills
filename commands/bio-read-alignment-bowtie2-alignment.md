# bio-read-alignment-bowtie2-alignment

> Align short reads using Bowtie2 with local or end-to-end modes. Supports gapped alignment. Use when aligning ChIP-seq, ATAC-seq, or when flexible alignment modes are needed.

**Available tools:** Read, Bash

# Bowtie2 Alignment

## Build Index

```bash
# Build index from reference FASTA
bowtie2-build reference.fa reference_index

# With threads (faster)
bowtie2-build --threads 8 reference.fa reference_index

# Creates: reference_index.1.bt2, .2.bt2, .3.bt2, .4.bt2, .rev.1.bt2, .rev.2.bt2
```

## Basic Alignment

```bash
# Paired-end reads
bowtie2 -p 8 -x reference_index -1 reads_1.fq.gz -2 reads_2.fq.gz -S aligned.sam

# Single-end reads
bowtie2 -p 8 -x reference_index -U reads.fq.gz -S aligned.sam

# Direct to sorted BAM
bowtie2 -p 8 -x reference_index -1 r1.fq.gz -2 r2.fq.gz | \
    samtools sort -@ 4 -o aligned.sorted.bam -
```

## Alignment Modes

```bash
# End-to-end mode (default) - align entire read
bowtie2 --end-to-end -x index -1 r1.fq -2 r2.fq -S aligned.sam

# Local mode - soft-clip ends for better alignment
bowtie2 --local -x index -1 r1.fq -2 r2.fq -S aligned.sam
```

## Sensitivity Presets

```bash
# Very fast (less sensitive)
bowtie2 --very-fast -x index -1 r1.fq -2 r2.fq -S aligned.sam

# Fast
bowtie2 --fast -x index -1 r1.fq -2 r2.fq -S aligned.sam

# Sensitive (default)
bowtie2 --sensitive -x index -1 r1.fq -2 r2.fq -S aligned.sam

# Very sensitive (slower but more accurate)
bowtie2 --very-sensitive -x index -1 r1.fq -2 r2.fq -S aligned.sam

# Local mode equivalents
bowtie2 --very-sensitive-local -x index -1 r1.fq -2 r2.fq -S aligned.sam
```

## ChIP-seq Alignment

```bash
# Typical ChIP-seq settings
bowtie2 -p 8 \
    --very-sensitive \
    --no-mixed \
    --no-discordant \
    -x index -1 chip_1.fq.gz -2 chip_2.fq.gz | \
    samtools view -bS -q 30 -F 4 - | \
    samtools sort -o chip.sorted.bam -
```

## ATAC-seq Alignment

```bash
# ATAC-seq with size selection
bowtie2 -p 8 \
    --very-sensitive \
    -X 2000 \                    # Max fragment length
    --no-mixed \
    --no-discordant \
    -x index -1 atac_1.fq.gz -2 atac_2.fq.gz | \
    samtools view -bS -q 30 - | \
    samtools sort -o atac.sorted.bam -
```

## Fragment Size Options

```bash
# Set expected insert size range
bowtie2 -p 8 \
    -I 100 \     # Minimum fragment length
    -X 500 \     # Maximum fragment length
    -x index -1 r1.fq -2 r2.fq -S aligned.sam
```

## Read Group and Output Options

```bash
# Add read group
bowtie2 -p 8 \
    --rg-id sample1 \
    --rg SM:sample1 \
    --rg PL:ILLUMINA \
    --rg LB:lib1 \
    -x index -1 r1.fq -2 r2.fq -S aligned.sam
```

## Multi-mapping Reads

```bash
# Report up to k alignments per read
bowtie2 -k 5 -x index -1 r1.fq -2 r2.fq -S aligned.sam

# Report all alignments
bowtie2 -a -x index -1 r1.fq -2 r2.fq -S aligned.sam
```

## Output Unmapped Reads

```bash
# Write unmapped reads to separate files
bowtie2 -p 8 \
    --un-conc-gz unmapped_%.fq.gz \
    -x index -1 r1.fq.gz -2 r2.fq.gz -S aligned.sam
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| -p | 1 | Number of threads |
| -x | - | Index basename |
| -1/-2 | - | Paired-end reads |
| -U | - | Single-end reads |
| -I | 0 | Min fragment length |
| -X | 500 | Max fragment length |
| -k | 1 | Report up to k alignments |
| --no-mixed | off | Suppress unpaired alignments |
| --no-discordant | off | Suppress discordant alignments |

## Alignment Statistics

```bash
# Bowtie2 prints alignment summary to stderr
bowtie2 -p 8 -x index -1 r1.fq -2 r2.fq -S aligned.sam 2> alignment_stats.txt
```

Example output:
```
1000000 reads; of these:
  1000000 (100.00%) were paired; of these:
    50000 (5.00%) aligned concordantly 0 times
    900000 (90.00%) aligned concordantly exactly 1 time
    50000 (5.00%) aligned concordantly >1 times
95.00% overall alignment rate
```

## Related Skills

- read-qc/fastp-workflow - Preprocess reads before alignment
- alignment-files/alignment-sorting - Post-alignment processing
- chip-seq/peak-calling - ChIP-seq analysis
- atac-seq/atac-peak-calling - ATAC-seq analysis
