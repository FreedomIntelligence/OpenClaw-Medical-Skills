# bio-genome-intervals-interval-arithmetic

> Core interval arithmetic operations including intersect, subtract, merge, complement, map, and groupby using bedtools and pybedtools. Use when finding overlapping regions, removing overlaps, combining adjacent intervals, or transferring annotations between interval files.

**Available tools:** Read, Bash

# Interval Arithmetic

Core set operations on genomic intervals using bedtools (CLI) and pybedtools (Python).

## Intersect - Find Overlapping Regions

### CLI

```bash
# Find overlapping intervals (report A entries that overlap B)
bedtools intersect -a peaks.bed -b genes.bed > overlapping.bed

# Report original A intervals (default behavior)
bedtools intersect -a peaks.bed -b genes.bed > peaks_in_genes.bed

# Report overlapping portion only
bedtools intersect -a peaks.bed -b genes.bed > overlap_regions.bed

# Report both A and B fields
bedtools intersect -a peaks.bed -b genes.bed -wa -wb > with_gene_info.bed

# Write original A entries that overlap B (-u for unique)
bedtools intersect -a peaks.bed -b genes.bed -u > peaks_overlapping_genes.bed

# Report A entries that do NOT overlap B
bedtools intersect -a peaks.bed -b genes.bed -v > peaks_not_in_genes.bed

# Require minimum overlap fraction (50% of A must overlap)
bedtools intersect -a peaks.bed -b genes.bed -f 0.5 > min_50pct.bed

# Reciprocal overlap (both A and B must have 50% overlap)
bedtools intersect -a peaks.bed -b genes.bed -f 0.5 -r > reciprocal_50pct.bed

# Count overlaps
bedtools intersect -a peaks.bed -b genes.bed -c > with_counts.bed

# Multiple B files
bedtools intersect -a peaks.bed -b genes.bed promoters.bed enhancers.bed -names genes promoters enhancers > multi.bed
```

### Python

```python
import pybedtools

a = pybedtools.BedTool('peaks.bed')
b = pybedtools.BedTool('genes.bed')

# Basic intersection
result = a.intersect(b)

# Keep original A entries that overlap
result = a.intersect(b, u=True)

# Report both A and B
result = a.intersect(b, wa=True, wb=True)

# Non-overlapping (inverse)
result = a.intersect(b, v=True)

# Minimum overlap fraction
result = a.intersect(b, f=0.5)

# Reciprocal overlap
result = a.intersect(b, f=0.5, r=True)

# Count overlaps
result = a.intersect(b, c=True)

# Save result
result.saveas('output.bed')
```

## Subtract - Remove Overlapping Regions

### CLI

```bash
# Remove portions of A that overlap B
bedtools subtract -a regions.bed -b exclude.bed > remaining.bed

# Remove entire A interval if ANY overlap with B
bedtools subtract -a regions.bed -b exclude.bed -A > non_overlapping.bed

# Require minimum overlap before removal
bedtools subtract -a regions.bed -b exclude.bed -f 0.5 > subtract_50pct.bed
```

### Python

```python
import pybedtools

a = pybedtools.BedTool('regions.bed')
b = pybedtools.BedTool('exclude.bed')

# Basic subtraction (remove overlapping portions)
result = a.subtract(b)

# Remove entire interval if any overlap
result = a.subtract(b, A=True)

# Require minimum overlap
result = a.subtract(b, f=0.5)

result.saveas('remaining.bed')
```

## Merge - Combine Overlapping/Adjacent Intervals

### CLI

```bash
# Merge overlapping intervals (input must be sorted)
bedtools sort -i peaks.bed | bedtools merge > merged.bed

# Merge intervals within N bp of each other
bedtools sort -i peaks.bed | bedtools merge -d 100 > merged_100bp.bed

# Report number of merged intervals
bedtools sort -i peaks.bed | bedtools merge -c 1 -o count > merged_counts.bed

# Aggregate columns (e.g., concatenate names, sum scores)
bedtools sort -i peaks.bed | bedtools merge -c 4,5 -o collapse,sum > merged_agg.bed

# Keep max score
bedtools sort -i peaks.bed | bedtools merge -c 5 -o max > merged_max.bed

# Strand-specific merge
bedtools sort -i peaks.bed | bedtools merge -s > merged_stranded.bed
```

