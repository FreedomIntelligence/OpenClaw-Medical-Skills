# bio-variant-calling-clinical-interpretation

> Clinical variant interpretation using ClinVar, ACMG guidelines, and pathogenicity predictors. Prioritize variants for diagnostic and research applications. Use when interpreting clinical significance of variants.

## Version Compatibility

Reference examples tested with: Entrez Direct 21.0+, bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Clinical Variant Interpretation

Prioritize and interpret variants for clinical significance using databases and ACMG/AMP guidelines.

## Interpretation Framework

```
Annotated VCF
    │
    ├── Database Lookup
    │   ├── ClinVar (clinical assertions)
    │   ├── OMIM (disease associations)
    │   └── gnomAD (population frequency)
    │
    ├── Computational Predictions
    │   ├── SIFT, PolyPhen-2
    │   ├── CADD, REVEL
    │   └── SpliceAI
    │
    ├── ACMG Classification
    │   └── Pathogenic → Likely Pathogenic → VUS → Likely Benign → Benign
    │
    └── Prioritized Variant List
```

## ClinVar Annotation

**Goal:** Annotate variants with ClinVar clinical significance and filter by pathogenicity.

**Approach:** Download the ClinVar VCF, add CLNSIG/CLNDN/CLNREVSTAT fields with bcftools annotate, then filter by significance level.

**"Find pathogenic variants in my VCF"** → Cross-reference variants against ClinVar clinical assertions and extract those classified as pathogenic or likely pathogenic.

### Download ClinVar

```bash
wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.tbi
```

### Annotate with bcftools

```bash
bcftools annotate \
    -a clinvar.vcf.gz \
    -c INFO/CLNSIG,INFO/CLNDN,INFO/CLNREVSTAT \
    input.vcf.gz -Oz -o with_clinvar.vcf.gz
```

### Filter Pathogenic Variants

```bash
# Pathogenic or Likely pathogenic
bcftools view -i 'INFO/CLNSIG~"Pathogenic" || INFO/CLNSIG~"Likely_pathogenic"' \
    with_clinvar.vcf.gz -Oz -o pathogenic.vcf.gz

# Exclude benign
bcftools view -e 'INFO/CLNSIG~"Benign" || INFO/CLNSIG~"Likely_benign"' \
    with_clinvar.vcf.gz -Oz -o not_benign.vcf.gz
```

## ClinVar Significance Levels

| CLNSIG | Meaning | Action |
|--------|---------|--------|
| Pathogenic | Disease-causing | Report |
| Likely_pathogenic | Probably disease-causing | Report with caveat |
| Uncertain_significance | VUS | May report, needs follow-up |
| Likely_benign | Probably not disease-causing | Usually exclude |
| Benign | Not disease-causing | Exclude |
| Conflicting | Multiple interpretations | Manual review |

## ClinVar Review Status

| CLNREVSTAT | Stars | Meaning |
|------------|-------|---------|
| practice_guideline | 4 | Expert panel reviewed |
| reviewed_by_expert_panel | 3 | ClinGen expert reviewed |
| criteria_provided,_multiple_submitters | 2 | Consistent assertions |
| criteria_provided,_single_submitter | 1 | One submitter with criteria |
| no_assertion_criteria | 0 | No criteria provided |

```bash
# Filter for high-confidence assertions (2+ stars)
bcftools view -i 'INFO/CLNREVSTAT~"multiple_submitters" || \
    INFO/CLNREVSTAT~"expert_panel" || \
    INFO/CLNREVSTAT~"practice_guideline"' \
    with_clinvar.vcf.gz -Oz -o high_confidence.vcf.gz
```

## InterVar (ACMG Classification)

**Goal:** Classify variants according to ACMG/AMP guidelines using automated criteria evaluation.

**Approach:** Convert VCF to ANNOVAR format, run InterVar to evaluate 28 ACMG criteria, and output five-tier classification.

Automated ACMG/AMP variant classification.

### Installation

```bash
git clone https://github.com/WGLab/InterVar.git
cd InterVar
# Download databases per documentation
```

### Run InterVar

```bash
python Intervar.py \
    -i input.avinput \
    -o output \
    -b hg38 \
    -d humandb/ \
    --input_type=AVinput
```

### From VCF

```bash
# Convert VCF to ANNOVAR format
convert2annovar.pl -format vcf4 input.vcf > input.avinput

# Run InterVar
python Intervar.py -i input.avinput -o intervar_results -b hg38
```

