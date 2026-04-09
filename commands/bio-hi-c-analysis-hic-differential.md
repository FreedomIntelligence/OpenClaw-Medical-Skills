# bio-hi-c-analysis-hic-differential

> Compare Hi-C contact matrices between conditions to identify differential chromatin interactions. Compute log2 fold changes, statistical significance, and visualize differential contact maps. Use when comparing Hi-C contacts between conditions.

## Version Compatibility

Reference examples tested with: cooler 0.9+, cooltools 0.6+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scipy 1.12+, statsmodels 0.14+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Hi-C Differential Analysis

**"Compare Hi-C contacts between my conditions"** → Compute log2 fold-change contact maps, identify statistically significant differential interactions, and visualize changes in 3D genome organization.
- Python: `cooltools` for expected values, custom differential analysis with `scipy.stats`

Compare Hi-C contact matrices between conditions.

## Required Imports

```python
import cooler
import cooltools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from scipy import stats
import bioframe
```

## Load Two Conditions

```python
# Load balanced cooler files at same resolution
clr1 = cooler.Cooler('condition1.mcool::resolutions/10000')
clr2 = cooler.Cooler('condition2.mcool::resolutions/10000')

print(f'Condition 1: {clr1.info["sum"]:,} contacts')
print(f'Condition 2: {clr2.info["sum"]:,} contacts')
```

## Compute Log2 Fold Change

```python
def log2_fold_change(clr1, clr2, region, pseudocount=1):
    '''Compute log2(condition2/condition1) for a region'''
    mat1 = clr1.matrix(balance=True).fetch(region)
    mat2 = clr2.matrix(balance=True).fetch(region)

    # Add pseudocount and compute log2 ratio
    log2fc = np.log2((mat2 + pseudocount) / (mat1 + pseudocount))
    log2fc[np.isinf(log2fc)] = np.nan

    return log2fc

region = 'chr1:50000000-60000000'
log2fc = log2_fold_change(clr1, clr2, region)
print(f'Log2FC range: {np.nanmin(log2fc):.2f} to {np.nanmax(log2fc):.2f}')
```

## Plot Differential Contact Map

```python
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Condition 1
mat1 = clr1.matrix(balance=True).fetch(region)
im1 = axes[0].imshow(np.log2(mat1 + 1), cmap='Reds', vmin=-10, vmax=-3)
axes[0].set_title('Condition 1')
plt.colorbar(im1, ax=axes[0])

# Condition 2
mat2 = clr2.matrix(balance=True).fetch(region)
im2 = axes[1].imshow(np.log2(mat2 + 1), cmap='Reds', vmin=-10, vmax=-3)
axes[1].set_title('Condition 2')
plt.colorbar(im2, ax=axes[1])

# Log2 fold change (diverging colormap)
norm = TwoSlopeNorm(vmin=-2, vcenter=0, vmax=2)
im3 = axes[2].imshow(log2fc, cmap='coolwarm', norm=norm)
axes[2].set_title('Log2(Cond2/Cond1)')
plt.colorbar(im3, ax=axes[2])

plt.tight_layout()
plt.savefig('differential_hic.png', dpi=150)
```

## Split View Comparison

```python
def plot_split_view(mat1, mat2, title=''):
    '''Upper triangle: condition1, Lower triangle: condition2'''
    combined = np.triu(mat1) + np.tril(mat2, k=-1)

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(np.log2(combined + 1), cmap='Reds', vmin=-10, vmax=-3)
    ax.axline((0, 0), slope=1, color='black', linewidth=0.5)
    ax.set_title(f'{title}\nUpper: Cond1, Lower: Cond2')
    plt.colorbar(im, ax=ax)
    return fig

mat1 = clr1.matrix(balance=True).fetch(region)
mat2 = clr2.matrix(balance=True).fetch(region)
fig = plot_split_view(mat1, mat2)
plt.savefig('split_view.png', dpi=150)
```

