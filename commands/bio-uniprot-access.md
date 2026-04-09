# bio-uniprot-access

> Access UniProt protein database for sequences, annotations, and functional information. Use when retrieving protein data, GO terms, domain annotations, or protein-protein interactions.

**Available tools:** Read, Bash

# UniProt Access

Query UniProt for protein sequences, functional annotations, and cross-references.

## UniProt REST API

### Fetch Single Entry

```python
import requests

def fetch_uniprot(accession, format='fasta'):
    '''Fetch UniProt entry. Formats: fasta, json, txt, xml, gff'''
    url = f'https://rest.uniprot.org/uniprotkb/{accession}.{format}'
    response = requests.get(url)
    response.raise_for_status()
    return response.text

sequence = fetch_uniprot('P53_HUMAN', 'fasta')
entry_json = fetch_uniprot('P04637', 'json')
```

### Search UniProt

```python
def search_uniprot(query, format='json', size=25):
    '''Search UniProt with query syntax'''
    url = 'https://rest.uniprot.org/uniprotkb/search'
    params = {'query': query, 'format': format, 'size': size}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json() if format == 'json' else response.text

results = search_uniprot('gene:BRCA1 AND organism_id:9606')
for entry in results['results']:
    print(entry['primaryAccession'], entry['proteinDescription']['recommendedName']['fullName']['value'])
```

### Query Syntax

| Query | Description |
|-------|-------------|
| `gene:TP53` | Gene name |
| `organism_id:9606` | Human (NCBI taxonomy) |
| `reviewed:true` | Swiss-Prot only |
| `length:[100 TO 500]` | Sequence length range |
| `go:0006915` | GO term (apoptosis) |
| `keyword:kinase` | Keyword |
| `ec:2.7.1.1` | Enzyme classification |
| `database:pdb` | Has PDB structure |

### Combine Queries

```python
# Human kinases with structures
query = 'organism_id:9606 AND keyword:kinase AND database:pdb AND reviewed:true'
results = search_uniprot(query, size=100)
```

## Batch Retrieval

### Multiple Accessions

```python
def batch_fetch(accessions, format='fasta'):
    '''Fetch multiple entries'''
    url = 'https://rest.uniprot.org/uniprotkb/accessions'
    params = {'accessions': ','.join(accessions), 'format': format}
    response = requests.get(url, params=params)
    return response.text

accessions = ['P04637', 'P53_HUMAN', 'Q9Y6K9']
sequences = batch_fetch(accessions)
```

### Stream Large Results

```python
def search_all(query, format='tsv', fields=None):
    '''Stream all results for large queries'''
    url = 'https://rest.uniprot.org/uniprotkb/stream'
    params = {'query': query, 'format': format}
    if fields:
        params['fields'] = ','.join(fields)
    response = requests.get(url, params=params, stream=True)
    return response.text

# Get all human proteins as TSV
all_human = search_all('organism_id:9606 AND reviewed:true',
                       fields=['accession', 'gene_names', 'protein_name'])
```

## ID Mapping

### Map Between Databases

```python
import time

def map_ids(ids, from_db, to_db):
    '''Map IDs between databases'''
    url = 'https://rest.uniprot.org/idmapping/run'
    response = requests.post(url, data={'ids': ','.join(ids), 'from': from_db, 'to': to_db})
    job_id = response.json()['jobId']

    # Poll for results
    while True:
        status = requests.get(f'https://rest.uniprot.org/idmapping/status/{job_id}')
        if 'results' in status.json() or 'failedIds' in status.json():
            break
        time.sleep(1)

    results = requests.get(f'https://rest.uniprot.org/idmapping/results/{job_id}')
    return results.json()

# Ensembl gene IDs to UniProt
mapping = map_ids(['ENSG00000141510', 'ENSG00000171862'], 'Ensembl', 'UniProtKB')
for result in mapping['results']:
    print(result['from'], '->', result['to']['primaryAccession'])
```

### Common Database Codes

| Code | Database |
|------|----------|
| `UniProtKB` | UniProt accessions |
| `UniProtKB_AC-ID` | UniProt AC or ID |
| `Ensembl` | Ensembl gene ID |
| `RefSeq_Protein` | RefSeq protein |
| `PDB` | PDB ID |
| `GeneID` | NCBI Gene ID |
| `Gene_Name` | Gene symbols |

## Extract Specific Data

### Parse JSON Entry

```python
import json

entry = json.loads(fetch_uniprot('P04637', 'json'))

accession = entry['primaryAccession']
gene_name = entry['genes'][0]['geneName']['value']
protein_name = entry['proteinDescription']['recommendedName']['fullName']['value']
sequence = entry['sequence']['value']
length = entry['sequence']['length']

# GO terms
go_terms = [ref for ref in entry.get('uniProtKBCrossReferences', [])
            if ref['database'] == 'GO']

# Domains (InterPro)
domains = [ref for ref in entry.get('uniProtKBCrossReferences', [])
           if ref['database'] == 'InterPro']

# PDB structures
pdb_refs = [ref for ref in entry.get('uniProtKBCrossReferences', [])
            if ref['database'] == 'PDB']
```

### Get Specific Fields (TSV)

```python
def get_fields(query, fields):
    '''Get specific fields as DataFrame'''
    import pandas as pd
    from io import StringIO

    url = 'https://rest.uniprot.org/uniprotkb/search'
    params = {'query': query, 'format': 'tsv', 'fields': ','.join(fields), 'size': 500}
    response = requests.get(url, params=params)
    return pd.read_csv(StringIO(response.text), sep='\t')

df = get_fields('organism_id:9606 AND keyword:kinase AND reviewed:true',
                ['accession', 'gene_names', 'protein_name', 'length', 'go_p'])
```

### Available Fields

| Field | Description |
|-------|-------------|
| `accession` | UniProt accession |
| `gene_names` | Gene names |
| `protein_name` | Protein name |
| `organism_name` | Species |
| `length` | Sequence length |
| `mass` | Molecular mass |
| `go_p` | GO biological process |
| `go_c` | GO cellular component |
| `go_f` | GO molecular function |
| `xref_pdb` | PDB cross-references |
| `ft_domain` | Domain features |
| `ft_binding` | Binding sites |

## Biopython Integration

```python
from Bio import SeqIO
from io import StringIO

fasta_text = fetch_uniprot('P04637', 'fasta')
record = SeqIO.read(StringIO(fasta_text), 'fasta')
print(record.id, len(record.seq))
```

## Related Skills

- database-access/entrez-fetch - NCBI protein access
- database-access/blast-searches - BLAST against UniProt
- structural-biology/structure-io - Download PDB structures
- structural-biology/alphafold-predictions - AlphaFold structures
