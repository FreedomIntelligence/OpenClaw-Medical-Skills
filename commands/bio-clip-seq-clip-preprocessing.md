# bio-clip-seq-clip-preprocessing

> Preprocess CLIP-seq data including adapter trimming, UMI extraction, and PCR duplicate removal. Use when preparing raw CLIP, iCLIP, or eCLIP reads for peak calling.

**Available tools:** Read, Bash

# CLIP-seq Preprocessing

## UMI Extraction (eCLIP/iCLIP)

```bash
# Extract UMI from read 1
umi_tools extract \
    --stdin=reads_R1.fastq.gz \
    --read2-in=reads_R2.fastq.gz \
    --bc-pattern=NNNNNNNNNN \
    --stdout=R1_umi.fastq.gz \
    --read2-out=R2_umi.fastq.gz

# bc-pattern: UMI barcode pattern
# N = UMI base
# For eCLIP: typically 10-nt UMI in read 1
```

## Adapter Trimming

```bash
# Trim adapters after UMI extraction
cutadapt \
    -a AGATCGGAAGAGCACACGTCT \
    -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
    -m 18 \
    -o trimmed_R1.fastq.gz \
    -p trimmed_R2.fastq.gz \
    R1_umi.fastq.gz R2_umi.fastq.gz
```

## Two-Pass Trimming (eCLIP)

```bash
# eCLIP protocol has inline adapters
# First pass: trim 3' adapter
cutadapt -a AGATCGGAAGAGC -m 18 -o pass1.fq.gz input.fq.gz

# Second pass: trim 5' adapter (read-through)
cutadapt -g AGATCGGAAGAGC -m 18 -o pass2.fq.gz pass1.fq.gz
```

## PCR Duplicate Removal

```bash
# After alignment, deduplicate using UMIs
umi_tools dedup \
    --stdin=aligned.bam \
    --stdout=deduped.bam \
    --paired \
    --method=unique

# Methods:
# unique: Exact UMI match
# cluster: Allow UMI mismatches (default)
# adjacency: Network-based clustering
```

## Python Preprocessing

```python
from umi_tools import UMIClusterer
import pysam

def count_umis_per_position(bam_path):
    '''Count unique UMIs at each genomic position'''
    from collections import defaultdict

    position_umis = defaultdict(set)

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for read in bam:
            if read.is_unmapped:
                continue

            # Extract UMI from read name (added by umi_tools extract)
            umi = read.query_name.split('_')[-1]
            pos = (read.reference_name, read.reference_start)
            position_umis[pos].add(umi)

    return {pos: len(umis) for pos, umis in position_umis.items()}
```

## Quality Control

```python
def clip_qc(bam_path):
    '''CLIP-seq specific QC metrics'''
    import pysam

    total = 0
    unique_positions = set()
    read_lengths = []

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for read in bam:
            if read.is_unmapped:
                continue
            total += 1
            unique_positions.add((read.reference_name, read.reference_start))
            read_lengths.append(read.query_length)

    return {
        'total_reads': total,
        'unique_positions': len(unique_positions),
        'mean_read_length': sum(read_lengths) / len(read_lengths),
        'complexity': len(unique_positions) / total
    }
```

## Related Skills

- clip-alignment - Align preprocessed reads
- read-qc/umi-processing - General UMI handling
- clip-peak-calling - Call peaks from aligned reads
