# bio-workflows-cytometry-pipeline

> End-to-end flow cytometry workflow from FCS files to differential analysis. Orchestrates compensation, transformation, gating/clustering, and statistical testing with CATALYST/diffcyt. Use when processing flow or mass cytometry data end-to-end.

**Available tools:** Read, Bash

# Flow Cytometry Pipeline

## Pipeline Overview

```
FCS Files ──> Compensation ──> Transformation ──> Gated/Clustered Data
                                                          │
                                                          ▼
                  ┌─────────────────────────────────────────────────┐
                  │            cytometry-pipeline                   │
                  ├─────────────────────────────────────────────────┤
                  │  1. Load FCS Files                              │
                  │  2. Compensation & Transformation               │
                  │  3. QC & Filtering                              │
                  │  4. Clustering (FlowSOM) or Gating              │
                  │  5. Dimensionality Reduction (UMAP)             │
                  │  6. Differential Abundance/State Analysis       │
                  │  7. Visualization                               │
                  └─────────────────────────────────────────────────┘
                                                          │
                                                          ▼
                      Differential Cell Populations + Markers
```

## Complete R Workflow (CATALYST)

```r
library(CATALYST)
library(diffcyt)
library(SingleCellExperiment)
library(flowCore)
library(ggplot2)

# === 1. SETUP PANEL AND METADATA ===
# Panel definition
panel <- data.frame(
    fcs_colname = c('FSC-A', 'SSC-A', 'CD45', 'CD3', 'CD4', 'CD8', 'CD19',
                    'CD14', 'CD56', 'HLA-DR', 'Ki67', 'IFNg'),
    antigen = c('FSC', 'SSC', 'CD45', 'CD3', 'CD4', 'CD8', 'CD19',
                'CD14', 'CD56', 'HLA-DR', 'Ki67', 'IFNg'),
    marker_class = c('none', 'none', 'type', 'type', 'type', 'type', 'type',
                     'type', 'type', 'type', 'state', 'state')
)

# Sample metadata
md <- data.frame(
    file_name = list.files('data/', pattern = '\\.fcs$'),
    sample_id = paste0('Sample', 1:8),
    condition = rep(c('Control', 'Treatment'), each = 4),
    patient_id = rep(paste0('Patient', 1:4), 2)
)

cat('Loading', nrow(md), 'FCS files...\n')

# === 2. LOAD AND PREPARE DATA ===
fcs_files <- file.path('data', md$file_name)
fs <- read.flowSet(fcs_files)

# Apply compensation if stored in FCS
fs_comp <- compensate(fs, spillover(fs[[1]]))

# Prepare SingleCellExperiment with CATALYST
sce <- prepData(fs_comp, panel, md,
                transform = TRUE,
                cofactor = 5,  # For CyTOF use 5, flow cytometry use 150
                FACS = TRUE)

cat('Loaded', ncol(sce), 'cells\n')

# === 3. QC ===
# Per-sample cell counts
table(sce$sample_id)

# Expression distributions
plotExprs(sce, color_by = 'condition')
ggsave('qc_expression_distributions.png', width = 12, height = 8)

# MDS plot for sample similarity
plotMDS(sce, color_by = 'condition')
ggsave('qc_mds.png', width = 8, height = 6)

# === 4. CLUSTERING ===
cat('Clustering...\n')
sce <- cluster(sce,
               features = 'type',  # Use lineage markers
               xdim = 10, ydim = 10,
               maxK = 20,
               seed = 42)

# Metaclustering at different resolutions
table(cluster_ids(sce, 'meta20'))

# === 5. DIMENSIONALITY REDUCTION ===
cat('Running UMAP...\n')
sce <- runDR(sce, dr = 'UMAP', features = 'type')

# Plot UMAP
plotDR(sce, dr = 'UMAP', color_by = 'meta20')
ggsave('umap_clusters.png', width = 8, height = 6)

plotDR(sce, dr = 'UMAP', color_by = 'condition')
ggsave('umap_condition.png', width = 8, height = 6)

# === 6. CLUSTER ANNOTATION ===
# Heatmap of marker expression
plotExprHeatmap(sce, features = 'type', k = 'meta20',
                by = 'cluster_id', scale = 'last', bars = TRUE)
ggsave('heatmap_clusters.png', width = 12, height = 8)

# Manual annotation based on markers
cluster_annotations <- c(
    '1' = 'CD4 T cells',
    '2' = 'CD8 T cells',
    '3' = 'B cells',
    '4' = 'Monocytes',
    '5' = 'NK cells'
    # ... continue for all clusters
)
sce$cell_type <- cluster_annotations[cluster_ids(sce, 'meta20')]

# === 7. DIFFERENTIAL ANALYSIS ===
cat('Running differential analysis...\n')

# Create design matrix
design <- createDesignMatrix(ei(sce), cols_design = 'condition')

# Contrast
contrast <- createContrast(c(0, 1))  # Treatment vs Control

# Differential Abundance (DA)
res_DA <- testDA_edgeR(sce, design, contrast, cluster_id = 'meta20')

da_results <- as.data.frame(rowData(res_DA))
da_results <- da_results[order(da_results$p_adj), ]
cat('\nDifferential Abundance Results:\n')
print(da_results[, c('cluster_id', 'logFC', 'p_val', 'p_adj')])

# Differential State (DS) - marker expression
res_DS <- testDS_limma(sce, design, contrast,
                        cluster_id = 'meta20',
                        markers_include = rownames(sce)[rowData(sce)$marker_class == 'state'])

ds_results <- as.data.frame(rowData(res_DS))
cat('\nDifferential State Results:\n')
sig_ds <- ds_results[ds_results$p_adj < 0.05, ]
print(sig_ds[, c('cluster_id', 'marker_id', 'logFC', 'p_adj')])

# === 8. VISUALIZATION ===
# DA heatmap
plotDiffHeatmap(sce, res_DA, all = TRUE, fdr = 0.05)
ggsave('da_heatmap.png', width = 10, height = 8)

# Abundance boxplots
plotAbundances(sce, k = 'meta20', by = 'cluster_id', group_by = 'condition')
ggsave('abundance_boxplots.png', width = 12, height = 8)

# Volcano plot
da_results$significant <- da_results$p_adj < 0.05
ggplot(da_results, aes(x = logFC, y = -log10(p_adj), color = significant)) +
    geom_point(size = 3) +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed') +
    scale_color_manual(values = c('gray', 'red')) +
    theme_bw() +
    labs(title = 'Differential Abundance')
ggsave('da_volcano.png', width = 8, height = 6)

# === 9. EXPORT ===
write.csv(da_results, 'da_results.csv', row.names = FALSE)
write.csv(ds_results, 'ds_results.csv', row.names = FALSE)
saveRDS(sce, 'cytometry_analysis.rds')

cat('\nAnalysis complete!\n')
cat('Significant DA clusters:', sum(da_results$p_adj < 0.05), '\n')
```

