# bio-codon-usage

> Analyze codon usage, calculate CAI (Codon Adaptation Index), and examine synonymous codon bias using Biopython. Use when analyzing coding sequences for expression optimization or evolutionary analysis.

**Available tools:** Read, Bash

# Codon Usage

Analyze codon usage patterns and calculate codon adaptation metrics using Biopython.

## Required Imports

```python
from Bio.Seq import Seq
from Bio.SeqUtils import GC123
from Bio.SeqUtils.CodonUsage import CodonAdaptationIndex
from Bio.Data import CodonTable
from collections import Counter
```

## Basic Codon Counting

### Count Codons in Sequence

```python
from collections import Counter

def count_codons(seq):
    seq_str = str(seq).upper()
    codons = [seq_str[i:i+3] for i in range(0, len(seq_str) - 2, 3)]
    return Counter(codons)

seq = Seq('ATGCGATCGATCGATCGTAA')
codon_counts = count_codons(seq)
```

### Codon Frequencies (Relative)

```python
def codon_frequencies(seq):
    counts = count_codons(seq)
    total = sum(counts.values())
    return {codon: count / total for codon, count in counts.items()}
```

## Codon Adaptation Index (CAI)

### Using CodonUsage Module

```python
from Bio.SeqUtils.CodonUsage import CodonAdaptationIndex

# Create CAI calculator with reference set
cai = CodonAdaptationIndex()

# Generate index from highly expressed genes
cai.generate_index('highly_expressed_genes.fasta')

# Calculate CAI for a sequence
seq = Seq('ATGCGATCGATCGATCGTAA')
cai_value = cai.cai_for_gene(str(seq))
print(f'CAI: {cai_value:.3f}')  # Range 0-1, higher = better adapted
```

### CAI with Custom Codon Index

```python
from Bio.SeqUtils.CodonUsage import CodonAdaptationIndex

cai = CodonAdaptationIndex()

# Set custom index (relative adaptiveness for each codon)
custom_index = {
    'TTT': 0.5, 'TTC': 1.0,  # Phe
    'TTA': 0.1, 'TTG': 0.5, 'CTT': 0.3, 'CTC': 1.0, 'CTA': 0.1, 'CTG': 1.0,  # Leu
    # ... define all 64 codons
}
cai.set_cai_index(custom_index)
```

## Synonymous Codon Usage

### RSCU (Relative Synonymous Codon Usage)

RSCU = (observed codon frequency) / (expected frequency if all synonymous codons were used equally)

```python
from Bio.Data import CodonTable

def calculate_rscu(seq, table_id=1):
    codon_table = CodonTable.unambiguous_dna_by_id[table_id]
    counts = count_codons(seq)

    # Group codons by amino acid
    aa_to_codons = {}
    for codon in counts:
        if codon in codon_table.stop_codons:
            continue
        try:
            aa = codon_table.forward_table[codon]
            aa_to_codons.setdefault(aa, []).append(codon)
        except KeyError:
            continue

    # Calculate RSCU for each codon
    rscu = {}
    for aa, codons in aa_to_codons.items():
        total = sum(counts.get(c, 0) for c in codons)
        n_synonymous = len(codons)
        expected = total / n_synonymous if n_synonymous > 0 else 0
        for codon in codons:
            observed = counts.get(codon, 0)
            rscu[codon] = observed / expected if expected > 0 else 0
    return rscu
```

### Identify Rare Codons

```python
def find_rare_codons(seq, threshold=0.1):
    freq = codon_frequencies(seq)
    return {codon: f for codon, f in freq.items() if f < threshold}
```

### Codon Bias by Position (GC123)

```python
from Bio.SeqUtils import GC123

seq = Seq('ATGCGATCGATCGATCGATCGATCGATCGTAA')
gc_total, gc_pos1, gc_pos2, gc_pos3 = GC123(seq)

print(f'Total GC: {gc_total:.1f}%')
print(f'1st position GC: {gc_pos1:.1f}%')
print(f'2nd position GC: {gc_pos2:.1f}%')
print(f'3rd position GC: {gc_pos3:.1f}% (wobble position)')
```

## Codon Tables

### Access Codon Tables

```python
from Bio.Data import CodonTable

# Get standard table
std_table = CodonTable.unambiguous_dna_by_id[1]

# List all available tables
for id, table in CodonTable.unambiguous_dna_by_id.items():
    print(f'{id}: {table.names[0]}')
```

### Common Codon Tables

| ID | Name | Organism |
|----|------|----------|
| 1 | Standard | Most organisms |
| 2 | Vertebrate Mitochondrial | Human, mouse mito |
| 4 | Mold Mitochondrial | Fungi, protozoa mito |
| 5 | Invertebrate Mitochondrial | Insects, worms mito |
| 11 | Bacterial/Plastid | E. coli, chloroplasts |

### Codon Table Properties

```python
table = CodonTable.unambiguous_dna_by_id[1]

print(f'Start codons: {table.start_codons}')
print(f'Stop codons: {table.stop_codons}')

# Forward table: codon -> amino acid
print(table.forward_table['ATG'])  # 'M'

# Back table: amino acid -> list of codons
back_table = {}
for codon, aa in table.forward_table.items():
    back_table.setdefault(aa, []).append(codon)
print(f'Leucine codons: {back_table["L"]}')
```

