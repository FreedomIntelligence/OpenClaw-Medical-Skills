# bulk-wgcna-analysis-with-omicverse

> Assist Claude in running PyWGCNA through omicverse—preprocessing expression matrices, constructing co-expression modules, visualising eigengenes, and extracting hub genes.

# Bulk WGCNA analysis with omicverse

## Overview
Activate this skill for users who want to reproduce the WGCNA workflow from [`t_wgcna.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_wgcna.ipynb). It guides you through loading expression data, configuring PyWGCNA, constructing weighted gene co-expression networks, and inspecting modules of interest.

## Instructions
1. **Prepare the environment**
   - Import `omicverse as ov`, `scanpy as sc`, `matplotlib.pyplot as plt`, and `pandas as pd`.
   - Set plotting defaults via `ov.plot_set()`.
2. **Load and filter expression data**
   - Read expression matrices (e.g., from `expressionList.csv`).
   - Calculate median absolute deviation with `from statsmodels import robust` and `gene_mad = data.apply(robust.mad)`.
   - Keep the top variable genes (e.g., `data = data.T.loc[gene_mad.sort_values(ascending=False).index[:2000]]`).
3. **Initialise PyWGCNA**
   - Create `pyWGCNA_5xFAD = ov.bulk.pyWGCNA(name=..., species='mus musculus', geneExp=data.T, outputPath='', save=True)`.
   - Confirm `pyWGCNA_5xFAD.geneExpr` looks correct before proceeding.
4. **Preprocess the dataset**
   - Run `pyWGCNA_5xFAD.preprocess()` to drop low-expression genes and problematic samples.
5. **Construct the co-expression network**
   - Evaluate soft-threshold power: `pyWGCNA_5xFAD.calculate_soft_threshold()`.
   - Build adjacency and TOM matrices via `calculating_adjacency_matrix()` and `calculating_TOM_similarity_matrix()`.
6. **Detect gene modules**
   - Generate dendrograms and modules: `calculate_geneTree()`, `calculate_dynamicMods(kwargs_function={'cutreeHybrid': {...}})`.
   - Derive module eigengenes with `calculate_gene_module(kwargs_function={'moduleEigengenes': {'softPower': 8}})`.
   - Visualise adjacency/TOM heatmaps using `plot_matrix(save=False)` if needed.
7. **Inspect specific modules**
   - Extract genes from modules with `get_sub_module([...], mod_type='module_color')`.
   - Build sub-networks using `get_sub_network(mod_list=[...], mod_type='module_color', correlation_threshold=0.2)` and plot them via `plot_sub_network(...)`.
8. **Update sample metadata for downstream analyses**
   - Load sample annotations `updateSampleInfo(path='.../sampleInfo.csv', sep=',')`.
   - Assign colour maps for metadata categories with `setMetadataColor(...)`.
9. **Analyse module–trait relationships**
   - Run `analyseWGCNA()` to compute module–trait statistics.
   - Plot module eigengene heatmaps and bar charts with `plotModuleEigenGene(module, metadata, show=True)` and `barplotModuleEigenGene(...)`.
10. **Find hub genes**
    - Identify top hubs per module using `top_n_hub_genes(moduleName='lightgreen', n=10)`.
11. **Troubleshooting tips**
    - Large datasets may require increasing `save=False` to avoid writing many intermediate files.
    - If module detection fails, confirm enough genes remain after MAD filtering and adjust `deepSplit` or `softPower`.
    - Ensure metadata categories have assigned colours before plotting eigengene heatmaps.

## Examples
- "Build a WGCNA network on the 5xFAD dataset, visualise modules, and extract hub genes from the lightgreen module."
- "Load sample metadata, update colours for sex and genotype, and plot module eigengene heatmaps."
- "Create a sub-network plot for the gold module using a correlation threshold of 0.2."

## References
- Tutorial notebook: [`t_wgcna.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_wgcna.ipynb)
- Tutorial dataset: [`data/5xFAD_paper/`](../../omicverse_guide/docs/Tutorials-bulk/data/5xFAD_paper/)
- Quick copy/paste commands: [`reference.md`](reference.md)
