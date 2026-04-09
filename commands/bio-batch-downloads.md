# bio-batch-downloads

> Download large datasets from NCBI efficiently using history server, batching, and rate limiting. Use when performing bulk sequence downloads, handling large query results, or production-scale data retrieval.

**Available tools:** Read, Bash

# Batch Downloads

Download large numbers of records from NCBI efficiently using the history server, batching, and proper rate limiting.

## Required Setup

```python
from Bio import Entrez
import time

Entrez.email = 'your.email@example.com'  # Required by NCBI
Entrez.api_key = 'your_api_key'          # Recommended for large downloads
```

## Rate Limits

| Authentication | Requests/Second | Delay Between |
|---------------|-----------------|---------------|
| Email only | 3 | 0.34 seconds |
| Email + API key | 10 | 0.1 seconds |

Get an API key at: https://www.ncbi.nlm.nih.gov/account/settings/

## History Server

The history server stores search results on NCBI servers, enabling efficient batch retrieval without re-sending large ID lists.

### How It Works

1. Search with `usehistory='y'`
2. Get `WebEnv` (session ID) and `query_key` (result set ID)
3. Fetch results in batches using these identifiers
4. Results stay available for ~15 minutes

```python
# Search with history
handle = Entrez.esearch(db='nucleotide', term='human[orgn] AND mRNA[fkey]', usehistory='y')
search = Entrez.read(handle)
handle.close()

webenv = search['WebEnv']
query_key = search['QueryKey']
total = int(search['Count'])

print(f"Found {total} records, stored in history")
```

## Core Pattern: Batch Download

```python
from Bio import Entrez, SeqIO
import time

Entrez.email = 'your.email@example.com'

def batch_download(db, term, output_file, rettype='fasta', batch_size=500):
    # Search with history
    handle = Entrez.esearch(db=db, term=term, usehistory='y')
    search = Entrez.read(handle)
    handle.close()

    webenv = search['WebEnv']
    query_key = search['QueryKey']
    total = int(search['Count'])

    print(f"Downloading {total} records...")

    with open(output_file, 'w') as out:
        for start in range(0, total, batch_size):
            print(f"  Fetching {start+1}-{min(start+batch_size, total)}...")

            handle = Entrez.efetch(
                db=db,
                rettype=rettype,
                retmode='text',
                retstart=start,
                retmax=batch_size,
                webenv=webenv,
                query_key=query_key
            )
            out.write(handle.read())
            handle.close()

            time.sleep(0.34)  # Rate limiting (no API key)

    print(f"Saved to {output_file}")
```

## Code Patterns

### Download All Search Results

```python
from Bio import Entrez
import time

Entrez.email = 'your.email@example.com'
Entrez.api_key = 'your_api_key'  # Optional

def download_search_results(db, term, output_file, rettype='fasta', batch_size=500):
    # Search with history server
    handle = Entrez.esearch(db=db, term=term, usehistory='y', retmax=0)
    search = Entrez.read(handle)
    handle.close()

    webenv = search['WebEnv']
    query_key = search['QueryKey']
    total = int(search['Count'])

    if total == 0:
        print("No records found")
        return

    delay = 0.1 if Entrez.api_key else 0.34

    with open(output_file, 'w') as out:
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            print(f"Downloading {start+1}-{end} of {total}")

            attempts = 3
            for attempt in range(attempts):
                try:
                    handle = Entrez.efetch(db=db, rettype=rettype, retmode='text',
                                           retstart=start, retmax=batch_size,
                                           webenv=webenv, query_key=query_key)
                    out.write(handle.read())
                    handle.close()
                    break
                except Exception as e:
                    if attempt < attempts - 1:
                        print(f"  Retry {attempt+1}: {e}")
                        time.sleep(5)
                    else:
                        raise

            time.sleep(delay)

    print(f"Downloaded {total} records to {output_file}")

download_search_results('nucleotide', 'human[orgn] AND insulin[gene] AND mRNA[fkey]', 'insulin_mrna.fasta')
```

### Download by ID List

```python
def download_by_ids(db, ids, output_file, rettype='fasta', batch_size=200):
    total = len(ids)
    delay = 0.1 if Entrez.api_key else 0.34

    with open(output_file, 'w') as out:
        for start in range(0, total, batch_size):
            batch = ids[start:start+batch_size]
            print(f"Downloading {start+1}-{start+len(batch)} of {total}")

            handle = Entrez.efetch(db=db, id=','.join(batch), rettype=rettype, retmode='text')
            out.write(handle.read())
            handle.close()

            time.sleep(delay)

    print(f"Downloaded {total} records to {output_file}")

# Example with list of IDs
ids = ['NM_007294', 'NM_000059', 'NM_000546', 'NM_001126112', 'NM_004985']
download_by_ids('nucleotide', ids, 'genes.fasta')
```

### Post IDs to History (EPost)

For very large ID lists, post them to the history server first:

