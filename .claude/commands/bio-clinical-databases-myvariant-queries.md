# bio-clinical-databases-myvariant-queries

> Query myvariant.info API for aggregated variant annotations from multiple databases (ClinVar, gnomAD, dbSNP, COSMIC, etc.) in a single request. Use when annotating variants with clinical and population data from multiple sources simultaneously.

## Version Compatibility

Reference examples tested with: SnpEff 5.2+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# MyVariant.info Queries

**"Annotate my variants from multiple databases at once"** → Query the myvariant.info aggregation API to retrieve ClinVar, gnomAD, dbSNP, COSMIC, and other annotations in a single request per variant.
- Python: `myvariant.MyVariantInfo().getvariants(ids, fields='clinvar,gnomad,dbnsfp')`

## Required Imports

```python
import myvariant
```

## Initialize Client

```python
mv = myvariant.MyVariantInfo()
```

## Query Single Variant

**Goal:** Retrieve aggregated annotations for a single variant from multiple databases in one request.

**Approach:** Query myvariant.info by HGVS notation or rsID, which returns ClinVar, gnomAD, dbSNP, COSMIC, and CADD data.

```python
# Query by HGVS notation (recommended)
result = mv.getvariant('chr7:g.140453136A>T')

# Query by rsID
result = mv.getvariant('rs121913527')

# Query by gene and protein change
result = mv.getvariant('BRAF:p.V600E')
```

## Query Multiple Variants

**Goal:** Batch-query up to 1000 variants in a single API call with field selection for efficiency.

**Approach:** Pass a list of variant identifiers to `getvariants()` with specific field filters to minimize response size.

```python
variants = [
    'chr7:g.140453136A>T',
    'chr17:g.7577120C>T',
    'rs121913527'
]

# Batch query (up to 1000 variants per request)
results = mv.getvariants(variants)

# With specific fields
results = mv.getvariants(
    variants,
    fields=['clinvar', 'gnomad_exome', 'dbsnp']
)
```

## Search Variants

**Goal:** Search for variants by gene, clinical significance, or genomic region using query syntax.

**Approach:** Use Lucene-style query strings with `mv.query()` to filter by gene symbol, ClinVar fields, or coordinate ranges.

```python
# Search by gene
results = mv.query('clinvar.gene.symbol:BRCA1', size=100)

# Search pathogenic variants in gene
results = mv.query(
    'clinvar.gene.symbol:BRCA1 AND clinvar.clinical_significance:Pathogenic',
    size=100
)

# Search by genomic region
results = mv.query('chr7:140400000-140500000')
```

## Available Fields

Common field paths for annotations:

| Field | Description |
|-------|-------------|
| `clinvar` | ClinVar annotations |
| `gnomad_exome` | gnomAD exome frequencies |
| `gnomad_genome` | gnomAD genome frequencies |
| `dbsnp` | dbSNP annotations |
| `cosmic` | COSMIC cancer mutations |
| `cadd` | CADD deleteriousness scores |
| `dbnsfp` | dbNSFP functional predictions |
| `snpeff` | SnpEff annotations |

## Extract Specific Annotations

**Goal:** Extract ClinVar classification, gnomAD frequency, and CADD score from a variant result.

**Approach:** Navigate the nested JSON response using dictionary access to reach specific annotation fields.

```python
result = mv.getvariant('chr7:g.140453136A>T')

# ClinVar classification
clinvar_sig = result.get('clinvar', {}).get('clinical_significance')

# gnomAD allele frequency
gnomad_af = result.get('gnomad_exome', {}).get('af', {}).get('af')

# CADD score
cadd_phred = result.get('cadd', {}).get('phred')
```

## Batch Processing with DataFrame

**Goal:** Convert batch variant query results into a structured pandas DataFrame for downstream analysis.

**Approach:** Query multiple rsIDs with selected fields, extract key annotations per variant, and assemble into a DataFrame.

```python
import pandas as pd

variants = ['rs121913527', 'rs1800566', 'rs104894155']
results = mv.getvariants(variants, fields=['clinvar', 'gnomad_exome'])

records = []
for r in results:
    records.append({
        'query': r.get('query'),
        'clinvar_sig': r.get('clinvar', {}).get('clinical_significance'),
        'gnomad_af': r.get('gnomad_exome', {}).get('af', {}).get('af')
    })

df = pd.DataFrame(records)
```

## Rate Limiting

**Goal:** Handle large variant sets exceeding the 1000-variant-per-request API limit.

**Approach:** Split variants into chunks and query sequentially, relying on myvariant's built-in rate limiting.

```python
# myvariant handles rate limiting automatically
# For large batches, use chunks
def batch_query(variants, chunk_size=1000):
    all_results = []
    for i in range(0, len(variants), chunk_size):
        chunk = variants[i:i + chunk_size]
        results = mv.getvariants(chunk)
        all_results.extend(results)
    return all_results
```

## Related Skills

- clinvar-lookup - Detailed ClinVar queries
- gnomad-frequencies - gnomAD-specific frequency queries
- dbsnp-queries - dbSNP rsID lookups
