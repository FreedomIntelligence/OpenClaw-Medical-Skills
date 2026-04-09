# bio-restriction-fragment-analysis

> Analyze restriction digest fragments using Biopython Bio.Restriction. Predict fragment sizes, get fragment sequences, simulate gel electrophoresis patterns, and perform double digests. Use when analyzing restriction digest fragment patterns.

**Available tools:** Read, Bash

# Fragment Analysis

## Get Fragment Sizes

```python
from Bio import SeqIO
from Bio.Restriction import EcoRI

record = SeqIO.read('sequence.fasta', 'fasta')
seq = record.seq

# catalyze() returns tuple: (fragments_5prime, fragments_3prime)
# For standard use, take the first element
fragments = EcoRI.catalyze(seq)[0]

# fragments is tuple of Seq objects
sizes = [len(f) for f in fragments]
print(f'Fragment sizes: {sorted(sizes, reverse=True)}')
```

## Linear vs Circular Digestion

```python
from Bio.Restriction import EcoRI

# Linear DNA
fragments_linear = EcoRI.catalyze(seq, linear=True)[0]

# Circular DNA (plasmid)
fragments_circular = EcoRI.catalyze(seq, linear=False)[0]

# Circular produces one fewer fragment (ends join)
print(f'Linear: {len(fragments_linear)} fragments')
print(f'Circular: {len(fragments_circular)} fragments')
```

## Get Fragment Sequences

```python
from Bio.Restriction import EcoRI

fragments = EcoRI.catalyze(seq)[0]

for i, frag in enumerate(fragments, 1):
    print(f'Fragment {i}: {len(frag)} bp')
    print(f'  5\' end: {frag[:20]}...')
    print(f'  3\' end: ...{frag[-20:]}')
```

## Double Digest

```python
from Bio.Restriction import EcoRI, BamHI, RestrictionBatch

# Method 1: Sequential digestion
frags_ecori = EcoRI.catalyze(seq)[0]
final_fragments = []
for frag in frags_ecori:
    sub_frags = BamHI.catalyze(frag)[0]
    final_fragments.extend(sub_frags)

# Method 2: Using RestrictionBatch
batch = RestrictionBatch([EcoRI, BamHI])
# Note: RestrictionBatch doesn't have catalyze, use Analysis

# Method 3: Manual calculation from positions
ecori_sites = EcoRI.search(seq)
bamhi_sites = BamHI.search(seq)
all_sites = sorted(set(ecori_sites + bamhi_sites))

fragment_sizes = []
for i in range(len(all_sites) - 1):
    fragment_sizes.append(all_sites[i + 1] - all_sites[i])
# Add terminal fragments
fragment_sizes.insert(0, all_sites[0])
fragment_sizes.append(len(seq) - all_sites[-1])
```

## Calculate Fragment Sizes from Positions

```python
def fragments_from_positions(seq_len, cut_positions, linear=True):
    '''Calculate fragment sizes from cut positions'''
    if not cut_positions:
        return [seq_len]

    positions = sorted(cut_positions)
    fragments = []

    if linear:
        # First fragment: start to first cut
        fragments.append(positions[0])
        # Middle fragments
        for i in range(len(positions) - 1):
            fragments.append(positions[i + 1] - positions[i])
        # Last fragment: last cut to end
        fragments.append(seq_len - positions[-1])
    else:
        # Circular: all fragments between cuts
        for i in range(len(positions) - 1):
            fragments.append(positions[i + 1] - positions[i])
        # Wrap-around fragment
        fragments.append((seq_len - positions[-1]) + positions[0])

    return fragments

# Usage
sites = EcoRI.search(seq)
sizes = fragments_from_positions(len(seq), sites, linear=True)
print(f'Fragment sizes: {sorted(sizes, reverse=True)}')
```

## Simulate Gel Pattern

