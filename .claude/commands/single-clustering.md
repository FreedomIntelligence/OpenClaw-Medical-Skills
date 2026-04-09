# single-cell-clustering-and-batch-correction-with-omicverse

> Guide Claude through omicverse's single-cell clustering workflow, covering preprocessing, QC, multimethod clustering, topic modeling, cNMF, and cross-batch integration as demonstrated in t_cluster.ipynb and t_single_batch.ipynb.

# Single-cell clustering and batch correction with omicverse

## Overview
This skill distills the single-cell tutorials [`t_cluster.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_cluster.ipynb) and [`t_single_batch.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_single_batch.ipynb). Use it when a user wants to preprocess an `AnnData` object, explore clustering alternatives (Leiden, Louvain, scICE, GMM, topic/cNMF models), and evaluate or harmonise batches with omicverse utilities.

## Instructions
1. **Import libraries and set plotting defaults**
   - Load `omicverse as ov`, `scanpy as sc`, and plotting helpers (`scvelo as scv` when using dentate gyrus demo data).
   - Apply `ov.plot_set()` or `ov.utils.ov_plot_set()` so figures adopt omicverse styling before embedding plots.
2. **Load data and annotate batches**
   - For demo clustering, fetch `scv.datasets.dentategyrus()`; for integration, read provided `.h5ad` files via `ov.read()` and set `adata.obs['batch']` identifiers for each cohort.
   - Confirm inputs are sparse numeric matrices; convert with `adata.X = adata.X.astype(np.int64)` when required for QC steps.
3. **Run quality control**
   - Execute `ov.pp.qc(adata, tresh={'mito_perc': 0.2, 'nUMIs': 500, 'detected_genes': 250}, batch_key='batch')` to drop low-quality cells and inspect summary statistics per batch.
   - Save intermediate filtered objects (`adata.write_h5ad(...)`) so users can resume from clean checkpoints.
4. **Preprocess and select features**
   - Call `ov.pp.preprocess(adata, mode='shiftlog|pearson', n_HVGs=3000, batch_key=None)` to normalise, log-transform, and flag highly variable genes; assign `adata.raw = adata` and subset to `adata.var.highly_variable_features` for downstream modelling.
   - Scale expression (`ov.pp.scale(adata)`) and compute PCA scores with `ov.pp.pca(adata, layer='scaled', n_pcs=50)`. Encourage reviewing variance explained via `ov.utils.plot_pca_variance_ratio(adata)`.
5. **Construct neighbourhood graph and baseline clustering**
   - Build neighbour graph using `sc.pp.neighbors(adata, n_neighbors=15, n_pcs=50, use_rep='scaled|original|X_pca')` or `ov.pp.neighbors(...)`.
   - Generate Leiden or Louvain labels through `ov.utils.cluster(adata, method='leiden'|'louvain', resolution=1)`, `ov.single.leiden(adata, resolution=1.0)`, or `ov.pp.leiden(adata, resolution=1)`; remind users that resolution tunes granularity.
   - **IMPORTANT - Dependency checks**: Always verify prerequisites before clustering or plotting:
     ```python
     # Before clustering: check neighbors graph exists
     if 'neighbors' not in adata.uns:
         if 'X_pca' in adata.obsm:
             ov.pp.neighbors(adata, n_neighbors=15, use_rep='X_pca')
         else:
             raise ValueError("PCA must be computed before neighbors graph")

     # Before plotting by cluster: check clustering was performed
     if 'leiden' not in adata.obs:
         ov.single.leiden(adata, resolution=1.0)
     ```
   - Visualise embeddings with `ov.pl.embedding(adata, basis='X_umap', color=['clusters','leiden'], frameon='small', wspace=0.5)` and confirm cluster separation. Always check that columns in `color=` parameter exist in `adata.obs` before plotting.
