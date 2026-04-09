# bio-flow-cytometry-clustering-phenotyping

> Unsupervised clustering and cell type identification for flow/mass cytometry. Covers FlowSOM, Phenograph, and CATALYST workflows. Use when discovering cell populations in high-dimensional cytometry data without predefined gates.

## Version Compatibility

Reference examples tested with: FlowSOM 2.10+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Clustering and Phenotyping

**"Cluster my cytometry data to find cell types"** → Discover cell populations in high-dimensional flow/mass cytometry data using unsupervised clustering without predefined gates.
- R: `FlowSOM::FlowSOM()` for self-organizing map clustering
- R: `CATALYST::cluster()` with Phenograph or FlowSOM

## FlowSOM Clustering

**Goal:** Cluster cytometry events into cell populations using self-organizing maps.

**Approach:** Build a FlowSOM grid on marker channels, then extract metacluster assignments per cell.

```r
library(FlowSOM)

# Prepare data
expr <- exprs(fcs)
marker_cols <- grep('CD|HLA', colnames(fcs), value = TRUE)

# Build SOM
fsom <- FlowSOM(fcs,
                colsToUse = marker_cols,
                xdim = 10, ydim = 10,
                nClus = 20,
                seed = 42)

# Get cluster assignments
clusters <- GetMetaclusters(fsom)

# Add to flowFrame
exprs(fcs) <- cbind(exprs(fcs), cluster = clusters)
```

## CATALYST Workflow (Full Pipeline)

**Goal:** Run the complete CATALYST clustering pipeline from flowSet to annotated cell populations.

**Approach:** Convert flowSet to SingleCellExperiment with prepData, then cluster on type markers with FlowSOM via CATALYST.

```r
library(CATALYST)
library(SingleCellExperiment)

# Create SCE from flowSet
sce <- prepData(fs, panel, md, transform = TRUE, cofactor = 5)

# Clustering
sce <- cluster(sce,
               features = 'type',  # Use 'type' markers from panel
               xdim = 10, ydim = 10,
               maxK = 20,
               seed = 42)

# View cluster assignments
table(cluster_ids(sce, 'meta20'))
```

## Phenograph Clustering

**Goal:** Identify cell populations using graph-based community detection on marker expression.

**Approach:** Build a k-nearest-neighbor graph on type markers, then partition with Louvain community detection via Rphenograph.

```r
library(Rphenograph)

# Extract expression matrix
expr <- assay(sce, 'exprs')

# Run Phenograph
pheno_result <- Rphenograph(t(expr[rowData(sce)$marker_class == 'type', ]), k = 30)

# Get clusters
sce$phenograph <- factor(membership(pheno_result[[2]]))
```

## Dimensionality Reduction

**Goal:** Project high-dimensional cytometry data into 2D for visualization of cell populations.

**Approach:** Run UMAP or tSNE on type marker channels using CATALYST's runDR wrapper, then plot colored by cluster.

```r
# UMAP
sce <- runDR(sce, dr = 'UMAP', features = 'type')

# tSNE
sce <- runDR(sce, dr = 'TSNE', features = 'type')

# Plot
plotDR(sce, 'UMAP', color_by = 'meta20')
```

## Cluster Annotation

**Goal:** Assign cell type labels to clusters based on marker expression profiles.

**Approach:** Visualize median marker expression per cluster with a heatmap, then map cluster IDs to cell type names.

```r
# Heatmap of marker expression by cluster
plotExprHeatmap(sce, features = 'type',
                by = 'cluster_id', k = 'meta20',
                scale = 'first', row_anno = FALSE)

# Manual annotation
cluster_annotation <- c(
    '1' = 'CD4 T cells',
    '2' = 'CD8 T cells',
    '3' = 'B cells',
    '4' = 'NK cells',
    '5' = 'Monocytes'
)

sce$cell_type <- cluster_annotation[as.character(cluster_ids(sce, 'meta20'))]
```

## Cluster Merging

**Goal:** Reduce overclustering by merging similar clusters into biologically meaningful groups.

**Approach:** Define a mapping table from original to merged cluster IDs, then apply with CATALYST's mergeClusters.

```r
# Merge similar clusters
merging_table <- data.frame(
    original = 1:20,
    merged = c(1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
               6, 6, 7, 7, 8, 8, 9, 9, 10, 10)
)

sce <- mergeClusters(sce, k = 'meta20', table = merging_table, id = 'merged')
```

## Abundance Analysis (per sample)

**Goal:** Quantify the relative frequency of each cell population across samples and conditions.

**Approach:** Cross-tabulate cluster assignments by sample ID, convert to proportions, and plot grouped by condition.

```r
# Cluster frequencies per sample
abundances <- table(cluster_ids(sce, 'meta20'), sce$sample_id)
freq <- prop.table(abundances, margin = 2)

# Plot
plotAbundances(sce, k = 'meta20', by = 'cluster_id', group_by = 'condition')
```

## Marker Expression Summary

**Goal:** Summarize and compare marker expression levels across clusters and conditions.

**Approach:** Plot per-cluster median expression with CATALYST's plotClusterExprs and pseudo-bulk expression faceted by cluster.

```r
# Median expression per cluster
plotClusterExprs(sce, k = 'meta20', features = 'type')

# Expression by cluster and condition
plotPbExprs(sce, k = 'meta20', features = 'type', facet_by = 'cluster_id')
```

## Export Results

**Goal:** Save clustering results and annotated SCE object for downstream analysis or sharing.

**Approach:** Extract cluster assignments into colData, export as CSV, and serialize the full SCE as RDS.

```r
# Add cluster info to metadata
colData(sce)$cluster <- cluster_ids(sce, 'meta20')

# Export to CSV
results <- as.data.frame(colData(sce))
write.csv(results, 'clustering_results.csv', row.names = FALSE)

# Save SCE
saveRDS(sce, 'sce_clustered.rds')
```

## Choosing Number of Clusters

**Goal:** Determine the optimal number of metaclusters for the dataset.

**Approach:** Compare normalized reduction stability (NRS) plots and heatmaps at different K values to find where clusters remain distinct.

```r
# Delta area plot
plotNRS(sce, features = 'type')

# Or visual inspection of heatmap at different K
plotExprHeatmap(sce, features = 'type', by = 'cluster_id', k = 'meta10')
plotExprHeatmap(sce, features = 'type', by = 'cluster_id', k = 'meta20')
```

## Batch Integration

**Goal:** Remove batch effects from cytometry data before or after clustering.

**Approach:** Detect batch effects by coloring UMAP by batch variable, then apply MNN correction with batchelor if needed.

```r
# If batch effects present
library(batchelor)

sce <- runDR(sce, dr = 'UMAP', features = 'type')

# Check for batch effects
plotDR(sce, 'UMAP', color_by = 'batch')

# MNN correction if needed
sce_corrected <- fastMNN(sce, batch = sce$batch)
```

## Related Skills

- gating-analysis - Manual alternative
- differential-analysis - Compare clusters between conditions
- single-cell/clustering - Similar concepts for scRNA-seq
