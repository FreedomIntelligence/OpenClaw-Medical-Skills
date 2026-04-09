# bio-genome-intervals-coverage-analysis

> Calculate read depth and coverage across genomic intervals using bedtools genomecov and coverage. Generate bedGraph files, compute per-base depth, and summarize coverage statistics. Use when assessing sequencing depth, creating coverage tracks, or evaluating target capture efficiency.

**Available tools:** Read, Bash

# Coverage Analysis

Calculate coverage and depth across genomic regions using bedtools and pybedtools.

## genomecov - Genome-wide Coverage

### Per-base Coverage (bedGraph)

```bash
# Generate bedGraph from BAM (per-base depth)
bedtools genomecov -ibam alignments.bam -bg > coverage.bedGraph

# Include zero-coverage regions
bedtools genomecov -ibam alignments.bam -bga > coverage_with_zeros.bedGraph

# Split by strand
bedtools genomecov -ibam alignments.bam -bg -strand + > plus_strand.bedGraph
bedtools genomecov -ibam alignments.bam -bg -strand - > minus_strand.bedGraph

# Scale by total reads (RPM normalization)
TOTAL=$(samtools view -c alignments.bam)
SCALE=$(echo "scale=10; 1000000/$TOTAL" | bc)
bedtools genomecov -ibam alignments.bam -bg -scale $SCALE > normalized.bedGraph

# Use only 5' end of reads
bedtools genomecov -ibam alignments.bam -bg -5 > five_prime.bedGraph

# Use only 3' end of reads
bedtools genomecov -ibam alignments.bam -bg -3 > three_prime.bedGraph
```

### Coverage Histogram

```bash
# Genome-wide coverage histogram
bedtools genomecov -ibam alignments.bam > coverage_hist.txt

# Output format: chr, depth, bases_at_depth, chr_size, fraction
# genome  0       1000000  10000000  0.1
# genome  1       5000000  10000000  0.5
# ...
```

### Coverage from BED

```bash
# Coverage from BED intervals
bedtools genomecov -i regions.bed -g genome.txt -bg > coverage.bedGraph

# BED must be sorted
bedtools sort -i regions.bed | bedtools genomecov -i stdin -g genome.txt -bg > coverage.bedGraph
```

### Python

```python
import pybedtools

# From BAM
bam = pybedtools.BedTool('alignments.bam')
coverage = bam.genome_coverage(bg=True)
coverage.saveas('coverage.bedGraph')

# With zeros
coverage = bam.genome_coverage(bga=True)

# Normalized
coverage = bam.genome_coverage(bg=True, scale=0.001)

# From BED
bed = pybedtools.BedTool('regions.bed')
coverage = bed.genome_coverage(bg=True, g='genome.txt')
```

## coverage - Coverage per Feature

### Basic Coverage

```bash
# Calculate how much of each region in A is covered by B
bedtools coverage -a targets.bed -b reads.bed > coverage_per_target.bed

# Output adds 4 columns: overlaps, bases_covered, region_length, fraction
# chr1  100  200  region1  5  50  100  0.5

# From BAM
bedtools coverage -a targets.bed -b alignments.bam > coverage.bed

# Count only (no coverage calculation)
bedtools coverage -a targets.bed -b reads.bed -counts > counts.bed
```

### Coverage Options

```bash
# Mean coverage per region
bedtools coverage -a targets.bed -b alignments.bam -mean > mean_coverage.bed

# Same strand only
bedtools coverage -a targets.bed -b alignments.bam -s > same_strand.bed

# Report depth at each position (histogram)
bedtools coverage -a targets.bed -b alignments.bam -d > per_base.bed

# Require minimum overlap
bedtools coverage -a targets.bed -b reads.bed -f 0.5 > min_overlap.bed

# Split alignments (for RNA-seq)
bedtools coverage -a exons.bed -b alignments.bam -split > exon_coverage.bed
```

### Python

```python
import pybedtools

a = pybedtools.BedTool('targets.bed')
b = pybedtools.BedTool('alignments.bam')

# Basic coverage
result = a.coverage(b)

# Mean coverage
result = a.coverage(b, mean=True)

# Counts only
result = a.coverage(b, counts=True)

# Per-base depth
result = a.coverage(b, d=True)

result.saveas('coverage.bed')
```

