# bio-small-rna-seq-smrna-preprocessing

> Preprocess small RNA sequencing data with adapter trimming and size selection optimized for miRNA, piRNA, and other small RNAs. Use when preparing small RNA-seq reads for downstream quantification or discovery analysis.

**Available tools:** Read, Bash

# Small RNA Preprocessing

## Adapter Trimming with Cutadapt

Small RNA libraries have specific 3' adapters that must be removed:

```bash
# Standard Illumina TruSeq small RNA adapter
cutadapt \
    -a TGGAATTCTCGGGTGCCAAGG \
    -m 18 \
    -M 30 \
    --discard-untrimmed \
    -o trimmed.fastq.gz \
    input.fastq.gz

# -a: 3' adapter sequence
# -m 18: Minimum length (miRNAs are 18-25 nt)
# -M 30: Maximum length (exclude longer fragments)
# --discard-untrimmed: Remove reads without adapter (likely not small RNA)
```

## Common Small RNA Adapters

| Kit | 3' Adapter Sequence |
|-----|---------------------|
| Illumina TruSeq | TGGAATTCTCGGGTGCCAAGG |
| NEBNext | AGATCGGAAGAGCACACGTCT |
| QIAseq | AACTGTAGGCACCATCAAT |
| Lexogen | TGGAATTCTCGGGTGCCAAGGAACTCCAGTCAC |

## Size Selection

```bash
# Filter by length after trimming
cutadapt \
    -a TGGAATTCTCGGGTGCCAAGG \
    -m 18 -M 26 \
    -o mirna_length.fastq.gz \
    input.fastq.gz

# miRNA: 18-26 nt (typically 21-23 nt)
# piRNA: 26-32 nt
# snoRNA: variable, typically longer
```

## Quality Trimming

```bash
# Trim low-quality bases from 3' end before adapter removal
cutadapt \
    -q 20 \
    -a TGGAATTCTCGGGTGCCAAGG \
    -m 18 \
    -o trimmed.fastq.gz \
    input.fastq.gz
```

## Using fastp for Small RNA

```bash
# fastp with small RNA settings
fastp \
    --in1 input.fastq.gz \
    --out1 trimmed.fastq.gz \
    --adapter_sequence TGGAATTCTCGGGTGCCAAGG \
    --length_required 18 \
    --length_limit 30 \
    --html report.html

# Note: fastp auto-detects adapters but specifying is more reliable
```

## Collapse Identical Reads

For small RNAs, collapsing identical sequences reduces computation:

```bash
# Using seqkit
seqkit rmdup -s trimmed.fastq.gz -o collapsed.fasta

# Using fastx_toolkit (legacy)
fastx_collapser -i trimmed.fastq -o collapsed.fasta
```

## Python Preprocessing

```python
import gzip
from collections import Counter

def collapse_reads(fastq_path):
    '''Collapse identical sequences and count occurrences'''
    counts = Counter()

    with gzip.open(fastq_path, 'rt') as f:
        while True:
            header = f.readline()
            if not header:
                break
            seq = f.readline().strip()
            f.readline()  # +
            f.readline()  # qual

            # Only keep reads in miRNA size range
            if 18 <= len(seq) <= 26:
                counts[seq] += 1

    return counts

# Write collapsed FASTA
def write_collapsed_fasta(counts, output_path):
    with open(output_path, 'w') as f:
        for i, (seq, count) in enumerate(counts.most_common()):
            f.write(f'>seq_{i}_x{count}\n{seq}\n')
```

## QC Metrics for Small RNA

Key metrics to check:
- Read length distribution (should peak at 21-23 nt for miRNA)
- Adapter content (high if library is good)
- Percentage of reads in target size range

```python
import matplotlib.pyplot as plt
from collections import Counter

def plot_length_distribution(fastq_path):
    lengths = Counter()
    with gzip.open(fastq_path, 'rt') as f:
        for i, line in enumerate(f):
            if i % 4 == 1:  # Sequence line
                lengths[len(line.strip())] += 1

    plt.bar(lengths.keys(), lengths.values())
    plt.xlabel('Read Length')
    plt.ylabel('Count')
    plt.title('Small RNA Length Distribution')
    plt.savefig('length_dist.png')
```

## Related Skills

- mirdeep2-analysis - Novel miRNA discovery
- mirge3-analysis - Fast miRNA quantification
- read-qc/adapter-trimming - General adapter trimming
