# tooluniverse-single-cell

> Production-ready single-cell and expression matrix analysis using scanpy, anndata, and scipy. Performs scRNA-seq QC, normalization, PCA, UMAP, Leiden/Louvain clustering, differential expression (Wilcoxon, t-test, DESeq2), cell type annotation, per-cell-type statistical analysis, gene-expression correlation, batch correction (Harmony), trajectory inference, and cell-cell communication analysis. NEW: Analyzes ligand-receptor interactions between cell types using OmniPath (CellPhoneDB, CellChatDB), scores communication strength, identifies signaling cascades, and handles multi-subunit receptor complexes. Integrates with ToolUniverse gene annotation tools (HPA, Ensembl, MyGene, UniProt) and enrichment tools (gseapy, PANTHER, STRING). Supports h5ad, 10X, CSV/TSV count matrices, and pre-annotated datasets. Use when analyzing single-cell RNA-seq data, studying cell-cell interactions, performing cell type differential expression, computing gene-expression correlations by cell type, analyzing tumor-immune communication, or answering questions about scRNA-seq datasets.

# Single-Cell Genomics and Expression Matrix Analysis

Comprehensive single-cell RNA-seq analysis and expression matrix processing using scanpy, anndata, scipy, and ToolUniverse. Designed for both full scRNA-seq workflows (raw counts to annotated cell types) and targeted expression-level analyses (per-cell-type DE, correlation, ANOVA, clustering).

**IMPORTANT**: This skill handles complex multi-workflow analysis. Most implementation details have been moved to `references/` for progressive disclosure. This document focuses on high-level decision-making and workflow orchestration.

---

## When to Use This Skill

Apply when users:
- Have scRNA-seq data (h5ad, 10X, CSV count matrices) and want analysis
- Ask about cell type identification, clustering, or annotation
- Need differential expression analysis by cell type or condition
- Want gene-expression correlation analysis (e.g., gene length vs expression by cell type)
- Ask about PCA, UMAP, t-SNE for expression data
- Need Leiden/Louvain clustering on expression matrices
- Want statistical comparisons between cell types (t-test, ANOVA, fold change)
- Ask about marker genes for cell populations
- Need batch correction (Harmony, combat)
- Want trajectory or pseudotime analysis
- Ask about cell-cell communication (ligand-receptor interactions)
- Questions mention "single-cell", "scRNA-seq", "cell type", "h5ad"
- Questions involve immune cell types (CD4, CD8, CD14, CD19, monocytes, etc.)

**BixBench Coverage**: 18+ questions across 5 projects (bix-22, bix-27, bix-31, bix-33, bix-36)

**NOT for** (use other skills instead):
- Bulk RNA-seq DESeq2 analysis only → Use `tooluniverse-rnaseq-deseq2`
- Gene enrichment only (no expression data) → Use `tooluniverse-gene-enrichment`
- VCF/variant analysis → Use `tooluniverse-variant-analysis`
- Statistical modeling (regression, survival) → Use `tooluniverse-statistical-modeling`

---

## Core Principles

1. **Data-first approach** - Load, inspect, and validate data before any analysis
2. **AnnData-centric** - All data flows through anndata objects for consistency
3. **Cell type awareness** - Many questions require per-cell-type subsetting and analysis
4. **Statistical rigor** - Proper normalization, multiple testing correction, effect sizes
5. **Scanpy standard pipeline** - Follow established best practices for scRNA-seq
6. **Flexible input** - Handle h5ad, 10X, CSV/TSV, pre-processed and raw data
7. **Question-driven** - Parse what the user is actually asking and extract the specific answer
8. **Enrichment integration** - Chain DE results into GO/KEGG/Reactome enrichment when requested
9. **Large dataset support** - Efficient handling of datasets with >100k cells

---

## Required Python Packages

```python
# Core (MUST be installed)
import scanpy as sc
import anndata as ad
import pandas as pd
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.multitest import multipletests

# Enrichment (for GO/KEGG/Reactome follow-up)
import gseapy as gp

# Optional
import harmonypy  # batch correction
```

**Installation**:
```bash
pip install scanpy anndata leidenalg umap-learn harmonypy gseapy pandas numpy scipy scikit-learn statsmodels
```

---

## High-Level Workflow Decision Tree

