# bio-local-blast

> Run local BLAST searches using BLAST+ command-line tools. Use when running fast unlimited searches, building custom databases, performing large-scale analysis, or when NCBI servers are slow or unavailable.

**Available tools:** Read, Bash

# Local BLAST

Run BLAST searches locally using NCBI BLAST+ command-line tools.

## Installation

```bash
# macOS
brew install blast

# Ubuntu/Debian
sudo apt install ncbi-blast+

# conda
conda install -c bioconda blast

# Verify installation
blastn -version
```

## BLAST+ Programs

| Command | Query | Database | Description |
|---------|-------|----------|-------------|
| `blastn` | DNA | DNA | Nucleotide-nucleotide |
| `blastp` | Protein | Protein | Protein-protein |
| `blastx` | DNA | Protein | Translated query vs protein |
| `tblastn` | Protein | DNA | Protein vs translated DB |
| `tblastx` | DNA | DNA | Translated vs translated |
| `makeblastdb` | - | - | Create BLAST database |

## Creating BLAST Databases

### makeblastdb - Create Database

```bash
# Create nucleotide database
makeblastdb -in sequences.fasta -dbtype nucl -out my_db

# Create protein database
makeblastdb -in proteins.fasta -dbtype prot -out my_proteins

# With title and parse sequence IDs
makeblastdb -in sequences.fasta -dbtype nucl -out my_db \
    -title "My Reference Database" -parse_seqids
```

**Key Options:**
| Option | Description | Values |
|--------|-------------|--------|
| `-in` | Input FASTA file | Path |
| `-dbtype` | Database type | `nucl`, `prot` |
| `-out` | Output database name | Path prefix |
| `-title` | Database title | String |
| `-parse_seqids` | Enable ID-based retrieval | Flag |
| `-taxid` | Assign taxonomy ID | Integer |
| `-taxid_map` | Taxonomy ID mapping file | Path |

### Database Files Created

```
my_db.nhr  # Header file (nucl) / .phr (prot)
my_db.nin  # Index file (nucl) / .pin (prot)
my_db.nsq  # Sequence file (nucl) / .psq (prot)
my_db.ndb  # Alias file (optional)
my_db.not  # ID index (if parse_seqids)
my_db.ntf  # Index (if parse_seqids)
my_db.nto  # Index (if parse_seqids)
```

## Running BLAST Searches

### Basic Usage

```bash
# BLASTN
blastn -query query.fasta -db my_db -out results.txt

# BLASTP
blastp -query proteins.fasta -db my_proteins -out results.txt

# BLASTX (translate query, search protein DB)
blastx -query genes.fasta -db nr -out results.txt
```

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `-query` | Query FASTA file | `-query seq.fa` |
| `-db` | Database name | `-db nt` |
| `-out` | Output file | `-out results.txt` |
| `-outfmt` | Output format | `-outfmt 6` |
| `-evalue` | E-value threshold | `-evalue 1e-5` |
| `-num_threads` | CPU threads | `-num_threads 8` |
| `-max_target_seqs` | Max hits | `-max_target_seqs 100` |
| `-max_hsps` | Max HSPs per hit | `-max_hsps 1` |
| `-word_size` | Word size | `-word_size 11` |
| `-dust` | Filter low complexity (nucl) | `-dust yes` |
| `-seg` | Filter low complexity (prot) | `-seg yes` |

### Output Formats (-outfmt)

| Value | Format |
|-------|--------|
| `0` | Pairwise (default) |
| `1` | Query-anchored with identities |
| `5` | BLAST XML |
| `6` | Tabular |
| `7` | Tabular with comments |
| `10` | CSV |

### Tabular Output Fields (-outfmt 6)

Default columns: `qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore`

Custom columns:
```bash
blastn -query query.fa -db my_db -outfmt "6 qseqid sseqid pident length evalue stitle"
```

**Available Fields:**
| Field | Description |
|-------|-------------|
| `qseqid` | Query ID |
| `sseqid` | Subject ID |
| `pident` | Percent identity |
| `length` | Alignment length |
| `mismatch` | Mismatches |
| `gapopen` | Gap openings |
| `qstart` | Query start |
| `qend` | Query end |
| `sstart` | Subject start |
| `send` | Subject end |
| `evalue` | E-value |
| `bitscore` | Bit score |
| `stitle` | Subject title |
| `qcovs` | Query coverage |
| `qcovhsp` | Query coverage per HSP |

## Code Patterns

### Create Database and Search

```bash
#!/bin/bash
# Create database from reference sequences
makeblastdb -in reference.fasta -dbtype nucl -out ref_db -parse_seqids

# Run BLAST
blastn -query query.fasta -db ref_db -out results.txt \
    -outfmt 6 -evalue 1e-10 -num_threads 4

# View results
head results.txt
```

### BLAST with Tabular Output

```bash
#!/bin/bash
blastn -query query.fasta -db my_db \
    -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore stitle" \
    -evalue 1e-5 \
    -max_target_seqs 10 \
    -num_threads 8 \
    -out results.tsv
```