## Depth Normalization

```python
def depth_normalize(clr, target_depth=None):
    '''Normalize matrix to target sequencing depth'''
    total = clr.info['sum']
    if target_depth is None:
        return 1.0
    return target_depth / total

# Normalize both samples to same depth
target = min(clr1.info['sum'], clr2.info['sum'])
scale1 = depth_normalize(clr1, target)
scale2 = depth_normalize(clr2, target)

mat1_norm = clr1.matrix(balance=True).fetch(region) * scale1
mat2_norm = clr2.matrix(balance=True).fetch(region) * scale2
```

## Statistical Testing (Per-Pixel)

**Goal:** Identify individual contact pixels that are statistically significantly different between two conditions using biological replicates.

**Approach:** For each pixel position, collect values across replicates in both conditions, apply a per-pixel t-test or Mann-Whitney U test, then correct for multiple testing with FDR.

```python
def differential_test(matrices1, matrices2, method='ttest'):
    '''
    Test for differential contacts between replicates.
    matrices1/2: lists of numpy arrays (replicates)
    '''
    n1, n2 = len(matrices1), len(matrices2)
    shape = matrices1[0].shape

    pvalues = np.ones(shape)
    log2fc = np.zeros(shape)

    for i in range(shape[0]):
        for j in range(shape[1]):
            vals1 = [m[i, j] for m in matrices1 if not np.isnan(m[i, j])]
            vals2 = [m[i, j] for m in matrices2 if not np.isnan(m[i, j])]

            if len(vals1) >= 2 and len(vals2) >= 2:
                if method == 'ttest':
                    _, p = stats.ttest_ind(vals1, vals2)
                elif method == 'mannwhitneyu':
                    _, p = stats.mannwhitneyu(vals1, vals2, alternative='two-sided')
                pvalues[i, j] = p
                log2fc[i, j] = np.log2((np.mean(vals2) + 1) / (np.mean(vals1) + 1))

    return log2fc, pvalues

# Example with replicates
rep1_cond1 = [clr.matrix(balance=True).fetch(region) for clr in condition1_reps]
rep1_cond2 = [clr.matrix(balance=True).fetch(region) for clr in condition2_reps]

log2fc, pvalues = differential_test(rep1_cond1, rep1_cond2)
```

## FDR Correction

```python
from statsmodels.stats.multitest import multipletests

# Flatten p-values, apply FDR
pval_flat = pvalues.flatten()
valid_mask = ~np.isnan(pval_flat)
pval_valid = pval_flat[valid_mask]

_, pval_adj, _, _ = multipletests(pval_valid, method='fdr_bh')

# Reshape back
pval_adj_full = np.full_like(pval_flat, np.nan)
pval_adj_full[valid_mask] = pval_adj
pvalues_adj = pval_adj_full.reshape(pvalues.shape)

# Significant differential contacts
sig_mask = (pvalues_adj < 0.05) & (np.abs(log2fc) > 1)
print(f'Significant differential contacts: {sig_mask.sum()}')
```

## Differential at Distance Bins

```python
def differential_by_distance(log2fc_matrix, max_dist=100):
    '''Summarize differential contacts by genomic distance'''
    n = log2fc_matrix.shape[0]
    results = []

    for d in range(max_dist):
        diag = np.diag(log2fc_matrix, d)
        valid = diag[~np.isnan(diag)]
        if len(valid) > 0:
            results.append({
                'distance': d,
                'mean_log2fc': np.mean(valid),
                'std_log2fc': np.std(valid),
                'n_contacts': len(valid),
            })

    return pd.DataFrame(results)

dist_df = differential_by_distance(log2fc)
plt.figure(figsize=(10, 4))
plt.errorbar(dist_df['distance'], dist_df['mean_log2fc'],
             yerr=dist_df['std_log2fc']/np.sqrt(dist_df['n_contacts']),
             alpha=0.5)
plt.axhline(0, color='black', linestyle='--')
plt.xlabel('Distance (bins)')
plt.ylabel('Mean log2 fold change')
plt.title('Differential contacts by distance')
plt.savefig('differential_by_distance.png', dpi=150)
```

