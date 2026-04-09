# bio-clinical-databases-dbsnp-queries

> Query dbSNP for rsID lookups, variant annotations, and cross-references to other databases. Use when mapping between rsIDs and genomic coordinates or retrieving basic variant information.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, Entrez Direct 21.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# dbSNP Queries

**"Look up variant information by rsID"** → Retrieve variant annotations, genomic coordinates, and cross-references to ClinVar/gnomAD from dbSNP using REST API queries.
- Python: `myvariant.MyVariantInfo().getvariant('rs12345')`

## Query rsID via myvariant.info

**Goal:** Retrieve variant information including dbSNP, ClinVar, and gnomAD annotations by rsID.

**Approach:** Query myvariant.info with the rsID and request specific annotation fields.

```python
import myvariant

mv = myvariant.MyVariantInfo()

def get_rsid_info(rsid):
    '''Get variant info by rsID'''
    result = mv.getvariant(rsid, fields=['dbsnp', 'clinvar', 'gnomad_exome'])
    return result

result = get_rsid_info('rs121913527')
```

## Query via NCBI Entrez

**Goal:** Search and fetch dbSNP records directly from NCBI using Entrez E-utilities.

**Approach:** Use BioPython Entrez esearch to find SNP IDs, then efetch to retrieve full XML records.

```python
from Bio import Entrez
import xml.etree.ElementTree as ET

Entrez.email = 'your@email.com'

def search_dbsnp(rsid):
    '''Search dbSNP by rsID'''
    handle = Entrez.esearch(db='snp', term=rsid)
    record = Entrez.read(handle)
    handle.close()
    return record

def fetch_dbsnp(snp_id):
    '''Fetch dbSNP record by internal ID'''
    handle = Entrez.efetch(db='snp', id=snp_id, rettype='xml')
    xml_data = handle.read()
    handle.close()
    return xml_data
```

## Map Coordinates to rsID

**Goal:** Find the rsID corresponding to a genomic position and allele change.

**Approach:** Construct an HGVS notation from coordinates and query myvariant.info for the dbSNP rsID field.

```python
def coords_to_rsid(chrom, pos, ref, alt):
    '''Find rsID for genomic coordinates'''
    mv = myvariant.MyVariantInfo()

    # Query by HGVS notation
    hgvs = f'chr{chrom}:g.{pos}{ref}>{alt}'
    result = mv.getvariant(hgvs, fields=['dbsnp.rsid'])

    if result:
        return result.get('dbsnp', {}).get('rsid')
    return None
```

## Map rsID to Coordinates

```python
def rsid_to_coords(rsid):
    '''Get genomic coordinates for rsID'''
    mv = myvariant.MyVariantInfo()
    result = mv.getvariant(rsid, fields=['dbsnp', 'vcf'])

    if not result:
        return None

    dbsnp = result.get('dbsnp', {})
    return {
        'chrom': dbsnp.get('chrom'),
        'pos': dbsnp.get('hg38', {}).get('start'),
        'ref': dbsnp.get('ref'),
        'alt': dbsnp.get('alt')
    }
```

## Batch rsID Lookup

```python
def batch_rsid_lookup(rsids, fields=None):
    '''Look up multiple rsIDs'''
    mv = myvariant.MyVariantInfo()

    if fields is None:
        fields = ['dbsnp', 'clinvar.clinical_significance', 'gnomad_exome.af.af']

    results = mv.getvariants(rsids, fields=fields)
    return results
```

## Parse dbSNP Annotations

```python
def parse_dbsnp(result):
    '''Extract key dbSNP annotations'''
    dbsnp = result.get('dbsnp', {})

    return {
        'rsid': dbsnp.get('rsid'),
        'chrom': dbsnp.get('chrom'),
        'pos_hg38': dbsnp.get('hg38', {}).get('start'),
        'pos_hg19': dbsnp.get('hg19', {}).get('start'),
        'ref': dbsnp.get('ref'),
        'alt': dbsnp.get('alt'),
        'gene': dbsnp.get('gene', {}).get('symbol'),
        'class': dbsnp.get('class'),  # snv, ins, del, etc.
        'validated': dbsnp.get('validated')
    }
```

## Variant Classes in dbSNP

| Class | Description |
|-------|-------------|
| snv | Single nucleotide variant |
| ins | Insertion |
| del | Deletion |
| indel | Insertion/deletion |
| mnv | Multiple nucleotide variant |

## Query NCBI Variation Services API

```python
import requests

def query_spdi(rsid):
    '''Query NCBI Variation Services for SPDI notation'''
    url = f'https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{rsid[2:]}'
    response = requests.get(url)
    if response.ok:
        return response.json()
    return None
```

## Related Skills

- myvariant-queries - Aggregated variant queries
- clinvar-lookup - ClinVar pathogenicity
- database-access/entrez-search - General Entrez queries
