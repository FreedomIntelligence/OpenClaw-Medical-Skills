# bio-spatial-transcriptomics-spatial-deconvolution

> Estimate cell type composition in spatial transcriptomics spots using reference-based deconvolution. Use cell2location, RCTD, SPOTlight, or Tangram to infer cell type proportions from scRNA-seq references. Use when estimating cell type composition in spatial spots.

## Version Compatibility

Reference examples tested with: anndata 0.10+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Deconvolution

Estimate cell type composition in spatial spots using scRNA-seq references.

## Required Imports

```python
import scanpy as sc
import anndata as ad
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

## Overview

Deconvolution estimates cell type proportions in each spatial spot using a reference single-cell dataset. Essential for Visium data where spots contain multiple cells.

## Using cell2location

**Goal:** Estimate cell type abundances per spatial spot using a probabilistic model trained on scRNA-seq reference signatures.

**Approach:** Train a regression model on reference scRNA-seq to extract cell type signatures, then decompose spatial spots using those signatures.

**"Deconvolve my Visium spots into cell types"** -> Train a reference signature model on scRNA-seq, then map cell type abundances to spatial locations using cell2location.

```python
import cell2location
from cell2location.utils.filtering import filter_genes
from cell2location.models import RegressionModel

# Load reference scRNA-seq
adata_ref = sc.read_h5ad('reference_scrna.h5ad')
adata_ref.obs['cell_type'] = adata_ref.obs['cell_type'].astype('category')

# Load spatial data
adata_vis = sc.read_h5ad('spatial_data.h5ad')

# Find shared genes
intersect = np.intersect1d(adata_vis.var_names, adata_ref.var_names)
adata_ref = adata_ref[:, intersect].copy()
adata_vis = adata_vis[:, intersect].copy()
```

## Train Reference Signature Model

**Goal:** Learn cell type gene expression signatures from annotated single-cell reference data.

**Approach:** Filter genes, set up a regression model on the scRNA-seq reference, train it, and export per-cell-type mean expression signatures.

```python
# Select genes for deconvolution
selected = filter_genes(adata_ref, cell_count_cutoff=5, cell_percentage_cutoff2=0.03,
                        nonz_mean_cutoff=1.12)
adata_ref = adata_ref[:, selected].copy()

# Prepare reference
cell2location.models.RegressionModel.setup_anndata(
    adata_ref,
    labels_key='cell_type',
)

# Train reference model
mod = RegressionModel(adata_ref)
mod.train(max_epochs=250, use_gpu=True)

# Export reference signatures
adata_ref = mod.export_posterior(adata_ref, sample_kwargs={'num_samples': 1000})
ref_sig = adata_ref.varm['means_per_cluster_mu_fg']
```

## Run Spatial Deconvolution

**Goal:** Decompose each spatial spot into cell type abundances using trained reference signatures.

**Approach:** Set up the Cell2location model with reference signatures and expected cells per spot, then train on the spatial data.

```python
# Ensure spatial data has same genes
adata_vis = adata_vis[:, adata_ref.var_names].copy()

# Setup spatial data
cell2location.models.Cell2location.setup_anndata(adata_vis)

# Train deconvolution model
mod_spatial = cell2location.models.Cell2location(
    adata_vis,
    cell_state_df=ref_sig,
    N_cells_per_location=10,  # Expected cells per spot
    detection_alpha=20,
)
mod_spatial.train(max_epochs=30000, use_gpu=True)

# Export results
adata_vis = mod_spatial.export_posterior(adata_vis, sample_kwargs={'num_samples': 1000})
```

## Access Deconvolution Results

```python
# Cell type abundances stored in obsm
abundances = adata_vis.obsm['q05_cell_abundance_w_sf']
print(f'Cell types: {abundances.shape[1]}')

# Convert to proportions
proportions = abundances / abundances.sum(axis=1, keepdims=True)
adata_vis.obsm['cell_type_proportions'] = proportions

# Add dominant cell type
cell_types = adata_ref.obs['cell_type'].cat.categories
adata_vis.obs['dominant_cell_type'] = cell_types[proportions.argmax(axis=1)]
```

## Using Tangram (Alternative)

**Goal:** Map single-cell reference data to spatial locations using optimal transport.

**Approach:** Find marker genes from the reference, align single cells to spatial spots using Tangram's mapping algorithm, then project cell type annotations.

```python
import tangram as tg

# Load data
adata_sc = sc.read_h5ad('reference_scrna.h5ad')
adata_sp = sc.read_h5ad('spatial_data.h5ad')

# Preprocess
sc.pp.normalize_total(adata_sc)
sc.pp.log1p(adata_sc)

# Find marker genes
sc.tl.rank_genes_groups(adata_sc, groupby='cell_type', method='wilcoxon')
markers = sc.get.rank_genes_groups_df(adata_sc, group=None)
markers = markers[markers['pvals_adj'] < 0.01].groupby('group').head(100)
marker_genes = markers['names'].unique().tolist()

# Prepare for Tangram
tg.pp_adatas(adata_sc, adata_sp, genes=marker_genes)

# Map single cells to spatial locations
ad_map = tg.map_cells_to_space(
    adata_sc,
    adata_sp,
    mode='clusters',
    cluster_label='cell_type',
    device='cuda:0',
)

