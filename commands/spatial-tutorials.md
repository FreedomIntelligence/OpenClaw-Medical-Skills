# spatial-transcriptomics-tutorials-with-omicverse

> Guide users through omicverse's spatial transcriptomics tutorials covering preprocessing, deconvolution, and downstream modelling workflows across Visium, Visium HD, Stereo-seq, and Slide-seq datasets.

# Spatial transcriptomics tutorials with omicverse

## Overview
Use this skill to navigate the spatial analysis tutorials located under [`Tutorials-space`](../../omicverse_guide/docs/Tutorials-space/). The notebooks span preprocessing utilities ([`t_crop_rotate.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_crop_rotate.ipynb), [`t_cellpose.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cellpose.ipynb)), deconvolution frameworks ([`t_decov.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_decov.ipynb), [`t_starfysh.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_starfysh.ipynb)), and downstream spatial modelling or integration tasks ([`t_cluster_space.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cluster_space.ipynb), [`t_staligner.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_staligner.ipynb), [`t_spaceflow.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_spaceflow.ipynb), [`t_commot_flowsig.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_commot_flowsig.ipynb), [`t_gaston.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_gaston.ipynb), [`t_slat.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_slat.ipynb), [`t_stt.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_stt.ipynb)). Follow the staged instructions below to match the "Preprocess", "Deconvolution", and "Downstream" groupings presented in the notebooks.

## Instructions
### Preprocess
1. **Load spatial slides and manipulate coordinates**
   - Import `omicverse as ov`, `scanpy as sc`, and enable plotting defaults with `ov.plot_set()` or `ov.plot_set(font_path='Arial')`. [`t_crop_rotate.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_crop_rotate.ipynb)
   - Fetch public Visium data via `sc.datasets.visium_sge(...)`, inspect `adata.obsm['spatial']`, and respect `uns['spatial'][library_id]['scalefactors']` when rescaling coordinates for high-resolution overlays.
   - Apply region selection and alignment helpers: `ov.space.crop_space_visium(...)` for bounding-box crops, `ov.space.rotate_space_visium(...)` followed by `ov.space.map_spatial_auto(..., method='phase')`, and refine offsets with `ov.space.map_spatial_manual(...)` before plotting using `sc.pl.embedding(..., basis='spatial')`.
2. **Segment Visium HD tiles into cells**
   - Organise Visium HD outputs (binned parquet counts, `.btf` histology) and load them through `ov.space.read_visium_10x(path, source_image_path=...)`. [`t_cellpose.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cellpose.ipynb)
   - Filter sparse bins (`ov.pp.filter_genes(..., min_cells=3)` and `ov.pp.filter_cells(..., min_counts=1)`) prior to segmentation.
   - Run nucleus/cell segmentation variants: `ov.space.visium_10x_hd_cellpose_he(...)` for H&E, `ov.space.visium_10x_hd_cellpose_expand(...)` to grow labels across neighbouring bins, and `ov.space.visium_10x_hd_cellpose_gex(...)` for gene-expression driven seeds. Harmonise labels with `ov.space.salvage_secondary_labels(...)` and aggregate to cell-level AnnData using `ov.space.bin2cell(..., labels_key='labels_joint')`.
3. **Initial QC for downstream tasks**
   - For Visium/DLPFC re-analyses, compute QC metrics (`sc.pp.calculate_qc_metrics(adata, inplace=True)`) and persist intermediate AnnData snapshots (`adata.write('data/cluster_svg.h5ad', compression='gzip')`) for reuse across tutorials. [`t_cluster_space.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cluster_space.ipynb)

### Deconvolution
4. **Configure single-cell references and spatial targets**
   - Load scRNA-seq references (`adata_sc = ov.read('data/sc.h5ad')`) with harmonised gene IDs and spatial slides (`adata_sp = sc.datasets.visium_sge(...)`). [`t_decov.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_decov.ipynb)
   - Instantiate the unified wrapper `ov.space.Deconvolution(...)`, passing shared keys like `celltype_key`, `adata_sc`, and `adata_sp`.
5. **Execute Tangram and cell2location pipelines**
   - Call `decov_obj.preprocess_sc(...)` / `decov_obj.preprocess_sp(...)` to align matrices, then run `decov_obj.deconvolution(method='tangram', ...)` and persist outputs with `ov.utils.save(...)` plus `.write(...)` hooks for AnnData members.
   - For cell2location, reinitialise `ov.space.Deconvolution(..., method='cell2location')`, train (`decov_obj.deconvolution(max_epochs=...)`), monitor via `decov_obj.mod_sc.plot_history(...)`, and store models (`decov_obj.save_model(...)`).
   - Visualise inferred proportions using `ov.space.plot_cell2location(...)`, `sc.pl.spatial(..., color=list_of_celltypes)`, and ROI-focused pie charts after cropping (`ov.space.crop_space_visium(...)`).
6. **Run Starfysh archetypal deconvolution**
   - Import Starfysh utilities (`from omicverse.external.starfysh import AA, utils, plot_utils, post_analysis`) and prepare expression counts plus optional signature sets. [`t_starfysh.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_starfysh.ipynb)
   - Identify anchor spots with `utils.prepare_data(...)`, optionally infer archetypes via `AA.ArchetypalAnalysis(...)`, and refine signatures using `utils.refine_anchors(...)`.
   - Train Starfysh models (`utils.run_starfysh(poe=False, ...)` or `poe=True` with histology) across multiple restarts, then parse outputs through `post_analysis.load_model(...)`, `plot_utils.pl_spatial_inf_feature(...)`, and `cell2proportion(...)` for per-cell-type maps.

### Downstream
7. **Spatial clustering and denoising**
   - Generate embeddings using omicverse wrappers: `ov.utils.cluster(..., use_rep='graphst|original|X_pca', method='mclust')`, `ov.space.merge_cluster(...)`, and evaluate ARI (`adjusted_rand_score(...)`). [`t_cluster_space.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cluster_space.ipynb)
   - Explore algorithm-specific toggles: GraphST/BINARY require precalculated latent spaces, STAGATE training (`ov.utils.cluster(..., use_rep='STAGATE', ...)`), and CAST for multi-slice single-cell resolution data.
8. **Integrate multi-slice datasets**
   - Concatenate Stereo-seq/Slide-seqV2 batches (`ad.concat(Batch_list, label='slice_name', keys=section_ids)`) and initialise `ov.space.pySTAligner(...)`. [`t_staligner.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_staligner.ipynb)
   - Train with `STAligner_obj.train_STAligner_subgraph(...)`, call `STAligner_obj.train()`, and retrieve latent embeddings via `STAligner_obj.predicted()` before clustering (`sc.pp.neighbors(..., use_rep='STAligner')`, `ov.utils.cluster(...)`).
9. **Model spatial gradients and trajectories**
   - For pseudo-spatial maps, build `sf_obj = ov.space.pySpaceFlow(adata)` and train using `sf_obj.train(spatial_regularization_strength=0.1, ...)`, then compute `sf_obj.cal_pSM(...)` to populate `adata.obs['pSM_spaceflow']`. [`t_spaceflow.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_spaceflow.ipynb)
   - Analyse transition dynamics with `STT_obj = ov.space.STT(adata, spatial_loc='xy_loc', region='Region')`, followed by `STT_obj.train(...)`, `STT_obj.stage_estimate()`, and downstream visualisations (`STT_obj.plot_pathway(...)`, `STT_obj.infer_lineage(...)`). [`t_stt.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_stt.ipynb)
10. **Infer communication and flow networks**
    - Pull ligand–receptor resources via `ov.external.commot.pp.ligand_receptor_database(species='human')`, filter with `filter_lr_database(...)`, and compute signaling using `ov.external.commot.tl.spatial_communication(...)`. [`t_commot_flowsig.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_commot_flowsig.ipynb)
    - Construct FlowSig inputs (`adata.layers['normalized'] = adata.X.copy()`, `ov.external.flowsig.tl.construct_intercellular_flow_network(...)`), retain spatially informative modules (Moran’s I filtering), and validate edges through bootstrapping thresholds (`edge_threshold = 0.7`).
11. **Extract structural layers and align developmental slices**
    - Train GASTON with `gas_obj = ov.space.GASTON(adata)`, rescale GLM-PC matrices via `gas_obj.load_rescale(A)`, and infer iso-depths using `gas_obj.cal_iso_depth(n_layers)`. Visualise with `gas_obj.plot_isodepth(...)`, `gas_obj.plot_clusters_restrict(...)`, and probe continuous/discontinuous gene lists (`gas_obj.cont_genes_layer`). [`t_gaston.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_gaston.ipynb)
    - For SLAT, construct spatial graphs (`Cal_Spatial_Net(adata1, k_cutoff=20)`), run alignment (`run_SLAT(...)`, `spatial_match(...)`), and examine correspondences through Sankey diagrams (`Sankey_multi(...)`) and lineage-focused subsetting (`cal_matching_cell(...)`). [`t_slat.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_slat.ipynb)

## Dependencies
- Core: `omicverse`, `scanpy`, `anndata`, `numpy`, `matplotlib`, `squidpy` (deconvolution + QC), `networkx` (FlowSig graphs).
- Segmentation: `cellpose`, `stardist`, `opencv-python`/`tifffile`, optional GPU-enabled PyTorch for acceleration. [`t_cellpose.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cellpose.ipynb)
- Deconvolution: `tangram`, `cell2location`, `pytorch-lightning`, `pandas`, `h5py`, plus optional GPU/CUDA stacks; Starfysh additionally needs `torch`, `scikit-learn`, and curated signature CSVs. [`t_decov.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_decov.ipynb), [`t_starfysh.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_starfysh.ipynb)
- Downstream modelling: `scikit-learn` (clustering, KMeans, ARI), `gseapy==1.0.4` for STT enrichment, `commot`, `flowsig`, `torch`-backed modules (STAligner, SpaceFlow, GASTON, SLAT), plus HTML exporters (Plotly) for Sankey plots.

## Critical functions and artefacts to surface quickly
- Spatial preprocessing: `ov.space.crop_space_visium`, `ov.space.rotate_space_visium`, `ov.space.map_spatial_auto`, `ov.space.map_spatial_manual`, `ov.space.bin2cell`.
- Deconvolution containers: `ov.space.Deconvolution.preprocess_sc`, `.preprocess_sp`, `.deconvolution`, `.adata_cell2location`, `.adata_impute`.
- Archetypal/Starfysh: `AA.ArchetypalAnalysis`, `utils.refine_anchors`, `utils.run_starfysh`, `plot_utils.pl_spatial_inf_feature`.
- Clustering/integration: `ov.utils.cluster`, `ov.space.merge_cluster`, `ov.space.pySTAligner`, `ov.space.pySpaceFlow`, `ov.space.STT`, `ov.space.GASTON`, `Cal_Spatial_Net`, `run_SLAT`, `Sankey_multi`.
- Communication: `ov.external.commot.pp.ligand_receptor_database`, `ov.external.commot.tl.spatial_communication`, `ov.external.flowsig.tl.construct_intercellular_flow_network`.

## Troubleshooting
- **Coordinate mismatches after rotation/cropping**: ensure scalefactors are applied when plotting and cast `adata.obsm['spatial']` to `float64` before running `map_spatial_auto`. [`t_crop_rotate.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_crop_rotate.ipynb)
- **Cellpose runtime errors**: verify `.btf` image paths, memory-map large TIFFs via `backend='tifffile'`, and adjust `mpp` plus `buffer` for dense tissues; GPU runs require matching CUDA/PyTorch builds. [`t_cellpose.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cellpose.ipynb)
- **Gene ID overlap failures in Tangram/cell2location**: harmonise identifiers (ENSEMBL vs gene symbols) and drop non-overlapping genes before `decov_obj.preprocess_*`. [`t_decov.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_decov.ipynb)
- **mclust errors in spatial clustering**: install `rpy2` and the R `mclust` package, or switch to the pure Python `method='mclust'` fallback when R bindings are unavailable. [`t_cluster_space.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cluster_space.ipynb)
- **STAligner/SpaceFlow convergence**: confirm `adata.obsm['spatial']` exists and scale coordinates; tune learning rates/regularisation strength when embeddings collapse to a point. [`t_staligner.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_staligner.ipynb), [`t_spaceflow.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_spaceflow.ipynb)
- **FlowSig network sparsity**: build spatial graphs prior to Moran’s I filtering and raise `edge_threshold` or increase bootstraps to stabilise edges. [`t_commot_flowsig.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_commot_flowsig.ipynb)
- **STT pathway downloads**: `gseapy` lookups need network access; cache gene sets locally and reuse via `ov.utils.geneset_prepare(...)` to avoid repeated requests. [`t_stt.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_stt.ipynb)
- **GASTON output directories**: provide writable `out_dir` paths and account for PyTorch nondeterminism when comparing replicate runs. [`t_gaston.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_gaston.ipynb)
- **SLAT alignment quality**: regenerate spatial graphs with appropriate `k_cutoff` and inspect `low_quality_index` flags before trusting downstream lineage analyses. [`t_slat.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_slat.ipynb)

## Examples
- "Crop, rotate, and manually re-align Visium coordinates before running Visium HD cell segmentation, then aggregate bins into cell-level AnnData."
- "Execute Tangram and cell2location through `ov.space.Deconvolution`, save trained models, and plot lymph node cell-type proportions."
- "Train STAligner and SpaceFlow on DLPFC slices, infer communication networks with COMMOT+FlowSig, and visualise iso-depth layers via GASTON."

## References
- Tutorials: [`Tutorials-space/`](../../omicverse_guide/docs/Tutorials-space/)
- Notebook index: [`t_crop_rotate.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_crop_rotate.ipynb), [`t_cellpose.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cellpose.ipynb), [`t_cluster_space.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_cluster_space.ipynb), [`t_decov.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_decov.ipynb), [`t_starfysh.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_starfysh.ipynb), [`t_staligner.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_staligner.ipynb), [`t_spaceflow.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_spaceflow.ipynb), [`t_commot_flowsig.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_commot_flowsig.ipynb), [`t_gaston.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_gaston.ipynb), [`t_slat.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_slat.ipynb), [`t_stt.ipynb`](../../omicverse_guide/docs/Tutorials-space/t_stt.ipynb)
- Quick copy/paste commands: [`reference.md`](reference.md)
