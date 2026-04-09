# bio-entrez-link

> Find cross-references between NCBI databases using Biopython Bio.Entrez. Use when navigating from genes to proteins, sequences to publications, finding related records, or discovering database relationships.

**Available tools:** Read, Bash

# Entrez Link

Navigate between NCBI databases using Biopython's Entrez module (ELink utility).

## Required Setup

```python
from Bio import Entrez

Entrez.email = 'your.email@example.com'  # Required by NCBI
Entrez.api_key = 'your_api_key'          # Optional, raises rate limit
```

## Core Function

### Entrez.elink() - Cross-Database Links

Find related records in the same or different databases.

```python
# Find proteins linked to a gene
handle = Entrez.elink(dbfrom='gene', db='protein', id='672')
record = Entrez.read(handle)
handle.close()

# Extract linked IDs
linkset = record[0]
if linkset['LinkSetDb']:
    links = linkset['LinkSetDb'][0]['Link']
    protein_ids = [link['Id'] for link in links]
    print(f"Found {len(protein_ids)} linked proteins")
```

**Key Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `dbfrom` | Source database | `'gene'` |
| `db` | Target database | `'protein'` |
| `id` | Source record ID(s) | `'672'` or `'672,675'` |
| `linkname` | Specific link type | `'gene_protein_refseq'` |
| `cmd` | Link command | `'neighbor'`, `'neighbor_score'` |

### ELink Result Structure

```python
record[0]                          # First linkset
record[0]['DbFrom']                # Source database
record[0]['IdList']                # Input IDs
record[0]['LinkSetDb']             # List of link results
record[0]['LinkSetDb'][0]['DbTo']  # Target database
record[0]['LinkSetDb'][0]['LinkName']  # Link name
record[0]['LinkSetDb'][0]['Link']  # List of linked records
record[0]['LinkSetDb'][0]['Link'][0]['Id']  # Linked ID
```

## Common Link Paths

### Gene to Other Databases

| From | To | Link Name | Description |
|------|-----|-----------|-------------|
| gene | protein | `gene_protein` | All proteins |
| gene | protein | `gene_protein_refseq` | RefSeq proteins only |
| gene | nucleotide | `gene_nuccore` | Nucleotide sequences |
| gene | nucleotide | `gene_nuccore_refseqrna` | RefSeq mRNA |
| gene | pubmed | `gene_pubmed` | Related publications |
| gene | homologene | `gene_homologene` | Homologs |
| gene | snp | `gene_snp` | SNPs in gene |
| gene | clinvar | `gene_clinvar` | Clinical variants |

### Nucleotide to Other Databases

| From | To | Link Name | Description |
|------|-----|-----------|-------------|
| nucleotide | protein | `nuccore_protein` | Encoded proteins |
| nucleotide | gene | `nuccore_gene` | Gene records |
| nucleotide | pubmed | `nuccore_pubmed` | Publications |
| nucleotide | taxonomy | `nuccore_taxonomy` | Organism taxonomy |
| nucleotide | biosample | `nuccore_biosample` | Sample info |
| nucleotide | sra | `nuccore_sra` | Related SRA data |

### Protein to Other Databases

| From | To | Link Name | Description |
|------|-----|-----------|-------------|
| protein | nucleotide | `protein_nuccore` | Coding sequences |
| protein | gene | `protein_gene` | Gene records |
| protein | pubmed | `protein_pubmed` | Publications |
| protein | structure | `protein_structure` | 3D structures |
| protein | cdd | `protein_cdd` | Conserved domains |

### PubMed Links

| From | To | Link Name | Description |
|------|-----|-----------|-------------|
| pubmed | pubmed | `pubmed_pubmed` | Related articles |
| pubmed | gene | `pubmed_gene` | Mentioned genes |
| pubmed | protein | `pubmed_protein` | Mentioned proteins |
| pubmed | nucleotide | `pubmed_nuccore` | Mentioned sequences |

## Code Patterns

### Gene to Protein

```python
from Bio import Entrez

Entrez.email = 'your.email@example.com'

def get_proteins_for_gene(gene_id):
    handle = Entrez.elink(dbfrom='gene', db='protein', id=gene_id, linkname='gene_protein_refseq')
    record = Entrez.read(handle)
    handle.close()

    if not record[0]['LinkSetDb']:
        return []
    return [link['Id'] for link in record[0]['LinkSetDb'][0]['Link']]

protein_ids = get_proteins_for_gene('672')  # BRCA1
print(f"RefSeq proteins: {protein_ids[:5]}")
```

### Nucleotide to Gene

```python
def get_gene_for_nucleotide(nuc_id):
    handle = Entrez.elink(dbfrom='nucleotide', db='gene', id=nuc_id)
    record = Entrez.read(handle)
    handle.close()

    if not record[0]['LinkSetDb']:
        return None
    return record[0]['LinkSetDb'][0]['Link'][0]['Id']

gene_id = get_gene_for_nucleotide('NM_007294')
print(f"Gene ID: {gene_id}")
```

