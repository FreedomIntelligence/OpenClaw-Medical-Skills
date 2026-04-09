# single-cell-multi-omics-integration

> Quick-reference sheet for OmicVerse tutorials spanning MOFA, GLUE pairing, SIMBA integration, TOSICA transfer, and StaVIA cartography.

# Single-Cell Multi-Omics Tutorials Cheat Sheet

This skill walk-through summarizes the OmicVerse notebooks that cover paired and unpaired multi-omic integration, multi-batch embedding, reference transfer, and trajectory cartography.

## MOFA on paired scRNA + scATAC (`t_mofa.ipynb`)
- **Data preparation:** Load preprocessed AnnData objects for RNA (`rna_p_n_raw.h5ad`) and ATAC (`atac_p_n_raw.h5ad`) with `ov.utils.read`, and initialise `pyMOFA` with matching `omics` and `omics_name` lists.
- **Model training:** Call `mofa_preprocess()` to select highly variable features and run the factor model with `mofa_run(outfile=...)`, which exports the learned MOFA+ factors to an HDF5 model file.
- **Result inspection:** Reload downstream AnnData, append factor scores via `ov.single.factor_exact`, and explore factor–cluster associations using `factor_correlation`, `get_weights`, and the plotting helpers in `pyMOFAART` (`plot_r2`, `plot_cor`, `plot_factor`, `plot_weights`, etc.).
- **Export workflow:** Persist factors and weights through the MOFA HDF5 artifact and reuse them by instantiating `pyMOFAART(model_path=...)` for later annotation or visualisation sessions.
- **Dependencies & hardware:** Requires `mofapy2`; plots optionally rely on `pymde`/`scvi-tools` but run on CPU.

## MOFA after GLUE pairing (`t_mofa_glue.ipynb`)
- **Data preparation:** Start from GLUE-derived embeddings (`rna-emb.h5ad`, `atac.emb.h5ad`), build a `GLUE_pair` object, and run `correlation()` to align unpaired cells before subsetting to highly variable features.
- **Model training:** Instantiate `pyMOFA` with the aligned AnnData objects, run `mofa_preprocess()`, and save the joint factors through `mofa_run(outfile='models/chen_rna_atac.hdf5')`.
- **Result inspection:** Use `pyMOFAART` plus AnnData that now contains the GLUE embeddings to compute factors (`get_factors`) and visualise variance explained, factor–cluster correlations, and ranked feature weights.
- **Export workflow:** Reuse the saved MOFA HDF5 model for downstream inspection; GLUE embeddings can be embedded with `scvi.model.utils.mde` (GPU-accelerated MDE is optional, `sc.tl.umap` works on CPU).
- **Dependencies & hardware:** Requires both `mofapy2` and the GLUE tooling (`scglue`, `scvi-tools`, `pymde`); GPU acceleration only affects optional MDE visualisation.

## SIMBA batch integration (`t_simba.ipynb`)
- **Data preparation:** Fetch the concatenated AnnData (`simba_adata_raw.h5ad`) derived from multiple pancreas studies and pass it, alongside a results directory, to `pySIMBA`.
- **Model training:** Execute `preprocess(...)` to bin features and build a SIMBA-compatible graph, then call `gen_graph()` followed by `train(num_workers=...)` to launch PyTorch-BigGraph optimisation (can scale with CPU workers) and `load(...)` to resume trained checkpoints.
- **Result inspection:** Apply `batch_correction()` to obtain the harmonised AnnData with SIMBA embeddings (`X_simba`) and visualise using `mde`/`sc.tl.umap` coloured by cell type or batch.
- **Export workflow:** Training outputs reside in the workdir (e.g., `result_human_pancreas/pbg/graph0`); reuse them with `simba_object.load(...)` for later analyses.
- **Dependencies & hardware:** Requires installing `simba` and `simba_pbg` (PyTorch BigGraph backend). GPU is optional; make sure adequate CPU threads and memory are available for graph training.

## TOSICA reference transfer (`t_tosica.ipynb`)
- **Data preparation:** Download demo AnnData references (`demo_train.h5ad`, `demo_test.h5ad`) and required gene-set GMT files via `ov.utils.download_tosica_gmt()`; confirm datasets are log-normalised before training.
- **Model training:** Create `pyTOSICA` with the reference AnnData, chosen pathway mask, label key, project directory, and batch size; train with `train(epochs=...)`, then persist weights with `save()` and optionally reload via `load()`.
- **Result inspection:** Generate predictions on query AnnData through `predicted(pre_adata=...)`, embed with OmicVerse preprocessing and GPU-enabled `mde` (UMAP fallback available), and explore pathway attention to interpret transformer heads.
- **Export workflow:** Saved project folder keeps model checkpoints and attention summaries; reuse the exported assets to annotate future datasets without retraining from scratch.
- **Dependencies & hardware:** Needs TOSICA (PyTorch transformer) plus downloaded gene-set masks; avoid setting `depth=2` if memory is constrained. GPU acceleration improves embedding (`mde`) but training runs on standard PyTorch (CPU/GPU depending on environment).

## StaVIA trajectory cartography (`t_stavia.ipynb`)
- **Data preparation:** Load example dentate gyrus velocity data via `scvelo.datasets.dentategyrus()`, preprocess with OmicVerse (`preprocess`, `scale`, `pca`, neighbours, UMAP) to populate the AnnData matrices used by VIA.
- **Model training:** Configure VIA hyperparameters (components, neighbours, seeds, root selection) and instantiate/run `VIA.core.VIA` on the chosen representation (`adata.obsm['scaled|original|X_pca']`).
- **Result inspection:** Store outputs such as pseudotime (`single_cell_pt_markov`), cluster graph abstractions, trajectory curves, atlas views, and stream plots through VIA plotting helpers.
- **Export workflow:** Persist derived visualisations and animations (e.g., `animate_streamplot_ov`, `animate_atlas`) to files (`.gif`) for reporting; recompute edge bundles via `make_edgebundle_milestone` when needed.
- **Dependencies & hardware:** Relies on `scvelo`, `pyVIA`, and OmicVerse plotting; computations are CPU-bound though producing large stream/animation outputs benefits from ample memory.
