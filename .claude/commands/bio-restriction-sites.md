# bio-restriction-sites

> Find restriction enzyme cut sites in DNA sequences using Biopython Bio.Restriction. Search with single enzymes, batches of enzymes, or commercially available enzyme sets. Returns cut positions for linear or circular DNA. Use when finding restriction enzyme cut sites in sequences.

**Available tools:** Read, Bash

# Finding Restriction Sites

## Core Pattern

```python
from Bio import SeqIO
from Bio.Restriction import EcoRI, BamHI, HindIII, RestrictionBatch, Analysis

record = SeqIO.read('sequence.fasta', 'fasta')
seq = record.seq

# Single enzyme
sites = EcoRI.search(seq)  # Returns list of cut positions
```

## Search with Single Enzyme

```python
from Bio.Restriction import EcoRI

sites = EcoRI.search(seq)
print(f'EcoRI cuts at positions: {sites}')
print(f'Number of sites: {len(sites)}')

# Check if enzyme cuts
if EcoRI.search(seq):
    print('EcoRI cuts this sequence')
else:
    print('EcoRI does not cut')
```

## Search with Multiple Enzymes

```python
from Bio.Restriction import RestrictionBatch, EcoRI, BamHI, HindIII, XhoI

batch = RestrictionBatch([EcoRI, BamHI, HindIII, XhoI])

# Method 1: batch.search()
results = batch.search(seq)
for enzyme, sites in results.items():
    if sites:
        print(f'{enzyme}: {sites}')

# Method 2: Analysis class
analysis = Analysis(batch, seq)
results = analysis.full()
```

## Use Built-in Enzyme Collections

```python
from Bio.Restriction import AllEnzymes, CommOnly

# All known enzymes (800+)
analysis = Analysis(AllEnzymes, seq)

# Commercially available only
analysis = Analysis(CommOnly, seq)

# Get results
results = analysis.full()
for enzyme, sites in results.items():
    if sites:
        print(f'{enzyme}: {sites}')
```

## Linear vs Circular DNA

```python
from Bio.Restriction import EcoRI, Analysis, RestrictionBatch

# Linear DNA (default)
sites_linear = EcoRI.search(seq, linear=True)

# Circular DNA (plasmid)
sites_circular = EcoRI.search(seq, linear=False)

# With Analysis class
batch = RestrictionBatch([EcoRI, BamHI])
analysis = Analysis(batch, seq, linear=False)  # Circular
```

## Filter Results

```python
from Bio.Restriction import Analysis, CommOnly

analysis = Analysis(CommOnly, seq)

# Only enzymes that cut
analysis.print_that_cut()

# Only enzymes that don't cut (non-cutters)
analysis.print_that_dont_cut()

# Enzymes that cut once
analysis.print_once_cutters()

# Enzymes that cut twice
analysis.print_twice_cutters()

# Get as dictionary
cutters = analysis.only_cut()
non_cutters = analysis.only_dont_cut()
once_cutters = analysis.once_cutters()
twice_cutters = analysis.twice_cutters()
```

## Get Enzyme Information

```python
from Bio.Restriction import EcoRI

# Recognition sequence
print(f'Site: {EcoRI.site}')           # GAATTC
print(f'Esite: {EcoRI.esite}')         # Recognition with cut position

# Cut characteristics
print(f'Overhang: {EcoRI.ovhg}')       # 4 (positive = 5' overhang)
print(f'Blunt: {EcoRI.is_blunt()}')    # False
print(f'5\' overhang: {EcoRI.is_5overhang()}')  # True
print(f'3\' overhang: {EcoRI.is_3overhang()}')  # False

# Overhang sequence
print(f'Overhang seq: {EcoRI.ovhgseq}')  # AATT

# Isoschizomers (same recognition, different cut)
print(f'Isoschizomers: {EcoRI.isoschizomers()}')

# Compatible enzymes (same overhang)
print(f'Compatible: {EcoRI.compatible_end()}')
```

## Common Cloning Enzymes

```python
from Bio.Restriction import (
    EcoRI, BamHI, HindIII, XhoI, SalI, NotI, XbaI, SpeI,
    NcoI, NdeI, BglII, PstI, KpnI, SacI, EcoRV, SmaI
)

common_enzymes = RestrictionBatch([
    EcoRI, BamHI, HindIII, XhoI, SalI, NotI, XbaI,
    NcoI, NdeI, BglII, PstI, KpnI, SacI, EcoRV, SmaI
])

analysis = Analysis(common_enzymes, seq)
results = analysis.full()
```

## Access Enzymes by Name

```python
from Bio.Restriction import AllEnzymes

# Get enzyme by string name
ecori = AllEnzymes.get('EcoRI')
sites = ecori.search(seq)

# Check if enzyme exists
if 'EcoRI' in AllEnzymes:
    print('EcoRI is in database')
```

## Search Multiple Sequences

```python
from Bio import SeqIO
from Bio.Restriction import RestrictionBatch, EcoRI, BamHI

batch = RestrictionBatch([EcoRI, BamHI])

for record in SeqIO.parse('sequences.fasta', 'fasta'):
    analysis = Analysis(batch, record.seq)
    results = analysis.full()
    print(f'{record.id}:')
    for enzyme, sites in results.items():
        if sites:
            print(f'  {enzyme}: {sites}')
```

## Notes

- **Positions are 1-based** - first base is position 1
- **Cut position** - where enzyme cuts (between bases)
- **Linear default** - set `linear=False` for circular DNA
- **Case insensitive** - recognition matches regardless of case
- **Ambiguous bases** - some enzymes recognize N, R, Y, etc.

## Related Skills

- restriction-mapping - Visualize cut positions on sequence
- enzyme-selection - Choose enzymes by criteria
- fragment-analysis - Analyze resulting fragments