### Find Related PubMed Articles

```python
def get_related_articles(pmid, max_results=10):
    handle = Entrez.elink(dbfrom='pubmed', db='pubmed', id=pmid, linkname='pubmed_pubmed')
    record = Entrez.read(handle)
    handle.close()

    if not record[0]['LinkSetDb']:
        return []
    links = record[0]['LinkSetDb'][0]['Link']
    return [link['Id'] for link in links[:max_results]]

related = get_related_articles('35412348')
print(f"Related articles: {related}")
```

### Get All Available Links

```python
def discover_links(db, record_id):
    handle = Entrez.elink(dbfrom=db, id=record_id, cmd='acheck')
    record = Entrez.read(handle)
    handle.close()

    links = {}
    for linkset in record[0].get('LinkSetDb', []):
        links[linkset['LinkName']] = linkset['DbTo']
    return links

available = discover_links('gene', '672')
for name, target in available.items():
    print(f"{name} -> {target}")
```

### Navigate Gene -> Protein -> Structure

```python
def gene_to_structures(gene_id):
    # Gene to protein
    handle = Entrez.elink(dbfrom='gene', db='protein', id=gene_id, linkname='gene_protein_refseq')
    record = Entrez.read(handle)
    handle.close()

    if not record[0]['LinkSetDb']:
        return []
    protein_ids = [link['Id'] for link in record[0]['LinkSetDb'][0]['Link'][:5]]

    # Protein to structure
    handle = Entrez.elink(dbfrom='protein', db='structure', id=','.join(protein_ids))
    record = Entrez.read(handle)
    handle.close()

    structure_ids = []
    for linkset in record:
        if linkset['LinkSetDb']:
            structure_ids.extend([link['Id'] for link in linkset['LinkSetDb'][0]['Link']])
    return structure_ids

structures = gene_to_structures('672')
print(f"Structure IDs: {structures[:5]}")
```

### Link Multiple IDs at Once

```python
def batch_link(dbfrom, db, ids):
    if isinstance(ids, list):
        ids = ','.join(ids)

    handle = Entrez.elink(dbfrom=dbfrom, db=db, id=ids)
    record = Entrez.read(handle)
    handle.close()

    # Returns one linkset per input ID
    results = {}
    for linkset in record:
        source_id = linkset['IdList'][0]
        linked_ids = []
        if linkset['LinkSetDb']:
            linked_ids = [link['Id'] for link in linkset['LinkSetDb'][0]['Link']]
        results[source_id] = linked_ids
    return results

results = batch_link('gene', 'protein', ['672', '675', '7157'])
for gene, proteins in results.items():
    print(f"Gene {gene}: {len(proteins)} proteins")
```

### Get Publications for a Sequence

```python
def get_sequence_publications(accession):
    # First get the GI/UID
    handle = Entrez.esearch(db='nucleotide', term=f'{accession}[accn]')
    search = Entrez.read(handle)
    handle.close()

    if not search['IdList']:
        return []
    uid = search['IdList'][0]

    # Link to PubMed
    handle = Entrez.elink(dbfrom='nucleotide', db='pubmed', id=uid)
    record = Entrez.read(handle)
    handle.close()

    if not record[0]['LinkSetDb']:
        return []
    return [link['Id'] for link in record[0]['LinkSetDb'][0]['Link']]

pmids = get_sequence_publications('NM_007294')
print(f"PubMed IDs: {pmids[:5]}")
```

## Link Commands

| Command | Description |
|---------|-------------|
| `neighbor` | Default - get linked records |
| `neighbor_score` | Include relevance scores |
| `neighbor_history` | Store results in history |
| `acheck` | List all available links |
| `ncheck` | Check if any links exist |
| `lcheck` | Check specific link exists |
| `llinks` | Get URLs to Entrez links |
| `prlinks` | Get provider links (external) |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Empty `LinkSetDb` | No links exist | Check if record has linked data |
| `HTTPError 400` | Invalid ID or database | Verify ID exists in source database |
| `KeyError` | Missing expected field | Check if `LinkSetDb` is empty first |
| Single linkset expected, got list | Multiple input IDs | Iterate through record list |

## Decision Tree

```
Need to find related records?
├── Know what link you want?
│   └── Use elink with specific linkname
├── Discover what links exist?
│   └── Use elink with cmd='acheck'
├── Navigate to target database?
│   └── Use elink(dbfrom=X, db=Y, id=Z)
├── Find related records in same database?
│   └── Use elink(dbfrom=X, db=X) with neighbor
├── Chain multiple databases?
│   └── Call elink multiple times
└── Need the actual records?
    └── Use elink first, then efetch with IDs
```

## Related Skills

- entrez-search - Search databases before linking
- entrez-fetch - Retrieve records after finding linked IDs
- batch-downloads - Download many linked records efficiently
