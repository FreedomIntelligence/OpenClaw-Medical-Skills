# single-cell-cellphonedb-communication-mapping

> Run omicverse's CellPhoneDB v5 wrapper on annotated single-cell data to infer ligand-receptor networks and produce CellChat-style visualisations.

# Single-cell CellPhoneDB communication mapping

## Overview
Apply this skill when a user wants to quantify ligand–receptor communication between annotated single-cell populations and display the networks with `CellChatViz`. It distils the workflow from [`t_cellphonedb.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_cellphonedb.ipynb), which analyses EVT trophoblast data.

## Instructions
1. **Prepare the environment**
   - Use an environment with `omicverse>=0.2`, `scanpy`, `anndata`, `pandas`, `matplotlib`, and `cellphonedb` resources. The tutorial assumes the pre-built CellPhoneDB v5 SQLite bundle downloaded as `cellphonedb.zip` in the working directory.
   - Activate omicverse plotting defaults via `ov.plot_set()` so that downstream figures follow the project palette.
2. **Load and subset the annotated AnnData object**
   - Read the normalised counts with `adata = ov.read('data/cpdb/normalised_log_counts.h5ad')`.
   - Filter to the cell populations of interest using `adata.obs['cell_labels']` (e.g., EVT, dNK, VCT). Ensure `adata.obs['cell_labels']` is categorical and free of missing values so CellPhoneDB groups cells correctly.
   - Confirm values are log-normalised (`adata.X.max()` should be <10 and non-integer); raw counts inflate CellPhoneDB permutations.
3. **Run CellPhoneDB via omicverse**
   - Execute `ov.single.run_cellphonedb_v5` with the curated AnnData and metadata column:
     ```python
     cpdb_results, adata_cpdb = ov.single.run_cellphonedb_v5(
         adata,
         cpdb_file_path='./cellphonedb.zip',
         celltype_key='cell_labels',
         min_cell_fraction=0.005,
         min_genes=200,
         min_cells=3,
         iterations=1000,
         threshold=0.1,
         pvalue=0.05,
         threads=10,
         output_dir='./cpdb_results',
         cleanup_temp=True,
     )
     ```
   - Persist the outputs for reuse (`ov.utils.save(cpdb_results, ...)`, `adata_cpdb.write(...)`). Saving avoids recomputing permutations.
4. **Initialise CellChat-style visualisation**
   - Create a colour dictionary that maps ordered `cell_labels` categories to `adata.uns['cell_labels_colors']` from previous plots.
   - Instantiate the viewer: `viz = ov.pl.CellChatViz(adata_cpdb, palette=color_dict)`. Inspect `adata_cpdb` to ensure communication slots (`uns`/`obsm`) were populated.
5. **Summarise global communication**
   - Derive aggregated counts/weights with `viz.compute_aggregated_network(pvalue_threshold=0.05, use_means=True)`.
   - Plot overall interaction strength and counts using `viz.netVisual_circle(...)` with matching figure sizes and colormaps.
   - Generate outgoing/incoming per-celltype circles using `viz.netVisual_individual_circle` and `viz.netVisual_individual_circle_incoming` to highlight senders versus receivers.
6. **Interrogate specific pathways**
   - Compute pathway summaries: `pathway_comm = viz.compute_pathway_communication(method='mean', min_lr_pairs=2, min_expression=0.1)`.
   - Identify significant signalling routes with `viz.get_significant_pathways_v2(...)`, then plot selected pathways using `viz.netVisual_aggregate(..., layout='circle')`, `viz.netVisual_chord_cell(...)`, or `viz.netVisual_heatmap_marsilea(...)`.
   - For ligand–receptor focus, call `viz.netVisual_chord_LR(...)` or `viz.netAnalysis_contribution(pathway)` to surface dominant pairs.
7. **System-level visualisations**
   - Compose bubble summaries for multiple pathways with `viz.netVisual_bubble_marsilea(...)`, optionally restricting `sources_use`/`targets_use`.
   - Display gene-level chords via `viz.netVisual_chord_gene(...)` to inspect signalling directionality.
   - Evaluate signalling roles using `viz.netAnalysis_computeCentrality()`, `viz.netAnalysis_signalingRole_network_marsilea(...)`, `viz.netAnalysis_signalingRole_scatter(...)`, and `viz.netAnalysis_signalingRole_heatmap(...)` for incoming/outgoing programmes.
8. **Troubleshooting tips**
   - **Metadata alignment**: CellPhoneDB requires a categorical `celltype_key`. If the column contains spaces, mixed casing, or `NaN`, clean it (`adata.obs['cell_labels'] = adata.obs['cell_labels'].astype('category').cat.remove_unused_categories()`).
   - **Database bundle**: `cpdb_file_path` must point to a full CellPhoneDB v5 SQLite zip. If omicverse raises `FileNotFoundError` or missing receptor tables, re-download the bundle from the official release and ensure the zip is not corrupted.
   - **Permutation failures**: Low cell counts per group (<`min_cells`) cause early termination. Increase `min_cell_fraction` thresholds or merge sparse clusters before rerunning.
   - **Palette mismatches**: When colours render incorrectly, rebuild `color_dict` from `adata.uns['cell_labels_colors']` after sorting categories to keep nodes and legends consistent.

## Examples
- "Run CellPhoneDB on our trophoblast dataset and export both the cpdb results pickle and processed AnnData."
- "Highlight significant 'Signaling by Fibroblast growth factor' interactions with chord and bubble plots."
- "Generate outgoing versus incoming communication circles to compare dNK subsets."

## References
- Tutorial notebook: [`t_cellphonedb.ipynb`](../../omicverse_guide/docs/Tutorials-single/t_cellphonedb.ipynb)
- Example data: [`omicverse_guide/docs/Tutorials-single/data/cpdb/`](../../omicverse_guide/docs/Tutorials-single/data/cpdb/)
- Quick copy/paste commands: [`reference.md`](reference.md)
