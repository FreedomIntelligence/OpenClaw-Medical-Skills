# bio-longread-qc

> Quality control for long-read sequencing data using NanoPlot, NanoStat, and chopper. Generate QC reports, filter reads by length and quality, and visualize read characteristics. Use when assessing ONT or PacBio run quality or filtering reads before assembly or alignment.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Long-Read Quality Control

**"Check the quality of my Nanopore/PacBio run"** → Generate read length distributions, quality score plots, and summary statistics, then filter reads by length and quality thresholds.
- CLI: `NanoPlot --fastq reads.fq.gz -o nanoplot_output/`, `chopper -q 10 -l 1000 < reads.fq > filtered.fq`

## NanoPlot - Visualization

```bash
# From FASTQ
NanoPlot --fastq reads.fastq.gz -o nanoplot_output -t 4

# From BAM
NanoPlot --bam aligned.bam -o nanoplot_output -t 4

# From sequencing summary (fastest)
NanoPlot --summary sequencing_summary.txt -o nanoplot_output
```

## NanoPlot - Common Options

```bash
NanoPlot --fastq reads.fastq.gz \
    -o nanoplot_output \
    -t 8 \
    --N50 \                        # Show N50 in plots
    --title "Sample QC" \
    --plots hex dot \              # Plot types
    --format png pdf \             # Output formats
    --color darkblue \
    --maxlength 50000 \            # Max length for plots
    --minlength 500                # Min length for plots
```

## NanoStat - Statistics Only

```bash
# Quick statistics (no plots)
NanoStat --fastq reads.fastq.gz --threads 4

# From BAM
NanoStat --bam aligned.bam --threads 4

# Output to file
NanoStat --fastq reads.fastq.gz --threads 4 > qc_stats.txt
```

## chopper - Filter Reads

```bash
# Filter by length and quality
gunzip -c reads.fastq.gz | chopper -q 10 -l 1000 | gzip > filtered.fastq.gz

# Quality >= 10, length >= 1000bp
```

## chopper - Common Options

```bash
gunzip -c reads.fastq.gz | chopper \
    --quality 10 \                 # Min quality
    --minlength 1000 \             # Min length
    --maxlength 50000 \            # Max length
    --headcrop 50 \                # Remove from start
    --tailcrop 50 \                # Remove from end
    --threads 4 \
    | gzip > filtered.fastq.gz
```

## NanoFilt - Alternative Filter

```bash
# Filter with NanoFilt
gunzip -c reads.fastq.gz | NanoFilt -q 10 -l 1000 | gzip > filtered.fastq.gz

# With more options
gunzip -c reads.fastq.gz | NanoFilt \
    --quality 10 \
    --length 1000 \
    --maxlength 50000 \
    --headcrop 50 \
    | gzip > filtered.fastq.gz
```

## Porechop - Adapter Trimming

```bash
# Trim adapters
porechop -i reads.fastq.gz -o trimmed.fastq.gz --threads 8

# With barcode splitting
porechop -i reads.fastq.gz -b output_dir/ --threads 8
```

## Generate Summary Statistics

```bash
# Quick summary with seqkit
seqkit stats reads.fastq.gz

# Detailed stats
seqkit stats -a reads.fastq.gz

# Watch stats during basecalling
seqkit watch --fields ReadLen,MeanQual reads.fastq.gz
```

## PycoQC - From Basecalling

```bash
# Generate QC report from sequencing_summary.txt
pycoQC -f sequencing_summary.txt -o pycoqc_report.html

# With BAM for alignment stats
pycoQC -f sequencing_summary.txt -a aligned.bam -o pycoqc_report.html
```

## Calculate N50

```bash
# With seqkit
seqkit stats -a reads.fastq.gz | grep N50

# Manual calculation
seqkit fx2tab -l reads.fastq.gz | cut -f 2 | sort -rn | \
    awk '{sum+=$1; len[NR]=$1} END {
        target=sum/2; cumsum=0;
        for(i=1; i<=NR; i++) {
            cumsum+=len[i];
            if(cumsum>=target) {print "N50:", len[i]; break}
        }
    }'
```

## Parse FASTQ Quality in Python

**Goal:** Compute read length and quality distributions from long-read FASTQ for custom QC analysis.

**Approach:** Iterate records with BioPython, collecting per-read length and mean Phred quality for summary statistics.

```python
import numpy as np
from Bio import SeqIO

lengths = []
qualities = []

for record in SeqIO.parse('reads.fastq', 'fastq'):
    lengths.append(len(record))
    qualities.append(np.mean(record.letter_annotations['phred_quality']))

print(f'Total reads: {len(lengths)}')
print(f'Total bases: {sum(lengths):,}')
print(f'Mean length: {np.mean(lengths):.0f}')
print(f'Median length: {np.median(lengths):.0f}')
print(f'Mean quality: {np.mean(qualities):.1f}')
```

## NanoPlot Output Files

| File | Description |
|------|-------------|
| NanoStats.txt | Summary statistics |
| NanoPlot-report.html | Interactive report |
| LengthvsQualityScatterPlot | Length vs Q plot |
| WeightedHistogramReadlength | Read length distribution |
| Yield_By_Length | Cumulative yield |

## Key Parameters - NanoPlot

| Parameter | Description |
|-----------|-------------|
| --fastq | Input FASTQ |
| --bam | Input BAM |
| --summary | Sequencing summary |
| -o | Output directory |
| -t | Threads |
| --N50 | Show N50 line |
| --plots | Plot types |
| --format | Output formats |

## Key Parameters - chopper

| Parameter | Default | Description |
|-----------|---------|-------------|
| -q | 0 | Min quality |
| -l | 0 | Min length |
| --maxlength | inf | Max length |
| --headcrop | 0 | Trim from start |
| --tailcrop | 0 | Trim from end |
| -t | 4 | Threads |

## Quality Thresholds

| Q Score | Accuracy | Typical Use |
|---------|----------|-------------|
| Q7 | ~80% | Very low quality |
| Q10 | ~90% | Basic filtering |
| Q15 | ~97% | Moderate filtering |
| Q20 | ~99% | High quality (SUP) |
| Q30 | ~99.9% | Very high (HiFi) |

## Related Skills

- long-read-alignment - Align filtered reads
- sequence-io/fastq-quality - FASTQ quality analysis
- medaka-polishing - Polish with filtered reads
