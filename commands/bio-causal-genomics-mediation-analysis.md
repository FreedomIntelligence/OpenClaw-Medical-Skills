# bio-causal-genomics-mediation-analysis

> Decompose genetic effects into direct and indirect paths through mediating variables using the mediation R package. Tests whether gene expression, methylation, or other molecular phenotypes mediate the effect of genetic variants on disease. Use when testing whether a molecular phenotype mediates the genotype-to-phenotype relationship.

## Version Compatibility

Reference examples tested with: R stats (base), ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Mediation Analysis

**"Test whether gene expression mediates the effect of this variant on disease"** → Decompose the total genetic effect into direct and indirect (mediated) paths through a molecular phenotype, estimating ACME, ADE, and proportion mediated with bootstrap confidence intervals.
- R: `mediation::mediate()` for causal mediation analysis

## Framework

Causal mediation decomposes the total effect of a treatment (genotype) on an outcome
(phenotype) into:

- **ACME** (Average Causal Mediation Effect) - Indirect effect through the mediator
- **ADE** (Average Direct Effect) - Direct effect not through the mediator
- **Total effect** = ACME + ADE
- **Proportion mediated** = ACME / Total effect

Typical genomic applications:
- SNP -> gene expression (mediator) -> disease
- SNP -> DNA methylation (mediator) -> gene expression
- SNP -> protein levels (mediator) -> clinical outcome

## Basic Mediation with the mediation Package

**Goal:** Decompose a genetic effect into direct and indirect (mediated) paths through a molecular phenotype.

**Approach:** Fit separate models for mediator and outcome, then run mediate() with bootstrap to estimate ACME (indirect), ADE (direct), and proportion mediated.

```r
library(mediation)

# --- Step 1: Fit mediator model ---
# How does the treatment (genotype) affect the mediator (expression)?
mediator_model <- lm(expression ~ genotype + age + sex + pc1 + pc2, data = dat)

# --- Step 2: Fit outcome model ---
# How do treatment and mediator jointly affect the outcome?
# For binary outcome, use glm with family = binomial
outcome_model <- glm(
  disease ~ genotype + expression + age + sex + pc1 + pc2,
  data = dat, family = binomial
)

# --- Step 3: Run mediation analysis ---
# treat: name of treatment variable (genotype)
# mediator: name of mediator variable (expression)
# boot = TRUE: Use nonparametric bootstrap for CIs
# sims: Number of bootstrap simulations (1000 minimum for publication)
med_result <- mediate(
  mediator_model, outcome_model,
  treat = 'genotype', mediator = 'expression',
  boot = TRUE, sims = 1000
)

summary(med_result)
# Key outputs:
# ACME: Indirect effect (through expression)
# ADE: Direct effect (not through expression)
# Total Effect: ACME + ADE
# Prop. Mediated: ACME / Total
```

## Interpreting Results

```r
# Extract key quantities
acme <- med_result$d0           # Indirect (mediated) effect
acme_ci <- med_result$d0.ci     # 95% CI for ACME
ade <- med_result$z0            # Direct effect
total <- med_result$tau.coef    # Total effect
prop_med <- med_result$n0       # Proportion mediated

cat('ACME (indirect):', round(acme, 4), '\n')
cat('ACME 95% CI:', round(acme_ci[1], 4), 'to', round(acme_ci[2], 4), '\n')
cat('ADE (direct):', round(ade, 4), '\n')
cat('Total effect:', round(total, 4), '\n')
cat('Proportion mediated:', round(prop_med, 3), '\n')

# Significant ACME (CI excludes 0): Evidence for mediation
# Proportion mediated > 0.2: Meaningful mediation
# Proportion mediated > 0.8: Mediator explains most of the effect
```

## eQTL Mediation

**Goal:** Test whether gene expression mediates the effect of an eQTL on a disease outcome across multiple genes.

**Approach:** Wrap the mediation workflow in a function, loop over candidate genes, and adjust p-values for multiple testing.

```r
library(mediation)

run_eqtl_mediation <- function(dat, snp_col, expr_col, outcome_col, covariates) {
  covar_formula <- paste(covariates, collapse = ' + ')

  med_formula <- as.formula(paste(expr_col, '~', snp_col, '+', covar_formula))
  out_formula <- as.formula(paste(outcome_col, '~', snp_col, '+', expr_col, '+', covar_formula))

  med_model <- lm(med_formula, data = dat)

  if (length(unique(dat[[outcome_col]])) == 2) {
    out_model <- glm(out_formula, data = dat, family = binomial)
  } else {
    out_model <- lm(out_formula, data = dat)
  }

  result <- mediate(
    med_model, out_model,
    treat = snp_col, mediator = expr_col,
    boot = TRUE, sims = 1000
  )

  data.frame(
    snp = snp_col, gene = expr_col,
    acme = result$d0, acme_p = result$d0.p,
    ade = result$z0, ade_p = result$z0.p,
    total = result$tau.coef, total_p = result$tau.p,
    prop_mediated = result$n0
  )
}

# Example: test mediation for multiple genes
genes <- c('GENE_A', 'GENE_B', 'GENE_C')
covars <- c('age', 'sex', 'pc1', 'pc2', 'pc3')

mediation_results <- do.call(rbind, lapply(genes, function(g) {
  run_eqtl_mediation(dat, 'rs12345', g, 'disease_status', covars)
}))

# Adjust for multiple testing
mediation_results$acme_fdr <- p.adjust(mediation_results$acme_p, method = 'BH')
```

