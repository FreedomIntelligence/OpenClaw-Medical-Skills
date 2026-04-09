# bio-primer-design-primer-basics

> Design PCR primers for a target sequence using primer3-py. Specify target regions, product size, melting temperature, and other constraints. Returns ranked primer pairs with quality metrics. Use when designing standard PCR primers.

**Available tools:** Read, Bash

# PCR Primer Design

Design PCR primers using primer3-py, the Python binding for Primer3.

## Required Imports

```python
import primer3
from primer3 import p3helpers
from Bio import SeqIO
from Bio.Seq import Seq
```

## Sequence Preparation (p3helpers)

```python
# Sanitize sequence (uppercase, remove whitespace)
raw_seq = '  atgc gatc GATC  '
clean_seq = p3helpers.sanitize_sequence(raw_seq)
print(f'Cleaned: {clean_seq}')  # 'ATGCGATCGATC'

# Reverse complement for designing reverse primers
seq = 'ATGCGATCGATC'
rc_seq = p3helpers.reverse_complement(seq)
print(f'Reverse complement: {rc_seq}')  # 'GATCGATCGCAT'

# Ensure valid DNA sequence (ACGT only, uppercase)
valid_seq = p3helpers.ensure_acgt_uppercase('atgcNNgatc')  # Raises error if invalid
```

## Basic Primer Design

```python
sequence = 'ATGCGTACGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG'

result = primer3.design_primers(
    seq_args={'SEQUENCE_TEMPLATE': sequence},
    global_args={
        'PRIMER_PRODUCT_SIZE_RANGE': [[100, 300]],
        'PRIMER_MIN_TM': 57.0,
        'PRIMER_OPT_TM': 60.0,
        'PRIMER_MAX_TM': 63.0,
        'PRIMER_MIN_GC': 40.0,
        'PRIMER_MAX_GC': 60.0,
    }
)
```

## Extract Primer Results

```python
num_returned = result['PRIMER_PAIR_NUM_RETURNED']
print(f'Found {num_returned} primer pairs')

for i in range(num_returned):
    left = result[f'PRIMER_LEFT_{i}_SEQUENCE']
    right = result[f'PRIMER_RIGHT_{i}_SEQUENCE']
    left_tm = result[f'PRIMER_LEFT_{i}_TM']
    right_tm = result[f'PRIMER_RIGHT_{i}_TM']
    product_size = result[f'PRIMER_PAIR_{i}_PRODUCT_SIZE']
    print(f'Pair {i}: {left} / {right}')
    print(f'  Tm: {left_tm:.1f}C / {right_tm:.1f}C, Product: {product_size}bp')
```

## Target a Specific Region

```python
# Target a specific region: [start, length]
result = primer3.design_primers(
    seq_args={
        'SEQUENCE_TEMPLATE': sequence,
        'SEQUENCE_TARGET': [100, 50],  # Target region at position 100, length 50
    },
    global_args={
        'PRIMER_PRODUCT_SIZE_RANGE': [[150, 300]],
        'PRIMER_OPT_TM': 60.0,
    }
)
```

## Primers Must Span a Region

```python
# Primers must span this region (e.g., exon junction)
result = primer3.design_primers(
    seq_args={
        'SEQUENCE_TEMPLATE': sequence,
        'SEQUENCE_INCLUDED_REGION': [50, 200],  # Primers within this region
    },
    global_args={'PRIMER_PRODUCT_SIZE_RANGE': [[100, 250]]}
)
```

## Exclude Regions

```python
# Exclude regions (e.g., SNP positions, repeats)
result = primer3.design_primers(
    seq_args={
        'SEQUENCE_TEMPLATE': sequence,
        'SEQUENCE_EXCLUDED_REGION': [[150, 20], [300, 15]],  # Regions to avoid
    },
    global_args={'PRIMER_PRODUCT_SIZE_RANGE': [[100, 300]]}
)
```

## Constrain Primer Positions

```python
# Force primer to overlap a specific position
result = primer3.design_primers(
    seq_args={
        'SEQUENCE_TEMPLATE': sequence,
        'SEQUENCE_FORCE_LEFT_START': 50,   # Left primer must start here
        'SEQUENCE_FORCE_RIGHT_START': 250,  # Right primer must start here
    },
    global_args={'PRIMER_PRODUCT_SIZE_RANGE': [[150, 250]]}
)
```

## Design for Sequencing

```python
# Single primer for sequencing
result = primer3.design_primers(
    seq_args={'SEQUENCE_TEMPLATE': sequence},
    global_args={
        'PRIMER_PICK_LEFT_PRIMER': 1,
        'PRIMER_PICK_RIGHT_PRIMER': 0,  # Only design left primer
        'PRIMER_PICK_INTERNAL_OLIGO': 0,
        'PRIMER_OPT_SIZE': 20,
        'PRIMER_MIN_SIZE': 18,
        'PRIMER_MAX_SIZE': 25,
    }
)
```

## Full Parameter Control

