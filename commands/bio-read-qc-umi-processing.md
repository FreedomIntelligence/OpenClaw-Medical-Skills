# bio-read-qc-umi-processing

> Extract, process, and deduplicate reads using Unique Molecular Identifiers (UMIs) with umi_tools. Use when library prep includes UMIs and accurate molecule counting is needed, such as in single-cell RNA-seq, low-input RNA-seq, or targeted sequencing to distinguish PCR from biological duplicates.

## Version Compatibility

Reference examples tested with: pandas 2.2+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# UMI Processing

**"Deduplicate reads using UMIs"** → Extract UMI barcodes, group reads by UMI+position, and collapse PCR duplicates to count unique molecules.
- CLI: `umi_tools extract` + `umi_tools dedup` (UMI-tools)
- CLI: `fgbio GroupReadsByUmi` + `fgbio CallMolecularConsensusReads`

UMIs (Unique Molecular Identifiers) are short random sequences added during library preparation to tag individual molecules before PCR amplification. This enables accurate PCR duplicate removal and molecule counting.

## UMI Workflow Overview

```
Raw FASTQ with UMIs
    |
    v
[umi_tools extract] --> Move UMI to read header
    |
    v
[Alignment] --> bwa/STAR/bowtie2
    |
    v
[umi_tools dedup] --> Remove PCR duplicates based on UMI + position
    |
    v
Deduplicated BAM
```

## Extract UMIs from Reads

### UMI in Read Sequence

```bash
# UMI at start of R1 (8bp UMI)
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN

# UMI at start of R2
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern2=NNNNNNNN

# UMI in both reads
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN \
    --bc-pattern2=NNNNNNNN
```

### UMI Pattern Syntax

| Pattern | Meaning |
|---------|---------|
| `N` | UMI base (extracted) |
| `C` | Cell barcode (extracted, kept separate) |
| `X` | Discard base |
| `NNNNNNNN` | 8bp UMI |
| `CCCCCCCCNNNNNNNN` | 8bp cell barcode + 8bp UMI |
| `NNNXXXNNN` | 3bp UMI, skip 3bp, 3bp UMI |

### Complex Patterns

```bash
# 10X Genomics 3' v3 (16bp cell barcode + 12bp UMI in R1)
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern=CCCCCCCCCCCCCCCCNNNNNNNNNNNN

# Skip bases between barcode and UMI
umi_tools extract \
    --stdin=R1.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --bc-pattern=NNNNNNNNXXXX  # 8bp UMI, skip 4bp

# Fixed anchor sequence
umi_tools extract \
    --stdin=R1.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --bc-pattern='(?P<umi_1>.{8})ATGC(?P<discard_1>.{4})'
```

### UMI in Separate Index Read

```bash
# UMI in I1 index read
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN \
    --extract-method=string \
    --umi-separator=":"
```

## Quality Filtering During Extraction

```bash
# Filter by UMI quality
umi_tools extract \
    --stdin=R1.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN \
    --quality-filter-threshold=20 \
    --quality-encoding=phred33

# Filter UMIs with N bases
umi_tools extract \
    --stdin=R1.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN \
    --filter-cell-barcode
```

## Deduplication

### Basic Deduplication

```bash
# Must be sorted and indexed first
samtools sort -o aligned_sorted.bam aligned.bam
samtools index aligned_sorted.bam

# Deduplicate
umi_tools dedup \
    --stdin=aligned_sorted.bam \
    --stdout=deduplicated.bam \
    --log=dedup.log
```

### Deduplication Methods

```bash
# Default: directional (recommended for most cases)
umi_tools dedup -I input.bam -S output.bam --method=directional

# Unique: only exact UMI matches (most stringent)
umi_tools dedup -I input.bam -S output.bam --method=unique

# Cluster: network-based clustering
umi_tools dedup -I input.bam -S output.bam --method=cluster

# Adjacency: cluster with adjacency
umi_tools dedup -I input.bam -S output.bam --method=adjacency

# Percentile: for highly duplicated data
umi_tools dedup -I input.bam -S output.bam --method=percentile
```

### Method Selection Guide

| Method | Use Case | Speed |
|--------|----------|-------|
| `directional` | Standard RNA-seq, most cases | Fast |
| `unique` | Very high diversity, PCR-free | Fastest |
| `cluster` | Low diversity, high errors | Slow |
| `adjacency` | Balance of accuracy/speed | Medium |
| `percentile` | Extremely high duplication | Fast |

### Paired-End Deduplication

```bash
# Paired-end mode
umi_tools dedup \
    -I aligned_sorted.bam \
    -S deduplicated.bam \
    --paired

# Use read2 for grouping (for R2-based libraries)
umi_tools dedup \
    -I aligned_sorted.bam \
    -S deduplicated.bam \
    --paired \
    --read2-in-read1
```

### Gene-Level Deduplication

