# bio-clinical-databases-polygenic-risk

> Calculate polygenic risk scores using PRSice-2, LDpred2, or PRS-CS from GWAS summary statistics. Use when predicting disease risk from genome-wide genetic variants.

## Version Compatibility

Reference examples tested with: LDpred2 1.14+, PRSice-2 2.3+, numpy 1.26+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Polygenic Risk Scores

**"Calculate polygenic risk scores for my cohort"** → Compute genome-wide risk scores from GWAS summary statistics and individual genotypes to predict disease susceptibility.
- CLI: `PRSice_linux --base gwas.txt --target genotypes --out prs_results`
- R: `bigsnpr::snp_ldpred2_auto()` for LDpred2 Bayesian PRS

## PRSice-2 Workflow

**Goal:** Calculate polygenic risk scores from GWAS summary statistics using clumping and thresholding.

**Approach:** Run PRSice-2 with GWAS summary stats and target genotypes, applying LD clumping and multiple p-value thresholds.

### Basic PRS Calculation

```bash
# PRSice-2 with clumping and thresholding
PRSice_linux \
    --base gwas_summary.txt \
    --target genotypes \
    --snp SNP \
    --chr CHR \
    --bp BP \
    --A1 A1 \
    --A2 A2 \
    --pvalue P \
    --beta BETA \
    --clump-kb 250 \
    --clump-r2 0.1 \
    --bar-levels 5e-8,1e-5,1e-3,0.01,0.05,0.1,0.5,1 \
    --fastscore \
    --all-score \
    --out prs_results
```

### PRSice-2 with Covariates

```bash
PRSice_linux \
    --base gwas_summary.txt \
    --target genotypes \
    --pheno phenotype.txt \
    --cov covariates.txt \
    --cov-col @PC[1-10],Age,Sex \
    --binary-target T \
    --clump-kb 250 \
    --clump-r2 0.1 \
    --out prs_with_cov
```

## GWAS Summary Statistics Format

```
SNP          CHR  BP        A1  A2  BETA    SE      P
rs12345      1    10000     A   G   0.05    0.01    1e-8
rs67890      1    20000     T   C   -0.03   0.02    0.001
```

## LDpred2 (R)

**Goal:** Compute Bayesian polygenic risk scores with automatic hyperparameter tuning via LDpred2-auto.

**Approach:** Load genotypes with bigsnpr, match GWAS variants, compute LD matrix, estimate heritability with LD score regression, then run LDpred2-auto.

### Setup and Run

```r
library(bigsnpr)
library(data.table)

# Load genotype data (plink bed/bim/fam)
obj.bigsnp <- snp_attach('genotypes.rds')
G <- obj.bigsnp$genotypes
map <- obj.bigsnp$map

# Load and format GWAS summary stats
sumstats <- fread('gwas_summary.txt')

# Match variants
df_beta <- snp_match(sumstats, map, strand_flip = TRUE)

# Compute LD matrix (correlation)
# Uses reference panel or in-sample LD
corr <- snp_cor(G, ind.col = df_beta$`_NUM_ID_`)

# LDpred2-auto (recommended - automatic hyperparameter tuning)
ldsc <- snp_ldsc2(corr, df_beta)
h2_est <- ldsc[['h2']]

multi_auto <- snp_ldpred2_auto(
    corr,
    df_beta,
    h2_init = h2_est,
    vec_p_init = seq_log(1e-4, 0.2, 30),
    ncores = 4
)

# Extract posterior effect sizes
beta_auto <- sapply(multi_auto, function(x) x$beta_est)
pred_auto <- big_prodMat(G, beta_auto)
```

### LDpred2 Grid Model

```r
# Grid of hyperparameters
h2_seq <- round(h2_est * c(0.7, 1, 1.4), 4)
p_seq <- signif(seq_log(1e-5, 1, 21), 2)
params <- expand.grid(p = p_seq, h2 = h2_seq, sparse = c(FALSE, TRUE))

# Run LDpred2-grid
beta_grid <- snp_ldpred2_grid(corr, df_beta, params, ncores = 4)
pred_grid <- big_prodMat(G, beta_grid)

# Select best parameters by validation R2
auc_grid <- apply(pred_grid, 2, function(x) {
    AUC(x, obj.bigsnp$fam$affection - 1)
})
best_params <- params[which.max(auc_grid), ]
```

