# bio-genome-intervals-proximity-operations

> Find nearest features, search within windows, and extend intervals using closest, window, flank, and slop operations. Use when performing TSS proximity analysis, assigning enhancers to genes, defining promoter regions, or finding nearby genomic features.

**Available tools:** Read, Bash

# Proximity Operations

Operations for finding nearby features and extending intervals using bedtools and pybedtools.

## Closest - Find Nearest Feature

### CLI

```bash
# Find nearest gene to each peak
bedtools closest -a peaks.bed -b genes.bed > peaks_with_nearest.bed

# Report distance to nearest feature
bedtools closest -a peaks.bed -b genes.bed -d > with_distance.bed

# Ignore overlapping features (find next nearest)
bedtools closest -a peaks.bed -b genes.bed -io > nearest_non_overlap.bed

# Ignore features on different strands
bedtools closest -a peaks.bed -b genes.bed -s > same_strand.bed

# Ignore features on same strand (opposite strand only)
bedtools closest -a peaks.bed -b genes.bed -S > opposite_strand.bed

# Only upstream features (5' direction relative to A strand)
bedtools closest -a peaks.bed -b genes.bed -D a -iu > upstream_only.bed

# Only downstream features
bedtools closest -a peaks.bed -b genes.bed -D a -id > downstream_only.bed

# Report multiple ties
bedtools closest -a peaks.bed -b genes.bed -t all > all_ties.bed

# First tie only
bedtools closest -a peaks.bed -b genes.bed -t first > first_tie.bed
```

### Python

```python
import pybedtools

a = pybedtools.BedTool('peaks.bed')
b = pybedtools.BedTool('genes.bed')

# Basic closest
result = a.closest(b)

# With distance
result = a.closest(b, d=True)

# Ignore overlaps
result = a.closest(b, io=True)

# Same strand only
result = a.closest(b, s=True)

# Report all ties
result = a.closest(b, t='all')

result.saveas('closest.bed')
```

## Window - Find Features Within Distance

### CLI

```bash
# Find genes within 10kb of peaks
bedtools window -a peaks.bed -b genes.bed -w 10000 > genes_within_10kb.bed

# Asymmetric window (5kb upstream, 2kb downstream of A)
bedtools window -a peaks.bed -b genes.bed -l 5000 -r 2000 > asymmetric.bed

# Same strand only
bedtools window -a peaks.bed -b genes.bed -w 10000 -sm > same_strand.bed

# Strand-aware window (upstream/downstream relative to strand)
bedtools window -a peaks.bed -b genes.bed -l 5000 -r 2000 -sw > strand_aware.bed
```

### Python

```python
import pybedtools

a = pybedtools.BedTool('peaks.bed')
b = pybedtools.BedTool('genes.bed')

# Symmetric window
result = a.window(b, w=10000)

# Asymmetric window
result = a.window(b, l=5000, r=2000)

# Same strand
result = a.window(b, w=10000, sm=True)

result.saveas('window.bed')
```

## Slop - Extend Interval Boundaries

### CLI

```bash
# Extend both ends by 100bp (requires genome file)
bedtools slop -i peaks.bed -g genome.txt -b 100 > extended.bed

# Extend 5' end by 500bp, 3' end by 100bp
bedtools slop -i peaks.bed -g genome.txt -l 500 -r 100 > asymmetric.bed

# Strand-aware extension (upstream/downstream)
bedtools slop -i peaks.bed -g genome.txt -l 500 -r 100 -s > strand_aware.bed

# Extend by percentage
bedtools slop -i peaks.bed -g genome.txt -b 0.5 -pct > extend_50pct.bed

# Header passthrough
bedtools slop -i peaks.bed -g genome.txt -b 100 -header > with_header.bed
```

### Python

```python
import pybedtools

bed = pybedtools.BedTool('peaks.bed')

# Symmetric extension
result = bed.slop(g='genome.txt', b=100)

# Asymmetric extension
result = bed.slop(g='genome.txt', l=500, r=100)

# Strand-aware
result = bed.slop(g='genome.txt', l=500, r=100, s=True)

# Percentage
result = bed.slop(g='genome.txt', b=0.5, pct=True)

result.saveas('extended.bed')
```

## Flank - Get Flanking Regions

### CLI

