# bio-single-cell-cell-annotation

> Automated cell type annotation using reference-based methods including CellTypist, scPred, SingleR, and Azimuth for consistent, reproducible cell labeling. Use when automatically annotating cell types using reference datasets.

## Version Compatibility

Reference examples tested with: pandas 2.2+, scanpy 1.10+, scikit-learn 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Automated Cell Type Annotation

## CellTypist (Python)

**Goal:** Automatically annotate cell types using a pre-trained or custom CellTypist model.

**Approach:** Load a reference model, predict cell types with majority voting for cluster-level consensus, and add predictions to AnnData.

**"Automatically label my cell types"** → Apply a trained classifier to assign cell type identities based on transcriptomic similarity to a reference atlas.

```python
import celltypist
import scanpy as sc

adata = sc.read_h5ad('adata_processed.h5ad')

# List available models
celltypist.models.models_description()

# Download model
celltypist.models.download_models(model='Immune_All_Low.pkl')

# Load model
model = celltypist.models.Model.load(model='Immune_All_Low.pkl')

# Predict cell types
predictions = celltypist.annotate(adata, model=model, majority_voting=True)

# Add predictions to adata
adata = predictions.to_adata()

# Access predictions
adata.obs['cell_type_celltypist'] = adata.obs['majority_voting']
adata.obs['cell_type_confidence'] = adata.obs['conf_score']

# Visualize
sc.pl.umap(adata, color=['cell_type_celltypist', 'conf_score'])
```

## CellTypist with Custom Model

**Goal:** Train a custom CellTypist model on a reference dataset for domain-specific annotation.

**Approach:** Train a logistic regression classifier on labeled reference data with feature selection, then apply to query data.

```python
# Train custom model
new_model = celltypist.train(adata_reference, labels='cell_type', n_jobs=10,
                              feature_selection=True, use_SGD=True)

# Save model
new_model.write('custom_model.pkl')

# Use custom model
predictions = celltypist.annotate(adata_query, model='custom_model.pkl')
```

## SingleR (R)

**Goal:** Annotate cell types by correlating expression profiles against curated reference datasets.

**Approach:** Compare each cell's expression to reference transcriptomes using SingleR's correlation-based assignment, with pruning for low-confidence calls.

```r
library(SingleR)
library(celldex)
library(Seurat)
library(SingleCellExperiment)

seurat_obj <- readRDS('seurat_processed.rds')
sce <- as.SingleCellExperiment(seurat_obj)

# Load reference (multiple available)
ref <- celldex::HumanPrimaryCellAtlasData()
# Other options:
# ref <- celldex::BlueprintEncodeData()
# ref <- celldex::MonacoImmuneData()
# ref <- celldex::ImmGenData()  # mouse

# Run SingleR
pred <- SingleR(test = sce, ref = ref, labels = ref$label.main, de.method = 'wilcox')

# Add to Seurat
seurat_obj$SingleR_labels <- pred$labels
seurat_obj$SingleR_pruned <- pred$pruned.labels

# Check annotation quality
plotScoreHeatmap(pred)
plotDeltaDistribution(pred)
```

## SingleR Fine Labels

```r
# Use fine-grained labels
pred_fine <- SingleR(test = sce, ref = ref, labels = ref$label.fine)

# Combine multiple references
ref1 <- celldex::BlueprintEncodeData()
ref2 <- celldex::MonacoImmuneData()
pred_combined <- SingleR(test = sce, ref = list(BP = ref1, Monaco = ref2),
                          labels = list(ref1$label.main, ref2$label.main))
```

## Azimuth (R/Seurat)

**Goal:** Annotate cell types using Seurat's Azimuth reference-mapping framework.

**Approach:** Map query cells onto a pre-built Azimuth reference atlas to transfer cell type labels with confidence scores.

