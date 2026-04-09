# bio-workflows-smrna-pipeline

> End-to-end small RNA-seq analysis from FASTQ to differential miRNA expression. Use when analyzing miRNA, piRNA, or other small RNA sequencing data.

**Available tools:** Read, Bash

# Small RNA-seq Pipeline

## Pipeline Overview

```
FASTQ → cutadapt trim → miRDeep2 → Quantification → DESeq2 → Target prediction
```

## Step 1: Preprocessing

```bash
# Adapter trimming and size selection
cutadapt -a TGGAATTCTCGGGTGCCAAGG \
    --minimum-length 18 --maximum-length 30 \
    -o trimmed.fastq.gz reads.fastq.gz
```

## Step 2: miRDeep2 Analysis

```bash
# Align to genome
mapper.pl trimmed.fastq.gz -e -h -i -j -l 18 \
    -m -p genome_index -s reads_collapsed.fa \
    -t reads_collapsed_vs_genome.arf

# miRNA quantification and novel prediction
miRDeep2.pl reads_collapsed.fa genome.fa \
    reads_collapsed_vs_genome.arf \
    mature_ref.fa none hairpin_ref.fa
```

## Step 3: Differential Expression

```r
library(DESeq2)
counts <- read.csv('mirna_counts.csv', row.names = 1)
dds <- DESeqDataSetFromMatrix(counts, colData, ~condition)
dds <- DESeq(dds)
results <- results(dds)
```

## Step 4: Target Prediction

```bash
# miRanda for target prediction
miranda mature_mirnas.fa target_3utrs.fa -out targets.txt
```

## QC Checkpoints

1. **After trimming**: Size distribution should peak at 21-23nt
2. **After alignment**: >70% mapping rate expected
3. **After DE**: Check volcano plot and PCA

## Related Skills

- small-rna-seq/mirdeep2-analysis - Detailed miRDeep2
- small-rna-seq/differential-mirna - DE analysis
- small-rna-seq/target-prediction - Target analysis
