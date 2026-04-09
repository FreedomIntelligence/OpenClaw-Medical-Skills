# bio-entrez-fetch

> Retrieve records from NCBI databases using Biopython Bio.Entrez. Use when downloading sequences, fetching GenBank records, getting document summaries, or parsing NCBI data into Biopython objects.

**Available tools:** Read, Bash

# Entrez Fetch

Retrieve records from NCBI databases using Biopython's Entrez module (EFetch, ESummary utilities).

## Required Setup

```python
from Bio import Entrez

Entrez.email = 'your.email@example.com'  # Required by NCBI
Entrez.api_key = 'your_api_key'          # Optional, raises rate limit 3->10 req/sec
```

## Core Functions

### Entrez.efetch() - Retrieve Full Records

Fetch complete records in various formats from any NCBI database.

```python
# Fetch GenBank record by ID
handle = Entrez.efetch(db='nucleotide', id='NM_007294', rettype='gb', retmode='text')
genbank_text = handle.read()
handle.close()

# Fetch FASTA sequence
handle = Entrez.efetch(db='nucleotide', id='NM_007294', rettype='fasta', retmode='text')
fasta_text = handle.read()
handle.close()

# Fetch multiple records
handle = Entrez.efetch(db='nucleotide', id='NM_007294,NM_000059', rettype='fasta', retmode='text')
```

**Key Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `db` | Database name | `'nucleotide'`, `'protein'`, `'pubmed'` |
| `id` | Record ID(s) | `'NM_007294'` or `'123,456,789'` |
| `rettype` | Return type | `'fasta'`, `'gb'`, `'abstract'` |
| `retmode` | Return mode | `'text'`, `'xml'` |
| `retstart` | Start index | `0` |
| `retmax` | Max records | `20` |
| `WebEnv` | History server session | From esearch |
| `query_key` | History server query | From esearch |

### Common Return Types by Database

**Nucleotide/Protein:**
| rettype | retmode | Description |
|---------|---------|-------------|
| `'fasta'` | `'text'` | FASTA sequence |
| `'gb'` | `'text'` | GenBank flat file |
| `'gp'` | `'text'` | GenPept flat file (protein) |
| `'gbwithparts'` | `'text'` | GenBank with contig sequences |
| `'seqid'` | `'text'` | Seq-id only |
| `'acc'` | `'text'` | Accession only |

**PubMed:**
| rettype | retmode | Description |
|---------|---------|-------------|
| `'abstract'` | `'text'` | Abstract text |
| `'medline'` | `'text'` | MEDLINE format |
| `'xml'` | `'xml'` | Full PubMed XML |

**Gene:**
| rettype | retmode | Description |
|---------|---------|-------------|
| `'gene_table'` | `'text'` | Gene table format |
| `'xml'` | `'xml'` | Full gene XML |

### Entrez.esummary() - Document Summaries

Get brief summaries without downloading full records. Faster than efetch.

```python
# Get summary for nucleotide record
handle = Entrez.esummary(db='nucleotide', id='NM_007294')
record = Entrez.read(handle)
handle.close()

summary = record[0]  # First (only) record
print(f"Title: {summary['Title']}")
print(f"Length: {summary['Length']}")
print(f"Organism: {summary['Organism']}")
```

**Common Summary Fields:**
```python
# Nucleotide/Protein
summary['Title']          # Record title/description
summary['Caption']        # Short identifier
summary['Length']         # Sequence length
summary['Organism']       # Source organism
summary['TaxId']          # Taxonomy ID
summary['AccessionVersion']  # Full accession.version

# PubMed
summary['Title']          # Article title
summary['AuthorList']     # Authors
summary['Source']         # Journal
summary['PubDate']        # Publication date
summary['DOI']            # Digital Object Identifier
```

## Parsing with Biopython

### Parse into SeqRecord Objects

```python
from Bio import Entrez, SeqIO

Entrez.email = 'your.email@example.com'

# Parse GenBank into SeqRecord
handle = Entrez.efetch(db='nucleotide', id='NM_007294', rettype='gb', retmode='text')
record = SeqIO.read(handle, 'genbank')
handle.close()

print(f"ID: {record.id}")
print(f"Length: {len(record.seq)}")
print(f"Features: {len(record.features)}")

# Parse FASTA into SeqRecord
handle = Entrez.efetch(db='nucleotide', id='NM_007294', rettype='fasta', retmode='text')
record = SeqIO.read(handle, 'fasta')
handle.close()
```

### Parse Multiple Records

```python
# Fetch multiple as FASTA
handle = Entrez.efetch(db='nucleotide', id='NM_007294,NM_000059,NM_000546', rettype='fasta', retmode='text')
records = list(SeqIO.parse(handle, 'fasta'))
handle.close()

for record in records:
    print(f"{record.id}: {len(record.seq)} bp")
```

### Parse XML with Entrez.read()

