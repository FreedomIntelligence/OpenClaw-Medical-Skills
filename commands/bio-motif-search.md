# bio-motif-search

> Find patterns, motifs, and subsequences in biological sequences using Biopython. Use when searching for transcription factor binding sites, regulatory elements, or any sequence pattern. For restriction enzyme analysis, use the restriction-analysis skill.

**Available tools:** Read, Bash

# Motif Search

Find patterns and motifs in biological sequences using Biopython and regex.

## Required Imports

```python
from Bio.Seq import Seq
from Bio import motifs
import re
```

## Core Methods

### find() - First Occurrence

```python
seq = Seq('ATGCGAATTCGATCGAATTCGATC')
pos = seq.find('GAATTC')  # Returns 4 (first position)
```

Returns -1 if not found.

### count() - Count Occurrences

```python
seq = Seq('ATGCGAATTCGATCGAATTCGATC')
n = seq.count('GAATTC')  # Returns 2
```

### find() with Start Position

```python
seq = Seq('ATGCGAATTCGATCGAATTCGATC')
first = seq.find('GAATTC')        # 4
second = seq.find('GAATTC', 5)    # 14 (search from position 5)
```

## Code Patterns

### Find All Occurrences

```python
def find_all(seq, pattern):
    pattern = str(pattern)
    seq_str = str(seq)
    positions = []
    pos = seq_str.find(pattern)
    while pos != -1:
        positions.append(pos)
        pos = seq_str.find(pattern, pos + 1)
    return positions

seq = Seq('ATGCGAATTCGATCGAATTCGATC')
positions = find_all(seq, 'GAATTC')  # [4, 14]
```

### Search Both Strands

```python
def find_both_strands(seq, pattern):
    results = []
    for pos in find_all(seq, pattern):
        results.append(('+', pos))
    rc = seq.reverse_complement()
    for pos in find_all(rc, pattern):
        results.append(('-', len(seq) - pos - len(pattern)))
    return results
```

### Regex Pattern Search

For ambiguous or flexible patterns:

```python
def regex_search(seq, pattern):
    seq_str = str(seq)
    return [(m.start(), m.group()) for m in re.finditer(pattern, seq_str)]

# Find all ATG start codons
matches = regex_search(seq, 'ATG')

# Find TATA box variants (TATAAA with possible variations)
matches = regex_search(seq, 'TATA[AT]A[AT]')
```

### IUPAC Ambiguity Pattern

```python
IUPAC_DNA = {
    'R': '[AG]', 'Y': '[CT]', 'S': '[GC]', 'W': '[AT]',
    'K': '[GT]', 'M': '[AC]', 'B': '[CGT]', 'D': '[AGT]',
    'H': '[ACT]', 'V': '[ACG]', 'N': '[ACGT]'
}

def iupac_to_regex(pattern):
    regex = ''
    for char in pattern:
        regex += IUPAC_DNA.get(char, char)
    return regex

# Search for pattern with ambiguous bases
pattern = 'GATNNTC'  # N = any base
regex = iupac_to_regex(pattern)  # 'GAT[ACGT][ACGT]TC'
matches = regex_search(seq, regex)
```

### Find ORFs (Start to Stop)

```python
def find_orfs(seq, start='ATG', stops=['TAA', 'TAG', 'TGA'], min_length=30):
    seq_str = str(seq)
    orfs = []
    start_positions = find_all(seq, start)
    for start_pos in start_positions:
        for frame_offset in range(3):
            if (start_pos - frame_offset) % 3 == 0:
                for stop in stops:
                    stop_pos = start_pos + 3
                    while stop_pos <= len(seq) - 3:
                        codon = seq_str[stop_pos:stop_pos + 3]
                        if codon == stop:
                            if stop_pos - start_pos >= min_length:
                                orfs.append((start_pos, stop_pos + 3, seq[start_pos:stop_pos + 3]))
                            break
                        stop_pos += 3
                break
    return orfs
```

### Find Repeats

```python
def find_tandem_repeats(seq, unit_length, min_copies=2):
    seq_str = str(seq)
    repeats = []
    for i in range(len(seq) - unit_length * min_copies + 1):
        unit = seq_str[i:i + unit_length]
        copies = 1
        pos = i + unit_length
        while pos <= len(seq) - unit_length and seq_str[pos:pos + unit_length] == unit:
            copies += 1
            pos += unit_length
        if copies >= min_copies:
            repeats.append((i, unit, copies))
    return repeats

seq = Seq('ATGCAGCAGCAGCAGTTT')
repeats = find_tandem_repeats(seq, 3, 2)  # Find CAG repeats
```

## Bio.motifs Module

### Create Motif from Instances

```python
from Bio import motifs
from Bio.Seq import Seq

instances = [Seq('TACAA'), Seq('TACGA'), Seq('TACTA'), Seq('TGCAA')]
m = motifs.create(instances)
```

