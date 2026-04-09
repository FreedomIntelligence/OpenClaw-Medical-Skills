# bio-genome-intervals-gtf-gff-handling

> Parse, query, and convert GTF and GFF3 annotation files. Extract gene, transcript, and exon coordinates using gffread, gtfparse, and gffutils. Use when extracting specific features from gene annotations or converting between annotation formats.

**Available tools:** Read, Bash

# GTF/GFF Handling

GTF and GFF3 are standard gene annotation formats. Both use 1-based coordinates.

## Format Comparison

| Feature | GTF | GFF3 |
|---------|-----|------|
| Coordinate system | 1-based, inclusive | 1-based, inclusive |
| Hierarchy | Implicit (gene_id, transcript_id) | Explicit (Parent attribute) |
| Attribute format | key "value"; | key=value; |
| Comments | # | # |
| Fasta sequences | Not standard | ##FASTA directive |

## GTF Format

```
chr1	HAVANA	gene	11869	14409	.	+	.	gene_id "ENSG00000223972"; gene_name "DDX11L1";
chr1	HAVANA	transcript	11869	14409	.	+	.	gene_id "ENSG00000223972"; transcript_id "ENST00000456328";
chr1	HAVANA	exon	11869	12227	.	+	.	gene_id "ENSG00000223972"; transcript_id "ENST00000456328"; exon_number "1";
```

## GFF3 Format

```
chr1	HAVANA	gene	11869	14409	.	+	.	ID=ENSG00000223972;Name=DDX11L1
chr1	HAVANA	mRNA	11869	14409	.	+	.	ID=ENST00000456328;Parent=ENSG00000223972
chr1	HAVANA	exon	11869	12227	.	+	.	ID=exon1;Parent=ENST00000456328
```

## Parse GTF with gtfparse (Python)

### Installation

```bash
pip install gtfparse
```

### Basic Parsing

```python
import gtfparse

# Load entire GTF
df = gtfparse.read_gtf('annotation.gtf')

# View columns
print(df.columns)
# ['seqname', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame',
#  'gene_id', 'transcript_id', 'gene_name', ...]

# Filter by feature type
genes = df[df['feature'] == 'gene']
transcripts = df[df['feature'] == 'transcript']
exons = df[df['feature'] == 'exon']

# Get specific gene
gene_df = df[df['gene_name'] == 'TP53']
```

### Extract Gene Coordinates

```python
import gtfparse

df = gtfparse.read_gtf('annotation.gtf')

# All genes
genes = df[df['feature'] == 'gene'][['seqname', 'start', 'end', 'strand', 'gene_id', 'gene_name']]

# Convert to BED format (0-based)
genes_bed = genes.copy()
genes_bed['start'] = genes_bed['start'] - 1  # GTF is 1-based, BED is 0-based
genes_bed = genes_bed[['seqname', 'start', 'end', 'gene_name', 'gene_id', 'strand']]
genes_bed.to_csv('genes.bed', sep='\t', header=False, index=False)
```

### Get Exons for Gene

```python
import gtfparse

df = gtfparse.read_gtf('annotation.gtf')

# Get all exons for TP53
tp53_exons = df[(df['gene_name'] == 'TP53') & (df['feature'] == 'exon')]
tp53_exons = tp53_exons[['seqname', 'start', 'end', 'transcript_id', 'exon_number']]
print(tp53_exons)
```

## Parse GFF with gffutils (Python)

### Installation

```bash
pip install gffutils
```

### Create Database

```python
import gffutils

# Create database (slow first time, fast for subsequent queries)
db = gffutils.create_db('annotation.gff3', 'annotation.db',
                         force=True, merge_strategy='create_unique')

# Or load existing database
db = gffutils.FeatureDB('annotation.db')
```

### Query Features

```python
import gffutils

db = gffutils.FeatureDB('annotation.db')

# Count features by type
for featuretype in db.featuretypes():
    count = db.count_features_of_type(featuretype)
    print(f'{featuretype}: {count}')

# Get all genes
for gene in db.features_of_type('gene'):
    print(f'{gene.id}: {gene.seqid}:{gene.start}-{gene.end}')

# Get gene by ID
gene = db['ENSG00000141510']  # TP53
print(f'{gene.attributes["Name"][0]}: {gene.seqid}:{gene.start}-{gene.end}')

# Get children (transcripts, exons)
for transcript in db.children(gene, featuretype='mRNA'):
    print(f'  Transcript: {transcript.id}')
    for exon in db.children(transcript, featuretype='exon'):
        print(f'    Exon: {exon.start}-{exon.end}')
```

### Get Introns

