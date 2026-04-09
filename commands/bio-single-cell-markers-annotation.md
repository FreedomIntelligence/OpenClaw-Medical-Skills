# bio-single-cell-markers-annotation

> Find marker genes and annotate cell types in single-cell RNA-seq using Seurat (R) and Scanpy (Python). Use for differential expression between clusters, identifying cluster-specific markers, scoring gene sets, and assigning cell type labels. Use when finding marker genes and annotating clusters.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, pandas 2.2+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Marker Genes and Cell Type Annotation

Find differentially expressed genes between clusters and annotate cell types.

## Scanpy (Python)

**Goal:** Identify cluster-specific marker genes, score gene sets, and annotate cell types using Scanpy.

**Approach:** Perform differential expression testing between clusters with Wilcoxon rank-sum, visualize markers with dot plots and heatmaps, and assign cell type labels manually.

**"Find marker genes for each cluster"** → Test each cluster against all others for differentially expressed genes and rank by statistical significance and fold change.

### Required Imports

```python
import scanpy as sc
import pandas as pd
```

### Find Markers for All Clusters

```python
# Find marker genes for each cluster vs all others
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')

# View top markers
sc.pl.rank_genes_groups(adata, n_genes=10, sharey=False)

# Get results as DataFrame
markers = sc.get.rank_genes_groups_df(adata, group=None)
print(markers.head(20))
```

### Marker Detection Methods

```python
# Wilcoxon rank-sum test (default, recommended)
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')

# t-test
sc.tl.rank_genes_groups(adata, groupby='leiden', method='t-test')

# Logistic regression
sc.tl.rank_genes_groups(adata, groupby='leiden', method='logreg')
```

### Filter Markers

```python
# Get markers with filters
markers = sc.get.rank_genes_groups_df(adata, group='0')
significant = markers[(markers['pvals_adj'] < 0.05) & (markers['logfoldchanges'] > 1)]
print(f'Cluster 0 significant markers: {len(significant)}')

# Filter all groups
sc.tl.filter_rank_genes_groups(adata, min_fold_change=1.5, min_in_group_fraction=0.25)
```

### Compare Specific Clusters

```python
# Find markers between two specific clusters
sc.tl.rank_genes_groups(adata, groupby='leiden', groups=['0'], reference='1', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=10)
```

### Visualize Marker Expression

```python
# Dot plot of top markers per cluster
markers_to_plot = ['CD3D', 'CD8A', 'MS4A1', 'CD14', 'FCGR3A', 'NKG7']
sc.pl.dotplot(adata, var_names=markers_to_plot, groupby='leiden')

# Stacked violin
sc.pl.stacked_violin(adata, var_names=markers_to_plot, groupby='leiden')

# Heatmap
sc.pl.rank_genes_groups_heatmap(adata, n_genes=5, groupby='leiden')

# Matrix plot
sc.pl.matrixplot(adata, var_names=markers_to_plot, groupby='leiden')
```

### Gene Set Scoring

```python
# Score cells for gene set expression
t_cell_genes = ['CD3D', 'CD3E', 'CD4', 'CD8A', 'CD8B']
sc.tl.score_genes(adata, gene_list=t_cell_genes, score_name='T_cell_score')

# Visualize score
sc.pl.umap(adata, color='T_cell_score')
```

### Cell Cycle Scoring

```python
# Score cell cycle phases
s_genes = ['MCM5', 'PCNA', 'TYMS', 'FEN1', 'MCM2']  # S phase genes
g2m_genes = ['HMGB2', 'CDK1', 'NUSAP1', 'UBE2C', 'BIRC5']  # G2/M genes

sc.tl.score_genes_cell_cycle(adata, s_genes=s_genes, g2m_genes=g2m_genes)
sc.pl.umap(adata, color=['S_score', 'G2M_score', 'phase'])
```

### Manual Cell Type Annotation

```python
# Create annotation dictionary
cluster_annotations = {
    '0': 'CD4 T cells',
    '1': 'CD14 Monocytes',
    '2': 'B cells',
    '3': 'CD8 T cells',
    '4': 'NK cells',
    '5': 'FCGR3A Monocytes'
}

# Add annotations
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_annotations)

# Visualize
sc.pl.umap(adata, color='cell_type')
```

### Export Markers

```python
# Export all markers to CSV
markers = sc.get.rank_genes_groups_df(adata, group=None)
markers.to_csv('all_markers.csv', index=False)

# Export top markers per cluster
top_markers = markers.groupby('group').head(20)
top_markers.to_csv('top_markers.csv', index=False)
```

---

## Seurat (R)

**Goal:** Identify cluster-specific marker genes, score gene modules, and annotate cell types using Seurat.

**Approach:** Run FindAllMarkers with Wilcoxon or MAST tests, visualize with FeaturePlot/DotPlot/DoHeatmap, and rename cluster identities with cell type labels.

