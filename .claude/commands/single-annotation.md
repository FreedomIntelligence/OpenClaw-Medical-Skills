# single-cell-annotation-skills-with-omicverse

> Guide Claude through SCSA, MetaTiME, CellVote, CellMatch, GPTAnno, and weighted KNN transfer workflows for annotating single-cell modalities.

# Single-cell annotation skills with omicverse

## Overview
Use this skill to reproduce and adapt the single-cell annotation playbook captured in omicverse tutorials: SCSA [`t_cellanno.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_cellanno.ipynb), MetaTiME [`t_metatime.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_metatime.ipynb), CellVote [`t_cellvote.md`](../../../omicverse_guide/docs/Tutorials-single/t_cellvote.md) & [`t_cellvote_pbmc3k.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_cellvote_pbmc3k.ipynb), CellMatch [`t_cellmatch.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_cellmatch.ipynb), GPTAnno [`t_gptanno.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_gptanno.ipynb), and label transfer [`t_anno_trans.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_anno_trans.ipynb). Each section below highlights required inputs, training/inference steps, and how to read the outputs.

## Instructions
1. **SCSA automated cluster annotation**
   - *Data requirements*: PBMC3k raw counts from 10x Genomics (`pbmc3k_filtered_gene_bc_matrices.tar.gz`) or the processed `sample/rna.h5ad`. Download instructions are embedded in the notebook; unpack to `data/filtered_gene_bc_matrices/hg19/`. Ensure an SCSA SQLite database is available (e.g. `pySCSA_2024_v1_plus.db` from the Figshare/Drive links listed in the tutorial) and point `model_path` to its location.
   - *Preprocessing & model fit*: Load with `sc.read_10x_mtx`, run QC (`ov.pp.qc`), normalization and HVG selection (`ov.pp.preprocess`), scaling (`ov.pp.scale`), PCA (`ov.pp.pca`), neighbors, Leiden clustering, and compute rank markers (`sc.tl.rank_genes_groups`). Instantiate `scsa = ov.single.pySCSA(...)` choosing `target='cellmarker'` or `'panglaodb'`, tissue scope, and thresholds (`foldchange`, `pvalue`).
   - *Inference & interpretation*: Call `scsa.cell_anno(clustertype='leiden', result_key='scsa_celltype_cellmarker')` or `scsa.cell_auto_anno` to append predictions to `adata.obs`. Compare to manual marker-based labels via `ov.utils.embedding` or `sc.pl.dotplot`, inspect marker dictionaries (`ov.single.get_celltype_marker`), and query supported tissues with `scsa.get_model_tissue()`. Use the ROI/ROE helpers (`ov.utils.roe`, `ov.utils.plot_cellproportion`) to validate abundance trends.

2. **MetaTiME tumour microenvironment states**
   - *Data requirements*: Batched TME AnnData with an scVI latent embedding. The tutorial uses `TiME_adata_scvi.h5ad` from Figshare (`https://figshare.com/ndownloader/files/41440050`). If starting from counts, run scVI (`scvi.model.SCVI`) first to populate `adata.obsm['X_scVI']`.
   - *Preprocessing & model fit*: Optionally subset to non-malignant cells via `adata.obs['isTME']`. Rebuild neighbors on the latent representation (`sc.pp.neighbors(adata, use_rep="X_scVI")`) and embed with pymde (`adata.obsm['X_mde'] = ov.utils.mde(...)`). Initialise `TiME_object = ov.single.MetaTiME(adata, mode='table')` and, if finer granularity is desired, over-cluster with `TiME_object.overcluster(resolution=8, clustercol='overcluster')`.
   - *Inference & interpretation*: Run `TiME_object.predictTiME(save_obs_name='MetaTiME')` to assign minor states and `Major_MetaTiME`. Visualise using `TiME_object.plot` or `sc.pl.embedding`. Interpret the outputs by comparing cluster-level distributions and confirming that MetaTiME and Major_MetaTiME columns align with expected niches.

