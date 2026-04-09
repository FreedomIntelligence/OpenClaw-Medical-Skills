# bio-format-conversion

> Convert between sequence file formats (FASTA, FASTQ, GenBank, EMBL) using Biopython Bio.SeqIO. Use when changing file formats or preparing data for different tools.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Format Conversion

**"Convert this file to a different format"** → Read records in one format, optionally add missing annotations, and write in the target format.
- Python: `SeqIO.convert()` for direct conversion, or `SeqIO.parse()` + `SeqIO.write()` when modifications are needed (BioPython)
- CLI: `seqkit seq` (SeqKit) for FASTA/FASTQ; `samtools view` for SAM/BAM/CRAM

Convert sequence files between formats using Biopython's Bio.SeqIO module.

## Required Import

```python
from Bio import SeqIO
```

## Core Function

### SeqIO.convert() - Direct Conversion
Convert between formats in a single call. Most efficient method.

```python
count = SeqIO.convert('input.gb', 'genbank', 'output.fasta', 'fasta')
print(f'Converted {count} records')
```

**Parameters:**
- `in_file` - Input filename or handle
- `in_format` - Input format string
- `out_file` - Output filename or handle
- `out_format` - Output format string

**Returns:** Number of records converted

## Common Conversions

| From | To | Notes |
|------|-----|-------|
| GenBank | FASTA | Loses annotations, keeps sequence |
| FASTA | GenBank | Need to add molecule_type |
| FASTQ | FASTA | Loses quality scores |
| FASTA | FASTQ | Need to add quality scores |
| GenBank | EMBL | Usually works directly |
| Stockholm | FASTA | Alignment to sequences |

## Code Patterns

### Simple Conversion
```python
SeqIO.convert('input.gb', 'genbank', 'output.fasta', 'fasta')
```

### GenBank to FASTA
```python
SeqIO.convert('sequence.gb', 'genbank', 'sequence.fasta', 'fasta')
```

### FASTQ to FASTA (drop quality)
```python
SeqIO.convert('reads.fastq', 'fastq', 'reads.fasta', 'fasta')
```

### FASTA to GenBank (requires molecule_type)

**Goal:** Convert FASTA to GenBank format, which requires molecule_type annotation.

**Approach:** Stream records through a generator that injects the missing annotation, then write.

**Reference (BioPython 1.83+):**
```python
records = SeqIO.parse('input.fasta', 'fasta')
def add_molecule_type(records):
    for record in records:
        record.annotations['molecule_type'] = 'DNA'
        yield record

SeqIO.write(add_molecule_type(records), 'output.gb', 'genbank')
```

### FASTA to FASTQ (add dummy quality)

**Goal:** Convert FASTA to FASTQ by assigning uniform placeholder quality scores.

**Approach:** Stream records through a generator that adds phred_quality to each, then write as FASTQ.

**Reference (BioPython 1.83+):**
```python
def add_quality(records, quality=30):
    for record in records:
        record.letter_annotations['phred_quality'] = [quality] * len(record.seq)
        yield record

records = SeqIO.parse('input.fasta', 'fasta')
SeqIO.write(add_quality(records), 'output.fastq', 'fastq')
```

### Batch Convert Multiple Files

**Goal:** Convert all files of one format in a directory to another format.

**Approach:** Glob for input files, apply `SeqIO.convert()` to each, and report per-file counts.

**Reference (BioPython 1.83+):**
```python
from pathlib import Path

for gb_file in Path('.').glob('*.gb'):
    fasta_file = gb_file.with_suffix('.fasta')
    count = SeqIO.convert(str(gb_file), 'genbank', str(fasta_file), 'fasta')
    print(f'{gb_file.name}: {count} records')
```

### Convert with Modifications
```python
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

def uppercase_record(rec):
    return SeqRecord(rec.seq.upper(), id=rec.id, description=rec.description)

records = SeqIO.parse('input.fasta', 'fasta')
modified = (uppercase_record(rec) for rec in records)
SeqIO.write(modified, 'output.fasta', 'fasta')
```

### Alignment Format Conversion
```python
from Bio import AlignIO

AlignIO.convert('alignment.sto', 'stockholm', 'alignment.phy', 'phylip')
```

## Format Compatibility Matrix

**Can convert directly (no modifications needed):**
- GenBank <-> EMBL
- FASTA -> any format (may need annotations added)
- Any format -> FASTA (always works, may lose data)
- FASTQ -> FASTA

**Requires adding data:**
- FASTA -> FASTQ (need quality scores)
- FASTA -> GenBank (need molecule_type)

**May lose data:**
- GenBank -> FASTA (loses features, annotations)
- FASTQ -> FASTA (loses quality scores)
- Any rich format -> FASTA

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: missing molecule_type` | FASTA to GenBank | Add molecule_type annotation |
| `ValueError: missing quality scores` | FASTA to FASTQ | Add phred_quality to letter_annotations |
| `KeyError: 'phred_quality'` | Wrong FASTQ variant | Try 'fastq-sanger', 'fastq-illumina' |

## Decision Tree

```
Converting formats?
├── Simple conversion (no data changes)?
│   └── Use SeqIO.convert() directly
├── Need to add annotations?
│   └── Parse, modify records, then write
├── Need to transform sequences?
│   └── Parse, apply transformation, then write
└── Multiple files?
    └── Loop with SeqIO.convert() or batch generator
```

## Related Skills

- read-sequences - Parse sequences for custom conversion logic
- write-sequences - Write converted sequences with modifications
- batch-processing - Convert multiple files at once
- compressed-files - Handle compressed input/output during conversion
- alignment-files - For SAM/BAM/CRAM conversion, use samtools view
