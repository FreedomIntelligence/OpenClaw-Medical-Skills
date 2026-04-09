# bio-pathway-enrichment-visualization

> Visualize enrichment results using enrichplot package functions. Use when creating publication-quality figures from clusterProfiler results. Covers dotplot, barplot, cnetplot, emapplot, gseaplot2, ridgeplot, and treeplot.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Enrichment Visualization

**"Create publication-quality plots from my enrichment analysis"** → Generate dotplots, gene-concept networks, enrichment maps, GSEA running score plots, and ridgeplots from clusterProfiler results.
- R: `dotplot()`, `cnetplot()`, `emapplot()`, `gseaplot2()` (enrichplot)

## Scope

This skill covers **enrichplot package functions** designed for clusterProfiler results:
- `dotplot()`, `barplot()` - Summary views
- `cnetplot()`, `emapplot()`, `treeplot()` - Network/hierarchical views
- `gseaplot2()`, `ridgeplot()` - GSEA-specific
- `goplot()`, `heatplot()`, `upsetplot()` - Specialized views

**For custom ggplot2 enrichment dotplots** (manual implementation), see `data-visualization/specialized-omics-plots`.

## Setup

**Goal:** Load required packages for visualizing enrichment analysis results.

**Approach:** Import clusterProfiler, enrichplot, and ggplot2 which provide the plotting functions for enrichment objects.

```r
library(clusterProfiler)
library(enrichplot)
library(ggplot2)

# Assume ego (enrichGO result), kk (enrichKEGG result), or gse (GSEA result) exists
```

## Dot Plot

**Goal:** Summarize enrichment results showing gene ratio, count, and significance in a single figure.

**Approach:** Use enrichplot dotplot which maps gene ratio to x-axis, term to y-axis, dot size to count, and color to p-value.

Most common visualization - shows gene ratio, count, and significance.

```r
dotplot(ego, showCategory = 20)

# Customize
dotplot(ego, showCategory = 15, font.size = 10, title = 'GO Enrichment') +
    scale_color_gradient(low = 'red', high = 'blue')

# Save
pdf('go_dotplot.pdf', width = 10, height = 8)
dotplot(ego, showCategory = 20)
dev.off()
```

## Bar Plot

Shows enrichment count or gene ratio.

```r
barplot(ego, showCategory = 20)

# Customize
barplot(ego, showCategory = 15, x = 'GeneRatio', color = 'p.adjust')
```

## Gene-Concept Network (cnetplot)

**Goal:** Visualize which genes contribute to multiple enriched terms, revealing shared biology.

**Approach:** Build a bipartite network connecting enriched terms to their member genes, optionally colored by fold change.

Shows relationships between genes and enriched terms.

```r
# Basic cnetplot
cnetplot(ego)

# With fold change colors
cnetplot(ego, foldChange = gene_list)

# Circular layout
cnetplot(ego, circular = TRUE, colorEdge = TRUE)

# Customize node size
cnetplot(ego, node_label = 'gene', cex_label_gene = 0.8)
```

## Enrichment Map (emapplot)

**Goal:** Identify clusters of related enriched terms by visualizing shared gene overlap.

**Approach:** Compute pairwise term similarity, then plot as a network where edges connect terms sharing genes.

Shows term-term relationships based on shared genes.

```r
# Requires pairwise_termsim first
ego_pt <- pairwise_termsim(ego)
emapplot(ego_pt)

# Customize
emapplot(ego_pt, showCategory = 30, cex_label_category = 0.6)

# Cluster by similarity
emapplot(ego_pt, group_category = TRUE, group_legend = TRUE)
```

## Tree Plot

Hierarchical clustering of enriched terms.

```r
ego_pt <- pairwise_termsim(ego)
treeplot(ego_pt)

# Show more categories
treeplot(ego_pt, showCategory = 30)
```

## Upset Plot

Show overlapping genes between terms.

```r
upsetplot(ego)

# Limit to specific number of terms
upsetplot(ego, n = 10)
```

## GSEA-Specific Plots

### Running Score Plot (gseaplot2)

```r
# Single gene set
gseaplot2(gse, geneSetID = 1, title = gse$Description[1])

# Multiple gene sets
gseaplot2(gse, geneSetID = 1:3)

# With subplots
gseaplot2(gse, geneSetID = 1, subplots = 1:3)

# By term ID
gseaplot2(gse, geneSetID = 'GO:0006955')
```

### Ridge Plot

Distribution of fold changes in gene sets.

```r
ridgeplot(gse)

# Top n gene sets
ridgeplot(gse, showCategory = 15)

# Order by NES
ridgeplot(gse, showCategory = 20) + theme(axis.text.y = element_text(size = 8))
```

## GO-Specific Plot (goplot)

DAG structure of GO terms.

```r
# Only for GO enrichment results
goplot(ego)

# Specific ontology
goplot(ego_bp)  # where ego_bp is enrichGO with ont='BP'
```

## Heatplot

Gene-concept heatmap.

```r
heatplot(ego, foldChange = gene_list)

# Customize
heatplot(ego, showCategory = 15, foldChange = gene_list)
```

## Compare Multiple Analyses

**Goal:** Visualize enrichment results side by side across multiple gene lists or conditions.

**Approach:** Use dotplot on compareCluster output, optionally faceting by cluster.

```r
# Compare clusters (from compareCluster)
dotplot(ck, showCategory = 10)

# Facet by cluster
dotplot(ck) + facet_grid(~Cluster)
```

## Customize ggplot2 Elements

**Goal:** Fine-tune enrichment plots with custom titles, themes, colors, and text sizes.

**Approach:** Chain ggplot2 modifiers onto enrichplot output since all functions return ggplot2 objects.

All enrichplot functions return ggplot2 objects.

```r
p <- dotplot(ego, showCategory = 20)

# Add title
p + ggtitle('GO Biological Process Enrichment')

# Change theme
p + theme_minimal()

# Adjust text
p + theme(axis.text.y = element_text(size = 10))

# Change colors
p + scale_color_viridis_c()
```

## Save Plots

**Goal:** Export enrichment plots as publication-quality PDF or PNG files.

**Approach:** Use base R pdf/png device functions or ggplot2 ggsave to write plots to files.

```r
# PDF (vector, publication quality)
pdf('enrichment_plots.pdf', width = 10, height = 8)
dotplot(ego, showCategory = 20)
dev.off()

# PNG (raster)
png('dotplot.png', width = 800, height = 600, res = 100)
dotplot(ego, showCategory = 20)
dev.off()

# Using ggsave
p <- dotplot(ego)
ggsave('dotplot.pdf', p, width = 10, height = 8)
```

## Visualization Summary

| Function | Best For | Input Type |
|----------|----------|------------|
| dotplot | Overview of enrichment | ORA, GSEA |
| barplot | Simple counts/ratios | ORA |
| cnetplot | Gene-term relationships | ORA |
| emapplot | Term clustering | ORA |
| treeplot | Hierarchical grouping | ORA |
| upsetplot | Term overlap | ORA |
| gseaplot2 | Running enrichment score | GSEA |
| ridgeplot | Fold change distribution | GSEA |
| goplot | GO DAG structure | GO only |
| heatplot | Gene-concept matrix | ORA |

## Related Skills

- go-enrichment - Generate GO enrichment results
- kegg-pathways - Generate KEGG enrichment results
- gsea - Generate GSEA results
