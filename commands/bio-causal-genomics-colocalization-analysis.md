# bio-causal-genomics-colocalization-analysis

> Test whether two traits share a causal variant at a genomic locus using Bayesian colocalization with coloc. Computes posterior probabilities for shared vs distinct causal variants between GWAS and eQTL signals. Use when determining if a GWAS signal and an eQTL share the same causal variant.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Colocalization Analysis

**"Test whether my GWAS signal and eQTL share the same causal variant"** → Compute Bayesian posterior probabilities for five colocalization hypotheses (no association, trait-1-only, trait-2-only, distinct causal variants, shared causal variant) to distinguish true causal overlap from LD-driven coincidence.
- R: `coloc::coloc.abf()` for approximate Bayes factor colocalization

## Overview

Colocalization tests whether two association signals at the same locus are driven by the
same causal variant. This distinguishes shared causality from coincidental overlap due to LD.

Five hypotheses tested by coloc:
- H0: No association with either trait
- H1: Association with trait 1 only
- H2: Association with trait 2 only
- H3: Both associated, different causal variants
- H4: Both associated, shared causal variant

## coloc.abf Analysis

**Goal:** Test whether two traits share a causal variant at a GWAS locus using Bayesian colocalization.

**Approach:** Format summary statistics for each trait as named lists, run coloc.abf to compute posterior probabilities for five hypotheses (H0-H4), and interpret PP.H4 as evidence for a shared causal variant.

```r
library(coloc)

# --- Input format: named list with GWAS summary stats ---
# Required fields: beta, varbeta, snp, position, type, N
# type = 'quant' (continuous) or 'cc' (case-control)

gwas_data <- list(
  beta = gwas_df$BETA,
  varbeta = gwas_df$SE^2,
  snp = gwas_df$SNP,
  position = gwas_df$POS,
  type = 'cc',           # Case-control study
  s = 0.3,               # Proportion of cases (required for cc)
  N = 50000              # Total sample size
)

eqtl_data <- list(
  beta = eqtl_df$BETA,
  varbeta = eqtl_df$SE^2,
  snp = eqtl_df$SNP,
  position = eqtl_df$POS,
  type = 'quant',        # Quantitative trait (expression)
  N = 500,               # eQTL sample size
  sdY = 1                # SD of trait (1 if already normalized)
)

# --- Run colocalization ---
result <- coloc.abf(dataset1 = gwas_data, dataset2 = eqtl_data)

# Posterior probabilities
# PP.H4 > 0.8: Strong evidence for colocalization (shared variant)
# PP.H3 > 0.8: Distinct causal variants at the locus
# PP.H4 between 0.5-0.8: Suggestive but inconclusive
print(result$summary)
```

## Prior Sensitivity

```r
# Default priors: p1 = 1e-4, p2 = 1e-4, p12 = 1e-5
# p1: Prior probability a SNP is associated with trait 1
# p2: Prior probability a SNP is associated with trait 2
# p12: Prior probability a SNP is associated with both traits
#
# Ratio p12/p1 represents prior belief in colocalization
# Default: p12/p1 = 0.1 (10% of trait 1 SNPs also affect trait 2)

result_sensitive <- coloc.abf(
  dataset1 = gwas_data,
  dataset2 = eqtl_data,
  p1 = 1e-4,
  p2 = 1e-4,
  p12 = 5e-6    # More conservative prior for shared association
)

# Sensitivity analysis across prior values
sensitivity(result, 'H4 > 0.8')
```

## Using P-values (No Beta/SE)

```r
# When only p-values are available, use MAF to approximate
gwas_pval <- list(
  pvalues = gwas_df$P,
  MAF = gwas_df$MAF,
  snp = gwas_df$SNP,
  position = gwas_df$POS,
  type = 'cc',
  s = 0.3,
  N = 50000
)

result <- coloc.abf(dataset1 = gwas_pval, dataset2 = eqtl_data)
```

## SuSiE-Coloc (Multiple Causal Variants)

**Goal:** Test colocalization at loci with multiple independent causal signals.

**Approach:** Run SuSiE fine-mapping on each dataset to identify credible sets, then test colocalization between all pairs of credible sets using coloc.susie.

```r
library(coloc)
library(susieR)

# coloc.abf assumes a single causal variant per locus
# SuSiE-coloc handles multiple causal variants

# LD matrix required (correlation matrix from reference panel)
ld_matrix <- as.matrix(read.table('ld_matrix.txt'))

# Run SuSiE on each dataset
susie_gwas <- runsusie(
  list(beta = gwas_df$BETA, varbeta = gwas_df$SE^2,
       snp = gwas_df$SNP, position = gwas_df$POS,
       type = 'cc', s = 0.3, N = 50000, LD = ld_matrix),
  L = 10       # Max number of causal variants to search for
)

susie_eqtl <- runsusie(
  list(beta = eqtl_df$BETA, varbeta = eqtl_df$SE^2,
       snp = eqtl_df$SNP, position = eqtl_df$POS,
       type = 'quant', N = 500, sdY = 1, LD = ld_matrix),
  L = 10
)

# Coloc using SuSiE credible sets
result_susie <- coloc.susie(susie_gwas, susie_eqtl)
print(result_susie$summary)
# Each row tests colocalization between a pair of credible sets
# hit1, hit2: Credible set indices from dataset 1 and 2
```