### Python

```python
import pybedtools

bed = pybedtools.BedTool('peaks.bed')

# Basic merge (auto-sorts)
merged = bed.sort().merge()

# Merge within distance
merged = bed.sort().merge(d=100)

# Count merged intervals
merged = bed.sort().merge(c=1, o='count')

# Aggregate columns (collapse names, sum scores)
merged = bed.sort().merge(c='4,5', o='collapse,sum')

# Strand-specific
merged = bed.sort().merge(s=True)

merged.saveas('merged.bed')
```

## Complement - Get Uncovered Regions

### CLI

```bash
# Get regions NOT covered by intervals (requires genome file)
bedtools complement -i covered.bed -g genome.txt > uncovered.bed

# genome.txt format: chr<TAB>size
# chr1	248956422
# chr2	242193529
# ...
```

### Python

```python
import pybedtools

bed = pybedtools.BedTool('covered.bed')
genome = 'genome.txt'  # or dict: {'chr1': (0, 248956422), ...}

# Get complement
uncovered = bed.complement(g=genome)
uncovered.saveas('uncovered.bed')

# Using genome dict
genome_dict = pybedtools.chromsizes('hg38')  # Built-in genome sizes
uncovered = bed.complement(genome=genome_dict)
```

## Cluster - Group Overlapping Intervals

### CLI

```bash
# Assign cluster IDs to overlapping intervals
bedtools sort -i peaks.bed | bedtools cluster > clustered.bed

# Cluster within distance
bedtools sort -i peaks.bed | bedtools cluster -d 100 > clustered_100bp.bed
```

### Python

```python
import pybedtools

bed = pybedtools.BedTool('peaks.bed')
clustered = bed.sort().cluster()
clustered.saveas('clustered.bed')
```

## Multiinter - Find Multi-way Overlaps

### CLI

```bash
# Find regions covered by multiple files
bedtools multiinter -i sample1.bed sample2.bed sample3.bed > multi_overlap.bed

# With sample names
bedtools multiinter -i sample1.bed sample2.bed sample3.bed \
    -names s1 s2 s3 > multi_overlap.bed

# Header output
bedtools multiinter -i sample1.bed sample2.bed sample3.bed -header > multi_overlap.bed
```

### Python

```python
import pybedtools

beds = [pybedtools.BedTool(f) for f in ['s1.bed', 's2.bed', 's3.bed']]
# Note: multiinter requires CLI workaround
result = pybedtools.BedTool().multi_intersect(i=[b.fn for b in beds])
```

## Jaccard - Similarity Metric

### CLI

```bash
# Calculate Jaccard similarity between two BED files
bedtools jaccard -a sample1.bed -b sample2.bed

# Output: intersection, union, jaccard, n_intersections
```

### Python

```python
import pybedtools

a = pybedtools.BedTool('sample1.bed')
b = pybedtools.BedTool('sample2.bed')

result = a.jaccard(b)
print(f"Jaccard index: {result['jaccard']}")
print(f"Intersection: {result['intersection']} bp")
print(f"Union: {result['union']} bp")
```

## Fisher's Exact Test

### CLI

```bash
# Statistical test for overlap significance
bedtools fisher -a peaks.bed -b genes.bed -g genome.txt
```

### Python

```python
import pybedtools

a = pybedtools.BedTool('peaks.bed')
b = pybedtools.BedTool('genes.bed')

result = a.fisher(b, genome='genome.txt')
print(result)  # Contains p-values and odds ratio
```

## Shuffle - Random Permutation

### CLI

```bash
# Randomly shuffle intervals (for null hypothesis testing)
bedtools shuffle -i peaks.bed -g genome.txt > shuffled.bed

# Exclude certain regions
bedtools shuffle -i peaks.bed -g genome.txt -excl blacklist.bed > shuffled.bed

# Maintain chromosome distribution
bedtools shuffle -i peaks.bed -g genome.txt -chrom > shuffled.bed
```

### Python

```python
import pybedtools

bed = pybedtools.BedTool('peaks.bed')
shuffled = bed.shuffle(g='genome.txt')
shuffled.saveas('shuffled.bed')
```

## Map - Transfer Values Between Files

Map overlapping B values onto A intervals with aggregation.

### CLI

