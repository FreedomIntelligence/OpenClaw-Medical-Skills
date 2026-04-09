# bio-workflows-neoantigen-pipeline

> End-to-end neoantigen discovery from somatic variants to ranked vaccine candidates. Integrates HLA typing, MHC binding prediction, pVACtools neoantigen calling, and immunogenicity scoring. Use when identifying tumor neoantigens for personalized vaccine design or checkpoint biomarkers.

**Available tools:** Read, Bash

# Neoantigen Pipeline

Complete workflow from somatic variants to ranked neoantigen vaccine candidates for personalized cancer immunotherapy.

## Workflow Overview

```
Somatic VCF (annotated) + Tumor RNA-seq (optional)
        |
        v
[1. HLA Typing] --> arcasHLA / OptiType (if types not provided)
        |
        v
[2. MHC Binding Prediction] --> MHCflurry / NetMHCpan
        |
        v
[3. Neoantigen Calling] --> pVACseq
        |
        v
[4. Immunogenicity Scoring] --> Multi-factor ranking
        |
        v
Ranked Vaccine Candidates (TSV + visualizations)
```

## Prerequisites

```bash
pip install pvactools mhcflurry vatools

mhcflurry-downloads fetch

conda install -c bioconda vep arcashla optitype
```

## Primary Path: pVACseq Pipeline

### Step 1: HLA Typing (if not provided)

HLA types are critical for MHC binding prediction. If not already known from clinical testing:

```bash
# From tumor RNA-seq BAM
arcasHLA extract tumor.bam -t 8 -o hla_output/
arcasHLA genotype hla_output/tumor.extracted.1.fq.gz hla_output/tumor.extracted.2.fq.gz \
    -g A,B,C,DRB1,DQB1,DPB1 -t 8 -o hla_output/

# Parse results
cat hla_output/tumor.genotype.json
```

```python
import json

with open('hla_output/tumor.genotype.json') as f:
    hla_data = json.load(f)

hla_alleles = []
for gene, alleles in hla_data.items():
    for allele in alleles:
        hla_alleles.append(f'HLA-{allele}')

# Format for pVACseq: HLA-A*02:01,HLA-A*24:02,HLA-B*07:02,...
hla_string = ','.join(hla_alleles)
print(f'HLA alleles: {hla_string}')
```

### Step 2: VCF Annotation with VEP

pVACseq requires VEP-annotated VCF with specific fields:

```bash
# Annotate somatic VCF
vep --input_file somatic.vcf \
    --output_file somatic.vep.vcf \
    --format vcf --vcf --symbol --terms SO \
    --plugin Frameshift --plugin Wildtype \
    --offline --cache \
    --pick --fork 4

# Add expression data (optional but recommended)
vcf-expression-annotator somatic.vep.vcf \
    expression.tsv gene \
    -s tumor_sample \
    -o somatic.vep.expression.vcf
```

### Step 3: Run pVACseq

```bash
# Basic run with MHC Class I
pvacseq run \
    somatic.vep.vcf \
    tumor_sample \
    "HLA-A*02:01,HLA-A*24:02,HLA-B*07:02,HLA-B*44:02,HLA-C*07:02,HLA-C*05:01" \
    MHCflurry MHCnuggetsI NetMHCpan \
    pvacseq_output/ \
    -e1 8,9,10,11 \
    --iedb-install-directory /path/to/iedb \
    -t 8

# With expression filtering
pvacseq run \
    somatic.vep.expression.vcf \
    tumor_sample \
    "HLA-A*02:01,HLA-A*24:02,HLA-B*07:02,HLA-B*44:02" \
    MHCflurry NetMHCpan \
    pvacseq_output/ \
    -e1 8,9,10,11 \
    --tumor-purity 0.7 \
    --trna-vaf 0.1 \
    --expn-val 1 \
    -t 8
```

### Step 4: Filter and Rank Candidates

```python
import pandas as pd
import numpy as np

results = pd.read_csv('pvacseq_output/MHC_Class_I/tumor_sample.filtered.tsv', sep='\t')

# Binding affinity filter (IC50 <500nM considered strong binder)
# IC50 <500nM: strong binder; 500-5000nM: weak binder
strong_binders = results[results['Median MT IC50 Score'] < 500].copy()

# Differential agretopicity index (DAI): difference between MT and WT binding
# Higher DAI = more tumor-specific
strong_binders['DAI'] = strong_binders['Median WT IC50 Score'] - strong_binders['Median MT IC50 Score']

# Expression filter (if available)
if 'Gene Expression' in strong_binders.columns:
    # TPM >1 ensures detectable expression
    strong_binders = strong_binders[strong_binders['Gene Expression'] > 1]

# VAF filter: prioritize clonal mutations
# VAF >0.1 ensures mutation present in substantial tumor fraction
strong_binders = strong_binders[strong_binders['Tumor DNA VAF'] > 0.1]

# Multi-factor scoring
def immunogenicity_score(row):
    score = 0
    # Strong binding (IC50 <150nM is very strong)
    if row['Median MT IC50 Score'] < 150:
        score += 3
    elif row['Median MT IC50 Score'] < 500:
        score += 2

    # High DAI (tumor-specificity)
    if row['DAI'] > 1000:
        score += 2
    elif row['DAI'] > 500:
        score += 1

    # Clonal mutation (high VAF)
    if row['Tumor DNA VAF'] > 0.3:
        score += 2
    elif row['Tumor DNA VAF'] > 0.15:
        score += 1

    # Expressed (if available)
    if 'Gene Expression' in row.index and row['Gene Expression'] > 10:
        score += 1

    return score

strong_binders['Immunogenicity Score'] = strong_binders.apply(immunogenicity_score, axis=1)

# Rank by composite score
ranked = strong_binders.sort_values('Immunogenicity Score', ascending=False)

# Top candidates for vaccine
top_candidates = ranked.head(20)
top_candidates.to_csv('top_neoantigen_candidates.tsv', sep='\t', index=False)

print(f'Total strong binders: {len(strong_binders)}')
print(f'Top 20 candidates exported')
print(ranked[['Gene Name', 'MT Epitope Seq', 'HLA Allele', 'Median MT IC50 Score', 'DAI', 'Immunogenicity Score']].head(10))
```

