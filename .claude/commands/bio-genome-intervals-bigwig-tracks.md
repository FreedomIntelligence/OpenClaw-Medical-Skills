# bio-genome-intervals-bigwig-tracks

> Create and read bigWig browser tracks for visualizing continuous genomic data. Convert bedGraph to bigWig, extract signal values, and generate coverage tracks using UCSC tools and pyBigWig. Use when preparing coverage tracks for genome browsers or extracting signal at specific regions.

**Available tools:** Read, Bash

# BigWig Tracks

BigWig is an indexed binary format for continuous genomic data. Efficient for genome browsers and programmatic access.

## Why BigWig?

| Format | Size | Random Access | Browser Support |
|--------|------|---------------|-----------------|
| bedGraph | Large | No | Limited |
| bigWig | ~10x smaller | Yes (indexed) | Excellent |

## Convert bedGraph to bigWig (CLI)

### Installation

```bash
# UCSC tools
conda install -c bioconda ucsc-bedgraphtobigwig ucsc-bigwigtobedgraph

# Or download directly
wget http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/bedGraphToBigWig
chmod +x bedGraphToBigWig
```

### Basic Conversion

```bash
# Sort bedGraph first (required)
sort -k1,1 -k2,2n coverage.bedGraph > coverage.sorted.bedGraph

# Convert to bigWig
bedGraphToBigWig coverage.sorted.bedGraph chrom.sizes output.bw

# chrom.sizes format: chr<TAB>size
# chr1	248956422
# chr2	242193529
```

### Get Chromosome Sizes

```bash
# From FASTA index
cut -f1,2 reference.fa.fai > chrom.sizes

# Download from UCSC
wget https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.chrom.sizes

# From BAM header
samtools view -H alignments.bam | grep @SQ | sed 's/@SQ\tSN:\|LN://g' > chrom.sizes
```

### Full Workflow

```bash
# Generate bedGraph from BAM
bedtools genomecov -ibam alignments.bam -bg > coverage.bedGraph

# Sort bedGraph
sort -k1,1 -k2,2n coverage.bedGraph > coverage.sorted.bedGraph

# Convert to bigWig
bedGraphToBigWig coverage.sorted.bedGraph hg38.chrom.sizes coverage.bw

# Clean up intermediate files
rm coverage.bedGraph coverage.sorted.bedGraph
```

## Read BigWig with pyBigWig (Python)

### Installation

```bash
pip install pyBigWig
```

### Open and Inspect

```python
import pyBigWig

# Open file
bw = pyBigWig.open('coverage.bw')

# File info
print(f'Chromosomes: {bw.chroms()}')
print(f'Header: {bw.header()}')

# Check if file is bigWig (not bigBed)
print(f'Is bigWig: {bw.isBigWig()}')

# Close when done
bw.close()
```

### Extract Values

```python
import pyBigWig

bw = pyBigWig.open('coverage.bw')

# Get values for a region (returns numpy array)
values = bw.values('chr1', 1000000, 1001000)
print(f'Mean: {values.mean():.2f}')
print(f'Max: {values.max():.2f}')

# Get specific intervals with values
intervals = bw.intervals('chr1', 1000000, 1001000)
# Returns: [(start, end, value), ...]
for start, end, val in intervals:
    print(f'{start}-{end}: {val}')

# Statistics for region
stats = bw.stats('chr1', 1000000, 1001000, type='mean')
print(f'Mean coverage: {stats[0]:.2f}')

# Available stat types: mean, min, max, coverage, std, sum
max_val = bw.stats('chr1', 1000000, 1001000, type='max')
coverage = bw.stats('chr1', 1000000, 1001000, type='coverage')

bw.close()
```

### Binned Statistics

```python
import pyBigWig

bw = pyBigWig.open('coverage.bw')

# Get mean values in 100bp bins across region
region_start, region_end = 1000000, 2000000
n_bins = 1000  # 100bp bins

binned = bw.stats('chr1', region_start, region_end, type='mean', nBins=n_bins)
# Returns list of n_bins values

bw.close()
```

### Extract for BED Regions

```python
import pyBigWig
import pybedtools

bw = pyBigWig.open('coverage.bw')
bed = pybedtools.BedTool('regions.bed')

# Get mean signal per region
results = []
for interval in bed:
    chrom, start, end = interval.chrom, interval.start, interval.end
    mean_signal = bw.stats(chrom, start, end, type='mean')[0]
    results.append({
        'chrom': chrom,
        'start': start,
        'end': end,
        'name': interval.name,
        'signal': mean_signal if mean_signal else 0
    })

bw.close()

# Convert to DataFrame
import pandas as pd
df = pd.DataFrame(results)
print(df)
```

