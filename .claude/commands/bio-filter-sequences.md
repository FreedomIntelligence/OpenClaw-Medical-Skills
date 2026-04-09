# bio-filter-sequences

> Filter and select sequences by criteria (length, ID, GC content, patterns) using Biopython. Use when subsetting sequences, removing unwanted records, or selecting by specific criteria.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Filter Sequences

**"Filter sequences by length, quality, or content"** → Apply boolean criteria to a stream of sequence records and write survivors to output.
- Python: generator expression with `SeqIO.parse()` + `SeqIO.write()` (BioPython)
- CLI: `seqkit seq -m 200` (SeqKit) or `awk` on FASTA

Filter and select sequences based on various criteria using Biopython.

## Required Imports

```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction
```

## Core Pattern

Use generator expressions for memory-efficient filtering:

```python
records = SeqIO.parse('input.fasta', 'fasta')
filtered = (rec for rec in records if len(rec.seq) >= 100)
SeqIO.write(filtered, 'output.fasta', 'fasta')
```

## Filter by Length

### Minimum Length
```python
records = SeqIO.parse('input.fasta', 'fasta')
long_seqs = (rec for rec in records if len(rec.seq) >= 500)
SeqIO.write(long_seqs, 'long.fasta', 'fasta')
```

### Length Range
```python
records = SeqIO.parse('input.fasta', 'fasta')
sized = (rec for rec in records if 100 <= len(rec.seq) <= 1000)
SeqIO.write(sized, 'sized.fasta', 'fasta')
```

### Remove Short Sequences
```python
min_length = 200
records = SeqIO.parse('input.fasta', 'fasta')
filtered = (rec for rec in records if len(rec.seq) >= min_length)
count = SeqIO.write(filtered, 'filtered.fasta', 'fasta')
```

## Filter by ID

### Select Specific IDs
```python
wanted_ids = {'seq1', 'seq2', 'seq3'}
records = SeqIO.parse('input.fasta', 'fasta')
selected = (rec for rec in records if rec.id in wanted_ids)
SeqIO.write(selected, 'selected.fasta', 'fasta')
```

### Select from ID File

**Goal:** Extract sequences whose IDs appear in an external list file.

**Approach:** Load IDs into a set for O(1) lookup, then stream-filter and write matches.

**Reference (BioPython 1.83+):**
```python
with open('ids.txt') as f:
    wanted_ids = {line.strip() for line in f}

records = SeqIO.parse('input.fasta', 'fasta')
selected = (rec for rec in records if rec.id in wanted_ids)
SeqIO.write(selected, 'selected.fasta', 'fasta')
```

### Exclude Specific IDs
```python
exclude_ids = {'bad_seq1', 'bad_seq2'}
records = SeqIO.parse('input.fasta', 'fasta')
kept = (rec for rec in records if rec.id not in exclude_ids)
SeqIO.write(kept, 'kept.fasta', 'fasta')
```

### Filter by ID Pattern
```python
import re

pattern = re.compile(r'^chr\d+$')  # Match chr1, chr2, etc.
records = SeqIO.parse('input.fasta', 'fasta')
chromosomes = (rec for rec in records if pattern.match(rec.id))
SeqIO.write(chromosomes, 'chromosomes.fasta', 'fasta')
```

## Filter by GC Content

```python
from Bio.SeqUtils import gc_fraction

records = SeqIO.parse('input.fasta', 'fasta')
moderate_gc = (rec for rec in records if 0.4 <= gc_fraction(rec.seq) <= 0.6)
SeqIO.write(moderate_gc, 'moderate_gc.fasta', 'fasta')
```

### High GC Sequences
```python
high_gc = (rec for rec in records if gc_fraction(rec.seq) >= 0.6)
```

### Low GC Sequences
```python
low_gc = (rec for rec in records if gc_fraction(rec.seq) <= 0.4)
```

## Filter by Sequence Content

### Remove Sequences with N's
```python
records = SeqIO.parse('input.fasta', 'fasta')
clean = (rec for rec in records if 'N' not in str(rec.seq).upper())
SeqIO.write(clean, 'clean.fasta', 'fasta')
```

