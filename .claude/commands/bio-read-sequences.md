# bio-read-sequences

> Read biological sequence files (FASTA, FASTQ, GenBank, EMBL, ABI, SFF) using Biopython Bio.SeqIO. Use when parsing sequence files, iterating multi-sequence files, random access to large files, or high-performance parsing.

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show biopython` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Read Sequences

Read biological sequence data from files using Biopython's Bio.SeqIO module.

**"Read sequences from a file"** → Parse file into a collection of SeqRecord objects with IDs, sequences, and annotations accessible.
- Python: `SeqIO.parse()` or `SeqIO.read()` (BioPython)
- R: `readDNAStringSet()` or `readAAStringSet()` (Biostrings)

## Required Import

#### Core import
```python
from Bio import SeqIO
```

## Core Functions

### SeqIO.parse() - Multiple Records
Use for files with one or more sequences. Returns an iterator of SeqRecord objects.

```python
for record in SeqIO.parse('sequences.fasta', 'fasta'):
    print(record.id, len(record.seq))
```

**Important:** Always specify the format explicitly as the second argument.

### SeqIO.read() - Single Record
Use when file contains exactly one sequence. Raises error if zero or multiple records.

```python
record = SeqIO.read('single.fasta', 'fasta')
```

### SeqIO.to_dict() - Load All Into Memory
Use for random access by record ID. Loads entire file into memory.

```python
records = SeqIO.to_dict(SeqIO.parse('sequences.fasta', 'fasta'))
seq = records['sequence_id'].seq
```

### SeqIO.index() - Large File Random Access
Use for large files when random access is needed without loading everything into memory.

```python
records = SeqIO.index('large.fasta', 'fasta')
seq = records['sequence_id'].seq
records.close()
```

### SeqIO.index_db() - SQLite-Backed Indexing
Use for very large files or multiple files. Creates persistent SQLite index.

```python
# Create index (first time - parses file)
records = SeqIO.index_db('index.sqlite', 'large.fasta', 'fasta')
seq = records['sequence_id'].seq
records.close()

# Reuse existing index (instant load)
records = SeqIO.index_db('index.sqlite')

# Index multiple files together
records = SeqIO.index_db('combined.sqlite', ['file1.fasta', 'file2.fasta'], 'fasta')
```

**Advantages over index():**
- Persistent index survives program restarts
- Can index multiple files as one database
- Lower memory for extremely large files
- SQLite file can be shared across processes

## High-Performance Parsing

For maximum throughput on large files, use low-level parsers (3-6x faster than SeqIO.parse):

### SimpleFastaParser

**Goal:** Parse large FASTA files at maximum speed without SeqRecord overhead.

**Approach:** Use low-level tuple-based parser returning (title, sequence) strings.

**Reference (BioPython 1.83+):**
```python
from Bio.SeqIO.FastaIO import SimpleFastaParser

with open('large.fasta') as handle:
    for title, sequence in SimpleFastaParser(handle):
        if len(sequence) > 1000:
            print(title.split()[0])  # First word is usually ID
```

Returns `(title, sequence)` tuples as strings (no SeqRecord overhead).

### FastqGeneralIterator

**Goal:** Parse large FASTQ files at maximum speed.

**Approach:** Use low-level tuple-based parser returning (title, sequence, quality_string) strings.

**Reference (BioPython 1.83+):**
```python
from Bio.SeqIO.QualityIO import FastqGeneralIterator

with open('reads.fastq') as handle:
    for title, sequence, quality in FastqGeneralIterator(handle):
        avg_qual = sum(ord(c) - 33 for c in quality) / len(quality)
```

Returns `(title, sequence, quality_string)` tuples.

## Common Formats

| Format | String | Typical Extension | Notes |
|--------|--------|-------------------|-------|
| FASTA | `'fasta'` | .fasta, .fa, .fna, .faa | Most common |
| FASTA 2-line | `'fasta-2line'` | .fasta | One line per sequence (no wrapping) |
| FASTQ | `'fastq'` | .fastq, .fq | With quality scores |
| FASTQ Solexa | `'fastq-solexa'` | .fastq | Old Solexa/Illumina (pre-1.3) |
| FASTQ Illumina | `'fastq-illumina'` | .fastq | Illumina 1.3-1.7 |
| GenBank | `'genbank'` or `'gb'` | .gb, .gbk | With features/annotations |
| EMBL | `'embl'` | .embl | European format with features |
| Swiss-Prot | `'swiss'` | .dat | UniProt format |

## Specialized Formats

| Format | String | Use Case |
|--------|--------|----------|
| ABI | `'abi'` | Sanger sequencing trace files (.ab1) |
| ABI Trimmed | `'abi-trim'` | ABI with low-quality ends trimmed |
| SFF | `'sff'` | 454/Ion Torrent flowgram data |
| SFF Trimmed | `'sff-trim'` | SFF with adapter/quality trimming |
| QUAL | `'qual'` | Quality scores file (pairs with FASTA) |
| PHD | `'phd'` | Phred/Phrap/Consed output |
| ACE | `'ace'` | Assembly format (Consed) |
| PDB SEQRES | `'pdb-seqres'` | Protein sequences from PDB files |
| PDB ATOM | `'pdb-atom'` | Sequences from ATOM records in PDB |
| SnapGene | `'snapgene'` | SnapGene .dna files |
| GCK | `'gck'` | Gene Construction Kit files |
| XDNA | `'xdna'` | DNA Strider / SerialCloner files |

### Reading ABI Trace Files

```python
# Read Sanger sequencing trace with quality
record = SeqIO.read('sample.ab1', 'abi')
print(f'Sequence: {record.seq}')
qualities = record.letter_annotations['phred_quality']

