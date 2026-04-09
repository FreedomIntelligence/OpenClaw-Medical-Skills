# bio-data-visualization-heatmaps-clustering

> Create clustered heatmaps with row/column annotations using ComplexHeatmap, pheatmap, and seaborn for gene expression and omics data visualization. Use when visualizing expression patterns across samples or identifying co-expressed gene clusters.

**Available tools:** Read, Bash

# Heatmaps and Clustering

## pheatmap (R) - Quick Heatmaps

```r
library(pheatmap)
library(RColorBrewer)

# Basic heatmap with clustering
pheatmap(mat, scale = 'row', cluster_rows = TRUE, cluster_cols = TRUE)

# With annotations
annotation_col <- data.frame(
    Condition = metadata$condition,
    Batch = metadata$batch,
    row.names = colnames(mat)
)

annotation_row <- data.frame(
    Pathway = gene_info$pathway,
    row.names = rownames(mat)
)

pheatmap(mat, scale = 'row',
         annotation_col = annotation_col,
         annotation_row = annotation_row,
         color = colorRampPalette(rev(brewer.pal(9, 'RdBu')))(100),
         show_rownames = FALSE,
         fontsize = 8)
```

## pheatmap Customization

```r
# Custom annotation colors
ann_colors <- list(
    Condition = c(Control = '#4DBBD5', Treatment = '#E64B35'),
    Batch = c(A = '#00A087', B = '#3C5488', C = '#F39B7F'),
    Pathway = c(Metabolism = '#8491B4', Signaling = '#91D1C2')
)

pheatmap(mat, scale = 'row',
         annotation_col = annotation_col,
         annotation_colors = ann_colors,
         clustering_distance_rows = 'correlation',
         clustering_distance_cols = 'euclidean',
         clustering_method = 'ward.D2',
         cutree_rows = 4,
         cutree_cols = 2,
         gaps_col = c(5, 10),
         border_color = NA,
         main = 'Gene Expression Heatmap')
```

## ComplexHeatmap (R) - Advanced

```r
library(ComplexHeatmap)
library(circlize)

# Color function
col_fun <- colorRamp2(c(-2, 0, 2), c('blue', 'white', 'red'))

# Basic heatmap
Heatmap(mat, name = 'Z-score', col = col_fun,
        cluster_rows = TRUE, cluster_columns = TRUE,
        show_row_names = FALSE, show_column_names = TRUE)
```

## ComplexHeatmap with Annotations

```r
# Column annotation
ha_col <- HeatmapAnnotation(
    Condition = metadata$condition,
    Batch = metadata$batch,
    Age = anno_barplot(metadata$age),
    col = list(
        Condition = c(Control = '#4DBBD5', Treatment = '#E64B35'),
        Batch = c(A = '#00A087', B = '#3C5488')
    )
)

# Row annotation
ha_row <- rowAnnotation(
    Pathway = gene_info$pathway,
    LogFC = anno_barplot(gene_info$log2FC, baseline = 0,
                          gp = gpar(fill = ifelse(gene_info$log2FC > 0, 'red', 'blue'))),
    col = list(Pathway = c(Metabolism = '#8491B4', Signaling = '#91D1C2'))
)

Heatmap(mat, name = 'Z-score', col = col_fun,
        top_annotation = ha_col,
        left_annotation = ha_row,
        row_split = gene_info$pathway,
        column_split = metadata$condition)
```

## Multiple Heatmaps

```r
# Combine heatmaps horizontally
ht1 <- Heatmap(mat1, name = 'Expression', col = col_fun)
ht2 <- Heatmap(mat2, name = 'Methylation', col = colorRamp2(c(0, 0.5, 1), c('blue', 'white', 'red')))

ht_list <- ht1 + ht2
draw(ht_list, row_title = 'Genes', column_title = 'Samples')
```

## seaborn (Python)

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Basic clustermap
g = sns.clustermap(df, cmap='RdBu_r', center=0, figsize=(10, 12),
                   row_cluster=True, col_cluster=True,
                   standard_scale=0)  # 0 = rows, 1 = columns
plt.savefig('heatmap.png', dpi=150, bbox_inches='tight')
```

## seaborn with Annotations

```python
# Create color mappings
condition_colors = {'Control': '#4DBBD5', 'Treatment': '#E64B35'}
batch_colors = {'A': '#00A087', 'B': '#3C5488', 'C': '#F39B7F'}

col_colors = pd.DataFrame({
    'Condition': metadata['condition'].map(condition_colors),
    'Batch': metadata['batch'].map(batch_colors)
})

row_colors = gene_info['pathway'].map({'Metabolism': '#8491B4', 'Signaling': '#91D1C2'})

g = sns.clustermap(df, cmap='RdBu_r', center=0,
                   row_colors=row_colors,
                   col_colors=col_colors,
                   figsize=(12, 14),
                   dendrogram_ratio=0.15,
                   cbar_pos=(0.02, 0.8, 0.03, 0.15))

g.ax_heatmap.set_xlabel('Samples')
g.ax_heatmap.set_ylabel('Genes')
```

## Clustering Methods

```r
# Distance metrics
# 'euclidean', 'correlation', 'manhattan', 'maximum', 'canberra', 'binary'

# Linkage methods
# 'complete', 'single', 'average', 'ward.D', 'ward.D2', 'mcquitty', 'median', 'centroid'

pheatmap(mat, clustering_distance_rows = 'correlation',
         clustering_distance_cols = 'euclidean',
         clustering_method = 'ward.D2')
```

## Extract Cluster Assignments

```r
# pheatmap
p <- pheatmap(mat, scale = 'row', cutree_rows = 4, silent = TRUE)
row_clusters <- cutree(p$tree_row, k = 4)

# ComplexHeatmap
ht <- Heatmap(mat, row_split = 4)
ht <- draw(ht)
row_order <- row_order(ht)
```

```python
# seaborn
g = sns.clustermap(df, cmap='RdBu_r')
row_linkage = g.dendrogram_row.linkage
from scipy.cluster.hierarchy import fcluster
clusters = fcluster(row_linkage, t=4, criterion='maxclust')
```

## Save Heatmaps

```r
# pheatmap to file
pheatmap(mat, filename = 'heatmap.pdf', width = 8, height = 10)

# ComplexHeatmap to file
pdf('heatmap.pdf', width = 8, height = 10)
draw(ht)
dev.off()
```

## Related Skills

- data-visualization/ggplot2-fundamentals - General plotting
- data-visualization/color-palettes - Color selection
- differential-expression/de-visualization - Expression heatmaps
