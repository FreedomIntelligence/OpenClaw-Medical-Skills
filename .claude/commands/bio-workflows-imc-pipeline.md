# bio-workflows-imc-pipeline

> End-to-end imaging mass cytometry workflow from raw acquisitions to spatial cell analysis. Orchestrates image preprocessing, segmentation, phenotyping, and spatial statistics. Use when analyzing imaging mass cytometry data end-to-end.

**Available tools:** Read, Bash

# Imaging Mass Cytometry Pipeline

## Pipeline Overview

```
Raw MCD/TIFF Files ──> Image Processing ──> Cell Masks
                                                 │
                                                 ▼
                ┌─────────────────────────────────────────────┐
                │              imc-pipeline                   │
                ├─────────────────────────────────────────────┤
                │  1. Data Preprocessing (spillover, hot px)  │
                │  2. Cell Segmentation (Cellpose/Mesmer)     │
                │  3. Single-cell Quantification              │
                │  4. Clustering & Phenotyping                │
                │  5. Spatial Analysis                        │
                │  6. Visualization                           │
                └─────────────────────────────────────────────┘
                                                 │
                                                 ▼
                    Cell Types + Spatial Neighborhoods
```

## Complete steinbock Workflow

### Step 1: Setup and Preprocessing

```bash
# Initialize steinbock project
steinbock preprocess imc \
    --mcd data/*.mcd \
    --panel panel.csv \
    --output raw/

# Hot pixel filtering
steinbock preprocess imc hotpixel \
    --input raw/ \
    --output img/ \
    --threshold 50

# Create nuclear and membrane channels
steinbock preprocess mosaic \
    --input img/ \
    --channels panel.csv \
    --output mosaics/
```

### Step 2: Cell Segmentation

```bash
# Using Cellpose
steinbock segment cellpose \
    --input img/ \
    --panel panel.csv \
    --channel DNA1 DNA2 \
    --output masks/ \
    --diameter 20

# Alternative: Using Mesmer
steinbock segment mesmer \
    --input img/ \
    --panel panel.csv \
    --nuclear DNA1 DNA2 \
    --membrane CD45 \
    --output masks/
```

### Step 3: Single-cell Quantification

```bash
# Extract intensities
steinbock measure intensities \
    --input img/ \
    --masks masks/ \
    --panel panel.csv \
    --output intensities/

# Measure cell properties (area, etc.)
steinbock measure regionprops \
    --masks masks/ \
    --output regionprops/

# Extract neighbor relationships
steinbock measure neighbors \
    --masks masks/ \
    --output neighbors/ \
    --distance 15
```

## Complete Python Workflow

```python
import pandas as pd
import numpy as np
import anndata as ad
import scanpy as sc
import squidpy as sq
from pathlib import Path

# === 1. LOAD DATA ===
data_dir = Path('steinbock_output')

intensities = pd.read_csv(data_dir / 'intensities.csv', index_col=0)
regionprops = pd.read_csv(data_dir / 'regionprops.csv', index_col=0)
neighbors = pd.read_csv(data_dir / 'neighbors.csv')

print(f'Loaded {len(intensities)} cells')

# === 2. CREATE ANNDATA ===
adata = ad.AnnData(X=intensities.values, obs=regionprops, var=pd.DataFrame(index=intensities.columns))
adata.obs['image_id'] = [idx.split('_')[0] for idx in intensities.index]
adata.obs['cell_id'] = intensities.index

# Add spatial coordinates
adata.obsm['spatial'] = regionprops[['centroid_y', 'centroid_x']].values

# === 3. PREPROCESSING ===
# Arcsinh transform (cofactor 5 for IMC)
adata.X = np.arcsinh(adata.X / 5)

# Scale for clustering
sc.pp.scale(adata, max_value=10)
adata.raw = adata.copy()

# === 4. DIMENSIONALITY REDUCTION ===
sc.pp.pca(adata, n_comps=20)
sc.pp.neighbors(adata, n_neighbors=15)
sc.tl.umap(adata)

# === 5. CLUSTERING ===
sc.tl.leiden(adata, resolution=0.8)
print(f'Found {adata.obs["leiden"].nunique()} clusters')

# === 6. PHENOTYPING ===
# Marker expression per cluster
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
marker_genes = sc.get.rank_genes_groups_df(adata, group=None)

# Annotate clusters based on markers
cluster_annotations = {
    '0': 'T cells',
    '1': 'Macrophages',
    '2': 'Tumor',
    '3': 'B cells',
    '4': 'Stromal'
}
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_annotations)

# === 7. SPATIAL ANALYSIS ===
# Build spatial graph
sq.gr.spatial_neighbors(adata, coord_type='generic', delaunay=True)

# Neighborhood enrichment
sq.gr.nhood_enrichment(adata, cluster_key='cell_type')

# Co-occurrence analysis
sq.gr.co_occurrence(adata, cluster_key='cell_type')

# Ripley's statistics
sq.gr.ripley(adata, cluster_key='cell_type', mode='L')

# === 8. VISUALIZATION ===
import matplotlib.pyplot as plt

# UMAP by cell type
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sc.pl.umap(adata, color='cell_type', ax=axes[0], show=False)
sc.pl.umap(adata, color='leiden', ax=axes[1], show=False)
plt.savefig('umap_celltypes.png', dpi=150, bbox_inches='tight')

# Spatial plot
fig, ax = plt.subplots(figsize=(10, 10))
sq.pl.spatial_scatter(adata[adata.obs['image_id'] == 'image1'],
                      color='cell_type', shape=None, size=10, ax=ax)
plt.savefig('spatial_celltypes.png', dpi=150, bbox_inches='tight')

# Neighborhood enrichment heatmap
sq.pl.nhood_enrichment(adata, cluster_key='cell_type')
plt.savefig('neighborhood_enrichment.png', dpi=150, bbox_inches='tight')

# === 9. DIFFERENTIAL ANALYSIS ===
# Compare conditions
adata.obs['condition'] = adata.obs['image_id'].map({
    'image1': 'Control', 'image2': 'Control',
    'image3': 'Treatment', 'image4': 'Treatment'
})

# Cell type proportions
proportions = adata.obs.groupby(['image_id', 'condition', 'cell_type']).size().unstack(fill_value=0)
proportions = proportions.div(proportions.sum(axis=1), axis=0)

# Save results
adata.write('imc_analysis.h5ad')
proportions.to_csv('cell_type_proportions.csv')
print('Analysis complete!')
```

