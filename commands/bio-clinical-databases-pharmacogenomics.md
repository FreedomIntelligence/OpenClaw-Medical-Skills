# bio-clinical-databases-pharmacogenomics

> Query PharmGKB and CPIC for drug-gene interactions, pharmacogenomic annotations, and dosing guidelines. Use when predicting drug response from genetic variants or implementing clinical pharmacogenomics.

## Version Compatibility

Reference examples tested with: pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Pharmacogenomics

## PharmGKB REST API

**Goal:** Retrieve drug-gene clinical annotations and dosing guidelines from PharmGKB.

**Approach:** Query PharmGKB REST endpoints by gene symbol or drug name and parse JSON annotation records.

**"Find pharmacogenomic annotations for this gene"** → Query PharmGKB for clinical annotations linking genes to drug response.
- Python: `requests.get()` against PharmGKB API (requests)

### Query Drug-Gene Relationships

```python
import requests

def get_pharmgkb_annotations(gene_symbol):
    '''Get PharmGKB clinical annotations for a gene'''
    url = f'https://api.pharmgkb.org/v1/data/clinicalAnnotation'
    params = {'view': 'base', 'location.genes.symbol': gene_symbol}
    response = requests.get(url, params=params)
    return response.json()['data']

annotations = get_pharmgkb_annotations('CYP2D6')
for ann in annotations[:5]:
    print(f"{ann['location']['genes'][0]['symbol']}: {ann['chemicals'][0]['name']}")
```

### Query by Drug

```python
def get_drug_annotations(drug_name):
    '''Get pharmacogenomic annotations for a drug'''
    url = 'https://api.pharmgkb.org/v1/data/clinicalAnnotation'
    params = {'view': 'base', 'chemicals.name': drug_name}
    response = requests.get(url, params=params)
    return response.json()['data']

warfarin_annotations = get_drug_annotations('warfarin')
```

### Get Dosing Guidelines

```python
def get_cpic_guidelines(gene_symbol):
    '''Get CPIC dosing guidelines for a gene'''
    url = 'https://api.pharmgkb.org/v1/data/guideline'
    params = {'view': 'base', 'relatedGenes.symbol': gene_symbol, 'source': 'CPIC'}
    response = requests.get(url, params=params)
    return response.json()['data']

guidelines = get_cpic_guidelines('CYP2C19')
for g in guidelines:
    print(f"{g['name']}: {g['chemicals'][0]['name']}")
```

## Star Allele Interpretation

**Goal:** Determine metabolizer phenotype from CYP star allele diplotypes using CPIC activity scores.

**Approach:** Sum per-allele activity scores and classify into PM/IM/NM/UM categories based on CPIC thresholds.

### CYP2D6 Metabolizer Status

```python
# CYP2D6 activity scores for common alleles
# Based on CPIC guidelines
CYP2D6_ACTIVITY = {
    '*1': 1.0,   # Normal function
    '*2': 1.0,   # Normal function
    '*3': 0.0,   # No function
    '*4': 0.0,   # No function
    '*5': 0.0,   # Gene deletion
    '*6': 0.0,   # No function
    '*9': 0.5,   # Decreased function
    '*10': 0.25, # Decreased function (common in East Asian)
    '*17': 0.5,  # Decreased function
    '*41': 0.5,  # Decreased function
}

def calculate_activity_score(allele1, allele2):
    '''Calculate CYP2D6 activity score from diplotype'''
    score1 = CYP2D6_ACTIVITY.get(allele1, 1.0)
    score2 = CYP2D6_ACTIVITY.get(allele2, 1.0)
    return score1 + score2

def get_metabolizer_status(activity_score):
    '''Convert activity score to metabolizer phenotype

    CPIC thresholds:
    - PM: 0
    - IM: 0 < score <= 1.25
    - NM: 1.25 < score <= 2.25
    - UM: > 2.25 (gene duplications)
    '''
    if activity_score == 0:
        return 'Poor Metabolizer (PM)'
    elif activity_score <= 1.25:
        return 'Intermediate Metabolizer (IM)'
    elif activity_score <= 2.25:
        return 'Normal Metabolizer (NM)'
    else:
        return 'Ultrarapid Metabolizer (UM)'

score = calculate_activity_score('*1', '*4')
status = get_metabolizer_status(score)
print(f'Activity score: {score}, Status: {status}')
```

