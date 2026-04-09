# bio-seq-objects

> Create and manipulate Seq, MutableSeq, and SeqRecord objects using Biopython. Use when creating sequences from strings, modifying sequence data in-place, or building annotated sequence records.

**Available tools:** Read, Bash

# Seq Objects

Create and manipulate biological sequence objects using Biopython.

## Required Imports

```python
from Bio.Seq import Seq, MutableSeq
from Bio.SeqRecord import SeqRecord
```

## Core Objects

### Seq - Immutable Sequence

The basic sequence object. Immutable like Python strings.

```python
seq = Seq('ATGCGATCGATCG')
```

Seq objects support string-like operations:
```python
len(seq)           # Length
seq[0]             # First base
seq[-1]            # Last base
seq[0:10]          # Slice (returns Seq)
str(seq)           # Convert to string
'ATG' in seq       # Membership test
seq.count('G')     # Count occurrences
seq.find('ATG')    # Find position (-1 if not found)
seq.upper()        # Uppercase
seq.lower()        # Lowercase
seq * 3            # Repeat sequence
seq.strip()        # Remove leading/trailing whitespace
```

### MutableSeq - Mutable Sequence

For in-place modifications when performance matters.

```python
mut_seq = MutableSeq('ATGCGATCG')
mut_seq[0] = 'C'              # Modify single position
mut_seq[0:3] = 'GGG'          # Replace slice
mut_seq.append('A')           # Add to end
mut_seq.insert(0, 'G')        # Insert at position
mut_seq.pop()                 # Remove and return last
mut_seq.remove('G')           # Remove first occurrence
mut_seq.reverse()             # Reverse in place
```

Convert between types:
```python
seq = Seq(mut_seq)            # MutableSeq to Seq
mut_seq = MutableSeq(seq)     # Seq to MutableSeq
```

### SeqRecord - Annotated Sequence

Sequence with metadata for file I/O and analysis.

```python
record = SeqRecord(
    Seq('ATGCGATCG'),
    id='gene1',
    name='example_gene',
    description='An example gene sequence'
)
```

SeqRecord attributes:
```python
record.seq           # The Seq object
record.id            # Identifier string
record.name          # Name string
record.description   # Description string
record.features      # List of SeqFeature objects
record.annotations   # Dict of annotations
record.letter_annotations  # Per-letter annotations (quality scores)
record.dbxrefs       # Database cross-references
```

### SeqRecord Methods

Transform entire records while preserving metadata:

```python
# Reverse complement (preserves ID, updates features)
rc_record = record.reverse_complement(id='gene1_rc', description='reverse complement')

# Translate to protein (creates new SeqRecord with protein)
protein_record = record.translate(id='gene1_protein')

# Quick format output (returns string in file format)
fasta_str = record.format('fasta')
genbank_str = record.format('genbank')
```

Slicing preserves features (adjusted to new coordinates):
```python
# Slice SeqRecord - features are clipped/adjusted automatically
subset = record[10:50]  # Features outside range are dropped
```

## Code Patterns

### Create Seq from String
```python
dna = Seq('ATGCGATCGATCG')
rna = Seq('AUGCGAUCGAUCG')
protein = Seq('MRCRS')
```

### Create SeqRecord for File Output
```python
record = SeqRecord(Seq('ATGCGATCG'), id='seq1', description='My sequence')
```

### Create SeqRecord with Annotations
```python
record = SeqRecord(Seq('ATGCGATCG'), id='gene1', description='Example')
record.annotations['organism'] = 'Homo sapiens'
record.annotations['molecule_type'] = 'DNA'
```

### Build SeqRecord from Parsed Data
```python
from Bio.SeqFeature import SeqFeature, FeatureLocation

record = SeqRecord(Seq('ATGCGATCGATCG'), id='gene1')
feature = SeqFeature(FeatureLocation(0, 9), type='CDS', qualifiers={'product': ['Example protein']})
record.features.append(feature)
```

### Batch Create SeqRecords
```python
sequences = ['ATGC', 'GCTA', 'TTAA']
records = [SeqRecord(Seq(s), id=f'seq_{i}') for i, s in enumerate(sequences)]
```

### Copy a SeqRecord
```python
from copy import deepcopy
new_record = deepcopy(record)
new_record.id = 'modified_copy'
```

### Modify SeqRecord Sequence
```python
record = SeqRecord(Seq('ATGCGATCG'), id='seq1')
record.seq = Seq('GGGGGATCG')  # Replace entire sequence
```

### Join Sequences into One SeqRecord
```python
combined_seq = seq1 + Seq('NNNN') + seq2  # With linker
combined_record = SeqRecord(combined_seq, id='combined')
```

### Transform SeqRecord with reverse_complement
```python
# Reverse complement a gene sequence
record = SeqRecord(Seq('ATGCGATCGATCG'), id='gene1', description='Forward strand')
rc_record = record.reverse_complement(id=f'{record.id}_rc', description='Reverse complement')
# Features are remapped to new coordinates
```

### Translate SeqRecord to Protein
```python
# Translate coding sequence
cds_record = SeqRecord(Seq('ATGCGATCGATCGTAA'), id='cds1', description='Coding sequence')
protein_record = cds_record.translate(id=f'{cds_record.id}_protein', to_stop=True)
```

### Quick Output with format()
```python
record = SeqRecord(Seq('ATGCGATCG'), id='seq1', description='Example sequence')
print(record.format('fasta'))
# >seq1 Example sequence
# ATGCGATCG
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TypeError: 'Seq' object does not support item assignment` | Trying to modify immutable Seq | Use MutableSeq instead |
| `TypeError: SeqRecord object argument must be a Seq object` | Passed string instead of Seq | Wrap string in Seq() |
| Missing annotations in output | Didn't set required annotations | Add `molecule_type` to annotations for GenBank output |

## Decision Tree

```
Need to work with sequence data?
├── Just doing string-like operations?
│   └── Use Seq
├── Need to modify sequence in-place?
│   └── Use MutableSeq
├── Need metadata (ID, description, features)?
│   └── Use SeqRecord
└── Need to write to file?
    └── Use SeqRecord with appropriate annotations
```

## Related Skills

- sequence-io/read-sequences - Parse files to get SeqRecord objects
- sequence-io/write-sequences - Write SeqRecord objects to files
- transcription-translation - Transform Seq objects (DNA to protein)
- reverse-complement - Get reverse complement of Seq
- sequence-slicing - Slice and extract from Seq/SeqRecord
- database-access/entrez-fetch - Fetch sequences from NCBI as SeqRecords
