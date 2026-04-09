# bulk-rna-seq-batch-correction-with-combat

> Use omicverse's pyComBat wrapper to remove batch effects from merged bulk RNA-seq or microarray cohorts, export corrected matrices, and benchmark pre/post correction visualisations.

# Bulk RNA-seq batch correction with ComBat

## Overview
Apply this skill when a user has multiple bulk expression matrices measured across different batches and needs to harmonise them
 before downstream analysis. It follows [`t_bulk_combat.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_bulk_combat.ipynb), w
hich demonstrates the pyComBat workflow on ovarian cancer microarray cohorts.

## Instructions
1. **Import core libraries**
   - Load `omicverse as ov`, `anndata`, `pandas as pd`, and `matplotlib.pyplot as plt`.
   - Call `ov.ov_plot_set()` (aliased `ov.plot_set()` in some releases) to align figures with omicverse styling.
2. **Load each batch separately**
   - Read the prepared pickled matrices (or user-provided expression tables) with `pd.read_pickle(...)`/`pd.read_csv(...)`.
   - Transpose to gene × sample before wrapping them in `anndata.AnnData` objects so `adata.obs` stores sample metadata.
   - Assign a `batch` column for every cohort (`adata.obs['batch'] = '1'`, `'2'`, ...). Encourage descriptive labels when availa
ble.
3. **Concatenate on shared genes**
   - Use `anndata.concat([adata1, adata2, adata3], merge='same')` to retain the intersection of genes across batches.
   - Confirm the combined `adata` reports balanced sample counts per batch; if not, prompt users to re-check inputs.
4. **Run ComBat batch correction**
   - Execute `ov.bulk.batch_correction(adata, batch_key='batch')`.
   - Explain that corrected values are stored in `adata.layers['batch_correction']` while the original counts remain in `adata.X`.
5. **Export corrected and raw matrices**
   - Obtain DataFrames via `adata.to_df().T` (raw) and `adata.to_df(layer='batch_correction').T` (corrected).
   - Encourage saving both tables (`.to_csv(...)`) plus the harmonised AnnData (`adata.write_h5ad('adata_batch.h5ad', compressio
n='gzip')`).
6. **Benchmark the correction**
   - For per-sample variance checks, draw before/after boxplots and recolour boxes using `ov.utils.red_color`, `blue_color`, `gree
n_color` palettes to match batches.
   - Copy raw counts to a named layer with `adata.layers['raw'] = adata.X.copy()` before PCA.
   - Run `ov.pp.pca(adata, layer='raw', n_pcs=50)` and `ov.pp.pca(adata, layer='batch_correction', n_pcs=50)`.
   - Visualise embeddings with `ov.utils.embedding(..., basis='raw|original|X_pca', color='batch', frameon='small')` and repeat fo
r the corrected layer to verify mixing.
7. **Troubleshooting tips**
   - Mismatched gene identifiers cause dropped features—remind users to harmonise feature names (e.g., gene symbols) before conca
tenation.
   - pyComBat expects log-scale intensities or similarly distributed counts; recommend log-transforming strongly skewed matrices.
   - If `batch_correction` layer is missing, ensure the `batch_key` matches the column name in `adata.obs`.

## Examples
- "Combine three GEO ovarian cohorts, run ComBat, and export both the raw and corrected CSV matrices."
- "Plot PCA embeddings before and after batch correction to confirm that batches 1–3 overlap."
- "Save the harmonised AnnData file so I can reload it later for downstream DEG analysis."

## References
- Tutorial notebook: [`t_bulk_combat.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_bulk_combat.ipynb)
- Example inputs: [`omicverse_guide/docs/Tutorials-bulk/data/combat/`](../../omicverse_guide/docs/Tutorials-bulk/data/combat/)
- Quick copy/paste commands: [`reference.md`](reference.md)
