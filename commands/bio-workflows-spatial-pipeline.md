# bio-workflows-spatial-pipeline

> End-to-end spatial transcriptomics workflow for Visium/Xenium data. Covers data loading, preprocessing, spatial analysis, domain detection, and visualization with Squidpy. Use when analyzing spatial transcriptomics data.

**Available tools:** Read, Bash

# Spatial Transcriptomics Pipeline

Complete workflow for analyzing Visium, Xenium, or other spatial transcriptomics data.

## Workflow Overview

```
Spatial data (Space Ranger output)
    |
    v
[1. Load Data] ---------> Read Visium/Xenium
    |
    v
[2. QC & Preprocessing] -> Filter, normalize
    |
    v
[3. Clustering] --------> Standard scRNA-seq clustering
    |
    v
[4. Spatial Analysis] --> Neighbors, statistics
    |
    v
[5. Domain Detection] --> Spatial domains
    |
    v
[6. Visualization] -----> Spatial plots
    |
    v
Annotated spatial data
```

## Primary Path: Squidpy + Scanpy

### Step 1: Load Data

```python
import scanpy as sc
import squidpy as sq
import numpy as np
import matplotlib.pyplot as plt

# Load Visium data (Space Ranger output)
adata = sq.read.visium('spaceranger_output/')

# Or load from specific files
adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
adata.uns['spatial'] = ...  # Add spatial info

# For Xenium
adata = sq.read.xenium('xenium_output/')

print(f'Loaded: {adata.n_obs} spots/cells, {adata.n_vars} genes')
```

### Step 2: Quality Control

```python
# QC metrics
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

# Visualize QC
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
sc.pl.spatial(adata, color='total_counts', ax=axes[0], show=False)
sc.pl.spatial(adata, color='n_genes_by_counts', ax=axes[1], show=False)
sc.pl.spatial(adata, color='pct_counts_mt', ax=axes[2], show=False)
plt.savefig('qc_spatial.pdf')

# Filter
sc.pp.filter_cells(adata, min_counts=500)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=10)
adata = adata[adata.obs.pct_counts_mt < 25, :]

print(f'After QC: {adata.n_obs} spots/cells')
```

### Step 3: Normalization and Clustering

```python
# Store raw counts
adata.layers['counts'] = adata.X.copy()

# Normalize
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# HVGs
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# PCA and clustering
adata.raw = adata
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)

# Visualize clusters in space
sc.pl.spatial(adata, color='leiden', spot_size=1.5)
plt.savefig('clusters_spatial.pdf')
```

### Step 4: Spatial Analysis

```python
# Build spatial neighbors graph
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)

# Neighborhood enrichment (which clusters are neighbors)
sq.gr.nhood_enrichment(adata, cluster_key='leiden')
sq.pl.nhood_enrichment(adata, cluster_key='leiden')
plt.savefig('nhood_enrichment.pdf')

# Co-occurrence analysis
sq.gr.co_occurrence(adata, cluster_key='leiden')
sq.pl.co_occurrence(adata, cluster_key='leiden')
plt.savefig('co_occurrence.pdf')

# Spatially variable genes
sq.gr.spatial_autocorr(adata, mode='moran', n_perms=100, n_jobs=4)

# Top spatially variable genes
svg = adata.uns['moranI'].sort_values('I', ascending=False)
top_svg = svg.head(20).index.tolist()
print('Top spatially variable genes:', top_svg[:10])
```

### Step 5: Domain Detection

```python
# Spatial domain detection using clustering with spatial constraints
# Option 1: Use spatial neighbors for Leiden clustering
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=15)
sc.tl.leiden(adata, resolution=0.3, key_added='spatial_domains',
             adjacency=adata.obsp['spatial_connectivities'])

# Visualize domains
sc.pl.spatial(adata, color='spatial_domains', spot_size=1.5)
plt.savefig('spatial_domains.pdf')

# Compare transcriptomic vs spatial clusters
sc.pl.spatial(adata, color=['leiden', 'spatial_domains'], ncols=2)
plt.savefig('clusters_comparison.pdf')
```

### Step 6: Visualization

```python
# Gene expression in space
genes = ['EPCAM', 'VIM', 'PTPRC', 'COL1A1']
sc.pl.spatial(adata, color=genes, ncols=2, spot_size=1.5, cmap='viridis')
plt.savefig('marker_genes_spatial.pdf')

# Cluster markers in space
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5)
plt.savefig('cluster_markers.pdf')

# Save
adata.write('spatial_analyzed.h5ad')
```

## Complete Workflow Script

```python
import scanpy as sc
import squidpy as sq
import matplotlib.pyplot as plt
import os

# Configuration
data_dir = 'spaceranger_output'
output_dir = 'spatial_results'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(f'{output_dir}/plots', exist_ok=True)

# Load
print('Loading data...')
adata = sq.read.visium(data_dir)
print(f'Loaded: {adata.n_obs} spots, {adata.n_vars} genes')

# QC
print('QC filtering...')
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
sc.pp.filter_cells(adata, min_counts=500)
sc.pp.filter_genes(adata, min_cells=10)
adata = adata[adata.obs.pct_counts_mt < 25, :]
print(f'After QC: {adata.n_obs} spots')

# Normalize and cluster
print('Processing...')
adata.layers['counts'] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
adata.raw = adata
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.leiden(adata, resolution=0.5)

# Spatial analysis
print('Spatial analysis...')
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)
sq.gr.nhood_enrichment(adata, cluster_key='leiden')
sq.gr.spatial_autocorr(adata, mode='moran', n_perms=100)

# Plots
print('Creating plots...')
sc.pl.spatial(adata, color='leiden', spot_size=1.5, save='_clusters.pdf')
sq.pl.nhood_enrichment(adata, cluster_key='leiden', save='_nhood.pdf')

# Save
adata.write(f'{output_dir}/spatial_analyzed.h5ad')
print(f'Results saved to {output_dir}/')
```

## Related Skills

- spatial-transcriptomics/spatial-data-io - Loading formats
- spatial-transcriptomics/spatial-preprocessing - QC details
- spatial-transcriptomics/spatial-statistics - Moran's I, co-occurrence
- spatial-transcriptomics/spatial-domains - Domain detection methods
- spatial-transcriptomics/spatial-deconvolution - Cell type estimation