```bash
# Get 100bp flanks on both sides (not original interval)
bedtools flank -i peaks.bed -g genome.txt -b 100 > flanks.bed

# Get upstream flank only
bedtools flank -i peaks.bed -g genome.txt -l 100 -r 0 > upstream.bed

# Get downstream flank only
bedtools flank -i peaks.bed -g genome.txt -l 0 -r 100 > downstream.bed

# Strand-aware flanking
bedtools flank -i peaks.bed -g genome.txt -l 500 -r 0 -s > upstream_strand.bed

# Percentage of interval size
bedtools flank -i peaks.bed -g genome.txt -b 0.5 -pct > flank_50pct.bed
```

### Python

```python
import pybedtools

bed = pybedtools.BedTool('peaks.bed')

# Both flanks
result = bed.flank(g='genome.txt', b=100)

# Upstream only (left)
result = bed.flank(g='genome.txt', l=100, r=0)

# Strand-aware upstream
result = bed.flank(g='genome.txt', l=500, r=0, s=True)

result.saveas('flanks.bed')
```

## Shift - Move Intervals

### CLI

```bash
# Shift all intervals downstream by 100bp
bedtools shift -i peaks.bed -g genome.txt -s 100 > shifted.bed

# Shift upstream (negative)
bedtools shift -i peaks.bed -g genome.txt -s -100 > shifted_up.bed

# Shift by percentage
bedtools shift -i peaks.bed -g genome.txt -s 0.5 -pct > shift_50pct.bed

# Shift with chromosome-specific values
bedtools shift -i peaks.bed -g genome.txt -s 100 -p 200 > shifted.bed  # plus strand +100, minus +200
```

### Python

```python
import pybedtools

bed = pybedtools.BedTool('peaks.bed')

# Shift downstream
result = bed.shift(g='genome.txt', s=100)

# Shift upstream
result = bed.shift(g='genome.txt', s=-100)

result.saveas('shifted.bed')
```

## Common Patterns

### Find Peaks Within 10kb of TSS

```bash
# Get TSS from genes (assumes BED6+ with strand)
awk -v OFS='\t' '{
    if ($6 == "+") print $1, $2, $2+1, $4, $5, $6;
    else print $1, $3-1, $3, $4, $5, $6;
}' genes.bed > tss.bed

# Find peaks within 10kb of TSS
bedtools window -a peaks.bed -b tss.bed -w 10000 > peaks_near_tss.bed
```

### Create Promoter Regions

```bash
# 2kb upstream, 500bp downstream of TSS (strand-aware)
bedtools flank -i tss.bed -g genome.txt -l 2000 -r 0 -s | \
    bedtools slop -i stdin -g genome.txt -l 0 -r 500 -s > promoters.bed

# Or simpler with slop from TSS
bedtools slop -i tss.bed -g genome.txt -l 2000 -r 500 -s > promoters.bed
```

### Find Nearest Gene Within 100kb

```python
import pybedtools

peaks = pybedtools.BedTool('peaks.bed')
genes = pybedtools.BedTool('genes.bed')

# Find closest gene
closest = peaks.closest(genes, d=True)

# Filter to within 100kb
within_100kb = closest.filter(lambda x: abs(int(x.fields[-1])) <= 100000)
within_100kb.saveas('peaks_with_nearby_genes.bed')
```

### Enhancer-Gene Assignment

```python
import pybedtools

enhancers = pybedtools.BedTool('enhancers.bed')
tss = pybedtools.BedTool('tss.bed')

# Find all genes within 1Mb window
assignments = enhancers.window(tss, w=1000000)

# Convert to DataFrame for analysis
df = assignments.to_dataframe()
```

## Genome File Format

```
# genome.txt format: chromosome<TAB>size
chr1	248956422
chr2	242193529
chr3	198295559
...

# Create from FASTA index
cut -f1,2 reference.fa.fai > genome.txt

# Download UCSC chromosome sizes
wget https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.chrom.sizes
```

## Key Parameters

| Operation | Parameter | Description |
|-----------|-----------|-------------|
| closest -d | Distance | Report distance in last column |
| closest -io | Ignore overlap | Skip overlapping features |
| closest -D | Direction | Report signed distance (a/b/ref) |
| window -w | Window | Symmetric window size |
| window -l/-r | Left/Right | Asymmetric window |
| slop -b | Both | Extend both ends |
| slop -s | Strand | Strand-aware extension |
| flank -l/-r | Left/Right | Flank size by side |

## Related Skills

- bed-file-basics - BED format fundamentals
- interval-arithmetic - intersect, subtract, merge
- gtf-gff-handling - Extract TSS from annotations
- chip-seq/peak-annotation - Peak annotation
