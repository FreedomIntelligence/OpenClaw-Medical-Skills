# bio-entrez-search

> Search NCBI databases using Biopython Bio.Entrez. Use when finding records by keyword, building complex search queries, discovering database structure, or getting global query counts across databases.

**Available tools:** Read, Bash

# Entrez Search

Search NCBI databases using Biopython's Entrez module (ESearch, EInfo, EGQuery utilities).

## Required Setup

```python
from Bio import Entrez

Entrez.email = 'your.email@example.com'  # Required by NCBI
Entrez.api_key = 'your_api_key'          # Optional, raises rate limit 3->10 req/sec
```

## Core Functions

### Entrez.esearch() - Search a Database

Search any NCBI database and get matching record IDs.

```python
handle = Entrez.esearch(db='nucleotide', term='human[orgn] AND BRCA1[gene]')
record = Entrez.read(handle)
handle.close()

print(f"Found {record['Count']} records")
print(f"IDs: {record['IdList']}")  # First 20 IDs by default
```

**Key Parameters:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| `db` | Database to search | Required |
| `term` | Search query | Required |
| `retmax` | Max IDs to return | 20 |
| `retstart` | Starting index (pagination) | 0 |
| `usehistory` | Store results on server | 'n' |
| `sort` | Sort order | database-specific |
| `datetype` | Date field to search | 'pdat' |
| `reldate` | Records from last N days | None |
| `mindate` | Start date (YYYY/MM/DD) | None |
| `maxdate` | End date (YYYY/MM/DD) | None |

**ESearch Result Fields:**
```python
record['Count']        # Total matching records (string)
record['IdList']       # List of record IDs
record['RetMax']       # Number of IDs returned
record['RetStart']     # Starting index
record['QueryKey']     # For history server (if usehistory='y')
record['WebEnv']       # For history server (if usehistory='y')
record['TranslationSet']  # Query translations applied
record['QueryTranslation']  # Final translated query
```

### Entrez.einfo() - Database Information

Get information about available databases or specific database fields.

```python
# List all available databases
handle = Entrez.einfo()
record = Entrez.read(handle)
handle.close()
print(record['DbList'])  # ['pubmed', 'protein', 'nucleotide', ...]

# Get info about specific database
handle = Entrez.einfo(db='nucleotide')
record = Entrez.read(handle)
handle.close()

print(f"Description: {record['DbInfo']['Description']}")
print(f"Record count: {record['DbInfo']['Count']}")

# List searchable fields
for field in record['DbInfo']['FieldList']:
    print(f"{field['Name']}: {field['Description']}")
```

**Database Info Fields:**
```python
record['DbInfo']['DbName']       # Database name
record['DbInfo']['Description']  # Database description
record['DbInfo']['Count']        # Total records in database
record['DbInfo']['LastUpdate']   # Last update date
record['DbInfo']['FieldList']    # Searchable fields
record['DbInfo']['LinkList']     # Available links to other databases
```

### Entrez.egquery() - Global Query

Search across all NCBI databases simultaneously.

```python
handle = Entrez.egquery(term='CRISPR')
record = Entrez.read(handle)
handle.close()

for result in record['eGQueryResult']:
    if int(result['Count']) > 0:
        print(f"{result['DbName']}: {result['Count']} records")
```

## Search Query Syntax

NCBI uses a specific query syntax:

### Field Tags
```python
# Search specific fields using [field_name]
term = 'BRCA1[gene]'                    # Gene name field
term = 'human[orgn]'                    # Organism field
term = 'Homo sapiens[ORGN]'             # Full organism name
term = 'NM_007294[accn]'                # Accession number
term = 'Smith J[auth]'                  # Author (PubMed)
term = 'Nature[jour]'                   # Journal (PubMed)
term = '1000:5000[slen]'                # Sequence length range
term = 'mRNA[fkey]'                     # Feature key
```

### Boolean Operators
```python
term = 'BRCA1 AND human'                # Both terms
term = 'cancer OR tumor'                # Either term
term = 'human NOT mouse'                # Exclude term
term = '(BRCA1 OR BRCA2) AND human'     # Grouping
```

### Date Ranges
```python
# Using date parameters
handle = Entrez.esearch(
    db='pubmed',
    term='CRISPR',
    datetype='pdat',     # Publication date
    mindate='2023/01/01',
    maxdate='2024/12/31'
)

# Or in query string
term = 'CRISPR AND 2024[pdat]'
term = 'CRISPR AND 2023:2024[pdat]'
```