## multicov - Counts Across Multiple BAMs

```bash
# Count reads in regions across multiple samples
bedtools multicov -bams sample1.bam sample2.bam sample3.bam -bed regions.bed > counts.txt

# Require mapping quality
bedtools multicov -bams sample1.bam sample2.bam -bed regions.bed -q 30 > counts.txt

# Split alignments
bedtools multicov -bams sample1.bam sample2.bam -bed regions.bed -s -split > counts.txt
```

## Calculate Coverage Statistics

### Mean/Median Depth

```python
import pybedtools
import pandas as pd
import numpy as np

# Load coverage BED (from bedtools coverage -d)
bed = pybedtools.BedTool('per_base_coverage.bed')
df = bed.to_dataframe()

# Calculate stats per region
stats = df.groupby(['chrom', 'start', 'end']).agg({
    'score': ['mean', 'median', 'std', 'max']
}).reset_index()

print(stats)
```

### Coverage Distribution

```python
import pybedtools

# Get coverage histogram
bam = pybedtools.BedTool('alignments.bam')
hist = bam.genome_coverage()

# Parse histogram
depths = []
fractions = []
for line in open(hist.fn):
    fields = line.strip().split('\t')
    if fields[0] == 'genome':
        depths.append(int(fields[1]))
        fractions.append(float(fields[4]))

# Calculate metrics
import numpy as np
mean_depth = sum(d * f for d, f in zip(depths, fractions))
print(f'Mean depth: {mean_depth:.1f}x')
```

## Common Patterns

### Target Region Coverage Summary

```bash
# Get per-region coverage stats
bedtools coverage -a targets.bed -b alignments.bam | \
    awk -v OFS='\t' '{
        mean = ($NF > 0) ? $5/$6 : 0;
        print $1, $2, $3, $4, $7, mean
    }' > summary.bed

# Regions with low coverage
bedtools coverage -a targets.bed -b alignments.bam | \
    awk '$NF < 0.8' > low_coverage.bed
```

### Normalize to CPM (Counts Per Million)

```python
import pybedtools

bam = pybedtools.BedTool('alignments.bam')

# Get total reads
import subprocess
result = subprocess.run(['samtools', 'view', '-c', 'alignments.bam'],
                        capture_output=True, text=True)
total_reads = int(result.stdout.strip())

# Generate CPM-normalized bedGraph
scale_factor = 1000000 / total_reads
coverage = bam.genome_coverage(bg=True, scale=scale_factor)
coverage.saveas('cpm_normalized.bedGraph')
```

### Exon Coverage for RNA-seq

```bash
# Calculate coverage across exons (handling spliced reads)
bedtools coverage -a exons.bed -b alignments.bam -split > exon_coverage.bed

# Summarize by gene
awk -v OFS='\t' '{
    gene = $4; gsub(/_exon.*/, "", gene);
    sum[gene] += $NF * ($3-$2);
    len[gene] += $3-$2;
}
END {
    for (g in sum) print g, sum[g]/len[g];
}' exon_coverage.bed > gene_coverage.txt
```

## bedGraph Format

```
# bedGraph: chr, start, end, value (0-based coordinates)
chr1    0       100     0
chr1    100     200     5.5
chr1    200     300     10.2
chr1    300     400     3.1
```

## Key Parameters

| Tool | Parameter | Description |
|------|-----------|-------------|
| genomecov -bg | bedGraph | Output bedGraph format |
| genomecov -bga | bedGraph all | Include zero coverage |
| genomecov -scale | Normalize | Scale values by factor |
| coverage -mean | Mean | Report mean coverage |
| coverage -d | Per-base | Report per-position depth |
| coverage -counts | Count | Count overlaps only |
| multicov -q | Quality | Minimum mapping quality |

## Related Skills

- bigwig-tracks - Convert bedGraph to bigWig
- alignment-files/sam-bam-basics - BAM processing
- interval-arithmetic - Intersect with regions
- chip-seq/chipseq-visualization - Peak coverage analysis
