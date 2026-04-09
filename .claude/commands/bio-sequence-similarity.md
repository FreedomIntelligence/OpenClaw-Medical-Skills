# bio-sequence-similarity

> Find homologous sequences using iterative BLAST (PSI-BLAST), profile HMMs (HMMER), and reciprocal best hit analysis. Use when identifying orthologs, distant homologs, or protein family members where standard BLAST is not sensitive enough.

**Available tools:** Read, Bash

# Sequence Similarity Searches

Advanced methods for finding homologous sequences beyond standard BLAST.

## PSI-BLAST (Position-Specific Iterated BLAST)

Builds a position-specific scoring matrix (PSSM) through iterations to find distant homologs.

### Basic PSI-BLAST

```bash
psiblast -query protein.fasta -db nr -out results.txt -num_iterations 3
```

### Save PSSM for Reuse

```bash
psiblast -query protein.fasta -db nr \
    -out results.txt \
    -out_pssm pssm.asn \
    -out_ascii_pssm pssm.txt \
    -num_iterations 5
```

### Use Existing PSSM

```bash
psiblast -in_pssm pssm.asn -db nr -out results.txt
```

### Output Format

```bash
psiblast -query protein.fasta -db nr \
    -out results.txt \
    -outfmt 6 \
    -num_iterations 3 \
    -inclusion_ethresh 0.001
```

### Key Parameters

```bash
psiblast -query protein.fasta -db nr \
    -num_iterations 5 \
    -inclusion_ethresh 0.001 \
    -evalue 0.01 \
    -num_threads 8 \
    -out results.txt
```

### PSI-BLAST Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| -num_iterations | 1 | Number of iterations |
| -inclusion_ethresh | 0.002 | E-value for PSSM inclusion |
| -evalue | 10 | E-value threshold for reporting |
| -num_threads | 1 | CPU threads |

## HMMER for Profile Searches

HMMER uses profile hidden Markov models for sensitive sequence searches.

### Search with Single Sequence

```bash
jackhmmer -o results.txt -A aligned.sto --cpu 8 query.fasta database.fasta
```

### Build Profile from Alignment

```bash
hmmbuild profile.hmm alignment.sto
```

### Search Database with Profile

```bash
hmmsearch -o results.txt --tblout hits.tbl profile.hmm database.fasta
hmmsearch -o results.txt --domtblout domains.tbl profile.hmm database.fasta
```

### Download Pfam Profiles

```bash
wget https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz
gunzip Pfam-A.hmm.gz
hmmpress Pfam-A.hmm
```

### Scan Sequence Against Pfam

```bash
hmmscan --tblout pfam_hits.tbl --domtblout domains.tbl Pfam-A.hmm query.fasta
```

### Parse HMMER Output

```bash
grep -v "^#" hits.tbl | head
awk '$5 < 1e-10' hits.tbl
```

### HMMER Output Columns (--tblout)

| Column | Description |
|--------|-------------|
| 1 | Target name |
| 2 | Accession |
| 3 | Query name |
| 4 | Query accession |
| 5 | E-value (full sequence) |
| 6 | Score (full sequence) |
| 7 | Bias |
| 8 | E-value (best domain) |
| 9 | Score (best domain) |

## Reciprocal Best Hit (RBH) Analysis

Find orthologs using bidirectional best hits.

### Create BLAST Databases

```bash
makeblastdb -in species_A.fasta -dbtype prot -out species_A_db
makeblastdb -in species_B.fasta -dbtype prot -out species_B_db
```

### Bidirectional BLAST

```bash
blastp -query species_A.fasta -db species_B_db -outfmt 6 -evalue 1e-5 -max_target_seqs 1 > A_vs_B.txt
blastp -query species_B.fasta -db species_A_db -outfmt 6 -evalue 1e-5 -max_target_seqs 1 > B_vs_A.txt
```

### Find Reciprocal Best Hits

```bash
awk 'FNR==NR {a[$1]=$2; next} $2 in a && a[$2]==$1 {print $1"\t"$2}' \
    A_vs_B.txt B_vs_A.txt > reciprocal_best_hits.txt
```

### Python RBH Script

