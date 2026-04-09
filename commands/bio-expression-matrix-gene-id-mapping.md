# bio-expression-matrix-gene-id-mapping

> Convert between gene identifier systems including Ensembl, Entrez, HGNC symbols, and UniProt. Use when mapping IDs for pathway analysis or matching different data sources.

**Available tools:** Read, Bash

# Gene ID Mapping

## Python: mygene

```python
import mygene
import pandas as pd

mg = mygene.MyGeneInfo()

# Ensembl to Symbol
ensembl_ids = ['ENSG00000141510', 'ENSG00000012048', 'ENSG00000141736']
results = mg.querymany(ensembl_ids, scopes='ensembl.gene', fields='symbol', species='human')
mapping = {r['query']: r.get('symbol', None) for r in results}
# {'ENSG00000141510': 'TP53', 'ENSG00000012048': 'BRCA1', 'ENSG00000141736': 'ERBB2'}

# Symbol to Entrez
symbols = ['TP53', 'BRCA1', 'ERBB2']
results = mg.querymany(symbols, scopes='symbol', fields='entrezgene', species='human')
mapping = {r['query']: r.get('entrezgene', None) for r in results}

# Ensembl to multiple fields
results = mg.querymany(ensembl_ids, scopes='ensembl.gene',
    fields=['symbol', 'entrezgene', 'uniprot'], species='human')
```

## Python: pyensembl

```python
from pyensembl import EnsemblRelease

# Load Ensembl release (downloads automatically first time)
ensembl = EnsemblRelease(110, species='human')  # or 'mouse'

# Gene ID to symbol
gene = ensembl.gene_by_id('ENSG00000141510')
print(gene.gene_name)  # TP53

# Symbol to gene ID
gene = ensembl.genes_by_name('TP53')[0]
print(gene.gene_id)  # ENSG00000141510

# Batch conversion
def ensembl_to_symbol(ensembl_ids, release=110):
    ens = EnsemblRelease(release, species='human')
    mapping = {}
    for eid in ensembl_ids:
        try:
            gene = ens.gene_by_id(eid.split('.')[0])  # Remove version
            mapping[eid] = gene.gene_name
        except ValueError:
            mapping[eid] = None
    return mapping
```

## Python: gseapy

```python
import gseapy as gp

# Ensembl to Symbol using Enrichr
gene_list = ['ENSG00000141510', 'ENSG00000012048']
converted = gp.biomart.ensembl2name(gene_list, organism='hsapiens')
```

## R: biomaRt

```r
library(biomaRt)

# Connect to Ensembl
ensembl <- useEnsembl(biomart='genes', dataset='hsapiens_gene_ensembl')

# Ensembl to Symbol
ensembl_ids <- c('ENSG00000141510', 'ENSG00000012048', 'ENSG00000141736')
results <- getBM(
    attributes=c('ensembl_gene_id', 'hgnc_symbol', 'entrezgene_id'),
    filters='ensembl_gene_id',
    values=ensembl_ids,
    mart=ensembl
)

# Symbol to Ensembl
symbols <- c('TP53', 'BRCA1', 'ERBB2')
results <- getBM(
    attributes=c('hgnc_symbol', 'ensembl_gene_id'),
    filters='hgnc_symbol',
    values=symbols,
    mart=ensembl
)

# All available attributes
listAttributes(ensembl)
```

## R: org.db Packages

```r
library(org.Hs.eg.db)  # Human
library(AnnotationDbi)

# Ensembl to Symbol
ensembl_ids <- c('ENSG00000141510', 'ENSG00000012048')
symbols <- mapIds(org.Hs.eg.db, keys=ensembl_ids, keytype='ENSEMBL', column='SYMBOL')

# Symbol to Entrez
symbols <- c('TP53', 'BRCA1')
entrez <- mapIds(org.Hs.eg.db, keys=symbols, keytype='SYMBOL', column='ENTREZID')

# Available keytypes
keytypes(org.Hs.eg.db)
# ENSEMBL, ENSEMBLPROT, ENSEMBLTRANS, ENTREZID, SYMBOL, UNIPROT, etc.
```