## Compare Compartment Changes

```python
# Load compartment eigenvectors
view_df = bioframe.make_viewframe(clr1.chromsizes)

_, eig1 = cooltools.eigs_cis(clr1, view_df=view_df, n_eigs=1)
_, eig2 = cooltools.eigs_cis(clr2, view_df=view_df, n_eigs=1)

# Merge and find switches
merged = eig1.merge(eig2, on=['chrom', 'start', 'end'], suffixes=('_1', '_2'))
merged['E1_diff'] = merged['E1_2'] - merged['E1_1']
merged['compartment_1'] = np.where(merged['E1_1'] > 0, 'A', 'B')
merged['compartment_2'] = np.where(merged['E1_2'] > 0, 'A', 'B')
merged['switched'] = merged['compartment_1'] != merged['compartment_2']

print(f"Compartment switches: {merged['switched'].sum()}")
print(merged[merged['switched']][['chrom', 'start', 'end', 'E1_1', 'E1_2']].head(10))
```

## Compare TAD Boundaries

```python
# Compute insulation for both
ins1 = cooltools.insulation(clr1, window_bp=[200000], ignore_diags=2)
ins2 = cooltools.insulation(clr2, window_bp=[200000], ignore_diags=2)

# Get boundaries
bounds1 = set(ins1[ins1['is_boundary_200000']]['start'])
bounds2 = set(ins2[ins2['is_boundary_200000']]['start'])

shared = bounds1 & bounds2
only_cond1 = bounds1 - bounds2
only_cond2 = bounds2 - bounds1

print(f'Shared boundaries: {len(shared)}')
print(f'Condition 1 specific: {len(only_cond1)}')
print(f'Condition 2 specific: {len(only_cond2)}')
```

## Differential Loop Analysis

```python
# Call loops in both conditions
dots1 = cooltools.dots(clr1, expected=expected1, view_df=view_df, max_loci_separation=2000000)
dots2 = cooltools.dots(clr2, expected=expected2, view_df=view_df, max_loci_separation=2000000)

def loops_overlap(l1, l2, tolerance=20000):
    return (l1['chrom1'] == l2['chrom1'] and
            abs(l1['start1'] - l2['start1']) < tolerance and
            abs(l1['start2'] - l2['start2']) < tolerance)

# Find differential loops
shared_loops = []
cond1_specific = []
for _, l1 in dots1.iterrows():
    found = False
    for _, l2 in dots2.iterrows():
        if loops_overlap(l1, l2):
            shared_loops.append(l1)
            found = True
            break
    if not found:
        cond1_specific.append(l1)

print(f'Shared loops: {len(shared_loops)}')
print(f'Condition 1 specific: {len(cond1_specific)}')
```

## Export Differential Results

```python
# Save log2FC matrix
np.save('log2fc_matrix.npy', log2fc)

# Save significant differential contacts as BED-like
sig_contacts = []
for i in range(log2fc.shape[0]):
    for j in range(i, log2fc.shape[1]):
        if sig_mask[i, j]:
            sig_contacts.append({
                'bin1': i,
                'bin2': j,
                'log2fc': log2fc[i, j],
                'pvalue': pvalues_adj[i, j],
            })

pd.DataFrame(sig_contacts).to_csv('differential_contacts.csv', index=False)

# Save compartment switches
merged[merged['switched']].to_csv('compartment_switches.csv', index=False)
```

## Related Skills

- hic-data-io - Load Hi-C matrices
- matrix-operations - Normalize matrices
- compartment-analysis - Call compartments
- tad-detection - Call TADs for comparison
- loop-calling - Call loops for comparison