## R Alternative (imcRtools)

```r
library(imcRtools)
library(cytomapper)
library(CATALYST)

# Read steinbock output
spe <- read_steinbock('steinbock_output/')

# Transform
assay(spe, 'exprs') <- asinh(counts(spe) / 5)

# Cluster
spe <- runDR(spe, features = rownames(spe), exprs_values = 'exprs', dr = 'UMAP')
spe <- cluster(spe, features = rownames(spe), exprs_values = 'exprs',
               xdim = 10, ydim = 10, maxK = 20)

# Spatial analysis
spe <- buildSpatialGraph(spe, img_id = 'image_id', type = 'expansion', threshold = 20)
spe <- aggregateNeighbors(spe, colPairName = 'neighborhood', by = 'cluster_id')

# Spatial context
cn <- detectCommunity(spe, colPairName = 'neighborhood',
                       size_threshold = 10, group_by = 'image_id')

# Plot
plotSpatial(spe, img_id = 'image1', node_color_by = 'cluster_id')
```

## QC Checkpoints

| Stage | Check | Action if Failed |
|-------|-------|------------------|
| Preprocessing | No hot pixel streaks | Lower threshold |
| Segmentation | >80% cells detected | Adjust diameter |
| Quantification | All markers extracted | Check panel.csv |
| Clustering | 5-20 clusters | Adjust resolution |
| Spatial | Neighbors detected | Check distance |

## Workflow Variants

### High-plex Panels (40+ markers)
```python
# Use batch-aware clustering
import scvi

scvi.model.SCVI.setup_anndata(adata, batch_key='image_id')
model = scvi.model.SCVI(adata)
model.train()
adata.obsm['X_scvi'] = model.get_latent_representation()
sc.pp.neighbors(adata, use_rep='X_scvi')
```

### Tumor Microenvironment Analysis
```python
# Spatial interactions with tumor
tumor_cells = adata[adata.obs['cell_type'] == 'Tumor'].obs_names
sq.gr.ligrec(adata, cluster_key='cell_type', source_groups=['Tumor'],
             target_groups=['T cells', 'Macrophages'])
```

## Related Skills

- imaging-mass-cytometry/data-preprocessing - Hot pixel, spillover
- imaging-mass-cytometry/cell-segmentation - Cellpose/Mesmer details
- imaging-mass-cytometry/phenotyping - Cluster annotation
- imaging-mass-cytometry/spatial-analysis - Spatial statistics
- imaging-mass-cytometry/interactive-annotation - Manual cell labeling
- imaging-mass-cytometry/quality-metrics - QC metrics
- single-cell/clustering - Clustering methods
- spatial-transcriptomics/spatial-statistics - Related spatial methods
