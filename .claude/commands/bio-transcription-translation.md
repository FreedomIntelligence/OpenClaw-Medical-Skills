# bio-transcription-translation

> Transcribe DNA to RNA and translate to protein using Biopython. Use when converting between DNA, RNA, and protein sequences, finding ORFs, or using alternative codon tables.

**Available tools:** Read, Bash

# Transcription and Translation

Convert between DNA, RNA, and protein sequences using Biopython.

## Required Import

```python
from Bio.Seq import Seq
```

## Core Methods

### Transcription (DNA to RNA)

```python
dna = Seq('ATGCGATCGATCG')
rna = dna.transcribe()  # Returns Seq('AUGCGAUCGAUCG')
```

Transcription replaces T with U. Works on coding strand (5' to 3').

### Back Transcription (RNA to DNA)

```python
rna = Seq('AUGCGAUCGAUCG')
dna = rna.back_transcribe()  # Returns Seq('ATGCGATCGATCG')
```

### Translation (RNA/DNA to Protein)

```python
# From coding DNA (includes ATG start)
coding_dna = Seq('ATGTTTGGT')
protein = coding_dna.translate()  # Returns Seq('MFG')

# From RNA
rna = Seq('AUGUUUGGU')
protein = rna.translate()  # Returns Seq('MFG')
```

## Translation Options

### Stop at First Stop Codon

```python
seq = Seq('ATGTTTGGTTAAGGG')
protein = seq.translate(to_stop=True)  # Stops at TAA, excludes stop
```

### Include Stop Codon Symbol

```python
seq = Seq('ATGTTTGGTTAA')
protein = seq.translate()  # Returns Seq('MFG*')
```

### Alternative Codon Tables

Biopython supports NCBI codon tables. Common tables:

| ID | Name | Use Case |
|----|------|----------|
| 1 | Standard | Default, most organisms |
| 2 | Vertebrate Mitochondrial | Human/vertebrate mitochondria |
| 4 | Mold Mitochondrial | Fungi, protozoa mitochondria |
| 5 | Invertebrate Mitochondrial | Insects, worms mitochondria |
| 6 | Ciliate Nuclear | Tetrahymena, Paramecium |
| 11 | Bacterial/Archaeal | Prokaryotes, plastids |

```python
# Bacterial translation
seq = Seq('ATGTTTGGT')
protein = seq.translate(table=11)

# Mitochondrial translation
protein = seq.translate(table=2)

# By name
protein = seq.translate(table='Vertebrate Mitochondrial')
```

### CDS Translation (Complete Coding Sequence)

For validated coding sequences with proper start/stop:

```python
cds = Seq('ATGTTTGGTTAA')  # Must start with start codon, end with stop
protein = cds.translate(cds=True)  # Validates and removes stop
```

The `cds=True` option:
- Validates start codon (ATG or alternative)
- Validates stop codon at end
- Removes stop codon from result
- Raises error if invalid CDS

## Code Patterns

### Basic Transcription and Translation Pipeline

```python
dna = Seq('ATGTTTGGTCATTAA')
rna = dna.transcribe()
protein = rna.translate()
print(f'DNA: {dna}')
print(f'RNA: {rna}')
print(f'Protein: {protein}')
```

### Translate All Six Reading Frames

```python
def six_frame_translation(seq):
    frames = []
    for strand, s in [('+', seq), ('-', seq.reverse_complement())]:
        for frame in range(3):
            length = 3 * ((len(s) - frame) // 3)
            fragment = s[frame:frame + length]
            frames.append((strand, frame, fragment.translate()))
    return frames

seq = Seq('ATGCGATCGATCGATCGATCG')
for strand, frame, protein in six_frame_translation(seq):
    print(f'{strand}{frame}: {protein}')
```

### Find All ORFs (Start to Stop)

```python
def find_orfs(seq, min_length=30):
    orfs = []
    for strand, s in [('+', seq), ('-', seq.reverse_complement())]:
        for frame in range(3):
            trans = s[frame:].translate()
            aa_start = 0
            while True:
                start = trans.find('M', aa_start)
                if start == -1:
                    break
                stop = trans.find('*', start)
                if stop == -1:
                    stop = len(trans)
                orf = trans[start:stop]
                if len(orf) * 3 >= min_length:
                    orfs.append((strand, frame, start * 3 + frame, str(orf)))
                aa_start = start + 1
    return orfs

seq = Seq('ATGCGATCGATCGATCGATCGTAA')
for strand, frame, pos, orf in find_orfs(seq, min_length=3):
    print(f'{strand} frame {frame} pos {pos}: {orf}')
```

### Translate with Quality Check

```python
def translate_cds_safe(seq):
    try:
        return seq.translate(cds=True)
    except Exception as e:
        return seq.translate(to_stop=True)  # Fallback
```

### Get Codon Table Info

```python
from Bio.Data import CodonTable

table = CodonTable.unambiguous_dna_by_id[1]
print(f'Start codons: {table.start_codons}')
print(f'Stop codons: {table.stop_codons}')
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TranslationError: First codon is not a start codon` | Used `cds=True` without valid start | Remove `cds=True` or fix sequence |
| `TranslationError: Final codon is not a stop codon` | Used `cds=True` without stop codon | Remove `cds=True` or add stop codon |
| `TranslationError: Sequence length not multiple of 3` | Partial codons at end | Trim sequence to multiple of 3 |
| Unexpected amino acids | Wrong codon table | Specify correct table for organism |

## Decision Tree

```
Need to convert sequence?
├── DNA to RNA?
│   └── Use seq.transcribe()
├── RNA to DNA?
│   └── Use seq.back_transcribe()
├── DNA/RNA to protein?
│   ├── Complete CDS with start/stop?
│   │   └── Use translate(cds=True)
│   ├── Stop at first stop codon?
│   │   └── Use translate(to_stop=True)
│   ├── Non-standard organism?
│   │   └── Use translate(table=N)
│   └── Get all including stop symbol?
│       └── Use translate()
└── Find all ORFs?
    └── Translate all six frames, search for M...*
```

## Related Skills

- seq-objects - Create Seq objects for translation
- reverse-complement - Translate both strands (six-frame translation)
- codon-usage - Analyze codon bias in coding sequences
- sequence-io/read-sequences - Parse GenBank files with CDS features
- database-access/entrez-fetch - Fetch CDS sequences from NCBI for translation
