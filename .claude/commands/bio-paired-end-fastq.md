# bio-paired-end-fastq

> Handle paired-end FASTQ files (R1/R2) using Biopython. Use when working with Illumina paired reads, synchronizing pairs, interleaving/deinterleaving, or filtering paired data.

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Paired-End FASTQ

**"Work with my paired-end FASTQ files"** → Iterate R1/R2 pairs in sync, filter both mates together, interleave/deinterleave files, and auto-detect paired file naming.
- Python: `SeqIO.parse()` with `zip()` iteration (BioPython)

Handle paired-end sequencing data (R1/R2 files) using Biopython.

## Required Import

```python
from Bio import SeqIO
```

## Paired File Naming Conventions

Common patterns for paired files:
- `sample_R1.fastq` / `sample_R2.fastq`
- `sample_1.fastq` / `sample_2.fastq`
- `sample_R1_001.fastq` / `sample_R2_001.fastq`

## Iterate Pairs Together

### Basic Paired Iteration
```python
r1_records = SeqIO.parse('reads_R1.fastq', 'fastq')
r2_records = SeqIO.parse('reads_R2.fastq', 'fastq')

for r1, r2 in zip(r1_records, r2_records):
    print(f'R1: {r1.id}, R2: {r2.id}')
    print(f'Lengths: {len(r1.seq)}, {len(r2.seq)}')
```

### Verify Pair Matching
```python
def iterate_pairs(r1_file, r2_file, format='fastq'):
    r1_records = SeqIO.parse(r1_file, format)
    r2_records = SeqIO.parse(r2_file, format)

    for r1, r2 in zip(r1_records, r2_records):
        # Strip /1, /2 or .1, .2 suffixes for comparison
        r1_base = r1.id.rsplit('/', 1)[0].rsplit('.', 1)[0]
        r2_base = r2.id.rsplit('/', 1)[0].rsplit('.', 1)[0]
        if r1_base != r2_base:
            raise ValueError(f'Pair mismatch: {r1.id} vs {r2.id}')
        yield r1, r2

for r1, r2 in iterate_pairs('reads_R1.fastq', 'reads_R2.fastq'):
    process_pair(r1, r2)
```

## Filter Pairs Together

### Filter by Quality (Both Must Pass)
```python
def filter_pairs_by_quality(r1_file, r2_file, min_avg_qual=25):
    r1_records = SeqIO.parse(r1_file, 'fastq')
    r2_records = SeqIO.parse(r2_file, 'fastq')

    r1_passed, r2_passed = [], []
    for r1, r2 in zip(r1_records, r2_records):
        q1 = sum(r1.letter_annotations['phred_quality']) / len(r1.seq)
        q2 = sum(r2.letter_annotations['phred_quality']) / len(r2.seq)
        if q1 >= min_avg_qual and q2 >= min_avg_qual:
            r1_passed.append(r1)
            r2_passed.append(r2)

    return r1_passed, r2_passed

r1_good, r2_good = filter_pairs_by_quality('reads_R1.fastq', 'reads_R2.fastq')
SeqIO.write(r1_good, 'filtered_R1.fastq', 'fastq')
SeqIO.write(r2_good, 'filtered_R2.fastq', 'fastq')
```

### Filter by Length (Both Must Pass)
```python
def filter_pairs_by_length(r1_file, r2_file, min_length=50):
    r1_records = SeqIO.parse(r1_file, 'fastq')
    r2_records = SeqIO.parse(r2_file, 'fastq')

    r1_passed, r2_passed = [], []
    for r1, r2 in zip(r1_records, r2_records):
        if len(r1.seq) >= min_length and len(r2.seq) >= min_length:
            r1_passed.append(r1)
            r2_passed.append(r2)

    return r1_passed, r2_passed
```

### Memory-Efficient Paired Filtering

**Goal:** Quality-filter paired reads while maintaining R1/R2 synchronization without loading all reads into memory.

**Approach:** Stream both files in lockstep with `zip`, evaluate both mates, and write only pairs where both pass.

**Reference (BioPython 1.83+):**
```python
def filter_pairs_streaming(r1_in, r2_in, r1_out, r2_out, min_qual=25):
    r1_records = SeqIO.parse(r1_in, 'fastq')
    r2_records = SeqIO.parse(r2_in, 'fastq')

    with open(r1_out, 'w') as r1_handle, open(r2_out, 'w') as r2_handle:
        passed = 0
        for r1, r2 in zip(r1_records, r2_records):
            q1 = sum(r1.letter_annotations['phred_quality']) / len(r1.seq)
            q2 = sum(r2.letter_annotations['phred_quality']) / len(r2.seq)
            if q1 >= min_qual and q2 >= min_qual:
                SeqIO.write(r1, r1_handle, 'fastq')
                SeqIO.write(r2, r2_handle, 'fastq')
                passed += 1
    return passed

count = filter_pairs_streaming('R1.fastq', 'R2.fastq', 'R1_filt.fastq', 'R2_filt.fastq')
print(f'{count} pairs passed filtering')
```

## Interleave Pairs

### Create Interleaved File

**Goal:** Merge separate R1/R2 files into a single interleaved file (R1, R2, R1, R2, ...).

**Approach:** Zip both iterators together and yield alternating records through a generator.

**Reference (BioPython 1.83+):**
```python
def interleave_pairs(r1_file, r2_file, output_file, format='fastq'):
    r1_records = SeqIO.parse(r1_file, format)
    r2_records = SeqIO.parse(r2_file, format)

    def interleaved():
        for r1, r2 in zip(r1_records, r2_records):
            yield r1
            yield r2

    count = SeqIO.write(interleaved(), output_file, format)
    return count // 2  # Return number of pairs

pairs = interleave_pairs('reads_R1.fastq', 'reads_R2.fastq', 'reads_interleaved.fastq')
print(f'Interleaved {pairs} pairs')
```

