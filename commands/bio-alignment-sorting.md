# bio-alignment-sorting

> Sort alignment files by coordinate or read name using samtools and pysam. Use when preparing BAM files for indexing, variant calling, or paired-end analysis.

**Available tools:** Read, Bash

# Alignment Sorting

Sort alignment files by coordinate or read name using samtools and pysam.

## Sort Orders

| Order | Flag | Use Case |
|-------|------|----------|
| Coordinate | default | Indexing, visualization, variant calling |
| Name | `-n` | Paired-end processing, fixmate, markdup |
| Tag | `-t TAG` | Sort by specific tag value |

## samtools sort

### Sort by Coordinate (Default)
```bash
samtools sort -o sorted.bam input.bam
```

### Sort by Read Name
```bash
samtools sort -n -o namesorted.bam input.bam
```

### Multi-threaded Sorting
```bash
samtools sort -@ 8 -o sorted.bam input.bam
```

### Control Memory Usage
```bash
samtools sort -m 4G -@ 4 -o sorted.bam input.bam
```

### Set Temporary Directory
```bash
samtools sort -T /tmp/sort_tmp -o sorted.bam input.bam
```

### Specify Output Format
```bash
# Output as BAM (default)
samtools sort -O bam -o sorted.bam input.bam

# Output as CRAM
samtools sort -O cram --reference ref.fa -o sorted.cram input.bam
```

### Sort by Tag
```bash
# Sort by cell barcode (10x Genomics)
samtools sort -t CB -o sorted_by_barcode.bam input.bam
```

### Pipe from Aligner
```bash
bwa mem ref.fa reads.fq | samtools sort -o aligned.bam
```

## samtools collate

Group paired reads together without full sorting (faster than name sort for some workflows):

```bash
# Collate paired reads
samtools collate -o collated.bam input.bam

# With output prefix for temp files
samtools collate -O input.bam /tmp/collate > collated.bam

# Fast mode (output to stdout)
samtools collate -u -O input.bam /tmp/collate | samtools fastq -1 R1.fq -2 R2.fq -
```

## Check Sort Order

### From Header
```bash
samtools view -H input.bam | grep "^@HD"
# SO:coordinate = coordinate sorted
# SO:queryname = name sorted
# SO:unsorted = not sorted
```

### Verify Sorted
```bash
# Check if coordinate sorted (returns 0 if sorted)
samtools view input.bam | awk '$4 < prev {exit 1} {prev=$4}'
```

## pysam Python Alternative

### Sort with pysam
```python
import pysam

pysam.sort('-o', 'sorted.bam', 'input.bam')
```

### Sort by Name
```python
pysam.sort('-n', '-o', 'namesorted.bam', 'input.bam')
```

### Sort with Options
```python
pysam.sort('-@', '4', '-m', '2G', '-o', 'sorted.bam', 'input.bam')
```

### Manual Sorting in Python
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as infile:
    header = infile.header
    reads = list(infile)

reads.sort(key=lambda r: (r.reference_id, r.reference_start))

with pysam.AlignmentFile('sorted.bam', 'wb', header=header) as outfile:
    for read in reads:
        outfile.write(read)
```

### Check Sort Order in pysam
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    hd = bam.header.get('HD', {})
    sort_order = hd.get('SO', 'unknown')
    print(f'Sort order: {sort_order}')
```

### Stream Sort from Aligner
For streaming from aligners, use shell pipes (simpler and more reliable):
```python
import subprocess

subprocess.run(
    'bwa mem ref.fa reads.fq | samtools sort -o aligned.bam',
    shell=True, check=True
)
```

Or use pysam with a named pipe:
```python
import os
import pysam
import subprocess

os.mkfifo('aligner.pipe')
try:
    aligner = subprocess.Popen(['bwa', 'mem', 'ref.fa', 'reads.fq'],
                               stdout=open('aligner.pipe', 'w'))
    pysam.sort('-o', 'aligned.bam', 'aligner.pipe')
    aligner.wait()
finally:
    os.unlink('aligner.pipe')
```

## samtools merge

Combine multiple BAM files into one.

### Basic Merge
```bash
samtools merge merged.bam sample1.bam sample2.bam sample3.bam
```

### Merge with Threads
```bash
samtools merge -@ 4 merged.bam sample1.bam sample2.bam sample3.bam
```

### Merge from File List
```bash
# files.txt contains one BAM path per line
samtools merge -b files.txt merged.bam
```

### Force Overwrite
```bash
samtools merge -f merged.bam sample1.bam sample2.bam
```

### Merge Specific Region
```bash
samtools merge -R chr1:1000000-2000000 merged_region.bam sample1.bam sample2.bam
```

### pysam Merge
```python
import pysam

pysam.merge('-f', 'merged.bam', 'sample1.bam', 'sample2.bam', 'sample3.bam')
```

## Common Workflows

### Align and Sort
```bash
bwa mem -t 8 ref.fa R1.fq R2.fq | samtools sort -@ 4 -o aligned.bam
samtools index aligned.bam
```

### Re-sort by Name for Duplicate Marking
```bash
# Full workflow: sort by name, fixmate, sort by coord, markdup
samtools sort -n -o namesorted.bam input.bam
samtools fixmate -m namesorted.bam fixmate.bam
samtools sort -o sorted.bam fixmate.bam
samtools markdup sorted.bam marked.bam
```

### Convert Name-sorted to Coordinate-sorted
```bash
samtools sort -o coord_sorted.bam name_sorted.bam
samtools index coord_sorted.bam
```

### Extract FASTQ from Sorted BAM
```bash
# Collate first to group pairs
samtools collate -u -O input.bam /tmp/collate | \
    samtools fastq -1 R1.fq -2 R2.fq -0 /dev/null -s /dev/null -
```

## Performance Tips

| Parameter | Effect |
|-----------|--------|
| `-@ N` | Use N additional threads |
| `-m SIZE` | Memory per thread (e.g., 4G) |
| `-T PREFIX` | Temp file location (use fast disk) |
| `-l LEVEL` | Compression level (1-9, default 6) |

### Optimal Settings for Large Files
```bash
# Use 8 threads, 4GB per thread, low compression for speed
samtools sort -@ 8 -m 4G -l 1 -o sorted.bam input.bam
```

## Quick Reference

| Task | Command |
|------|---------|
| Sort by coordinate | `samtools sort -o out.bam in.bam` |
| Sort by name | `samtools sort -n -o out.bam in.bam` |
| Sort with threads | `samtools sort -@ 8 -o out.bam in.bam` |
| Collate pairs | `samtools collate -o out.bam in.bam` |
| Merge BAMs | `samtools merge out.bam in1.bam in2.bam` |
| Check sort order | `samtools view -H in.bam \| grep "^@HD"` |
| Sort + index | `samtools sort -o out.bam in.bam && samtools index out.bam` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `out of memory` | Insufficient RAM | Use `-m` to limit per-thread memory |
| `disk full` | Temp files filling disk | Use `-T` to specify different location |
| `truncated file` | Interrupted sort | Re-run sort from original |

## Related Skills

- sam-bam-basics - View and convert alignment files
- alignment-indexing - Index after coordinate sorting
- duplicate-handling - Requires name-sorted input for fixmate
- alignment-filtering - Filter before or after sorting