## PRS-CS

**Goal:** Compute PRS using continuous shrinkage priors with an external LD reference panel.

**Approach:** Run PRS-CS to estimate posterior effect sizes, then score with plink.

```bash
# PRS-CS with external LD reference
python PRScs.py \
    --ref_dir=ldblk_1kg_eur \
    --bim_prefix=target \
    --sst_file=gwas_summary.txt \
    --n_gwas=100000 \
    --out_dir=prscs_output

# Score with plink
plink --bfile target \
    --score prscs_output_pst_eff_a1_b0.5_phi1e-02.txt 2 4 6 \
    --out prs_scores
```

## Score Normalization

**Goal:** Normalize raw PRS values to Z-scores and population percentiles for interpretable reporting.

**Approach:** Z-score normalize against a reference distribution, then convert to percentiles via the normal CDF.

```python
import numpy as np
from scipy import stats

def normalize_prs(scores, reference_scores=None):
    '''Z-score normalize PRS

    Args:
        scores: Array of PRS values
        reference_scores: Population reference (if None, use scores)

    Returns:
        Z-scored PRS values
    '''
    if reference_scores is None:
        reference_scores = scores
    mean = np.mean(reference_scores)
    std = np.std(reference_scores)
    return (scores - mean) / std

def prs_to_percentile(z_score):
    '''Convert Z-scored PRS to population percentile'''
    return stats.norm.cdf(z_score) * 100

# Example
prs_raw = np.array([0.5, 1.2, -0.3, 2.1, 0.8])
prs_z = normalize_prs(prs_raw)
percentiles = prs_to_percentile(prs_z)
```

## Risk Stratification

**Goal:** Categorize individuals into clinical risk groups based on their Z-scored PRS.

**Approach:** Apply population-distribution-based thresholds to assign Low/Average/High/Very High risk tiers.

```python
def stratify_risk(prs_z, thresholds=None):
    '''Categorize PRS into risk groups

    Default thresholds based on population distribution:
    - Low: < -1 SD (bottom 16%)
    - Average: -1 to 1 SD (middle 68%)
    - High: > 1 SD (top 16%)
    - Very high: > 2 SD (top 2.5%)
    '''
    if thresholds is None:
        thresholds = {'low': -1, 'high': 1, 'very_high': 2}

    if prs_z > thresholds['very_high']:
        return 'Very High Risk'
    elif prs_z > thresholds['high']:
        return 'High Risk'
    elif prs_z < thresholds['low']:
        return 'Low Risk'
    else:
        return 'Average Risk'
```

## PGS Catalog Integration

**Goal:** Download pre-computed PRS weights from the PGS Catalog for published scores.

**Approach:** Query the PGS Catalog REST API by score ID and retrieve the scoring file URL.

```python
def download_pgs_weights(pgs_id):
    '''Download PRS weights from PGS Catalog

    Args:
        pgs_id: PGS ID (e.g., 'PGS000001')
    '''
    import requests
    url = f'https://www.pgscatalog.org/rest/score/{pgs_id}'
    response = requests.get(url)
    score_info = response.json()

    # Download scoring file
    ftp_url = score_info['ftp_scoring_file']
    # Use wget or requests to download

    return score_info
```

## Validation Metrics

**Goal:** Evaluate PRS predictive performance using discrimination and effect size metrics.

**Approach:** Compute Nagelkerke R-squared, AUC, and odds ratio per standard deviation from logistic regression models.

```r
# Nagelkerke's R2 for case-control
library(rms)
mod <- lrm(case ~ prs + age + sex + PC1 + PC2, data = df)
r2 <- mod$stats['R2']

# AUC
library(pROC)
auc_result <- auc(case ~ prs, data = df)

# Odds ratio per SD
mod <- glm(case ~ scale(prs), data = df, family = 'binomial')
or_per_sd <- exp(coef(mod)['scale(prs)'])
```

## Related Skills

- population-genetics/gwas-analysis - GWAS input
- population-genetics/population-structure - Population matching
- clinical-databases/variant-prioritization - Clinical filtering