## ACMG/AMP Criteria

### Pathogenic Criteria

| Code | Type | Description |
|------|------|-------------|
| PVS1 | Very Strong | Null variant in gene where LOF is disease mechanism |
| PS1-4 | Strong | Same AA change, functional studies, etc. |
| PM1-6 | Moderate | Hot spot, absent from controls, etc. |
| PP1-5 | Supporting | Co-segregation, computational evidence |

### Benign Criteria

| Code | Type | Description |
|------|------|-------------|
| BA1 | Stand-alone | AF >5% in gnomAD |
| BS1-4 | Strong | AF greater than expected, functional studies |
| BP1-7 | Supporting | Missense in gene with truncating mechanism |

## Population Frequency Filtering

**Goal:** Restrict to rare variants that could be disease-causing.

**Approach:** Filter by gnomAD allele frequency threshold appropriate for the disease model (dominant vs. recessive).

```bash
# Rare variants only (gnomAD AF < 0.01)
bcftools view -i 'INFO/gnomAD_AF<0.01 || INFO/gnomAD_AF="."' \
    input.vcf.gz -Oz -o rare.vcf.gz

# Ultra-rare for dominant diseases (AF < 0.0001)
bcftools view -i 'INFO/gnomAD_AF<0.0001 || INFO/gnomAD_AF="."' \
    input.vcf.gz -Oz -o ultrarare.vcf.gz
```

## Pathogenicity Score Filtering

**Goal:** Prioritize variants using computational pathogenicity predictors.

**Approach:** Filter by CADD PHRED score (deleteriousness) and REVEL score (missense pathogenicity), alone or in combination with ClinVar.

### CADD Scores

```bash
# CADD > 20 (top 1% deleterious)
bcftools view -i 'INFO/CADD_PHRED>20' input.vcf.gz -Oz -o cadd_filtered.vcf.gz

# CADD > 30 (top 0.1%)
bcftools view -i 'INFO/CADD_PHRED>30' input.vcf.gz -Oz -o highly_deleterious.vcf.gz
```

### REVEL Scores

```bash
# REVEL > 0.5 (likely pathogenic)
bcftools view -i 'INFO/REVEL>0.5' input.vcf.gz -Oz -o revel_filtered.vcf.gz
```

### Combined Filtering

```bash
bcftools view -i '(INFO/CADD_PHRED>20 || INFO/REVEL>0.5) && \
    (INFO/CLNSIG~"Pathogenic" || INFO/CLNSIG~"Likely" || INFO/CLNSIG=".")' \
    input.vcf.gz -Oz -o prioritized.vcf.gz
```

## Python: Clinical Prioritization

**Goal:** Implement a multi-criteria variant classification pipeline in Python.

**Approach:** Combine ClinVar lookups, population frequency, and computational scores (CADD, REVEL) into a tiered classification function.

```python
from cyvcf2 import VCF, Writer

def classify_variant(variant):
    clnsig = variant.INFO.get('CLNSIG', '')
    af = variant.INFO.get('gnomAD_AF', 0) or 0
    cadd = variant.INFO.get('CADD_PHRED', 0) or 0
    revel = variant.INFO.get('REVEL', 0) or 0

    # Known pathogenic
    if 'Pathogenic' in str(clnsig):
        return 'PATHOGENIC'
    if 'Likely_pathogenic' in str(clnsig):
        return 'LIKELY_PATHOGENIC'

    # Known benign
    if 'Benign' in str(clnsig) or af > 0.05:
        return 'BENIGN'

    # Computational prediction
    if cadd > 25 or revel > 0.7:
        if af < 0.0001:
            return 'LIKELY_PATHOGENIC'
        elif af < 0.01:
            return 'VUS_FAVOR_PATH'

    if cadd < 10 and revel < 0.3:
        return 'LIKELY_BENIGN'

    return 'VUS'

vcf = VCF('annotated.vcf.gz')
results = []

for variant in vcf:
    classification = classify_variant(variant)
    if classification in ('PATHOGENIC', 'LIKELY_PATHOGENIC', 'VUS_FAVOR_PATH'):
        gene = variant.INFO.get('SYMBOL', 'Unknown')
        consequence = variant.INFO.get('Consequence', 'Unknown')
        results.append({
            'chrom': variant.CHROM,
            'pos': variant.POS,
            'ref': variant.REF,
            'alt': variant.ALT[0],
            'gene': gene,
            'consequence': consequence,
            'classification': classification,
            'clnsig': variant.INFO.get('CLNSIG', '.'),
            'cadd': variant.INFO.get('CADD_PHRED', '.'),
            'af': variant.INFO.get('gnomAD_AF', '.')
        })

# Output prioritized variants
for r in results:
    print(f"{r['gene']}\t{r['chrom']}:{r['pos']}\t{r['consequence']}\t{r['classification']}")
```