```bash
# Map mean scores from B to A
bedtools map -a genes.bed -b scores.bedGraph -c 4 -o mean > genes_with_scores.bed

# Multiple operations at once
bedtools map -a regions.bed -b data.bed -c 5,5,5 -o mean,min,max > multi_stats.bed

# Count overlapping features
bedtools map -a genes.bed -b peaks.bed -c 1 -o count > genes_with_peak_counts.bed

# Collapse names of overlapping features
bedtools map -a genes.bed -b peaks.bed -c 4 -o collapse > genes_with_peak_names.bed

# Distinct values only
bedtools map -a genes.bed -b annotations.bed -c 4 -o distinct > unique_annotations.bed
```

### Python

```python
import pybedtools

a = pybedtools.BedTool('genes.bed')
b = pybedtools.BedTool('scores.bedGraph')

# Map mean scores
result = a.map(b, c=4, o='mean')

# Multiple operations
result = a.map(b, c='5,5,5', o='mean,min,max')

result.saveas('mapped.bed')
```

### Map Operations

| Operation | Description |
|-----------|-------------|
| sum | Sum of values |
| count | Number of overlapping features |
| count_distinct | Number of distinct values |
| min, max | Minimum/maximum value |
| mean, median | Average values |
| collapse | Comma-separated list |
| distinct | Unique values only |
| first, last | First/last overlapping value |

## Groupby - Aggregate by Columns

Group intervals and compute summary statistics.

### CLI

```bash
# Sum scores by gene (column 4)
bedtools groupby -i sorted.bed -g 4 -c 5 -o sum > gene_totals.bed

# Group by chromosome and compute stats
bedtools groupby -i sorted.bed -g 1 -c 2,3 -o min,max > chr_ranges.bed

# Multiple grouping columns
bedtools groupby -i sorted.bed -g 1,4 -c 5 -o mean > by_chr_gene.bed

# Collapse names within groups
bedtools groupby -i sorted.bed -g 1,2,3 -c 4 -o collapse > merged_names.bed

# Count features per group
bedtools groupby -i sorted.bed -g 1 -c 1 -o count > features_per_chr.bed

# Use column ranges
bedtools groupby -i sorted.bed -g 1-3 -c 5 -o sum > grouped.bed
```

### Python

```python
import pybedtools

bed = pybedtools.BedTool('sorted.bed')

# Group by column 4, sum column 5
result = bed.groupby(g=4, c=5, o='sum')

# Multiple operations
result = bed.groupby(g=[1, 4], c=[5, 5], o=['mean', 'count'])

result.saveas('grouped.bed')
```

**Note:** Input must be sorted by grouping columns.

## Common Patterns

### Find Peaks in Promoters

```python
import pybedtools

peaks = pybedtools.BedTool('peaks.bed')
promoters = pybedtools.BedTool('promoters.bed')

# Peaks overlapping promoters
peaks_in_promoters = peaks.intersect(promoters, u=True)
print(f'{peaks_in_promoters.count()} peaks in promoters')
```

### Find Unique Regions in Sample

```python
import pybedtools

sample_a = pybedtools.BedTool('sample_a.bed')
sample_b = pybedtools.BedTool('sample_b.bed')

# Regions unique to sample A
unique_a = sample_a.intersect(sample_b, v=True)
unique_a.saveas('unique_to_a.bed')
```

### Merge Replicates

```bash
# Concatenate and merge peaks from replicates
cat rep1.bed rep2.bed rep3.bed | bedtools sort | bedtools merge -d 100 > consensus.bed
```

## Key Parameters

| Operation | Key Flags | Description |
|-----------|-----------|-------------|
| intersect -u | Unique | Report A once if overlap |
| intersect -v | Inverse | A that don't overlap B |
| intersect -f | Fraction | Minimum overlap fraction |
| intersect -r | Reciprocal | Both must meet -f threshold |
| intersect -c | Count | Count overlapping B features |
| subtract -A | All | Remove entire A if any overlap |
| merge -d | Distance | Merge within N bp |
| merge -c -o | Columns/Ops | Aggregate columns |

## Related Skills

- bed-file-basics - BED format and creation
- proximity-operations - closest, window, flank, slop
- coverage-analysis - coverage calculations
- chip-seq/peak-calling - peak file operations
