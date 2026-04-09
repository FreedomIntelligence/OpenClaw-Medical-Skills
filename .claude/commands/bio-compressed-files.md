# bio-compressed-files

> Read and write compressed sequence files (gzip, bzip2, BGZF) using Biopython. Use when working with .gz or .bz2 sequence files. Use BGZF for indexable compressed files.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Compressed Files

Handle gzip, bzip2, and BGZF compressed sequence files with Biopython.

**"Read a compressed sequence file"** → Open a compressed file handle in text mode, then parse with the standard SeqIO interface.
- gzip: `gzip.open(path, 'rt')` (Python stdlib)
- bzip2: `bz2.open(path, 'rt')` (Python stdlib)
- BGZF: `bgzf.open(path, 'rt')` (BioPython) or direct `SeqIO.parse(path, fmt)`

**"Make a compressed file indexable"** → Convert to BGZF format. Only BGZF supports `SeqIO.index()` on compressed data.

## Required Imports

```python
import gzip
import bz2
from Bio import SeqIO
from Bio import bgzf
```

## Reading Compressed Files

**Goal:** Parse sequence records from compressed files without decompressing to disk.

**Approach:** Open a decompression handle in text mode (`'rt'`), then pass the handle to `SeqIO.parse()`. The parser works identically to uncompressed input.

### Gzip (.gz) (BioPython 1.83+)
```python
with gzip.open('sequences.fasta.gz', 'rt') as handle:
    for record in SeqIO.parse(handle, 'fasta'):
        print(record.id, len(record.seq))
```

**Important:** Use `'rt'` (read text) mode, not `'rb'` (read binary).

### Bzip2 (.bz2) (BioPython 1.83+)
```python
with bz2.open('sequences.fasta.bz2', 'rt') as handle:
    for record in SeqIO.parse(handle, 'fasta'):
        print(record.id, len(record.seq))
```

### BGZF (Block Gzip) (BioPython 1.83+)
BGZF files can be read like regular gzip, but also support indexing:

```python
for record in SeqIO.parse('sequences.fasta.bgz', 'fasta'):
    print(record.id)

with bgzf.open('sequences.fasta.bgz', 'rt') as handle:
    for record in SeqIO.parse(handle, 'fasta'):
        print(record.id)
```

## Writing Compressed Files

**Goal:** Save sequence records directly to compressed files without an intermediate uncompressed step.

**Approach:** Open a compression handle in text mode (`'wt'`), then pass it to `SeqIO.write()`.

### Gzip (.gz)
```python
with gzip.open('output.fasta.gz', 'wt') as handle:
    SeqIO.write(records, handle, 'fasta')
```

### Bzip2 (.bz2)
```python
with bz2.open('output.fasta.bz2', 'wt') as handle:
    SeqIO.write(records, handle, 'fasta')
```

### BGZF (.bgz)
```python
with bgzf.open('output.fasta.bgz', 'wt') as handle:
    SeqIO.write(records, handle, 'fasta')
```

## BGZF: Indexable Compression

**Goal:** Enable random access to records in compressed sequence files.

**Approach:** Write sequences in BGZF (Block GZip Format) — the only compressed format supporting `SeqIO.index()` and `SeqIO.index_db()`. BGZF is a gzip variant used by BAM and tabix-indexed files.

### Create Indexable Compressed File

```python
from Bio import SeqIO, bgzf

records = SeqIO.parse('input.fasta', 'fasta')
with bgzf.open('output.fasta.bgz', 'wt') as handle:
    SeqIO.write(records, handle, 'fasta')
```

### Index a BGZF File

```python
records = SeqIO.index('sequences.fasta.bgz', 'fasta')
seq = records['target_id'].seq
records.close()

records = SeqIO.index_db('index.sqlite', 'sequences.fasta.bgz', 'fasta')
```

### Convert Gzip to BGZF

**"Convert gzip to indexable format"** → Parse from gzip handle, write through BGZF handle.

```python
from Bio import SeqIO, bgzf
import gzip

with gzip.open('input.fasta.gz', 'rt') as in_handle:
    with bgzf.open('output.fasta.bgz', 'wt') as out_handle:
        SeqIO.write(SeqIO.parse(in_handle, 'fasta'), out_handle, 'fasta')
```

