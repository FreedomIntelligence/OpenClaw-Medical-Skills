# bulk-rna-seq-deseq2-analysis-with-omicverse

> Walk Claude through PyDESeq2-based differential expression, including ID mapping, DE testing, fold-change thresholding, and enrichment visualisation.

# Bulk RNA-seq DESeq2 analysis with omicverse

## Overview
Use this skill when a user wants to reproduce the DESeq2 workflow showcased in [`t_deseq2.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_deseq2.ipynb). It covers loading raw featureCounts matrices, mapping Ensembl IDs to symbols, running PyDESeq2 via `ov.bulk.pyDEG`, and exploring downstream enrichment plots.

## Instructions
1. **Import and format the expression matrix**
   - Call `import omicverse as ov` and `ov.utils.ov_plot_set()` to standardise visuals.
   - Read tab-separated count data from featureCounts using `ov.utils.read(..., index_col=0, header=1)`.
   - Strip trailing `.bam` from column names with `[c.split('/')[-1].replace('.bam', '') for c in data.columns]`.
2. **Map gene identifiers**
   - Ensure the appropriate mapping pair exists by running `ov.utils.download_geneid_annotation_pair()`.
   - Replace `gene_id` with gene symbols using `ov.bulk.Matrix_ID_mapping(data, 'genesets/pair_<GENOME>.tsv')`.
3. **Initialise the DEG object**
   - Create `dds = ov.bulk.pyDEG(data)` from the mapped counts.
   - Resolve duplicate gene names with `dds.drop_duplicates_index()` and confirm success in logs.
4. **Define contrasts and run DESeq2**
   - Collect sample labels into `treatment_groups` and `control_groups` lists that match column names exactly.
   - Execute `dds.deg_analysis(treatment_groups, control_groups, method='DEseq2')` to invoke PyDESeq2.
5. **Filter and tune thresholds**
   - Inspect result shape (`dds.result.shape`) and optionally filter low-expression genes, e.g. `dds.result.loc[dds.result['log2(BaseMean)'] > 1]`.
   - Set thresholds via `dds.foldchange_set(fc_threshold=-1, pval_threshold=0.05, logp_max=6)` to auto-pick fold-change cutoffs.
6. **Visualise differential genes**
   - Draw volcano plots with `dds.plot_volcano(...)` and summarise key genes.
   - Produce per-gene boxplots: `dds.plot_boxplot(genes=[...], treatment_groups=..., control_groups=..., figsize=(2, 3))`.
7. **Run enrichment analyses (optional)**
   - Download enrichment libraries using `ov.utils.download_pathway_database()` and load them through `ov.utils.geneset_prepare`.
   - Rank genes for GSEA with `rnk = dds.ranking2gsea()`.
   - Instantiate `gsea_obj = ov.bulk.pyGSEA(rnk, pathway_dict)` and call `gsea_obj.enrichment()` to compute terms.
   - Plot enrichment bubble charts via `gsea_obj.plot_enrichment(...)` and GSEA curves with `gsea_obj.plot_gsea(term_num=..., ...)`.
8. **Troubleshooting**
   - If PyDESeq2 raises errors about size factors, remind users to provide raw counts (not log-transformed data).
   - `gene_id` mapping depends on species; direct them to download the correct genome pair when results look sparse.
   - Large pathway libraries may require raising recursion limits or filtering to the top N terms before plotting.

## Examples
- "Run PyDESeq2 on treated vs control replicates and highlight the top enriched WikiPathways terms."
- "Filter DEGs to genes with log2(BaseMean) > 1, auto-select fold-change cutoffs, and create volcano and boxplots."
- "Generate the ranked gene list for GSEA and plot the enrichment curve for the top pathway."

## References
- Tutorial notebook: [`t_deseq2.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_deseq2.ipynb)
- Sample featureCounts matrix: [`sample/counts.txt`](../../sample/counts.txt)
- Quick copy/paste commands: [`reference.md`](reference.md)
