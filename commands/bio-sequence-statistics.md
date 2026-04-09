# bio-sequence-statistics

> Calculate sequence statistics (N50, length distribution, GC content, summary reports) using Biopython. Use when analyzing sequence datasets, generating QC reports, or comparing assemblies.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Sequence Statistics

**"Calculate N50 and other assembly statistics"** → Compute sequence count, length distribution, N50/L50, GC content, and nucleotide composition for FASTA datasets.
- Python: `SeqIO.parse()`, `gc_fraction()` (BioPython)

Calculate comprehensive statistics for sequence datasets using Biopython.

## Required Imports

```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction
import statistics
```

## Basic Statistics

### Sequence Count and Total Length
```python
records = list(SeqIO.parse('sequences.fasta', 'fasta'))
total_seqs = len(records)
total_bp = sum(len(r.seq) for r in records)
print(f'Sequences: {total_seqs}')
print(f'Total bp: {total_bp:,}')
```

### Length Statistics
```python
lengths = [len(r.seq) for r in SeqIO.parse('sequences.fasta', 'fasta')]

print(f'Count: {len(lengths)}')
print(f'Total: {sum(lengths):,} bp')
print(f'Min: {min(lengths):,} bp')
print(f'Max: {max(lengths):,} bp')
print(f'Mean: {statistics.mean(lengths):,.1f} bp')
print(f'Median: {statistics.median(lengths):,.1f} bp')
print(f'Std Dev: {statistics.stdev(lengths):,.1f} bp')
```

## N50 and Nx Statistics

### Calculate N50
```python
def calculate_n50(lengths):
    sorted_lengths = sorted(lengths, reverse=True)
    total = sum(sorted_lengths)
    cumsum = 0
    for length in sorted_lengths:
        cumsum += length
        if cumsum >= total * 0.5:
            return length
    return 0

lengths = [len(r.seq) for r in SeqIO.parse('assembly.fasta', 'fasta')]
n50 = calculate_n50(lengths)
print(f'N50: {n50:,} bp')
```

### Calculate Any Nx Value
```python
def calculate_nx(lengths, x):
    '''Calculate Nx where x is percentage (e.g., 50 for N50, 90 for N90)'''
    sorted_lengths = sorted(lengths, reverse=True)
    total = sum(sorted_lengths)
    threshold = total * (x / 100)
    cumsum = 0
    for length in sorted_lengths:
        cumsum += length
        if cumsum >= threshold:
            return length
    return 0

lengths = [len(r.seq) for r in SeqIO.parse('assembly.fasta', 'fasta')]
print(f'N50: {calculate_nx(lengths, 50):,} bp')
print(f'N75: {calculate_nx(lengths, 75):,} bp')
print(f'N90: {calculate_nx(lengths, 90):,} bp')
```

### L50 (Number of Sequences in N50)
```python
def calculate_l50(lengths):
    sorted_lengths = sorted(lengths, reverse=True)
    total = sum(sorted_lengths)
    cumsum = 0
    for i, length in enumerate(sorted_lengths, 1):
        cumsum += length
        if cumsum >= total * 0.5:
            return i
    return len(sorted_lengths)

lengths = [len(r.seq) for r in SeqIO.parse('assembly.fasta', 'fasta')]
print(f'L50: {calculate_l50(lengths)} sequences')
```

## GC Content Statistics

### Overall GC Content
```python
from Bio.SeqUtils import gc_fraction

total_gc = 0
total_len = 0
for record in SeqIO.parse('sequences.fasta', 'fasta'):
    total_gc += gc_fraction(record.seq) * len(record.seq)
    total_len += len(record.seq)

overall_gc = total_gc / total_len
print(f'Overall GC: {overall_gc:.1%}')
```

### Per-Sequence GC Distribution
```python
gc_values = [gc_fraction(r.seq) for r in SeqIO.parse('sequences.fasta', 'fasta')]

print(f'Mean GC: {statistics.mean(gc_values):.1%}')
print(f'Median GC: {statistics.median(gc_values):.1%}')
print(f'Min GC: {min(gc_values):.1%}')
print(f'Max GC: {max(gc_values):.1%}')
print(f'Std Dev: {statistics.stdev(gc_values):.2%}')
```

### GC Content Histogram Data
```python
from collections import Counter

gc_values = [gc_fraction(r.seq) for r in SeqIO.parse('sequences.fasta', 'fasta')]
bins = [int(gc * 100 // 5) * 5 for gc in gc_values]  # 5% bins
histogram = Counter(bins)

for gc_bin in sorted(histogram.keys()):
    count = histogram[gc_bin]
    print(f'{gc_bin}-{gc_bin+5}%: {count} sequences')
```

## Length Distribution

### Length Histogram Data
```python
from collections import Counter

lengths = [len(r.seq) for r in SeqIO.parse('sequences.fasta', 'fasta')]

# Define bins (e.g., 0-100, 100-200, etc.)
bin_size = 100
bins = [(l // bin_size) * bin_size for l in lengths]
histogram = Counter(bins)

for length_bin in sorted(histogram.keys()):
    count = histogram[length_bin]
    print(f'{length_bin}-{length_bin + bin_size}: {count}')
```

