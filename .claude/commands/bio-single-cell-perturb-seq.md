# bio-single-cell-perturb-seq

> Analyze Perturb-seq and CROP-seq CRISPR screening data integrated with scRNA-seq. Use when identifying gene function through pooled genetic perturbations in single cells.

## Version Compatibility

Reference examples tested with: MAGeCK 0.5+, pandas 2.2+, pertpy 0.7+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Perturb-seq Analysis

**"Analyze my Perturb-seq CRISPR screen"** → Link guide RNA assignments to transcriptional phenotypes in pooled CRISPR screens with single-cell readout to identify gene function.
- Python: `pertpy.tl.Mixscape(adata)` for perturbation classification, `pertpy.tl.Augur` for prioritization

## Load and Annotate Perturbations

```python
import scanpy as sc
import pertpy as pt

adata = sc.read_h5ad('perturb_seq.h5ad')

# Guide assignments typically stored in obs
# Format: cell barcode -> guide identity -> target gene
adata.obs['guide_id'] = guide_assignments['guide_id']
adata.obs['target_gene'] = guide_assignments['target_gene']

# Mark non-targeting controls
adata.obs['is_control'] = adata.obs['target_gene'] == 'non-targeting'
```

## Pertpy Analysis

```python
# Initialize perturbation analysis
ps = pt.tl.PerturbationSpace(adata)

# Differential expression per perturbation vs control
de = pt.tl.PseudobulkDE(adata)
de.fit(
    groupby='target_gene',
    control='non-targeting',
    n_threads=8
)
results = de.results()

# Filter significant genes
sig_results = results[results['pval_adj'] < 0.05]

# Perturbation signatures (effect sizes)
ps = pt.tl.PerturbationSignature(adata)
ps.compute(groupby='target_gene', control='non-targeting')

# Get signature matrix
signatures = ps.get_signature_matrix()
```

## Perturbation Embedding

```python
# Compute perturbation-level embeddings
pt.tl.perturbation_embedding(adata, groupby='target_gene', method='mean')

# Cluster perturbations by phenotype
pt.tl.cluster_perturbations(adata, resolution=0.5)

# Find functionally related perturbations
pt.pl.perturbation_heatmap(adata, groupby='perturbation_cluster')
```

## Mixscape (Seurat v5)

**Goal:** Classify cells in a CRISPR screen as successfully perturbed or escaped based on their transcriptional response relative to non-targeting controls.

**Approach:** Compute per-cell perturbation signatures against non-targeting controls using PCA-projected differences, then run Mixscape mixture model classification to separate knockout-responsive cells from escapees.

```r
library(Seurat)
library(SeuratObject)

# Load Perturb-seq data
seurat <- Read10X('filtered_feature_bc_matrix/')
seurat <- CreateSeuratObject(seurat)

# Add perturbation metadata
seurat <- AddMetaData(seurat, metadata = perturbation_calls)

# Standard preprocessing
seurat <- NormalizeData(seurat)
seurat <- FindVariableFeatures(seurat)
seurat <- ScaleData(seurat)
seurat <- RunPCA(seurat)
seurat <- RunUMAP(seurat, dims = 1:30)

# Mixscape: Classify perturbed vs non-perturbed cells
seurat <- CalcPerturbSig(
    seurat,
    assay = 'RNA',
    slot = 'data',
    new.assay.name = 'PRTB',
    gd.class = 'gene',
    nt.cell.class = 'NT',
    num.neighbors = 20,
    reduction = 'pca',
    ndims = 15
)

# Run Mixscape classification
seurat <- RunMixscape(
    seurat,
    assay = 'PRTB',
    slot = 'scale.data',
    labels = 'gene',
    nt.class.name = 'NT',
    min.de.genes = 5,
    iter.num = 10,
    de.assay = 'RNA',
    prtb.type = 'KO'
)

# View classification results
table(seurat$mixscape_class.global)
```

## Mixscape Visualization

```r
# UMAP colored by perturbation
DimPlot(seurat, reduction = 'umap', group.by = 'mixscape_class', label = TRUE)

# Perturbation score distribution
VlnPlot(seurat, features = 'mixscape_class_p_ko', group.by = 'gene')

# DE genes for each perturbation
MixscapeHeatmap(seurat, ident.1 = 'TP53', ident.2 = 'NT', balanced = TRUE)

# LDA projection
seurat <- MixscapeLDA(seurat, labels = 'gene', nt.class.name = 'NT')
LDAPlot(seurat)
```

## Guide Assignment from CRISPR Feature Barcode

```python
import pandas as pd

# From Cell Ranger output (CRISPR Guide Capture)
guides = pd.read_csv('crispr_analysis/protospacer_calls_per_cell.csv')

# Clean up guide calls
guides['cell_barcode'] = guides['cell_barcode'].str.replace('-1', '')
guides = guides[guides['num_features'] == 1]  # Single guide per cell

# Merge with expression data
adata.obs = adata.obs.merge(
    guides[['cell_barcode', 'feature_call', 'target_gene']],
    left_index=True,
    right_on='cell_barcode',
    how='left'
)
```

## Guide Quality Control

```python
# Check guide representation
guide_counts = adata.obs['target_gene'].value_counts()
print(f'Guides per target: {guide_counts.mean():.1f}')
print(f'Cells per guide: {adata.obs.groupby("guide_id").size().mean():.1f}')

# Filter low-representation guides
# Standard: keep guides with >= 100 cells
min_cells = 100
valid_guides = guide_counts[guide_counts >= min_cells].index
adata = adata[adata.obs['target_gene'].isin(valid_guides)]

# Check for guide bias
sc.pl.violin(adata, keys='n_genes_by_counts', groupby='target_gene', rotation=90)
```

## Multi-Guide Analysis

```python
# Cells with multiple guides (MOI > 1)
multi_guide = adata.obs[adata.obs['num_guides'] > 1]
print(f'Multi-guide cells: {len(multi_guide) / len(adata):.1%}')

# Options:
# 1. Remove multi-guide cells
adata = adata[adata.obs['num_guides'] == 1]

# 2. Keep only cells where guides target same gene
# 3. Analyze combinatorial effects
```

## Pseudobulk Differential Expression

```python
# Aggregate to pseudobulk for robust DE
from pertpy.tools import PseudobulkDE

pb = PseudobulkDE(adata)
pb.fit(
    groupby='target_gene',
    control='non-targeting',
    method='deseq2',  # or 'edger', 'wilcoxon'
    min_cells=50
)

# Get results for specific perturbation
tp53_de = pb.results('TP53')
sig_genes = tp53_de[tp53_de['padj'] < 0.05].sort_values('log2FoldChange')
```

## Pathway Enrichment

```python
import decoupler as dc

# Get DE genes per perturbation
de_results = pb.results()

# Run pathway enrichment
dc.run_ora(
    mat=de_results,
    net=dc.get_resource('MSigDB'),
    source='geneset',
    target='gene'
)

# Visualize top pathways
dc.plot_barplot(de_results, 'TP53', top_n=20)
```

## Screen QC Metrics

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Cells per guide | >200 | 100-200 | <100 |
| Guide detection rate | >90% | 80-90% | <80% |
| Non-targeting cells | 5-15% | 15-25% | >25% |
| Mixscape KO fraction | >50% | 30-50% | <30% |

## Related Skills

- single-cell/preprocessing - scRNA-seq preprocessing
- single-cell/markers-annotation - DE and marker gene concepts
- single-cell/batch-integration - Multi-sample integration
- crispr-screens/mageck-analysis - Bulk screen analysis