```
START: User question about scRNA-seq data
│
├─ Q1: What type of analysis is needed?
│  │
│  ├─ FULL PIPELINE (raw counts → annotated clusters)
│  │  └─ Workflow: QC → Normalize → HVG → PCA → Cluster → Annotate → DE
│  │     See: references/scanpy_workflow.md
│  │
│  ├─ DIFFERENTIAL EXPRESSION (per-cell-type comparison)
│  │  └─ Workflow: Load → Normalize → Per-CT DE → Report
│  │     Pattern: Most common BixBench pattern (bix-33)
│  │     See: Section "Per-Cell-Type Differential Expression" below
│  │
│  ├─ CORRELATION ANALYSIS (gene property vs expression)
│  │  └─ Workflow: Load → Filter genes → Compute correlation
│  │     Pattern: Gene length vs expression (bix-22)
│  │     See: Section "Statistical Analysis on Expression Data" below
│  │
│  ├─ CLUSTERING & PCA (expression matrix analysis)
│  │  └─ Workflow: Load → Transform → PCA/Cluster → Report
│  │     See: references/clustering_guide.md
│  │
│  ├─ CELL COMMUNICATION (ligand-receptor interactions)
│  │  └─ Workflow: Load → Get L-R pairs → Score → Identify signaling
│  │     See: references/cell_communication.md (DETAILED)
│  │
│  └─ TRAJECTORY ANALYSIS (pseudotime)
│     └─ Workflow: Load → Normalize → Trajectory → Pseudotime
│        See: references/trajectory_analysis.md
│
├─ Q2: What data format is available?
│  ├─ h5ad file → sc.read_h5ad() → Check contents (counts, metadata, clusters)
│  ├─ 10X files → sc.read_10x_mtx() or sc.read_10x_h5()
│  ├─ CSV/TSV → pd.read_csv() → Convert to AnnData (check orientation!)
│  └─ Other → See: references/scanpy_workflow.md "Data Loading"
│
└─ Q3: Are there pre-computed results to use?
   ├─ Has cell type annotations → Skip clustering, go to analysis
   ├─ Has PCA/UMAP → Skip dimensionality reduction
   ├─ Has DE results → Skip DE, analyze results
   └─ Raw counts only → Full pipeline needed
```

---

## Common Analysis Patterns (BixBench)

### Pattern 1: Per-Cell-Type Differential Expression

**Question**: "Which immune cell type has the most DEGs after treatment?"

**Workflow**:
```python
import scanpy as sc

# Load and normalize
adata = sc.read_h5ad("data.h5ad")
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# Per-cell-type DE
cell_types = adata.obs['cell_type'].unique()
de_results = {}

for ct in cell_types:
    adata_ct = adata[adata.obs['cell_type'] == ct].copy()

    # Check sufficient cells
    n_treat = (adata_ct.obs['condition'] == 'treatment').sum()
    n_ctrl = (adata_ct.obs['condition'] == 'control').sum()
    if n_treat < 3 or n_ctrl < 3:
        continue

    # Run DE
    sc.tl.rank_genes_groups(adata_ct, groupby='condition',
                             groups=['treatment'], reference='control',
                             method='wilcoxon')
    df = sc.get.rank_genes_groups_df(adata_ct, group='treatment')

    # Count significant
    sig = df[df['pvals_adj'] < 0.05]
    de_results[ct] = {'n_sig': len(sig), 'results': df}
    print(f"{ct}: {len(sig)} DEGs")

# Answer: Which has most?
top_ct = max(de_results, key=lambda x: de_results[x]['n_sig'])
print(f"Answer: {top_ct} ({de_results[top_ct]['n_sig']} DEGs)")
```

**BixBench**: bix-33

**See**: references/scanpy_workflow.md "Differential Expression"

### Pattern 2: Gene Property vs Expression Correlation

**Question**: "What is the Pearson correlation between gene length and expression in CD4 T cells?"

