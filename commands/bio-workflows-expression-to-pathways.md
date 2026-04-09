# bio-workflows-expression-to-pathways

> Workflow from differential expression results to functional enrichment analysis. Covers GO, KEGG, Reactome enrichment with clusterProfiler and visualization. Use when taking DE results to pathway enrichment.

**Available tools:** Read, Bash

# Expression to Pathways Workflow

Convert differential expression results into biological insights through functional enrichment analysis.

## Workflow Overview

```
DE Results (gene list or ranked list)
    |
    v
[1. Gene ID Conversion] --> Convert to Entrez/Ensembl
    |
    v
[2. Over-representation Analysis]
    |
    +---> GO Enrichment (BP, MF, CC)
    |
    +---> KEGG Pathways
    |
    +---> Reactome Pathways
    |
    v
[3. GSEA (ranked genes)]
    |
    v
[4. Visualization] -----> Dot plots, networks, bar plots
    |
    v
Functional annotations and pathway insights
```

## Input Preparation

### From DESeq2 Results

```r
library(DESeq2)
library(clusterProfiler)
library(org.Hs.eg.db)

# Load DE results
res <- read.csv('deseq2_results.csv', row.names = 1)

# Significant genes for ORA
sig_genes <- rownames(subset(res, padj < 0.05 & abs(log2FoldChange) > 1))

# All genes for background
all_genes <- rownames(res)

# Ranked list for GSEA (by stat or log2FC)
ranked_genes <- res$log2FoldChange
names(ranked_genes) <- rownames(res)
ranked_genes <- sort(ranked_genes, decreasing = TRUE)
ranked_genes <- ranked_genes[!is.na(ranked_genes)]
```

### Gene ID Conversion

```r
# Convert gene symbols to Entrez IDs
sig_entrez <- bitr(sig_genes, fromType = 'SYMBOL', toType = 'ENTREZID',
                   OrgDb = org.Hs.eg.db)

# For ranked list
ranked_entrez <- bitr(names(ranked_genes), fromType = 'SYMBOL', toType = 'ENTREZID',
                      OrgDb = org.Hs.eg.db)
ranked_list <- ranked_genes[ranked_entrez$SYMBOL]
names(ranked_list) <- ranked_entrez$ENTREZID
```

## Step 1: GO Over-representation Analysis

```r
# Biological Process
go_bp <- enrichGO(gene = sig_entrez$ENTREZID,
                  OrgDb = org.Hs.eg.db,
                  ont = 'BP',
                  pAdjustMethod = 'BH',
                  pvalueCutoff = 0.05,
                  qvalueCutoff = 0.1,
                  readable = TRUE)

# Molecular Function
go_mf <- enrichGO(gene = sig_entrez$ENTREZID,
                  OrgDb = org.Hs.eg.db,
                  ont = 'MF',
                  pAdjustMethod = 'BH',
                  pvalueCutoff = 0.05,
                  readable = TRUE)

# Cellular Component
go_cc <- enrichGO(gene = sig_entrez$ENTREZID,
                  OrgDb = org.Hs.eg.db,
                  ont = 'CC',
                  pAdjustMethod = 'BH',
                  pvalueCutoff = 0.05,
                  readable = TRUE)

# Simplify redundant terms
go_bp_simple <- simplify(go_bp, cutoff = 0.7, by = 'p.adjust')
```

## Step 2: KEGG Pathway Enrichment

```r
kegg <- enrichKEGG(gene = sig_entrez$ENTREZID,
                   organism = 'hsa',
                   pvalueCutoff = 0.05,
                   qvalueCutoff = 0.1)

# Convert KEGG IDs to readable names
kegg <- setReadable(kegg, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID')
```

## Step 3: Reactome Pathway Enrichment

```r
library(ReactomePA)

reactome <- enrichPathway(gene = sig_entrez$ENTREZID,
                          organism = 'human',
                          pvalueCutoff = 0.05,
                          readable = TRUE)
```

## Step 4: Gene Set Enrichment Analysis (GSEA)

```r
# GO GSEA
gsea_go <- gseGO(geneList = ranked_list,
                 OrgDb = org.Hs.eg.db,
                 ont = 'BP',
                 minGSSize = 10,
                 maxGSSize = 500,
                 pvalueCutoff = 0.05,
                 verbose = FALSE)

# KEGG GSEA
gsea_kegg <- gseKEGG(geneList = ranked_list,
                     organism = 'hsa',
                     minGSSize = 10,
                     maxGSSize = 500,
                     pvalueCutoff = 0.05,
                     verbose = FALSE)
```

## Step 5: Visualization

```r
library(enrichplot)
library(ggplot2)

# Dot plot
dotplot(go_bp_simple, showCategory = 20) +
    ggtitle('GO Biological Process Enrichment')
ggsave('go_bp_dotplot.pdf', width = 10, height = 8)

# Bar plot
barplot(kegg, showCategory = 15) +
    ggtitle('KEGG Pathway Enrichment')
ggsave('kegg_barplot.pdf', width = 9, height = 6)

# Enrichment map (network of related terms)
go_bp_simple <- pairwise_termsim(go_bp_simple)
emapplot(go_bp_simple, showCategory = 30) +
    ggtitle('GO Term Similarity Network')
ggsave('go_network.pdf', width = 10, height = 10)

# Concept network (gene-term connections)
cnetplot(go_bp, showCategory = 5, categorySize = 'pvalue') +
    ggtitle('Gene-Concept Network')
ggsave('cnet_plot.pdf', width = 12, height = 10)

# GSEA plot for specific pathway
gseaplot2(gsea_kegg, geneSetID = 1:3, pvalue_table = TRUE)
ggsave('gsea_plot.pdf', width = 10, height = 8)

# Ridge plot for GSEA
ridgeplot(gsea_go, showCategory = 15)
ggsave('gsea_ridge.pdf', width = 8, height = 10)
```