# Get cell type proportions
tg.project_cell_annotations(ad_map, adata_sp, annotation='cell_type')
# Results in adata_sp.obsm['tangram_ct_pred']
```

## Using RCTD (via R)

```python
# RCTD runs in R; use rpy2 for integration
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
pandas2ri.activate()

# Save data for R
adata_vis.write_h5ad('spatial_for_rctd.h5ad')
adata_ref.write_h5ad('reference_for_rctd.h5ad')

# R code for RCTD
r_code = '''
library(spacexr)
library(Seurat)

# Load data (convert from h5ad first)
# ... R-specific loading code ...

# Create RCTD object
rctd <- create.RCTD(puck, reference, max_cores=4)
rctd <- run_RCTD(rctd, doublet_mode='full')

# Get results
results <- rctd@results
weights <- normalize_weights(results$weights)
'''
```

## Visualize Cell Type Proportions

**Goal:** Display estimated cell type abundances as spatial heatmaps across the tissue.

**Approach:** Plot each cell type's proportion as a separate spatial panel using Scanpy's spatial plot.

```python
# Plot cell type abundances spatially
cell_types_to_plot = ['T_cell', 'Macrophage', 'Epithelial', 'Fibroblast']

fig, axes = plt.subplots(2, 2, figsize=(12, 12))
for ax, ct in zip(axes.flatten(), cell_types_to_plot):
    ct_idx = list(adata_ref.obs['cell_type'].cat.categories).index(ct)
    adata_vis.obs[f'{ct}_proportion'] = proportions[:, ct_idx]
    sc.pl.spatial(adata_vis, color=f'{ct}_proportion', ax=ax, show=False,
                  title=ct, cmap='Reds', vmin=0, vmax=1)
plt.tight_layout()
plt.savefig('cell_type_proportions.png', dpi=150)
```

## Pie Chart Per Spot (Advanced)

```python
from matplotlib.patches import Wedge

def plot_pie_spatial(adata, proportions, cell_types, spot_size=0.5):
    fig, ax = plt.subplots(figsize=(12, 12))
    colors = plt.cm.tab20(np.linspace(0, 1, len(cell_types)))

    coords = adata.obsm['spatial']
    for i in range(adata.n_obs):
        x, y = coords[i]
        props = proportions[i]
        start_angle = 0
        for j, prop in enumerate(props):
            if prop > 0.01:  # Skip tiny proportions
                wedge = Wedge((x, y), spot_size * 50, start_angle,
                             start_angle + prop * 360, color=colors[j])
                ax.add_patch(wedge)
                start_angle += prop * 360

    ax.set_xlim(coords[:, 0].min() - 100, coords[:, 0].max() + 100)
    ax.set_ylim(coords[:, 1].min() - 100, coords[:, 1].max() + 100)
    ax.set_aspect('equal')
    ax.invert_yaxis()

    # Legend
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[i]) for i in range(len(cell_types))]
    ax.legend(handles, cell_types, loc='upper right')
    plt.savefig('pie_chart_spatial.png', dpi=150)
```

## Evaluate Deconvolution Quality

**Goal:** Validate deconvolution results by correlating estimated proportions with known marker gene expression.

**Approach:** For each cell type, compute correlation between its estimated proportion and mean expression of canonical marker genes.

```python
# Check correlation between expected and observed cell counts
# (if you have known cell type markers)

marker_genes = {
    'T_cell': ['CD3D', 'CD3E', 'CD4', 'CD8A'],
    'Macrophage': ['CD68', 'CD14', 'CSF1R'],
    'Epithelial': ['EPCAM', 'KRT8', 'KRT18'],
}

for ct, markers in marker_genes.items():
    available_markers = [m for m in markers if m in adata_vis.var_names]
    if available_markers:
        marker_expr = adata_vis[:, available_markers].X.mean(axis=1)
        ct_idx = list(cell_types).index(ct)
        ct_prop = proportions[:, ct_idx]
        corr = np.corrcoef(marker_expr.flatten(), ct_prop)[0, 1]
        print(f'{ct}: marker-proportion correlation = {corr:.3f}')
```

## Compare Deconvolution Methods

```python
# Store results from different methods
adata_vis.obsm['cell2location'] = cell2location_proportions
adata_vis.obsm['tangram'] = tangram_proportions

# Correlation between methods
for ct_idx, ct in enumerate(cell_types):
    c2l = adata_vis.obsm['cell2location'][:, ct_idx]
    tg = adata_vis.obsm['tangram'][:, ct_idx]
    corr = np.corrcoef(c2l, tg)[0, 1]
    print(f'{ct}: cell2location vs tangram = {corr:.3f}')
```

## Export Results

```python
# Save proportions as CSV
prop_df = pd.DataFrame(
    proportions,
    index=adata_vis.obs_names,
    columns=cell_types
)
prop_df.to_csv('cell_type_proportions.csv')

# Save annotated AnnData
adata_vis.write_h5ad('spatial_deconvolved.h5ad')
```

## Related Skills

- spatial-data-io - Load spatial data
- single-cell/data-io - Load scRNA-seq reference
- spatial-visualization - Visualize deconvolution results
- single-cell/markers-annotation - Annotate reference cell types
