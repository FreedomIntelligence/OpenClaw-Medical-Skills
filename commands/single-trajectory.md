# single-trajectory-analysis

> Guide to reproducing OmicVerse trajectory workflows spanning PAGA, Palantir, VIA, velocity coupling, and fate scoring notebooks.

# Single-trajectory analysis skill

## Overview
This skill describes how to reproduce and extend the single-trajectory analysis workflow in `omicverse`, combining graph-based trajectory inference, RNA velocity coupling, and downstream fate scoring notebooks.

## Trajectory setup
- **PAGA (Partition-based graph abstraction)**
  - Build a neighborhood graph (`pp.neighbors`) on the preprocessed AnnData object.
  - Use `tl.paga` to compute cluster connectivity and `tl.draw_graph` or `tl.umap` with `init_pos='paga'` for embedding.
  - Interpret edge weights to prioritize branch resolution and seed paths.
- **Palantir**
  - Run `Palantir` on diffusion components, seeding with manually selected start cells (e.g., naïve T cells).
  - Extract pseudotime, branch probabilities, and differentiation potential for subsequent overlays.
- **VIA**
  - Execute `via.VIA` on the kNN graph to identify lineage progression with automatic root selection or user-defined roots.
  - Export terminal states and pseudotime for cross-validation against PAGA and Palantir results.

## Velocity coupling (VIA + scVelo)
- Use `scv.pp.filter_and_normalize`, `scv.pp.moments`, and `scv.tl.velocity` to generate velocity layers.
- Provide VIA with `adata.layers['velocity']` to refine lineage directionality (`via.VIA(..., velocity_weight=...)`).
- Compare VIA pseudotime with scVelo latent time (`scv.tl.latent_time`) to validate directionality and root selection.

## Downstream fate scoring notebooks
- **`t_cellfate*.ipynb`**: Map lineage probabilities onto T-cell subsets, quantify fate bias, and visualize heatmaps.
- **`t_metacells.ipynb`**: Aggregate metacell trajectories for robustness checks and meta-state differential expression.
- **`t_cytotrace.ipynb`**: Integrate CytoTRACE differentiation potential with velocity-informed lineages for maturation scoring.

## Required preprocessing
1. Quality control: remove low-quality cells/genes, apply doublet filtering.
2. Normalization & log transformation (`sc.pp.normalize_total`, `sc.pp.log1p`).
3. Highly variable gene selection tailored to immune datasets (`sc.pp.highly_variable_genes`).
4. Batch correction if necessary (e.g., `scvi-tools`, `bbknn`).
5. Compute PCA, neighbor graph, and embedding (UMAP/FA) used by all trajectory methods.
6. For velocity: compute moments on the same neighbor graph before running VIA coupling.

## Parameter tuning
- Neighbor graph `n_neighbors` and `n_pcs` should be harmonized across PAGA, VIA, and Palantir to maintain consistency.
- In VIA, adjust `knn`, `too_big_factor`, and `root_user` for datasets with uneven sampling.
- Palantir requires careful start cell selection; use marker genes and velocity arrows to confirm.
- For PAGA, tweak `threshold` to control edge sparsity; ensure connected components reflect biological branches.
- Velocity estimation: compare `mode='stochastic'` vs `mode='dynamical'` in scVelo; recalibrate if terminal states disagree with VIA.

## Visualization and export
1. Overlay PAGA edges on UMAP (`scv.pl.paga`) and annotate branch labels.
2. Plot Palantir pseudotime and branch probabilities on embeddings.
3. Visualize VIA trajectories using `via.plot_fates` and `via.plot_scatter`.
4. Export pseudotime tables and fate probabilities to CSV for downstream notebooks.
5. Save high-resolution figures (PNG/SVG) and notebook artifacts for reproducibility.
6. Update notebooks with consistent color schemes and metadata columns before sharing.

## Troubleshooting tips
- **Missing velocity layers**: re-run `scv.pp.moments` and `scv.tl.velocity` ensuring `adata.layers['spliced']`/`['unspliced']` exist; verify loom/H5AD import preserved layers.
- **Disconnected PAGA graph**: inspect neighbor graph or adjust `n_neighbors`; confirm batch correction didn’t fragment the manifold.
- **Palantir convergence issues**: reduce diffusion components or reinitialize start cells; ensure no NaN values in data matrix.
- **VIA terminal states unstable**: increase iterations (`cluster_graph_pruning_iter`), or provide manual terminal state hints based on marker expression.
- **Notebook kernel memory errors**: downsample cells or precompute summaries (metacells) before rerunning.
