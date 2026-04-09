# bio-pathway-gsea

> Gene Set Enrichment Analysis using clusterProfiler gseGO and gseKEGG. Use when analyzing ranked gene lists to find coordinated expression changes in gene sets without arbitrary significance cutoffs. Detects subtle but coordinated expression changes.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Gene Set Enrichment Analysis (GSEA)

## Core Concept

GSEA uses **all genes ranked by a statistic** (log2FC, signed p-value) rather than a subset of significant genes. It finds gene sets where members are enriched at the top or bottom of the ranked list.

## Prepare Ranked Gene List

**Goal:** Create a sorted named vector of gene-level statistics suitable for GSEA input.

**Approach:** Extract fold changes (or other statistics) from DE results, name by gene ID, and sort in decreasing order.

**"Run GSEA on my differential expression results"** → Rank all genes by expression statistic and test whether predefined gene sets cluster toward the extremes of the ranked list.

```r
library(clusterProfiler)
library(org.Hs.eg.db)

de_results <- read.csv('de_results.csv')

# Create named vector: values = statistic, names = gene IDs
gene_list <- de_results$log2FoldChange
names(gene_list) <- de_results$gene_id

# Sort in decreasing order (REQUIRED)
gene_list <- sort(gene_list, decreasing = TRUE)
```

## Convert Gene IDs for GSEA

**Goal:** Map gene symbols to Entrez IDs while preserving the ranked statistic values.

**Approach:** Use bitr for ID conversion, then rebuild the named sorted vector with Entrez IDs as names.

```r
# Convert symbols to Entrez IDs
gene_ids <- bitr(names(gene_list), fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)

# Create ranked list with Entrez IDs
gene_list_entrez <- gene_list[names(gene_list) %in% gene_ids$SYMBOL]
names(gene_list_entrez) <- gene_ids$ENTREZID[match(names(gene_list_entrez), gene_ids$SYMBOL)]
gene_list_entrez <- sort(gene_list_entrez, decreasing = TRUE)
```

## Alternative Ranking Statistics

**Goal:** Choose a ranking metric that balances magnitude and significance for GSEA.

**Approach:** Use signed p-value (-log10(p) * sign(FC)) or Wald statistic as alternatives to raw log2 fold change.

```r
# Signed p-value (recommended for detecting both up and down)
gene_list <- -log10(de_results$pvalue) * sign(de_results$log2FoldChange)
names(gene_list) <- de_results$gene_id
gene_list <- sort(gene_list, decreasing = TRUE)

# Wald statistic (from DESeq2)
gene_list <- de_results$stat
names(gene_list) <- de_results$gene_id
gene_list <- sort(gene_list, decreasing = TRUE)
```

## GSEA with GO

**Goal:** Detect coordinated expression changes across GO gene sets without requiring a significance cutoff.

**Approach:** Run gseGO on a ranked gene list, testing whether GO term members are enriched at the top or bottom of the list.

```r
gse_go <- gseGO(
    geneList = gene_list_entrez,
    OrgDb = org.Hs.eg.db,
    ont = 'BP',                     # BP, MF, CC, or ALL
    minGSSize = 10,
    maxGSSize = 500,
    pvalueCutoff = 0.05,
    verbose = FALSE,
    pAdjustMethod = 'BH'
)

# Make readable
gse_go <- setReadable(gse_go, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID')
```

## GSEA with KEGG

**Goal:** Identify KEGG pathways with coordinated expression changes across all genes.

**Approach:** Run gseKEGG on the ranked gene list using KEGG pathway definitions.

```r
gse_kegg <- gseKEGG(
    geneList = gene_list_entrez,
    organism = 'hsa',
    minGSSize = 10,
    maxGSSize = 500,
    pvalueCutoff = 0.05,
    verbose = FALSE
)

# Make readable
gse_kegg <- setReadable(gse_kegg, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID')
```

## GSEA with Custom Gene Sets

**Goal:** Run GSEA against user-provided or non-standard gene set collections.

**Approach:** Load a GMT file and use the generic GSEA function with TERM2GENE mapping.

```r
# Read GMT file (Gene Matrix Transposed)
gene_sets <- read.gmt('msigdb_hallmarks.gmt')

gse_custom <- GSEA(
    geneList = gene_list_entrez,
    TERM2GENE = gene_sets,
    minGSSize = 10,
    maxGSSize = 500,
    pvalueCutoff = 0.05
)
```

## MSigDB Gene Sets

**Goal:** Run GSEA using curated gene set collections from the Molecular Signatures Database.

**Approach:** Retrieve gene sets via msigdbr, format as TERM2GENE data frame, and run GSEA.

```r
# Use msigdbr package for MSigDB gene sets
library(msigdbr)

# Hallmark gene sets
hallmarks <- msigdbr(species = 'Homo sapiens', category = 'H')
hallmarks_t2g <- hallmarks[, c('gs_name', 'entrez_gene')]

gse_hallmark <- GSEA(
    geneList = gene_list_entrez,
    TERM2GENE = hallmarks_t2g,
    pvalueCutoff = 0.05
)

# Other categories: C1 (positional), C2 (curated), C3 (motif), C5 (GO), C6 (oncogenic), C7 (immunologic)
```

## Understanding Results

```r
# View results
head(gse_go)
results <- as.data.frame(gse_go)

# Key columns:
# - NES: Normalized Enrichment Score (positive = upregulated, negative = downregulated)
# - pvalue: Nominal p-value
# - p.adjust: FDR-adjusted p-value
# - core_enrichment: Leading edge genes
```

## Interpreting NES (Normalized Enrichment Score)

| NES | Interpretation |
|-----|----------------|
| Positive (> 0) | Gene set enriched in upregulated genes |
| Negative (< 0) | Gene set enriched in downregulated genes |
| |NES| > 1.5 | Strong enrichment |

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| geneList | required | Named, sorted numeric vector |
| OrgDb | required | Organism database (for gseGO) |
| organism | hsa | KEGG organism code (for gseKEGG) |
| ont | BP | Ontology: BP, MF, CC, ALL |
| minGSSize | 10 | Min genes in gene set |
| maxGSSize | 500 | Max genes in gene set |
| pvalueCutoff | 0.05 | P-value threshold |
| pAdjustMethod | BH | Adjustment method |
| nPerm | 10000 | Permutations (if permutation test used) |
| eps | 1e-10 | Boundary for p-value calculation |

## Export Results

**Goal:** Save GSEA results and extract leading edge genes for downstream analysis.

**Approach:** Convert enrichment object to data frame, export to CSV, and parse core_enrichment for driving genes.

```r
results_df <- as.data.frame(gse_go)
write.csv(results_df, 'gsea_go_results.csv', row.names = FALSE)

# Get leading edge genes for a term
leading_edge <- strsplit(results_df$core_enrichment[1], '/')[[1]]
```

## Notes

- **Must be sorted** - gene list must be sorted in decreasing order
- **Named vector** - names are gene IDs, values are statistics
- **No arbitrary cutoffs** - uses all genes, not just significant ones
- **NES sign matters** - positive = upregulated enrichment
- **Leading edge** - core_enrichment contains driving genes

## Related Skills

- go-enrichment - Over-representation analysis for GO
- kegg-pathways - Over-representation analysis for KEGG
- enrichment-visualization - GSEA plots, ridge plots
