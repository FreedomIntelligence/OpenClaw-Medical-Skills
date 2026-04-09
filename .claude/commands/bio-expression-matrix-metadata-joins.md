# bio-expression-matrix-metadata-joins

> Merge sample metadata with count matrices and add gene annotations. Use when preparing data for differential expression analysis or visualization.

**Available tools:** Read, Bash

# Metadata Joins

## Load Sample Metadata

```python
import pandas as pd

# Load metadata
metadata = pd.read_csv('sample_info.csv', index_col=0)

# Metadata should have samples as rows, attributes as columns
# Index should match count matrix column names
```

## Basic Join

```python
import pandas as pd

# Count matrix: genes x samples
counts = pd.read_csv('counts.tsv', sep='\t', index_col=0)

# Metadata: samples x attributes
metadata = pd.read_csv('metadata.csv', index_col=0)

# Ensure sample order matches
common_samples = counts.columns.intersection(metadata.index)
counts = counts[common_samples]
metadata = metadata.loc[common_samples]

# Verify alignment
assert all(counts.columns == metadata.index)
```

## Handle Sample Name Mismatches

```python
def harmonize_sample_names(counts, metadata):
    '''Match sample names between counts and metadata.'''
    count_samples = set(counts.columns)
    meta_samples = set(metadata.index)

    common = count_samples & meta_samples
    only_counts = count_samples - meta_samples
    only_meta = meta_samples - count_samples

    if only_counts:
        print(f'Samples in counts but not metadata: {only_counts}')
    if only_meta:
        print(f'Samples in metadata but not counts: {only_meta}')

    counts = counts[sorted(common)]
    metadata = metadata.loc[sorted(common)]
    return counts, metadata

counts, metadata = harmonize_sample_names(counts, metadata)
```

## Flexible Sample Name Matching

```python
def fuzzy_match_samples(counts, metadata):
    '''Try to match sample names with common transformations.'''
    count_cols = counts.columns.tolist()
    meta_idx = metadata.index.tolist()

    # Try exact match first
    if set(count_cols) == set(meta_idx):
        return counts, metadata

    # Common transformations
    transformations = [
        lambda x: x.replace('_', '-'),
        lambda x: x.replace('-', '_'),
        lambda x: x.split('_')[0],
        lambda x: x.replace('.bam', ''),
        lambda x: x.upper(),
        lambda x: x.lower(),
    ]

    for transform in transformations:
        transformed = {transform(c): c for c in count_cols}
        matches = {m: transformed[transform(m)] for m in meta_idx if transform(m) in transformed}
        if len(matches) == len(meta_idx):
            print(f'Matched using transformation')
            counts = counts[[matches[m] for m in meta_idx]]
            return counts, metadata

    raise ValueError('Could not match sample names')
```

## Add Gene Annotations

```python
import mygene

def add_gene_annotations(counts, fields=['symbol', 'name', 'type_of_gene']):
    '''Add gene annotation columns to count matrix.'''
    mg = mygene.MyGeneInfo()

    clean_ids = [g.split('.')[0] for g in counts.index]
    results = mg.querymany(clean_ids, scopes='ensembl.gene',
        fields=fields, species='human', as_dataframe=True)

    # Merge annotations
    results = results.reset_index().rename(columns={'query': 'gene_id'})
    counts_reset = counts.reset_index().rename(columns={counts.index.name: 'gene_id'})
    counts_reset['clean_id'] = counts_reset['gene_id'].str.split('.').str[0]

    annotated = counts_reset.merge(
        results[['gene_id'] + fields].drop_duplicates(),
        left_on='clean_id', right_on='gene_id', how='left', suffixes=('', '_anno'))

    annotated = annotated.drop(['clean_id', 'gene_id_anno'], axis=1, errors='ignore')
    annotated = annotated.set_index('gene_id')

    return annotated
```

## R: Create DESeq2 Data

```r
library(DESeq2)

# Load data
counts <- read.delim('counts.tsv', row.names=1)
metadata <- read.csv('metadata.csv', row.names=1)

# Ensure matching samples
common <- intersect(colnames(counts), rownames(metadata))
counts <- counts[, common]
metadata <- metadata[common, , drop=FALSE]

# Create DESeqDataSet
dds <- DESeqDataSetFromMatrix(
    countData=as.matrix(counts),
    colData=metadata,
    design=~condition  # Adjust to your design
)
```

## R: Create edgeR DGEList

```r
library(edgeR)

# Load data
counts <- read.delim('counts.tsv', row.names=1)
metadata <- read.csv('metadata.csv', row.names=1)

# Match samples
common <- intersect(colnames(counts), rownames(metadata))
counts <- counts[, common]
metadata <- metadata[common, , drop=FALSE]

# Create DGEList
y <- DGEList(counts=as.matrix(counts), group=metadata$condition)
y$samples <- cbind(y$samples, metadata)
```

## Create AnnData with Metadata

```python
import anndata as ad
import pandas as pd

def create_annotated_anndata(counts, sample_metadata, gene_metadata=None):
    '''Create AnnData object with full metadata.'''
    # AnnData expects samples as rows
    adata = ad.AnnData(X=counts.T)

    # Add sample metadata (obs)
    adata.obs = sample_metadata.loc[counts.columns].copy()

    # Add gene metadata (var)
    if gene_metadata is not None:
        adata.var = gene_metadata.loc[counts.index].copy()
    else:
        adata.var_names = counts.index

    return adata

# Usage
adata = create_annotated_anndata(counts, metadata)
adata.write_h5ad('annotated_counts.h5ad')
```

## Validate Metadata

```python
def validate_metadata(counts, metadata, required_columns=['condition']):
    '''Check metadata validity.'''
    issues = []

    # Check sample overlap
    count_samples = set(counts.columns)
    meta_samples = set(metadata.index)

    if count_samples != meta_samples:
        missing = count_samples - meta_samples
        extra = meta_samples - count_samples
        if missing:
            issues.append(f'Samples missing metadata: {missing}')
        if extra:
            issues.append(f'Extra metadata samples: {extra}')

    # Check required columns
    for col in required_columns:
        if col not in metadata.columns:
            issues.append(f'Missing required column: {col}')
        elif metadata[col].isna().any():
            n_na = metadata[col].isna().sum()
            issues.append(f'Column {col} has {n_na} missing values')

    if issues:
        for issue in issues:
            print(f'WARNING: {issue}')
        return False

    print('Metadata validation passed')
    return True
```

## Merge Multiple Metadata Files

```python
def merge_metadata_files(files, on='sample_id'):
    '''Merge multiple metadata files.'''
    dfs = [pd.read_csv(f) for f in files]
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on=on, how='outer')
    return merged.set_index(on)

# Usage
metadata = merge_metadata_files(['clinical.csv', 'sequencing.csv', 'qc.csv'])
```

## Related Skills

- expression-matrix/counts-ingest - Load count data
- expression-matrix/gene-id-mapping - Convert gene IDs
- differential-expression/deseq2-basics - Downstream analysis
- single-cell/preprocessing - Single-cell metadata handling
