# bio-alignment-msa-parsing

> Parse and analyze multiple sequence alignments using Biopython. Extract sequences, identify conserved regions, analyze gaps, work with annotations, and manipulate alignment data for downstream analysis. Use when parsing or manipulating multiple sequence alignments.

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# MSA Parsing and Analysis

Parse multiple sequence alignments to extract information, analyze content, and prepare for downstream analysis.

## Required Import

**Goal:** Load modules for parsing, analyzing, and manipulating multiple sequence alignments.

**Approach:** Import AlignIO for reading, Counter for column analysis, and alignment classes for constructing modified alignments.

```python
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from collections import Counter
```

## Loading Alignments

**Goal:** Read an MSA file and inspect its dimensions.

**Approach:** Use `AlignIO.read()` specifying the file and format.

```python
from Bio import AlignIO

alignment = AlignIO.read('alignment.fasta', 'fasta')
print(f'{len(alignment)} sequences, {alignment.get_alignment_length()} columns')
```

## Extracting Sequence Information

### Get All Sequence IDs
```python
seq_ids = [record.id for record in alignment]
```

### Get Sequences as Strings
```python
sequences = [str(record.seq) for record in alignment]
```

### Get Sequence by ID
```python
def get_sequence_by_id(alignment, seq_id):
    for record in alignment:
        if record.id == seq_id:
            return record
    return None

target = get_sequence_by_id(alignment, 'species_A')
```

### Access Descriptions and Annotations
```python
for record in alignment:
    print(f'ID: {record.id}')
    print(f'Description: {record.description}')
    print(f'Annotations: {record.annotations}')
```

## Column-wise Analysis

**Goal:** Analyze alignment content column by column to assess composition, conservation, and variability.

**Approach:** Use column indexing (`alignment[:, idx]`) and Counter to examine character frequencies at each position.

### Get Single Column
```python
column_5 = alignment[:, 5]  # Returns string of characters at position 5
print(column_5)  # e.g., 'AAAGA'
```

### Iterate Over Columns
```python
for col_idx in range(alignment.get_alignment_length()):
    column = alignment[:, col_idx]
    print(f'Column {col_idx}: {column}')
```

### Count Characters in Column
```python
from collections import Counter

def column_composition(alignment, col_idx):
    column = alignment[:, col_idx]
    return Counter(column)

counts = column_composition(alignment, 0)
print(counts)  # Counter({'A': 3, 'G': 1, '-': 1})
```

### Find Conserved Positions
```python
def find_conserved_positions(alignment, threshold=1.0):
    conserved = []
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        counts = Counter(column)
        most_common_char, most_common_count = counts.most_common(1)[0]
        if most_common_char != '-':
            conservation = most_common_count / len(alignment)
            if conservation >= threshold:
                conserved.append((col_idx, most_common_char))
    return conserved

fully_conserved = find_conserved_positions(alignment, threshold=1.0)
mostly_conserved = find_conserved_positions(alignment, threshold=0.8)
```

## Gap Analysis

**Goal:** Quantify gap distribution across sequences and columns to identify problematic regions or sequences.

**Approach:** Count gap characters per sequence and per column, then identify positions exceeding a gap fraction threshold.

### Count Gaps Per Sequence
```python
gap_counts = [(record.id, str(record.seq).count('-')) for record in alignment]
for seq_id, gaps in gap_counts:
    print(f'{seq_id}: {gaps} gaps')
```

### Count Gaps Per Column
```python
def gaps_per_column(alignment):
    return [alignment[:, i].count('-') for i in range(alignment.get_alignment_length())]

gap_profile = gaps_per_column(alignment)
```

### Find Gappy Columns
```python
def find_gappy_columns(alignment, threshold=0.5):
    gappy = []
    num_seqs = len(alignment)
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        gap_fraction = column.count('-') / num_seqs
        if gap_fraction >= threshold:
            gappy.append(col_idx)
    return gappy

columns_to_remove = find_gappy_columns(alignment, threshold=0.5)
```

### Remove Gappy Columns
```python
def remove_gappy_columns(alignment, threshold=0.5):
    num_seqs = len(alignment)
    keep_columns = []
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        gap_fraction = column.count('-') / num_seqs
        if gap_fraction < threshold:
            keep_columns.append(col_idx)

    new_records = []
    for record in alignment:
        new_seq = ''.join(str(record.seq)[i] for i in keep_columns)
        new_records.append(SeqRecord(Seq(new_seq), id=record.id, description=record.description))
    return MultipleSeqAlignment(new_records)

cleaned = remove_gappy_columns(alignment, threshold=0.5)
```

## Consensus Sequence

**"Get consensus sequence"** → Derive a single representative sequence from an MSA based on majority-rule voting at each column.

**Goal:** Generate a consensus sequence from the alignment using a frequency threshold.

**Approach:** At each column, select the most common non-gap character if it exceeds the threshold; otherwise mark as ambiguous.

