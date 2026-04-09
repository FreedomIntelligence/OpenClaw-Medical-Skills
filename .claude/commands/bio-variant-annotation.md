# bio-variant-annotation

> Comprehensive variant annotation using bcftools annotate/csq, VEP, SnpEff, and ANNOVAR. Add database annotations, predict functional consequences, and assess clinical significance. Use when annotating variants with functional and clinical information.

## Version Compatibility

Reference examples tested with: bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Variant Annotation

## Tool Comparison

| Tool | Best For | Speed | Output |
|------|----------|-------|--------|
| bcftools csq | Simple consequence prediction | Fast | VCF |
| VEP | Comprehensive with plugins | Moderate | VCF/TXT |
| SnpEff | Fast batch annotation | Fast | VCF |
| ANNOVAR | Flexible databases | Moderate | TXT |

## bcftools annotate

**Goal:** Add or remove INFO/ID annotations from external databases using bcftools.

**Approach:** Match variants by position and allele against annotation VCF/BED/TAB files, copying specified columns.

**"Add rsIDs to my VCF from dbSNP"** → Match variant positions against a database and copy identifiers or annotation fields into the VCF.

### Add Annotations from Database

```bash
bcftools annotate -a dbsnp.vcf.gz -c ID input.vcf.gz -Oz -o annotated.vcf.gz
```

### Annotation Columns (`-c`)

| Option | Description |
|--------|-------------|
| `ID` | Copy ID column |
| `INFO` | Copy all INFO fields |
| `INFO/TAG` | Copy specific INFO field |
| `+INFO/TAG` | Add to existing values |

### Add rsIDs from dbSNP

```bash
bcftools annotate -a dbsnp.vcf.gz -c ID input.vcf.gz -Oz -o with_rsids.vcf.gz
```

### Add Multiple Annotations

```bash
bcftools annotate -a database.vcf.gz -c ID,INFO/AF,INFO/CAF input.vcf.gz -Oz -o annotated.vcf.gz
```

### Add from BED/TAB Files

```bash
# BED with 4th column as annotation
bcftools annotate -a regions.bed.gz -c CHROM,FROM,TO,INFO/REGION \
    -h <(echo '##INFO=<ID=REGION,Number=1,Type=String,Description="Region name">') \
    input.vcf.gz -Oz -o annotated.vcf.gz

# Tab file: CHROM POS VALUE
bcftools annotate -a annotations.tab.gz -c CHROM,POS,INFO/SCORE \
    -h <(echo '##INFO=<ID=SCORE,Number=1,Type=Float,Description="Custom score">') \
    input.vcf.gz -Oz -o annotated.vcf.gz
```

### Remove Annotations

```bash
bcftools annotate -x INFO/DP,INFO/MQ input.vcf.gz -Oz -o clean.vcf.gz
bcftools annotate -x INFO input.vcf.gz -Oz -o minimal.vcf.gz  # Remove all INFO
```

### Set ID from Fields

```bash
bcftools annotate --set-id '%CHROM\_%POS\_%REF\_%ALT' input.vcf.gz -Oz -o with_ids.vcf.gz
```

## bcftools csq

**Goal:** Predict functional consequences of variants using gene annotations.

**Approach:** Map variants to GFF3 gene models and classify as synonymous, missense, frameshift, etc.

Simple consequence prediction using GFF annotation.

```bash
bcftools csq -f reference.fa -g genes.gff3.gz input.vcf.gz -Oz -o consequences.vcf.gz
```

### Consequence Types

| Consequence | Description |
|-------------|-------------|
| `synonymous` | No amino acid change |
| `missense` | Amino acid change |
| `stop_gained` | Introduces stop codon |
| `frameshift` | Changes reading frame |
| `splice_donor/acceptor` | Affects splicing |

## Ensembl VEP

**Goal:** Annotate variants comprehensively with consequence, impact, pathogenicity scores, and population frequencies.

**Approach:** Run VEP with offline cache, enabling SIFT, PolyPhen, HGVS, frequency, and plugin-based predictions.

**"Annotate my variants with functional consequences"** → Predict coding effects, impact severity, and pathogenicity using Ensembl's Variant Effect Predictor.

### Installation

```bash
conda install -c bioconda ensembl-vep
vep_install -a cf -s homo_sapiens -y GRCh38 --CONVERT
```

### Basic Annotation

```bash
vep -i input.vcf -o output.vcf --vcf --cache --offline
```

### Comprehensive Annotation

```bash
vep -i input.vcf -o output.vcf \
    --vcf \
    --cache --offline \
    --species homo_sapiens \
    --assembly GRCh38 \
    --everything \
    --fork 4
```

