# bio-alignment-indexing

> Create and use BAI/CSI indices for BAM/CRAM files using samtools and pysam. Use when enabling random access to alignment files or fetching specific genomic regions.

**Available tools:** Read, Bash

# Alignment Indexing

Create indices for random access to alignment files using samtools and pysam.

## Index Types

| Index | Extension | Use Case |
|-------|-----------|----------|
| BAI | `.bai` | Standard BAM index, chromosomes < 512 Mbp |
| CSI | `.csi` | Large chromosomes, custom bin sizes |
| CRAI | `.crai` | CRAM index |

## samtools index

### Create BAI Index
```bash
samtools index input.bam
# Creates input.bam.bai
```

### Create CSI Index
```bash
samtools index -c input.bam
# Creates input.bam.csi
```

### Specify Output Name
```bash
samtools index input.bam output.bai
```

### Multi-threaded Indexing
```bash
samtools index -@ 4 input.bam
```

### Index CRAM
```bash
samtools index input.cram
# Creates input.cram.crai
```

## Index Requirements

Indexing requires coordinate-sorted files:
```bash
# Check sort order
samtools view -H input.bam | grep "^@HD"
# Should show SO:coordinate

# Sort if needed, then index
samtools sort -o sorted.bam input.bam
samtools index sorted.bam
```

## Using Indices for Region Access

### samtools view with Region
```bash
# Requires index file present
samtools view input.bam chr1:1000000-2000000
```

### Multiple Regions
```bash
samtools view input.bam chr1:1000-2000 chr2:3000-4000
```

### Regions from BED File
```bash
samtools view -L regions.bed input.bam
```

## pysam Python Alternative

### Create Index
```python
import pysam

pysam.index('input.bam')
# Creates input.bam.bai
```

### Create CSI Index
```python
pysam.index('input.bam', 'input.bam.csi', csi=True)
```

### Fetch with Index
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    # fetch() requires index
    for read in bam.fetch('chr1', 1000000, 2000000):
        print(read.query_name)
```

### Check if Indexed
```python
import pysam
from pathlib import Path

def is_indexed(bam_path):
    bam_path = Path(bam_path)
    return (bam_path.with_suffix('.bam.bai').exists() or
            Path(str(bam_path) + '.bai').exists() or
            bam_path.with_suffix('.bam.csi').exists())

if not is_indexed('input.bam'):
    pysam.index('input.bam')
```

### Fetch Multiple Regions
```python
regions = [('chr1', 1000, 2000), ('chr1', 5000, 6000), ('chr2', 1000, 2000)]

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for chrom, start, end in regions:
        count = sum(1 for _ in bam.fetch(chrom, start, end))
        print(f'{chrom}:{start}-{end}: {count} reads')
```

### Count Reads in Region
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    count = bam.count('chr1', 1000000, 2000000)
    print(f'Reads in region: {count}')
```

### Get Reads Covering Position
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for read in bam.fetch('chr1', 1000000, 1000001):
        if read.reference_start <= 1000000 < read.reference_end:
            print(f'{read.query_name} covers position 1000000')
```

## Index File Locations

samtools looks for indices in two locations:
```
input.bam.bai   # Standard location
input.bai       # Alternative location
```

For CRAM:
```
input.cram.crai
```

## idxstats - Index Statistics

### Get Per-Chromosome Counts
```bash
samtools idxstats input.bam
```

Output format:
```
chr1    248956422    5000000    0
chr2    242193529    4500000    0
*       0            0          10000
```

Columns: reference name, length, mapped reads, unmapped reads

### Sum Total Mapped Reads
```bash
samtools idxstats input.bam | awk '{sum += $3} END {print sum}'
```

### pysam idxstats
```python
with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for stat in bam.get_index_statistics():
        print(f'{stat.contig}: {stat.mapped} mapped, {stat.unmapped} unmapped')
```

## FASTA Index (faidx)

Related but different - index reference FASTA for random access:

```bash
samtools faidx reference.fa
# Creates reference.fa.fai

# Fetch region from indexed FASTA
samtools faidx reference.fa chr1:1000-2000
```

### pysam FastaFile
```python
with pysam.FastaFile('reference.fa') as ref:
    seq = ref.fetch('chr1', 1000, 2000)
    print(seq)
```

## Quick Reference

| Task | samtools | pysam |
|------|----------|-------|
| Create BAI | `samtools index file.bam` | `pysam.index('file.bam')` |
| Create CSI | `samtools index -c file.bam` | `pysam.index('file.bam', csi=True)` |
| Fetch region | `samtools view file.bam chr1:1-1000` | `bam.fetch('chr1', 0, 1000)` |
| Count in region | `samtools view -c file.bam chr1:1-1000` | `bam.count('chr1', 0, 1000)` |
| Index stats | `samtools idxstats file.bam` | `bam.get_index_statistics()` |
| Index FASTA | `samtools faidx ref.fa` | Automatic with FastaFile |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `random alignment retrieval only works for indexed BAM` | Missing index | Run `samtools index file.bam` |
| `file is not sorted` | Unsorted BAM | Sort first with `samtools sort` |
| `chromosome not found` | Wrong chromosome name | Check names with `samtools view -H` |

## Related Skills

- sam-bam-basics - View and convert alignment files
- alignment-sorting - Sort BAM files (required before indexing)
- alignment-filtering - Filter by regions using index
- bam-statistics - Use idxstats for quick counts
- sequence-io/read-sequences - Index FASTA with SeqIO.index_db()
