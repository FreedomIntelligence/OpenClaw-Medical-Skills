# bio-pathway-wikipathways

> WikiPathways enrichment using clusterProfiler and rWikiPathways. Use when analyzing gene lists against community-curated open-source pathways. Performs over-representation analysis and GSEA for 30+ species.

## Version Compatibility

Reference examples tested with: ReactomePA 1.46+, clusterProfiler 4.10+, rWikiPathways 1.24+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# WikiPathways Enrichment

## Core Pattern - Over-Representation Analysis

**Goal:** Identify WikiPathways that are over-represented in a gene list.

**Approach:** Test for enrichment using enrichWP against community-curated open-source pathway definitions.

**"Run pathway enrichment against WikiPathways"** → Test whether genes from community-curated WikiPathways are over-represented among significant genes.

```r
library(clusterProfiler)
library(org.Hs.eg.db)

wp_result <- enrichWP(
    gene = entrez_ids,         # Character vector of Entrez IDs
    organism = 'Homo sapiens', # Full species name
    pvalueCutoff = 0.05,
    pAdjustMethod = 'BH'
)

head(as.data.frame(wp_result))
```

## Prepare Gene List

**Goal:** Extract significant Entrez gene IDs from DE results for WikiPathways enrichment.

**Approach:** Filter by significance thresholds and convert gene symbols to Entrez IDs with bitr.

```r
de_results <- read.csv('de_results.csv')
sig_genes <- de_results[de_results$padj < 0.05 & abs(de_results$log2FoldChange) > 1, 'gene_symbol']

gene_ids <- bitr(sig_genes, fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)
entrez_ids <- gene_ids$ENTREZID
```

## GSEA on WikiPathways

**Goal:** Detect coordinated expression changes in WikiPathways using a ranked gene list.

**Approach:** Sort genes by fold change and run gseWP for rank-based enrichment testing.

```r
# Create ranked gene list
gene_list <- de_results$log2FoldChange
names(gene_list) <- de_results$entrez_id
gene_list <- sort(gene_list, decreasing = TRUE)

gsea_wp <- gseWP(
    geneList = gene_list,
    organism = 'Homo sapiens',
    pvalueCutoff = 0.05,
    pAdjustMethod = 'BH'
)

head(as.data.frame(gsea_wp))
```

## With Background Universe

```r
all_genes <- de_results$entrez_id

wp_result <- enrichWP(
    gene = entrez_ids,
    universe = all_genes,
    organism = 'Homo sapiens',
    pvalueCutoff = 0.05
)
```

## Make Results Readable

```r
# Convert Entrez IDs to gene symbols
wp_readable <- setReadable(wp_result, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID')
```

## Visualization

**Goal:** Create summary plots of WikiPathways enrichment results.

**Approach:** Use enrichplot functions (dotplot, barplot, cnetplot, emapplot) on the enrichment result object.

```r
library(enrichplot)

# Dot plot
dotplot(wp_result, showCategory = 15)

# Bar plot
barplot(wp_result, showCategory = 15)

# Gene-concept network
cnetplot(wp_readable, categorySize = 'pvalue')

# Enrichment map
wp_result <- pairwise_termsim(wp_result)
emapplot(wp_result)
```

## Using rWikiPathways Directly

**Goal:** Query the WikiPathways database directly for pathway metadata, gene lists, and GMT files.

**Approach:** Use rWikiPathways API functions to list organisms, retrieve pathway info, and download gene set definitions.

```r
library(rWikiPathways)

# List available organisms
listOrganisms()

# Get all pathways for an organism
human_pathways <- listPathways('Homo sapiens')

# Get pathway info
pathway_info <- getPathwayInfo('WP554')  # ACE Inhibitor Pathway

# Get genes in a pathway
pathway_genes <- getXrefList('WP554', 'H')  # HGNC symbols
pathway_entrez <- getXrefList('WP554', 'L')  # Entrez IDs

# Download pathway as GMT for custom analysis
downloadPathwayArchive(organism = 'Homo sapiens', format = 'gmt')
```

## Custom GMT-Based Analysis

**Goal:** Run enrichment using a downloaded WikiPathways GMT file for offline or custom analysis.

**Approach:** Download the GMT archive via rWikiPathways, read it with read.gmt, and run enricher.

```r
# Download WikiPathways GMT
library(rWikiPathways)
downloadPathwayArchive(organism = 'Homo sapiens', format = 'gmt', destpath = '.')

# Read GMT and run enrichment
wp_gmt <- read.gmt('wikipathways-Homo_sapiens.gmt')

wp_custom <- enricher(
    gene = entrez_ids,
    TERM2GENE = wp_gmt,
    pvalueCutoff = 0.05
)
```

## Different Organisms

```r
# Mouse
wp_mouse <- enrichWP(gene = mouse_entrez, organism = 'Mus musculus')

# Rat
wp_rat <- enrichWP(gene = rat_entrez, organism = 'Rattus norvegicus')

# Zebrafish
wp_zfish <- enrichWP(gene = zfish_entrez, organism = 'Danio rerio')

# List all available organisms
library(rWikiPathways)
listOrganisms()
```

## Compare Clusters

**Goal:** Compare WikiPathways enrichment across multiple gene lists (e.g., upregulated vs downregulated).

**Approach:** Use compareCluster with enrichWP to run enrichment per group and visualize with dotplot.

```r
gene_clusters <- list(
    upregulated = up_genes,
    downregulated = down_genes
)

compare_wp <- compareCluster(
    geneClusters = gene_clusters,
    fun = 'enrichWP',
    organism = 'Homo sapiens',
    pvalueCutoff = 0.05
)

dotplot(compare_wp)
```

## Export Results

```r
results_df <- as.data.frame(wp_result)
write.csv(results_df, 'wikipathways_enrichment.csv', row.names = FALSE)
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| gene | required | Vector of Entrez IDs |
| organism | required | Full species name |
| pvalueCutoff | 0.05 | P-value threshold |
| pAdjustMethod | BH | Adjustment method |
| universe | NULL | Background genes |
| minGSSize | 10 | Min genes per pathway |
| maxGSSize | 500 | Max genes per pathway |

## Common Organisms

| Common Name | Scientific Name |
|-------------|-----------------|
| Human | Homo sapiens |
| Mouse | Mus musculus |
| Rat | Rattus norvegicus |
| Zebrafish | Danio rerio |
| Fruit fly | Drosophila melanogaster |
| C. elegans | Caenorhabditis elegans |
| Arabidopsis | Arabidopsis thaliana |
| Yeast | Saccharomyces cerevisiae |

## WikiPathways vs Other Databases

| Feature | WikiPathways | KEGG | Reactome |
|---------|--------------|------|----------|
| Curation | Community | Expert | Peer-reviewed |
| License | Open (CC0) | Commercial | Open |
| Species | 30+ | 4000+ | 7 |
| Focus | Disease, drug | Metabolic | Signaling |
| Updates | Continuous | Ongoing | Quarterly |

## Related Skills

- go-enrichment - Gene Ontology enrichment
- kegg-pathways - KEGG pathway enrichment
- reactome-pathways - Reactome pathway enrichment
- gsea - Gene Set Enrichment Analysis
- enrichment-visualization - Visualization functions
