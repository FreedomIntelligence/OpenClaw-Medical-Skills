# bio-hi-c-analysis-hic-visualization

> Visualize Hi-C contact matrices, TADs, loops, and genomic features using matplotlib, cooltools, and HiCExplorer. Create triangle plots, virtual 4C, and multi-track figures. Use when visualizing contact matrices or genomic features.

## Version Compatibility

Reference examples tested with: cooler 0.9+, cooltools 0.6+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Hi-C Visualization

**"Plot my Hi-C contact matrix"** → Create triangle heatmaps, virtual 4C profiles, and multi-track figures combining contact maps with genomic annotations.
- Python: `matplotlib.pyplot.imshow()` on cooler matrices, `cooltools` for aggregate plots
- CLI: `hicPlotMatrix` (HiCExplorer)

Visualize Hi-C contact matrices and genomic features.

## Required Imports

```python
import cooler
import cooltools
import cooltools.lib.plotting
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import bioframe
```

## Basic Contact Matrix Plot

```python
clr = cooler.Cooler('matrix.mcool::resolutions/10000')

# Get matrix for a region
matrix = clr.matrix(balance=True).fetch('chr1:50000000-60000000')

fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(matrix, cmap='Reds', norm=LogNorm(vmin=0.001, vmax=0.1))
plt.colorbar(im, ax=ax, label='Balanced contacts')
ax.set_title('chr1:50-60Mb')
plt.savefig('contact_matrix.png', dpi=150)
```

## Triangle (Upper Triangle) Plot

```python
def plot_triangle(matrix, ax, cmap='Reds', vmin=None, vmax=None):
    '''Plot Hi-C matrix as triangle (rotated 45 degrees)'''
    n = matrix.shape[0]

    # Create rotated matrix
    rotated = np.zeros((n, 2*n))
    for i in range(n):
        for j in range(i, n):
            y = j - i
            x = i + j
            rotated[y, x] = matrix[i, j]

    # Plot
    im = ax.imshow(rotated[:n//2, :], cmap=cmap, aspect='auto',
                   norm=LogNorm(vmin=vmin, vmax=vmax) if vmin else None)
    ax.set_ylim(n//2, 0)
    return im

matrix = clr.matrix(balance=True).fetch('chr1:50000000-60000000')
fig, ax = plt.subplots(figsize=(12, 4))
im = plot_triangle(matrix, ax, vmin=0.001, vmax=0.1)
plt.colorbar(im, ax=ax)
plt.savefig('triangle_plot.png', dpi=150)
```

## Plot with TADs

```python
import pandas as pd

matrix = clr.matrix(balance=True).fetch('chr1:50000000-60000000')
tads = pd.read_csv('tads.bed', sep='\t', names=['chrom', 'start', 'end'])

fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(matrix, cmap='Reds', norm=LogNorm(vmin=0.001, vmax=0.1))

# Overlay TAD boundaries
region_start = 50000000
bin_size = clr.binsize
for _, tad in tads[tads['chrom'] == 'chr1'].iterrows():
    if region_start <= tad['start'] < 60000000:
        pos = (tad['start'] - region_start) / bin_size
        ax.axhline(pos, color='blue', linewidth=0.5, alpha=0.5)
        ax.axvline(pos, color='blue', linewidth=0.5, alpha=0.5)

plt.colorbar(im, ax=ax)
plt.savefig('matrix_with_tads.png', dpi=150)
```

## Plot with Loops

```python
matrix = clr.matrix(balance=True).fetch('chr1:50000000-60000000')
loops = pd.read_csv('loops.bedpe', sep='\t')

fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(matrix, cmap='Reds', norm=LogNorm(vmin=0.001, vmax=0.1))

# Mark loops
region_start = 50000000
bin_size = clr.binsize
for _, loop in loops[loops['chrom1'] == 'chr1'].iterrows():
    if (region_start <= loop['start1'] < 60000000 and
        region_start <= loop['start2'] < 60000000):
        x = (loop['start1'] - region_start) / bin_size
        y = (loop['start2'] - region_start) / bin_size
        circle = plt.Circle((y, x), 3, fill=False, color='blue', linewidth=1)
        ax.add_patch(circle)

plt.colorbar(im, ax=ax)
plt.savefig('matrix_with_loops.png', dpi=150)
```

## Compare Two Matrices

```python
clr1 = cooler.Cooler('sample1.mcool::resolutions/10000')
clr2 = cooler.Cooler('sample2.mcool::resolutions/10000')

region = 'chr1:50000000-60000000'
mat1 = clr1.matrix(balance=True).fetch(region)
mat2 = clr2.matrix(balance=True).fetch(region)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Sample 1
im1 = axes[0].imshow(mat1, cmap='Reds', norm=LogNorm(vmin=0.001, vmax=0.1))
axes[0].set_title('Sample 1')
plt.colorbar(im1, ax=axes[0])

# Sample 2
im2 = axes[1].imshow(mat2, cmap='Reds', norm=LogNorm(vmin=0.001, vmax=0.1))
axes[1].set_title('Sample 2')
plt.colorbar(im2, ax=axes[1])

# Log2 fold change
log2fc = np.log2(mat2 / mat1)
log2fc[np.isinf(log2fc)] = np.nan
im3 = axes[2].imshow(log2fc, cmap='coolwarm', vmin=-2, vmax=2)
axes[2].set_title('Log2(Sample2/Sample1)')
plt.colorbar(im3, ax=axes[2])

plt.tight_layout()
plt.savefig('comparison.png', dpi=150)
```

