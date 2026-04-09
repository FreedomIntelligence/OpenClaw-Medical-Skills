# bio-small-rna-seq-mirge3-analysis

> Fast miRNA quantification with isomiR detection and A-to-I editing analysis using miRge3. Use when quantifying known miRNAs quickly or analyzing isomiR variants and RNA editing.

**Available tools:** Read, Bash

# miRge3 Analysis

## Basic Quantification

```bash
# Run miRge3 on FASTQ files
miRge3.0 annotate \
    -s sample1.fastq.gz,sample2.fastq.gz \
    -lib miRge3_libs \
    -on human \
    -db mirbase \
    -o output_dir \
    -a TGGAATTCTCGGGTGCCAAGG \
    --threads 8

# Key options:
# -s: Input FASTQ files (comma-separated)
# -lib: Path to miRge3 library
# -on: Organism name
# -db: Database (mirbase or mirgenedb)
# -a: 3' adapter sequence
```

## Install miRge3 Libraries

```bash
# Download pre-built libraries
miRge3.0 --download-library human mirbase

# Libraries include:
# - Bowtie indices for miRNAs, tRNAs, rRNAs
# - miRBase or MirGeneDB annotations
# - A-to-I editing sites
```

## IsomiR Detection

```bash
# Enable isomiR analysis
miRge3.0 annotate \
    -s sample.fastq.gz \
    -lib miRge3_libs \
    -on human \
    -db mirbase \
    --isomir \
    -o output_dir

# IsomiRs include:
# - 5' variants (templated and non-templated)
# - 3' variants (templated and non-templated)
# - Internal modifications
```

## A-to-I RNA Editing

```bash
# Detect A-to-I editing
miRge3.0 annotate \
    -s sample.fastq.gz \
    -lib miRge3_libs \
    -on human \
    -db mirbase \
    --AtoI \
    -o output_dir

# Outputs editing sites and frequencies
```

## Output Files

| File | Description |
|------|-------------|
| miR.Counts.csv | Raw read counts per miRNA |
| miR.RPM.csv | RPM normalized counts |
| isomiR.Counts.csv | IsomiR-level counts |
| isomiR.summary.csv | IsomiR summary per miRNA |
| annotation.report.html | Interactive QC report |

## Python API

```python
from mirge3.annotate import annotate

# Run programmatically
annotate(
    samples=['sample1.fastq.gz', 'sample2.fastq.gz'],
    lib_path='miRge3_libs',
    organism='human',
    database='mirbase',
    adapter='TGGAATTCTCGGGTGCCAAGG',
    output_dir='results',
    threads=8
)
```

## Parse miRge3 Output

```python
import pandas as pd

def load_mirge3_counts(output_dir):
    '''Load miRge3 count matrix'''
    counts = pd.read_csv(f'{output_dir}/miR.Counts.csv', index_col=0)
    return counts

def load_isomirs(output_dir):
    '''Load isomiR-level counts'''
    isomirs = pd.read_csv(f'{output_dir}/isomiR.Counts.csv', index_col=0)
    return isomirs

# Filter low-expressed miRNAs
def filter_low_counts(counts, min_total=10):
    '''Keep miRNAs with total count >= threshold'''
    return counts[counts.sum(axis=1) >= min_total]
```

## Compare Multiple Samples

```python
def normalize_rpm(counts):
    '''Normalize to reads per million'''
    total_per_sample = counts.sum(axis=0)
    rpm = counts / total_per_sample * 1e6
    return rpm

def log_transform(rpm, pseudocount=1):
    '''Log2 transform with pseudocount'''
    import numpy as np
    return np.log2(rpm + pseudocount)
```

## IsomiR Analysis

```python
def summarize_isomirs(isomir_counts):
    '''Summarize isomiR diversity per miRNA'''
    # Group by canonical miRNA
    isomir_counts['miRNA'] = isomir_counts.index.str.extract(r'(hsa-\w+-\d+[a-z]*)')[0]

    summary = isomir_counts.groupby('miRNA').agg({
        'count': ['sum', 'count', lambda x: x.idxmax()]
    })
    summary.columns = ['total_reads', 'n_isomirs', 'dominant_isomir']
    return summary
```

## Related Skills

- smrna-preprocessing - Prepare reads for miRge3
- mirdeep2-analysis - Alternative with novel miRNA discovery
- differential-mirna - DE analysis of miRge3 counts