### CYP2C19 Interpretation

```python
CYP2C19_ACTIVITY = {
    '*1': 1.0,   # Normal function
    '*2': 0.0,   # No function (most common loss-of-function)
    '*3': 0.0,   # No function
    '*17': 1.5,  # Increased function
}

def cyp2c19_phenotype(allele1, allele2):
    '''Determine CYP2C19 metabolizer status'''
    score = CYP2C19_ACTIVITY.get(allele1, 1.0) + CYP2C19_ACTIVITY.get(allele2, 1.0)
    if score == 0:
        return 'Poor Metabolizer'
    elif score < 1.5:
        return 'Intermediate Metabolizer'
    elif score <= 2.0:
        return 'Normal Metabolizer'
    elif score <= 2.5:
        return 'Rapid Metabolizer'
    else:
        return 'Ultrarapid Metabolizer'
```

## Drug Interaction Lookup

**Goal:** Check whether a specific drug-gene-variant combination has a known pharmacogenomic interaction.

**Approach:** Query PharmGKB variant annotation endpoint filtered by drug and gene, then match to the target variant.

```python
def check_pgx_interaction(drug, gene, variant):
    '''Check for pharmacogenomic drug-gene-variant interaction'''
    url = 'https://api.pharmgkb.org/v1/data/variantAnnotation'
    params = {
        'chemicals.name': drug,
        'location.genes.symbol': gene
    }
    response = requests.get(url, params=params)
    annotations = response.json().get('data', [])

    for ann in annotations:
        if variant in str(ann.get('variant', {}).get('name', '')):
            return {
                'drug': drug,
                'gene': gene,
                'variant': variant,
                'phenotype': ann.get('phenotypes', []),
                'evidence': ann.get('evidenceLevel')
            }
    return None
```

## Common PGx Gene-Drug Pairs

| Gene | Drugs | Clinical Impact |
|------|-------|-----------------|
| CYP2D6 | Codeine, tamoxifen, ondansetron | Efficacy, toxicity |
| CYP2C19 | Clopidogrel, omeprazole, escitalopram | Efficacy, dosing |
| CYP2C9 | Warfarin, phenytoin, NSAIDs | Bleeding risk, dosing |
| VKORC1 | Warfarin | Dosing |
| TPMT | Azathioprine, mercaptopurine | Myelosuppression |
| DPYD | Fluorouracil, capecitabine | Severe toxicity |
| HLA-B*57:01 | Abacavir | Hypersensitivity |
| HLA-B*15:02 | Carbamazepine | SJS/TEN |
| SLCO1B1 | Simvastatin | Myopathy risk |
| UGT1A1 | Irinotecan | Neutropenia |

## Batch PGx Annotation

**Goal:** Annotate a cohort of variants across multiple pharmacogenes with drug interaction data.

**Approach:** Iterate over a list of pharmacogenes, fetch PharmGKB annotations for each, and collect results into a DataFrame.

```python
import pandas as pd

def annotate_pgx_variants(vcf_variants, pgx_genes):
    '''Annotate variants in pharmacogenes

    Args:
        vcf_variants: DataFrame with chrom, pos, ref, alt
        pgx_genes: List of pharmacogenes to check
    '''
    results = []
    for gene in pgx_genes:
        annotations = get_pharmgkb_annotations(gene)
        for ann in annotations:
            results.append({
                'gene': gene,
                'drug': ann['chemicals'][0]['name'] if ann.get('chemicals') else None,
                'phenotype': ann.get('phenotypes', []),
                'level': ann.get('levelOfEvidence')
            })
    return pd.DataFrame(results)

pgx_genes = ['CYP2D6', 'CYP2C19', 'CYP2C9', 'VKORC1', 'TPMT']
pgx_df = annotate_pgx_variants(vcf_df, pgx_genes)
```

## Related Skills

- clinical-databases/clinvar-lookup - Pathogenicity classification
- variant-calling/clinical-interpretation - ACMG guidelines
- clinical-databases/variant-prioritization - Clinical filtering