## Split View (Upper/Lower Triangle)

```python
mat1 = clr1.matrix(balance=True).fetch(region)
mat2 = clr2.matrix(balance=True).fetch(region)

# Combine: upper triangle from mat1, lower from mat2
combined = np.triu(mat1) + np.tril(mat2, k=-1)

fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(combined, cmap='Reds', norm=LogNorm(vmin=0.001, vmax=0.1))
ax.axline((0, 0), slope=1, color='black', linewidth=0.5)
ax.set_title('Sample1 (upper) vs Sample2 (lower)')
plt.colorbar(im, ax=ax)
plt.savefig('split_view.png', dpi=150)
```

## Virtual 4C

**Goal:** Extract a one-dimensional contact frequency profile from a single viewpoint locus, simulating a 4C experiment from Hi-C data.

**Approach:** Select the matrix row corresponding to the viewpoint bin, extract balanced contact values across the chromosome, and plot as a filled line graph.

```python
def virtual_4c(clr, viewpoint_chrom, viewpoint_pos, resolution=10000):
    '''Extract virtual 4C from Hi-C'''
    # Get row of matrix at viewpoint
    viewpoint_bin = viewpoint_pos // resolution

    # Get contacts from this bin to all others on same chromosome
    matrix = clr.matrix(balance=True).fetch(viewpoint_chrom)
    v4c = matrix[viewpoint_bin, :]

    # Create coordinates
    bins = clr.bins().fetch(viewpoint_chrom)
    coords = bins['start'].values

    return coords, v4c

coords, v4c = virtual_4c(clr, 'chr1', 55000000)

fig, ax = plt.subplots(figsize=(12, 3))
ax.fill_between(coords / 1e6, 0, v4c, alpha=0.5)
ax.axvline(55, color='red', linestyle='--', label='Viewpoint')
ax.set_xlabel('Position (Mb)')
ax.set_ylabel('Contact frequency')
ax.set_title('Virtual 4C from chr1:55Mb')
ax.legend()
plt.savefig('virtual_4c.png', dpi=150)
```

## Multi-Track Figure

```python
fig = plt.figure(figsize=(12, 10))

# Hi-C matrix (triangle)
ax1 = fig.add_axes([0.1, 0.5, 0.8, 0.4])
matrix = clr.matrix(balance=True).fetch('chr1:50000000-60000000')
plot_triangle(matrix, ax1, vmin=0.001, vmax=0.1)
ax1.set_ylabel('Hi-C')

# Insulation score
ax2 = fig.add_axes([0.1, 0.35, 0.8, 0.1])
insulation = pd.read_csv('insulation.bedgraph', sep='\t',
                         names=['chrom', 'start', 'end', 'score'])
ins_region = insulation[(insulation['chrom'] == 'chr1') &
                        (insulation['start'] >= 50000000) &
                        (insulation['end'] <= 60000000)]
ax2.plot(ins_region['start'] / 1e6, ins_region['score'])
ax2.set_ylabel('Insulation')
ax2.set_xlim(50, 60)

# Gene track (placeholder)
ax3 = fig.add_axes([0.1, 0.2, 0.8, 0.1])
ax3.set_ylabel('Genes')
ax3.set_xlim(50, 60)

# CTCF ChIP-seq (placeholder)
ax4 = fig.add_axes([0.1, 0.05, 0.8, 0.1])
ax4.set_xlabel('Position (Mb)')
ax4.set_ylabel('CTCF')
ax4.set_xlim(50, 60)

plt.savefig('multi_track.png', dpi=150)
```

## Using HiCExplorer Visualization

```bash
# Plot matrix with HiCExplorer
hicPlotMatrix \
    -m matrix.cool \
    --region chr1:50000000-60000000 \
    --log1p \
    --colorMap Reds \
    -o hic_plot.png

# Plot with TADs
hicPlotTADs \
    --tracks tracks.ini \
    --region chr1:50000000-60000000 \
    -o tad_plot.png
```

## Cooltools Pileup Plot

```python
import cooltools

# Pileup at features (e.g., loop anchors)
pileup = cooltools.pileup(
    clr,
    features=loops[['chrom1', 'start1', 'end1', 'chrom2', 'start2', 'end2']],
    view_df=view_df,
    expected=expected,
    flank=100000,
)

# Average pileup
avg_pileup = np.nanmean(pileup, axis=2)

fig, ax = plt.subplots(figsize=(6, 6))
im = ax.imshow(avg_pileup, cmap='Reds')
ax.set_title('Average pileup at loops')
plt.colorbar(im, ax=ax)
plt.savefig('pileup.png', dpi=150)
```

## Related Skills

- hic-data-io - Load contact matrices
- tad-detection - Generate TADs to visualize
- loop-calling - Generate loops to visualize
- compartment-analysis - Visualize compartments
