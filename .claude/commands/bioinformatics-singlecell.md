# bioinformatics-singlecell

> Advanced single-cell multi-omics analysis including scRNA-seq, scCITE-seq, scATAC-seq, and TARGET-seq. Use when analyzing single-cell data, cell type identification, trajectory analysis, differential expression, UMAP/clustering, integrating protein and RNA modalities (TotalVI), or working with Scanpy, Seurat, scvi-tools. Includes workflows for MPN, hematologic malignancies, megakaryocyte biology.

# Single-Cell Multi-Omics Analysis

## Core Libraries & Environment

```python
# Essential imports
import scanpy as sc
import anndata as ad
import scvi
import muon as mu
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Settings
sc.settings.verbosity = 3
sc.settings.set_figure_params(dpi=100, frameon=False, figsize=(6, 6))
```

## Standard scRNA-seq Workflow

```python
# 1. Load and QC
adata = sc.read_10x_mtx('path/to/filtered_feature_bc_matrix/')
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
adata = adata[adata.obs.pct_counts_mt < 20, :]

# 2. Normalization & HVG
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, batch_key='batch')

# 3. Dimensionality reduction
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, svd_solver='arpack')
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=40)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)
```

## TotalVI for CITE-seq Integration

```python
# Setup MuData
mdata = mu.MuData({'rna': adata_rna, 'protein': adata_prot})

# Train TotalVI
scvi.model.TOTALVI.setup_mudata(
    mdata, rna_layer='counts', protein_layer='counts',
    batch_key='batch', modalities={'rna_layer': 'rna', 'protein_layer': 'protein'}
)
model = scvi.model.TOTALVI(mdata, latent_distribution='normal', n_latent=20)
model.train(max_epochs=200, early_stopping=True)

# Get embeddings
mdata.obsm['X_totalVI'] = model.get_latent_representation()
sc.pp.neighbors(mdata, use_rep='X_totalVI')
sc.tl.umap(mdata)
sc.tl.leiden(mdata, key_added='leiden_totalVI', resolution=0.6)
```

## Differential Expression

```python
# DEG analysis
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
result = adata.uns['rank_genes_groups']
df = pd.DataFrame({
    'gene': result['names']['0'],
    'log2FC': result['logfoldchanges']['0'],
    'pval_adj': result['pvals_adj']['0']
})
sig_genes = df[(df['pval_adj'] < 0.05) & (abs(df['log2FC']) > 1)]
```

## Publication-Quality Visualization

```python
# Dot plot with proper expression cutoffs
sc.pl.dotplot(
    adata, var_names=marker_genes, groupby='leiden',
    expression_cutoff=0.0001, mean_only_expressed=False,
    standard_scale='None', smallest_dot=0.1, dot_max=1.0,
    cmap='viridis', colorbar_title='Expression'
)

# UMAP by batch
for batch in adata.obs['batch'].unique():
    adata_batch = adata[adata.obs['batch'] == batch]
    sc.pl.umap(adata_batch, color='FOXP3', title=f'{batch}')
```

## Cell Type Annotation Markers

### Hematopoietic Markers
- **HSC**: CD34, KIT, THY1, CD38low
- **CMP/GMP**: CD34+, CD38+, CD123
- **MEP**: CD34+, CD38+, CD41/ITGA2B
- **Megakaryocytes**: ITGA2B, PF4, GP1BA, PPBP, VWF
- **Erythroid**: HBB, HBA1/2, GYPA, KLF1

### MPN-Specific Markers
- **Inflammatory MKs**: S100A8/9, CHI3L1, CXCL8, IL6
- **Fibrosis markers**: TGFB1, COL1A1, LOXL2, VEGFA
- **Disease genes**: JAK2, CALR, MPL, PPM1D, ASXL1

## Output & Saving

```python
# Save processed data
adata.write('processed_adata.h5ad')
model.save('totalvi_model/')
df.to_csv('DEG_results.csv', index=False)
```

See `references/cell_markers.md` for complete marker lists.
See `references/scvi_advanced.md` for advanced scvi-tools workflows.