```python
def simulate_gel(fragment_sizes, ladder=None):
    '''Print a text-based gel simulation'''
    if ladder is None:
        ladder = [10000, 8000, 6000, 5000, 4000, 3000, 2000, 1500, 1000, 750, 500, 250]

    max_size = max(max(fragment_sizes), max(ladder))

    print('Ladder  |  Digest')
    print('-' * 30)

    for size in sorted(ladder + fragment_sizes, reverse=True):
        ladder_mark = f'{size:>6}' if size in ladder else '      '
        digest_mark = '====' if size in fragment_sizes else ''
        print(f'{ladder_mark}  |  {digest_mark}')

# Usage
sizes = [len(f) for f in EcoRI.catalyze(seq)[0]]
simulate_gel(sizes)
```

## Detailed Fragment Report

```python
from Bio.Restriction import EcoRI, BamHI

def fragment_report(seq, enzyme, linear=True):
    '''Generate detailed fragment analysis'''
    sites = enzyme.search(seq, linear=linear)
    fragments = enzyme.catalyze(seq, linear=linear)[0]

    print(f'Enzyme: {enzyme}')
    print(f'Recognition site: {enzyme.site}')
    print(f'Number of sites: {len(sites)}')
    print(f'Cut positions: {sites}')
    print(f'\nFragments ({len(fragments)}):')

    sizes = sorted([len(f) for f in fragments], reverse=True)
    total = sum(sizes)

    for i, size in enumerate(sizes, 1):
        pct = (size / total) * 100
        print(f'  {i}. {size:6d} bp ({pct:5.1f}%)')

    print(f'\nTotal: {total} bp')
    return sizes

# Usage
sizes = fragment_report(seq, EcoRI)
```

## Compare Expected vs Observed Fragments

```python
def compare_fragments(expected, observed, tolerance=50):
    '''Compare expected fragment sizes with observed (from gel)'''
    matched = []
    unmatched_exp = list(expected)
    unmatched_obs = list(observed)

    for exp in expected:
        for obs in observed:
            if abs(exp - obs) <= tolerance:
                matched.append((exp, obs))
                if exp in unmatched_exp:
                    unmatched_exp.remove(exp)
                if obs in unmatched_obs:
                    unmatched_obs.remove(obs)
                break

    print('Matched fragments:')
    for exp, obs in matched:
        print(f'  Expected: {exp}, Observed: {obs}')

    if unmatched_exp:
        print(f'\nMissing (expected but not observed): {unmatched_exp}')
    if unmatched_obs:
        print(f'\nExtra (observed but not expected): {unmatched_obs}')

# Usage
expected = [3000, 2000, 1500, 500]
observed = [3050, 2000, 1480, 510, 200]  # From gel
compare_fragments(expected, observed)
```

## Fragment with Sequence Context

```python
from Bio.Restriction import EcoRI

def annotated_fragments(seq, enzyme, context=50):
    '''Get fragments with surrounding sequence context'''
    sites = enzyme.search(seq)
    fragments = enzyme.catalyze(seq)[0]

    print(f'{enzyme} digest ({len(fragments)} fragments):')

    for i, (frag, site) in enumerate(zip(fragments, [0] + sites), 1):
        print(f'\nFragment {i}: {len(frag)} bp (starts at {site})')
        print(f"  5' sequence: {str(frag[:context])}...")
        print(f"  3' sequence: ...{str(frag[-context:])}")

# Usage
annotated_fragments(seq, EcoRI)
```

## Notes

- **catalyze() returns tuple** - use `[0]` to get 5' fragments
- **Fragment order** - fragments returned in 5' to 3' order
- **Circular DNA** - produces n fragments from n cuts (not n+1)
- **Double digest** - combine cut positions, then calculate fragments

## Related Skills

- restriction-sites - Find cut positions for fragment calculation
- restriction-mapping - Visualize fragment positions
- enzyme-selection - Choose enzymes for desired fragments