```r
library(Seurat)
library(Azimuth)

seurat_obj <- readRDS('seurat_processed.rds')

# Run Azimuth with PBMC reference
seurat_obj <- RunAzimuth(seurat_obj, reference = 'pbmcref')

# Available references: pbmcref, bonemarrowref, lungref, etc.

# Access predictions
seurat_obj$azimuth_labels <- seurat_obj$predicted.celltype.l2
seurat_obj$azimuth_score <- seurat_obj$predicted.celltype.l2.score

# Visualize
DimPlot(seurat_obj, group.by = 'azimuth_labels', label = TRUE) + NoLegend()
FeaturePlot(seurat_obj, features = 'predicted.celltype.l2.score')
```

## scPred (R)

**Goal:** Train and apply a supervised classifier for cell type prediction using scPred.

**Approach:** Extract informative PCA features from a labeled reference, train an SVM/RF classifier, and predict cell types on query data.

```r
library(scPred)
library(Seurat)

# Train on reference
reference <- readRDS('reference_seurat.rds')
reference <- getFeatureSpace(reference, 'cell_type')
reference <- trainModel(reference)

# Get training probabilities
get_probabilities(reference)
get_scpred(reference)

# Plot model performance
plot_probabilities(reference)

# Predict on query
query <- readRDS('query_seurat.rds')
query <- scPredict(query, reference)

# Results
query$scpred_prediction
query$scpred_max
```

## Annotation Confidence Filtering

```python
# CellTypist: filter low confidence
high_conf = adata[adata.obs['conf_score'] > 0.5].copy()

# Flag uncertain cells
adata.obs['annotation_uncertain'] = adata.obs['conf_score'] < 0.3
```

```r
# SingleR: use pruned labels (low-quality removed)
seurat_obj$final_labels <- ifelse(is.na(pred$pruned.labels), 'Unknown', pred$labels)

# Azimuth: filter by score
seurat_obj$high_conf_labels <- ifelse(seurat_obj$predicted.celltype.l2.score > 0.7,
                                       seurat_obj$predicted.celltype.l2, 'Low_confidence')
```

## Consensus Annotation

**Goal:** Combine predictions from multiple annotation tools into a single consensus label per cell.

**Approach:** Aggregate labels from SingleR, Azimuth, and CellTypist using majority voting, flagging ambiguous cells where methods disagree.

```r
# Combine multiple methods
annotations <- data.frame(
    SingleR = seurat_obj$SingleR_labels,
    Azimuth = seurat_obj$azimuth_labels,
    CellTypist = seurat_obj$celltypist_labels
)

# Majority vote
get_consensus <- function(x) {
    tbl <- table(x)
    if (max(tbl) >= 2) names(which.max(tbl)) else 'Ambiguous'
}
seurat_obj$consensus_label <- apply(annotations, 1, get_consensus)
```

## Compare Annotations

**Goal:** Quantitatively assess agreement between different annotation methods.

**Approach:** Compute adjusted Rand index and normalized mutual information between label sets, and build a confusion matrix.

```python
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# Compare two annotations
ari = adjusted_rand_score(adata.obs['manual_annotation'], adata.obs['celltypist'])
nmi = normalized_mutual_info_score(adata.obs['manual_annotation'], adata.obs['celltypist'])

# Confusion matrix
pd.crosstab(adata.obs['manual_annotation'], adata.obs['celltypist'])
```

## Marker-Based Validation

```r
# Validate predictions with known markers
canonical_markers <- list(
    T_cell = c('CD3D', 'CD3E', 'CD4', 'CD8A'),
    B_cell = c('CD19', 'MS4A1', 'CD79A'),
    Monocyte = c('CD14', 'LYZ', 'S100A8'),
    NK = c('NKG7', 'GNLY', 'NCAM1')
)

# Check marker expression per predicted type
DotPlot(seurat_obj, features = unlist(canonical_markers), group.by = 'predicted_labels') +
    RotatedAxis()
```

## Related Skills

- single-cell/clustering - Manual marker-based annotation
- single-cell/cell-communication - Use annotated types for CCC
- single-cell/trajectory-inference - Trajectory on annotated data
