# bio-restriction-enzyme-selection

> Select restriction enzymes by criteria using Biopython Bio.Restriction. Find enzymes that cut once, don't cut, produce specific overhangs, are commercially available, or have compatible ends for cloning. Use when selecting restriction enzymes for cloning or analysis.

**Available tools:** Read, Bash

# Enzyme Selection

## Find Enzymes by Cut Frequency

```python
from Bio import SeqIO
from Bio.Restriction import Analysis, CommOnly, AllEnzymes

record = SeqIO.read('sequence.fasta', 'fasta')
seq = record.seq

analysis = Analysis(CommOnly, seq)

# Enzymes that cut exactly once (good for linearization)
once_cutters = analysis.once_cutters()

# Enzymes that cut exactly twice (good for excision)
twice_cutters = analysis.twice_cutters()

# Enzymes that don't cut (good for cloning insert)
non_cutters = analysis.only_dont_cut()

# All enzymes that cut (any number of times)
all_cutters = analysis.only_cut()
```

## Find Non-Cutters for Insert

```python
from Bio.Restriction import Analysis, CommOnly

# Find enzymes that don't cut your insert
insert_seq = record.seq
analysis = Analysis(CommOnly, insert_seq)

non_cutters = analysis.only_dont_cut()
print('Enzymes that do not cut the insert:')
for enzyme in non_cutters:
    print(f'  {enzyme}')
```

## Find Compatible Enzyme Pairs

```python
from Bio.Restriction import EcoRI, BamHI, BglII, XhoI, SalI

# Check if enzymes produce compatible overhangs
def find_compatible_enzymes(enzyme):
    '''Find enzymes with same overhang'''
    compatible = enzyme.compatible_end()
    print(f'{enzyme} is compatible with: {compatible}')

find_compatible_enzymes(BamHI)  # Compatible with BglII
find_compatible_enzymes(XhoI)   # Compatible with SalI
```

## Filter by Overhang Type

```python
from Bio.Restriction import CommOnly, Analysis

analysis = Analysis(CommOnly, seq)
cutters = analysis.only_cut()

# Filter by overhang type
blunt_cutters = [e for e in cutters if e.is_blunt()]
five_prime = [e for e in cutters if e.is_5overhang()]
three_prime = [e for e in cutters if e.is_3overhang()]

print(f'Blunt cutters: {len(blunt_cutters)}')
print(f'5\' overhang: {len(five_prime)}')
print(f'3\' overhang: {len(three_prime)}')
```

## Filter by Recognition Site Length

```python
from Bio.Restriction import AllEnzymes, CommOnly

# 6-cutters (most common for cloning)
six_cutters = [e for e in CommOnly if len(e.site) == 6]

# 8-cutters (rare cutters, good for large constructs)
eight_cutters = [e for e in CommOnly if len(e.site) == 8]

# 4-cutters (frequent cutters)
four_cutters = [e for e in CommOnly if len(e.site) == 4]

print(f'4-cutters: {len(four_cutters)}')
print(f'6-cutters: {len(six_cutters)}')
print(f'8-cutters: {len(eight_cutters)}')
```

## Find Enzymes with Specific Overhang

```python
from Bio.Restriction import CommOnly

def find_by_overhang(overhang_seq):
    '''Find enzymes that produce a specific overhang'''
    matching = []
    for enzyme in CommOnly:
        if hasattr(enzyme, 'ovhgseq') and enzyme.ovhgseq == overhang_seq:
            matching.append(enzyme)
    return matching

# Find enzymes with AATT overhang (like EcoRI)
aatt_enzymes = find_by_overhang('AATT')
print(f'Enzymes with AATT overhang: {aatt_enzymes}')
```

## Find Unique Cutters in Multiple Sequences

```python
from Bio import SeqIO
from Bio.Restriction import Analysis, CommOnly

records = list(SeqIO.parse('sequences.fasta', 'fasta'))

# Find enzymes that cut once in each sequence
common_once_cutters = None

for record in records:
    analysis = Analysis(CommOnly, record.seq)
    once = set(analysis.once_cutters().keys())

    if common_once_cutters is None:
        common_once_cutters = once
    else:
        common_once_cutters &= once

print('Enzymes that cut once in all sequences:')
for enzyme in common_once_cutters:
    print(f'  {enzyme}')
```

## Select Enzymes for Directional Cloning

```python
from Bio.Restriction import Analysis, CommOnly

def find_cloning_pairs(vector_seq, insert_seq):
    '''Find enzyme pairs for directional cloning'''

    # Analyze both sequences
    vec_analysis = Analysis(CommOnly, vector_seq)
    ins_analysis = Analysis(CommOnly, insert_seq)

    # Enzymes that cut vector once
    vec_once = set(vec_analysis.once_cutters().keys())

    # Enzymes that don't cut insert
    ins_non = set(ins_analysis.only_dont_cut())

    # Candidates: cut vector once, don't cut insert
    candidates = vec_once & ins_non

    # Group by overhang type for pairs
    five_prime = [e for e in candidates if e.is_5overhang()]
    three_prime = [e for e in candidates if e.is_3overhang()]
    blunt = [e for e in candidates if e.is_blunt()]

    print(f'Candidate enzymes: {len(candidates)}')
    print(f"  5' overhang: {[str(e) for e in five_prime[:5]]}")
    print(f"  3' overhang: {[str(e) for e in three_prime[:5]]}")
    print(f"  Blunt: {[str(e) for e in blunt[:5]]}")

    return candidates

# Usage
# candidates = find_cloning_pairs(vector_seq, insert_seq)
```