## Step 6: Export Results

```r
# Export enrichment results
write.csv(as.data.frame(go_bp), 'go_bp_enrichment.csv', row.names = FALSE)
write.csv(as.data.frame(kegg), 'kegg_enrichment.csv', row.names = FALSE)
write.csv(as.data.frame(reactome), 'reactome_enrichment.csv', row.names = FALSE)
write.csv(as.data.frame(gsea_go), 'gsea_go_results.csv', row.names = FALSE)

# Combine key results
combined <- rbind(
    data.frame(Database = 'GO_BP', as.data.frame(go_bp_simple)[1:10,]),
    data.frame(Database = 'KEGG', as.data.frame(kegg)[1:10,]),
    data.frame(Database = 'Reactome', as.data.frame(reactome)[1:10,])
)
write.csv(combined, 'top_enriched_pathways.csv', row.names = FALSE)
```

## Parameter Recommendations

| Analysis | Parameter | Value |
|----------|-----------|-------|
| enrichGO | pvalueCutoff | 0.05 |
| enrichGO | qvalueCutoff | 0.1 |
| simplify | cutoff | 0.7 |
| gseGO | minGSSize | 10 |
| gseGO | maxGSSize | 500 |
| GSEA | perm | 1000 (default) |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| No enriched terms | Too few genes, wrong IDs | Check gene IDs, relax thresholds |
| All terms significant | Too many genes | Be more stringent with DE cutoffs |
| Gene ID conversion fails | Wrong organism, format | Check OrgDb package, gene format |
| GSEA no results | Poor ranking, small gene sets | Check ranked list, adjust minGSSize |

## Complete Workflow Script

```r
library(clusterProfiler)
library(org.Hs.eg.db)
library(ReactomePA)
library(enrichplot)
library(ggplot2)

# Configuration
de_file <- 'deseq2_results.csv'
output_dir <- 'pathway_analysis'
dir.create(output_dir, showWarnings = FALSE)

# Load and prepare data
res <- read.csv(de_file, row.names = 1)
sig_genes <- rownames(subset(res, padj < 0.05 & abs(log2FoldChange) > 1))
cat('Significant genes:', length(sig_genes), '\n')

# Convert IDs
sig_entrez <- bitr(sig_genes, fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)
cat('Converted to Entrez:', nrow(sig_entrez), '\n')

# Ranked list for GSEA
ranked <- res$log2FoldChange
names(ranked) <- rownames(res)
ranked <- sort(ranked[!is.na(ranked)], decreasing = TRUE)
ranked_entrez <- bitr(names(ranked), fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)
ranked_list <- ranked[ranked_entrez$SYMBOL]
names(ranked_list) <- ranked_entrez$ENTREZID

# GO enrichment
go_bp <- enrichGO(sig_entrez$ENTREZID, OrgDb = org.Hs.eg.db, ont = 'BP', readable = TRUE)
go_bp_simple <- simplify(go_bp, cutoff = 0.7)

# KEGG
kegg <- enrichKEGG(sig_entrez$ENTREZID, organism = 'hsa')
kegg <- setReadable(kegg, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID')

# Reactome
reactome <- enrichPathway(sig_entrez$ENTREZID, organism = 'human', readable = TRUE)

# GSEA
gsea_go <- gseGO(ranked_list, OrgDb = org.Hs.eg.db, ont = 'BP', verbose = FALSE)

# Plots
pdf(file.path(output_dir, 'enrichment_plots.pdf'), width = 10, height = 8)
print(dotplot(go_bp_simple, showCategory = 20) + ggtitle('GO Biological Process'))
print(barplot(kegg, showCategory = 15) + ggtitle('KEGG Pathways'))
if (nrow(as.data.frame(reactome)) > 0) {
    print(dotplot(reactome, showCategory = 15) + ggtitle('Reactome Pathways'))
}
dev.off()

# Export
write.csv(as.data.frame(go_bp_simple), file.path(output_dir, 'go_bp.csv'), row.names = FALSE)
write.csv(as.data.frame(kegg), file.path(output_dir, 'kegg.csv'), row.names = FALSE)
write.csv(as.data.frame(reactome), file.path(output_dir, 'reactome.csv'), row.names = FALSE)

cat('\nResults saved to:', output_dir, '\n')
cat('GO BP terms:', nrow(as.data.frame(go_bp_simple)), '\n')
cat('KEGG pathways:', nrow(as.data.frame(kegg)), '\n')
cat('Reactome pathways:', nrow(as.data.frame(reactome)), '\n')
```

## Related Skills

- pathway-analysis/go-enrichment - GO enrichment details
- pathway-analysis/kegg-pathways - KEGG analysis
- pathway-analysis/reactome-pathways - Reactome analysis
- pathway-analysis/gsea - GSEA methods
- pathway-analysis/enrichment-visualization - Visualization options
