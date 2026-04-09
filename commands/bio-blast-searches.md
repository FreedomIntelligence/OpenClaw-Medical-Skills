# bio-blast-searches

> Run remote BLAST searches against NCBI databases using Biopython Bio.Blast. Use when identifying unknown sequences, finding homologs, or searching for sequence similarity against NCBI's nr/nt databases.

**Available tools:** Read, Bash

# BLAST Searches

Run BLAST searches against NCBI databases using Biopython's Bio.Blast module.

## Required Import

```python
from Bio.Blast import NCBIWWW, NCBIXML
from Bio import SeqIO
```

## BLAST Programs

| Program | Query | Database | Use Case |
|---------|-------|----------|----------|
| `blastn` | Nucleotide | Nucleotide | DNA/RNA sequence similarity |
| `blastp` | Protein | Protein | Protein sequence similarity |
| `blastx` | Nucleotide | Protein | Find protein hits for DNA query |
| `tblastn` | Protein | Nucleotide | Find DNA encoding protein-like |
| `tblastx` | Nucleotide | Nucleotide | Translated vs translated |

## Core Function

### NCBIWWW.qblast()

Submit a BLAST query to NCBI servers.

```python
from Bio.Blast import NCBIWWW

# Simple BLASTN search
result_handle = NCBIWWW.qblast('blastn', 'nt', sequence)
```

**Key Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `program` | BLAST program | `'blastn'`, `'blastp'` |
| `database` | Target database | `'nr'`, `'nt'`, `'refseq_rna'` |
| `sequence` | Query sequence | String or SeqRecord |
| `entrez_query` | Limit by Entrez query | `'Homo sapiens[organism]'` |
| `hitlist_size` | Max hits to return | `50` |
| `expect` | E-value threshold | `0.001` |
| `word_size` | Word size | `11` for blastn |
| `gapcosts` | Gap penalties | `'5 2'` (open, extend) |
| `format_type` | Output format | `'XML'` (default), `'Text'` |

## Common Databases

**Nucleotide:**
| Database | Description |
|----------|-------------|
| `nt` | All GenBank + EMBL + DDBJ |
| `refseq_rna` | RefSeq RNA sequences |
| `refseq_genomic` | RefSeq genomic sequences |

**Protein:**
| Database | Description |
|----------|-------------|
| `nr` | Non-redundant protein |
| `refseq_protein` | RefSeq proteins |
| `swissprot` | SwissProt (curated) |
| `pdb` | Protein structures |

## Parsing Results

### NCBIXML Parser

```python
from Bio.Blast import NCBIWWW, NCBIXML

# Run BLAST
result_handle = NCBIWWW.qblast('blastn', 'nt', sequence)

# Parse XML results
blast_record = NCBIXML.read(result_handle)
result_handle.close()

# Iterate hits
for alignment in blast_record.alignments:
    print(f"Hit: {alignment.title}")
    for hsp in alignment.hsps:
        print(f"  E-value: {hsp.expect}")
        print(f"  Score: {hsp.score}")
        print(f"  Identity: {hsp.identities}/{hsp.align_length}")
```

### Alignment/HSP Attributes

```python
# Alignment (hit) attributes
alignment.title          # Hit description
alignment.accession      # Accession number
alignment.length         # Subject sequence length
alignment.hsps           # List of HSPs

# HSP (High-scoring Segment Pair) attributes
hsp.score               # Raw score
hsp.bits                # Bit score
hsp.expect              # E-value
hsp.identities          # Number of identical positions
hsp.positives           # Number of positive-scoring positions
hsp.gaps                # Number of gaps
hsp.align_length        # Alignment length
hsp.query               # Aligned query sequence
hsp.match               # Match line (| for identity)
hsp.sbjct               # Aligned subject sequence
hsp.query_start         # Query start position
hsp.query_end           # Query end position
hsp.sbjct_start         # Subject start position
hsp.sbjct_end           # Subject end position
hsp.strand              # Strand (blastn)
hsp.frame               # Reading frame (blastx/tblastn)
```

## Code Patterns

### Basic BLASTN

```python
from Bio.Blast import NCBIWWW, NCBIXML

sequence = '''ATGAAAGCAATTTTCGTACTGAAAGGTTGGTGGCGCACTTCCTGA'''

print("Running BLASTN (this may take a minute)...")
result_handle = NCBIWWW.qblast('blastn', 'nt', sequence)

blast_record = NCBIXML.read(result_handle)
result_handle.close()

print(f"\nFound {len(blast_record.alignments)} hits")
for alignment in blast_record.alignments[:5]:
    hsp = alignment.hsps[0]
    print(f"\n{alignment.title[:70]}...")
    print(f"  E-value: {hsp.expect:.2e}")
    print(f"  Identity: {hsp.identities}/{hsp.align_length} ({100*hsp.identities/hsp.align_length:.1f}%)")
```

### BLASTP with Organism Filter

