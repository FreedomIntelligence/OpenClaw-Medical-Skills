# bio-spatial-transcriptomics-spatial-visualization

> Visualize spatial transcriptomics data using Squidpy and Scanpy. Create tissue plots with gene expression, clusters, and annotations overlaid on histology images. Use when visualizing spatial expression patterns.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, scanpy 1.10+, squidpy 1.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Visualization

**"Plot gene expression on my tissue section"** → Overlay gene expression, cluster assignments, or continuous scores on spatial coordinates with optional histology image background.
- Python: `squidpy.pl.spatial_scatter(adata, color='gene')`, `scanpy.pl.spatial(adata, color='leiden')`

Create visualizations for spatial transcriptomics data.

## Required Imports

```python
import squidpy as sq
import scanpy as sc
import matplotlib.pyplot as plt
```

## Basic Spatial Plot

**Goal:** Create a spatial scatter plot with spots colored by a variable of interest.

**Approach:** Use Squidpy's `spatial_scatter` to overlay expression or metadata values on tissue coordinates.

```python
# Plot spots colored by a variable
sq.pl.spatial_scatter(adata, color='total_counts', size=1.3)

# Multiple variables
sq.pl.spatial_scatter(adata, color=['total_counts', 'n_genes_by_counts'], ncols=2)
```

## Plot with Scanpy

```python
# Scanpy's spatial plot
sc.pl.spatial(adata, color='leiden', spot_size=1.5)

# Multiple genes
sc.pl.spatial(adata, color=['GENE1', 'GENE2', 'GENE3'], ncols=3)
```

## Show Tissue Image

```python
# Plot with tissue background
sc.pl.spatial(adata, color='leiden', img_key='hires', alpha_img=0.5)

# Without tissue
sc.pl.spatial(adata, color='leiden', img_key=None)
```

## Customize Appearance

```python
# Adjust spot size and colors
sc.pl.spatial(
    adata,
    color='leiden',
    spot_size=1.5,
    palette='tab20',
    title='Cluster assignments',
    frameon=False,
)
```

## Gene Expression on Tissue

**Goal:** Visualize gene expression patterns overlaid on tissue spatial coordinates.

**Approach:** Plot individual or multiple genes using Scanpy's spatial plot with configurable colormaps and value ranges.

```python
# Single gene
sc.pl.spatial(adata, color='CD3D', cmap='viridis', vmin=0, vmax='p99')

# Multiple genes side by side
genes = ['CD3D', 'MS4A1', 'CD14', 'NKG7']
sc.pl.spatial(adata, color=genes, ncols=2, cmap='Reds', vmin=0)
```

## Expression with Colorbar Control

```python
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, gene in zip(axes, ['GENE1', 'GENE2']):
    sc.pl.spatial(adata, color=gene, ax=ax, show=False, vmin=0, vmax=5, cmap='viridis')
    ax.set_title(gene)

plt.tight_layout()
plt.savefig('gene_expression.png', dpi=300)
```

## Compare Conditions/Samples

```python
# Split by sample
sc.pl.spatial(adata, color='leiden', groups=['sample1', 'sample2'], ncols=2)

# Or manually
samples = adata.obs['sample'].unique()
fig, axes = plt.subplots(1, len(samples), figsize=(5*len(samples), 5))

for ax, sample in zip(axes, samples):
    adata_sub = adata[adata.obs['sample'] == sample]
    sc.pl.spatial(adata_sub, color='leiden', ax=ax, show=False, title=sample)

plt.tight_layout()
```

## Overlay Annotations

```python
# Plot with custom annotations
fig, ax = plt.subplots(figsize=(8, 8))
sc.pl.spatial(adata, color='leiden', ax=ax, show=False)

# Add text annotations
for cluster in adata.obs['leiden'].unique():
    mask = adata.obs['leiden'] == cluster
    coords = adata.obsm['spatial'][mask].mean(axis=0)
    ax.annotate(f'C{cluster}', coords, fontsize=12, ha='center')

plt.savefig('annotated.png', dpi=300)
```

## Co-expression Plot

**Goal:** Visualize co-localization of two genes using dual-channel RGB encoding.

**Approach:** Normalize expression of each gene to [0,1], assign to red and green channels, and render as a scatter plot.

