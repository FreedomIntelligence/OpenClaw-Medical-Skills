# bio-sequence-properties

> Calculate sequence properties like GC content, molecular weight, isoelectric point, and GC skew using Biopython. Use when analyzing sequence composition, computing physical properties, or comparing sequences.

**Available tools:** Read, Bash

# Sequence Properties

Calculate physical and chemical properties of biological sequences using Biopython.

## Required Imports

```python
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction, molecular_weight, GC123, GC_skew, nt_search, seq1, seq3
from Bio.SeqUtils.ProtParam import ProteinAnalysis
```

## DNA/RNA Properties

### GC Content

```python
from Bio.SeqUtils import gc_fraction

seq = Seq('ATGCGATCGATCGATCGATCG')
gc = gc_fraction(seq)  # Returns 0.476... (fraction)
gc_percent = gc * 100  # Convert to percentage
```

Handle ambiguous bases:
```python
gc = gc_fraction(seq, ambiguous='ignore')  # Ignore N bases in calculation
gc = gc_fraction(seq, ambiguous='weighted')  # Weight by probability
```

### GC at Codon Positions (GC123)

Analyze GC content at each codon position (useful for codon bias analysis):

```python
from Bio.SeqUtils import GC123

seq = Seq('ATGCGATCGATCGATCGATCG')
gc_total, gc_pos1, gc_pos2, gc_pos3 = GC123(seq)
# gc_total: overall GC%
# gc_pos1: GC% at 1st codon position
# gc_pos2: GC% at 2nd codon position
# gc_pos3: GC% at 3rd codon position (wobble)
```

### GC Skew

Calculate (G-C)/(G+C) in sliding windows to identify replication origins:

```python
from Bio.SeqUtils import GC_skew

seq = Seq('ATGCGATCGATCGATCGATCG' * 10)
skew_values = GC_skew(seq, window=100)  # Returns list of skew values
```

### Molecular Weight

```python
from Bio.SeqUtils import molecular_weight

dna = Seq('ATGCGATCG')
mw = molecular_weight(dna)  # Single-stranded DNA weight

# Double-stranded DNA
mw_ds = molecular_weight(dna, double_stranded=True)

# Circular DNA
mw_circ = molecular_weight(dna, circular=True)

# RNA
rna = Seq('AUGCGAUCG')
mw_rna = molecular_weight(rna, seq_type='RNA')

# Protein
protein = Seq('MRCRS')
mw_prot = molecular_weight(protein, seq_type='protein')
```

### Melting Temperature

```python
from Bio.SeqUtils import MeltingTemp

seq = Seq('ATGCGATCGATCG')

# Basic Tm (Wallace rule - short oligos)
tm_wallace = MeltingTemp.Tm_Wallace(seq)

# GC method (more accurate for longer sequences)
tm_gc = MeltingTemp.Tm_GC(seq)

# Nearest neighbor (most accurate)
tm_nn = MeltingTemp.Tm_NN(seq)

# With salt correction
tm_corrected = MeltingTemp.Tm_NN(seq, Na=50, Mg=1.5)
```

### Sequence Search with IUPAC Codes (nt_search)

Built-in search that handles IUPAC ambiguity codes:

```python
from Bio.SeqUtils import nt_search

seq = 'ATGCGATCGATCGATNGATC'
# Search for pattern with ambiguous bases
result = nt_search(seq, 'GATNGATC')  # N matches any base
# Returns: ['GATNGATC', 8] - pattern and position(s)
```

### Base Composition

```python
def base_composition(seq):
    seq_str = str(seq).upper()
    total = len(seq_str)
    return {base: seq_str.count(base) / total * 100 for base in 'ATGC'}
```

## Amino Acid Code Conversion

Convert between 1-letter and 3-letter amino acid codes:

```python
from Bio.SeqUtils import seq1, seq3

# 3-letter to 1-letter
one_letter = seq1('MetAlaGlyTrp')  # Returns 'MAGW'

# 1-letter to 3-letter
three_letter = seq3('MAGW')  # Returns 'MetAlaGlyTrp'

# With custom separator
three_letter = seq3('MAGW', join='-')  # Returns 'Met-Ala-Gly-Trp'
```

## Protein Properties

### Using ProteinAnalysis

```python
from Bio.SeqUtils.ProtParam import ProteinAnalysis

protein = ProteinAnalysis('MAEGEITTFTALTEKFNLPPGNYKKPKLLYCSNG')
```

### Basic Properties

```python
mw = protein.molecular_weight()           # Molecular weight in Daltons
pi = protein.isoelectric_point()          # Isoelectric point
aa_comp = protein.amino_acids_percent     # Amino acid composition (property)
aa_count = protein.count_amino_acids()    # Raw amino acid counts
```

### Stability and Hydropathy

```python
instability = protein.instability_index()  # < 40 = stable, > 40 = unstable
gravy = protein.gravy()                    # Negative = hydrophilic, Positive = hydrophobic
arom = protein.aromaticity()               # Fraction of Phe+Trp+Tyr
```

### Charge at Specific pH

```python
charge = protein.charge_at_pH(7.0)  # Net charge at pH 7.0
charge_acidic = protein.charge_at_pH(4.0)
charge_basic = protein.charge_at_pH(10.0)
```

### Flexibility Profile

```python
flexibility = protein.flexibility()  # List of flexibility values per residue
# Based on Vihinen, 1994 scale
```

### Secondary Structure

```python
helix, turn, sheet = protein.secondary_structure_fraction()
```

### Extinction Coefficient