### Motif Properties

```python
# Consensus sequences
m.consensus              # Most common base at each position
m.degenerate_consensus   # IUPAC degenerate consensus
m.anticonsensus          # Least likely sequence

# Counts and matrices
m.counts                 # Position frequency matrix (counts)
pwm = m.counts.normalize(pseudocounts=0.5)  # Position weight matrix
pssm = pwm.log_odds()    # Position-specific scoring matrix
```

### Information Content

```python
# Per-position information content
pwm = m.counts.normalize(pseudocounts=0.5)
pssm = pwm.log_odds()

# Mean information content (bits)
mean_ic = pssm.mean()

# Score range
max_score = pssm.max
min_score = pssm.min

# Relative entropy
print(f'Mean IC: {mean_ic:.3f} bits')
print(f'Max score: {max_score:.3f}')
print(f'Min score: {min_score:.3f}')
```

### PSSM Search

```python
seq = Seq('ATGCTACAAGCTACGATACTA')

# Search with threshold
for position, score in pssm.search(seq, threshold=3.0):
    match = seq[position:position + len(m.consensus)]
    print(f'Position {position}: {match} (score: {score:.2f})')

# Search both strands
for position, score in pssm.search(seq, threshold=3.0, both=True):
    print(f'Position {position}: score {score:.2f}')
```

### Calculate Threshold from Distribution

```python
# Calculate score distribution from PSSM
sd = pssm.distribution()

# Get threshold for specific false positive rate
threshold = sd.threshold_fpr(0.01)  # 1% FPR

# Get threshold for specific false negative rate
threshold = sd.threshold_fnr(0.1)   # 10% FNR

# Balanced threshold
threshold = sd.threshold_balanced(1000)  # For sequence of length 1000
```

## Reading Motif Files

### JASPAR Format

```python
from Bio import motifs

with open('motif.jaspar') as f:
    m = motifs.read(f, 'jaspar')
print(f'Name: {m.name}')
print(f'Matrix ID: {m.matrix_id}')
print(m.counts)
```

### MEME Format

```python
with open('meme.txt') as f:
    record = motifs.parse(f, 'meme')
for m in record:
    print(f'{m.name}: {m.consensus}')
```

### TRANSFAC Format

```python
with open('motif.transfac') as f:
    record = motifs.parse(f, 'transfac')
for m in record:
    print(f'{m.name}: {m.consensus}')
```

### Write Motifs

```python
# Write to JASPAR format
with open('output.jaspar', 'w') as f:
    f.write(m.format('jaspar'))

# Write to TRANSFAC format
with open('output.transfac', 'w') as f:
    f.write(m.format('transfac'))
```

## Common Motif Patterns

| Motif | Pattern | Description |
|-------|---------|-------------|
| Start codon | `ATG` | Translation initiation |
| Stop codons | `TAA\|TAG\|TGA` | Translation termination |
| Kozak | `[AG]CCATGG` | Eukaryotic translation initiation |
| TATA box | `TATA[AT]A[AT]` | Promoter element |
| GC box | `GGGCGG` | Promoter element (Sp1) |
| CAAT box | `CCAAT` | Promoter element |
| Poly-A signal | `AATAAA` | mRNA polyadenylation |
| E-box | `CA[ACGT]{2}TG` | bHLH TF binding |
| CpG island | High CG density | Promoter regions |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| No matches found | Case mismatch | Use `.upper()` on both |
| Missing matches | Pattern on opposite strand | Search reverse complement too |
| `TypeError` | Mixing Seq and string | Use `str()` conversion |
| `ValueError` parsing motif | Wrong format specified | Check file format |

## Decision Tree

```
Need to find patterns in sequence?
├── Exact match?
│   ├── Just need position of first? → seq.find()
│   ├── Need count? → seq.count()
│   └── Need all positions? → loop with find()
├── Fuzzy/ambiguous pattern?
│   └── Use regex with re.finditer()
├── IUPAC pattern?
│   └── Convert to regex, then search
├── Both strands?
│   └── Search original and reverse_complement
├── Probabilistic (PWM/PSSM)?
│   └── Use Bio.motifs
│       ├── Create from instances → motifs.create()
│       ├── Read from file → motifs.read() / parse()
│       ├── Get consensus → m.consensus, m.degenerate_consensus
│       ├── Search sequence → pssm.search()
│       └── Calculate threshold → distribution.threshold_fpr()
└── Restriction sites?
    └── Use restriction-analysis skill (Bio.Restriction)
```

## Related Skills

- seq-objects - Create Seq objects for searching
- reverse-complement - Search both strands for motifs
- sequence-io/filter-sequences - Filter sequences that contain specific motifs
- restriction-analysis/restriction-sites - For restriction enzyme site searching
- database-access - Download motif databases from NCBI/JASPAR
