# bio-restriction-mapping

> Create restriction maps showing enzyme cut positions on DNA sequences using Biopython Bio.Restriction. Visualize cut sites, calculate distances between sites, and generate text or graphical maps. Use when creating or analyzing restriction maps.

**Available tools:** Read, Bash

# Restriction Mapping

## Create Basic Restriction Map

```python
from Bio import SeqIO
from Bio.Restriction import EcoRI, BamHI, HindIII, RestrictionBatch, Analysis

record = SeqIO.read('sequence.fasta', 'fasta')
seq = record.seq

batch = RestrictionBatch([EcoRI, BamHI, HindIII])
analysis = Analysis(batch, seq)

# Print formatted map
analysis.print_as('map')
```

## Output Formats

```python
# Map format (visual)
analysis.print_as('map')

# Linear format (list)
analysis.print_as('linear')

# Tabular format
analysis.print_as('tabulate')

# Get as string instead of printing
map_str = analysis.format_as('map')
linear_str = analysis.format_as('linear')
```

## Calculate Distances Between Sites

```python
from Bio.Restriction import EcoRI, BamHI

ecori_sites = EcoRI.search(seq)
bamhi_sites = BamHI.search(seq)

# All cut positions sorted
all_sites = sorted(ecori_sites + bamhi_sites)

# Calculate distances between consecutive sites
distances = []
for i in range(len(all_sites) - 1):
    dist = all_sites[i + 1] - all_sites[i]
    distances.append((all_sites[i], all_sites[i + 1], dist))
    print(f'{all_sites[i]} -> {all_sites[i + 1]}: {dist} bp')
```

## Create Detailed Restriction Map

```python
from Bio import SeqIO
from Bio.Restriction import RestrictionBatch, Analysis
from Bio.Restriction import EcoRI, BamHI, HindIII, XhoI, NotI

record = SeqIO.read('plasmid.fasta', 'fasta')
seq = record.seq
seq_len = len(seq)

enzymes = RestrictionBatch([EcoRI, BamHI, HindIII, XhoI, NotI])
analysis = Analysis(enzymes, seq, linear=False)

print(f'Restriction Map: {record.id}')
print(f'Length: {seq_len} bp (circular)')
print('=' * 50)

results = analysis.full()
all_cuts = []

for enzyme, sites in results.items():
    for site in sites:
        all_cuts.append((site, str(enzyme)))

all_cuts.sort(key=lambda x: x[0])

print('\nCut sites (5\' -> 3\'):')
for pos, enz in all_cuts:
    pct = (pos / seq_len) * 100
    print(f'  {pos:6d} bp ({pct:5.1f}%) - {enz}')
```

## Text-Based Map Visualization

```python
def draw_restriction_map(seq, results, width=80):
    '''Draw a simple text restriction map'''
    seq_len = len(seq)
    scale = width / seq_len

    # Header
    print(f'0{" " * (width - 6)}{seq_len}')
    print('|' + '-' * (width - 2) + '|')

    # Plot each enzyme
    for enzyme, sites in results.items():
        if not sites:
            continue
        line = [' '] * width
        for site in sites:
            pos = int(site * scale)
            if pos >= width:
                pos = width - 1
            line[pos] = '|'
        print(''.join(line) + f' {enzyme}')

    print('|' + '-' * (width - 2) + '|')

# Usage
batch = RestrictionBatch([EcoRI, BamHI, HindIII])
analysis = Analysis(batch, seq)
results = analysis.full()
draw_restriction_map(seq, results)
```

## Map with GenBank Features

```python
from Bio import SeqIO
from Bio.Restriction import RestrictionBatch, Analysis, EcoRI, BamHI

record = SeqIO.read('plasmid.gb', 'genbank')
seq = record.seq

enzymes = RestrictionBatch([EcoRI, BamHI])
analysis = Analysis(enzymes, seq, linear=False)
results = analysis.full()

print('Restriction Sites and Overlapping Features:')
print('=' * 60)

for enzyme, sites in results.items():
    for site in sites:
        print(f'\n{enzyme} at position {site}:')
        for feature in record.features:
            start = int(feature.location.start)
            end = int(feature.location.end)
            if start <= site <= end:
                feat_type = feature.type
                label = feature.qualifiers.get('label', feature.qualifiers.get('gene', ['unknown']))[0]
                print(f'  Within {feat_type}: {label} ({start}-{end})')
```

## Export Map to File

```python
def export_restriction_map(seq, results, output_file, seq_name='sequence'):
    '''Export restriction map to text file'''
    with open(output_file, 'w') as f:
        f.write(f'Restriction Map: {seq_name}\n')
        f.write(f'Length: {len(seq)} bp\n')
        f.write('=' * 50 + '\n\n')

        all_cuts = []
        for enzyme, sites in results.items():
            for site in sites:
                all_cuts.append((site, str(enzyme)))

        all_cuts.sort()

        f.write('Site\tPosition\tFrom_Start\n')
        for pos, enz in all_cuts:
            f.write(f'{enz}\t{pos}\t{pos}\n')

        f.write('\n\nFragment sizes between sites:\n')
        if all_cuts:
            positions = sorted([c[0] for c in all_cuts])
            for i in range(len(positions) - 1):
                size = positions[i + 1] - positions[i]
                f.write(f'{positions[i]} -> {positions[i + 1]}: {size} bp\n')

# Usage
export_restriction_map(seq, results, 'restriction_map.txt', record.id)
```

## Circular Map Coordinates

```python
def circular_distances(sites, seq_len):
    '''Calculate fragment sizes for circular DNA'''
    if not sites:
        return []

    sites = sorted(sites)
    fragments = []

    # Between consecutive sites
    for i in range(len(sites) - 1):
        fragments.append(sites[i + 1] - sites[i])

    # Wrap-around fragment
    wrap = (seq_len - sites[-1]) + sites[0]
    fragments.append(wrap)

    return fragments

# Usage
ecori_sites = EcoRI.search(seq, linear=False)
fragments = circular_distances(ecori_sites, len(seq))
print(f'EcoRI fragments (circular): {fragments}')
```

## Related Skills

- restriction-sites - Find where enzymes cut
- enzyme-selection - Choose enzymes for mapping
- fragment-analysis - Analyze fragment sizes
