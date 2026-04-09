# bio-hi-c-analysis-loop-calling

> Detect chromatin loops and point interactions from Hi-C data using cooltools, chromosight, and HiCCUPS-like methods. Identify CTCF-mediated loops and enhancer-promoter contacts. Use when detecting chromatin loops from Hi-C data.

## Version Compatibility

Reference examples tested with: bedtools 2.31+, cooler 0.9+, cooltools 0.6+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, pybedtools 0.9+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Chromatin Loop Calling

**"Call chromatin loops from my Hi-C data"** → Detect point enrichments in contact matrices representing CTCF-mediated loops and enhancer-promoter interactions.
- Python: `cooltools.dots()` or `chromosight detect --pattern=loops`

Detect chromatin loops and point interactions from Hi-C data.

## Required Imports

```python
import cooler
import cooltools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bioframe
```

## Call Loops with cooltools (Dot Calling)

```python
clr = cooler.Cooler('matrix.mcool::resolutions/10000')
view_df = bioframe.make_viewframe(clr.chromsizes)

# Compute expected values
expected = cooltools.expected_cis(clr, view_df=view_df, ignore_diags=2)

# Call dots (loops)
dots = cooltools.dots(
    clr,
    expected=expected,
    view_df=view_df,
    max_loci_separation=2000000,  # Max loop size (2Mb)
    max_nans_tolerated=0.5,
)

print(f'Found {len(dots)} loops')
print(dots.head())
```

## Using chromosight (CLI)

```bash
# Call loops with chromosight
chromosight detect \
    --pattern loops \
    --min-dist 20000 \
    --max-dist 2000000 \
    matrix.cool \
    loops_output

# Output: loops_output.tsv with loop coordinates and scores
```

## Parse chromosight Output

```python
loops = pd.read_csv('loops_output.tsv', sep='\t')
print(f'Found {len(loops)} loops')
print(loops.head())

# Columns: chrom1, start1, end1, chrom2, start2, end2, score, etc.
```

## Using HiCExplorer hicDetectLoops

```bash
# Call loops with HiCExplorer
hicDetectLoops \
    -m matrix.cool \
    -o loops.bedgraph \
    --maxLoopDistance 2000000 \
    --windowSize 10 \
    --peakWidth 6 \
    --pValuePreselection 0.05 \
    --pValue 0.05
```

## Loop Statistics

```python
# Calculate loop sizes
loops['size'] = abs(loops['end2'] - loops['start1'])

print('Loop size statistics:')
print(f'  Mean: {loops["size"].mean() / 1000:.0f} kb')
print(f'  Median: {loops["size"].median() / 1000:.0f} kb')
print(f'  Min: {loops["size"].min() / 1000:.0f} kb')
print(f'  Max: {loops["size"].max() / 1000:.0f} kb')

# Size distribution
plt.hist(loops['size'] / 1000, bins=50)
plt.xlabel('Loop size (kb)')
plt.ylabel('Count')
plt.savefig('loop_sizes.png', dpi=150)
```

## Filter Loops by Score

```python
# Keep high-confidence loops
score_threshold = loops['score'].quantile(0.75)
high_conf_loops = loops[loops['score'] >= score_threshold]
print(f'High confidence loops: {len(high_conf_loops)}')
```

## Annotate Loops with Features

```python
import pybedtools

# Convert loop anchors to BED
anchor1 = loops[['chrom1', 'start1', 'end1']].copy()
anchor1.columns = ['chrom', 'start', 'end']
anchor2 = loops[['chrom2', 'start2', 'end2']].copy()
anchor2.columns = ['chrom', 'start', 'end']

# Load CTCF peaks
ctcf_peaks = pybedtools.BedTool('ctcf_peaks.bed')

# Intersect anchors with CTCF
anchor1_bed = pybedtools.BedTool.from_dataframe(anchor1)
anchor1_ctcf = anchor1_bed.intersect(ctcf_peaks, wa=True, u=True)

print(f'Anchors with CTCF: {len(anchor1_ctcf)} / {len(anchor1)}')
```

## Compare Loops Between Conditions