**Workflow**:
```python
import scanpy as sc
import pandas as pd
import numpy as np
from scipy import stats
from scipy.sparse import issparse

# Load data
adata = sc.read_h5ad("data.h5ad")

# Load gene annotations
gene_info = pd.read_csv("gene_info.tsv", sep='\t', index_col=0)
common = adata.var_names.intersection(gene_info.index)
adata.var['gene_length'] = gene_info.loc[common, 'gene_length'].reindex(adata.var_names)
adata.var['gene_type'] = gene_info.loc[common, 'gene_type'].reindex(adata.var_names)

# Filter to protein-coding genes
mask = adata.var['gene_type'] == 'protein_coding'
adata_pc = adata[:, mask].copy()

# Per-cell-type correlation
cell_types = ['CD4 T cells', 'CD8 T cells', 'CD14 Monocytes']  # etc.

for ct in cell_types:
    adata_ct = adata_pc[adata_pc.obs['cell_type'] == ct]

    # Mean expression per gene
    X = adata_ct.X.toarray() if issparse(adata_ct.X) else adata_ct.X
    mean_expr = np.mean(X, axis=0)
    gene_lengths = adata_ct.var['gene_length'].values

    # Remove NaN
    valid = ~np.isnan(gene_lengths) & ~np.isnan(mean_expr)

    # Pearson correlation
    r, p = stats.pearsonr(gene_lengths[valid], mean_expr[valid])
    print(f"{ct}: r = {r:.6f}, p = {p:.2e}, n = {valid.sum()} genes")
```

**BixBench**: bix-22

**See**: SKILL_OLD.md "Phase 6: Statistical Analysis on Expression Data"

### Pattern 3: PCA on Expression Matrix

**Question**: "What percentage of variance is explained by PC1 after log10 transform?"

**Workflow**:
```python
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

# Load expression matrix
df = pd.read_csv("expression.csv", index_col=0)

# Orient: samples as rows, genes as columns
if df.shape[0] > df.shape[1] * 5:
    df = df.T  # Genes were rows, transpose

# Log10 transform with pseudocount
X = np.log10(df.values + 1)

# Run PCA
n_components = min(X.shape[0], X.shape[1])
pca = PCA(n_components=n_components)
pca.fit(X)

# Variance explained
print(f"PC1: {pca.explained_variance_ratio_[0]*100:.2f}% variance")
print(f"PC1+PC2: {sum(pca.explained_variance_ratio_[:2])*100:.2f}%")
print(f"Top 10 PCs: {sum(pca.explained_variance_ratio_[:10])*100:.2f}%")
```

**BixBench**: bix-27

**See**: references/clustering_guide.md "PCA Analysis"

### Pattern 4: Statistical Comparison Between Cell Types

**Question**: "What is the t-statistic comparing LFCs between CD4/CD8 and other cell types?"

**Workflow**:
```python
from scipy import stats

# After running per-cell-type DE (Pattern 1):
# Extract LFCs for different cell type groups

# Group 1: CD4/CD8 cells
cd4_lfc = de_results['CD4 T cells']['results']['log2FoldChange'].values
cd8_lfc = de_results['CD8 T cells']['results']['log2FoldChange'].values
cd4_cd8_lfc = np.concatenate([cd4_lfc, cd8_lfc])

# Group 2: Other cells
other_lfc = []
for ct in ['CD14 Monocytes', 'NK cells', 'B cells']:
    other_lfc.append(de_results[ct]['results']['log2FoldChange'].values)
other_lfc = np.concatenate(other_lfc)

# Welch's t-test (unequal variances)
t_stat, p_val = stats.ttest_ind(cd4_cd8_lfc, other_lfc, equal_var=False)
print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_val:.4e}")
```

**BixBench**: bix-31

**See**: SKILL_OLD.md "Phase 6.3: T-Tests Between Groups"

### Pattern 5: ANOVA Across Cell Types

**Question**: "What is the F-statistic for miRNA expression across immune cell types?"

**Workflow**:
```python
import pandas as pd
from scipy import stats

# Load miRNA expression
df = pd.read_csv("mirna_expr.csv", index_col=0)
meta = pd.read_csv("metadata.csv", index_col=0)

# Exclude PBMCs
meta_filtered = meta[meta['cell_type'] != 'PBMC']
df_filtered = df[meta_filtered.index]

# Group by cell type
cell_types = meta_filtered['cell_type'].unique()
groups = {}
for ct in cell_types:
    samples = meta_filtered[meta_filtered['cell_type'] == ct].index
    groups[ct] = df_filtered[samples].values.flatten()

# One-way ANOVA
f_stat, p_val = stats.f_oneway(*groups.values())
print(f"F-statistic: {f_stat:.4f}")
print(f"p-value: {p_val:.4e}")
```

