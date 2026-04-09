# bio-alignment-files-bam-statistics

> Generate alignment statistics using samtools flagstat, stats, depth, and coverage. Use when assessing alignment quality, calculating coverage, or generating QC reports.

**Available tools:** Read, Bash

# BAM Statistics

Generate alignment statistics using samtools and pysam.

## Quick Summary Commands

| Command | Output | Speed |
|---------|--------|-------|
| `flagstat` | Read counts by category | Very fast |
| `idxstats` | Per-chromosome counts | Very fast (needs index) |
| `stats` | Comprehensive statistics | Moderate |
| `depth` | Per-position depth | Slow (full scan) |
| `coverage` | Per-region coverage | Fast (needs index) |

## samtools flagstat

Fast summary of alignment flags.

```bash
samtools flagstat input.bam
```

Output:
```
10000000 + 0 in total (QC-passed reads + QC-failed reads)
0 + 0 secondary
50000 + 0 supplementary
0 + 0 duplicates
9800000 + 0 mapped (98.00% : N/A)
9950000 + 0 paired in sequencing
4975000 + 0 read1
4975000 + 0 read2
9700000 + 0 properly paired (97.49% : N/A)
9750000 + 0 with itself and mate mapped
100000 + 0 singletons (1.01% : N/A)
25000 + 0 with mate mapped to a different chr
10000 + 0 with mate mapped to a different chr (mapQ>=5)
```

### Multi-threaded
```bash
samtools flagstat -@ 4 input.bam
```

### Output to File
```bash
samtools flagstat input.bam > flagstat.txt
```

## samtools idxstats

Per-chromosome read counts (requires index).

```bash
samtools idxstats input.bam
```

Output format: `chrom length mapped unmapped`
```
chr1    248956422    5000000    1000
chr2    242193529    4800000    800
chrM    16569        50000      100
*       0            0          150000
```

### Parse idxstats
```bash
# Total mapped reads
samtools idxstats input.bam | awk '{sum += $3} END {print sum}'

# Mitochondrial percentage
samtools idxstats input.bam | awk '
    /^chrM/ {mt = $3}
    {total += $3}
    END {print mt/total*100 "% mitochondrial"}'
```

## samtools stats

Comprehensive statistics including insert size, base quality, and more.

```bash
samtools stats input.bam > stats.txt
```

### View Summary Numbers
```bash
samtools stats input.bam | grep "^SN"
```

Key summary fields:
- `raw total sequences` - Total reads
- `reads mapped` - Mapped reads
- `reads mapped and paired` - Properly paired
- `insert size average` - Mean insert size
- `insert size standard deviation` - Insert size spread
- `average length` - Mean read length
- `error rate` - Mismatch rate

### Generate Plots (with plot-bamstats)
```bash
samtools stats input.bam > stats.txt
plot-bamstats -p plots/ stats.txt
```

### Stats for Specific Region
```bash
samtools stats input.bam chr1:1000000-2000000 > region_stats.txt
```

## samtools depth

Per-position read depth.

### Basic Depth
```bash
samtools depth input.bam > depth.txt
```

Output: `chrom position depth`

### Depth at Specific Positions
```bash
samtools depth -r chr1:1000-2000 input.bam
```

### Include Zero-Depth Positions
```bash
samtools depth -a input.bam > depth_with_zeros.txt
```

### Maximum Depth Cap
```bash
samtools depth -d 0 input.bam  # No cap (default 8000)
```

### Depth from BED Regions
```bash
samtools depth -b regions.bed input.bam
```

### Calculate Mean Depth
```bash
samtools depth input.bam | awk '{sum += $3; n++} END {print sum/n}'
```

## samtools coverage

Per-chromosome or per-region coverage statistics (faster than depth).

```bash
samtools coverage input.bam
```

Output columns:
- `#rname` - Reference name
- `startpos` - Start position
- `endpos` - End position
- `numreads` - Number of reads
- `covbases` - Bases with coverage
- `coverage` - Percentage of bases covered
- `meandepth` - Mean depth
- `meanbaseq` - Mean base quality
- `meanmapq` - Mean mapping quality