### Wildcards and Phrases
```python
term = 'immun*'                         # Wildcard
term = '"breast cancer"[title]'         # Exact phrase
```

## Common Databases

| Database | `db` value | Common Fields |
|----------|------------|---------------|
| PubMed | `pubmed` | `[auth]`, `[title]`, `[jour]`, `[pdat]` |
| Nucleotide | `nucleotide` | `[orgn]`, `[gene]`, `[accn]`, `[slen]` |
| Protein | `protein` | `[orgn]`, `[gene]`, `[accn]`, `[molwt]` |
| Gene | `gene` | `[orgn]`, `[sym]`, `[chr]` |
| SRA | `sra` | `[orgn]`, `[platform]`, `[strategy]` |
| Taxonomy | `taxonomy` | `[scin]`, `[comn]`, `[rank]` |
| Assembly | `assembly` | `[orgn]`, `[level]`, `[refseq]` |

## Code Patterns

### Basic Search with Pagination

```python
from Bio import Entrez

Entrez.email = 'your.email@example.com'

def search_ncbi(db, term, max_results=100):
    handle = Entrez.esearch(db=db, term=term, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()
    return record['IdList'], int(record['Count'])

ids, total = search_ncbi('nucleotide', 'human[orgn] AND insulin[gene]')
print(f'Retrieved {len(ids)} of {total} total records')
```

### Paginated Search for Large Results

```python
def search_all_ids(db, term, batch_size=10000):
    all_ids = []
    handle = Entrez.esearch(db=db, term=term, retmax=0)
    record = Entrez.read(handle)
    handle.close()
    total = int(record['Count'])

    for start in range(0, total, batch_size):
        handle = Entrez.esearch(db=db, term=term, retstart=start, retmax=batch_size)
        record = Entrez.read(handle)
        handle.close()
        all_ids.extend(record['IdList'])

    return all_ids
```

### Search with History Server (for Large Results)

```python
# Store results on NCBI server for subsequent fetching
handle = Entrez.esearch(db='nucleotide', term='human[orgn] AND mRNA[fkey]', usehistory='y')
record = Entrez.read(handle)
handle.close()

webenv = record['WebEnv']
query_key = record['QueryKey']
total = int(record['Count'])

# Use webenv and query_key with efetch for batch downloads
# See batch-downloads skill for details
```

### Recent Records Only

```python
# Records from last 30 days
handle = Entrez.esearch(db='pubmed', term='CRISPR', reldate=30, datetype='pdat')
record = Entrez.read(handle)
handle.close()
```

### Get Available Fields for a Database

```python
def get_search_fields(db):
    handle = Entrez.einfo(db=db)
    record = Entrez.read(handle)
    handle.close()
    return [(f['Name'], f['Description']) for f in record['DbInfo']['FieldList']]

fields = get_search_fields('nucleotide')
for name, desc in fields[:10]:
    print(f'{name}: {desc}')
```

### Check Query Translation

```python
handle = Entrez.esearch(db='nucleotide', term='human BRCA1')
record = Entrez.read(handle)
handle.close()

# See how NCBI interpreted your query
print(f"Your query was translated to: {record['QueryTranslation']}")
# e.g., '"homo sapiens"[Organism] AND BRCA1[All Fields]'
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `HTTPError 429` | Rate limit exceeded | Add delays or use API key |
| `HTTPError 400` | Invalid query syntax | Check field names and operators |
| Empty IdList | No matches or typo | Check QueryTranslation field |
| `RuntimeError` | Missing email | Set `Entrez.email` |

## Decision Tree

```
Need to search NCBI?
├── Finding records in one database?
│   └── Use Entrez.esearch()
├── Search across all databases?
│   └── Use Entrez.egquery()
├── Need database field names?
│   └── Use Entrez.einfo(db='database')
├── List all available databases?
│   └── Use Entrez.einfo() (no db argument)
├── Results > 10,000 records?
│   └── Use usehistory='y', then batch fetch
└── Need to fetch actual records?
    └── See entrez-fetch skill
```

## Related Skills

- entrez-fetch - Retrieve full records after searching
- entrez-link - Find related records in other databases
- batch-downloads - Download large result sets efficiently
- geo-data - Search GEO expression datasets (specialized search)
- blast-searches - Search by sequence similarity instead of keywords
