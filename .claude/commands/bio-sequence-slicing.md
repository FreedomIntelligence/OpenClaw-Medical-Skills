# bio-sequence-slicing

> Slice, extract, and concatenate biological sequences using Biopython. Use when extracting subsequences, joining sequences, or manipulating sequence regions by position.

**Available tools:** Read, Bash

# Sequence Slicing

Extract, slice, and concatenate sequences using Biopython's Seq objects.

## Required Import

```python
from Bio.Seq import Seq
```

## Core Operations

### Indexing (Single Position)

```python
seq = Seq('ATGCGATCG')
seq[0]      # 'A' - first base (0-indexed)
seq[-1]     # 'G' - last base
seq[3]      # 'C' - fourth base
```

### Slicing (Extract Region)

```python
seq = Seq('ATGCGATCGATCG')
seq[0:3]     # Seq('ATG') - first 3 bases
seq[3:6]     # Seq('CGA') - positions 3-5
seq[:5]      # Seq('ATGCG') - first 5
seq[-5:]     # Seq('GATCG') - last 5
seq[::2]     # Seq('AGGTGTG') - every 2nd base
seq[::-1]    # Seq('GCTAGCTAGCGTA') - reversed
```

**Note:** Slicing returns a Seq object, not a string.

### Concatenation

```python
seq1 = Seq('ATGC')
seq2 = Seq('GGGG')
combined = seq1 + seq2  # Seq('ATGCGGGG')
```

Can also concatenate with strings:
```python
seq = Seq('ATGC')
extended = seq + 'NNNN'  # Seq('ATGCNNNN')
```

## Code Patterns

### Extract CDS by Coordinates

```python
genome = Seq('NNNNATGCGATCGATCGTAANNN')
cds_start, cds_end = 4, 21
cds = genome[cds_start:cds_end]
```

### Extract with 1-Based Coordinates

Biology often uses 1-based coordinates. Convert to 0-based:

```python
def extract_1based(seq, start, end):
    '''Extract using 1-based inclusive coordinates'''
    return seq[start - 1:end]

genome = Seq('ATGCGATCGATCG')
region = extract_1based(genome, 1, 3)  # Seq('ATG')
```

### Split Sequence into Codons

```python
def split_codons(seq):
    return [seq[i:i+3] for i in range(0, len(seq) - len(seq) % 3, 3)]

seq = Seq('ATGCGATCGATCG')
codons = split_codons(seq)  # [Seq('ATG'), Seq('CGA'), ...]
```

### Split into Fixed-Length Chunks

```python
def chunk_sequence(seq, size):
    return [seq[i:i+size] for i in range(0, len(seq), size)]

seq = Seq('ATGCGATCGATCGATCGATCG')
chunks = chunk_sequence(seq, 10)
```

### Join Sequences with Linker

```python
seqs = [Seq('ATGC'), Seq('GGGG'), Seq('TTTT')]
linker = Seq('NNN')
joined = linker.join(seqs)  # Seq('ATGCNNNGGGGNNTTTT')
```

Or manually:
```python
linker = 'NNN'
joined = Seq(linker.join(str(s) for s in seqs))
```

### Extract Multiple Regions

```python
def extract_regions(seq, regions):
    '''Extract and concatenate multiple regions'''
    return sum((seq[start:end] for start, end in regions), Seq(''))

exon_coords = [(0, 50), (100, 150), (200, 250)]
mrna = extract_regions(genomic_seq, exon_coords)
```

### Extract Flanking Regions

```python
def get_flanking(seq, position, flank_size):
    '''Get sequence around a position'''
    start = max(0, position - flank_size)
    end = min(len(seq), position + flank_size + 1)
    return seq[start:end]

seq = Seq('ATGCGATCGATCGATCGATCG')
flanking = get_flanking(seq, 10, 5)  # 5 bp on each side of position 10
```

### Tile Sequence into Overlapping Windows

```python
def sliding_windows(seq, window_size, step=1):
    for i in range(0, len(seq) - window_size + 1, step):
        yield seq[i:i + window_size]

seq = Seq('ATGCGATCGATCG')
for window in sliding_windows(seq, 5, 2):
    print(window)
```

### Extract Feature from SeqRecord

```python
from Bio import SeqIO

for record in SeqIO.parse('sequence.gb', 'genbank'):
    for feature in record.features:
        if feature.type == 'CDS':
            cds_seq = feature.extract(record.seq)
            print(f'{feature.qualifiers.get("gene", ["?"])[0]}: {cds_seq[:30]}...')
```

### Create New SeqRecord from Slice

```python
from Bio.SeqRecord import SeqRecord

original = SeqRecord(Seq('ATGCGATCGATCGATCG'), id='full', description='Full sequence')
subset = SeqRecord(original.seq[5:15], id='subset', description=f'Positions 5-15 of {original.id}')
```

## Coordinate Systems

| System | Position 1 | Example |
|--------|------------|---------|
| 0-based (Python) | Index 0 | `seq[0:3]` gets positions 0, 1, 2 |
| 1-based (Biology) | Index 1 | Position 1-3 = `seq[0:3]` |
| 0-based half-open | Start inclusive, end exclusive | Standard Python slicing |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `IndexError` | Index out of range | Check sequence length first |
| Unexpected length | Off-by-one error | Remember end index is exclusive |
| Empty result | Start >= end | Check coordinate order |
| Wrong positions | 1-based vs 0-based confusion | Convert coordinates explicitly |

## Decision Tree

```
Need to extract or combine sequences?
├── Single position?
│   └── Use indexing: seq[i]
├── Contiguous region?
│   └── Use slicing: seq[start:end]
├── Multiple non-contiguous regions?
│   └── Extract each, concatenate with +
├── Join sequences?
│   ├── No linker: seq1 + seq2
│   └── With linker: linker.join(seqs)
├── Split into parts?
│   └── List comprehension with slicing
└── From GenBank features?
    └── Use feature.extract(record.seq)
```

## Related Skills

- seq-objects - Create Seq and SeqRecord objects
- sequence-io/read-sequences - Parse GenBank files with features to extract
- transcription-translation - Translate extracted CDS regions
- alignment-files - Extract sequences from BAM using samtools fasta/fastq