### Filter and Sort Results

```bash
# Get hits with >90% identity
awk -F'\t' '$3 >= 90' results.tsv

# Sort by E-value
sort -t$'\t' -k11 -g results.tsv

# Get best hit per query
sort -t$'\t' -k1,1 -k11,11g results.tsv | sort -t$'\t' -k1,1 -u
```

### Batch BLAST Multiple Files

```bash
#!/bin/bash
for query_file in queries/*.fasta; do
    base=$(basename "$query_file" .fasta)
    echo "Processing $base..."

    blastn -query "$query_file" -db my_db \
        -outfmt 6 -evalue 1e-5 -num_threads 4 \
        -out "results/${base}_blast.tsv"
done
```

### Python Wrapper

```python
import subprocess
import os

def make_blast_db(fasta_file, db_name, db_type='nucl'):
    cmd = ['makeblastdb', '-in', fasta_file, '-dbtype', db_type, '-out', db_name, '-parse_seqids']
    subprocess.run(cmd, check=True)

def run_blast(query, db, output, program='blastn', evalue=1e-5, threads=4, outfmt=6):
    cmd = [program, '-query', query, '-db', db, '-out', output,
           '-outfmt', str(outfmt), '-evalue', str(evalue), '-num_threads', str(threads)]
    subprocess.run(cmd, check=True)

def parse_blast_tabular(filename):
    columns = ['qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen',
               'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore']
    hits = []
    with open(filename) as f:
        for line in f:
            values = line.strip().split('\t')
            hit = dict(zip(columns, values))
            hit['pident'] = float(hit['pident'])
            hit['evalue'] = float(hit['evalue'])
            hit['length'] = int(hit['length'])
            hits.append(hit)
    return hits

# Example usage
make_blast_db('reference.fasta', 'ref_db')
run_blast('query.fasta', 'ref_db', 'results.tsv')
hits = parse_blast_tabular('results.tsv')
for hit in hits[:5]:
    print(f"{hit['qseqid']} -> {hit['sseqid']}: {hit['pident']}% identity, E={hit['evalue']}")
```

### Reciprocal Best BLAST

```bash
#!/bin/bash
# Forward BLAST: A vs B
blastp -query species_A.fasta -db species_B_db -outfmt 6 -evalue 1e-5 \
    -max_target_seqs 1 -out A_vs_B.tsv

# Reverse BLAST: B vs A
blastp -query species_B.fasta -db species_A_db -outfmt 6 -evalue 1e-5 \
    -max_target_seqs 1 -out B_vs_A.tsv

# Find reciprocal best hits
awk 'NR==FNR {a[$1]=$2; next} $2 in a && a[$2]==$1' A_vs_B.tsv B_vs_A.tsv
```

### Extract Hit Sequences

```bash
# Get subject sequence by ID (requires -parse_seqids)
blastdbcmd -db my_db -entry "sequence_id" -out hit.fasta

# Get multiple sequences
blastdbcmd -db my_db -entry_batch ids.txt -out hits.fasta

# Get all sequences from database
blastdbcmd -db my_db -entry all -out all_seqs.fasta
```

## Prebuilt Databases

Download from NCBI:
```bash
# Download and extract (uses update_blastdb.pl)
update_blastdb.pl --decompress nt

# Or download manually from:
# https://ftp.ncbi.nlm.nih.gov/blast/db/
```

Common databases:
- `nt` - All nucleotide sequences
- `nr` - Non-redundant protein
- `refseq_rna` - RefSeq RNA
- `swissprot` - UniProt SwissProt

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `BLAST Database error` | Database not found | Check path, rebuild database |
| `No hits found` | No matches or wrong DB type | Verify database type matches query |
| `Sequence too short` | Query below word size | Lower word_size or use longer query |
| `Out of memory` | Large database | Reduce threads, use -num_threads 1 |

## Local vs Remote BLAST

| Aspect | Local | Remote |
|--------|-------|--------|
| Speed | Fast | Can be slow |
| Databases | Must download/create | All NCBI DBs available |
| Throughput | Unlimited | Rate limited |
| Setup | Requires installation | Just Biopython |
| Updates | Manual | Automatic |

## Decision Tree

```
Running BLAST locally?
├── Have reference sequences?
│   └── makeblastdb to create database
├── Download NCBI database?
│   └── update_blastdb.pl or manual download
├── Need tabular output?
│   └── -outfmt 6 (or 7 with headers)
├── Filter low-complexity?
│   └── -dust yes (nucl) or -seg yes (prot)
├── Multiple queries?
│   └── Put all in one FASTA, use -num_threads
├── Need XML output?
│   └── -outfmt 5
└── Extract hit sequences?
    └── blastdbcmd -entry
```

## Related Skills

- blast-searches - Remote BLAST via NCBI (no installation needed)
- sequence-io - Read/write FASTA files for queries
- batch-downloads - Download sequences to build local databases
