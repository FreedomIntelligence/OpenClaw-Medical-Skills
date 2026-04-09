# bio-causal-genomics-mendelian-randomization

> Estimate causal effects between exposures and outcomes using genetic variants as instrumental variables with TwoSampleMR. Implements IVW, MR-Egger, weighted median, and MR-PRESSO methods for robust causal inference from GWAS summary statistics. Use when testing whether an exposure causally affects an outcome using genetic instruments.

## Version Compatibility

Reference examples tested with: TwoSampleMR 0.5+, MendelianRandomization 0.9+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion("<pkg>")` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Mendelian Randomization

**"Test whether my exposure causally affects this outcome using GWAS data"** → Use genetic variants as instrumental variables to estimate causal effects from GWAS summary statistics, applying IVW, MR-Egger, and weighted median methods for robust inference.
- R: `TwoSampleMR::mr()` for multi-method causal estimation
- R: `MendelianRandomization::mr_ivw()` for individual methods

## Core Concepts

Mendelian randomization (MR) uses genetic variants as instrumental variables (IVs) to estimate
causal effects of exposures on outcomes. Valid instruments must satisfy three assumptions:

1. **Relevance** - The variant is associated with the exposure (F-statistic > 10)
2. **Independence** - The variant is not associated with confounders
3. **Exclusion restriction** - The variant affects the outcome only through the exposure

## TwoSampleMR Workflow

**Goal:** Estimate the causal effect of an exposure on an outcome using GWAS summary statistics and genetic instruments.

**Approach:** Extract instruments for the exposure, extract matching outcome data, harmonize allele directions, and run multiple MR methods (IVW, Egger, weighted median, weighted mode).

**"Test if an exposure causally affects an outcome"** -> Use genetic variants as instrumental variables to estimate causal effects from GWAS data.
- R: `TwoSampleMR` (extract_instruments + harmonise_data + mr)
- R: `MendelianRandomization` (mr_input + mr_ivw/mr_egger)

```r
library(TwoSampleMR)

# --- Step 1: Extract instruments for the exposure ---
# From OpenGWAS (requires authentication -- see below)
exposure_dat <- extract_instruments(outcomes = 'ieu-a-2', p1 = 5e-08, clump = TRUE)

# From local GWAS summary statistics
exposure_dat <- read_exposure_data(
  filename = 'exposure_gwas.txt',
  sep = '\t',
  snp_col = 'SNP', beta_col = 'BETA', se_col = 'SE',
  effect_allele_col = 'A1', other_allele_col = 'A2',
  pval_col = 'P', eaf_col = 'EAF'
)

# Clump instruments to remove LD (r2 < 0.001, 10 Mb window)
# r2 < 0.001: Standard threshold to ensure instrument independence
# 10000 kb window: Wide enough to capture long-range LD
exposure_dat <- clump_data(exposure_dat, clump_r2 = 0.001, clump_kb = 10000)

# --- Step 2: Extract outcome data ---
outcome_dat <- extract_outcome_data(snps = exposure_dat$SNP, outcomes = 'ieu-a-7')

# From local summary statistics
outcome_dat <- read_outcome_data(
  filename = 'outcome_gwas.txt',
  sep = '\t',
  snp_col = 'SNP', beta_col = 'BETA', se_col = 'SE',
  effect_allele_col = 'A1', other_allele_col = 'A2',
  pval_col = 'P', eaf_col = 'EAF'
)

# --- Step 3: Harmonize ---
# Ensures effect alleles are aligned between exposure and outcome
dat <- harmonise_data(exposure_dat, outcome_dat, action = 2)

# action = 1: Assume all alleles on forward strand
# action = 2: Try to infer forward strand (default, recommended)
# action = 3: Correct strand for palindromic SNPs using allele frequencies

# --- Step 4: Perform MR ---
results <- mr(dat)

# Run all standard methods
results <- mr(dat, method_list = c(
  'mr_ivw',              # Inverse variance weighted (primary)
  'mr_egger_regression', # MR-Egger (detects pleiotropy)
  'mr_weighted_median',  # Weighted median (robust to 50% invalid)
  'mr_weighted_mode'     # Weighted mode (robust to outliers)
))
```

## OpenGWAS Authentication

OpenGWAS (ieugwasr) requires authentication. The auth system has changed multiple
times. Refer to the ieugwasr README for current instructions:
https://github.com/MRCIEU/ieugwasr

For reproducibility, prefer downloading GWAS summary statistics directly and using
`read_exposure_data()` / `read_outcome_data()` with local files.

## Interpreting Results

**Goal:** Evaluate MR evidence through method comparison, heterogeneity testing, and sensitivity analyses.

**Approach:** Compare estimates across methods for consistency, test for heterogeneity (Cochran's Q), pleiotropy (Egger intercept), and single-SNP influence (leave-one-out).

```r
# Method comparison table
results