3. **CellVote consensus labelling**
   - *Data requirements*: A clustered AnnData (e.g. PBMC3k stored as `CELLVOTE_PBMC3K` env var or `data/pbmc3k.h5ad`) plus at least two precomputed annotation columns (simulated in the tutorial as `scsa_annotation`, `gpt_celltype`, `gbi_celltype`). Prepare per-cluster marker genes via `sc.tl.rank_genes_groups`.
   - *Preprocessing & model fit*: After standard preprocessing (normalize, log1p, HVGs, PCA, neighbors, Leiden) build a marker dictionary `marker_dict = top_markers_from_rgg(adata, 'leiden', topn=10)` or via `ov.single.get_celltype_marker`. Instantiate `cv = ov.single.CellVote(adata)`.
   - *Inference & interpretation*: Call `cv.vote(clusters_key='leiden', cluster_markers=marker_dict, celltype_keys=[...], species='human', organization='PBMC', provider='openai', model='gpt-4o-mini')`. Offline examples monkey-patch arbitration to avoid API calls; online voting requires valid credentials. Final consensus labels live in `adata.obs['CellVote_celltype']`. Compare each cluster’s majority vote with the input sources (`adata.obs[['leiden', 'scsa_annotation', ...]]`) to justify decisions.

4. **CellMatch ontology mapping**
   - *Data requirements*: Annotated AnnData such as `pertpy.dt.haber_2017_regions()` with `adata.obs['cell_label']`. Download Cell Ontology JSON (`cl.json`) via `ov.single.download_cl(...)` or manual links, and optionally Cell Taxonomy resources (`Cell_Taxonomy_resource.txt`). Ensure access to a SentenceTransformer model (`sentence-transformers/all-MiniLM-L6-v2`, `BAAI/bge-base-en-v1.5`, etc.), downloading to `local_model_dir` if offline.
   - *Preprocessing & model fit*: Create the mapper with `ov.single.CellOntologyMapper(cl_obo_file='new_ontology/cl.json', model_name='sentence-transformers/all-MiniLM-L6-v2', local_model_dir='./my_models')`. Run `mapper.map_adata(...)` to assign ontology-derived labels/IDs, optionally enabling taxonomy matching (`use_taxonomy=True` after calling `load_cell_taxonomy_resource`).
   - *Inference & interpretation*: Explore mapping summaries (`mapper.print_mapping_summary_taxonomy`) and inspect embeddings coloured by `cell_ontology`, `cell_ontology_cl_id`, or `enhanced_cell_ontology`. Use helper queries such as `mapper.find_similar_cells('T helper cell')`, `mapper.get_cell_info(...)`, and category browsing to validate ontology coverage.

5. **GPTAnno LLM-powered annotation**
   - *Data requirements*: The same PBMC3k dataset (raw matrix or `.h5ad`) and cluster assignments. Access to an LLM endpoint—configure `AGI_API_KEY` for OpenAI-compatible providers (`provider='openai'`, `'qwen'`, `'kimi'`, etc.), or supply a local model path for `ov.single.gptcelltype_local`.
   - *Preprocessing & model fit*: Follow the QC, normalization, HVG, scaling, PCA, neighbor, Leiden, and marker discovery steps described above (reusing outputs from the SCSA workflow). Build the marker dictionary automatically with `ov.single.get_celltype_marker(adata, clustertype='leiden', rank=True, key='rank_genes_groups', foldchange=2, topgenenumber=5)`.
   - *Inference & interpretation*: Invoke `ov.single.gptcelltype(...)` specifying tissue/species context and desired provider/model. Post-process responses to keep clean labels (`result[key].split(': ')[-1]...`) and write them to `adata.obs['gpt_celltype']`. Compare embeddings (`ov.pl.embedding(..., color=['leiden','gpt_celltype'])`) to verify cluster identities. If operating offline, call `ov.single.gptcelltype_local` with a downloaded instruction-tuned checkpoint.

6. **Weighted KNN annotation transfer**
   - *Data requirements*: Cross-modal GLUE outputs with aligned embeddings, e.g. `data/analysis_lymph/rna-emb.h5ad` (annotated RNA) and `data/analysis_lymph/atac-emb.h5ad` (query ATAC) where both contain `obsm['X_glue']`.
   - *Preprocessing & model fit*: Load both modalities, optionally concatenate for QC plots, and compute a shared low-dimensional embedding with `ov.utils.mde`. Train a neighbour model using `ov.utils.weighted_knn_trainer(train_adata=rna, train_adata_emb='X_glue', n_neighbors=15)`.
   - *Inference & interpretation*: Transfer labels via `labels, uncert = ov.utils.weighted_knn_transfer(query_adata=atac, query_adata_emb='X_glue', label_keys='major_celltype', knn_model=knn_transformer, ref_adata_obs=rna.obs)`. Store predictions in `atac.obs['transf_celltype']` and uncertainties in `atac.obs['transf_celltype_unc']`; copy to `major_celltype` if you want consistent naming. Visualise (`ov.utils.embedding`) and inspect uncertainty to flag ambiguous cells.