## Code Patterns

### Full Codon Usage Report

```python
def codon_usage_report(seq, table_id=1):
    from Bio.Data import CodonTable

    table = CodonTable.unambiguous_dna_by_id[table_id]
    counts = count_codons(seq)
    total = sum(counts.values())

    # Group by amino acid
    aa_groups = {}
    for codon, aa in table.forward_table.items():
        aa_groups.setdefault(aa, []).append(codon)

    report = {}
    for aa, codons in sorted(aa_groups.items()):
        aa_total = sum(counts.get(c, 0) for c in codons)
        report[aa] = {
            'total': aa_total,
            'codons': {c: {'count': counts.get(c, 0),
                          'freq': counts.get(c, 0) / aa_total if aa_total > 0 else 0}
                      for c in codons}
        }
    return report
```

### Compare Codon Usage Between Sequences

```python
def compare_codon_usage(seq1, seq2):
    freq1 = codon_frequencies(seq1)
    freq2 = codon_frequencies(seq2)

    all_codons = set(freq1.keys()) | set(freq2.keys())
    comparison = {}
    for codon in sorted(all_codons):
        f1, f2 = freq1.get(codon, 0), freq2.get(codon, 0)
        comparison[codon] = {'seq1': f1, 'seq2': f2, 'diff': f1 - f2}
    return comparison
```

### Optimize Codons for Expression

```python
def optimize_codons(protein_seq, preferred_codons):
    '''Replace codons with preferred synonymous codons'''
    optimized = []
    for aa in str(protein_seq):
        if aa in preferred_codons:
            optimized.append(preferred_codons[aa])
        else:
            optimized.append('NNN')  # Unknown
    return Seq(''.join(optimized))

# E. coli preferred codons
ecoli_preferred = {
    'A': 'GCG', 'R': 'CGT', 'N': 'AAC', 'D': 'GAT', 'C': 'TGC',
    'Q': 'CAG', 'E': 'GAA', 'G': 'GGT', 'H': 'CAC', 'I': 'ATT',
    'L': 'CTG', 'K': 'AAA', 'M': 'ATG', 'F': 'TTC', 'P': 'CCG',
    'S': 'TCT', 'T': 'ACC', 'W': 'TGG', 'Y': 'TAC', 'V': 'GTT',
}
```

### Codon Usage from FASTA File

```python
from Bio import SeqIO

def analyze_fasta_codon_usage(filename):
    all_counts = Counter()
    for record in SeqIO.parse(filename, 'fasta'):
        all_counts.update(count_codons(record.seq))

    total = sum(all_counts.values())
    return {codon: count / total for codon, count in all_counts.items()}
```

### Effective Number of Codons (Nc)

A measure of codon bias (lower = more biased, range 20-61):

```python
import math

def effective_nc(seq, table_id=1):
    from Bio.Data import CodonTable
    table = CodonTable.unambiguous_dna_by_id[table_id]
    counts = count_codons(seq)

    # Group by degeneracy class
    aa_groups = {}
    for codon, aa in table.forward_table.items():
        aa_groups.setdefault(aa, []).append(codon)

    # Calculate F for each amino acid
    nc_sum = 0
    for aa, codons in aa_groups.items():
        n = sum(counts.get(c, 0) for c in codons)
        if n <= 1:
            continue
        pi_sq_sum = sum((counts.get(c, 0) / n) ** 2 for c in codons)
        F = (n * pi_sq_sum - 1) / (n - 1)
        nc_sum += 1 / F if F > 0 else len(codons)

    return nc_sum if nc_sum > 0 else 61
```

## Property Reference

| Metric | Range | Interpretation |
|--------|-------|----------------|
| CAI | 0-1 | Higher = better adapted to host |
| RSCU | 0-N | 1.0 = no bias, >1 = overused, <1 = underused |
| Nc | 20-61 | Lower = more biased |
| GC3 | 0-100% | GC at wobble position |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `KeyError` | Non-standard codon | Handle N-containing codons |
| Wrong counts | Sequence not in frame | Ensure length is multiple of 3 |
| No index set | Called CAI without training | Call `generate_index()` first |

## Decision Tree

```
Need to analyze codon usage?
├── Count codon frequencies?
│   └── Use Counter on 3-mers
├── Calculate adaptation to host?
│   └── Use CodonAdaptationIndex (CAI)
├── Identify synonymous bias?
│   └── Calculate RSCU
├── Check wobble position bias?
│   └── Use GC123()
├── Measure overall bias?
│   └── Calculate Nc (effective number of codons)
└── Optimize for expression?
    └── Replace with preferred synonymous codons
```

## Related Skills

- transcription-translation - Translate sequences and understand codon tables
- sequence-properties - GC123 for wobble position GC content
- sequence-io/read-sequences - Parse CDS sequences from GenBank files
- database-access/entrez-fetch - Fetch reference gene sets from NCBI for CAI training
