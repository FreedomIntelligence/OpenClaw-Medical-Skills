# bio-causal-genomics-pleiotropy-detection

> Detect and correct for horizontal pleiotropy in Mendelian randomization analyses using MR-PRESSO for outlier removal, MR-Egger regression for directional pleiotropy, and Steiger filtering for variant directionality. Use when validating MR results, detecting pleiotropic instruments, or running sensitivity analyses for causal inference.

## Version Compatibility

Reference examples tested with: MR-PRESSO 1.0+, TwoSampleMR 0.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion("<pkg>")` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Pleiotropy Detection

**"Check my MR results for pleiotropic bias"** → Detect and correct for horizontal pleiotropy using outlier removal (MR-PRESSO), directional pleiotropy testing (MR-Egger intercept), and variant directionality filtering (Steiger) to validate causal inference results.
- R: `MRPRESSO::mr_presso()` for global and distortion tests
- R: `TwoSampleMR::mr_egger_regression()` for Egger intercept test

## Overview

Horizontal pleiotropy violates the exclusion restriction assumption of MR: instruments
affect the outcome through pathways other than the exposure. Detecting and correcting
for pleiotropy is essential for valid causal inference.

Types of pleiotropy:
- **Vertical** (mediated): Instrument -> exposure -> outcome (valid, not a problem)
- **Horizontal** (direct): Instrument -> outcome bypassing exposure (violates MR assumptions)
- **Balanced**: Pleiotropic effects cancel out (IVW still valid, Egger intercept ~0)
- **Directional**: Pleiotropic effects are systematic (biases IVW, Egger detects this)

## MR-PRESSO

**Goal:** Detect and remove pleiotropic outlier instruments from an MR analysis.

**Approach:** Run MR-PRESSO to test for global pleiotropy, identify individual outlier SNPs, test whether their removal changes the causal estimate (distortion test), and obtain a corrected estimate.

```r
# install.packages('remotes')
# remotes::install_github('rondolab/MR-PRESSO')
library(MRPRESSO)

# Input: harmonized data from TwoSampleMR
# Columns needed: beta.exposure, beta.outcome, se.exposure, se.outcome
presso_input <- data.frame(
  bx = dat$beta.exposure,
  by = dat$beta.outcome,
  bxse = dat$se.exposure,
  byse = dat$se.outcome
)

# --- Run MR-PRESSO ---
# NbDistribution: Number of simulations for null distribution (minimum 1000)
# SignifThreshold: P-value threshold for outlier detection (0.05 standard)
presso_result <- mr_presso(
  BetaOutcome = 'by', BetaExposure = 'bx',
  SdOutcome = 'byse', SdExposure = 'bxse',
  OUTLIERtest = TRUE, DISTORTIONtest = TRUE,
  data = presso_input,
  NbDistribution = 5000,
  SignifThreshold = 0.05
)

# --- Global test ---
# Tests whether there is any pleiotropy among instruments
# Significant p-value: Evidence of horizontal pleiotropy
global_p <- presso_result$`MR-PRESSO results`$`Global Test`$Pvalue
cat('Global test p-value:', global_p, '\n')

# --- Outlier test ---
# Identifies individual pleiotropic SNPs
outliers <- presso_result$`MR-PRESSO results`$`Outlier Test`
cat('\nOutlier test results:\n')
print(outliers)

# Outlier SNPs (p < 0.05)
outlier_indices <- which(outliers$Pvalue < 0.05)
cat('Outlier SNPs:', length(outlier_indices), '\n')

# --- Distortion test ---
# Tests whether removing outliers significantly changes the causal estimate
# Significant: Outliers were meaningfully biasing the estimate
distortion_p <- presso_result$`MR-PRESSO results`$`Distortion Test`$Pvalue
cat('Distortion test p-value:', distortion_p, '\n')