## Multi-Omics Mediation

**Goal:** Test cascading mediation chains across multiple molecular layers (e.g., SNP -> methylation -> expression -> disease).

**Approach:** Fit sequential models for each link in the chain and run separate mediation analyses for each mediator-outcome pair.

```r
# Test mediation chains: SNP -> methylation -> expression -> disease
library(mediation)

# Step 1: SNP -> methylation
mod_meth <- lm(methylation ~ genotype + age + sex, data = dat)

# Step 2: methylation -> expression (controlling for genotype)
mod_expr <- lm(expression ~ methylation + genotype + age + sex, data = dat)

# Step 3: expression -> disease (controlling for methylation and genotype)
mod_disease <- glm(
  disease ~ expression + methylation + genotype + age + sex,
  data = dat, family = binomial
)

# Test methylation as mediator of SNP -> expression
med_meth_expr <- mediate(mod_meth, mod_expr, treat = 'genotype', mediator = 'methylation',
                         boot = TRUE, sims = 1000)

# Test expression as mediator of methylation -> disease
med_expr_disease <- mediate(mod_expr, mod_disease, treat = 'methylation', mediator = 'expression',
                            boot = TRUE, sims = 1000)
```

## High-Dimensional Mediation (HDMA)

**Goal:** Test thousands of potential mediators simultaneously (e.g., all CpG sites) to identify which mediate a genetic effect.

**Approach:** Use HIMA's penalized regression to jointly select significant mediators from a high-dimensional mediator matrix and estimate their indirect effects.

```r
# For testing many potential mediators simultaneously (e.g., all CpG sites)
# install.packages('HIMA')
library(HIMA)

# X: treatment (genotype), M: high-dimensional mediators, Y: outcome
# HIMA uses penalized regression to select significant mediators

result <- hima(
  X = dat$genotype,
  Y = dat$disease,
  M = as.matrix(dat[, mediator_cols]),
  COV.XM = as.matrix(dat[, covariate_cols]),
  Y.family = 'binomial',
  M.family = 'gaussian',
  penalty = 'MCP'    # Minimax concave penalty (default)
)

# Results: significant mediators with estimated indirect effects
significant_mediators <- result[result$BH.FDR < 0.05, ]
```

## Assumptions and Diagnostics

```r
# --- Sequential ignorability assumption ---
# 1. No unmeasured confounders between treatment and mediator
# 2. No unmeasured confounders between mediator and outcome
# 3. No unmeasured confounders between treatment and outcome
# This assumption is UNTESTABLE but can be probed with sensitivity analysis

# --- Sensitivity analysis ---
# Tests how robust results are to unmeasured confounding
sens <- medsens(med_result, rho.by = 0.1, effect.type = 'indirect', sims = 1000)
summary(sens)

# rho: Correlation between residuals of mediator and outcome models
# At what rho does ACME cross zero? (larger |rho| = more robust)
# rho at which ACME = 0 is called the sensitivity parameter
# |rho| > 0.3: Reasonably robust to unmeasured confounding

plot(sens)
```

## Visualization

```r
library(ggplot2)

plot_mediation_diagram <- function(acme, ade, total, prop_med) {
  cat('Mediation Path Diagram:\n\n')
  cat('  Genotype ---[a]---> Mediator ---[b]---> Outcome\n')
  cat('      |                                     ^\n')
  cat('      +----------[c\' (ADE)]----------------+\n')
  cat('\n')
  cat('  Indirect (a*b = ACME):', round(acme, 4), '\n')
  cat('  Direct (c\' = ADE):', round(ade, 4), '\n')
  cat('  Total (c):', round(total, 4), '\n')
  cat('  Proportion mediated:', round(prop_med, 3), '\n')
}

plot_mediation_results <- function(results_df) {
  results_df$gene <- factor(results_df$gene, levels = results_df$gene[order(results_df$prop_mediated)])

  ggplot(results_df, aes(x = gene, y = prop_mediated)) +
    geom_col(fill = 'steelblue', alpha = 0.7) +
    geom_hline(yintercept = 0.2, linetype = 'dashed', color = 'red', alpha = 0.5) +
    coord_flip() +
    labs(x = NULL, y = 'Proportion Mediated', title = 'Mediation by Gene Expression') +
    theme_minimal()
}
```

## Related Skills

- mendelian-randomization - Causal inference using genetic instruments
- colocalization-analysis - Test if signals share a causal variant
- population-genetics/association-testing - GWAS for treatment-outcome associations
- multi-omics-integration/mofa-integration - Multi-omics data for mediation chains