### Limit N Content
```python
def n_fraction(seq):
    return str(seq).upper().count('N') / len(seq)

records = SeqIO.parse('input.fasta', 'fasta')
low_n = (rec for rec in records if n_fraction(rec.seq) < 0.05)
```

### Contains Specific Motif
```python
motif = 'GAATTC'  # EcoRI site
records = SeqIO.parse('input.fasta', 'fasta')
with_motif = (rec for rec in records if motif in str(rec.seq).upper())
SeqIO.write(with_motif, 'with_ecori.fasta', 'fasta')
```

### Regex Pattern in Sequence
```python
import re

pattern = re.compile(r'ATG.{30,100}T(AA|AG|GA)')  # ORF-like pattern
records = SeqIO.parse('input.fasta', 'fasta')
matches = (rec for rec in records if pattern.search(str(rec.seq)))
```

## Filter by Description

### Description Contains Keyword
```python
records = SeqIO.parse('input.fasta', 'fasta')
kinases = (rec for rec in records if 'kinase' in rec.description.lower())
SeqIO.write(kinases, 'kinases.fasta', 'fasta')
```

### Multiple Keywords (OR)
```python
keywords = ['kinase', 'phosphatase', 'transferase']
records = SeqIO.parse('input.fasta', 'fasta')
enzymes = (rec for rec in records if any(k in rec.description.lower() for k in keywords))
```

## Combine Multiple Filters

**Goal:** Remove sequences that fail any of several quality/content thresholds.

**Approach:** Define a predicate function that checks all criteria, apply it as a generator filter, and write survivors.

**Reference (BioPython 1.83+):**
```python
from Bio.SeqUtils import gc_fraction

def passes_filters(record):
    if len(record.seq) < 100:
        return False
    if gc_fraction(record.seq) < 0.3 or gc_fraction(record.seq) > 0.7:
        return False
    if 'N' in str(record.seq).upper():
        return False
    return True

records = SeqIO.parse('input.fasta', 'fasta')
filtered = (rec for rec in records if passes_filters(rec))
SeqIO.write(filtered, 'filtered.fasta', 'fasta')
```

## Sample Sequences

### Random Sample (requires loading all)
```python
import random

records = list(SeqIO.parse('input.fasta', 'fasta'))
sample = random.sample(records, min(100, len(records)))
SeqIO.write(sample, 'sample.fasta', 'fasta')
```

### First N Sequences
```python
from itertools import islice

records = SeqIO.parse('input.fasta', 'fasta')
first_100 = islice(records, 100)
SeqIO.write(first_100, 'first100.fasta', 'fasta')
```

### Every Nth Sequence
```python
records = SeqIO.parse('input.fasta', 'fasta')
every_10th = (rec for i, rec in enumerate(records) if i % 10 == 0)
SeqIO.write(every_10th, 'sampled.fasta', 'fasta')
```

## Split by Criteria

### Split by Length

**Goal:** Partition sequences into separate files based on a length threshold.

**Approach:** Load all records, apply list comprehension split, and write each partition.

**Reference (BioPython 1.83+):**
```python
records = list(SeqIO.parse('input.fasta', 'fasta'))
short = [r for r in records if len(r.seq) < 500]
long = [r for r in records if len(r.seq) >= 500]
SeqIO.write(short, 'short.fasta', 'fasta')
SeqIO.write(long, 'long.fasta', 'fasta')
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Generator exhausted | Used generator twice | Re-create generator or use list() |
| Empty output | Filter too strict | Check filter conditions |
| Memory error | List too large | Use generator expressions |

## Related Skills

- read-sequences - Parse sequences before filtering
- write-sequences - Write filtered sequences to output
- fastq-quality - Filter FASTQ by quality scores
- paired-end-fastq - Synchronized filtering of paired reads
- sequence-manipulation/motif-search - Filter by complex motif patterns
- alignment-files - Filter aligned reads with samtools view -f/-F
