# bio-duplicate-handling

> Mark and remove PCR/optical duplicates using samtools fixmate and markdup. Use when preparing alignments for variant calling or when duplicate reads would bias analysis.

**Available tools:** Read, Bash

# Duplicate Handling

Mark and remove PCR/optical duplicates using samtools.

## Why Remove Duplicates?

PCR duplicates are identical copies of the same original molecule, created during library preparation. They:
- Inflate coverage artificially
- Bias allele frequencies
- Can create false positive variant calls

Optical duplicates are clusters read multiple times due to their proximity on the flowcell.

## Duplicate Marking Workflow

The standard samtools workflow requires multiple steps:

```bash
# 1. Sort by name (required for fixmate)
samtools sort -n -o namesort.bam input.bam

# 2. Add mate information with fixmate
samtools fixmate -m namesort.bam fixmate.bam

# 3. Sort by coordinate (required for markdup)
samtools sort -o coordsort.bam fixmate.bam

# 4. Mark duplicates
samtools markdup coordsort.bam marked.bam

# 5. Index result
samtools index marked.bam
```

### Pipeline Version
```bash
samtools sort -n input.bam | \
    samtools fixmate -m - - | \
    samtools sort - | \
    samtools markdup - marked.bam

samtools index marked.bam
```

## samtools fixmate

Adds mate information required by markdup. Must be run on name-sorted BAM.

### Basic Usage
```bash
samtools fixmate namesorted.bam fixmate.bam
```

### Add Mate Score Tag (-m)
```bash
# Required for markdup to work correctly
samtools fixmate -m namesorted.bam fixmate.bam
```

### Multi-threaded
```bash
samtools fixmate -m -@ 4 namesorted.bam fixmate.bam
```

### Remove Secondary/Unmapped
```bash
samtools fixmate -r -m namesorted.bam fixmate.bam
```

## samtools markdup

Marks or removes duplicate alignments. Requires coordinate-sorted BAM with mate tags from fixmate.

### Mark Duplicates (Keep in File)
```bash
samtools markdup input.bam marked.bam
```

### Remove Duplicates
```bash
samtools markdup -r input.bam deduped.bam
```

### Output Statistics
```bash
samtools markdup -s input.bam marked.bam 2> markdup_stats.txt
```

### Optical Duplicate Distance
```bash
# Set pixel distance for optical duplicate detection (default: 100)
samtools markdup -d 2500 input.bam marked.bam
```

### Multi-threaded
```bash
samtools markdup -@ 4 input.bam marked.bam
```

### Write Stats to File
```bash
samtools markdup -f stats.txt input.bam marked.bam
```

## Duplicate Statistics

### Check Duplicate Rate
```bash
samtools flagstat marked.bam
# Look for "duplicates" line
```

### Count Duplicates
```bash
# Count reads with duplicate flag
samtools view -c -f 1024 marked.bam
```

### Percentage Duplicates
```bash
total=$(samtools view -c marked.bam)
dups=$(samtools view -c -f 1024 marked.bam)
echo "scale=2; $dups * 100 / $total" | bc
```

## pysam Python Alternative

### Full Pipeline
```python
import pysam

# Sort by name
pysam.sort('-n', '-o', 'namesort.bam', 'input.bam')

# Fixmate
pysam.fixmate('-m', 'namesort.bam', 'fixmate.bam')

# Sort by coordinate
pysam.sort('-o', 'coordsort.bam', 'fixmate.bam')

# Mark duplicates
pysam.markdup('coordsort.bam', 'marked.bam')

# Index
pysam.index('marked.bam')
```

### Check Duplicate Flag
```python
import pysam

with pysam.AlignmentFile('marked.bam', 'rb') as bam:
    total = 0
    duplicates = 0
    for read in bam:
        total += 1
        if read.is_duplicate:
            duplicates += 1

    print(f'Total: {total}')
    print(f'Duplicates: {duplicates}')
    print(f'Rate: {duplicates/total*100:.2f}%')
```

### Filter Out Duplicates
```python
import pysam

with pysam.AlignmentFile('marked.bam', 'rb') as infile:
    with pysam.AlignmentFile('nodup.bam', 'wb', header=infile.header) as outfile:
        for read in infile:
            if not read.is_duplicate:
                outfile.write(read)
```

### Mark Duplicates Manually (Simple Case)
```python
import pysam
from collections import defaultdict

def simple_markdup(input_bam, output_bam):
    seen = defaultdict(set)

    with pysam.AlignmentFile(input_bam, 'rb') as infile:
        with pysam.AlignmentFile(output_bam, 'wb', header=infile.header) as outfile:
            for read in infile:
                if read.is_unmapped:
                    outfile.write(read)
                    continue

                key = (read.reference_id, read.reference_start, read.is_reverse,
                       read.next_reference_id, read.next_reference_start)

                if key in seen:
                    read.is_duplicate = True
                else:
                    seen[key].add(read.query_name)

                outfile.write(read)

simple_markdup('sorted.bam', 'marked.bam')
```

## Alternative: From Aligner

Some aligners can mark duplicates directly:

### BWA-MEM2 with samblaster
```bash
bwa-mem2 mem ref.fa R1.fq R2.fq | \
    samblaster | \
    samtools sort -o marked.bam
```

### Using Picard (Alternative Tool)
```bash
java -jar picard.jar MarkDuplicates \
    I=input.bam \
    O=marked.bam \
    M=metrics.txt
```

## Quick Reference

| Task | Command |
|------|---------|
| Full workflow | `sort -n \| fixmate -m \| sort \| markdup` |
| Mark duplicates | `samtools markdup in.bam out.bam` |
| Remove duplicates | `samtools markdup -r in.bam out.bam` |
| Count duplicates | `samtools view -c -f 1024 marked.bam` |
| View non-duplicates | `samtools view -F 1024 marked.bam` |
| Get stats | `samtools markdup -s in.bam out.bam` |

## Duplicate FLAG

| Flag | Value | Meaning |
|------|-------|---------|
| 0x400 | 1024 | PCR or optical duplicate |

### Filter Commands
```bash
# View only duplicates
samtools view -f 1024 marked.bam

# View non-duplicates only
samtools view -F 1024 marked.bam

# Count non-duplicates
samtools view -c -F 1024 marked.bam
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `mate not found` | Input not name-sorted | Run `samtools sort -n` first |
| `no MC tag` | fixmate not run with -m | Re-run fixmate with `-m` flag |
| `not coordinate sorted` | Input to markdup not sorted | Run `samtools sort` after fixmate |

## Related Skills

- alignment-sorting - Sort by name/coordinate for workflow
- alignment-filtering - Filter duplicates from output
- bam-statistics - Check duplicate rates with flagstat
- variant-calling - Duplicate marking before calling
