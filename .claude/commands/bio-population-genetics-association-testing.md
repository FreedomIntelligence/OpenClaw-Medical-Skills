# bio-population-genetics-association-testing

> Genome-wide association studies (GWAS) with PLINK. Perform case-control and quantitative trait association testing using logistic/linear regression with covariates, generate Manhattan and QQ plots for result visualization. Use when running GWAS or association tests.

**Available tools:** Read, Bash

# Association Testing

GWAS analysis using PLINK 2.0's unified `--glm` command for case-control and quantitative traits.

## PLINK 2.0 Association Testing

### Basic Case-Control (Binary Phenotype)

```bash
# Basic logistic regression
plink2 --bfile data --glm --out results

# With phenotype file
plink2 --bfile data --pheno pheno.txt --glm --out results
```

### Quantitative Trait (Continuous Phenotype)

```bash
# Linear regression for quantitative traits
plink2 --bfile data --pheno pheno.txt --glm --out results
```

### With Covariates

```bash
# Include covariates (sex, age, PCs)
plink2 --bfile data \
    --pheno pheno.txt \
    --covar covariates.txt \
    --glm --out results

# Specify which covariates to use
plink2 --bfile data \
    --pheno pheno.txt \
    --covar covariates.txt \
    --covar-name PC1,PC2,PC3,age,sex \
    --glm --out results
```

## Covariate Files

### Phenotype File Format

```
# pheno.txt: FID IID pheno
# For binary: 1=control, 2=case, -9=missing
# For quantitative: continuous values
FAM001 IND001 2
FAM002 IND002 1
FAM003 IND003 1.5
```

### Covariate File Format

```
# covariates.txt: FID IID cov1 cov2 ...
FAM001 IND001 0.15 35 1
FAM002 IND002 -0.22 42 2
FAM003 IND003 0.08 28 1
```

## GLM Options

### Phenotype Handling

```bash
# Multiple phenotypes (test all)
plink2 --bfile data --pheno pheno_multi.txt --glm --out results

# Specific phenotype column
plink2 --bfile data --pheno pheno_multi.txt --pheno-name trait1 --glm --out results

# Missing phenotype handling
plink2 --bfile data --glm allow-no-covars --out results
```

### Model Options

```bash
# Additive model (default)
plink2 --bfile data --glm --out results

# Dominant model
plink2 --bfile data --glm dominant --out results

# Recessive model
plink2 --bfile data --glm recessive --out results

# Genotypic (2df test)
plink2 --bfile data --glm genotypic --out results

# Hide covariates from output (cleaner output)
plink2 --bfile data --covar cov.txt --glm hide-covar --out results
```

### Firth Regression (Rare Variants)

```bash
# Enable Firth fallback for case-control (default in PLINK 2.0)
plink2 --bfile data --glm firth-fallback --out results

# Force Firth regression
plink2 --bfile data --glm firth --out results

# Disable Firth
plink2 --bfile data --glm no-firth --out results
```

## Output Format

### Output Columns

```bash
# Default output: results.PHENO1.glm.logistic or results.PHENO1.glm.linear
# Columns: CHROM, POS, ID, REF, ALT, A1, FIRTH?, TEST, OBS_CT, OR/BETA, SE, Tstat, P
```

### Custom Output Columns

```bash
# Add specific columns
plink2 --bfile data --glm cols=+a1freq,+machr2 --out results

# Available columns:
# +a1freq: A1 allele frequency
# +machr2: MaCH R-squared
# +ax: Reference allele dosage
# +err: Standard errors
```

## Population Stratification Control

### Include Principal Components

```bash
# 1. Run PCA
plink2 --bfile data --pca 10 --out pca_results

# 2. Use PCs as covariates
plink2 --bfile data \
    --pheno pheno.txt \
    --covar pca_results.eigenvec \
    --covar-name PC1,PC2,PC3,PC4,PC5 \
    --glm --out results
```