# Auto-trim low quality ends
record_trimmed = SeqIO.read('sample.ab1', 'abi-trim')
```

### Reading 454/Ion Torrent SFF

```python
for record in SeqIO.parse('reads.sff', 'sff'):
    print(record.id, len(record.seq))

# With trimming applied
for record in SeqIO.parse('reads.sff', 'sff-trim'):
    print(record.id, len(record.seq))
```

### Reading PDB Sequences

```python
# Get sequences from SEQRES records
for record in SeqIO.parse('structure.pdb', 'pdb-seqres'):
    print(f'Chain {record.id}: {record.seq}')

# Get sequences from ATOM coordinates
for record in SeqIO.parse('structure.pdb', 'pdb-atom'):
    print(f'Chain {record.id}: {record.seq}')
```

## Alignment Formats (Read-Only)

| Format | String | Notes |
|--------|--------|-------|
| PHYLIP | `'phylip'` | Interleaved phylip |
| PHYLIP Sequential | `'phylip-sequential'` | Sequential phylip |
| PHYLIP Relaxed | `'phylip-relaxed'` | Longer names allowed |
| Clustal | `'clustal'` | ClustalW output |
| Stockholm | `'stockholm'` | Rfam/Pfam alignments |
| NEXUS | `'nexus'` | PAUP/MrBayes format |
| MAF | `'maf'` | Multiple Alignment Format |

## SeqRecord Object Attributes

After parsing, each record has these key attributes:

```python
record.id          # Sequence identifier (string)
record.name        # Sequence name (string)
record.description # Full description line (string)
record.seq         # Sequence data (Seq object)
record.features    # List of SeqFeature objects (GenBank/EMBL)
record.annotations # Dictionary of annotations
record.letter_annotations  # Per-letter annotations (quality scores)
record.dbxrefs     # Database cross-references
```

## Code Patterns

### Collect All Sequences Into a List
```python
records = list(SeqIO.parse('sequences.fasta', 'fasta'))
```

### Count Records Without Loading All
```python
count = sum(1 for _ in SeqIO.parse('sequences.fasta', 'fasta'))
```

### Fast Count (FASTA only)
```python
from Bio.SeqIO.FastaIO import SimpleFastaParser
with open('sequences.fasta') as f:
    count = sum(1 for _ in SimpleFastaParser(f))
```

### Get Sequence IDs Only
```python
ids = [record.id for record in SeqIO.parse('sequences.fasta', 'fasta')]
```

### Read GenBank with Features
```python
for record in SeqIO.parse('sequence.gb', 'genbank'):
    for feature in record.features:
        if feature.type == 'CDS':
            print(feature.qualifiers.get('product', ['Unknown'])[0])
            cds_seq = feature.extract(record.seq)  # Get feature sequence
```

### Access FASTQ Quality Scores
```python
for record in SeqIO.parse('reads.fastq', 'fastq'):
    qualities = record.letter_annotations['phred_quality']
    avg_quality = sum(qualities) / len(qualities)
```

### Read From File Handle
```python
with open('sequences.fasta', 'r') as handle:
    for record in SeqIO.parse(handle, 'fasta'):
        print(record.id)
```

### Custom ID Function for Indexing
```python
def get_accession(identifier):
    return identifier.split('.')[0]  # Remove version

records = SeqIO.index('sequences.fasta', 'fasta', key_function=get_accession)
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: More than one record` | Used `read()` on multi-record file | Use `parse()` instead |
| `ValueError: No records found` | Used `read()` on empty file | Check file exists and has content |
| `ValueError: unknown format` | Typo in format string | Check format string spelling |
| `UnicodeDecodeError` | Binary file or wrong encoding | Open with `encoding='latin-1'` or check file |
| `sqlite3.OperationalError` | index_db file locked | Close other connections first |

## Decision Tree

```
Need to read sequences?
├── Single record in file?
│   └── Use SeqIO.read()
├── Multiple records?
│   ├── Need all in memory at once?
│   │   └── Use list(SeqIO.parse()) or SeqIO.to_dict()
│   ├── Process one at a time (memory efficient)?
│   │   └── Use SeqIO.parse() iterator
│   ├── Large file, need random access by ID?
│   │   ├── Single session? → Use SeqIO.index()
│   │   └── Persistent/multi-file? → Use SeqIO.index_db()
│   └── Maximum throughput needed?
│       └── Use SimpleFastaParser or FastqGeneralIterator
├── Sanger sequencing trace?
│   └── Use 'abi' or 'abi-trim' format
├── 454/Ion Torrent data?
│   └── Use 'sff' or 'sff-trim' format
└── Protein from structure?
    └── Use 'pdb-seqres' or 'pdb-atom' format
```

## Related Skills

- write-sequences - Write parsed sequences to new files
- filter-sequences - Filter sequences by criteria after reading
- format-conversion - Convert between formats
- compressed-files - Read gzip/bzip2/BGZF compressed sequence files
- sequence-manipulation/seq-objects - Work with parsed SeqRecord objects
- database-access - Fetch sequences from NCBI instead of local files
- alignment-files - For SAM/BAM/CRAM alignment files, use samtools/pysam
