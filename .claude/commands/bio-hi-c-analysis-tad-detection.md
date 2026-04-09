# bio-hi-c-analysis-tad-detection

> Call topologically associating domains (TADs) from Hi-C data using insulation score, HiCExplorer, and other methods. Identify domain boundaries and hierarchical domain structure. Use when calling TADs from Hi-C insulation scores.

## Version Compatibility

Reference examples tested with: cooler 0.9+, cooltools 0.6+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# TAD Detection

**"Call TADs from my Hi-C data"** → Identify topologically associating domain boundaries using insulation score minima or other boundary-detection algorithms.
- Python: `cooltools.insulation(clr, window_bp)` then threshold boundary strength
- CLI: `hicFindTADs` (HiCExplorer)

Call topologically associating domains from Hi-C contact matrices.

## Required Imports

```python
import cooler
import cooltools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bioframe
```

## Compute Insulation Score

```python
clr = cooler.Cooler('matrix.mcool::resolutions/10000')
view_df = bioframe.make_viewframe(clr.chromsizes)

# Compute insulation score
insulation = cooltools.insulation(
    clr,
    window_bp=[100000, 200000, 500000],  # Multiple window sizes
    ignore_diags=2,
)

print(insulation.head())
# Columns include: chrom, start, end, log2_insulation_score_100000, etc.
```

## Call TAD Boundaries

```python
# Find boundaries (local minima in insulation score)
boundaries = cooltools.find_insulation(
    clr,
    window_bp=200000,  # Single window
    ignore_diags=2,
    min_dist_bad_bin=0,
)

# Filter significant boundaries
boundaries['is_boundary'] = boundaries['boundary_strength'] > 0.1
strong_boundaries = boundaries[boundaries['is_boundary']]
print(f'Found {len(strong_boundaries)} TAD boundaries')
```

## Extract TAD Regions

**Goal:** Convert a set of TAD boundary positions into TAD interval coordinates (start-end pairs) for downstream overlap analysis.

**Approach:** Sort boundaries by position per chromosome, then define each TAD as the interval between consecutive boundary positions.

```python
def boundaries_to_tads(boundaries_df, chrom):
    '''Convert boundary positions to TAD intervals'''
    chr_bounds = boundaries_df[
        (boundaries_df['chrom'] == chrom) &
        (boundaries_df['is_boundary'])
    ].sort_values('start')

    tads = []
    starts = [0] + list(chr_bounds['start'])
    ends = list(chr_bounds['start']) + [boundaries_df[boundaries_df['chrom'] == chrom]['end'].max()]

    for start, end in zip(starts, ends):
        if end > start:
            tads.append({'chrom': chrom, 'start': start, 'end': end})

    return pd.DataFrame(tads)

tads_chr1 = boundaries_to_tads(boundaries, 'chr1')
print(f'chr1 TADs: {len(tads_chr1)}')
print(tads_chr1.head())
```

## Using HiCExplorer (CLI)

```bash
# Compute TADs with HiCExplorer
hicFindTADs \
    -m matrix.cool \
    --outPrefix tads \
    --correctForMultipleTesting fdr \
    --minDepth 60000 \
    --maxDepth 200000 \
    --step 10000 \
    --thresholdComparisons 0.05

# Output files:
# tads_domains.bed - TAD intervals
# tads_boundaries.bed - Boundary positions
# tads_score.bedgraph - Insulation score track
```

## Using HiCExplorer in Python

```python
# After running hicFindTADs
tads = pd.read_csv('tads_domains.bed', sep='\t', header=None,
                   names=['chrom', 'start', 'end'])
boundaries = pd.read_csv('tads_boundaries.bed', sep='\t', header=None,
                         names=['chrom', 'start', 'end', 'score'])

print(f'TADs: {len(tads)}')
print(f'Boundaries: {len(boundaries)}')
```

## TAD Statistics

```python
# Calculate TAD sizes
tads['size'] = tads['end'] - tads['start']

print('TAD size statistics:')
print(f'  Mean: {tads["size"].mean() / 1000:.0f} kb')
print(f'  Median: {tads["size"].median() / 1000:.0f} kb')
print(f'  Min: {tads["size"].min() / 1000:.0f} kb')
print(f'  Max: {tads["size"].max() / 1000:.0f} kb')

# Size distribution
plt.hist(tads['size'] / 1000, bins=50)
plt.xlabel('TAD size (kb)')
plt.ylabel('Count')
plt.title('TAD size distribution')
plt.savefig('tad_sizes.png', dpi=150)
```

## Plot Insulation Score

```python
fig, ax = plt.subplots(figsize=(15, 3))

chr_data = insulation[insulation['chrom'] == 'chr1']
ax.plot(chr_data['start'] / 1e6, chr_data['log2_insulation_score_200000'])

# Mark boundaries
bounds = chr_data[chr_data['is_boundary']]
ax.scatter(bounds['start'] / 1e6, bounds['log2_insulation_score_200000'],
           color='red', s=20, zorder=5)

ax.set_xlabel('Position (Mb)')
ax.set_ylabel('Insulation score (log2)')
ax.set_title('chr1 insulation score (red = boundaries)')
plt.tight_layout()
plt.savefig('insulation_track.png', dpi=150)
```

## Compare TAD Boundaries Between Conditions

```python
# Load boundaries from two conditions
bounds1 = pd.read_csv('condition1_boundaries.bed', sep='\t',
                      names=['chrom', 'start', 'end'])
bounds2 = pd.read_csv('condition2_boundaries.bed', sep='\t',
                      names=['chrom', 'start', 'end'])

# Find overlapping boundaries (within tolerance)
tolerance = 50000  # 50kb

def find_overlaps(df1, df2, tol):
    overlaps = []
    for _, b1 in df1.iterrows():
        matches = df2[
            (df2['chrom'] == b1['chrom']) &
            (abs(df2['start'] - b1['start']) <= tol)
        ]
        if len(matches) > 0:
            overlaps.append(b1)
    return pd.DataFrame(overlaps)

shared = find_overlaps(bounds1, bounds2, tolerance)
print(f'Shared boundaries: {len(shared)}')
print(f'Condition 1 specific: {len(bounds1) - len(shared)}')
print(f'Condition 2 specific: {len(bounds2) - len(shared)}')
```

## Hierarchical TADs

```python
# Compute insulation at multiple scales
windows = [100000, 200000, 500000, 1000000]
insulation_multi = cooltools.insulation(clr, window_bp=windows, ignore_diags=2)

# Boundaries at each scale represent different hierarchy levels
for w in windows:
    col = f'is_boundary_{w}'
    n_bounds = insulation_multi[col].sum()
    print(f'Window {w/1000:.0f}kb: {n_bounds} boundaries')
```

## Export TADs

```python
# Save as BED
tads[['chrom', 'start', 'end']].to_csv(
    'tads.bed', sep='\t', index=False, header=False
)

# Save boundaries as BED
boundaries[boundaries['is_boundary']][['chrom', 'start', 'end', 'boundary_strength']].to_csv(
    'boundaries.bed', sep='\t', index=False, header=False
)

# Save insulation as bedGraph
insulation[['chrom', 'start', 'end', 'log2_insulation_score_200000']].to_csv(
    'insulation.bedgraph', sep='\t', index=False, header=False
)
```

## Related Skills

- hic-data-io - Load Hi-C matrices
- hic-visualization - Visualize TADs on contact matrices
- compartment-analysis - Compartments operate at larger scale than TADs