```python
# Load loops from two conditions
loops1 = pd.read_csv('condition1_loops.bedpe', sep='\t')
loops2 = pd.read_csv('condition2_loops.bedpe', sep='\t')

# Find overlapping loops
tolerance = 20000  # 20kb

def loops_overlap(l1, l2, tol):
    return (l1['chrom1'] == l2['chrom1'] and
            l1['chrom2'] == l2['chrom2'] and
            abs(l1['start1'] - l2['start1']) <= tol and
            abs(l1['start2'] - l2['start2']) <= tol)

shared = []
for _, loop1 in loops1.iterrows():
    for _, loop2 in loops2.iterrows():
        if loops_overlap(loop1, loop2, tolerance):
            shared.append(loop1)
            break

print(f'Shared loops: {len(shared)}')
print(f'Condition 1 specific: {len(loops1) - len(shared)}')
print(f'Condition 2 specific: {len(loops2) - len(set(range(len(loops2))) - set([]))}')
```

## Aggregate Peak Analysis (APA)

**Goal:** Assess the overall strength and validity of called loops by stacking contact sub-matrices centered on loop anchors and averaging the signal.

**Approach:** For each loop, extract a fixed-size snippet from the contact matrix centered on the loop anchor pair, then compute the element-wise mean across all snippets to produce an aggregate enrichment map.

```python
# Stack loops and compute average signal
from cooltools.lib import snip

def compute_apa(clr, loops, window=100000, resolution=10000):
    '''Compute average peak analysis'''
    flank = window // resolution

    stacks = []
    for _, loop in loops.iterrows():
        try:
            # Get region around loop
            snippet = clr.matrix(balance=True).fetch(
                f"{loop['chrom1']}:{loop['start1']-window}-{loop['end1']+window}",
                f"{loop['chrom2']}:{loop['start2']-window}-{loop['end2']+window}"
            )
            if snippet.shape[0] == snippet.shape[1]:
                stacks.append(snippet)
        except:
            continue

    if len(stacks) > 0:
        apa = np.nanmean(stacks, axis=0)
        return apa
    return None

apa_matrix = compute_apa(clr, loops.head(100))
if apa_matrix is not None:
    plt.imshow(np.log2(apa_matrix), cmap='Reds')
    plt.colorbar(label='log2(contact)')
    plt.title('Aggregate Peak Analysis')
    plt.savefig('apa.png', dpi=150)
```

## Using cooltools pileup for APA

```python
import cooltools

# Compute pileup (APA)
stack = cooltools.pileup(
    clr,
    features=loops[['chrom1', 'start1', 'end1', 'chrom2', 'start2', 'end2']],
    view_df=view_df,
    expected=expected,
    flank=100000,
)

# Average across all features
apa = np.nanmean(stack, axis=2)
```

## Export Loops

```python
# Save as BEDPE
loops[['chrom1', 'start1', 'end1', 'chrom2', 'start2', 'end2', 'score']].to_csv(
    'loops.bedpe', sep='\t', index=False, header=False
)

# Save as Juicer format (for visualization in Juicebox)
loops_juicer = loops.copy()
loops_juicer['color'] = '0,0,255'  # Blue
loops_juicer[['chrom1', 'start1', 'end1', 'chrom2', 'start2', 'end2', 'color']].to_csv(
    'loops.2dbed', sep='\t', index=False, header=False
)
```

## Loops at Promoter-Enhancer Pairs

```python
# Check if loops connect promoters and enhancers
promoters = pd.read_csv('promoters.bed', sep='\t', names=['chrom', 'start', 'end', 'gene'])
enhancers = pd.read_csv('enhancers.bed', sep='\t', names=['chrom', 'start', 'end'])

# For each loop, check if one anchor is promoter, other is enhancer
pe_loops = []
for _, loop in loops.iterrows():
    # Check anchor 1
    anchor1_prom = any((promoters['chrom'] == loop['chrom1']) &
                       (promoters['start'] <= loop['end1']) &
                       (promoters['end'] >= loop['start1']))
    anchor1_enh = any((enhancers['chrom'] == loop['chrom1']) &
                      (enhancers['start'] <= loop['end1']) &
                      (enhancers['end'] >= loop['start1']))

    # Check anchor 2
    anchor2_prom = any((promoters['chrom'] == loop['chrom2']) &
                       (promoters['start'] <= loop['end2']) &
                       (promoters['end'] >= loop['start2']))
    anchor2_enh = any((enhancers['chrom'] == loop['chrom2']) &
                      (enhancers['start'] <= loop['end2']) &
                      (enhancers['end'] >= loop['start2']))

    if (anchor1_prom and anchor2_enh) or (anchor1_enh and anchor2_prom):
        pe_loops.append(loop)

print(f'Promoter-enhancer loops: {len(pe_loops)}')
```

## Related Skills

- hic-data-io - Load Hi-C matrices
- hic-visualization - Visualize loops
- chip-seq - CTCF ChIP-seq for loop anchor validation