**BixBench**: bix-36

**See**: SKILL_OLD.md "Phase 6.4: ANOVA Across Groups"

### Pattern 6: Cell-Cell Communication Analysis

**Question**: "Which ligand-receptor interactions are strongest between tumor and T cells?"

**Workflow**:
```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Step 1: Get ligand-receptor pairs from OmniPath
result = tu.run_tool(
    "OmniPath_get_ligand_receptor_interactions",
    databases="CellPhoneDB,CellChatDB"
)
lr_pairs = pd.DataFrame(result['data']['interactions'])

# Step 2: Filter to expressed pairs
# (genes present in dataset, mean expression > 0.05)
expressed_lr = lr_pairs[
    lr_pairs['source_genesymbol'].isin(adata.var_names) &
    lr_pairs['target_genesymbol'].isin(adata.var_names)
]

# Step 3: Score communication between cell types
# (mean ligand expr in sender * mean receptor expr in receiver)
communication_scores = score_cell_communication(
    adata, expressed_lr, cell_type_col='cell_type'
)

# Step 4: Filter to tumor-T cell interactions
tumor_tcell = communication_scores[
    ((communication_scores['sender'] == 'Tumor') &
     (communication_scores['receiver'].str.contains('T cell'))) |
    ((communication_scores['receiver'] == 'Tumor') &
     (communication_scores['sender'].str.contains('T cell')))
]

# Step 5: Top interactions
top_interactions = tumor_tcell.nlargest(20, 'score')
print(top_interactions[['sender', 'receiver', 'ligand', 'receptor', 'score']])
```

**See**: references/cell_communication.md (COMPLETE workflow with all helper functions)

---

## Scanpy vs Seurat Equivalents

For users familiar with Seurat (R):

| Operation | Seurat (R) | Scanpy (Python) |
|-----------|------------|-----------------|
| Load data | `Read10X()` | `sc.read_10x_mtx()` |
| Normalize | `NormalizeData()` | `sc.pp.normalize_total() + sc.pp.log1p()` |
| Find HVGs | `FindVariableFeatures()` | `sc.pp.highly_variable_genes()` |
| Scale | `ScaleData()` | `sc.pp.scale()` |
| PCA | `RunPCA()` | `sc.tl.pca()` |
| Neighbors | `FindNeighbors()` | `sc.pp.neighbors()` |
| Cluster | `FindClusters()` | `sc.tl.leiden()` or `sc.tl.louvain()` |
| UMAP | `RunUMAP()` | `sc.tl.umap()` |
| Find markers | `FindMarkers()` | `sc.tl.rank_genes_groups()` |
| DE test | `FindMarkers(test.use="wilcox")` | `method='wilcoxon'` |
| Batch correction | `RunHarmony()` | `harmonypy.run_harmony()` |

**See**: references/seurat_workflow.md for complete Seurat → Scanpy translation

---

## When to Use ToolUniverse Tools

### Gene Annotation and Validation
- **HPA_search_genes_by_query**: Search for cell-type marker genes
- **MyGene_query_genes** / **MyGene_batch_query**: Gene ID conversion, gene info
- **ensembl_lookup_gene**: Get Ensembl gene details
- **UniProt_get_function_by_accession**: Protein function lookup

### Cell-Cell Communication (NEW)
- **OmniPath_get_ligand_receptor_interactions**: Get validated L-R pairs (CellPhoneDB, CellChatDB)
- **OmniPath_get_signaling_interactions**: Downstream signaling cascades
- **OmniPath_get_complexes**: Multi-subunit receptor composition
- **OmniPath_get_cell_communication_annotations**: Pathway categories

### Enrichment Analysis (Post-DE)
- **PANTHER_enrichment**: GO enrichment (BP, MF, CC) with curation
- **STRING_functional_enrichment**: Network-based enrichment
- **ReactomeAnalysis_pathway_enrichment**: Curated Reactome pathways

**See**: references/cell_communication.md for complete OmniPath integration examples

---

## Data Loading Best Practices

### Critical: Matrix Orientation

