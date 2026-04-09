# bio-single-cell-data-io

> Read, write, and create single-cell data objects using Seurat (R) and Scanpy (Python). Use for loading 10X Genomics data, importing/exporting h5ad and RDS files, creating Seurat objects and AnnData objects, and converting between formats. Use when loading, saving, or converting single-cell data formats.

## Version Compatibility

Reference examples tested with: Cell Ranger 8.0+, anndata 0.10+, numpy 1.26+, pandas 2.2+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Single-Cell Data I/O

Read, write, and create single-cell data objects for analysis.

## Scanpy (Python)

**Goal:** Load, create, and save single-cell data objects using Scanpy and AnnData.

**Approach:** Read 10X Genomics output, CSV, or Loom formats into AnnData objects, manipulate metadata and layers, and write to h5ad format.

**"Load my 10X data"** → Read Cell Ranger output directory or h5 file into an AnnData object with expression matrix, cell barcodes, and gene annotations.

### Required Imports

```python
import scanpy as sc
import anndata as ad
import pandas as pd
import numpy as np
```

### Reading 10X Genomics Data

```python
# Read 10X cellranger output (filtered_feature_bc_matrix directory)
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/', var_names='gene_symbols', cache=True)
print(f'Loaded {adata.n_obs} cells x {adata.n_vars} genes')

# Read 10X h5 file directly
adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
```

### AnnData Object Structure

```python
# AnnData stores:
# - adata.X: expression matrix (cells x genes)
# - adata.obs: cell metadata (DataFrame)
# - adata.var: gene metadata (DataFrame)
# - adata.uns: unstructured annotations (dict)
# - adata.obsm: cell embeddings (PCA, UMAP)
# - adata.varm: gene embeddings
# - adata.obsp: cell-cell graphs
# - adata.layers: alternative matrices (raw counts, normalized)

print(f'Shape: {adata.shape}')
print(f'Cell metadata: {adata.obs.columns.tolist()}')
print(f'Gene metadata: {adata.var.columns.tolist()}')
```

### Creating AnnData from Matrix

```python
import anndata as ad
import numpy as np
import pandas as pd

counts = np.random.poisson(1, size=(100, 500))  # 100 cells x 500 genes
cell_ids = [f'cell_{i}' for i in range(100)]
gene_ids = [f'gene_{i}' for i in range(500)]

adata = ad.AnnData(
    X=counts,
    obs=pd.DataFrame(index=cell_ids),
    var=pd.DataFrame(index=gene_ids)
)
```

### Reading/Writing h5ad Files

```python
# h5ad is the native AnnData format
adata = sc.read_h5ad('data.h5ad')

# Write to h5ad
adata.write_h5ad('output.h5ad')

# Write compressed
adata.write_h5ad('output.h5ad', compression='gzip')
```

### Reading Other Formats

```python
# CSV/TSV (genes as columns, cells as rows)
adata = sc.read_csv('counts.csv')

# Loom format
adata = sc.read_loom('data.loom')

# Text file (tab-separated)
adata = sc.read_text('counts.txt')
```

### Adding Metadata

```python
# Add cell metadata
adata.obs['sample'] = 'sample_1'
adata.obs['batch'] = ['batch_1'] * 50 + ['batch_2'] * 50

# Add gene metadata
adata.var['gene_type'] = 'protein_coding'

# Add unstructured data
adata.uns['experiment'] = 'PBMC_3k'
```

### Subsetting AnnData

```python
# Subset by cells
adata_subset = adata[adata.obs['batch'] == 'batch_1'].copy()

# Subset by genes
adata_subset = adata[:, adata.var['highly_variable']].copy()

# Boolean indexing
adata_subset = adata[adata.obs['n_genes'] > 200, :].copy()
```

### Storing Raw Counts

```python
# Store raw counts before normalization
adata.raw = adata.copy()

# Access raw counts later
raw_counts = adata.raw.X

# Or use layers
adata.layers['counts'] = adata.X.copy()
```

---

## Seurat (R)

**Goal:** Load, create, and save single-cell data objects using Seurat.

**Approach:** Read 10X Genomics output into Seurat objects, manipulate metadata, merge samples, and serialize with RDS or h5Seurat formats.

### Required Libraries

```r
library(Seurat)
library(Matrix)
```