```python
import gffutils

db = gffutils.FeatureDB('annotation.db')

# Get introns for a transcript
transcript = db['ENST00000269305']
introns = list(db.interfeatures(db.children(transcript, featuretype='exon'),
                                 new_featuretype='intron'))
for intron in introns:
    print(f'Intron: {intron.start}-{intron.end}')
```

## Convert Formats with gffread (CLI)

### Installation

```bash
conda install -c bioconda gffread
```

### GTF to GFF3

```bash
gffread annotation.gtf -o annotation.gff3
```

### GFF3 to GTF

```bash
gffread annotation.gff3 -T -o annotation.gtf
```

### Extract Sequences

```bash
# Extract transcript sequences
gffread -w transcripts.fa -g genome.fa annotation.gtf

# Extract CDS sequences
gffread -x cds.fa -g genome.fa annotation.gtf

# Extract protein sequences
gffread -y proteins.fa -g genome.fa annotation.gtf
```

### Filter Features

```bash
# Keep only protein-coding genes
gffread annotation.gtf -C -o coding.gtf

# Keep specific gene types
gffread annotation.gtf --keep-genes=protein_coding -o coding.gtf
```

## Extract Regions with bedtools

### Get Promoters

```bash
# Extract TSS (transcript start sites)
awk '$3 == "transcript"' annotation.gtf | \
    awk -v OFS='\t' '{
        if ($7 == "+") print $1, $4-1, $4, ".", ".", $7;
        else print $1, $5-1, $5, ".", ".", $7;
    }' > tss.bed

# Get promoter regions (2kb upstream of TSS)
bedtools flank -i tss.bed -g genome.txt -l 2000 -r 0 -s > promoters.bed
```

### Get Gene Bodies

```bash
# Extract gene coordinates to BED
awk '$3 == "gene"' annotation.gtf | \
    awk -v OFS='\t' '{
        split($0, a, "gene_id \""); split(a[2], b, "\"");
        print $1, $4-1, $5, b[1], ".", $7;
    }' > genes.bed
```

### Get Exons

```bash
# Extract unique exons
awk '$3 == "exon"' annotation.gtf | \
    awk -v OFS='\t' '{print $1, $4-1, $5, ".", ".", $7}' | \
    sort -k1,1 -k2,2n | uniq > exons.bed
```

## Python: GTF to BED Conversion

```python
import gtfparse
import pandas as pd

def gtf_to_bed(gtf_path, feature_type='gene', output_path=None):
    '''Convert GTF features to BED format.'''
    df = gtfparse.read_gtf(gtf_path)
    features = df[df['feature'] == feature_type].copy()

    # Convert to 0-based coordinates
    bed = pd.DataFrame({
        'chrom': features['seqname'],
        'start': features['start'] - 1,
        'end': features['end'],
        'name': features.get('gene_name', features.get('gene_id', '.')),
        'score': 0,
        'strand': features['strand']
    })

    if output_path:
        bed.to_csv(output_path, sep='\t', header=False, index=False)
    return bed

# Usage
genes_bed = gtf_to_bed('annotation.gtf', 'gene', 'genes.bed')
exons_bed = gtf_to_bed('annotation.gtf', 'exon', 'exons.bed')
```

## Validate GTF/GFF

```bash
# Check GTF format
gffread -E annotation.gtf

# Check GFF3 format
gffread -E annotation.gff3

# Detailed validation
gt gff3validator annotation.gff3  # requires genometools
```

## Common Attributes

### GTF Attributes

| Attribute | Description |
|-----------|-------------|
| gene_id | Ensembl gene ID |
| gene_name | Gene symbol |
| gene_biotype | protein_coding, lncRNA, etc. |
| transcript_id | Ensembl transcript ID |
| transcript_name | Transcript symbol |
| exon_number | Exon position in transcript |
| exon_id | Ensembl exon ID |

### GFF3 Attributes

| Attribute | Description |
|-----------|-------------|
| ID | Unique feature identifier |
| Name | Display name |
| Parent | Parent feature ID |
| Dbxref | Database cross-references |
| gene_biotype | Gene type |

## Memory-Efficient Processing

```python
import gtfparse

# Process large files in chunks (gtfparse loads all into memory)
# For very large files, use gffutils database approach

# Or filter during parsing
df = gtfparse.read_gtf('annotation.gtf',
                        features=['gene', 'exon'])  # Only load specific features
```

## Related Skills

- bed-file-basics - BED format and conversion
- interval-arithmetic - Gene/exon overlap analysis
- proximity-operations - TSS proximity analysis
- differential-expression/de-results - Gene coordinate mapping