```python
from Bio.Blast import NCBIWWW, NCBIXML

protein_seq = '''MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH'''

result_handle = NCBIWWW.qblast(
    'blastp',
    'nr',
    protein_seq,
    entrez_query='Mammalia[organism]',
    hitlist_size=20,
    expect=0.001
)

blast_record = NCBIXML.read(result_handle)
result_handle.close()

for alignment in blast_record.alignments[:10]:
    hsp = alignment.hsps[0]
    print(f"{alignment.accession}: E={hsp.expect:.2e} - {alignment.title[:50]}...")
```

### BLAST from FASTA File

```python
from Bio import SeqIO
from Bio.Blast import NCBIWWW, NCBIXML

record = SeqIO.read('query.fasta', 'fasta')

result_handle = NCBIWWW.qblast('blastn', 'nt', record.seq)
blast_record = NCBIXML.read(result_handle)
result_handle.close()

for alignment in blast_record.alignments[:5]:
    print(f"{alignment.accession}: {alignment.title[:60]}...")
```

### Save Results to File

```python
from Bio.Blast import NCBIWWW

result_handle = NCBIWWW.qblast('blastn', 'nt', sequence)

# Save XML for later parsing
with open('blast_results.xml', 'w') as out:
    out.write(result_handle.read())
result_handle.close()

# Parse saved file
from Bio.Blast import NCBIXML
with open('blast_results.xml') as f:
    blast_record = NCBIXML.read(f)
```

### Extract Top Hits

```python
def get_top_hits(sequence, program='blastn', database='nt', num_hits=10, evalue=0.01):
    result_handle = NCBIWWW.qblast(
        program, database, sequence,
        hitlist_size=num_hits,
        expect=evalue
    )
    blast_record = NCBIXML.read(result_handle)
    result_handle.close()

    hits = []
    for alignment in blast_record.alignments:
        hsp = alignment.hsps[0]
        hits.append({
            'accession': alignment.accession,
            'title': alignment.title,
            'evalue': hsp.expect,
            'identity': hsp.identities / hsp.align_length,
            'coverage': hsp.align_length / blast_record.query_length
        })
    return hits

hits = get_top_hits(my_sequence, num_hits=5)
for hit in hits:
    print(f"{hit['accession']}: {hit['identity']:.1%} identity, E={hit['evalue']:.2e}")
```

### BLASTX (DNA to Protein)

```python
from Bio.Blast import NCBIWWW, NCBIXML

dna_sequence = '''ATGAAAGCAATTTTCGTACTGAAAGGTTGGTGGCGCACTTCCTGA'''

result_handle = NCBIWWW.qblast('blastx', 'nr', dna_sequence)
blast_record = NCBIXML.read(result_handle)
result_handle.close()

for alignment in blast_record.alignments[:5]:
    hsp = alignment.hsps[0]
    print(f"{alignment.accession}: frame {hsp.frame}, E={hsp.expect:.2e}")
    print(f"  {alignment.title[:60]}...")
```

### Multiple Sequences

```python
from Bio import SeqIO
from Bio.Blast import NCBIWWW, NCBIXML
import time

def blast_multiple(fasta_file, program='blastn', database='nt'):
    results = {}
    for record in SeqIO.parse(fasta_file, 'fasta'):
        print(f"BLASTing {record.id}...")

        result_handle = NCBIWWW.qblast(program, database, str(record.seq), hitlist_size=5)
        blast_record = NCBIXML.read(result_handle)
        result_handle.close()

        results[record.id] = blast_record
        time.sleep(5)  # Be nice to NCBI servers

    return results
```

### Filter by Identity/Coverage

```python
def filter_blast_hits(blast_record, min_identity=0.9, min_coverage=0.8):
    query_length = blast_record.query_length
    filtered = []

    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            identity = hsp.identities / hsp.align_length
            coverage = hsp.align_length / query_length

            if identity >= min_identity and coverage >= min_coverage:
                filtered.append({
                    'accession': alignment.accession,
                    'title': alignment.title,
                    'identity': identity,
                    'coverage': coverage,
                    'evalue': hsp.expect
                })

    return filtered
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Timeout | NCBI servers busy | Retry later, use smaller query |
| No hits | Wrong database or program | Check program/database match |
| Empty results | E-value too stringent | Increase expect parameter |
| URLError | Network issue | Check connection, retry |

## Timing Notes

- Remote BLAST can take 30 seconds to several minutes
- Longer queries take longer
- Peak times (US business hours) may be slower
- For many queries, consider local BLAST

## Decision Tree

```
Need to BLAST a sequence?
├── DNA query?
│   ├── Against DNA database? → blastn
│   └── Against protein database? → blastx
├── Protein query?
│   ├── Against protein database? → blastp
│   └── Against DNA database? → tblastn
├── Want to limit organisms?
│   └── Use entrez_query parameter
├── Need many searches?
│   └── Consider local-blast skill
└── Need results fast?
    └── Use local-blast skill
```

## Related Skills

- local-blast - Run BLAST locally for faster, unlimited searches
- entrez-fetch - Fetch full records for BLAST hits
- sequence-io - Read query sequences from files
