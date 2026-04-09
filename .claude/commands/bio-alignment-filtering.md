# bio-alignment-filtering

> Filter alignments by flags, mapping quality, and regions using samtools view and pysam. Use when extracting specific reads, removing low-quality alignments, or subsetting to target regions.

**Available tools:** Read, Bash

# Alignment Filtering

Filter alignments by flags, quality, and regions using samtools and pysam.

## Filter Flags

| Option | Description |
|--------|-------------|
| `-f FLAG` | Include reads with ALL bits set |
| `-F FLAG` | Exclude reads with ANY bits set |
| `-G FLAG` | Exclude reads with ALL bits set |
| `-q MAPQ` | Minimum mapping quality |
| `-L BED` | Include reads overlapping regions |

## Common FLAG Values

| Flag | Hex | Meaning |
|------|-----|---------|
| 1 | 0x1 | Paired |
| 2 | 0x2 | Proper pair |
| 4 | 0x4 | Unmapped |
| 8 | 0x8 | Mate unmapped |
| 16 | 0x10 | Reverse strand |
| 32 | 0x20 | Mate reverse strand |
| 64 | 0x40 | First in pair (read1) |
| 128 | 0x80 | Second in pair (read2) |
| 256 | 0x100 | Secondary alignment |
| 512 | 0x200 | Failed QC |
| 1024 | 0x400 | Duplicate |
| 2048 | 0x800 | Supplementary |

## Filter by FLAG

### Keep Only Mapped Reads
```bash
samtools view -F 4 -o mapped.bam input.bam
```

### Keep Only Unmapped Reads
```bash
samtools view -f 4 -o unmapped.bam input.bam
```

### Keep Only Properly Paired
```bash
samtools view -f 2 -o proper.bam input.bam
```

### Remove Duplicates
```bash
samtools view -F 1024 -o nodup.bam input.bam
```

### Remove Secondary and Supplementary
```bash
samtools view -F 2304 -o primary.bam input.bam
```

### Keep Only Primary Alignments
```bash
samtools view -F 256 -F 2048 -o primary.bam input.bam
# Or combined: -F 2304
```

### Keep Read1 Only
```bash
samtools view -f 64 -o read1.bam input.bam
```

### Keep Read2 Only
```bash
samtools view -f 128 -o read2.bam input.bam
```

### Forward Strand Only
```bash
samtools view -F 16 -o forward.bam input.bam
```

### Reverse Strand Only
```bash
samtools view -f 16 -o reverse.bam input.bam
```

## Filter by Mapping Quality

### Minimum MAPQ
```bash
samtools view -q 30 -o highqual.bam input.bam
```

### MAPQ and Mapped
```bash
samtools view -F 4 -q 30 -o filtered.bam input.bam
```

### Common MAPQ Thresholds

| MAPQ | Meaning |
|------|---------|
| 0 | Mapped to multiple locations equally well |
| 20 | ~1% chance of wrong mapping |
| 30 | ~0.1% chance of wrong mapping |
| 40 | ~0.01% chance of wrong mapping |
| 60 | Unique mapping (BWA max) |

## Filter by Region

### Single Region
```bash
samtools view -o region.bam input.bam chr1:1000000-2000000
```

### Multiple Regions
```bash
samtools view -o regions.bam input.bam chr1:1000-2000 chr2:3000-4000
```

### Regions from BED File
```bash
samtools view -L targets.bed -o targets.bam input.bam
```

### Combine Region and Quality
```bash
samtools view -q 30 -L targets.bed -o filtered.bam input.bam
```

## Combined Filters

### Standard Quality Filter
```bash
# Primary, mapped, non-duplicate, MAPQ >= 30
samtools view -F 3332 -q 30 -o filtered.bam input.bam
# 3332 = 4 (unmapped) + 256 (secondary) + 1024 (duplicate) + 2048 (supplementary)
```