### Required Libraries

```r
library(Seurat)
library(dplyr)
```

### Find All Markers

```r
# Find markers for all clusters
all_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)

# View top markers per cluster
top_markers <- all_markers %>%
    group_by(cluster) %>%
    slice_max(n = 5, order_by = avg_log2FC)
print(top_markers)
```

### Find Markers for Specific Cluster

```r
# Markers for cluster 0 vs all others
cluster0_markers <- FindMarkers(seurat_obj, ident.1 = 0, min.pct = 0.25)
head(cluster0_markers)
```

### Compare Two Clusters

```r
# Find markers between two specific clusters
markers_0_vs_1 <- FindMarkers(seurat_obj, ident.1 = 0, ident.2 = 1, min.pct = 0.25)
head(markers_0_vs_1)
```

### Marker Detection Methods

```r
# Wilcoxon (default, fast)
markers <- FindMarkers(seurat_obj, ident.1 = 0, test.use = 'wilcox')

# MAST (recommended for DE)
markers <- FindMarkers(seurat_obj, ident.1 = 0, test.use = 'MAST')

# DESeq2
markers <- FindMarkers(seurat_obj, ident.1 = 0, test.use = 'DESeq2')

# Logistic regression
markers <- FindMarkers(seurat_obj, ident.1 = 0, test.use = 'LR')
```

### Visualize Markers

```r
# Feature plot on UMAP
FeaturePlot(seurat_obj, features = c('CD3D', 'MS4A1', 'CD14', 'NKG7'))

# Violin plot
VlnPlot(seurat_obj, features = c('CD3D', 'MS4A1', 'CD14'))

# Dot plot
markers_to_plot <- c('CD3D', 'CD8A', 'MS4A1', 'CD14', 'FCGR3A', 'NKG7')
DotPlot(seurat_obj, features = markers_to_plot) + RotatedAxis()

# Heatmap
top10 <- all_markers %>%
    group_by(cluster) %>%
    top_n(n = 10, wt = avg_log2FC)
DoHeatmap(seurat_obj, features = top10$gene)
```

### Gene Module Scoring

```r
# Score cells for gene set
t_cell_genes <- list(c('CD3D', 'CD3E', 'CD4', 'CD8A', 'CD8B'))
seurat_obj <- AddModuleScore(seurat_obj, features = t_cell_genes, name = 'T_cell_score')

# Visualize
FeaturePlot(seurat_obj, features = 'T_cell_score1')
```

### Cell Cycle Scoring

```r
# Built-in cell cycle genes
s.genes <- cc.genes$s.genes
g2m.genes <- cc.genes$g2m.genes

seurat_obj <- CellCycleScoring(seurat_obj, s.features = s.genes, g2m.features = g2m.genes)
DimPlot(seurat_obj, group.by = 'Phase')
```

### Manual Cell Type Annotation

```r
# Rename cluster identities
new_cluster_ids <- c(
    '0' = 'CD4 T cells',
    '1' = 'CD14 Monocytes',
    '2' = 'B cells',
    '3' = 'CD8 T cells',
    '4' = 'NK cells',
    '5' = 'FCGR3A Monocytes'
)

seurat_obj <- RenameIdents(seurat_obj, new_cluster_ids)
DimPlot(seurat_obj, reduction = 'umap', label = TRUE)

# Store in metadata
seurat_obj$cell_type <- Idents(seurat_obj)
```

### Export Markers

```r
# Export to CSV
write.csv(all_markers, file = 'all_markers.csv', row.names = FALSE)

# Export top markers
write.csv(top_markers, file = 'top_markers.csv', row.names = FALSE)
```

---

## Common PBMC Markers

| Cell Type | Markers |
|-----------|---------|
| CD4 T cells | CD3D, CD4, IL7R |
| CD8 T cells | CD3D, CD8A, CD8B |
| B cells | MS4A1, CD79A, CD19 |
| NK cells | NKG7, GNLY, NCAM1 |
| CD14 Monocytes | CD14, LYZ, S100A8 |
| FCGR3A Monocytes | FCGR3A, MS4A7 |
| Dendritic cells | FCER1A, CST3 |
| Platelets | PPBP, PF4 |

## Method Comparison

| Task | Scanpy | Seurat |
|------|--------|--------|
| All markers | `rank_genes_groups()` | `FindAllMarkers()` |
| Specific cluster | `rank_genes_groups(groups=['0'])` | `FindMarkers(ident.1=0)` |
| Two clusters | `rank_genes_groups(reference='1')` | `FindMarkers(ident.1=0, ident.2=1)` |
| Gene scoring | `score_genes()` | `AddModuleScore()` |
| Dot plot | `sc.pl.dotplot()` | `DotPlot()` |

## Related Skills

- clustering - Must cluster before finding markers
- preprocessing - Data must be normalized
- data-io - Export annotated data