AnnData expects: **cells/samples as rows (obs), genes as columns (var)**

```python
import scanpy as sc
import pandas as pd
import anndata as ad

# Load h5ad (already oriented)
adata = sc.read_h5ad("data.h5ad")

# Load CSV/TSV (check orientation!)
df = pd.read_csv("counts.csv", index_col=0)

# Heuristic: If genes > samples by 5x, transpose
if df.shape[0] > df.shape[1] * 5:
    print("Transposing: genes were rows")
    df = df.T

adata = ad.AnnData(df)
```

### Load Metadata
```python
meta = pd.read_csv("metadata.csv", index_col=0)
# Align indices
common = adata.obs_names.intersection(meta.index)
adata = adata[common].copy()
for col in meta.columns:
    adata.obs[col] = meta.loc[common, col]
```

**See**: references/scanpy_workflow.md "Phase 1: Data Loading"

---

## Quality Control Checklist

```python
# QC metrics
adata.var['mt'] = adata.var_names.str.startswith(('MT-', 'mt-'))
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

# Filter cells
sc.pp.filter_cells(adata, min_genes=200)  # Min genes per cell
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()  # Max mito %

# Filter genes
sc.pp.filter_genes(adata, min_cells=3)  # Min cells per gene

print(f"After QC: {adata.n_obs} cells x {adata.n_vars} genes")
```

**See**: references/scanpy_workflow.md "Phase 2: Quality Control"

---

## Differential Expression Decision Tree

```
Q: What type of DE analysis?

Single-Cell DE (many cells per condition):
├─ Use: sc.tl.rank_genes_groups()
├─ Methods: wilcoxon (default), t-test, logreg
├─ Best for: Per-cell-type DE, marker gene finding
└─ See: references/scanpy_workflow.md "Differential Expression"

Pseudo-Bulk DE (aggregate counts by sample):
├─ Use: DESeq2 via PyDESeq2
├─ Best for: Sample-level comparisons, replicates
└─ See: SKILL_OLD.md "Phase 5.3: DESeq2-based DE"

Statistical Tests Only:
├─ Use: scipy.stats (ttest_ind, f_oneway, pearsonr)
├─ Best for: Correlation, ANOVA, t-tests on summaries
└─ See: "Statistical Analysis on Expression Data" below
```

---

## Statistical Analysis on Expression Data

For BixBench questions requiring specific statistical tests:

### Pearson/Spearman Correlation
```python
from scipy import stats

# Gene property vs expression
r, p = stats.pearsonr(gene_lengths, mean_expression)
r_s, p_s = stats.spearmanr(gene_lengths, mean_expression)
```

### T-Tests
```python
# Welch's t-test (unequal variance)
t_stat, p_val = stats.ttest_ind(group1, group2, equal_var=False)

# Student's t-test (equal variance)
t_stat, p_val = stats.ttest_ind(group1, group2, equal_var=True)
```

### ANOVA
```python
# One-way ANOVA across multiple groups
f_stat, p_val = stats.f_oneway(group1, group2, group3, ...)
```

### Multiple Testing Correction
```python
from statsmodels.stats.multitest import multipletests

# Benjamini-Hochberg (FDR)
reject, pvals_adj, _, _ = multipletests(pvals, method='fdr_bh')

# Bonferroni
reject, pvals_adj, _, _ = multipletests(pvals, method='bonferroni')
```

**See**: SKILL_OLD.md "Phase 6: Statistical Analysis on Expression Data" for complete examples

---

## Marker Gene Identification

```python
# Find marker genes for each cluster
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')

# Get results for cluster 0
markers = sc.get.rank_genes_groups_df(adata, group='0')
top_markers = markers.head(10)

# Annotate clusters using markers
marker_dict = {
    'T cells': ['CD3D', 'CD3E', 'CD8A'],
    'B cells': ['CD19', 'MS4A1', 'CD79A'],
    'Monocytes': ['CD14', 'LYZ', 'S100A9'],
}
# Score and assign cell types
```

**See**: references/marker_identification.md for complete workflow

---

## Batch Correction with Harmony