## HyPrColoc (Multi-Trait)

**Goal:** Test colocalization across three or more traits simultaneously to identify shared causal variant clusters.

**Approach:** Provide beta and SE matrices (SNPs x traits) to hyprcoloc, which clusters traits sharing a causal variant using a branch-and-bound algorithm.

```r
# install.packages('remotes')
# remotes::install_github('jrs95/hyprcoloc')
library(hyprcoloc)

# Test colocalization across multiple traits simultaneously
# Input: matrices of betas and SEs (rows = SNPs, columns = traits)
betas <- cbind(gwas_df$BETA, eqtl1_df$BETA, eqtl2_df$BETA)
ses <- cbind(gwas_df$SE, eqtl1_df$SE, eqtl2_df$SE)
colnames(betas) <- colnames(ses) <- c('GWAS', 'eQTL_gene1', 'eQTL_gene2')
rownames(betas) <- rownames(ses) <- gwas_df$SNP

result_hypr <- hyprcoloc(
  effect.est = betas,
  effect.se = ses,
  trait.names = colnames(betas),
  snp.id = rownames(betas)
)

# Output: clusters of traits sharing a causal variant
print(result_hypr$results)
```

## Input Preparation

```r
# --- Extract a locus (1 Mb window around lead SNP) ---
extract_locus <- function(sumstats, lead_snp_pos, chr, window = 500000) {
  locus <- sumstats[sumstats$CHR == chr &
                    sumstats$POS >= (lead_snp_pos - window) &
                    sumstats$POS <= (lead_snp_pos + window), ]
  locus[order(locus$POS), ]
}

# --- Generate LD matrix from plink ---
# plink --bfile ref_panel --chr 6 --from-bp 30000000 --to-bp 31000000 \
#   --r square --out ld_matrix
# Read into R:
ld <- as.matrix(read.table('ld_matrix.ld'))
```

## Visualization

```r
library(ggplot2)

plot_coloc_locus <- function(gwas_df, eqtl_df, result) {
  pp4 <- round(result$summary['PP.H4.abf'], 3)

  p1 <- ggplot(gwas_df, aes(x = POS / 1e6, y = -log10(P))) +
    geom_point(alpha = 0.6) +
    labs(x = 'Position (Mb)', y = '-log10(P)', title = paste('GWAS | PP.H4 =', pp4)) +
    theme_minimal()

  p2 <- ggplot(eqtl_df, aes(x = POS / 1e6, y = -log10(P))) +
    geom_point(alpha = 0.6, color = 'steelblue') +
    labs(x = 'Position (Mb)', y = '-log10(P)', title = 'eQTL') +
    theme_minimal()

  library(patchwork)
  p1 / p2
}
```

## LocusCompare Plot

```r
# LocusCompare: scatter of -log10(P) for GWAS vs eQTL at shared SNPs
plot_locuscompare <- function(gwas_df, eqtl_df) {
  merged <- merge(
    gwas_df[, c('SNP', 'P')],
    eqtl_df[, c('SNP', 'P')],
    by = 'SNP', suffixes = c('.gwas', '.eqtl')
  )

  ggplot(merged, aes(x = -log10(P.gwas), y = -log10(P.eqtl))) +
    geom_point(alpha = 0.5) +
    geom_smooth(method = 'lm', se = FALSE, linetype = 'dashed', color = 'grey50') +
    labs(x = '-log10(P) GWAS', y = '-log10(P) eQTL', title = 'LocusCompare') +
    theme_minimal()
}
```

## Decision Framework

```
PP.H4 > 0.8:  Strong colocalization -- traits share a causal variant
PP.H3 > 0.8:  Distinct causal variants -- LD-driven overlap, not shared causality
PP.H4 0.5-0.8: Suggestive -- increase sample size, try SuSiE-coloc
PP.H0/H1/H2 dominant: Insufficient signal at this locus
```

Common pitfalls:
- Small eQTL sample sizes reduce power (N < 200 is problematic)
- LD can inflate PP.H3 when two nearby causal variants exist -- use SuSiE-coloc
- Always check that both traits have significant signals at the locus before running coloc

## Related Skills

- mendelian-randomization - Test causal effects using genetic instruments
- fine-mapping - Identify causal variants and credible sets
- population-genetics/linkage-disequilibrium - LD reference panels for SuSiE-coloc
- differential-expression/deseq2-basics - Generate eQTL data for colocalization
