# bio-expression-matrix-sparse-handling

> Work with sparse matrices for memory-efficient storage of count data. Use when dealing with single-cell data or large bulk RNA-seq datasets where most values are zero.

**Available tools:** Read, Bash

# Sparse Matrix Handling

## Check Sparsity

```python
import numpy as np

# Calculate sparsity (proportion of zeros)
def check_sparsity(counts):
    zeros = (counts == 0).sum().sum()
    total = counts.size
    sparsity = zeros / total
    print(f'Sparsity: {sparsity:.1%} ({zeros:,} / {total:,} zeros)')
    return sparsity

# Rule of thumb: use sparse if >50% zeros
```

## Convert Dense to Sparse

```python
import scipy.sparse as sp
import pandas as pd

# From pandas DataFrame
dense_df = pd.read_csv('counts.csv', index_col=0)
sparse_matrix = sp.csr_matrix(dense_df.values)

# Keep row/column names
gene_names = dense_df.index.tolist()
sample_names = dense_df.columns.tolist()

# CSR vs CSC
# CSR (Compressed Sparse Row): efficient row slicing, matrix-vector products
# CSC (Compressed Sparse Column): efficient column slicing
sparse_csr = sp.csr_matrix(dense_df.values)  # Row-oriented
sparse_csc = sp.csc_matrix(dense_df.values)  # Column-oriented
```

## Convert Sparse to Dense

```python
import pandas as pd
import scipy.sparse as sp

# To numpy array
dense_array = sparse_matrix.toarray()

# To pandas DataFrame
dense_df = pd.DataFrame(
    sparse_matrix.toarray(),
    index=gene_names,
    columns=sample_names
)
```

## Memory Comparison

```python
import sys
import scipy.sparse as sp

def compare_memory(dense, sparse):
    dense_mb = dense.nbytes / 1e6
    sparse_mb = (sparse.data.nbytes + sparse.indices.nbytes + sparse.indptr.nbytes) / 1e6
    ratio = dense_mb / sparse_mb
    print(f'Dense:  {dense_mb:.1f} MB')
    print(f'Sparse: {sparse_mb:.1f} MB')
    print(f'Ratio:  {ratio:.1f}x smaller')
    return ratio

sparse = sp.csr_matrix(counts.values)
compare_memory(counts.values, sparse)
```

## Save/Load Sparse Matrices

```python
import scipy.sparse as sp
import numpy as np

# Save sparse matrix
sp.save_npz('counts_sparse.npz', sparse_matrix)

# Save with metadata
np.savez('counts_with_meta.npz',
    data=sparse_matrix.data,
    indices=sparse_matrix.indices,
    indptr=sparse_matrix.indptr,
    shape=sparse_matrix.shape,
    genes=np.array(gene_names),
    samples=np.array(sample_names))

# Load sparse matrix
sparse_matrix = sp.load_npz('counts_sparse.npz')

# Load with metadata
loaded = np.load('counts_with_meta.npz', allow_pickle=True)
sparse_matrix = sp.csr_matrix(
    (loaded['data'], loaded['indices'], loaded['indptr']),
    shape=tuple(loaded['shape']))
gene_names = loaded['genes'].tolist()
```

## AnnData with Sparse Matrices

```python
import anndata as ad
import scipy.sparse as sp
import pandas as pd

# Create AnnData with sparse matrix
adata = ad.AnnData(
    X=sp.csr_matrix(counts.values),
    obs=pd.DataFrame(index=counts.columns),  # Samples
    var=pd.DataFrame(index=counts.index)     # Genes
)

# Note: AnnData transposes so cells/samples are rows
adata = ad.AnnData(
    X=sp.csr_matrix(counts.T.values),  # Transpose for samples-as-rows
    obs=pd.DataFrame(index=counts.columns),
    var=pd.DataFrame(index=counts.index)
)

# Save (automatically handles sparse)
adata.write_h5ad('counts.h5ad')

# Check if stored sparse
adata = ad.read_h5ad('counts.h5ad')
print(f'Matrix type: {type(adata.X)}')
```

## Sparse Operations

```python
import scipy.sparse as sp
import numpy as np

# Row sums (gene totals)
row_sums = np.array(sparse_matrix.sum(axis=1)).flatten()

# Column sums (sample totals)
col_sums = np.array(sparse_matrix.sum(axis=0)).flatten()

# Filter rows by sum (keep genes with >10 total counts)
keep_mask = row_sums > 10
sparse_filtered = sparse_matrix[keep_mask, :]

# Filter columns (keep samples with >1000 counts)
keep_cols = col_sums > 1000
sparse_filtered = sparse_matrix[:, keep_cols]

# Log transform (add pseudocount)
sparse_log = sparse_matrix.copy()
sparse_log.data = np.log1p(sparse_log.data)
```

## Subsetting Sparse Matrices

```python
# Select specific genes
gene_idx = [gene_names.index(g) for g in ['TP53', 'BRCA1', 'MYC'] if g in gene_names]
subset = sparse_matrix[gene_idx, :]

# Select specific samples
sample_idx = [sample_names.index(s) for s in ['sample1', 'sample2']]
subset = sparse_matrix[:, sample_idx]

# Boolean indexing
expressed = row_sums > 0
sparse_expressed = sparse_matrix[expressed, :]
```

## Normalization on Sparse

```python
import numpy as np
import scipy.sparse as sp

def normalize_sparse_cpm(sparse_matrix):
    '''CPM normalization for sparse matrix.'''
    lib_sizes = np.array(sparse_matrix.sum(axis=0)).flatten()
    scaling_factors = 1e6 / lib_sizes
    normalized = sparse_matrix.multiply(scaling_factors)  # Broadcasts across columns
    return normalized

def normalize_sparse_log1p(sparse_matrix):
    '''Log1p transform sparse matrix in place.'''
    result = sparse_matrix.copy()
    result.data = np.log1p(result.data)
    return result

cpm = normalize_sparse_cpm(sparse_matrix)
log_cpm = normalize_sparse_log1p(cpm)
```

## 10X Matrix Format

```python
import scipy.io
import pandas as pd

# Read 10X format
matrix = scipy.io.mmread('matrix.mtx').T.tocsr()  # Transpose and convert to CSR
features = pd.read_csv('features.tsv', sep='\t', header=None)
barcodes = pd.read_csv('barcodes.tsv', sep='\t', header=None)

gene_names = features[1].tolist()  # Gene symbols
cell_barcodes = barcodes[0].tolist()

# Write 10X format
scipy.io.mmwrite('output_matrix.mtx', sparse_matrix)
```

## Related Skills

- expression-matrix/counts-ingest - Load count data
- single-cell/data-io - Single-cell data loading
- single-cell/preprocessing - Single-cell normalization