### Length Percentiles
```python
import statistics

lengths = sorted(len(r.seq) for r in SeqIO.parse('sequences.fasta', 'fasta'))

percentiles = [10, 25, 50, 75, 90, 95, 99]
for p in percentiles:
    idx = int(len(lengths) * p / 100)
    print(f'P{p}: {lengths[idx]:,} bp')
```

## Comprehensive Summary Report

**Goal:** Generate a complete QC summary (counts, lengths, N50, GC) for any FASTA file.

**Approach:** Load all records, compute length and GC arrays, derive N50/L50 from cumulative sorted lengths, and package into a dictionary.

**Reference (BioPython 1.83+):**
```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction
import statistics

def sequence_summary(fasta_file):
    records = list(SeqIO.parse(fasta_file, 'fasta'))
    lengths = [len(r.seq) for r in records]
    gc_values = [gc_fraction(r.seq) for r in records]

    sorted_lengths = sorted(lengths, reverse=True)
    total_bp = sum(lengths)

    cumsum = 0
    n50 = 0
    l50 = 0
    for i, length in enumerate(sorted_lengths, 1):
        cumsum += length
        if cumsum >= total_bp * 0.5 and n50 == 0:
            n50 = length
            l50 = i

    return {
        'file': fasta_file,
        'sequences': len(records),
        'total_bp': total_bp,
        'min_length': min(lengths),
        'max_length': max(lengths),
        'mean_length': statistics.mean(lengths),
        'median_length': statistics.median(lengths),
        'n50': n50,
        'l50': l50,
        'gc_mean': statistics.mean(gc_values),
        'gc_std': statistics.stdev(gc_values) if len(gc_values) > 1 else 0
    }

stats = sequence_summary('assembly.fasta')
print(f'File: {stats["file"]}')
print(f'Sequences: {stats["sequences"]:,}')
print(f'Total bp: {stats["total_bp"]:,}')
print(f'Min/Max: {stats["min_length"]:,} / {stats["max_length"]:,} bp')
print(f'Mean: {stats["mean_length"]:,.1f} bp')
print(f'Median: {stats["median_length"]:,.1f} bp')
print(f'N50: {stats["n50"]:,} bp (L50: {stats["l50"]})')
print(f'GC: {stats["gc_mean"]:.1%} (+/- {stats["gc_std"]:.1%})')
```

## Compare Multiple Assemblies

**Goal:** Generate a side-by-side comparison table of key metrics across multiple assembly files.

**Approach:** Run `sequence_summary` on each file and format results into an aligned table.

**Reference (BioPython 1.83+):**
```python
from pathlib import Path

def compare_assemblies(fasta_files):
    results = []
    for fasta_file in fasta_files:
        stats = sequence_summary(str(fasta_file))
        results.append(stats)
    return results

files = list(Path('assemblies/').glob('*.fasta'))
comparisons = compare_assemblies(files)

print(f'{"File":<30} {"Seqs":>10} {"Total bp":>15} {"N50":>12}')
print('-' * 70)
for stats in comparisons:
    print(f'{Path(stats["file"]).name:<30} {stats["sequences"]:>10,} {stats["total_bp"]:>15,} {stats["n50"]:>12,}')
```

## Export to CSV

```python
import csv
from pathlib import Path

def export_stats_csv(fasta_files, output_csv):
    fieldnames = ['file', 'sequences', 'total_bp', 'min_length', 'max_length',
                  'mean_length', 'median_length', 'n50', 'l50', 'gc_mean', 'gc_std']

    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for fasta_file in fasta_files:
            stats = sequence_summary(str(fasta_file))
            writer.writerow(stats)

files = list(Path('assemblies/').glob('*.fasta'))
export_stats_csv(files, 'assembly_stats.csv')
```

## Nucleotide Composition

```python
from collections import Counter

def nucleotide_composition(fasta_file):
    total_counts = Counter()
    for record in SeqIO.parse(fasta_file, 'fasta'):
        total_counts.update(str(record.seq).upper())

    total = sum(total_counts.values())
    return {base: count / total for base, count in total_counts.items()}

comp = nucleotide_composition('sequences.fasta')
for base in ['A', 'T', 'G', 'C', 'N']:
    if base in comp:
        print(f'{base}: {comp[base]:.2%}')
```

## Common Metrics Reference

| Metric | Description |
|--------|-------------|
| N50 | Length where 50% of total bases are in sequences >= this length |
| L50 | Number of sequences needed to reach N50 |
| N90 | Length where 90% of total bases are in sequences >= this length |
| GC% | Proportion of G+C bases |
| Contiguity | Higher N50 = more contiguous assembly |

## Related Skills

- read-sequences - Parse sequences for statistics calculation
- batch-processing - Calculate stats across multiple files
- fastq-quality - Quality score statistics for FASTQ files
- sequence-manipulation/sequence-properties - Per-sequence GC content and properties
- alignment-files - samtools stats/flagstat for alignment statistics