## Gene Panel Filtering

**Goal:** Restrict analysis to variants within a clinical gene panel.

**Approach:** Filter by BED coordinates or VEP gene symbol annotations to target specific genes.

```bash
# Filter to gene panel
bcftools view -R gene_panel.bed input.vcf.gz -Oz -o panel_variants.vcf.gz

# Or by gene symbol (requires VEP annotation)
bcftools view -i 'INFO/CSQ~"BRCA1" || INFO/CSQ~"BRCA2"' \
    input.vcf.gz -Oz -o brca_variants.vcf.gz
```

## Disease-Specific Resources

| Resource | Content | Use |
|----------|---------|-----|
| ClinVar | Clinical assertions | Primary lookup |
| OMIM | Gene-disease relationships | Gene prioritization |
| HGMD | Published mutations | Literature evidence |
| gnomAD | Population frequencies | Rarity filtering |
| ClinGen | Gene validity/dosage | LOF interpretation |

## Reporting Template

```bash
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%INFO/SYMBOL\t%INFO/Consequence\t\
%INFO/CLNSIG\t%INFO/CLNDN\t%INFO/gnomAD_AF\t%INFO/CADD_PHRED\n' \
    prioritized.vcf.gz > clinical_report.tsv
```

## Complete Workflow

**Goal:** Run an end-to-end clinical variant interpretation pipeline from annotation through reporting.

**Approach:** Chain ClinVar annotation, rare variant filtering, pathogenicity extraction, VUS review, and TSV report generation.

```bash
#!/bin/bash
set -euo pipefail

INPUT=$1
CLINVAR=$2
OUTPUT_PREFIX=$3

echo "=== Add ClinVar annotations ==="
bcftools annotate -a $CLINVAR \
    -c INFO/CLNSIG,INFO/CLNDN,INFO/CLNREVSTAT,INFO/CLNVC \
    $INPUT -Oz -o ${OUTPUT_PREFIX}_clinvar.vcf.gz

echo "=== Filter rare variants ==="
bcftools view -i 'INFO/gnomAD_AF<0.01 || INFO/gnomAD_AF="."' \
    ${OUTPUT_PREFIX}_clinvar.vcf.gz -Oz -o ${OUTPUT_PREFIX}_rare.vcf.gz

echo "=== Extract pathogenic/likely pathogenic ==="
bcftools view -i 'INFO/CLNSIG~"athogenic"' \
    ${OUTPUT_PREFIX}_rare.vcf.gz -Oz -o ${OUTPUT_PREFIX}_pathogenic.vcf.gz

echo "=== Extract high-impact VUS ==="
bcftools view -i 'INFO/CLNSIG~"Uncertain" && INFO/CADD_PHRED>20' \
    ${OUTPUT_PREFIX}_rare.vcf.gz -Oz -o ${OUTPUT_PREFIX}_vus_review.vcf.gz

echo "=== Generate report ==="
bcftools query -H -f '%CHROM\t%POS\t%REF\t%ALT\t%INFO/SYMBOL\t%INFO/Consequence\t\
%INFO/CLNSIG\t%INFO/CLNDN\t%INFO/gnomAD_AF\t%INFO/CADD_PHRED\n' \
    ${OUTPUT_PREFIX}_pathogenic.vcf.gz > ${OUTPUT_PREFIX}_report.tsv

echo "=== Complete ==="
echo "Pathogenic: ${OUTPUT_PREFIX}_pathogenic.vcf.gz"
echo "VUS for review: ${OUTPUT_PREFIX}_vus_review.vcf.gz"
echo "Report: ${OUTPUT_PREFIX}_report.tsv"
```

## Related Skills

- variant-calling/variant-annotation - VEP/SnpEff annotation
- variant-calling/filtering-best-practices - Quality filtering
- database-access/entrez-fetch - Download ClinVar/OMIM data
- pathway-analysis/go-enrichment - Gene set analysis