### Interleave with Modified IDs
```python
def interleave_with_suffix(r1_file, r2_file, output_file):
    r1_records = SeqIO.parse(r1_file, 'fastq')
    r2_records = SeqIO.parse(r2_file, 'fastq')

    def interleaved():
        for r1, r2 in zip(r1_records, r2_records):
            r1.id = f'{r1.id}/1'
            r1.description = ''
            r2.id = f'{r2.id}/2'
            r2.description = ''
            yield r1
            yield r2

    SeqIO.write(interleaved(), output_file, 'fastq')
```

## Deinterleave

### Split Interleaved to Paired Files
```python
def deinterleave(interleaved_file, r1_file, r2_file, format='fastq'):
    records = SeqIO.parse(interleaved_file, format)

    r1_records = []
    r2_records = []
    for i, record in enumerate(records):
        if i % 2 == 0:
            r1_records.append(record)
        else:
            r2_records.append(record)

    SeqIO.write(r1_records, r1_file, format)
    SeqIO.write(r2_records, r2_file, format)
    return len(r1_records)

pairs = deinterleave('interleaved.fastq', 'R1.fastq', 'R2.fastq')
print(f'Deinterleaved {pairs} pairs')
```

### Memory-Efficient Deinterleave
```python
def deinterleave_streaming(interleaved_file, r1_file, r2_file, format='fastq'):
    records = SeqIO.parse(interleaved_file, format)

    with open(r1_file, 'w') as r1_h, open(r2_file, 'w') as r2_h:
        pairs = 0
        for i, record in enumerate(records):
            if i % 2 == 0:
                SeqIO.write(record, r1_h, format)
            else:
                SeqIO.write(record, r2_h, format)
                pairs += 1
    return pairs
```

## Paired Statistics

### Count and Verify Pairs
```python
def paired_stats(r1_file, r2_file):
    r1_count = sum(1 for _ in SeqIO.parse(r1_file, 'fastq'))
    r2_count = sum(1 for _ in SeqIO.parse(r2_file, 'fastq'))

    if r1_count != r2_count:
        print(f'WARNING: Unequal counts! R1={r1_count}, R2={r2_count}')
    else:
        print(f'Pairs: {r1_count}')
        print(f'Total reads: {r1_count * 2}')

    return r1_count, r2_count

paired_stats('reads_R1.fastq', 'reads_R2.fastq')
```

### Paired Quality Summary
```python
def paired_quality_summary(r1_file, r2_file):
    r1_quals, r2_quals = [], []

    r1_records = SeqIO.parse(r1_file, 'fastq')
    r2_records = SeqIO.parse(r2_file, 'fastq')

    for r1, r2 in zip(r1_records, r2_records):
        r1_quals.append(sum(r1.letter_annotations['phred_quality']) / len(r1.seq))
        r2_quals.append(sum(r2.letter_annotations['phred_quality']) / len(r2.seq))

    print(f'R1 mean quality: {sum(r1_quals)/len(r1_quals):.1f}')
    print(f'R2 mean quality: {sum(r2_quals)/len(r2_quals):.1f}')

paired_quality_summary('reads_R1.fastq', 'reads_R2.fastq')
```

## Find Paired Files

### Auto-Detect Pair from R1
```python
from pathlib import Path

def find_r2(r1_path):
    r1_path = Path(r1_path)
    name = r1_path.name

    # Try common patterns
    patterns = [
        ('_R1', '_R2'),
        ('_1', '_2'),
        ('_R1_', '_R2_'),
        ('.R1.', '.R2.'),
    ]

    for p1, p2 in patterns:
        if p1 in name:
            r2_name = name.replace(p1, p2, 1)
            r2_path = r1_path.parent / r2_name
            if r2_path.exists():
                return r2_path

    return None

r2_file = find_r2('sample_R1.fastq')
if r2_file:
    print(f'Found pair: {r2_file}')
```

### Find All Paired Files in Directory
```python
from pathlib import Path

def find_all_pairs(directory, r1_pattern='*_R1*.fastq*'):
    pairs = []
    for r1_file in Path(directory).glob(r1_pattern):
        r2_file = find_r2(r1_file)
        if r2_file:
            pairs.append((r1_file, r2_file))
    return pairs

pairs = find_all_pairs('data/')
for r1, r2 in pairs:
    print(f'{r1.name} <-> {r2.name}')
```

## Compressed Paired Files

### Handle Gzipped Pairs
```python
import gzip

def iterate_gzipped_pairs(r1_gz, r2_gz):
    with gzip.open(r1_gz, 'rt') as r1_h, gzip.open(r2_gz, 'rt') as r2_h:
        r1_records = SeqIO.parse(r1_h, 'fastq')
        r2_records = SeqIO.parse(r2_h, 'fastq')
        for r1, r2 in zip(r1_records, r2_records):
            yield r1, r2

for r1, r2 in iterate_gzipped_pairs('reads_R1.fastq.gz', 'reads_R2.fastq.gz'):
    print(r1.id, r2.id)
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Pair count mismatch | Files out of sync | Re-download or repair files |
| ID mismatch | Wrong file pairing | Check file naming conventions |
| Memory error | Large files loaded to list | Use streaming/generator approach |
| Missing R2 | Wrong naming pattern | Check `find_r2()` patterns |

## Related Skills

- read-sequences - Parse individual FASTQ files
- fastq-quality - Quality filtering before paired processing
- filter-sequences - Additional filtering criteria
- compressed-files - Handle gzipped paired files
- alignment-files - After filtering, align paired reads with bwa mem; proper pairs in BAM
