# bio-geo-data

> Query NCBI Gene Expression Omnibus (GEO) for expression datasets using Biopython Bio.Entrez. Use when finding microarray/RNA-seq datasets, downloading expression data, or linking GEO series to SRA runs.

**Available tools:** Read, Bash

# GEO Data

Query and access Gene Expression Omnibus datasets using Biopython's Entrez module.

## Required Setup

```python
from Bio import Entrez

Entrez.email = 'your.email@example.com'  # Required by NCBI
Entrez.api_key = 'your_api_key'          # Optional
```

## GEO Database Types

| Database | db value | Description |
|----------|----------|-------------|
| GEO DataSets | `gds` | Curated datasets (GDS*) |
| GEO Profiles | `geoprofiles` | Individual gene profiles |

**GEO Record Types:**
| Prefix | Type | Description |
|--------|------|-------------|
| GSE | Series | Complete study/experiment |
| GSM | Sample | Individual sample |
| GPL | Platform | Array/sequencing platform |
| GDS | DataSet | Curated, normalized dataset |

## Searching GEO

### Search GEO DataSets (GDS)

```python
from Bio import Entrez

Entrez.email = 'your.email@example.com'

# Search curated datasets
handle = Entrez.esearch(db='gds', term='breast cancer AND Homo sapiens[orgn]', retmax=10)
record = Entrez.read(handle)
handle.close()

print(f"Found {record['Count']} datasets")
print(f"IDs: {record['IdList']}")
```

### Search GEO Series (GSE)

```python
# Search GEO Series via gds database
# Use entry_type filter
handle = Entrez.esearch(db='gds', term='RNA-seq[title] AND human[orgn] AND gse[entry_type]', retmax=10)
record = Entrez.read(handle)
handle.close()
```

### Common Search Fields

| Field | Description | Example |
|-------|-------------|---------|
| `[orgn]` | Organism | `human[orgn]` |
| `[title]` | Dataset title | `breast cancer[title]` |
| `[description]` | Description text | `stem cell[description]` |
| `[platform]` | Platform GPL | `GPL570[platform]` |
| `[entry_type]` | Record type | `gse[entry_type]`, `gds[entry_type]` |
| `[gdstype]` | Study type | `expression profiling[gdstype]` |
| `[pubmed]` | PubMed ID | `35412348[pubmed]` |
| `[pdat]` | Publication date | `2024[pdat]` |

### GDS Types

```python
# Expression profiling by array
term = 'expression profiling by array[gdstype] AND cancer'

# RNA-seq expression
term = 'expression profiling by high throughput sequencing[gdstype]'

# ChIP-seq
term = 'genome binding/occupancy profiling[gdstype]'
```

## Fetching GEO Information

### Get GEO DataSet Summary

```python
# Fetch summary for GDS records
handle = Entrez.esummary(db='gds', id='200024320')
record = Entrez.read(handle)
handle.close()

summary = record[0]
print(f"Accession: {summary['Accession']}")
print(f"Title: {summary['title']}")
print(f"Summary: {summary['summary'][:200]}...")
print(f"Organism: {summary['taxon']}")
print(f"Platform: {summary['GPL']}")
print(f"Samples: {summary['n_samples']}")
```

### Summary Fields

```python
summary['Accession']     # GSE/GDS accession
summary['title']         # Dataset title
summary['summary']       # Description
summary['taxon']         # Organism
summary['GPL']           # Platform ID
summary['n_samples']     # Number of samples
summary['FTPLink']       # FTP download link
summary['PubMedIds']     # Associated publications
summary['gdsType']       # Dataset type
summary['ptechType']     # Platform technology
```

## Code Patterns

### Search and List GEO Series

```python
from Bio import Entrez

Entrez.email = 'your.email@example.com'

def search_geo(term, entry_type='gse', max_results=20):
    full_term = f'{term} AND {entry_type}[entry_type]'
    handle = Entrez.esearch(db='gds', term=full_term, retmax=max_results)
    search = Entrez.read(handle)
    handle.close()

    if not search['IdList']:
        return []

    handle = Entrez.esummary(db='gds', id=','.join(search['IdList']))
    summaries = Entrez.read(handle)
    handle.close()

    results = []
    for s in summaries:
        results.append({
            'accession': s['Accession'],
            'title': s['title'],
            'organism': s['taxon'],
            'samples': s['n_samples'],
            'platform': s['GPL']
        })
    return results

datasets = search_geo('breast cancer RNA-seq AND human[orgn]')
for ds in datasets:
    print(f"{ds['accession']}: {ds['title'][:60]}... ({ds['samples']} samples)")
```

### Find RNA-Seq Datasets

```python
def find_rnaseq_datasets(organism, keywords, max_results=20):
    term = f'{keywords} AND {organism}[orgn] AND expression profiling by high throughput sequencing[gdstype] AND gse[entry_type]'

    handle = Entrez.esearch(db='gds', term=term, retmax=max_results)
    search = Entrez.read(handle)
    handle.close()

    if not search['IdList']:
        return []

    handle = Entrez.esummary(db='gds', id=','.join(search['IdList']))
    summaries = Entrez.read(handle)
    handle.close()

    return summaries

datasets = find_rnaseq_datasets('Homo sapiens', 'COVID-19')
for ds in datasets:
    print(f"{ds['Accession']}: {ds['n_samples']} samples - {ds['title'][:50]}...")
```