### Simple Majority Consensus
```python
def consensus_sequence(alignment, threshold=0.5, gap_char='-', ambiguous='N'):
    consensus = []
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        counts = Counter(column)
        most_common_char, most_common_count = counts.most_common(1)[0]
        if most_common_char == gap_char:
            counts.pop(gap_char, None)
            if counts:
                most_common_char, most_common_count = counts.most_common(1)[0]
            else:
                most_common_char = gap_char

        if most_common_count / len(alignment) >= threshold:
            consensus.append(most_common_char)
        else:
            consensus.append(ambiguous)
    return ''.join(consensus)

consensus = consensus_sequence(alignment, threshold=0.5)
```

### Note on Bio.Align.AlignInfo
The `AlignInfo.SummaryInfo` class is **deprecated** in recent Biopython versions. The custom `consensus_sequence()` function above is the recommended approach. If you see deprecation warnings when using `AlignInfo`, use the custom implementation instead.

## Extracting Regions

### Slice by Column Range
```python
region = alignment[:, 100:200]  # Columns 100-199
```

### Slice by Sequence Range
```python
subset = alignment[0:10]  # First 10 sequences
```

### Extract Ungapped Regions from Reference
```python
def extract_ungapped_regions(alignment, ref_idx=0):
    ref_seq = str(alignment[ref_idx].seq)
    ungapped_cols = [i for i, char in enumerate(ref_seq) if char != '-']

    new_records = []
    for record in alignment:
        new_seq = ''.join(str(record.seq)[i] for i in ungapped_cols)
        new_records.append(SeqRecord(Seq(new_seq), id=record.id, description=record.description))
    return MultipleSeqAlignment(new_records)

ungapped = extract_ungapped_regions(alignment, ref_idx=0)
```

## Sequence Filtering

**Goal:** Subset an alignment to retain only sequences matching specific criteria (ID pattern, gap content, uniqueness).

**Approach:** Iterate over alignment records, apply filter conditions, and reconstruct a new MultipleSeqAlignment from matching records.

### Filter by Sequence ID Pattern
```python
import re

def filter_by_id(alignment, pattern):
    regex = re.compile(pattern)
    matching = [record for record in alignment if regex.search(record.id)]
    return MultipleSeqAlignment(matching)

bacteria_only = filter_by_id(alignment, r'^Bac_')
```

### Filter by Gap Content
```python
def filter_by_gap_content(alignment, max_gap_fraction=0.1):
    filtered = []
    for record in alignment:
        gap_fraction = str(record.seq).count('-') / len(record.seq)
        if gap_fraction <= max_gap_fraction:
            filtered.append(record)
    return MultipleSeqAlignment(filtered)

low_gap_seqs = filter_by_gap_content(alignment, max_gap_fraction=0.1)
```

### Remove Duplicate Sequences
```python
def remove_duplicates(alignment):
    seen_seqs = {}
    unique_records = []
    for record in alignment:
        seq_str = str(record.seq)
        if seq_str not in seen_seqs:
            seen_seqs[seq_str] = record.id
            unique_records.append(record)
    return MultipleSeqAlignment(unique_records)

unique_alignment = remove_duplicates(alignment)
```

## Working with Annotations

### Stockholm Format Annotations
```python
alignment = AlignIO.read('pfam.sto', 'stockholm')

for record in alignment:
    if 'secondary_structure' in record.letter_annotations:
        ss = record.letter_annotations['secondary_structure']
        print(f'{record.id}: {ss}')
```

### Add Annotations to Records
```python
for record in alignment:
    record.annotations['source'] = 'my_analysis'
    record.annotations['quality'] = 'high'
```

## Position Mapping

**Goal:** Convert between alignment column coordinates and ungapped sequence coordinates.

**Approach:** Walk through the sequence tracking gap characters to map between the two coordinate systems.

### Map Alignment Position to Sequence Position
```python
def alignment_to_sequence_position(record, align_pos):
    seq_pos = 0
    for i, char in enumerate(str(record.seq)):
        if i == align_pos:
            return seq_pos if char != '-' else None
        if char != '-':
            seq_pos += 1
    return None
```

### Map Sequence Position to Alignment Position
```python
def sequence_to_alignment_position(record, seq_pos):
    current_seq_pos = 0
    for i, char in enumerate(str(record.seq)):
        if char != '-':
            if current_seq_pos == seq_pos:
                return i
            current_seq_pos += 1
    return None
```

## Quick Reference: Common Operations

| Task | Code |
|------|------|
| Get column | `alignment[:, col_idx]` |
| Get sequence | `alignment[seq_idx]` |
| Column count | `alignment.get_alignment_length()` |
| Sequence count | `len(alignment)` |
| Find gaps | `str(record.seq).count('-')` |
| Consensus | Use custom `consensus_sequence()` function |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `IndexError` | Column index out of range | Check `get_alignment_length()` |
| Unequal sequence lengths | Invalid MSA | Ensure all sequences same length |
| Empty Counter | All gaps in column | Handle gap-only columns |

## Related Skills

- alignment-io - Read/write alignment files in various formats
- pairwise-alignment - Create pairwise alignments
- msa-statistics - Calculate conservation metrics
- sequence-manipulation/motif-search - Search for patterns