## flowCore + Manual Gating Workflow

```r
library(flowCore)
library(flowWorkspace)
library(ggcyto)

# Load data
fs <- read.flowSet(list.files('data/', pattern = '\\.fcs$', full.names = TRUE))

# Compensation
comp_matrix <- spillover(fs[[1]])[[1]]
fs_comp <- compensate(fs, comp_matrix)

# Transformation
trans <- estimateLogicle(fs_comp[[1]], colnames(comp_matrix))
fs_trans <- transform(fs_comp, trans)

# Create GatingSet
gs <- GatingSet(fs_trans)

# Apply gates
gs_add_gating_method(gs, alias = 'live',
                     pop = '+', parent = 'root',
                     dims = 'FSC-A,SSC-A',
                     gating_method = 'gate_flowclust_2d',
                     gating_args = list(K = 2, target = c(50000, 25000)))

gs_add_gating_method(gs, alias = 'singlets',
                     pop = '+', parent = 'live',
                     dims = 'FSC-A,FSC-H',
                     gating_method = 'singletGate')

# Visualize gates
autoplot(gs[[1]], 'singlets')

# Extract gated data
gated_data <- gs_pop_get_data(gs, 'singlets')
```

## Python Alternative (FlowCytometryTools)

```python
import flowkit as fk
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Load FCS files
sample = fk.Sample('sample.fcs')

# Get data as DataFrame
data = sample.as_dataframe(source='raw')

# Compensation (if needed)
comp_matrix = sample.metadata['spill']
data_comp = np.dot(data, np.linalg.inv(comp_matrix))

# Arcsinh transformation
cofactor = 150  # For flow cytometry
data_trans = np.arcsinh(data_comp / cofactor)

# Clustering
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data_trans)

kmeans = KMeans(n_clusters=10, random_state=42)
clusters = kmeans.fit_predict(data_scaled)
```

## QC Checkpoints

| Stage | Check | Action if Failed |
|-------|-------|------------------|
| Loading | All FCS files read | Check file integrity |
| Compensation | Spillover values reasonable | Recalculate |
| Transformation | Distributions normalized | Adjust cofactor |
| Events | >10K cells per sample | Check acquisition |
| Clustering | 10-30 populations | Adjust K/resolution |
| DA | >3 replicates per group | Need more samples |

## Workflow Variants

### CyTOF Data
```r
# CyTOF-specific settings
sce <- prepData(fs, panel, md,
                transform = TRUE,
                cofactor = 5,  # CyTOF uses cofactor 5
                FACS = FALSE)  # Not flow cytometry

# Bead normalization should be done upstream (Fluidigm software)
```

### Paired Design
```r
# For paired samples (e.g., pre/post treatment)
design <- createDesignMatrix(ei(sce), cols_design = c('condition', 'patient_id'))

# Include patient as blocking factor
formula <- createFormula(ei(sce), cols_fixed = 'condition', cols_random = 'patient_id')
res_DA <- testDA_voom(sce, formula, contrast)
```

## Related Skills

- flow-cytometry/fcs-handling - FCS file operations
- flow-cytometry/compensation-transformation - Data preprocessing
- flow-cytometry/gating-analysis - Manual gating
- flow-cytometry/clustering-phenotyping - Unsupervised clustering
- flow-cytometry/differential-analysis - Statistical testing
- flow-cytometry/doublet-detection - Remove doublet events
- flow-cytometry/bead-normalization - CyTOF EQ bead normalization
- flow-cytometry/cytometry-qc - Comprehensive QC
- single-cell/clustering - Related clustering methods