```python
eps_reduced, eps_cystine = protein.molar_extinction_coefficient()
# eps_reduced: all Cys are reduced
# eps_cystine: all Cys form disulfide bonds
```

### Protein Scale Profiles

Calculate profiles using any amino acid scale:

```python
# Kyte-Doolittle hydropathy profile
kd_scale = {'A': 1.8, 'R': -4.5, 'N': -3.5, ...}
profile = protein.protein_scale(kd_scale, window=7)
```

## Code Patterns

### Analyze Multiple Sequences

```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction

def analyze_fasta(filename):
    results = []
    for record in SeqIO.parse(filename, 'fasta'):
        results.append({
            'id': record.id,
            'length': len(record.seq),
            'gc': gc_fraction(record.seq) * 100
        })
    return results
```

### GC Content Distribution (Sliding Windows)

```python
from Bio.SeqUtils import gc_fraction

def gc_distribution(seq, window_size=100, step=50):
    gc_values = []
    for i in range(0, len(seq) - window_size + 1, step):
        window = seq[i:i + window_size]
        gc_values.append((i, gc_fraction(window) * 100))
    return gc_values
```

### GC Skew Plot Data

```python
from Bio.SeqUtils import GC_skew

def gc_skew_analysis(seq, window=1000):
    skew = GC_skew(seq, window=window)
    positions = list(range(0, len(seq) - window + 1, window))
    cumulative = []
    total = 0
    for s in skew:
        total += s
        cumulative.append(total)
    return positions, skew, cumulative
```

### Full Protein Analysis Report

```python
from Bio.SeqUtils.ProtParam import ProteinAnalysis

def protein_report(sequence):
    protein = ProteinAnalysis(str(sequence).replace('*', ''))
    helix, turn, sheet = protein.secondary_structure_fraction()
    return {
        'length': len(sequence),
        'molecular_weight': protein.molecular_weight(),
        'isoelectric_point': protein.isoelectric_point(),
        'charge_at_pH7': protein.charge_at_pH(7.0),
        'instability_index': protein.instability_index(),
        'gravy': protein.gravy(),
        'aromaticity': protein.aromaticity(),
        'helix_fraction': helix,
        'turn_fraction': turn,
        'sheet_fraction': sheet,
    }
```

### Dinucleotide Frequencies

```python
from collections import Counter

def dinucleotide_freq(seq):
    seq_str = str(seq)
    dinucs = [seq_str[i:i+2] for i in range(len(seq_str) - 1)]
    counts = Counter(dinucs)
    total = sum(counts.values())
    return {di: count / total for di, count in counts.items()}
```

### CpG Observed/Expected Ratio

```python
def cpg_ratio(seq):
    seq_str = str(seq).upper()
    cpg = seq_str.count('CG')
    c = seq_str.count('C')
    g = seq_str.count('G')
    expected = (c * g) / len(seq_str) if len(seq_str) > 0 else 0
    return cpg / expected if expected > 0 else 0
```

## Property Reference

### DNA/RNA Properties

| Property | Function | Notes |
|----------|----------|-------|
| GC content | `gc_fraction()` | Returns fraction (0-1) |
| GC by position | `GC123()` | Total, pos1, pos2, pos3 |
| GC skew | `GC_skew()` | (G-C)/(G+C) in windows |
| Molecular weight | `molecular_weight()` | In Daltons |
| Melting temp | `MeltingTemp.Tm_*()` | Multiple methods |
| IUPAC search | `nt_search()` | Handles ambiguity codes |

### Protein Properties

| Property | Method | Typical Range |
|----------|--------|---------------|
| MW | `molecular_weight()` | Daltons |
| pI | `isoelectric_point()` | 0-14 |
| Charge | `charge_at_pH(pH)` | Varies |
| Instability | `instability_index()` | <40 stable |
| GRAVY | `gravy()` | -2 to +2 |
| Aromaticity | `aromaticity()` | 0-0.15 |
| Flexibility | `flexibility()` | Per-residue list |

### Amino Acid Codes

| Function | Input | Output |
|----------|-------|--------|
| `seq1()` | 'MetAlaGly' | 'MAG' |
| `seq3()` | 'MAG' | 'MetAlaGly' |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `KeyError` in ProteinAnalysis | Non-standard amino acid | Remove X, *, etc. |
| Wrong MW | Wrong seq_type | Specify 'RNA' or 'protein' |
| Invalid Tm | Sequence too short | Use >10 bp for accurate Tm |
| Empty GC_skew | Sequence shorter than window | Reduce window size |

## Decision Tree

```
Need sequence properties?
├── DNA/RNA sequence?
│   ├── GC content? → gc_fraction()
│   ├── GC at codon positions? → GC123()
│   ├── GC skew (replication origin)? → GC_skew()
│   ├── Molecular weight? → molecular_weight()
│   ├── Melting temperature? → MeltingTemp.Tm_NN()
│   └── Search with IUPAC codes? → nt_search()
├── Protein sequence?
│   └── Create ProteinAnalysis object
│       ├── Size → molecular_weight()
│       ├── Charge → isoelectric_point(), charge_at_pH()
│       ├── Stability → instability_index()
│       ├── Hydrophobicity → gravy()
│       ├── Flexibility → flexibility()
│       └── Structure → secondary_structure_fraction()
└── Convert amino acid codes?
    └── seq1() / seq3()
```

## Related Skills

- seq-objects - Create Seq objects for property calculation
- sequence-io/sequence-statistics - File-level statistics (N50, totals)
- codon-usage - GC123 for codon position analysis
- transcription-translation - Translate before protein analysis
- alignment-files/bam-statistics - samtools stats for alignment-level GC and quality stats
