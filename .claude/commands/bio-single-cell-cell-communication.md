# bio-single-cell-cell-communication

> Infer cell-cell communication networks from scRNA-seq data using CellChat, NicheNet, and LIANA for ligand-receptor interaction analysis. Use when inferring ligand-receptor interactions between cell types.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Cell-Cell Communication Analysis

**"Infer cell-cell communication from my scRNA-seq data"** → Predict ligand-receptor interactions between cell types and visualize intercellular signaling networks.
- R: `CellChat::createCellChat()` → `computeCommunProb()` → `netAnalysis()`
- Python: `liana.method.cellchat()` (LIANA framework)

## CellChat (R)

**Goal:** Infer and quantify intercellular communication networks from scRNA-seq data using curated ligand-receptor databases.

**Approach:** Create a CellChat object from a Seurat object with cell type labels, select a signaling database subset, identify overexpressed ligands/receptors, compute communication probabilities using the trimean method, then aggregate into pathway-level networks.

```r
library(CellChat)
library(Seurat)

# Create CellChat object from Seurat
cellchat <- createCellChat(object = seurat_obj, group.by = 'cell_type')

# Set ligand-receptor database
CellChatDB <- CellChatDB.human  # or CellChatDB.mouse
cellchat@DB <- CellChatDB

# Subset to secreted signaling (optional)
CellChatDB.use <- subsetDB(CellChatDB, search = 'Secreted Signaling')
cellchat@DB <- CellChatDB.use

# Preprocessing
cellchat <- subsetData(cellchat)
cellchat <- identifyOverExpressedGenes(cellchat)
cellchat <- identifyOverExpressedInteractions(cellchat)

# Compute communication probability
cellchat <- computeCommunProb(cellchat, type = 'triMean')
cellchat <- filterCommunication(cellchat, min.cells = 10)

# Infer signaling pathways
cellchat <- computeCommunProbPathway(cellchat)
cellchat <- aggregateNet(cellchat)
```

## CellChat Visualization

```r
# Network plots
netVisual_circle(cellchat@net$count, vertex.weight = groupSize, weight.scale = TRUE,
                 label.edge = FALSE, title.name = 'Number of interactions')

netVisual_circle(cellchat@net$weight, vertex.weight = groupSize, weight.scale = TRUE,
                 label.edge = FALSE, title.name = 'Interaction strength')

# Heatmap of interactions
netVisual_heatmap(cellchat, color.heatmap = 'Reds')

# Specific pathway visualization
netVisual_aggregate(cellchat, signaling = 'WNT', layout = 'circle')
netVisual_aggregate(cellchat, signaling = 'WNT', layout = 'chord')

# Bubble plot
netVisual_bubble(cellchat, sources.use = c(1, 2), targets.use = c(3, 4),
                 remove.isolate = FALSE)

# Chord diagram for ligand-receptor pairs
netVisual_chord_gene(cellchat, sources.use = 1, targets.use = c(2, 3, 4),
                     lab.cex = 0.5, legend.pos.x = 10)
```

## CellChat Pathway Analysis

```r
# Identify signaling roles
cellchat <- netAnalysis_computeCentrality(cellchat, slot.name = 'netP')

# Signaling role heatmap
netAnalysis_signalingRole_heatmap(cellchat, signaling = c('WNT', 'TGFb', 'BMP'))

# Dominant senders/receivers
netAnalysis_signalingRole_scatter(cellchat)

# Compare pathways
rankNet(cellchat, mode = 'comparison', stacked = TRUE, do.stat = TRUE)
```

## Compare Conditions (CellChat)

```r
# Create separate CellChat objects
cellchat_ctrl <- createCellChat(subset(seurat_obj, condition == 'control'), group.by = 'cell_type')
cellchat_treat <- createCellChat(subset(seurat_obj, condition == 'treatment'), group.by = 'cell_type')

# Process both (same steps as above)
# ...

# Merge for comparison
cellchat_list <- list(Control = cellchat_ctrl, Treatment = cellchat_treat)
cellchat_merged <- mergeCellChat(cellchat_list, add.names = names(cellchat_list))

# Compare interactions
compareInteractions(cellchat_merged, show.legend = FALSE)

# Differential interactions
netVisual_diffInteraction(cellchat_merged, weight.scale = TRUE)
netVisual_heatmap(cellchat_merged)

# Pathway comparison
rankNet(cellchat_merged, mode = 'comparison', stacked = TRUE)
```

## NicheNet (R)