### Variant Calling Prep
```bash
# Properly paired, primary, no duplicates, MAPQ >= 20
samtools view -f 2 -F 3328 -q 20 -o clean.bam input.bam
# 3328 = 256 (secondary) + 1024 (duplicate) + 2048 (supplementary)
# Note: -f 2 (proper pair) implies mapped, so -F 4 is not strictly needed
```

### ChIP-seq Filter
```bash
# Remove duplicates and low MAPQ
samtools view -F 1024 -q 30 -o filtered.bam input.bam
```

## Subsample Reads

### Random Subsample
```bash
# Keep ~10% of reads
samtools view -s 0.1 -o subset.bam input.bam

# With seed for reproducibility
samtools view -s 42.1 -o subset.bam input.bam
```

### Subsample to Target Count
```bash
# Calculate fraction needed
total=$(samtools view -c input.bam)
frac=$(echo "scale=4; 1000000 / $total" | bc)
samtools view -s "$frac" -o subset.bam input.bam
```

## pysam Python Alternative

### Basic Filtering
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('filtered.bam', 'wb', header=infile.header) as outfile:
        for read in infile:
            if read.is_unmapped:
                continue
            if read.mapping_quality < 30:
                continue
            if read.is_duplicate:
                continue
            outfile.write(read)
```

### Filter with Function
```python
import pysam

def passes_filter(read):
    if read.is_unmapped:
        return False
    if read.is_secondary or read.is_supplementary:
        return False
    if read.is_duplicate:
        return False
    if read.mapping_quality < 30:
        return False
    return True

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('filtered.bam', 'wb', header=infile.header) as outfile:
        for read in infile:
            if passes_filter(read):
                outfile.write(read)
```

### Filter by Region
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('region.bam', 'wb', header=infile.header) as outfile:
        for read in infile.fetch('chr1', 1000000, 2000000):
            outfile.write(read)
```

### Filter from BED File
```python
import pysam

def read_bed(bed_path):
    regions = []
    with open(bed_path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            regions.append((parts[0], int(parts[1]), int(parts[2])))
    return regions

regions = read_bed('targets.bed')

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('targets.bam', 'wb', header=infile.header) as outfile:
        for chrom, start, end in regions:
            for read in infile.fetch(chrom, start, end):
                outfile.write(read)
```

### Subsample
```python
import pysam
import random

random.seed(42)
fraction = 0.1

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    with pysam.AlignmentFile('subset.bam', 'wb', header=infile.header) as outfile:
        for read in infile:
            if random.random() < fraction:
                outfile.write(read)
```

## Quick Reference

| Task | samtools command |
|------|------------------|
| Mapped only | `view -F 4` |
| Unmapped only | `view -f 4` |
| Properly paired | `view -f 2` |
| Primary only | `view -F 2304` |
| No duplicates | `view -F 1024` |
| High MAPQ | `view -q 30` |
| Region | `view file.bam chr1:1-1000` |
| BED regions | `view -L file.bed` |
| Subsample 10% | `view -s 0.1` |
| Standard filter | `view -F 3332 -q 30` |

## Common Filter Combinations

| Purpose | Flags |
|---------|-------|
| Clean reads | `-F 3332 -q 30` (mapped, primary, no dups, high qual) |
| Variant calling | `-f 2 -F 3328 -q 20` (proper pair, primary, no dups) |
| Coverage analysis | `-F 1284 -q 1` (mapped, primary, no dups) |
| Count unique | `-F 2304` (primary only) |

Flag breakdowns:
- 2304 = 256 + 2048 (secondary + supplementary)
- 3328 = 256 + 1024 + 2048 (secondary + duplicate + supplementary)
- 3332 = 4 + 256 + 1024 + 2048 (unmapped + secondary + duplicate + supplementary)
- 1284 = 4 + 256 + 1024 (unmapped + secondary + duplicate)

## Related Skills

- sam-bam-basics - View and understand alignment files
- alignment-sorting - Sort before/after filtering
- alignment-indexing - Required for region filtering
- duplicate-handling - Mark duplicates before filtering
- bam-statistics - Check filter effects
