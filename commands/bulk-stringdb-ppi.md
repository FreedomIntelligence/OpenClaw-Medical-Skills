# string-protein-interaction-analysis-with-omicverse

> Help Claude query STRING for protein interactions, build PPI graphs with pyPPI, and render styled network figures for bulk gene lists.

# STRING protein interaction analysis with omicverse

## Overview
Invoke this skill when the user has a list of genes and wants to explore STRING protein–protein interactions via omicverse. The
 workflow mirrors [`t_network.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_network.ipynb), covering species selection, S
TRING API queries, and quick visualisation of the resulting network.

## Instructions
1. **Set up libraries**
   - Import `omicverse as ov` and call `ov.utils.ov_plot_set()` (or `ov.plot_set()`) to match omicverse aesthetics.
2. **Collect gene inputs**
   - Accept a curated list of gene symbols (`gene_list = [...]`).
   - Encourage the user to flag priority genes or categories so you can colour-code groups in the plot.
3. **Assign metadata for plotting**
   - Build dictionaries mapping genes to types and colours, e.g. `gene_type_dict = dict(zip(gene_list, ['Type1']*5 + ['Type2']*6
))` and `gene_color_dict = {...}`.
   - Remind users that consistent group labels improve legend readability.
4. **Query STRING interactions**
   - Call `ov.bulk.string_interaction(gene_list, species_id)` where `species_id` is the NCBI taxonomy ID (e.g. 4932 for yeast).
   - Inspect the resulting DataFrame for combined scores and evidence channels to verify coverage.
5. **Construct the network object**
   - Initialise `ppi = ov.bulk.pyPPI(gene=gene_list, gene_type_dict=..., gene_color_dict=..., species=species_id)`.
   - Run `ppi.interaction_analysis()` to fetch and cache STRING edges.
6. **Visualise the network**
   - Generate a default plot with `ppi.plot_network()` to reproduce the notebook figure.
   - Mention that advanced styling (layout, node size, legends) can be tuned through `ov.utils.plot_network` keyword arguments if
 the user requests adjustments.
7. **Troubleshooting**
   - Ensure gene symbols match the species—STRING expects case-sensitive identifiers; suggest mapping Ensembl IDs to symbols when
 queries fail.
   - If the API rate-limits, instruct the user to wait or provide a cached interaction table.
   - For missing interactions, recommend enabling STRING's "add_nodes" option via `ppi.interaction_analysis(add_nodes=...)` to exp
and the network.

## Examples
- "Retrieve STRING interactions for FAA4 and plot the network highlighting two gene classes."
- "Download the STRING edge table for my Saccharomyces cerevisiae gene panel and colour nodes by module."
- "Extend the network by adding the top five predicted partners before plotting."

## References
- Tutorial notebook: [`t_network.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_network.ipynb)
- STRING background: [string-db.org](https://string-db.org/)
- Quick copy/paste commands: [`reference.md`](reference.md)