```python
def post_and_download(db, ids, output_file, rettype='fasta', batch_size=500):
    # Post IDs to history server
    handle = Entrez.epost(db=db, id=','.join(ids))
    result = Entrez.read(handle)
    handle.close()

    webenv = result['WebEnv']
    query_key = result['QueryKey']
    total = len(ids)

    delay = 0.1 if Entrez.api_key else 0.34

    with open(output_file, 'w') as out:
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            print(f"Fetching {start+1}-{end} of {total}")

            handle = Entrez.efetch(db=db, rettype=rettype, retmode='text',
                                   retstart=start, retmax=batch_size,
                                   webenv=webenv, query_key=query_key)
            out.write(handle.read())
            handle.close()

            time.sleep(delay)

    print(f"Downloaded {total} records")
```

### Download GenBank with Progress

```python
from Bio import Entrez, SeqIO
from io import StringIO
import time

def download_genbank_records(term, output_file, batch_size=100):
    Entrez.email = 'your.email@example.com'

    # Search
    handle = Entrez.esearch(db='nucleotide', term=term, usehistory='y')
    search = Entrez.read(handle)
    handle.close()

    webenv, query_key = search['WebEnv'], search['QueryKey']
    total = int(search['Count'])

    records = []
    for start in range(0, total, batch_size):
        print(f"Fetching {start+1}-{min(start+batch_size, total)} of {total}")

        handle = Entrez.efetch(db='nucleotide', rettype='gb', retmode='text',
                               retstart=start, retmax=batch_size,
                               webenv=webenv, query_key=query_key)
        batch_records = list(SeqIO.parse(handle, 'genbank'))
        handle.close()

        records.extend(batch_records)
        time.sleep(0.34)

    SeqIO.write(records, output_file, 'genbank')
    print(f"Saved {len(records)} GenBank records")
    return records
```

### Download with Retry Logic

```python
import time
from urllib.error import HTTPError

def robust_download(db, term, output_file, rettype='fasta', batch_size=500, max_retries=3):
    handle = Entrez.esearch(db=db, term=term, usehistory='y')
    search = Entrez.read(handle)
    handle.close()

    webenv, query_key = search['WebEnv'], search['QueryKey']
    total = int(search['Count'])
    delay = 0.1 if Entrez.api_key else 0.34

    with open(output_file, 'w') as out:
        for start in range(0, total, batch_size):
            for retry in range(max_retries):
                try:
                    handle = Entrez.efetch(db=db, rettype=rettype, retmode='text',
                                           retstart=start, retmax=batch_size,
                                           webenv=webenv, query_key=query_key)
                    data = handle.read()
                    handle.close()

                    if data.strip():
                        out.write(data)
                    break

                except HTTPError as e:
                    if e.code == 429:  # Rate limit
                        wait = 10 * (retry + 1)
                        print(f"Rate limited, waiting {wait}s...")
                        time.sleep(wait)
                    elif retry == max_retries - 1:
                        raise
                    else:
                        time.sleep(5)

            time.sleep(delay)

    print(f"Downloaded to {output_file}")
```

### Stream to File (Memory Efficient)

```python
def stream_download(db, term, output_file, rettype='fasta', batch_size=1000):
    handle = Entrez.esearch(db=db, term=term, usehistory='y')
    search = Entrez.read(handle)
    handle.close()

    webenv, query_key = search['WebEnv'], search['QueryKey']
    total = int(search['Count'])

    downloaded = 0
    with open(output_file, 'w') as out:
        for start in range(0, total, batch_size):
            handle = Entrez.efetch(db=db, rettype=rettype, retmode='text',
                                   retstart=start, retmax=batch_size,
                                   webenv=webenv, query_key=query_key)

            # Stream chunks to file
            while True:
                chunk = handle.read(8192)
                if not chunk:
                    break
                out.write(chunk)

            handle.close()
            downloaded = min(start + batch_size, total)
            print(f"Progress: {downloaded}/{total} ({100*downloaded/total:.1f}%)")
            time.sleep(0.34)
```

## Batch Size Guidelines

| Database | rettype | Recommended Batch |
|----------|---------|-------------------|
| nucleotide | fasta | 500-1000 |
| nucleotide | gb | 100-200 |
| protein | fasta | 500-1000 |
| protein | gp | 100-200 |
| pubmed | abstract | 1000-2000 |
| pubmed | xml | 200-500 |

Smaller batches for GenBank/XML (more data per record).

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `HTTPError 429` | Rate limit exceeded | Increase delay, use API key |
| `HTTPError 400` | Invalid WebEnv/query_key | Session expired, re-search |
| Incomplete data | Connection interrupted | Add retry logic |
| Memory error | Batch too large | Reduce batch_size |
| Empty response | No more records | Check total vs start |

## Decision Tree

```
Need to download many NCBI records?
├── Have search query?
│   └── Use esearch with usehistory='y', then batch efetch
├── Have list of IDs?
│   ├── < 200 IDs? → Direct efetch with comma-separated IDs
│   └── >= 200 IDs? → Use epost, then batch efetch
├── Need records as Biopython objects?
│   └── Parse each batch with SeqIO
├── Downloading > 10,000 records?
│   └── Use streaming to avoid memory issues
└── Getting rate limited?
    └── Get API key, add retry logic
```

## Related Skills

- entrez-search - Build search queries for batch downloads
- entrez-fetch - Single record fetching
- sra-data - For raw sequencing data (use SRA toolkit instead)