## Critical API Reference - EXACT Function Signatures

### pySCSA - IMPORTANT: Parameter is `clustertype`, NOT `cluster`

**CORRECT usage:**
```python
# Step 1: Initialize pySCSA
scsa = ov.single.pySCSA(
    adata,
    foldchange=1.5,
    pvalue=0.01,
    species='Human',
    tissue='All',
    target='cellmarker'  # or 'panglaodb'
)

# Step 2: Run annotation - NOTE: use clustertype='leiden', NOT cluster='leiden'!
anno_result = scsa.cell_anno(clustertype='leiden', cluster='all')

# Step 3: Add cell type labels to adata.obs
scsa.cell_auto_anno(adata, clustertype='leiden', key='scsa_celltype')
# Results are stored in adata.obs['scsa_celltype']
```

**WRONG - DO NOT USE:**
```python
# WRONG! 'cluster' is NOT a valid parameter for cell_auto_anno!
# scsa.cell_auto_anno(adata, cluster='leiden')  # ERROR!
```

### COSG Marker Genes - Results stored in adata.uns, NOT adata.obs

**CORRECT usage:**
```python
# Step 1: Run COSG marker gene identification
ov.single.cosg(adata, groupby='leiden', n_genes_user=50)

# Step 2: Access results from adata.uns (NOT adata.obs!)
marker_names = adata.uns['rank_genes_groups']['names']  # DataFrame with cluster columns
marker_scores = adata.uns['rank_genes_groups']['scores']

# Step 3: Get top markers for specific cluster
cluster_0_markers = adata.uns['rank_genes_groups']['names']['0'][:10].tolist()

# Step 4: To create celltype column, manually map clusters to cell types
cluster_to_celltype = {
    '0': 'T cells',
    '1': 'B cells',
    '2': 'Monocytes',
}
adata.obs['cosg_celltype'] = adata.obs['leiden'].map(cluster_to_celltype)
```

**WRONG - DO NOT USE:**
```python
# WRONG! COSG does NOT create adata.obs columns directly!
# adata.obs['cosg_celltype']  # This key does NOT exist after running COSG!
# adata.uns['cosg_celltype']  # This key also does NOT exist!
```

### Common Pitfalls to Avoid

1. **pySCSA parameter confusion**:
   - `clustertype` = which obs column contains cluster labels (e.g., 'leiden')
   - `cluster` = which specific clusters to annotate ('all' or specific cluster IDs)
   - These are DIFFERENT parameters!

2. **COSG result access**:
   - COSG is a marker gene finder, NOT a cell type annotator
   - Results are per-cluster gene rankings stored in `adata.uns['rank_genes_groups']`
   - To assign cell types, you must manually map clusters to cell types based on markers

3. **Result storage patterns in OmicVerse**:
   - Cell type annotations → `adata.obs['<key>']`
   - Marker gene results → `adata.uns['<key>']` (includes 'names', 'scores', 'logfoldchanges')
   - Differential expression → `adata.uns['rank_genes_groups']`

## Examples
- "Run SCSA with both CellMarker and PanglaoDB references on PBMC3k, then benchmark against manual marker assignments before feeding the results into CellVote."
- "Annotate tumour microenvironment states in the MetaTiME Figshare dataset, highlight Major_MetaTiME classes, and export the label distribution per patient."
- "Download Cell Ontology resources, map `haber_2017_regions` clusters to ontology terms, and enrich ambiguous clusters using Cell Taxonomy hints."
- "Propagate RNA-derived `major_celltype` labels onto GLUE-integrated ATAC cells and report clusters with high transfer uncertainty."

## References
- Tutorials and notebooks: [`t_cellanno.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_cellanno.ipynb), [`t_metatime.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_metatime.ipynb), [`t_cellvote.md`](../../../omicverse_guide/docs/Tutorials-single/t_cellvote.md), [`t_cellvote_pbmc3k.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_cellvote_pbmc3k.ipynb), [`t_cellmatch.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_cellmatch.ipynb), [`t_gptanno.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_gptanno.ipynb), [`t_anno_trans.ipynb`](../../../omicverse_guide/docs/Tutorials-single/t_anno_trans.ipynb).
- Sample data & assets: PBMC3k matrix from 10x Genomics, MetaTiME `TiME_adata_scvi.h5ad` (Figshare), SCSA database downloads, GLUE embeddings under `data/analysis_lymph/`, Cell Ontology `cl.json`, and Cell Taxonomy resource.
- Quick copy commands: [`reference.md`](reference.md).