## Code Patterns

### Read Gzipped FASTQ
```python
with gzip.open('reads.fastq.gz', 'rt') as handle:
    records = list(SeqIO.parse(handle, 'fastq'))
print(f'Loaded {len(records)} reads')
```

### Count Records in Gzipped File
```python
with gzip.open('sequences.fasta.gz', 'rt') as handle:
    count = sum(1 for _ in SeqIO.parse(handle, 'fasta'))
print(f'{count} sequences')
```

### Fast Count with Low-Level Parser
```python
from Bio.SeqIO.FastaIO import SimpleFastaParser
import gzip

with gzip.open('sequences.fasta.gz', 'rt') as handle:
    count = sum(1 for _ in SimpleFastaParser(handle))
```

### Convert Compressed to Uncompressed
```python
with gzip.open('input.fasta.gz', 'rt') as in_handle:
    records = SeqIO.parse(in_handle, 'fasta')
    SeqIO.write(records, 'output.fasta', 'fasta')
```

### Convert Uncompressed to Compressed
```python
records = SeqIO.parse('input.fasta', 'fasta')
with gzip.open('output.fasta.gz', 'wt') as out_handle:
    SeqIO.write(records, out_handle, 'fasta')
```

### Auto-Detect Compression

```python
from pathlib import Path
from Bio import SeqIO, bgzf
import gzip
import bz2

def open_sequence_file(filepath, format):
    filepath = Path(filepath)
    suffix = filepath.suffix.lower()
    if suffix == '.gz':
        # Could be gzip or bgzf - bgzf handles both
        handle = bgzf.open(filepath, 'rt')
    elif suffix == '.bgz':
        handle = bgzf.open(filepath, 'rt')
    elif suffix == '.bz2':
        handle = bz2.open(filepath, 'rt')
    else:
        handle = open(filepath, 'r')
    return SeqIO.parse(handle, format)
```

### Process Large Gzipped File (Memory Efficient)
```python
with gzip.open('large.fastq.gz', 'rt') as handle:
    for record in SeqIO.parse(handle, 'fastq'):
        if len(record.seq) >= 100:
            process(record)
```

### Compress Existing File (Raw Copy)
```python
import shutil

with open('sequences.fasta', 'rb') as f_in:
    with gzip.open('sequences.fasta.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
```

## Compression Comparison

| Format | Extension | Indexable | Speed | Compression |
|--------|-----------|-----------|-------|-------------|
| Gzip | `.gz` | No | Fast | Good |
| BGZF | `.bgz` | **Yes** | Fast | Good |
| Bzip2 | `.bz2` | No | Slow | Better |
| LZMA | `.xz` | No | Slowest | Best |

## When to Use Each Format

| Use Case | Recommended Format |
|----------|-------------------|
| Archive (no random access needed) | gzip or bzip2 |
| Need to index compressed file | **BGZF** |
| BAM files and tabix | BGZF (native) |
| Maximum compression | bzip2 or xz |
| Best speed | gzip or BGZF |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TypeError: a bytes-like object is required` | Used 'rb' mode | Use 'rt' for text mode |
| `UnicodeDecodeError` | Wrong encoding | Try `gzip.open(file, 'rt', encoding='latin-1')` |
| `gzip.BadGzipFile` | Not a gzip file | Check file extension matches actual format |
| `OSError: Not a gzipped file` | Corrupt or wrong format | Verify file integrity |
| `SeqIO.index() fails on .gz` | Regular gzip not indexable | Convert to BGZF first |

## Decision Tree

```
Working with compressed sequence files?
├── Just reading sequentially?
│   └── Use gzip.open() or bz2.open() with 'rt' mode
├── Need to index the compressed file?
│   └── Convert to BGZF, then use SeqIO.index()
├── Writing compressed output?
│   ├── Will need to index later? → Use bgzf.open()
│   └── Just archiving? → Use gzip.open() or bz2.open()
└── Converting between formats?
    └── Parse with SeqIO, write to new handle
```

## Related Skills

- read-sequences - Core parsing functions used with compressed handles
- write-sequences - Write to compressed output files
- batch-processing - Process multiple compressed files
- alignment-files - BAM files use BGZF natively; samtools handles compression