```python
result = primer3.design_primers(
    seq_args={
        'SEQUENCE_TEMPLATE': sequence,
        'SEQUENCE_TARGET': [200, 50],
    },
    global_args={
        'PRIMER_PRODUCT_SIZE_RANGE': [[150, 300], [300, 500]],  # Multiple ranges
        'PRIMER_NUM_RETURN': 5,
        'PRIMER_MIN_SIZE': 18,
        'PRIMER_OPT_SIZE': 20,
        'PRIMER_MAX_SIZE': 25,
        'PRIMER_MIN_TM': 57.0,
        'PRIMER_OPT_TM': 60.0,
        'PRIMER_MAX_TM': 63.0,
        'PRIMER_MIN_GC': 40.0,
        'PRIMER_OPT_GC_PERCENT': 50.0,
        'PRIMER_MAX_GC': 60.0,
        'PRIMER_MAX_POLY_X': 4,           # Max consecutive identical bases
        'PRIMER_MAX_NS_ACCEPTED': 0,       # No ambiguous bases
        'PRIMER_MAX_SELF_ANY': 8,          # Self-complementarity
        'PRIMER_MAX_SELF_END': 3,          # 3' self-complementarity
        'PRIMER_PAIR_MAX_COMPL_ANY': 8,    # Pair complementarity
        'PRIMER_PAIR_MAX_COMPL_END': 3,    # Pair 3' complementarity
        'PRIMER_MAX_END_STABILITY': 9.0,   # Max 3' end stability (delta G)
    }
)
```

## Load Sequence from FASTA

```python
from Bio import SeqIO

record = SeqIO.read('gene.fasta', 'fasta')
sequence = str(record.seq)

result = primer3.design_primers(
    seq_args={'SEQUENCE_TEMPLATE': sequence, 'SEQUENCE_ID': record.id},
    global_args={'PRIMER_PRODUCT_SIZE_RANGE': [[100, 300]], 'PRIMER_OPT_TM': 60.0}
)
```

## Calculate Tm Directly

```python
# Calculate Tm for an existing primer
tm = primer3.calc_tm('ATGCGATCGATCGATCGATC')
print(f'Tm: {tm:.1f}C')

# With custom salt/DNA concentrations
tm = primer3.calc_tm('ATGCGATCGATCGATCGATC', mv_conc=50.0, dv_conc=1.5, dntp_conc=0.2, dna_conc=50.0)
```

### Tm Calculation Defaults

| Parameter | Default | Description |
|-----------|---------|-------------|
| mv_conc | 50.0 mM | Monovalent cations (Na+, K+) |
| dv_conc | 0.0 mM | Divalent cations (Mg2+) |
| dntp_conc | 0.0 mM | dNTP concentration |
| dna_conc | 50.0 nM | DNA oligo concentration |

## Calculate Hairpin and Dimer Tm

```python
# Hairpin Tm
hairpin = primer3.calc_hairpin('ATGCGATCGATCGATCGATC')
print(f'Hairpin Tm: {hairpin.tm:.1f}C, dG: {hairpin.dg:.1f}')

# Homodimer Tm
homodimer = primer3.calc_homodimer('ATGCGATCGATCGATCGATC')
print(f'Homodimer Tm: {homodimer.tm:.1f}C, dG: {homodimer.dg:.1f}')

# Heterodimer Tm (between two different primers)
heterodimer = primer3.calc_heterodimer('ATGCGATCGATCGATCGATC', 'GCTAGCTAGCTAGCTAGCTA')
print(f'Heterodimer Tm: {heterodimer.tm:.1f}C, dG: {heterodimer.dg:.1f}')
```

## Format Results as DataFrame

```python
import pandas as pd

def primers_to_dataframe(result):
    rows = []
    for i in range(result['PRIMER_PAIR_NUM_RETURNED']):
        rows.append({
            'pair': i,
            'left_seq': result[f'PRIMER_LEFT_{i}_SEQUENCE'],
            'right_seq': result[f'PRIMER_RIGHT_{i}_SEQUENCE'],
            'left_tm': result[f'PRIMER_LEFT_{i}_TM'],
            'right_tm': result[f'PRIMER_RIGHT_{i}_TM'],
            'left_gc': result[f'PRIMER_LEFT_{i}_GC_PERCENT'],
            'right_gc': result[f'PRIMER_RIGHT_{i}_GC_PERCENT'],
            'product_size': result[f'PRIMER_PAIR_{i}_PRODUCT_SIZE'],
            'penalty': result[f'PRIMER_PAIR_{i}_PENALTY'],
        })
    return pd.DataFrame(rows)

df = primers_to_dataframe(result)
print(df)
```

## Common Global Arguments

| Parameter | Description | Default |
|-----------|-------------|---------|
| PRIMER_PRODUCT_SIZE_RANGE | Allowed product sizes | [[100,300]] |
| PRIMER_NUM_RETURN | Number of primer pairs | 5 |
| PRIMER_MIN/OPT/MAX_SIZE | Primer length | 18/20/27 |
| PRIMER_MIN/OPT/MAX_TM | Melting temperature | 57/60/63 |
| PRIMER_MIN/MAX_GC | GC content percent | 20/80 |
| PRIMER_MAX_POLY_X | Max poly-X run | 5 |
| PRIMER_MAX_SELF_ANY | Self complementarity | 8 |
| PRIMER_MAX_SELF_END | 3' self complementarity | 3 |

## Related Skills

- qpcr-primers - Design primers with internal probes for qPCR
- primer-validation - Check primers for specificity and secondary structures
- sequence-io - Load template sequences
- database-access/local-blast - BLAST primers for specificity checking
