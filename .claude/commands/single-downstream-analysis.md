# single-cell-downstream-analysis

> Checklist-style reference for OmicVerse downstream tutorials covering AUCell scoring, metacell DEG, and related exports.

# Single-cell downstream analysis quick-reference

This skill sheet distills the OmicVerse single-cell downstream tutorials into an executable checklist. Each module
highlights **prerequisites**, the **core API entry points**, **interpretation checkpoints**, **resource planning notes**, and
any **optional validation or export steps** surfaced in the notebooks.

## AUCell pathway scoring (`t_aucell.ipynb`)
- **Prerequisites**
  - Download pathway collections (GO, KEGG, or custom) that match the organism under study before running the tutorial.
  - Ensure an `AnnData` object with clustering/embedding (`adata.obsm['X_umap']`) is prepared.
- **Core calls**
  - `ov.single.geneset_aucell` for one pathway; `ov.single.pathway_aucell` for multiple pathways.
  - `ov.single.pathway_aucell_enrichment` to score all pathways in a library (set `num_workers` for parallelism).
- **Result checks**
  - Interpret AUCell scores as expression-like values (0–1). Use `sc.pl.embedding` to confirm pathway activity patterns.
  - Run `sc.tl.rank_genes_groups` on the AUCell `AnnData` to find cluster-enriched pathways and visualize with
    `sc.pl.rank_genes_groups_dotplot`.
- **Resources**
  - Library-wide scoring can be CPU-intensive; allocate workers (`num_workers=8` in tutorial) and sufficient memory for the
    dense AUCell matrix.
- **Optional validation / exports**
  - Persist scores with `adata_aucs.write_h5ad('...')` for reuse.
  - Plot enriched pathways via `ov.single.pathway_enrichment` and `ov.single.pathway_enrichment_plot` heatmaps.

## scRNA-seq DEG (bulk-style meta cell) (`t_scdeg.ipynb`)
- **Prerequisites**
  - Run quality control and preprocessing (`ov.pp.qc`, `ov.pp.preprocess`, `ov.pp.scale`, `ov.pp.pca`).
  - Retain raw counts in `adata.raw` before HVG filtering.
- **Core calls**
  - Construct differential objects with `ov.bulk.pyDEG(test_adata.to_df(...).T)` for full-cell and metacell views.
  - Build metacells via `ov.single.MetaCell(..., use_gpu=True)` when GPU is available for acceleration.
- **Result checks**
  - Inspect volcano plots (`dds.plot_volcano`) and targeted boxplots (`dds.plot_boxplot`) for top DEGs.
  - Map DEG markers back to UMAP embeddings using `ov.utils.embedding` to confirm localization.
- **Resources**
  - Metacell construction benefits from GPU but can fall back to CPU; ensure enough memory for transposed dense matrices
    passed to `pyDEG`.
- **Optional validation / exports**
  - Save metacell embeddings with matplotlib figures; adjust `legend_*` settings for publication-ready visuals.

## scRNA-seq DEG (cell-type & composition) (`t_deg_single.ipynb`)
- **Prerequisites**
  - Annotated `adata` with `condition`, `cell_label`, and optional `batch` metadata.
  - Initialize mixed CPU/GPU resources when using graph-based DA methods (`ov.settings.cpu_gpu_mixed_init()`).
- **Core calls**
  - `ov.single.DEG(..., method='wilcoxon'|'t-test'|'memento-de')` with `deg_obj.run(...)` to target cell types.
  - `ov.single.DCT(..., method='sccoda'|'milo')` for differential composition testing.
  - Graph setup for Milo: `ov.pp.preprocess`, `ov.single.batch_correction`, `ov.pp.neighbors`, `ov.pp.umap`.
- **Result checks**
  - Review DEG tables from `deg_obj` (Wilcoxon / memento) and adjust capture rate / bootstraps for stability.
  - For scCODA, tune FDR via `sim_results.set_fdr()`; interpret boxplots with condition-level shifts.
  - Milo diagnostics: histogram of P-values, logFC vs –log10 FDR scatter, beeswarm of differential abundance.
- **Resources**
  - Memento and Milo require multiple CPUs (`num_cpus`, `num_boot`, high `k`); ensure adequate compute time.
  - Harmony/scVI batch correction needs GPU memory when enabled; plan for VRAM usage.
- **Optional validation / exports**
  - Visual diagnostics include UMAP overlays (`ov.pl.embedding`), Milo beeswarm plots, and custom color palettes.

## scDrug response prediction (`t_scdrug.ipynb`)
- **Prerequisites**
  - Fetch tumor-focused dataset (e.g., `infercnvpy.datasets.maynard2020_3k`).
  - Download reference assets **before** running predictions:
    - Gene annotations via `ov.utils.get_gene_annotation` (requires GTF from GENCODE or T2T-CHM13).
    - `ov.utils.download_GDSC_data()` and `ov.utils.download_CaDRReS_model()` for drug-response models.
    - Clone CaDRReS-Sc repo (`git clone https://github.com/CSB5/CaDRReS-Sc`).
- **Core calls**
  - Tumor resolution detection: `ov.single.autoResolution(adata, cpus=4)`.
  - Drug response runner: `ov.single.Drug_Response(adata, scriptpath='CaDRReS-Sc', modelpath='models/', output='result')`.
- **Result checks**
  - Inspect clustering and IC50 outputs stored under `output`; cross-reference with inferred CNV states.