### --everything Enables

- `--sift b` - SIFT predictions
- `--polyphen b` - PolyPhen predictions
- `--hgvs` - HGVS nomenclature
- `--symbol` - Gene symbols
- `--canonical` - Canonical transcript
- `--af` - 1000 Genomes frequencies
- `--af_gnomade/g` - gnomAD frequencies
- `--pubmed` - PubMed IDs

### Filter by Impact

```bash
vep -i input.vcf -o output.vcf --vcf \
    --cache --offline \
    --pick \
    --filter "IMPACT in HIGH,MODERATE"
```

### Plugins

```bash
# CADD scores
vep -i input.vcf -o output.vcf --vcf \
    --cache --offline \
    --plugin CADD,whole_genome_SNVs.tsv.gz

# dbNSFP (multiple predictors)
vep -i input.vcf -o output.vcf --vcf \
    --cache --offline \
    --plugin dbNSFP,dbNSFP4.3a.gz,ALL

# Multiple plugins
vep -i input.vcf -o output.vcf --vcf \
    --cache --offline \
    --plugin CADD,cadd.tsv.gz \
    --plugin dbNSFP,dbnsfp.gz,SIFT_score,Polyphen2_HDIV_score \
    --plugin SpliceAI,spliceai.vcf.gz
```

### VEP Output Fields

| Field | Description |
|-------|-------------|
| Consequence | SO term (e.g., missense_variant) |
| IMPACT | HIGH, MODERATE, LOW, MODIFIER |
| SYMBOL | Gene symbol |
| HGVSc/HGVSp | HGVS coding/protein change |
| SIFT/PolyPhen | Pathogenicity predictions |

## SnpEff

**Goal:** Annotate variants with gene effects and impact categories using SnpEff.

**Approach:** Run SnpEff ann against a genome database, then use SnpSift for database cross-referencing and filtering.

### Installation

```bash
conda install -c bioconda snpeff
snpEff download GRCh38.105
```

### Basic Annotation

```bash
snpEff ann GRCh38.105 input.vcf > output.vcf
```

### With Statistics

```bash
snpEff ann -v -stats stats.html -csvStats stats.csv GRCh38.105 input.vcf > output.vcf
```

### Filter by Impact

```bash
snpEff ann GRCh38.105 input.vcf | \
    SnpSift filter "(ANN[*].IMPACT = 'HIGH')" > high_impact.vcf
```

### SnpEff Impact Categories

| Impact | Examples |
|--------|----------|
| HIGH | Stop gained, frameshift, splice donor/acceptor |
| MODERATE | Missense, inframe indel |
| LOW | Synonymous, splice region |
| MODIFIER | Intron, intergenic, UTR |

### SnpSift Database Annotations

```bash
# dbSNP
SnpSift annotate dbsnp.vcf.gz input.vcf > annotated.vcf

# ClinVar
SnpSift annotate clinvar.vcf.gz input.vcf > annotated.vcf

# dbNSFP
SnpSift dbnsfp -db dbNSFP4.3a.txt.gz input.vcf > annotated.vcf

# Chain multiple
snpEff ann GRCh38.105 input.vcf | \
    SnpSift annotate dbsnp.vcf.gz | \
    SnpSift annotate clinvar.vcf.gz > fully_annotated.vcf
```

### SnpSift Filtering

```bash
SnpSift filter "(QUAL >= 30) & (DP >= 10)" input.vcf > filtered.vcf
SnpSift filter "(exists CLNSIG) & (CLNSIG has 'Pathogenic')" input.vcf > pathogenic.vcf
```

## ANNOVAR

**Goal:** Annotate variants with gene, frequency, and pathogenicity databases using ANNOVAR.

**Approach:** Run table_annovar.pl with multiple protocols (gene, filter, region) against downloaded annotation databases.

### Installation

```bash
# Download from https://annovar.openbioinformatics.org/ (registration required)
annotate_variation.pl -buildver hg38 -downdb -webfrom annovar refGene humandb/
annotate_variation.pl -buildver hg38 -downdb -webfrom annovar gnomad30_genome humandb/
```

### Table Annotation

```bash
table_annovar.pl input.vcf humandb/ \
    -buildver hg38 \
    -out annotated \
    -remove \
    -protocol refGene,gnomad30_genome,clinvar_20230416,dbnsfp42a \
    -operation g,f,f,f \
    -nastring . \
    -vcfinput
```

## Python: Parse Annotated VCF

**Goal:** Extract and interpret annotation fields from VEP CSQ or SnpEff ANN strings in Python.

**Approach:** Parse pipe-delimited annotation strings against the header-defined field order, then filter by impact or consequence.

