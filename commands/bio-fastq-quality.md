# bio-fastq-quality

> Work with FASTQ quality scores using Biopython. Use when analyzing read quality, filtering by quality, trimming low-quality bases, or generating quality reports.

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# FASTQ Quality Scores

**"Filter my FASTQ reads by quality score"** → Access, analyze, and filter Phred quality scores, trim low-quality bases, and generate per-position quality profiles.
- Python: `SeqIO.parse()` with `letter_annotations['phred_quality']` (BioPython)

Analyze and manipulate FASTQ quality scores using Biopython.

## Required Imports

```python
from Bio import SeqIO
from Bio.Seq import Seq
```

## Accessing Quality Scores

Quality scores are stored in `letter_annotations['phred_quality']` as a list of integers.

```python
for record in SeqIO.parse('reads.fastq', 'fastq'):
    qualities = record.letter_annotations['phred_quality']
    print(record.id, qualities[:10])  # First 10 quality scores
```

## Quality Score Basics

| Phred Score | Error Probability | Accuracy |
|-------------|-------------------|----------|
| 10 | 1 in 10 | 90% |
| 20 | 1 in 100 | 99% |
| 30 | 1 in 1000 | 99.9% |
| 40 | 1 in 10000 | 99.99% |

## Code Patterns

### Calculate Average Quality per Read
```python
for record in SeqIO.parse('reads.fastq', 'fastq'):
    quals = record.letter_annotations['phred_quality']
    avg_qual = sum(quals) / len(quals)
    print(f'{record.id}: {avg_qual:.1f}')
```

### Filter Reads by Mean Quality
```python
def high_quality_reads(records, min_avg_qual=20):
    for record in records:
        quals = record.letter_annotations['phred_quality']
        if sum(quals) / len(quals) >= min_avg_qual:
            yield record

records = SeqIO.parse('reads.fastq', 'fastq')
good_reads = high_quality_reads(records, min_avg_qual=25)
SeqIO.write(good_reads, 'filtered.fastq', 'fastq')
```

### Filter by Minimum Quality at Any Position
```python
def all_bases_above(records, min_qual=20):
    for record in records:
        if min(record.letter_annotations['phred_quality']) >= min_qual:
            yield record
```

### Trim Low-Quality Ends (3' Trimming)
```python
def trim_low_quality(record, min_qual=20):
    quals = record.letter_annotations['phred_quality']
    trim_pos = len(quals)
    for i in range(len(quals) - 1, -1, -1):
        if quals[i] >= min_qual:
            trim_pos = i + 1
            break
    return record[:trim_pos]

records = SeqIO.parse('reads.fastq', 'fastq')
trimmed = (trim_low_quality(rec) for rec in records)
SeqIO.write(trimmed, 'trimmed.fastq', 'fastq')
```

### Sliding Window Quality Trim

**Goal:** Trim a read at the first position where average quality in a sliding window drops below threshold.

**Approach:** Slide a fixed-size window across quality scores; when the window average falls below the cutoff, truncate the record at that position.

**Reference (BioPython 1.83+):**
```python
def sliding_window_trim(record, window_size=5, min_avg_qual=20):
    quals = record.letter_annotations['phred_quality']
    for i in range(len(quals) - window_size + 1):
        window = quals[i:i + window_size]
        if sum(window) / window_size < min_avg_qual:
            return record[:i] if i > 0 else None
    return record
```

### Quality Statistics Summary
```python
import statistics

all_quals = []
for record in SeqIO.parse('reads.fastq', 'fastq'):
    all_quals.extend(record.letter_annotations['phred_quality'])

print(f'Mean quality: {statistics.mean(all_quals):.1f}')
print(f'Median quality: {statistics.median(all_quals):.1f}')
print(f'Min quality: {min(all_quals)}')
print(f'Max quality: {max(all_quals)}')
```

### Per-Position Quality Profile

**Goal:** Compute mean quality at each read position to identify systematic quality drops (e.g., read-end degradation).

**Approach:** Accumulate quality scores by position across all reads, then compute per-position means.

**Reference (BioPython 1.83+):**
```python
from collections import defaultdict

position_quals = defaultdict(list)
for record in SeqIO.parse('reads.fastq', 'fastq'):
    for i, q in enumerate(record.letter_annotations['phred_quality']):
        position_quals[i].append(q)

for pos in sorted(position_quals.keys())[:20]:
    quals = position_quals[pos]
    print(f'Position {pos}: mean={sum(quals)/len(quals):.1f}')
```