# --- Corrected estimate ---
# MR estimate after removing outlier SNPs
main_results <- presso_result$`Main MR results`
cat('\nRaw IVW estimate:', main_results$`Causal Estimate`[1], '\n')
cat('Corrected IVW estimate:', main_results$`Causal Estimate`[2], '\n')
```

## MR-Egger Diagnostics

**Goal:** Test for directional pleiotropy and obtain a pleiotropy-adjusted causal estimate.

**Approach:** Fit MR-Egger regression where the intercept estimates average pleiotropic bias, and check I-squared for instrument strength under the NOME assumption.

```r
library(TwoSampleMR)

# MR-Egger regression allows for a non-zero intercept
# The intercept estimates the average pleiotropic effect
egger <- mr_egger_regression(dat$beta.exposure, dat$beta.outcome,
                              dat$se.exposure, dat$se.outcome)

# --- Egger intercept ---
# Significant intercept (p < 0.05): Directional pleiotropy present
# Non-significant: No evidence (but low power with < 10 SNPs)
cat('Egger intercept:', round(egger$b_i, 5), '\n')
cat('Intercept SE:', round(egger$se_i, 5), '\n')
cat('Intercept p-value:', format.pval(egger$pval_i), '\n')

# --- Egger slope ---
# Valid causal estimate EVEN with directional pleiotropy (InSIDE assumption)
cat('\nEgger causal estimate:', round(egger$b, 4), '\n')
cat('Egger SE:', round(egger$se, 4), '\n')
cat('Egger p-value:', format.pval(egger$pval), '\n')

# --- I-squared for Egger ---
# I^2 measures instrument strength for MR-Egger specifically
# I^2 > 0.9: Egger estimate reliable
# I^2 < 0.6: Egger has low power, interpret with caution (NOME violation)
isq <- Isq(dat$beta.exposure, dat$se.exposure)
cat('\nI-squared:', round(isq, 3), '\n')
if (isq < 0.9) cat('Warning: I-squared < 0.9; Egger estimate may be unreliable (NOME violation)\n')
```

## Steiger Filtering

**Goal:** Verify that instruments act in the correct causal direction (exposure -> outcome, not reverse).

**Approach:** Apply the Steiger test to each instrument, remove those explaining more outcome variance than exposure variance, and re-run MR on filtered instruments.

```r
library(TwoSampleMR)

# Steiger test: Verify each instrument explains more variance in
# the exposure than the outcome. Instruments failing this test
# may act through a reverse causal pathway.

steiger <- steiger_filtering(dat)

# Keep only correctly oriented instruments
dat_steiger <- steiger[steiger$steiger_dir == TRUE, ]
cat('Instruments passing Steiger filter:', nrow(dat_steiger), 'of', nrow(steiger), '\n')

# Re-run MR with filtered instruments
results_steiger <- mr(dat_steiger)
print(results_steiger[, c('method', 'nsnp', 'b', 'se', 'pval')])

# Directionality test (aggregate)
direction <- directionality_test(dat)
cat('\nCorrect causal direction:', direction$correct_causal_direction, '\n')
cat('Steiger p-value:', format.pval(direction$steiger_pval), '\n')
```

## Additional Sensitivity Methods

```r
library(TwoSampleMR)

# --- Contamination mixture ---
# Assumes some instruments are valid, others are not
# Does not require majority valid assumption
mr_conmix <- mr(dat, method_list = 'mr_raps')

# --- MR-RAPS ---
# NOTE: MRAPS CRAN package was archived March 2025.
# Use the MendelianRandomization package instead, or install from GitHub:
# remotes::install_github('qingyuanzhao/mr.raps')
library(MendelianRandomization)

mr_input <- mr_input(
  bx = dat$beta.exposure, bxse = dat$se.exposure,
  by = dat$beta.outcome, byse = dat$se.outcome
)

raps_result <- mr_raps(mr_input)
cat('MR-RAPS estimate:', raps_result$Estimate, '\n')
cat('MR-RAPS p-value:', raps_result$Pvalue, '\n')