```python
# For structured data, use XML mode
handle = Entrez.efetch(db='gene', id='672', retmode='xml')
records = Entrez.read(handle)
handle.close()

# Navigate nested structure
gene = records[0]
print(f"Gene: {gene['Entrezgene_gene']['Gene-ref']['Gene-ref_locus']}")
```

## Code Patterns

### Fetch Sequence by Accession

```python
from Bio import Entrez, SeqIO

Entrez.email = 'your.email@example.com'

def fetch_sequence(accession, db='nucleotide'):
    handle = Entrez.efetch(db=db, id=accession, rettype='fasta', retmode='text')
    record = SeqIO.read(handle, 'fasta')
    handle.close()
    return record

seq = fetch_sequence('NM_007294')
print(f"{seq.id}: {seq.seq[:50]}...")
```

### Fetch GenBank with Features

```python
def fetch_genbank(accession):
    handle = Entrez.efetch(db='nucleotide', id=accession, rettype='gb', retmode='text')
    record = SeqIO.read(handle, 'genbank')
    handle.close()
    return record

gb = fetch_genbank('NM_007294')
for feature in gb.features:
    if feature.type == 'CDS':
        print(f"CDS: {feature.location}")
        print(f"Product: {feature.qualifiers.get('product', ['?'])[0]}")
```

### Fetch PubMed Abstract

```python
def fetch_abstract(pmid):
    handle = Entrez.efetch(db='pubmed', id=pmid, rettype='abstract', retmode='text')
    abstract = handle.read()
    handle.close()
    return abstract

abstract = fetch_abstract('35412348')
print(abstract)
```

### Get Record Summaries

```python
def get_summaries(db, ids):
    if isinstance(ids, list):
        ids = ','.join(ids)
    handle = Entrez.esummary(db=db, id=ids)
    records = Entrez.read(handle)
    handle.close()
    return records

summaries = get_summaries('nucleotide', ['NM_007294', 'NM_000059'])
for s in summaries:
    print(f"{s['Caption']}: {s['Title'][:50]}... ({s['Length']} bp)")
```

### Search Then Fetch

```python
# Search for records
handle = Entrez.esearch(db='nucleotide', term='human[orgn] AND insulin[gene] AND mRNA[fkey]', retmax=5)
search_results = Entrez.read(handle)
handle.close()

ids = search_results['IdList']

# Fetch the sequences
handle = Entrez.efetch(db='nucleotide', id=','.join(ids), rettype='fasta', retmode='text')
records = list(SeqIO.parse(handle, 'fasta'))
handle.close()

for record in records:
    print(f"{record.id}: {len(record.seq)} bp")
```

### Fetch Protein by Gene ID

```python
# Search gene database
handle = Entrez.esearch(db='gene', term='BRCA1[sym] AND human[orgn]')
result = Entrez.read(handle)
handle.close()
gene_id = result['IdList'][0]

# Get linked protein IDs
handle = Entrez.elink(dbfrom='gene', db='protein', id=gene_id)
links = Entrez.read(handle)
handle.close()

protein_ids = [link['Id'] for link in links[0]['LinkSetDb'][0]['Link'][:3]]

# Fetch proteins
handle = Entrez.efetch(db='protein', id=','.join(protein_ids), rettype='fasta', retmode='text')
proteins = list(SeqIO.parse(handle, 'fasta'))
handle.close()
```

### Save Fetched Records to File

```python
def download_sequences(ids, output_file, db='nucleotide', format='fasta'):
    handle = Entrez.efetch(db=db, id=','.join(ids), rettype=format, retmode='text')
    with open(output_file, 'w') as out:
        out.write(handle.read())
    handle.close()

download_sequences(['NM_007294', 'NM_000059'], 'brca_genes.fasta')
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `HTTPError 400` | Invalid ID or parameters | Verify ID exists, check rettype |
| `HTTPError 429` | Rate limit exceeded | Add delays or use API key |
| Empty result | Record doesn't exist | Verify accession in web browser |
| `ValueError` in SeqIO | Wrong format specified | Match rettype with SeqIO format |
| `ExpatError` | XML parsing error | Use `retmode='text'` instead |

## Decision Tree

```
Need to retrieve NCBI records?
├── Need full sequence?
│   └── Use efetch with rettype='fasta'
├── Need sequence + annotations?
│   └── Use efetch with rettype='gb' (GenBank)
├── Just need metadata (length, organism)?
│   └── Use esummary (faster)
├── Need PubMed abstract?
│   └── Use efetch with rettype='abstract'
├── Need structured data for parsing?
│   └── Use efetch with retmode='xml' + Entrez.read()
├── Downloading many records?
│   └── See batch-downloads skill
└── Need records from multiple databases?
    └── See entrez-link skill first
```

## Related Skills

- entrez-search - Find record IDs before fetching
- entrez-link - Find related records in other databases
- batch-downloads - Download large numbers of records efficiently
- sequence-io/read-sequences - Parse downloaded sequences with SeqIO