## Apply Mapping to Count Matrix

```python
import pandas as pd
import mygene

def map_count_matrix_ids(counts, from_type='ensembl.gene', to_type='symbol', species='human'):
    '''Map gene IDs in count matrix index.'''
    mg = mygene.MyGeneInfo()

    # Remove version numbers from Ensembl IDs
    clean_ids = [g.split('.')[0] for g in counts.index]

    # Query mygene
    results = mg.querymany(clean_ids, scopes=from_type, fields=to_type, species=species)

    # Build mapping
    mapping = {}
    for r in results:
        if to_type in r:
            mapping[r['query']] = r[to_type]

    # Apply mapping
    new_index = [mapping.get(g.split('.')[0], g) for g in counts.index]
    counts_mapped = counts.copy()
    counts_mapped.index = new_index

    # Handle duplicates (sum)
    counts_mapped = counts_mapped.groupby(counts_mapped.index).sum()

    return counts_mapped

# Usage
counts_symbols = map_count_matrix_ids(counts, 'ensembl.gene', 'symbol')
```

## R Equivalent

```r
library(biomaRt)

map_count_matrix_ids <- function(counts, from_type='ensembl_gene_id', to_type='hgnc_symbol') {
    ensembl <- useEnsembl(biomart='genes', dataset='hsapiens_gene_ensembl')

    # Remove version numbers
    clean_ids <- gsub('\\..*', '', rownames(counts))

    # Get mapping
    mapping <- getBM(
        attributes=c(from_type, to_type),
        filters=from_type,
        values=clean_ids,
        mart=ensembl
    )

    # Merge and aggregate duplicates
    counts$gene_id <- clean_ids
    merged <- merge(counts, mapping, by.x='gene_id', by.y=from_type, all.x=TRUE)
    merged$gene_id <- NULL

    # Use symbol as rowname, sum duplicates
    rownames(merged) <- merged[[to_type]]
    merged[[to_type]] <- NULL
    counts_mapped <- aggregate(. ~ rownames(merged), data=merged, FUN=sum)
    rownames(counts_mapped) <- counts_mapped[,1]
    counts_mapped <- counts_mapped[,-1]

    return(counts_mapped)
}
```

## Handle Unmapped IDs

```python
def robust_id_mapping(gene_ids, from_type, to_type, species='human'):
    '''Map IDs with fallback for unmapped genes.'''
    import mygene
    mg = mygene.MyGeneInfo()

    clean_ids = [g.split('.')[0] for g in gene_ids]
    results = mg.querymany(clean_ids, scopes=from_type, fields=to_type, species=species)

    mapping = {}
    unmapped = []
    for r in results:
        original = gene_ids[clean_ids.index(r['query'])]
        if to_type in r:
            mapping[original] = r[to_type]
        else:
            mapping[original] = original  # Keep original if unmapped
            unmapped.append(original)

    print(f'Mapped: {len(gene_ids) - len(unmapped)}/{len(gene_ids)}')
    print(f'Unmapped: {len(unmapped)}')

    return mapping, unmapped
```

## Common ID Types

| Type | Example | Use Case |
|------|---------|----------|
| Ensembl Gene | ENSG00000141510 | RNA-seq, GTF files |
| Ensembl Transcript | ENST00000269305 | Transcript-level analysis |
| Entrez Gene | 7157 | NCBI databases, KEGG |
| HGNC Symbol | TP53 | Human readable |
| UniProt | P04637 | Protein databases |
| RefSeq | NM_000546 | NCBI RefSeq |

## Related Skills

- expression-matrix/counts-ingest - Load count data
- expression-matrix/metadata-joins - Add annotations
- pathway-analysis/go-enrichment - Requires Entrez IDs
- pathway-analysis/kegg-pathways - Requires Entrez IDs