```python
def find_rbh(forward_blast, reverse_blast):
    '''Find reciprocal best hits from BLAST results'''
    forward = {}
    with open(forward_blast) as f:
        for line in f:
            parts = line.strip().split('\t')
            query, subject = parts[0], parts[1]
            if query not in forward:
                forward[query] = subject

    reverse = {}
    with open(reverse_blast) as f:
        for line in f:
            parts = line.strip().split('\t')
            query, subject = parts[0], parts[1]
            if query not in reverse:
                reverse[query] = subject

    rbh = []
    for a, b in forward.items():
        if b in reverse and reverse[b] == a:
            rbh.append((a, b))

    return rbh

rbh_pairs = find_rbh('A_vs_B.txt', 'B_vs_A.txt')
for a, b in rbh_pairs:
    print(f'{a}\t{b}')
```

## Delta-BLAST

Uses conserved domain database for more sensitive initial search.

```bash
deltablast -query protein.fasta -db nr -rpsdb cdd_delta -out results.txt
```

## PHI-BLAST (Pattern-Hit Initiated)

Search with a pattern plus sequence.

```bash
phi_pattern="G-x(2)-[ST]-x-[RK]"
phiblast -query protein.fasta -db nr -pattern "$phi_pattern" -out results.txt
```

## Iterative Search with Biopython

```python
from Bio.Blast import NCBIWWW, NCBIXML

with open('query.fasta') as f:
    query = f.read()

result_handle = NCBIWWW.qblast('psiblast', 'nr', query, expect=0.001, word_size=3)

with open('psiblast_result.xml', 'w') as out:
    out.write(result_handle.read())
result_handle.close()

with open('psiblast_result.xml') as f:
    records = NCBIXML.parse(f)
    for record in records:
        for alignment in record.alignments:
            for hsp in alignment.hsps:
                if hsp.expect < 1e-10:
                    print(f'{alignment.hit_def[:50]}: E={hsp.expect}')
```

## HMMER with Biopython

```python
from Bio import SearchIO

results = SearchIO.parse('hmmsearch_output.txt', 'hmmer3-text')
for query_result in results:
    print(f'Query: {query_result.id}')
    for hit in query_result:
        print(f'  Hit: {hit.id}, E-value: {hit.evalue}')
        for hsp in hit:
            print(f'    Domain: {hsp.bitscore} bits')
```

## Jackhmmer (Iterative HMMER)

Similar to PSI-BLAST but uses HMM profiles.

```bash
jackhmmer -N 5 -o results.txt --tblout hits.tbl query.fasta database.fasta
jackhmmer -N 5 -A iterations.sto --chkhmm checkpoint query.fasta database.fasta
```

## OrthoFinder for Multi-Species Orthologs

```bash
orthofinder -f proteomes/ -t 8
orthofinder -f proteomes/ -t 8 -M msa
```

### Prepare Input

```bash
mkdir proteomes
cp species_*.fasta proteomes/
```

### Output Files

| File | Content |
|------|---------|
| Orthogroups.tsv | All orthogroups |
| Orthogroups_SingleCopyOrthologues.txt | 1:1 orthologs |
| Species_Tree/ | Inferred species tree |
| Gene_Trees/ | Individual gene trees |

## E-value vs Bit Score

| E-value | Interpretation |
|---------|----------------|
| < 1e-50 | Highly significant, likely homolog |
| 1e-50 to 1e-10 | Significant, probable homolog |
| 1e-10 to 1e-3 | Marginal, possible remote homolog |
| > 0.01 | Not significant |

## Complete Ortholog Finding Pipeline

```bash
#!/bin/bash
SPECIES_A=$1
SPECIES_B=$2
EVALUE=1e-10
THREADS=8

echo "Building databases..."
makeblastdb -in $SPECIES_A -dbtype prot -out db_A
makeblastdb -in $SPECIES_B -dbtype prot -out db_B

echo "Running forward BLAST..."
blastp -query $SPECIES_A -db db_B -outfmt 6 -evalue $EVALUE \
    -max_target_seqs 1 -num_threads $THREADS > forward.txt

echo "Running reverse BLAST..."
blastp -query $SPECIES_B -db db_A -outfmt 6 -evalue $EVALUE \
    -max_target_seqs 1 -num_threads $THREADS > reverse.txt

echo "Finding reciprocal best hits..."
awk 'FNR==NR {best[$1]=$2; next}
     $2 in best && best[$2]==$1 {print $1"\t"$2}' \
     forward.txt reverse.txt > orthologs.txt

echo "Found $(wc -l < orthologs.txt) ortholog pairs"

rm -f db_A.* db_B.*
```

## Related Skills

- blast-searches - Basic remote BLAST
- local-blast - Local BLAST databases
- entrez-fetch - Download sequences
- alignment - Align identified homologs
