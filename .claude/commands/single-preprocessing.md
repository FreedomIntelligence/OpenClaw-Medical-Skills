# single-cell-preprocessing-with-omicverse

> Walk through omicverse's single-cell preprocessing tutorials to QC PBMC3k data, normalise counts, detect HVGs, and run PCA/embedding pipelines on CPU, CPU–GPU mixed, or GPU stacks.

# Single-cell preprocessing with omicverse

## Overview
Follow this skill when a user needs to reproduce the preprocessing workflow from the omicverse notebooks [`t_preprocess.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_preprocess.ipynb), [`t_preprocess_cpu.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_preprocess_cpu.ipynb), and [`t_preprocess_gpu.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_preprocess_gpu.ipynb). The tutorials operate on the 10x PBMC3k dataset and cover QC filtering, normalisation, highly variable gene (HVG) detection, dimensionality reduction, and downstream embeddings.

## Instructions
1. **Set up the environment**
   - Import `omicverse as ov` and `scanpy as sc`, then call `ov.plot_set(font_path='Arial')` (or `ov.ov_plot_set()` in legacy notebooks) to standardise figure styling.
   - Encourage `%load_ext autoreload` and `%autoreload 2` when iterating inside notebooks so code edits propagate without restarting the kernel.
2. **Prepare input data**
   - Download the PBMC3k filtered matrix from 10x Genomics (`pbmc3k_filtered_gene_bc_matrices.tar.gz`) and extract it under `data/filtered_gene_bc_matrices/hg19/`.
   - Load the matrix via `sc.read_10x_mtx(..., var_names='gene_symbols', cache=True)` and keep a writable folder like `write/` for exports.
3. **Perform quality control (QC)**
   - Run `ov.pp.qc(adata, tresh={'mito_perc': 0.2, 'nUMIs': 500, 'detected_genes': 250}, doublets_method='scrublet')` for the CPU/CPU–GPU pipelines; omit `doublets_method` on pure GPU where Scrublet is not yet supported.
   - Review the returned AnnData summary to confirm doublet rates and QC thresholds; advise adjusting cut-offs for different species or sequencing depths.
4. **Store raw counts before transformations**
   - Call `ov.utils.store_layers(adata, layers='counts')` immediately after QC so the original counts remain accessible for later recovery and comparison.
5. **Normalise and select HVGs**
   - Use `ov.pp.preprocess(adata, mode='shiftlog|pearson', n_HVGs=2000, target_sum=5e5)` to apply shift-log normalisation followed by Pearson residual HVG detection (set `target_sum=None` on GPU, which keeps defaults).
   - For CPU–GPU mixed runs, demonstrate `ov.pp.recover_counts(...)` to invert normalisation and store reconstructed counts in `adata.layers['recover_counts']`.
6. **Manage `.raw` and layer recovery**
   - Snapshot normalised data to `.raw` with `adata.raw = adata` (or `adata.raw = adata.copy()`), and show `ov.utils.retrieve_layers(adata_counts, layers='counts')` to compare normalised vs. raw intensities.
7. **Scale, reduce, and embed**
   - Scale features using `ov.pp.scale(adata)` (layers hold scaled matrices) followed by `ov.pp.pca(adata, layer='scaled', n_pcs=50)`.
   - Construct neighbourhood graphs with:
     - `sc.pp.neighbors(adata, n_neighbors=15, n_pcs=50, use_rep='scaled|original|X_pca')` for the baseline notebook.
     - `ov.pp.neighbors(..., use_rep='scaled|original|X_pca')` on CPU–GPU to leverage accelerated routines.
     - `ov.pp.neighbors(..., method='cagra')` on GPU to call RAPIDS graph primitives.
   - Generate embeddings via `ov.utils.mde(...)`, `ov.pp.umap(adata)`, `ov.pp.mde(...)`, `ov.pp.tsne(...)`, or `ov.pp.sude(...)` depending on the notebook variant.
8. **Cluster and annotate**
   - Run `ov.pp.leiden(adata, resolution=1)` or `ov.single.leiden(adata, resolution=1.0)` after neighbour graph construction; CPU–GPU pipelines also showcase `ov.pp.score_genes_cell_cycle` before clustering.
   - **IMPORTANT - Defensive checks**: When generating code that plots by clustering results (e.g., `color='leiden'`), always check if the clustering has been performed first:
     ```python
     # Check if leiden clustering exists, if not, run it
     if 'leiden' not in adata.obs:
         if 'neighbors' not in adata.uns:
             ov.pp.neighbors(adata, n_neighbors=15, use_rep='X_pca')
         ov.single.leiden(adata, resolution=1.0)
     ```
   - Plot embeddings with `ov.pl.embedding(...)` or `ov.utils.embedding(...)`, colouring by `leiden` clusters and marker genes. Always verify that the column specified in `color=` parameter exists in `adata.obs` before plotting.
9. **Document outputs**
   - Encourage saving intermediate AnnData objects (`adata.write('write/pbmc3k_preprocessed.h5ad')`) and figure exports using Matplotlib’s `plt.savefig(...)` to preserve QC summaries and embeddings.
10. **Notebook-specific notes**
    - *Baseline (`t_preprocess.ipynb`)*: Focuses on CPU execution with Scanpy neighbours; emphasise storing counts before and after `retrieve_layers` demonstrations.
    - *CPU–GPU mixed (`t_preprocess_cpu.ipynb`)*: Highlights Omicverse ≥1.7.0 mixed acceleration. Include timing magics (%%time) to showcase speedups and call out `doublets_method='scrublet'` support.
    - *GPU (`t_preprocess_gpu.ipynb`)*: Requires a CUDA-capable GPU, RAPIDS 24.04 stack, and `rapids-singlecell`. Mention the `ov.pp.anndata_to_GPU`/`ov.pp.anndata_to_CPU` transfers and `method='cagra'` neighbours. Note the current warning that pure-GPU pipelines depend on RAPIDS updates.
11. **Troubleshooting tips**
    - If `sc.read_10x_mtx` fails, verify the extracted folder structure and ensure gene symbols are available via `var_names='gene_symbols'`.
    - Address GPU import errors by confirming the conda environment matches the RAPIDS version for the installed CUDA driver (`nvidia-smi`).
    - For `ov.pp.preprocess` dimension mismatches, ensure QC filtered out empty barcodes so HVG selection does not encounter zero-variance features.
    - When embeddings lack expected fields (e.g., `scaled|original|X_pca` missing), re-run `ov.pp.scale` and `ov.pp.pca` to rebuild the cached layers.
    - **Pipeline dependency errors**: When encountering errors like "Could not find 'leiden' in adata.obs or adata.var_names":
      - Always check if required preprocessing steps (neighbors, PCA) exist before dependent operations
      - Check if clustering results exist in `adata.obs` before trying to color plots by them
      - Use defensive checks in generated code to handle incomplete pipelines gracefully
    - **Code generation best practice**: Generate robust code with conditional checks for prerequisites rather than assuming perfect sequential execution. Users may run steps in separate sessions or skip intermediate steps.

## Critical API Reference - Batch Column Handling

### Batch Column Validation - REQUIRED Before Batch Operations

**IMPORTANT**: Always validate and prepare the batch column before any batch-aware operations (batch correction, integration, etc.). Missing or NaN values will cause errors.

**CORRECT usage:**
```python
# Step 1: Check if batch column exists, create default if not
if 'batch' not in adata.obs.columns:
    adata.obs['batch'] = 'batch_1'  # Default single batch

# Step 2: Handle NaN/missing values - CRITICAL!
adata.obs['batch'] = adata.obs['batch'].fillna('unknown')

# Step 3: Convert to categorical for efficient memory usage
adata.obs['batch'] = adata.obs['batch'].astype('category')

# Now safe to use in batch-aware operations
ov.pp.combat(adata, batch='batch')  # or other batch correction methods
```

**WRONG - DO NOT USE:**
```python
# WRONG! Using batch column without validation can cause NaN errors
# ov.pp.combat(adata, batch='batch')  # May fail if batch has NaN values!

# WRONG! Assuming batch column exists
# adata.obs['batch'].unique()  # KeyError if column doesn't exist!
```

### Common Batch-Related Pitfalls

1. **NaN values in batch column**: Always use `fillna()` before batch operations
2. **Missing batch column**: Always check existence before use
3. **Non-categorical batch**: Convert to category for memory efficiency
4. **Mixed data types**: Ensure consistent string type before categorization

```python
# Complete defensive batch preparation pattern:
def prepare_batch_column(adata, batch_key='batch', default_batch='batch_1'):
    """Prepare batch column for batch-aware operations."""
    if batch_key not in adata.obs.columns:
        adata.obs[batch_key] = default_batch
    adata.obs[batch_key] = adata.obs[batch_key].fillna('unknown')
    adata.obs[batch_key] = adata.obs[batch_key].astype(str).astype('category')
    return adata
```

## Highly Variable Genes (HVG) - Small Dataset Handling

### LOESS Failure with Small Batches

**IMPORTANT**: The `seurat_v3` HVG flavor uses LOESS regression which fails on small datasets or small per-batch subsets (<500 cells per batch). This manifests as:
```
ValueError: Extrapolation not allowed with blending
```

**CORRECT - Use try/except fallback pattern:**
```python
# Robust HVG selection for any dataset size
try:
    sc.pp.highly_variable_genes(
        adata,
        flavor='seurat_v3',
        n_top_genes=2000,
        batch_key='batch'  # if batch correction is needed
    )
except ValueError as e:
    if 'Extrapolation' in str(e) or 'LOESS' in str(e):
        # Fallback to simpler method for small datasets
        sc.pp.highly_variable_genes(
            adata,
            flavor='seurat',  # Works with any size
            n_top_genes=2000
        )
    else:
        raise
```

**Alternative - Use cell_ranger flavor for batch-aware HVG:**
```python
# cell_ranger flavor is more robust for batched data
sc.pp.highly_variable_genes(
    adata,
    flavor='cell_ranger',  # No LOESS, works with batches
    n_top_genes=2000,
    batch_key='batch'
)
```

### Best Practices for Batch-Aware HVG

1. **Check batch sizes before HVG**: Small batches (<500 cells) will cause LOESS to fail
2. **Prefer `seurat` or `cell_ranger`** when batch sizes vary significantly
3. **Use `seurat_v3` only** when all batches have >500 cells
4. **Always wrap in try/except** when dataset size is unknown

```python
# Safe batch-aware HVG pattern
def safe_highly_variable_genes(adata, batch_key='batch', n_top_genes=2000):
    """Select HVGs with automatic fallback for small batches."""
    try:
        sc.pp.highly_variable_genes(
            adata, flavor='seurat_v3', n_top_genes=n_top_genes, batch_key=batch_key
        )
    except ValueError:
        # Fallback for small batches
        sc.pp.highly_variable_genes(
            adata, flavor='seurat', n_top_genes=n_top_genes
        )
```

## Examples
- "Download PBMC3k counts, run QC with Scrublet, normalise with `shiftlog|pearson`, and compute MDE + UMAP embeddings on CPU."
- "Set up the mixed CPU–GPU workflow in a fresh conda env, recover raw counts after normalisation, and score cell cycle phases before Leiden clustering."
- "Provision a RAPIDS environment, transfer AnnData to GPU, run `method='cagra'` neighbours, and return embeddings to CPU for plotting."

## References
- Detailed walkthrough notebooks: [`t_preprocess.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_preprocess.ipynb), [`t_preprocess_cpu.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_preprocess_cpu.ipynb), [`t_preprocess_gpu.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_preprocess_gpu.ipynb)
- Quick copy/paste commands: [`reference.md`](reference.md)