# Key columns: method, nsnp, b (causal estimate), se, pval
# IVW is the primary method; others are sensitivity analyses
# Consistent direction/magnitude across methods strengthens evidence

# --- Heterogeneity (Cochran's Q) ---
het <- mr_heterogeneity(dat)
# Significant Q-statistic suggests pleiotropy or invalid instruments
# Q p-value < 0.05: Evidence of heterogeneity

# --- Pleiotropy (Egger intercept) ---
pleiotropy <- mr_pleiotropy_test(dat)
# Significant intercept (p < 0.05): Evidence of directional pleiotropy
# Non-significant intercept: No evidence (but low power with few SNPs)

# --- Leave-one-out ---
loo <- mr_leaveoneout(dat)
# Check if any single SNP drives the result
# Causal estimate should remain stable when each SNP is removed

# --- Single SNP analysis ---
single <- mr_singlesnp(dat)
```

## Instrument Strength

**Goal:** Assess whether genetic instruments are strong enough for valid MR inference.

**Approach:** Compute per-instrument F-statistics from exposure effect sizes and standard errors, removing weak instruments (F < 10).

```r
# F-statistic for each instrument
# F = (beta_exposure / se_exposure)^2
# F > 10: Sufficient instrument strength (conventional threshold)
# F < 10: Weak instrument bias (toward confounded observational estimate)
dat$f_statistic <- (dat$beta.exposure / dat$se.exposure)^2

# Mean F-statistic across all instruments
mean_f <- mean(dat$f_statistic)
cat('Mean F-statistic:', mean_f, '\n')
cat('Instruments with F < 10:', sum(dat$f_statistic < 10), '\n')

# Remove weak instruments
dat <- dat[dat$f_statistic >= 10, ]
```

## Bidirectional MR

**Goal:** Test whether causal direction runs from exposure to outcome or vice versa.

**Approach:** Run Steiger directionality test and perform MR in both directions to distinguish true causation from reverse causation.

```r
# Steiger test: Verify variant explains more variance in exposure than outcome
steiger <- directionality_test(dat)
# correct_causal_direction = TRUE: Instruments are valid
# correct_causal_direction = FALSE: Reverse causation likely

# Run MR in reverse direction
exposure_rev <- extract_instruments(outcomes = 'ieu-a-7')
outcome_rev <- extract_outcome_data(snps = exposure_rev$SNP, outcomes = 'ieu-a-2')
dat_rev <- harmonise_data(exposure_rev, outcome_rev)
results_rev <- mr(dat_rev)
```

## Visualization

**Goal:** Create diagnostic plots for MR results including scatter, forest, leave-one-out, and funnel plots.

**Approach:** Use TwoSampleMR built-in plotting functions to visualize method slopes, per-SNP estimates, and potential asymmetry.

```r
library(TwoSampleMR)

# Scatter plot: SNP-exposure vs SNP-outcome effects with method slopes
mr_scatter_plot(results, dat)

# Forest plot: Individual SNP and combined estimates
mr_forest_plot(single)

# Leave-one-out plot
mr_leaveoneout_plot(loo)

# Funnel plot: Precision vs causal estimate (asymmetry = pleiotropy)
mr_funnel_plot(single)
```

## Power Calculation

**Goal:** Estimate MR power based on instrument strength, sample size, and expected effect size.

**Approach:** Compute total variance explained by instruments from allele frequencies and effect sizes.

```r
# MR power depends on: sample size, variance explained by instruments, effect size
# Use mRnd web tool: https://shiny.cnsgenomics.com/mRnd/
# Or approximate:
variance_explained <- sum(2 * dat$eaf.exposure * (1 - dat$eaf.exposure) * dat$beta.exposure^2)
cat('Variance explained by instruments:', variance_explained, '\n')
# Higher R^2 = more power; typically need R^2 > 0.01 for reasonable power
```

## Related Skills

- pleiotropy-detection - Sensitivity analyses for MR assumptions
- colocalization-analysis - Confirm shared causal variants
- fine-mapping - Prioritize causal variants at instrument loci
- population-genetics/association-testing - GWAS for exposure and outcome data