# --- Multivariable MR ---
# Controls for pleiotropy by including multiple exposures simultaneously
# e.g., adjust for BMI when estimating effect of lipids on CHD
exposure1 <- extract_instruments('ieu-a-300')  # LDL
exposure2 <- extract_instruments('ieu-a-302')  # HDL

# Combine and perform multivariable MR
# (See TwoSampleMR vignette for full multivariable workflow)
```

## Comprehensive Sensitivity Framework

**Goal:** Run a complete battery of MR sensitivity analyses to validate causal findings.

**Approach:** Apply IVW, MR-Egger, weighted median, weighted mode, heterogeneity, Egger intercept, leave-one-out, and MR-PRESSO in a single function and summarize results.

```r
library(TwoSampleMR)
library(MRPRESSO)

run_sensitivity <- function(dat) {
  results <- list()

  # 1. IVW (primary)
  results$ivw <- mr(dat, method_list = 'mr_ivw')

  # 2. MR-Egger
  results$egger <- mr(dat, method_list = 'mr_egger_regression')

  # 3. Weighted median (robust to 50% invalid instruments)
  results$median <- mr(dat, method_list = 'mr_weighted_median')

  # 4. Weighted mode
  results$mode <- mr(dat, method_list = 'mr_weighted_mode')

  # 5. Heterogeneity
  results$het <- mr_heterogeneity(dat)

  # 6. Egger intercept
  results$pleio <- mr_pleiotropy_test(dat)

  # 7. Leave-one-out
  results$loo <- mr_leaveoneout(dat)

  # 8. MR-PRESSO
  presso_input <- data.frame(
    bx = dat$beta.exposure, by = dat$beta.outcome,
    bxse = dat$se.exposure, byse = dat$se.outcome
  )
  results$presso <- mr_presso(
    BetaOutcome = 'by', BetaExposure = 'bx',
    SdOutcome = 'byse', SdExposure = 'bxse',
    OUTLIERtest = TRUE, DISTORTIONtest = TRUE,
    data = presso_input, NbDistribution = 5000, SignifThreshold = 0.05
  )

  results
}

summarize_sensitivity <- function(sens) {
  cat('=== MR Sensitivity Analysis Summary ===\n\n')

  # Method comparison
  all_mr <- rbind(sens$ivw, sens$egger, sens$median, sens$mode)
  cat('Method comparison:\n')
  print(all_mr[, c('method', 'b', 'se', 'pval')])

  # Heterogeneity
  cat('\nHeterogeneity (Cochran Q):\n')
  cat('  Q p-value (IVW):', sens$het$Q_pval[sens$het$method == 'Inverse variance weighted'], '\n')

  # Egger intercept
  cat('\nEgger intercept:\n')
  cat('  Intercept:', sens$pleio$egger_intercept, '\n')
  cat('  P-value:', sens$pleio$pval, '\n')

  # MR-PRESSO global test
  cat('\nMR-PRESSO global test p-value:',
      sens$presso$`MR-PRESSO results`$`Global Test`$Pvalue, '\n')

  cat('\n--- Interpretation ---\n')
  cat('Consistent estimates across methods: Evidence strengthened\n')
  cat('Significant Egger intercept: Directional pleiotropy present\n')
  cat('Significant MR-PRESSO global: Horizontal pleiotropy detected\n')
  cat('Significant heterogeneity: Instruments may be invalid\n')
}
```

## STROBE-MR Reporting

When reporting MR analyses, follow STROBE-MR guidelines:

1. Report all MR methods tested (not just the most significant)
2. Report heterogeneity Q-statistic and p-value
3. Report Egger intercept with p-value
4. Report MR-PRESSO global test and number of outliers removed
5. Report F-statistics for instrument strength
6. Report Steiger directionality test
7. State whether results are consistent across sensitivity analyses
8. Acknowledge limitations of the MR assumptions

## Related Skills

- mendelian-randomization - Primary MR analysis that pleiotropy tests validate
- fine-mapping - Identify causal variants at instrument loci
- population-genetics/association-testing - GWAS data for MR instruments