### Combined Workflow

```bash
# QC, PCA, and GWAS in sequence
plink2 --bfile raw --maf 0.01 --geno 0.05 --hwe 1e-6 --make-bed --out qc
plink2 --bfile qc --pca 10 --out pca
plink2 --bfile qc \
    --pheno pheno.txt \
    --covar pca.eigenvec \
    --covar-name PC1-PC5 \
    --glm hide-covar --out gwas
```

## Result Filtering

### Command Line Filtering

```bash
# Filter significant results
awk 'NR==1 || $13 < 5e-8' results.PHENO1.glm.logistic > significant.txt

# Extract top hits
sort -k13 -g results.PHENO1.glm.logistic | head -100 > top_hits.txt
```

### Python Analysis

```python
import pandas as pd

results = pd.read_csv('results.PHENO1.glm.logistic', sep='\t')

significant = results[results['P'] < 5e-8]
print(f'Genome-wide significant hits: {len(significant)}')

suggestive = results[results['P'] < 1e-5]
print(f'Suggestive hits: {len(suggestive)}')
```

## Visualization

### Manhattan Plot (Python)

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

results = pd.read_csv('results.PHENO1.glm.logistic', sep='\t')
results = results[results['TEST'] == 'ADD']
results['-log10P'] = -np.log10(results['P'])

chrom_colors = ['#1f77b4', '#ff7f0e']
results['color'] = results['#CHROM'].apply(lambda x: chrom_colors[x % 2])

cumulative_pos = []
offset = 0
for chrom in sorted(results['#CHROM'].unique()):
    chrom_data = results[results['#CHROM'] == chrom]
    cumulative_pos.extend(chrom_data['POS'] + offset)
    offset += chrom_data['POS'].max()

results['cumulative_pos'] = cumulative_pos

plt.figure(figsize=(14, 6))
plt.scatter(results['cumulative_pos'], results['-log10P'], c=results['color'], s=1)
plt.axhline(y=-np.log10(5e-8), color='red', linestyle='--', label='Genome-wide (5e-8)')
plt.axhline(y=-np.log10(1e-5), color='blue', linestyle='--', label='Suggestive (1e-5)')
plt.xlabel('Chromosome')
plt.ylabel('-log10(P)')
plt.legend()
plt.savefig('manhattan.png', dpi=150)
```

### QQ Plot (Python)

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

results = pd.read_csv('results.PHENO1.glm.logistic', sep='\t')
observed_p = results[results['TEST'] == 'ADD']['P'].dropna().sort_values()

n = len(observed_p)
expected_p = np.arange(1, n + 1) / (n + 1)

plt.figure(figsize=(6, 6))
plt.scatter(-np.log10(expected_p), -np.log10(observed_p), s=1)
plt.plot([0, 8], [0, 8], 'r--')
plt.xlabel('Expected -log10(P)')
plt.ylabel('Observed -log10(P)')

lambda_gc = np.median(stats.chi2.ppf(1 - observed_p, 1)) / stats.chi2.ppf(0.5, 1)
plt.title(f'QQ Plot (λ = {lambda_gc:.3f})')
plt.savefig('qqplot.png', dpi=150)
```

## Genomic Inflation

```python
from scipy import stats
import numpy as np

results = pd.read_csv('results.PHENO1.glm.logistic', sep='\t')
pvalues = results[results['TEST'] == 'ADD']['P'].dropna()

chisq = stats.chi2.ppf(1 - pvalues, 1)
lambda_gc = np.median(chisq) / stats.chi2.ppf(0.5, 1)
print(f'Genomic inflation factor: {lambda_gc:.3f}')
# Good: 1.0-1.05, Acceptable: 1.05-1.1, Concerning: >1.1
```

## Related Skills

- plink-basics - Data preparation and QC
- population-structure - PCA for stratification control
- linkage-disequilibrium - LD pruning before analysis