```python
# Visualize co-expression of two genes
import numpy as np

gene1, gene2 = 'CD3D', 'CD8A'
expr1 = adata[:, gene1].X.toarray().flatten()
expr2 = adata[:, gene2].X.toarray().flatten()

# Create RGB image (red=gene1, green=gene2)
from matplotlib.colors import Normalize
norm = Normalize(vmin=0, vmax=np.percentile(np.concatenate([expr1, expr2]), 99))
colors = np.zeros((adata.n_obs, 3))
colors[:, 0] = norm(expr1)  # Red channel
colors[:, 1] = norm(expr2)  # Green channel

fig, ax = plt.subplots(figsize=(8, 8))
coords = adata.obsm['spatial']
ax.scatter(coords[:, 0], coords[:, 1], c=colors, s=10)
ax.set_aspect('equal')
ax.set_title(f'{gene1} (red) + {gene2} (green)')
plt.savefig('coexpression.png', dpi=300)
```

## Visualize Spatial Statistics

```python
# Plot Moran's I results
sq.pl.spatial_scatter(adata, color='GENE1', size=1.3)

# Plot neighborhood enrichment
sq.pl.nhood_enrichment(adata, cluster_key='leiden')

# Plot co-occurrence
sq.pl.co_occurrence(adata, cluster_key='leiden')
```

## Interactive Visualization with Napari

**Goal:** Explore spatial data interactively with zoomable tissue images and spot overlays.

**Approach:** Load tissue images and spot coordinates into napari layers for pan-and-zoom exploration.

```python
import napari

# Create viewer
viewer = napari.Viewer()

# Add tissue image
library_id = list(adata.uns['spatial'].keys())[0]
img = adata.uns['spatial'][library_id]['images']['hires']
viewer.add_image(img, name='tissue')

# Add spots
coords = adata.obsm['spatial']
scalef = adata.uns['spatial'][library_id]['scalefactors']['tissue_hires_scalef']
viewer.add_points(coords * scalef, size=10, name='spots')

napari.run()
```

## Save Publication-Quality Figures

**Goal:** Export high-resolution spatial plots suitable for publication.

**Approach:** Configure frameless spatial plots with appropriate DPI and save as both PDF and PNG.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 8))
sc.pl.spatial(
    adata,
    color='leiden',
    ax=ax,
    show=False,
    frameon=False,
    title='',
    legend_loc='right margin',
)
plt.savefig('figure.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figure.png', dpi=300, bbox_inches='tight')
```

## Multi-Panel Figure

**Goal:** Assemble a composite figure combining spatial plots, gene expression, UMAP, and violin plots.

**Approach:** Create a 2x3 subplot grid with different visualization types for comprehensive data overview.

```python
fig = plt.figure(figsize=(15, 10))

# Tissue with clusters
ax1 = fig.add_subplot(2, 3, 1)
sc.pl.spatial(adata, color='leiden', ax=ax1, show=False, title='Clusters')

# Gene 1
ax2 = fig.add_subplot(2, 3, 2)
sc.pl.spatial(adata, color='CD3D', ax=ax2, show=False, title='CD3D', cmap='Reds')

# Gene 2
ax3 = fig.add_subplot(2, 3, 3)
sc.pl.spatial(adata, color='MS4A1', ax=ax3, show=False, title='MS4A1', cmap='Blues')

# QC metrics
ax4 = fig.add_subplot(2, 3, 4)
sc.pl.spatial(adata, color='total_counts', ax=ax4, show=False, title='Total counts')

# UMAP
ax5 = fig.add_subplot(2, 3, 5)
sc.pl.umap(adata, color='leiden', ax=ax5, show=False, title='UMAP')

# Violin plot
ax6 = fig.add_subplot(2, 3, 6)
sc.pl.violin(adata, ['CD3D', 'MS4A1'], groupby='leiden', ax=ax6, show=False)

plt.tight_layout()
plt.savefig('multi_panel.png', dpi=300)
```

## Crop and Zoom

```python
# Zoom into a region
x_min, x_max = 2000, 4000
y_min, y_max = 2000, 4000

fig, ax = plt.subplots(figsize=(8, 8))
sc.pl.spatial(adata, color='leiden', ax=ax, show=False)
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_max, y_min)  # Note: y is inverted in images
plt.savefig('zoomed.png', dpi=300)
```

## Related Skills

- spatial-data-io - Load spatial data
- spatial-statistics - Compute statistics to visualize
- single-cell/clustering - Generate cluster labels