## Create BigWig with pyBigWig

```python
import pyBigWig

# Create new bigWig
bw = pyBigWig.open('output.bw', 'w')

# Add header (chromosome sizes)
bw.addHeader([('chr1', 248956422), ('chr2', 242193529)])

# Add entries (must be sorted by position)
# Method 1: Individual entries
bw.addEntries(['chr1', 'chr1'], [0, 100], ends=[100, 200], values=[1.5, 2.3])

# Method 2: Chromosome at a time (more efficient)
bw.addEntries('chr1', [0, 100, 200], ends=[100, 200, 300], values=[1.5, 2.3, 3.1])

# Method 3: Fixed-width spans (most efficient for dense data)
bw.addEntries('chr2', 0, values=[1.0, 2.0, 3.0, 4.0], span=100, step=100)
# Creates: chr2:0-100=1.0, chr2:100-200=2.0, chr2:200-300=3.0, chr2:300-400=4.0

bw.close()
```

## deepTools for BigWig Operations

### Installation

```bash
conda install -c bioconda deeptools
```

### Generate Normalized BigWig from BAM

```bash
# RPKM normalization
bamCoverage -b alignments.bam -o coverage.bw --normalizeUsing RPKM

# CPM normalization
bamCoverage -b alignments.bam -o coverage.bw --normalizeUsing CPM

# BPM (bins per million) - like TPM for ChIP-seq
bamCoverage -b alignments.bam -o coverage.bw --normalizeUsing BPM

# With bin size and smoothing
bamCoverage -b alignments.bam -o coverage.bw \
    --binSize 10 \
    --normalizeUsing CPM \
    --smoothLength 30

# Extend reads to fragment length
bamCoverage -b alignments.bam -o coverage.bw \
    --extendReads 200 \
    --normalizeUsing CPM
```

### Compare BigWig Files

```bash
# Log2 ratio of two bigWig files
bigwigCompare -b1 treatment.bw -b2 control.bw -o log2ratio.bw --ratio log2

# Subtract
bigwigCompare -b1 treatment.bw -b2 control.bw -o diff.bw --ratio subtract

# Mean of multiple files
bigwigAverage -b file1.bw file2.bw file3.bw -o average.bw
```

### Summarize BigWig Over Regions

```bash
# Matrix for heatmap (signal around regions)
computeMatrix reference-point -S signal.bw -R regions.bed \
    -b 2000 -a 2000 -o matrix.gz

# Plot heatmap
plotHeatmap -m matrix.gz -o heatmap.png

# Summary statistics per region
multiBigwigSummary BED-file -b sample1.bw sample2.bw -o results.npz --BED regions.bed
```

## Convert BigWig to bedGraph

```bash
# Using UCSC tool
bigWigToBedGraph input.bw output.bedGraph

# Extract specific region
bigWigToBedGraph input.bw output.bedGraph -chrom=chr1 -start=1000000 -end=2000000
```

## Common Patterns

### ChIP-seq Signal Track

```bash
# Generate normalized track
bamCoverage -b chip.bam -o chip.bw \
    --normalizeUsing CPM \
    --extendReads 200 \
    --binSize 10

# Generate input-subtracted track
bigwigCompare -b1 chip.bw -b2 input.bw -o chip_minus_input.bw --ratio subtract
```

### RNA-seq Coverage

```bash
# Strand-specific coverage
bamCoverage -b rnaseq.bam -o forward.bw --filterRNAstrand forward
bamCoverage -b rnaseq.bam -o reverse.bw --filterRNAstrand reverse
```

### Extract Signal for Analysis

```python
import pyBigWig
import pandas as pd

def extract_signal(bw_path, bed_path, stat='mean'):
    '''Extract bigWig signal for BED regions.'''
    import pybedtools
    bw = pyBigWig.open(bw_path)
    bed = pybedtools.BedTool(bed_path)

    results = []
    for interval in bed:
        val = bw.stats(interval.chrom, interval.start, interval.end, type=stat)[0]
        results.append({
            'chrom': interval.chrom,
            'start': interval.start,
            'end': interval.end,
            'name': interval.name if interval.name else '.',
            'signal': val if val is not None else 0
        })

    bw.close()
    return pd.DataFrame(results)

# Usage
df = extract_signal('coverage.bw', 'peaks.bed', stat='mean')
print(df)
```

## Related Skills

- coverage-analysis - Generate bedGraph input
- chip-seq/chipseq-visualization - ChIP-seq signal tracks
- alignment-files/bam-statistics - BAM to coverage
- interval-arithmetic - Region operations
