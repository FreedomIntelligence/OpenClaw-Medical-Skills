# bio-small-rna-seq-mirdeep2-analysis

> Discover novel miRNAs and quantify known miRNAs using miRDeep2 de novo prediction from small RNA-seq data. Use when identifying new miRNAs or performing comprehensive miRNA profiling with discovery.

**Available tools:** Read, Bash

# miRDeep2 Analysis

## Workflow Overview

```
Collapsed reads (FASTA)
    |
    v
mapper.pl ---------> Align to genome, create ARF file
    |
    v
miRDeep2.pl -------> Predict novel miRNAs, quantify known
    |
    v
quantifier.pl -----> Quantify known miRNAs only (optional)
```

## Step 1: Prepare Genome Index

```bash
# Build bowtie index for miRDeep2 mapper
bowtie-build genome.fa genome_index
```

## Step 2: Map Reads with mapper.pl

```bash
# Collapse reads and map to genome
mapper.pl reads.fastq \
    -e \
    -h \
    -i \
    -j \
    -k TGGAATTCTCGGGTGCCAAGG \
    -l 18 \
    -m \
    -p genome_index \
    -s reads_collapsed.fa \
    -t reads_vs_genome.arf \
    -v

# Key options:
# -e: Input is FASTQ
# -h: Parse Illumina headers
# -k: Clip 3' adapter
# -l 18: Discard reads < 18 nt
# -m: Collapse reads
# -p: Bowtie index prefix
# -s: Output collapsed FASTA
# -t: Output ARF alignment file
```

## Step 3: Run miRDeep2 Prediction

```bash
# Predict novel miRNAs
miRDeep2.pl \
    reads_collapsed.fa \
    genome.fa \
    reads_vs_genome.arf \
    mature_ref.fa \
    mature_other.fa \
    hairpin_ref.fa \
    -t Human \
    2> report.log

# Arguments:
# 1. Collapsed reads FASTA
# 2. Genome FASTA
# 3. Alignment ARF file
# 4. Known mature miRNAs (same species)
# 5. Known mature miRNAs (other species, for conservation)
# 6. Known hairpin precursors
# -t: Species for miRBase lookup
```

## Prepare miRBase References

```bash
# Download from miRBase
wget https://www.mirbase.org/download/mature.fa
wget https://www.mirbase.org/download/hairpin.fa

# Extract species-specific sequences
grep -A1 ">hsa-" mature.fa > mature_human.fa
grep -A1 ">hsa-" hairpin.fa > hairpin_human.fa
```

## Step 4: Quantify Known miRNAs Only

```bash
# If not doing novel discovery
quantifier.pl \
    -p hairpin_human.fa \
    -m mature_human.fa \
    -r reads_collapsed.fa \
    -t hsa

# Output: miRNAs_expressed_all_samples.csv
```

## Output Files

| File | Description |
|------|-------------|
| result_*.html | Interactive results report |
| result_*.csv | Predicted novel miRNAs with scores |
| miRNAs_expressed_all_samples*.csv | Expression quantification |
| pdfs_*.pdf | Secondary structure plots |

## Interpret miRDeep2 Scores

```
Score interpretation:
>10: High confidence novel miRNA
5-10: Medium confidence
1-5: Low confidence, needs validation
<1: Likely false positive

Key metrics:
- miRDeep2 score: Overall confidence
- Total read count: Expression level
- Mature/star ratio: Strand bias (expect asymmetry)
- Randfold p-value: Structural stability
```

## Parse Results in Python

```python
import pandas as pd

def parse_mirdeep2_results(csv_path):
    '''Parse miRDeep2 novel miRNA predictions'''
    df = pd.read_csv(csv_path, sep='\t', skiprows=1)

    # Filter high-confidence predictions
    # Score > 10 indicates high confidence novel miRNA
    high_conf = df[df['miRDeep2 score'] > 10]

    return high_conf

# Parse quantification results
def parse_quantifier_output(csv_path):
    '''Parse quantifier.pl expression matrix'''
    df = pd.read_csv(csv_path, sep='\t')
    return df
```

## Related Skills

- smrna-preprocessing - Prepare reads for miRDeep2
- mirge3-analysis - Faster quantification alternative
- differential-mirna - DE analysis of miRNA counts
