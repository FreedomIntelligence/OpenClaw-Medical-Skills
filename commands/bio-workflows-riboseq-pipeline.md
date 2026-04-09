# bio-workflows-riboseq-pipeline

> End-to-end Ribo-seq analysis from FASTQ to translation efficiency and ORF detection. Use when analyzing ribosome profiling data to study translation.

**Available tools:** Read, Bash

# Ribo-seq Pipeline

## Pipeline Overview

```
FASTQ → Preprocessing → rRNA removal → Alignment → P-site → TE → ORF calling
```

## Step 1: Preprocessing

```bash
# Remove adapters
cutadapt -a CTGTAGGCACCATCAAT \
    --minimum-length 25 --maximum-length 35 \
    -o trimmed.fastq.gz reads.fastq.gz

# Remove rRNA
bowtie2 -x rRNA_index --un non_rrna.fastq.gz -U trimmed.fastq.gz
```

## Step 2: Alignment

```bash
# Align to transcriptome
STAR --genomeDir star_index \
    --readFilesIn non_rrna.fastq.gz \
    --readFilesCommand zcat \
    --outFilterMismatchNmax 2 \
    --alignEndsType EndToEnd \
    --outSAMtype BAM SortedByCoordinate
```

## Step 3: P-site Calibration

```python
from plastid import BAMGenomeArray

# Build metagene profile
metagene_generate annotation.gtf ribo.bam metagene_output/

# Calculate P-site offsets
psite annotation.gtf metagene_output/profile.txt psite_offsets.txt
```

## Step 4: Translation Efficiency

```python
# TE = Ribo-seq RPKM / RNA-seq RPKM
from plastid import BAMGenomeArray
import numpy as np

ribo_counts = count_reads(ribo_bam, genes)
rna_counts = count_reads(rna_bam, genes)
te = ribo_counts / rna_counts
```

## Step 5: ORF Detection

```bash
# RiboCode for ORF calling
RiboCode -a annotation.gtf -c config.txt -o ribocoded_orfs
```

## Related Skills

- ribo-seq/ - Individual Ribo-seq analysis skills
- differential-expression - For differential TE