### Count Reads by Quality Threshold
```python
thresholds = [20, 25, 30, 35]
counts = {t: 0 for t in thresholds}

for record in SeqIO.parse('reads.fastq', 'fastq'):
    avg = sum(record.letter_annotations['phred_quality']) / len(record.seq)
    for t in thresholds:
        if avg >= t:
            counts[t] += 1

for t, c in counts.items():
    print(f'Q>={t}: {c} reads')
```

### Remove N Bases and Low Quality Together
```python
def clean_read(record, min_qual=20):
    seq = str(record.seq)
    quals = record.letter_annotations['phred_quality']
    keep = [(s, q) for s, q in zip(seq, quals) if s != 'N' and q >= min_qual]
    if not keep:
        return None
    new_seq, new_quals = zip(*keep)
    new_record = record[:0]  # Empty copy with same metadata
    new_record.seq = Seq(''.join(new_seq))
    new_record.letter_annotations['phred_quality'] = list(new_quals)
    return new_record
```

## FASTQ Format Variants

| Variant | Format String | Quality Encoding | ASCII Range |
|---------|---------------|------------------|-------------|
| Sanger/Illumina 1.8+ | `'fastq'` | Phred+33 (standard) | 33-126 |
| Solexa | `'fastq-solexa'` | Solexa+64 | 59-126 |
| Illumina 1.3-1.7 | `'fastq-illumina'` | Phred+64 | 64-126 |

Most modern data uses standard `'fastq'` (Sanger/Illumina 1.8+).

## Quality Score Conversion

For legacy data using different quality encodings:

```python
from Bio.SeqIO.QualityIO import phred_quality_from_solexa, solexa_quality_from_phred
```

### Convert Solexa to Phred

```python
from Bio.SeqIO.QualityIO import phred_quality_from_solexa

# Convert single score
solexa_score = 10
phred_score = phred_quality_from_solexa(solexa_score)

# Convert list of scores
solexa_scores = [10, 20, 30, 40]
phred_scores = [phred_quality_from_solexa(s) for s in solexa_scores]
```

### Convert Phred to Solexa

```python
from Bio.SeqIO.QualityIO import solexa_quality_from_phred

phred_score = 30
solexa_score = solexa_quality_from_phred(phred_score)
```

### Convert Between FASTQ Variants

```python
from Bio import SeqIO

# Read old Illumina format, write standard format
records = SeqIO.parse('old_reads.fastq', 'fastq-illumina')
SeqIO.write(records, 'standard_reads.fastq', 'fastq')

# Read Solexa format, write standard format
records = SeqIO.parse('solexa_reads.fastq', 'fastq-solexa')
SeqIO.write(records, 'standard_reads.fastq', 'fastq')
```

### Auto-Detect Quality Encoding

**Goal:** Determine which FASTQ quality encoding (Sanger, Solexa, or Illumina 1.3+) a file uses.

**Approach:** Sample quality lines, find the minimum ASCII value, and compare against known offset ranges.

**Reference (BioPython 1.83+):**
```python
def detect_quality_encoding(filepath, sample_size=1000):
    min_qual = 126
    max_qual = 0
    count = 0

    with open(filepath) as f:
        for i, line in enumerate(f):
            if i % 4 == 3:  # Quality line
                for char in line.strip():
                    min_qual = min(min_qual, ord(char))
                    max_qual = max(max_qual, ord(char))
                count += 1
                if count >= sample_size:
                    break

    if min_qual < 59:
        return 'fastq'  # Sanger/Illumina 1.8+ (Phred+33)
    elif min_qual < 64:
        return 'fastq-solexa'  # Solexa+64
    else:
        return 'fastq-illumina'  # Illumina 1.3+ (Phred+64)
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `KeyError: 'phred_quality'` | Not FASTQ or wrong variant | Check format, try 'fastq-illumina' |
| Quality scores all 0 | Wrong encoding assumed | Try different FASTQ variant |
| Trimmed reads empty | Too aggressive trimming | Lower quality threshold |

## Related Skills

- read-sequences - Parse FASTQ files
- filter-sequences - Filter reads by other criteria (length, content)
- paired-end-fastq - Handle R1/R2 paired quality filtering
- sequence-statistics - Generate summary statistics including quality
- alignment-files - After filtering, align reads with bwa/bowtie2; quality scores in BAM