- **Resources**
  - Requires external CaDRReS-Sc environment (Python/R dependencies) and storage for model downloads.
  - Running inferCNV preprocessing may need multiple CPUs and substantial RAM.
- **Optional validation / exports**
  - Persist intermediate `AnnData` (`adata.write('scanpyobj.h5ad')`) to reuse for downstream analyses or re-runs.

## SCENIC regulon discovery (`t_scenic.ipynb`)
- **Prerequisites**
  - Mouse hematopoiesis dataset loaded via `ov.single.mouse_hsc_nestorowa16()` (or provide preprocessed data with raw counts).
  - Download cisTarget ranking databases (`*.feather`) and motif annotations (`motifs-*.tbl`) for the species; allocate
    >3 GB disk space and verify paths (`db_glob`, `motif_path`).
- **Core calls**
  - Initialize analysis: `ov.single.SCENIC(adata, db_glob=..., motif_path=..., n_jobs=12)`.
  - Run RegDiffusion-based GRN inference, regulon pruning, and AUCell scoring via the SCENIC object methods.
- **Result checks**
  - Examine regulon activity matrices (`scenic_obj.auc_mtx.head()`), RSS scores, and embeddings colored by regulon activity.
  - Use RSS plots, dendrograms, and AUCell distributions to interpret TF specificity and activity thresholds.
- **Resources**
  - Multi-core CPU recommended (`n_jobs` matches available cores); ensure enough RAM for motif enrichment.
  - Large downloads and intermediate objects (pickle/h5ad) require disk space.
- **Optional validation / exports**
  - Save `scenic_obj` (`ov.utils.save`) and regulon AnnData (`regulon_ad.write`).
  - Optional plots: RSS per cell type, regulon embeddings, AUC histograms with threshold lines, GRN network visualizations.

## cNMF program discovery (`t_cnmf.ipynb`)
- **Prerequisites**
  - Preprocess with HVG selection (`ov.pp.preprocess`), scaling (`ov.pp.scale`), PCA, and have UMAP embeddings for inspection.
  - Select component range (e.g., `np.arange(5, 11)`) and iterations; ensure output directory exists.
- **Core calls**
  - Instantiate analysis: `ov.single.cNMF(..., output_dir='...', name='...')`.
  - Factorization workflow: `cnmf_obj.factorize(...)`, `cnmf_obj.combine(...)`, `cnmf_obj.k_selection_plot()`,
    `cnmf_obj.consensus(...)`.
  - Extract results: `cnmf_obj.load_results(...)`, `cnmf_obj.get_results(...)`, optional RF classifier via `get_results_rfc`.
- **Result checks**
  - Evaluate stability via K-selection plot and local density histogram; confirm chosen K with consensus heatmaps.
  - Inspect topic usage embeddings (`ov.pl.embedding`), cluster labels, and dotplots of top genes.
- **Resources**
  - Multiple iterations and components are CPU-heavy; consider distributing workers (`total_workers`) and verifying disk
    space for intermediate factorization files.
- **Optional validation / exports**
  - Visualizations include Euclidean distance heatmaps, density histograms, UMAP overlays for topics/clusters, and dotplots.

## NOCD overlapping communities (`t_nocd.ipynb`)
- **Prerequisites**
  - Prepare AnnData via `ov.single.scanpy_lazy` (automated preprocessing) before running NOCD.
  - Note: Tutorial warns NOCD implementation is under active development—expect variability.
- **Core calls**
  - Pipeline wrapper: `scbrca = ov.single.scnocd(adata)` followed by chained methods (`matrix_transform`, `matrix_normalize`,
    `GNN_configure`, `GNN_preprocess`, `GNN_model`, `GNN_result`, `GNN_plot`, `cal_nocd`, `calculate_nocd`).
- **Result checks**
  - Compare standard Leiden clusters versus NOCD outputs on UMAP embeddings to identify multi-fate cells.
- **Resources**
  - Graph neural network stages can be GPU-accelerated; ensure CUDA availability or be prepared for longer CPU runtimes.
  - Track memory usage when constructing large adjacency matrices.
- **Optional validation / exports**
  - Generate multiple UMAP overlays (`sc.pl.umap`) for `nocd`, `nocd_n`, and Leiden labels using shared color maps.

## Lazy pipeline & reporting (`t_lazy.ipynb`)
- **Prerequisites**
  - Install OmicVerse ≥1.7.0 with lazy utilities; supported species currently human/mouse.
  - Prepare batch metadata (`sample_key`) and optionally initialize hybrid compute (`ov.settings.cpu_gpu_mixed_init()`).
- **Core calls**
  - Turnkey preprocessing: `ov.single.lazy(adata, species='mouse', sample_key='batch', ...)` with optional `reforce_steps`
    and module-specific kwargs.
  - Reporting: `ov.single.generate_scRNA_report(...)` to build HTML summary; `ov.generate_reference_table(adata)` for
    citation tracking.
- **Result checks**
  - Inspect generated embeddings (`ov.pl.embedding`) for quality and annotation alignment.
  - Review HTML report for QC metrics, normalization, batch correction, and embeddings.
- **Resources**
  - Steps like Harmony or scVI may invoke GPU; confirm hardware availability or adjust `reforce_steps` accordingly.
  - Report generation writes to disk; ensure output path is writable.
- **Optional validation / exports**
  - Customize embeddings by color key; store HTML report and reference table alongside project documentation.
