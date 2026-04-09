# bio-ribo-seq-riboseq-preprocessing

> Preprocess ribosome profiling data including adapter trimming, size selection, rRNA removal, and alignment. Use when preparing Ribo-seq reads for downstream analysis of translation.

## Version Compatibility

Reference examples tested with: Bowtie2 2.5.3+, STAR 2.7.11+, cutadapt 4.4+, numpy 1.26+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Ribo-seq Preprocessing

**"Preprocess my ribosome profiling data"** → Trim adapters, size-select ribosome-protected fragments (26-34 nt), remove rRNA contamination, and align to the transcriptome for translation analysis.
- CLI: `cutadapt` → `bowtie2` (rRNA removal) → `STAR` (genome alignment)

## Workflow Overview

```
Raw Ribo-seq FASTQ
    |
    v
Adapter trimming (cutadapt)
    |
    v
Size selection (25-35 nt typical)
    |
    v
rRNA removal (SortMeRNA/bowtie2)
    |
    v
Alignment to transcriptome
    |
    v
Quality filtered BAM
```

## Adapter Trimming

**Goal:** Remove 3' adapter sequences from ribosome footprint reads to recover the true insert.

**Approach:** Run cutadapt with the known adapter sequence and length filters to discard fragments outside the expected footprint range.

```bash
# Trim 3' adapter
cutadapt \
    -a CTGTAGGCACCATCAAT \
    -m 20 \
    -M 40 \
    -o trimmed.fastq.gz \
    input.fastq.gz
```

## Size Selection

**Goal:** Retain only reads corresponding to ribosome-protected fragments (typically 28-32 nt).

**Approach:** Apply minimum and maximum length filters with cutadapt to select the footprint size range.

```bash
# Select ribosome footprint size range
# Typical: 28-32 nt (protected by ribosome)
cutadapt \
    -m 28 \
    -M 32 \
    -o size_selected.fastq.gz \
    trimmed.fastq.gz
```

## rRNA Removal

**Goal:** Deplete ribosomal RNA reads that typically constitute the majority of a Ribo-seq library.

**Approach:** Align reads against rRNA reference databases using SortMeRNA or Bowtie2 and collect only unmapped (non-rRNA) reads.

```bash
# Option 1: SortMeRNA (comprehensive)
sortmerna \
    --ref rRNA_databases/silva-bac-16s-id90.fasta \
    --ref rRNA_databases/silva-euk-18s-id95.fasta \
    --ref rRNA_databases/silva-euk-28s-id98.fasta \
    --reads size_selected.fastq.gz \
    --aligned rRNA_reads \
    --other non_rRNA_reads \
    --fastx \
    --threads 8

# Option 2: Bowtie2 to rRNA index
bowtie2 -x rRNA_index \
    -U size_selected.fastq.gz \
    --un non_rRNA.fastq.gz \
    -S /dev/null \
    -p 8
```

## Alignment to Transcriptome

**Goal:** Map cleaned ribosome footprint reads to the genome or transcriptome for positional analysis.

**Approach:** Align with STAR (spliced) or Bowtie2 (transcriptome) using stringent filters for uniquely mapped reads with few mismatches.

```bash
# STAR alignment (spliced)
STAR --runMode alignReads \
    --genomeDir STAR_index \
    --readFilesIn non_rRNA.fastq.gz \
    --readFilesCommand zcat \
    --outFilterMultimapNmax 1 \
    --outFilterMismatchNmax 2 \
    --alignIntronMax 1 \
    --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix riboseq_

# Or bowtie2 to transcriptome
bowtie2 -x transcriptome_index \
    -U non_rRNA.fastq.gz \
    -S aligned.sam \
    --no-unal \
    -p 8
```

## Quality Metrics

**Goal:** Assess preprocessing success by checking read length distribution and mapping rates.

**Approach:** Extract read lengths from the aligned BAM and run samtools flagstat to verify expected footprint sizes and mapping efficiency.

```bash
# Check read length distribution
samtools view aligned.bam | \
    awk '{print length($10)}' | \
    sort | uniq -c | sort -k2n

# Expected: Peak at 28-30 nt

# Check mapping rate
samtools flagstat aligned.bam
```

## Python Preprocessing

```python
import pysam
import numpy as np
from collections import Counter

def get_length_distribution(bam_path):
    '''Get read length distribution from BAM'''
    lengths = Counter()
    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for read in bam:
            if not read.is_unmapped:
                lengths[read.query_length] += 1
    return lengths

def filter_by_length(bam_in, bam_out, min_len=28, max_len=32):
    '''Filter BAM by read length'''
    with pysam.AlignmentFile(bam_in, 'rb') as infile:
        with pysam.AlignmentFile(bam_out, 'wb', template=infile) as outfile:
            for read in infile:
                if min_len <= read.query_length <= max_len:
                    outfile.write(read)
```

## Related Skills

- ribosome-periodicity - Validate preprocessing quality
- read-qc - General quality control
- read-alignment - Alignment concepts