```r
library(nichenetr)
library(Seurat)
library(tidyverse)

# Load NicheNet databases
ligand_target_matrix <- readRDS('ligand_target_matrix.rds')
lr_network <- readRDS('lr_network.rds')
weighted_networks <- readRDS('weighted_networks.rds')

# Define sender and receiver cells
sender_celltypes <- c('Macrophage', 'Dendritic')
receiver <- 'T_cell'

# Get expressed genes
expressed_genes_sender <- get_expressed_genes(sender_celltypes, seurat_obj, pct = 0.10)
expressed_genes_receiver <- get_expressed_genes(receiver, seurat_obj, pct = 0.10)

# Define gene set of interest (e.g., DE genes in receiver)
geneset_oi <- FindMarkers(seurat_obj, ident.1 = 'activated_T', ident.2 = 'naive_T') %>%
    filter(p_val_adj < 0.05, avg_log2FC > 0.5) %>% rownames()

# Background genes
background_genes <- expressed_genes_receiver

# Define potential ligands
ligands <- lr_network %>% pull(from) %>% unique()
expressed_ligands <- intersect(ligands, expressed_genes_sender)

receptors <- lr_network %>% pull(to) %>% unique()
expressed_receptors <- intersect(receptors, expressed_genes_receiver)

potential_ligands <- lr_network %>%
    filter(from %in% expressed_ligands & to %in% expressed_receptors) %>%
    pull(from) %>% unique()

# NicheNet ligand activity analysis
ligand_activities <- predict_ligand_activities(
    geneset = geneset_oi,
    background_expressed_genes = background_genes,
    ligand_target_matrix = ligand_target_matrix,
    potential_ligands = potential_ligands
)

# Top ligands
best_ligands <- ligand_activities %>% top_n(20, pearson) %>% arrange(-pearson) %>% pull(test_ligand)
```

## NicheNet Visualization

```r
# Ligand-target heatmap
active_ligand_target_links <- best_ligands %>%
    lapply(get_weighted_ligand_target_links, geneset_oi, ligand_target_matrix, n = 200) %>%
    bind_rows() %>% drop_na()

vis_ligand_target <- prepare_ligand_target_visualization(
    ligand_target_df = active_ligand_target_links,
    ligand_target_matrix = ligand_target_matrix,
    cutoff = 0.33
)

p_ligand_target <- vis_ligand_target %>%
    make_heatmap_ggplot('Prioritized ligands', 'Target genes',
                        color = 'purple', legend_position = 'top')

# Ligand-receptor heatmap
lr_network_top <- lr_network %>%
    filter(from %in% best_ligands & to %in% expressed_receptors) %>%
    distinct(from, to)

vis_ligand_receptor <- get_exprs_avg(seurat_obj, 'cell_type') %>%
    inner_join(lr_network_top, by = c('gene' = 'to'))

p_ligand_receptor <- vis_ligand_receptor %>%
    make_heatmap_ggplot('Ligands', 'Receptors', color = 'mediumvioletred')

# Ligand expression by cell type
p_ligand_expression <- DotPlot(seurat_obj, features = best_ligands, cols = 'RdYlBu') +
    RotatedAxis()
```

## LIANA (Python)

```python
import liana as li
import scanpy as sc

adata = sc.read_h5ad('adata.h5ad')

# Run LIANA with multiple methods
li.mt.rank_aggregate(adata, groupby='cell_type', resource_name='consensus',
                     expr_prop=0.1, verbose=True)

# Get results
liana_results = adata.uns['liana_res']

# Filter significant interactions
sig_interactions = liana_results[liana_results['liana_rank'] < 0.01]

# Visualize
li.pl.dotplot(adata, colour='magnitude_rank', size='specificity_rank',
              source_groups=['Macrophage'], target_groups=['T_cell'])
```

## LIANA with Tensor Decomposition

```python
# Multi-sample/condition analysis
li.mt.rank_aggregate(adata, groupby='cell_type', resource_name='consensus',
                     use_raw=False, verbose=True)

# Build tensor for decomposition
li.multi.build_tensor(adata, sample_key='sample', groupby='cell_type',
                      ligand_key='ligand_complex', receptor_key='receptor_complex')

# Run tensor decomposition
li.multi.decompose_tensor(adata, n_components=5)

# Visualize factor loadings
li.pl.factor_loadings(adata, factor_idx=0)
```

## Related Skills

- single-cell/clustering - Define cell types first
- single-cell/trajectory-inference - Communication along trajectory
- spatial-transcriptomics/spatial-communication - Spatial context
- pathway-analysis/go-enrichment - Pathway enrichment of targets