### Get GSE Download Link

```python
def get_geo_ftp(gse_accession):
    '''Get FTP download link for a GSE'''
    handle = Entrez.esearch(db='gds', term=f'{gse_accession}[accn]')
    search = Entrez.read(handle)
    handle.close()

    if not search['IdList']:
        return None

    handle = Entrez.esummary(db='gds', id=search['IdList'][0])
    summary = Entrez.read(handle)[0]
    handle.close()

    return summary.get('FTPLink')

ftp_link = get_geo_ftp('GSE123456')
print(f"Download from: {ftp_link}")
```

### Link GEO to SRA

Many GEO RNA-seq datasets have associated SRA data.

```python
def geo_to_sra(gse_accession):
    '''Find SRA runs associated with a GEO series'''
    # Search GEO
    handle = Entrez.esearch(db='gds', term=f'{gse_accession}[accn]')
    search = Entrez.read(handle)
    handle.close()

    if not search['IdList']:
        return []

    # Link to SRA
    handle = Entrez.elink(dbfrom='gds', db='sra', id=search['IdList'][0])
    links = Entrez.read(handle)
    handle.close()

    if not links[0]['LinkSetDb']:
        return []

    sra_ids = [link['Id'] for link in links[0]['LinkSetDb'][0]['Link']]

    # Get SRA accessions
    handle = Entrez.esummary(db='sra', id=','.join(sra_ids[:50]))
    summaries = Entrez.read(handle)
    handle.close()

    runs = []
    for s in summaries:
        expxml = s.get('ExpXml', '')
        if 'SRR' in str(expxml) or 'SRX' in str(expxml):
            runs.append(s)
    return runs

sra_data = geo_to_sra('GSE123456')
print(f"Found {len(sra_data)} SRA records")
```

### Search by PubMed ID

```python
def geo_from_pubmed(pmid):
    '''Find GEO datasets associated with a publication'''
    handle = Entrez.elink(dbfrom='pubmed', db='gds', id=pmid)
    links = Entrez.read(handle)
    handle.close()

    if not links[0]['LinkSetDb']:
        return []

    gds_ids = [link['Id'] for link in links[0]['LinkSetDb'][0]['Link']]

    handle = Entrez.esummary(db='gds', id=','.join(gds_ids))
    summaries = Entrez.read(handle)
    handle.close()

    return summaries

datasets = geo_from_pubmed('35412348')
for ds in datasets:
    print(f"{ds['Accession']}: {ds['title']}")
```

### Download GEO Data (GEOparse)

For full data parsing, use the GEOparse library:

```python
# pip install GEOparse
import GEOparse

# Download and parse GSE
gse = GEOparse.get_GEO('GSE123456')

# Access metadata
print(f"Title: {gse.metadata['title'][0]}")
print(f"Samples: {len(gse.gsms)}")

# Get sample metadata
for gsm_name, gsm in gse.gsms.items():
    print(f"{gsm_name}: {gsm.metadata['title'][0]}")

# Get expression table
if gse.gpls:
    gpl_name = list(gse.gpls.keys())[0]
    expression_table = gse.pivot_samples('VALUE')
```

## Download Options

### Direct FTP Download

```bash
# Download entire GSE
wget -r -np -nd ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE123nnn/GSE123456/

# Download specific file types
wget ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE123nnn/GSE123456/suppl/*counts*.txt.gz
```

### Series Matrix Files

```python
import gzip
import urllib.request

def download_series_matrix(gse):
    '''Download series matrix file'''
    gse_prefix = gse[:len(gse)-3] + 'nnn'
    url = f'https://ftp.ncbi.nlm.nih.gov/geo/series/{gse_prefix}/{gse}/matrix/{gse}_series_matrix.txt.gz'

    filename = f'{gse}_series_matrix.txt.gz'
    urllib.request.urlretrieve(url, filename)
    return filename
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Empty results | Wrong entry_type | Add `gse[entry_type]` or `gds[entry_type]` |
| No FTPLink | Superseries or no data | Check if series has supplementary files |
| No SRA link | Microarray data | SRA only for sequencing data |

## Decision Tree

```
Need GEO expression data?
├── Looking for curated datasets?
│   └── Search gds with [entry_type]=gds
├── Looking for any experiment?
│   └── Search gds with [entry_type]=gse
├── Want RNA-seq specifically?
│   └── Add 'expression profiling by high throughput sequencing[gdstype]'
├── Have a publication?
│   └── Link pubmed -> gds
├── Need raw sequencing data?
│   └── Link gds -> sra, then use sra-data skill
├── Need processed expression matrix?
│   └── Download series matrix or use GEOparse
└── Need full metadata?
    └── Use GEOparse library
```

## Related Skills

- entrez-search - General database searching
- entrez-link - Link GEO to SRA and other databases
- sra-data - Download raw sequencing data from linked SRA
- batch-downloads - Download multiple GEO records