### Parse VEP CSQ

```python
from cyvcf2 import VCF

def parse_vep_csq(csq_string, csq_header):
    fields = csq_header.split('|')
    values = csq_string.split('|')
    return dict(zip(fields, values))

vcf = VCF('vep_output.vcf')
csq_header = None
for h in vcf.header_iter():
    if h['HeaderType'] == 'INFO' and h['ID'] == 'CSQ':
        csq_header = h['Description'].split('Format: ')[1].rstrip('"')
        break

for variant in vcf:
    csq = variant.INFO.get('CSQ')
    if csq:
        for transcript in csq.split(','):
            parsed = parse_vep_csq(transcript, csq_header)
            if parsed.get('IMPACT') in ('HIGH', 'MODERATE'):
                print(f"{variant.CHROM}:{variant.POS} {parsed['SYMBOL']} {parsed['Consequence']}")
```

### Parse SnpEff ANN

```python
from cyvcf2 import VCF

def parse_snpeff_ann(ann_string):
    fields = ['Allele', 'Annotation', 'Impact', 'Gene_Name', 'Gene_ID',
              'Feature_Type', 'Feature_ID', 'Transcript_BioType', 'Rank',
              'HGVS_c', 'HGVS_p', 'cDNA_pos', 'CDS_pos', 'Protein_pos', 'Distance']
    values = ann_string.split('|')
    return dict(zip(fields, values[:len(fields)]))

for variant in VCF('snpeff_output.vcf'):
    ann = variant.INFO.get('ANN')
    if ann:
        for transcript in ann.split(','):
            parsed = parse_snpeff_ann(transcript)
            if parsed['Impact'] == 'HIGH':
                print(f"{variant.CHROM}:{variant.POS} {parsed['Gene_Name']} {parsed['Annotation']}")
```

## Complete Annotation Pipeline

**Goal:** Run a full annotation workflow from normalization through VEP annotation to impact filtering.

**Approach:** Normalize variants, annotate with VEP (--everything --pick), then filter for HIGH/MODERATE impact.

```bash
#!/bin/bash
set -euo pipefail

INPUT=$1
REFERENCE=$2
VEP_CACHE=$3
OUTPUT_PREFIX=$4

# Normalize variants
bcftools norm -f $REFERENCE -m-any $INPUT -Oz -o ${OUTPUT_PREFIX}_norm.vcf.gz
bcftools index ${OUTPUT_PREFIX}_norm.vcf.gz

# VEP annotation
vep -i ${OUTPUT_PREFIX}_norm.vcf.gz \
    -o ${OUTPUT_PREFIX}_vep.vcf \
    --vcf --cache --offline --dir_cache $VEP_CACHE \
    --assembly GRCh38 --everything --pick --fork 4

bgzip ${OUTPUT_PREFIX}_vep.vcf
bcftools index ${OUTPUT_PREFIX}_vep.vcf.gz

# Filter high/moderate impact
bcftools view -i 'INFO/CSQ~"HIGH" || INFO/CSQ~"MODERATE"' \
    ${OUTPUT_PREFIX}_vep.vcf.gz -Oz -o ${OUTPUT_PREFIX}_filtered.vcf.gz
```

## Pathogenicity Predictors

| Predictor | Deleterious | Benign |
|-----------|-------------|--------|
| SIFT | < 0.05 | >= 0.05 |
| PolyPhen-2 (HDIV) | > 0.957 (probably), > 0.453 (possibly) | <= 0.453 |
| CADD | > 20 (top 1%), > 30 (top 0.1%) | < 10 |
| REVEL | > 0.5 | < 0.5 |

## Clinical Significance (ClinVar)

| Code | Meaning |
|------|---------|
| Pathogenic | Disease-causing |
| Likely_pathogenic | Probably disease-causing |
| Uncertain_significance | VUS |
| Likely_benign | Probably not disease-causing |
| Benign | Not disease-causing |

## Quick Reference

| Task | Command |
|------|---------|
| Add rsIDs | `bcftools annotate -a dbsnp.vcf.gz -c ID in.vcf.gz` |
| VEP annotation | `vep -i in.vcf -o out.vcf --vcf --cache --everything` |
| SnpEff annotation | `snpEff ann GRCh38.105 in.vcf > out.vcf` |
| Consequences only | `bcftools csq -f ref.fa -g genes.gff in.vcf.gz` |

## Related Skills

- variant-calling/variant-normalization - Normalize before annotating
- variant-calling/filtering-best-practices - Filter by annotations
- variant-calling/vcf-basics - Query annotated fields
- database-access/entrez-fetch - Download annotation databases