### Coverage for Specific Region
```bash
samtools coverage -r chr1:1000000-2000000 input.bam
```

### Coverage from BED
```bash
samtools coverage -b regions.bed input.bam
```

### Histogram Output
```bash
samtools coverage -m input.bam
```

## pysam Python Alternative

### Count Reads
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    total = mapped = paired = proper = 0
    for read in bam:
        total += 1
        if not read.is_unmapped:
            mapped += 1
        if read.is_paired:
            paired += 1
        if read.is_proper_pair:
            proper += 1

    print(f'Total: {total}')
    print(f'Mapped: {mapped} ({mapped/total*100:.1f}%)')
    print(f'Properly paired: {proper} ({proper/paired*100:.1f}%)')
```

### Per-Chromosome Counts
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for stat in bam.get_index_statistics():
        print(f'{stat.contig}: {stat.mapped} mapped, {stat.unmapped} unmapped')
```

### Calculate Depth at Position
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for pileup in bam.pileup('chr1', 1000000, 1000001):
        print(f'Position {pileup.pos}: depth {pileup.n}')
```

### Mean Depth in Region
```python
import pysam

def mean_depth(bam_path, chrom, start, end):
    depths = []
    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup in bam.pileup(chrom, start, end, truncate=True):
            depths.append(pileup.n)

    if depths:
        return sum(depths) / len(depths)
    return 0

depth = mean_depth('input.bam', 'chr1', 1000000, 2000000)
print(f'Mean depth: {depth:.1f}x')
```

### Coverage Statistics
```python
import pysam

def coverage_stats(bam_path, chrom, start, end):
    covered = 0
    total_depth = 0

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup in bam.pileup(chrom, start, end, truncate=True):
            covered += 1
            total_depth += pileup.n

    length = end - start
    pct_covered = covered / length * 100
    mean_depth = total_depth / length if length > 0 else 0

    return {
        'length': length,
        'covered_bases': covered,
        'pct_covered': pct_covered,
        'mean_depth': mean_depth
    }

stats = coverage_stats('input.bam', 'chr1', 1000000, 2000000)
print(f'Coverage: {stats["pct_covered"]:.1f}%')
print(f'Mean depth: {stats["mean_depth"]:.1f}x')
```

### Insert Size Distribution
```python
import pysam
from collections import Counter

insert_sizes = Counter()

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for read in bam:
        if read.is_proper_pair and read.is_read1 and read.template_length > 0:
            insert_sizes[read.template_length] += 1

sizes = list(insert_sizes.keys())
mean_insert = sum(s * c for s, c in insert_sizes.items()) / sum(insert_sizes.values())
print(f'Mean insert size: {mean_insert:.0f}')
print(f'Min: {min(sizes)}, Max: {max(sizes)}')
```

## Quick Reference

| Task | Command |
|------|---------|
| Quick counts | `samtools flagstat input.bam` |
| Per-chrom counts | `samtools idxstats input.bam` |
| Full stats | `samtools stats input.bam` |
| Coverage summary | `samtools coverage input.bam` |
| Per-position depth | `samtools depth input.bam` |
| Mean depth | `samtools depth input.bam \| awk '{sum+=$3;n++}END{print sum/n}'` |

## Common Metrics

| Metric | Good | Concerning |
|--------|------|------------|
| Mapping rate | >95% | <80% |
| Proper pair rate | >90% | <70% |
| Duplicate rate | <20% | >40% |
| Error rate | <1% | >2% |
| Coverage uniformity | <2x CV | >3x CV |

## Related Skills

- sam-bam-basics - View alignment files
- alignment-indexing - idxstats requires index
- duplicate-handling - Check duplicate rates
- alignment-filtering - Filter before stats
- sequence-io/sequence-statistics - FASTA/FASTQ statistics