## Check Commercial Availability

```python
from Bio.Restriction import CommOnly, AllEnzymes, EcoRI

# Check if enzyme is commercially available
def is_commercial(enzyme):
    return enzyme in CommOnly

print(f'EcoRI commercial: {is_commercial(EcoRI)}')

# List all commercial enzymes
print(f'Total commercial enzymes: {len(CommOnly)}')
```

## Find Isoschizomers

```python
from Bio.Restriction import EcoRI, HpaII

# Isoschizomers: same recognition, may have different cuts
isoschizomers = EcoRI.isoschizomers()
print(f'EcoRI isoschizomers: {isoschizomers}')

# Neoschizomers: same recognition, different cut position
neoschizomers = HpaII.neoschizomers()
print(f'HpaII neoschizomers: {neoschizomers}')
```

## Check Methylation Sensitivity

Some enzymes are blocked by DNA methylation (Dam, Dcm in E. coli). Important when digesting genomic DNA from bacteria.

```python
from Bio.Restriction import DpnI, DpnII, Sau3AI, MboI

# Check if enzyme is sensitive to methylation
def check_methylation(enzyme):
    dam = enzyme.is_dam_methylable()
    dcm = enzyme.is_dcm_methylable()
    print(f'{enzyme}: Dam={dam}, Dcm={dcm}')

check_methylation(DpnI)   # Requires Dam methylation to cut
check_methylation(DpnII)  # Blocked by Dam methylation
check_methylation(Sau3AI) # Not affected by Dam
check_methylation(MboI)   # Blocked by Dam methylation
```

```python
from Bio.Restriction import CommOnly, Analysis

# Find enzymes not affected by common methylation
def find_methylation_insensitive(seq):
    analysis = Analysis(CommOnly, seq)
    cutters = analysis.only_cut()

    insensitive = [e for e in cutters
                   if not e.is_dam_methylable() and not e.is_dcm_methylable()]

    print(f'Methylation-insensitive cutters: {len(insensitive)}')
    return insensitive

# Usage for genomic DNA from E. coli
# insensitive = find_methylation_insensitive(seq)
```

## Type IIS Enzymes for Golden Gate Cloning

Type IIS enzymes cut outside their recognition site, enabling scarless assembly.

```python
from Bio.Restriction import BsaI, BbsI, BsmBI, SapI

# Type IIS enzymes cut outside recognition sequence
# BsaI: GGTCTC(N)1 - cuts 1bp after recognition
# BsmBI: CGTCTC(N)1

def type_iis_info(enzyme):
    print(f'{enzyme}:')
    print(f'  Recognition: {enzyme.site}')
    print(f'  Overhang: {enzyme.ovhg} bp ({enzyme.ovhgseq if enzyme.ovhgseq else "variable"})')
    print(f'  Cuts outside: {enzyme.fst3cut}, {enzyme.fst5cut}')

type_iis_info(BsaI)
type_iis_info(BsmBI)
```

```python
from Bio.Restriction import BsaI, BsmBI
from Bio.Seq import Seq

# Golden Gate assembly: design parts with compatible overhangs
# BsaI creates 4-bp overhangs that can be designed for specific fusion

def find_golden_gate_sites(seq, enzyme=BsaI):
    '''Find Type IIS sites and their overhang positions'''
    sites = enzyme.search(seq)

    if not sites:
        print(f'No {enzyme} sites found - sequence is Golden Gate compatible')
        return []

    print(f'{enzyme} sites found at: {sites}')
    print('These sites must be removed for Golden Gate cloning')
    return sites

# Check if insert is free of BsaI sites
insert_seq = Seq('ATGCGATCGATCGATCG')
find_golden_gate_sites(insert_seq, BsaI)
```

```python
# Common Type IIS enzymes for Golden Gate/modular cloning
from Bio.Restriction import BsaI, BsmBI, BbsI, SapI, BtgZI

golden_gate_enzymes = [BsaI, BsmBI, BbsI, SapI, BtgZI]

for enzyme in golden_gate_enzymes:
    print(f'{enzyme}: site={enzyme.site}, overhang={enzyme.ovhg}bp')
```

## Enzyme Properties Reference

```python
from Bio.Restriction import EcoRI

# Get all properties
print(f'Site: {EcoRI.site}')
print(f'Cut: {EcoRI.fst3cut}, {EcoRI.fst5cut}')
print(f'Overhang: {EcoRI.ovhg} ({EcoRI.ovhgseq})')
print(f'Blunt: {EcoRI.is_blunt()}')
print(f'5\' overhang: {EcoRI.is_5overhang()}')
print(f'3\' overhang: {EcoRI.is_3overhang()}')
print(f'Ambiguous: {EcoRI.is_ambiguous()}')
print(f'Defined: {EcoRI.is_defined()}')
```

## Related Skills

- restriction-sites - Find where selected enzymes cut
- restriction-mapping - Map selected enzyme sites
- fragment-analysis - Predict fragments from selected enzymes