```python
import harmonypy

# After PCA
sc.tl.pca(adata, n_comps=50)

# Run Harmony on PCA
ho = harmonypy.run_harmony(
    adata.obsm['X_pca'][:, :30],
    adata.obs,
    'batch',  # batch column
    random_state=0
)

# Store corrected PCs
adata.obsm['X_pca_harmony'] = ho.Z_corr.T

# Re-cluster on corrected PCs
sc.pp.neighbors(adata, use_rep='X_pca_harmony')
sc.tl.leiden(adata, resolution=0.5)
sc.tl.umap(adata)
```

**See**: references/scanpy_workflow.md "Batch Correction"

---

## Report Generation

Always extract the specific answer to the user's question:

```python
# Example: "Which cell type has the most DEGs?"
report = f"""
# Analysis Results

## Per-Cell-Type Differential Expression

| Cell Type | Significant DEGs (padj < 0.05) |
|-----------|-------------------------------|
{chr(10).join([f"| {ct} | {res['n_sig']} |" for ct, res in de_results.items()])}

## Answer

**{top_ct}** has the highest number of significantly differentially expressed
genes with **{de_results[top_ct]['n_sig']} DEGs** (Wilcoxon test, BH-corrected
p < 0.05).
"""
```

---

## Troubleshooting Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: leidenalg` | `pip install leidenalg` |
| Sparse matrix errors | Use `.toarray()`: `X = adata.X.toarray() if issparse(adata.X) else adata.X` |
| Wrong matrix orientation | Check: more genes than samples? Transpose if needed |
| NaN in correlation | Filter: `valid = ~np.isnan(x) & ~np.isnan(y)` |
| Too few cells for DE | Need >= 3 cells per condition per cell type |
| Gene names don't match | Use MyGene for ID conversion |
| Memory error (large datasets) | Use `sc.pp.highly_variable_genes()` to reduce features |

**See**: references/troubleshooting.md for detailed solutions

---

## Reference Documentation

**Core Workflows**:
- **references/scanpy_workflow.md** - Complete scanpy pipeline (QC, normalize, PCA, cluster, DE)
- **references/seurat_workflow.md** - Seurat → Scanpy translation guide
- **references/clustering_guide.md** - Leiden, Louvain, hierarchical, bootstrap consensus
- **references/marker_identification.md** - Marker genes, cell type annotation
- **references/trajectory_analysis.md** - Pseudotime, trajectory inference

**Advanced Topics**:
- **references/cell_communication.md** - Complete OmniPath/CellPhoneDB workflow (L-R interactions, signaling)
- **references/troubleshooting.md** - Common errors, package issues, data format problems

**Utility Scripts**:
- **scripts/qc_metrics.py** - QC calculations, filtering thresholds
- **scripts/normalize_data.py** - Normalization methods
- **scripts/find_markers.py** - Marker gene identification

---

## Complete Workflow Example

```python
import scanpy as sc

# 1. Load data
adata = sc.read_10x_h5("filtered_feature_bc_matrix.h5")

# 2. QC
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# 3. Normalize
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata.copy()

# 4. HVG + PCA
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.tl.pca(adata, n_comps=50)

# 5. Cluster
sc.pp.neighbors(adata, n_pcs=30)
sc.tl.leiden(adata, resolution=0.5)
sc.tl.umap(adata)

# 6. Find markers
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')
markers = sc.get.rank_genes_groups_df(adata, group='0')

# 7. Annotate (manual or automatic)
# 8. Per-cell-type DE (if conditions present)
# 9. Cell communication analysis (if needed)
```

**See**: references/scanpy_workflow.md for detailed explanations of each step

---

## Summary

This skill provides:
1. Complete scRNA-seq pipeline (QC → clustering → annotation → DE)
2. Per-cell-type differential expression with multiple methods
3. Gene property correlation analysis by cell type
4. Statistical comparisons (t-test, ANOVA, correlation)
5. Expression matrix clustering (hierarchical, bootstrap consensus, PCA)
6. Cell-cell communication analysis (OmniPath, CellPhoneDB, CellChatDB)
7. Batch correction (Harmony, ComBat)
8. Trajectory inference and pseudotime
9. Integration with ToolUniverse for annotation and enrichment

**BixBench Coverage**: 18+ questions across 5 projects (bix-22, bix-27, bix-31, bix-33, bix-36)

**For detailed workflows, see references/ directory.**