6. **Explore advanced clustering strategies**
   - **scICE consensus**: instantiate `model = ov.utils.cluster(adata, method='scICE', use_rep='scaled|original|X_pca', resolution_range=(4,20), n_boot=50, n_steps=11)` and inspect stability via `model.plot_ic(figsize=(6,4))` before selecting `model.best_k` groups.
   - **Gaussian mixtures**: run `ov.utils.cluster(..., method='GMM', n_components=21, covariance_type='full', tol=1e-9, max_iter=1000)` for model-based assignments.
   - **Topic modelling**: fit `LDA_obj = ov.utils.LDA_topic(...)`, review `LDA_obj.plot_topic_contributions(6)`, derive cluster calls with `LDA_obj.predicted(k)` and optionally refine using `LDA_obj.get_results_rfc(...)`.
   - **cNMF programs**: initialise `cnmf_obj = ov.single.cNMF(... components=np.arange(5,11), n_iter=20, num_highvar_genes=2000, output_dir=...)`, factorise (`factorize`, `combine`), select K via `k_selection_plot`, and propagate usage scores back with `cnmf_obj.get_results(...)` and `cnmf_obj.get_results_rfc(...)`.
7. **Evaluate clustering quality**
   - Compare predicted labels against known references with `adjusted_rand_score(adata.obs['clusters'], adata.obs['leiden'])` and report metrics for each method (Leiden, Louvain, GMM, LDA variants, cNMF models) to justify chosen parameters.
8. **Embed with multiple layouts**
   - Use `ov.utils.mde(...)` to create MDE projections from different latent spaces (`adata.obsm["scaled|original|X_pca"]`, harmonised embeddings, topic compositions) and plot via `ov.utils.embedding(..., color=['batch','cell_type'])` or `ov.pl.embedding` for consistent review of cluster/batch mixing.
9. **Perform batch correction and integration**
   - Apply `ov.single.batch_correction(adata, batch_key='batch', methods='harmony'|'combat'|'scanorama'|'scVI'|'CellANOVA', n_pcs=50, ...)` sequentially to generate harmonised embeddings stored in `adata.obsm` (`X_harmony`, `X_combat`, `X_scanorama`, `X_scVI`, `X_cellanova`). For `scVI`, mention latent size (`n_latent=30`) and `gene_likelihood="nb"`; for CellANOVA define control pools via `control_dict`.
   - After each correction, project to 2D with `ov.utils.mde` and visualise `batch` vs `cell_type` to check mixing and conservation.
10. **Benchmark integration performance**
    - Persist final object (`adata.write_h5ad('neurips2021_batch_all.h5ad', compression='gzip')`) and reload when necessary.
    - Use `scib_metrics.benchmark.Benchmarker` with embeddings list (`["X_pca", "X_combat", "X_harmony", "X_cellanova", "X_scanorama", "X_mira_topic", "X_mira_feature", "X_scVI"]`) to compute batch-vs-biology trade-offs via `bm.benchmark()` and summarise with `bm.plot_results_table(min_max_scale=False)`.
11. **General troubleshooting**
    - Ensure `adata.raw` captures the unscaled log-normalised matrix before subsetting to HVGs.
    - Confirm `use_rep='scaled|original|X_pca'` strings exist in `adata.obsm` prior to clustering; rerun preprocessing if missing.
    - Monitor memory when running cNMF or scVI; adjust `n_iter`, `components`, or latent dimensions for smaller datasets.
    - **Pipeline dependency errors**: When you encounter errors like "Could not find 'leiden' in adata.obs", always check and add prerequisites:
      - Before leiden/louvain clustering → ensure `'neighbors' in adata.uns`
      - Before plotting by clustering → ensure the cluster column exists in `adata.obs`
      - Before UMAP/embedding → ensure PCA or another dimensionality reduction is complete
    - **Code generation pattern**: When generating multi-step code, use defensive checks rather than assuming prior steps completed successfully. This prevents cascading failures when users run steps out of order or in separate sessions.

## Examples
- "Normalise dentate gyrus cells, compare Leiden, scICE, and GMM clusters, and report ARI scores versus provided `clusters`."
- "Batch-correct three NeurIPS datasets with Harmony and scVI, produce MDE embeddings coloured by `batch` and `cell_type`, and benchmark the embeddings."
- "Fit topic and cNMF models on a preprocessed AnnData object, retrieve classifier-refined cluster calls, and visualise the resulting programs on UMAP."

## References
- Clustering walkthrough: [`t_cluster.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_cluster.ipynb)
- Batch integration walkthrough: [`t_single_batch.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_single_batch.ipynb)
- Quick copy/paste commands: [`reference.md`](reference.md)