```bash
# Deduplicate per gene (for RNA-seq)
umi_tools dedup \
    -I aligned_sorted.bam \
    -S deduplicated.bam \
    --per-gene \
    --gene-tag=GX

# With GTF file for gene assignment
umi_tools dedup \
    -I aligned_sorted.bam \
    -S deduplicated.bam \
    --per-gene \
    --per-cell \
    --gene-tag=XT
```

## UMI Counting

### Count UMIs per Gene

```bash
# Count table (gene x cell for single-cell)
umi_tools count \
    -I deduplicated.bam \
    -S counts.tsv \
    --per-gene \
    --gene-tag=GX \
    --per-cell \
    --cell-tag=CB

# Wide format (matrix)
umi_tools count \
    -I deduplicated.bam \
    -S counts.tsv \
    --per-gene \
    --gene-tag=GX \
    --wide-format-cell-counts
```

### Count Table Format

```
gene    cell    count
ENSG00000139618    ACGT    15
ENSG00000139618    TGCA    8
ENSG00000141510    ACGT    42
```

## Group UMIs Without Deduplication

```bash
# Add UMI group tag to BAM (BX tag)
umi_tools group \
    -I aligned_sorted.bam \
    -S grouped.bam \
    --group-out=groups.tsv \
    --output-bam
```

## Complete Workflows

### Standard RNA-seq with UMIs

**Goal:** Process UMI-tagged RNA-seq reads from raw FASTQ through alignment to a deduplicated BAM file.

**Approach:** Extract UMIs from read headers with umi_tools, align with STAR, then deduplicate based on UMI + mapping position to produce a PCR-artifact-free BAM.

```bash
#!/bin/bash
set -euo pipefail

SAMPLE=$1
REFERENCE=$2

# 1. Extract UMIs (8bp at start of R1)
umi_tools extract \
    --stdin=${SAMPLE}_R1.fastq.gz \
    --read2-in=${SAMPLE}_R2.fastq.gz \
    --stdout=${SAMPLE}_R1_umi.fastq.gz \
    --read2-out=${SAMPLE}_R2_umi.fastq.gz \
    --bc-pattern=NNNNNNNN

# 2. Align with STAR
STAR --runThreadN 8 \
    --genomeDir $REFERENCE \
    --readFilesIn ${SAMPLE}_R1_umi.fastq.gz ${SAMPLE}_R2_umi.fastq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix ${SAMPLE}_ \
    --outSAMtype BAM SortedByCoordinate

# 3. Index
samtools index ${SAMPLE}_Aligned.sortedByCoord.out.bam

# 4. Deduplicate
umi_tools dedup \
    -I ${SAMPLE}_Aligned.sortedByCoord.out.bam \
    -S ${SAMPLE}_deduplicated.bam \
    --output-stats=${SAMPLE}_dedup_stats \
    --paired

# 5. Index deduplicated BAM
samtools index ${SAMPLE}_deduplicated.bam

echo "Done: ${SAMPLE}_deduplicated.bam"
```

### Single-Cell Workflow (Post-CellRanger)

```bash
# CellRanger output has CB (cell barcode) and UB (UMI) tags
# Deduplicate per cell per gene
umi_tools dedup \
    -I possorted_genome_bam.bam \
    -S deduplicated.bam \
    --per-cell \
    --cell-tag=CB \
    --umi-tag=UB \
    --extract-umi-method=tag \
    --per-gene \
    --gene-tag=GX
```

## Statistics and QC

### Deduplication Stats

```bash
# Generate stats file
umi_tools dedup \
    -I input.bam \
    -S output.bam \
    --output-stats=dedup_stats

# Output files:
# dedup_stats_per_umi_per_position.tsv
# dedup_stats_per_umi.tsv
# dedup_stats_edit_distance.tsv
```

### Interpret Deduplication Rate

```python
import pandas as pd

stats = pd.read_csv('dedup.log', sep='\t', comment='#')
total_reads = stats['total_reads'].iloc[0]
unique_reads = stats['unique_reads'].iloc[0]
dedup_rate = 1 - (unique_reads / total_reads)
print(f'Deduplication rate: {dedup_rate:.1%}')
```

## Performance Tips

```bash
# Increase speed with multiple cores (dedup only)
umi_tools dedup -I input.bam -S output.bam --parallel

# Reduce memory for large files
umi_tools dedup -I input.bam -S output.bam --buffer-whole-contig

# Skip statistics for speed
umi_tools dedup -I input.bam -S output.bam --no-sort-output
```

## Alternative: fastp UMI Handling

For simple UMI extraction during QC:

```bash
# Extract 8bp UMI from R1 to header
fastp -i R1.fq.gz -I R2.fq.gz \
      -o R1_umi.fq.gz -O R2_umi.fq.gz \
      --umi --umi_loc read1 --umi_len 8
```

Note: fastp extracts UMIs but doesn't deduplicate - use umi_tools dedup after alignment.

## Related Skills

- fastp-workflow - Simple UMI extraction during preprocessing
- quality-filtering - QC before UMI extraction
- alignment-files/sam-bam-basics - BAM sorting/indexing required before dedup
- single-cell/preprocessing - scRNA-seq workflows use UMI counting
