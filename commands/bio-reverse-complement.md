# bio-reverse-complement

> Generate reverse complements and complements of DNA/RNA sequences using Biopython. Use when working with opposite strands, primer design, or converting between template and coding strands.

**Available tools:** Read, Bash

# Reverse Complement

Generate complementary and reverse complementary sequences using Biopython.

## Required Import

```python
from Bio.Seq import Seq
```

## Core Methods

### reverse_complement()

Returns the reverse complement (5' to 3' of the opposite strand).

```python
seq = Seq('ATGCGATCG')
rc = seq.reverse_complement()  # Returns Seq('CGATCGCAT')
```

This is the most commonly used operation - it gives you the sequence of the opposite strand in the conventional 5' to 3' direction.

### complement()

Returns the complement without reversing.

```python
seq = Seq('ATGCGATCG')
comp = seq.complement()  # Returns Seq('TACGCTAGC')
```

Less commonly used - gives the opposite strand but in 3' to 5' direction.

### reverse_complement_rna()

For RNA sequences (uses U instead of T):

```python
rna = Seq('AUGCGAUCG')
rc_rna = rna.reverse_complement_rna()  # Returns Seq('CGAUCGCAU')
```

### complement_rna()

```python
rna = Seq('AUGCGAUCG')
comp_rna = rna.complement_rna()  # Returns Seq('UACGCUAGC')
```

## Base Pairing Rules

### DNA

| Base | Complement |
|------|------------|
| A | T |
| T | A |
| G | C |
| C | G |

### RNA

| Base | Complement |
|------|------------|
| A | U |
| U | A |
| G | C |
| C | G |

### Ambiguous Bases (IUPAC)

| Code | Bases | Complement |
|------|-------|------------|
| R | A/G | Y |
| Y | C/T | R |
| S | G/C | S |
| W | A/T | W |
| K | G/T | M |
| M | A/C | K |
| B | C/G/T | V |
| D | A/G/T | H |
| H | A/C/T | D |
| V | A/C/G | B |
| N | A/C/G/T | N |

Biopython handles IUPAC ambiguity codes correctly.

## Code Patterns

### Basic Reverse Complement

```python
seq = Seq('ATGCGATCGATCG')
rc = seq.reverse_complement()
print(f'Original: 5\'-{seq}-3\'')
print(f'RevComp:  5\'-{rc}-3\'')
```

### Visualize Double-Stranded DNA

```python
def show_dsdna(seq):
    comp = seq.complement()
    print(f"5'-{seq}-3'")
    print(f"   {'|' * len(seq)}")
    print(f"3'-{comp}-5'")

seq = Seq('ATGCGATCG')
show_dsdna(seq)
```

### Check if Sequence is Palindrome (Self-Complementary)

```python
def is_palindrome(seq):
    return seq == seq.reverse_complement()

seq1 = Seq('GAATTC')  # EcoRI site - palindrome
seq2 = Seq('ATGCGA')  # Not a palindrome
print(f'GAATTC is palindrome: {is_palindrome(seq1)}')
print(f'ATGCGA is palindrome: {is_palindrome(seq2)}')
```

### Reverse Complement a FASTA File

```python
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

def reverse_complement_records(records):
    for record in records:
        rc_record = SeqRecord(
            record.seq.reverse_complement(),
            id=record.id + '_rc',
            description=record.description + ' reverse complement'
        )
        yield rc_record

records = SeqIO.parse('sequences.fasta', 'fasta')
rc_records = reverse_complement_records(records)
SeqIO.write(rc_records, 'sequences_rc.fasta', 'fasta')
```

### Primer Design Helper

```python
def design_primer_pair(template, start, end):
    '''Design forward and reverse primers for a region'''
    forward = template[start:start + 20]
    reverse = template[end - 20:end].reverse_complement()
    return forward, reverse

template = Seq('ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG')
fwd, rev = design_primer_pair(template, 0, 40)
print(f'Forward primer (5\'-3\'): {fwd}')
print(f'Reverse primer (5\'-3\'): {rev}')
```

### Handle Both Strands in Analysis

```python
def search_both_strands(seq, motif):
    '''Search for a motif on both strands'''
    motif = Seq(motif)
    results = []
    pos = seq.find(motif)
    while pos != -1:
        results.append(('+', pos))
        pos = seq.find(motif, pos + 1)
    rc = seq.reverse_complement()
    pos = rc.find(motif)
    while pos != -1:
        results.append(('-', len(seq) - pos - len(motif)))
        pos = rc.find(motif, pos + 1)
    return results

seq = Seq('ATGCGAATTCGATCGATGAATTCGATC')
hits = search_both_strands(seq, 'GAATTC')
for strand, pos in hits:
    print(f'Found on {strand} strand at position {pos}')
```

## Common Use Cases

| Task | Method |
|------|--------|
| Get opposite strand | `reverse_complement()` |
| Primer for opposite strand | `reverse_complement()` of target region |
| Template strand from coding | `reverse_complement()` |
| Check palindrome | `seq == seq.reverse_complement()` |
| Search both strands | Search original and reverse_complement |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Wrong bases in result | Mixing DNA/RNA methods | Use `reverse_complement_rna()` for RNA |
| `TypeError` | Passing string instead of Seq | Wrap in `Seq()` first |

## Decision Tree

```
Need to work with strand orientation?
├── Get opposite strand sequence (5' to 3')?
│   └── Use reverse_complement()
├── Get base-paired sequence (same direction)?
│   └── Use complement()
├── Working with RNA?
│   └── Use reverse_complement_rna()
├── Check if restriction site (palindrome)?
│   └── seq == seq.reverse_complement()
└── Designing primers?
    └── Reverse primer = reverse_complement() of 3' end
```

## Related Skills

- seq-objects - Create Seq objects to complement
- transcription-translation - Six-frame translation uses reverse complement
- motif-search - Search both strands for motifs
- restriction-analysis/restriction-sites - Restriction sites are often palindromic
- alignment-files/sam-bam-basics - BAM FLAG indicates read strand; use samtools view -f 16 for reverse
