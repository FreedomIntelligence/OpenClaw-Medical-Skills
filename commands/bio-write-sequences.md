# bio-write-sequences

> Write biological sequences to files (FASTA, FASTQ, GenBank, EMBL) using Biopython Bio.SeqIO. Use when saving sequences, creating new sequence files, or outputting modified records.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Write Sequences

**"Write sequences to a file"** → Serialize SeqRecord objects into a formatted sequence file.
- Python: `SeqIO.write()` (BioPython)
- R: `writeXStringSet()` (Biostrings)

Write SeqRecord objects to sequence files using Biopython's Bio.SeqIO module.

## Required Import

```python
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
```

## Core Functions

### SeqIO.write() - Write Records to File
Write one or more SeqRecord objects to a file.

```python
SeqIO.write(records, 'output.fasta', 'fasta')
```

**Parameters:**
- `records` - Single SeqRecord, list, or iterator of SeqRecords
- `handle` - Filename (string) or file handle
- `format` - Output format string

**Returns:** Number of records written (integer)

### record.format() - Get Formatted String
Get a string representation without writing to file.

```python
formatted = record.format('fasta')
print(formatted)
```

## Creating SeqRecord Objects

**Goal:** Construct in-memory sequence records suitable for writing to any format.

**Approach:** Create `SeqRecord` with at minimum a `Seq` and `id`. Add `letter_annotations` for FASTQ, `annotations['molecule_type']` for GenBank/EMBL.

**"Create a sequence record from scratch"** → Wrap a `Seq` string in a `SeqRecord` with metadata fields.
- Python: `SeqRecord(Seq(...), id=...)` (BioPython)

### Minimal SeqRecord
```python
record = SeqRecord(Seq('ATGCGATCGATCG'), id='seq1')
```

### Full SeqRecord
```python
record = SeqRecord(
    Seq('ATGCGATCGATCG'),
    id='seq1',
    name='sequence_one',
    description='Example sequence for demonstration'
)
```

### With Annotations (for GenBank output)
```python
from Bio.SeqFeature import SeqFeature, FeatureLocation

record = SeqRecord(
    Seq('ATGCGATCGATCG'),
    id='seq1',
    annotations={'molecule_type': 'DNA'}
)
record.features.append(
    SeqFeature(FeatureLocation(0, 9), type='gene', qualifiers={'gene': ['exampleGene']})
)
```

## Common Formats

| Format | String | Notes |
|--------|--------|-------|
| FASTA | `'fasta'` | Most universal, sequence + header only |
| FASTQ | `'fastq'` | Requires quality scores in letter_annotations |
| GenBank | `'genbank'` | Requires annotations and molecule_type |
| EMBL | `'embl'` | Similar requirements to GenBank |
| Tab | `'tab'` | Simple ID + sequence tabular format |

## Code Patterns

### Write Single Record
```python
record = SeqRecord(Seq('ATGC'), id='my_seq', description='test sequence')
SeqIO.write(record, 'output.fasta', 'fasta')
```

### Write Multiple Records
```python
records = [
    SeqRecord(Seq('ATGC'), id='seq1'),
    SeqRecord(Seq('GCTA'), id='seq2'),
    SeqRecord(Seq('TTAA'), id='seq3')
]
count = SeqIO.write(records, 'output.fasta', 'fasta')
print(f'Wrote {count} records')
```

### Write to File Handle
```python
with open('output.fasta', 'w') as handle:
    SeqIO.write(records, handle, 'fasta')
```

### Write Modified Records

**Goal:** Transform sequences in-memory and write the modified versions to a new file.

**Approach:** Parse input, apply transformation via generator, write output. Using a generator avoids loading all records into memory.

**"Modify sequences and save"** → Parse records, transform each, write to new file with `SeqIO.write()`.

```python
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

def uppercase_record(rec):
    return SeqRecord(rec.seq.upper(), id=rec.id, description=rec.description)

records = SeqIO.parse('input.fasta', 'fasta')
modified = (uppercase_record(rec) for rec in records)
SeqIO.write(modified, 'output.fasta', 'fasta')
```

### Append to Existing File
```python
with open('output.fasta', 'a') as handle:
    SeqIO.write(new_records, handle, 'fasta')
```

### Write FASTQ with Quality Scores
```python
record = SeqRecord(Seq('ATGCGATCG'), id='read1')
record.letter_annotations['phred_quality'] = [30, 30, 28, 25, 30, 30, 28, 25, 30]
SeqIO.write(record, 'output.fastq', 'fastq')
```

### Write GenBank Format
```python
record = SeqRecord(Seq('ATGCGATCGATCG'), id='SEQ001', name='example')
record.annotations['molecule_type'] = 'DNA'
record.annotations['topology'] = 'linear'
record.annotations['organism'] = 'Example organism'
SeqIO.write(record, 'output.gb', 'genbank')
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TypeError: SeqRecord expected` | Passed raw string/Seq | Wrap in SeqRecord object |
| `ValueError: missing molecule_type` | GenBank without annotations | Add `record.annotations['molecule_type'] = 'DNA'` |
| `ValueError: missing quality scores` | FASTQ without phred_quality | Add quality scores to letter_annotations |
| `ValueError: Sequences must all be the same length` | PHYLIP with unequal lengths | Pad or trim sequences first |

## Format-Specific Requirements

### FASTQ
Must have quality scores:
```python
record.letter_annotations['phred_quality'] = [30] * len(record.seq)
```

### GenBank/EMBL
Must have molecule_type:
```python
record.annotations['molecule_type'] = 'DNA'  # or 'RNA', 'protein'
```

### PHYLIP
All sequences must be same length. IDs truncated to 10 characters.

## Related Skills

- read-sequences - Read sequences before modifying and writing
- format-conversion - Direct format conversion without intermediate processing
- filter-sequences - Filter sequences before writing subset
- sequence-manipulation/seq-objects - Create SeqRecord objects to write
- alignment-files - For SAM/BAM output, use samtools/pysam