### Step 5: MHC Class II Neoantigens (CD4+ T cell help)

```bash
pvacseq run \
    somatic.vep.vcf \
    tumor_sample \
    "DRB1*01:01,DRB1*07:01,DQB1*02:01,DQB1*03:01" \
    MHCnuggetsII NetMHCIIpan \
    pvacseq_class2_output/ \
    -e2 15 \
    --iedb-install-directory /path/to/iedb \
    -t 8
```

## Alternative: Standalone MHCflurry

For quick binding predictions without full pVACseq pipeline:

```python
from mhcflurry import Class1PresentationPredictor

predictor = Class1PresentationPredictor.load()

peptides = ['SIINFEKL', 'GILGFVFTL', 'NLVPMVATV']
alleles = ['HLA-A*02:01', 'HLA-B*07:02']

results = predictor.predict(peptides=peptides, alleles=alleles, verbose=0)
print(results[['peptide', 'allele', 'mhcflurry_presentation_score', 'mhcflurry_affinity']])
```

## Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# IC50 distribution
ax1 = axes[0]
ax1.hist(ranked['Median MT IC50 Score'], bins=50, edgecolor='black')
ax1.axvline(500, color='red', linestyle='--', label='500nM threshold')
ax1.set_xlabel('Median MT IC50 (nM)')
ax1.set_ylabel('Count')
ax1.set_title('Binding Affinity Distribution')
ax1.legend()

# DAI vs IC50
ax2 = axes[1]
scatter = ax2.scatter(ranked['Median MT IC50 Score'], ranked['DAI'],
                      c=ranked['Immunogenicity Score'], cmap='viridis', alpha=0.7)
ax2.set_xlabel('MT IC50 (nM)')
ax2.set_ylabel('Differential Agretopicity Index')
ax2.set_title('Tumor Specificity vs Binding')
plt.colorbar(scatter, ax=ax2, label='Immunogenicity Score')

# Top genes
ax3 = axes[2]
gene_counts = ranked['Gene Name'].value_counts().head(15)
gene_counts.plot(kind='barh', ax=ax3)
ax3.set_xlabel('Number of Neoantigens')
ax3.set_title('Top Genes with Neoantigens')

plt.tight_layout()
plt.savefig('neoantigen_summary.pdf')
```

## Parameter Recommendations

| Step | Parameter | Value | Rationale |
|------|-----------|-------|-----------|
| pVACseq | -e1 | 8,9,10,11 | MHC-I binds 8-11mer peptides |
| pVACseq | -e2 | 15 | MHC-II binds 13-25mer, 15 is core |
| Filtering | IC50 | <500nM | Standard strong binder threshold |
| Filtering | VAF | >0.1 | Ensures clonal representation |
| Filtering | Expression | >1 TPM | Detectable transcription |
| Ranking | DAI | >500 | Good tumor specificity |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| No neoantigens found | Low mutation burden | Lower IC50 threshold to 1000nM |
| Missing HLA alleles | Incomplete typing | Use OptiType with WES data |
| VEP annotation errors | Plugin missing | Install Frameshift, Wildtype plugins |
| Expression data mismatch | Sample naming | Verify sample IDs match between VCF and expression |
| Low DAI values | Germline contamination | Ensure proper somatic filtering |

## Output Files

| File | Description |
|------|-------------|
| `*.filtered.tsv` | pVACseq filtered neoantigens |
| `*.all_epitopes.tsv` | All predicted epitopes |
| `top_neoantigen_candidates.tsv` | Ranked vaccine candidates |
| `neoantigen_summary.pdf` | Visualization figures |

## Related Skills

- immunoinformatics/mhc-binding-prediction - MHCflurry parameters
- immunoinformatics/neoantigen-prediction - pVACtools details
- immunoinformatics/immunogenicity-scoring - Ranking algorithms
- immunoinformatics/epitope-prediction - B-cell epitopes
- clinical-databases/hla-typing - HLA determination methods
- workflows/somatic-variant-pipeline - Upstream somatic calling