### Reading 10X Genomics Data

```r
# Read 10X cellranger output
counts <- Read10X(data.dir = 'filtered_feature_bc_matrix/')

# Create Seurat object
seurat_obj <- CreateSeuratObject(counts = counts, project = 'PBMC', min.cells = 3, min.features = 200)
print(seurat_obj)
```

### Reading 10X h5 File

```r
# Read h5 file directly
counts <- Read10X_h5('filtered_feature_bc_matrix.h5')
seurat_obj <- CreateSeuratObject(counts = counts, project = 'PBMC')
```

### Seurat Object Structure (v5)

```r
# Seurat v5 uses layers instead of slots
# - Layers: counts, data, scale.data
# - Metadata: seurat_obj@meta.data
# - Reductions: seurat_obj@reductions
# - Graphs: seurat_obj@graphs

# Access layers (v5 syntax)
counts <- LayerData(seurat_obj, layer = 'counts')
# Or shorthand
counts <- seurat_obj[['RNA']]$counts

# Access metadata
head(seurat_obj@meta.data)
```

### Creating from Matrix

```r
# Create from sparse matrix
counts <- Matrix(rpois(1000 * 500, 1), nrow = 500, ncol = 1000, sparse = TRUE)
rownames(counts) <- paste0('gene_', 1:500)
colnames(counts) <- paste0('cell_', 1:1000)

seurat_obj <- CreateSeuratObject(counts = counts, project = 'MyProject')
```

### Reading/Writing RDS Files

```r
# Save Seurat object
saveRDS(seurat_obj, file = 'seurat_obj.rds')

# Load Seurat object
seurat_obj <- readRDS('seurat_obj.rds')
```

### Adding Metadata

```r
# Add cell metadata
seurat_obj$sample <- 'sample_1'
seurat_obj$batch <- c(rep('batch_1', 500), rep('batch_2', 500))

# Or using AddMetaData
metadata_df <- data.frame(
    cell_type = rep('unknown', ncol(seurat_obj)),
    row.names = colnames(seurat_obj)
)
seurat_obj <- AddMetaData(seurat_obj, metadata = metadata_df)
```

### Subsetting Seurat Objects

```r
# Subset by metadata
seurat_subset <- subset(seurat_obj, subset = batch == 'batch_1')

# Subset by cells
seurat_subset <- subset(seurat_obj, cells = colnames(seurat_obj)[1:500])

# Subset by features
seurat_subset <- subset(seurat_obj, features = rownames(seurat_obj)[1:100])
```

### Merging Objects

```r
# Merge multiple Seurat objects
merged <- merge(seurat_obj1, y = c(seurat_obj2, seurat_obj3), add.cell.ids = c('S1', 'S2', 'S3'))

# Join layers after merge (v5)
merged <- JoinLayers(merged)
```

---

## Format Conversion

**Goal:** Convert single-cell data objects between Seurat (R) and AnnData (Python) formats.

**Approach:** Use SeuratDisk as an intermediary to convert via h5Seurat/h5ad bridge files.

### Seurat to AnnData

```r
# In R: save as h5Seurat
library(SeuratDisk)
SaveH5Seurat(seurat_obj, filename = 'data.h5seurat')
Convert('data.h5seurat', dest = 'h5ad')
```

```python
# In Python: read converted file
adata = sc.read_h5ad('data.h5ad')
```

### AnnData to Seurat

```python
# In Python: save as h5ad
adata.write_h5ad('data.h5ad')
```

```r
# In R: convert and load
library(SeuratDisk)
Convert('data.h5ad', dest = 'h5seurat')
seurat_obj <- LoadH5Seurat('data.h5seurat')
```

## Common Data Formats

| Format | Extension | Description | Tool |
|--------|-----------|-------------|------|
| 10X MTX | folder | Cellranger output | Both |
| 10X h5 | .h5 | Cellranger HDF5 | Both |
| h5ad | .h5ad | AnnData native | Scanpy |
| RDS | .rds | R serialized | Seurat |
| Loom | .loom | HDF5-based | Both |
| h5Seurat | .h5seurat | Seurat HDF5 | Seurat |

## Related Skills

- preprocessing - QC filtering and normalization after loading
- clustering - Dimensionality reduction and clustering
- markers-annotation - Find marker genes and annotate cell types
