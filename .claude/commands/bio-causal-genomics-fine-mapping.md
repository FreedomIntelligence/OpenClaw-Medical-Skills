# bio-causal-genomics-fine-mapping

> Identify likely causal variants within GWAS loci using SuSiE for sum of single effects regression and FINEMAP for shotgun stochastic search. Computes posterior inclusion probabilities and credible sets to prioritize variants for functional follow-up. Use when narrowing GWAS association signals to candidate causal variants or building credible sets for functional validation.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Fine-Mapping

**"Narrow my GWAS locus to the likely causal variant"** → Compute posterior inclusion probabilities (PIPs) for each variant and construct credible sets containing the causal variant at a specified confidence level, accounting for LD and multiple causal signals.
- R: `susieR::susie_rss()` for SuSiE fine-mapping from summary statistics
- CLI: `finemap --sss` for shotgun stochastic search

## Overview

Fine-mapping narrows GWAS association signals to identify likely causal variants. Key outputs:

- **PIP** (Posterior Inclusion Probability) - Probability each variant is causal (0-1)
- **Credible set** - Minimal set of variants containing the causal variant at a given confidence level (e.g., 95%)
- **L** - Number of independent causal signals at the locus

## SuSiE (Sum of Single Effects)

**Goal:** Fine-map a GWAS locus to identify likely causal variants and credible sets from individual-level data.

**Approach:** Fit SuSiE's sum-of-single-effects model on the genotype matrix, then extract 95% credible sets (each containing the causal variant) and per-variant posterior inclusion probabilities.

```r
library(susieR)

# --- From individual-level data ---
# X: genotype matrix (n x p), standardized
# Y: phenotype vector (n x 1)
# L: max number of causal variants (10 is a reasonable default)
fit <- susie(X, Y, L = 10)

# Extract credible sets
# 95% credible sets: each set contains the causal variant with >= 95% probability
# coverage: minimum posterior mass for the credible set (default 0.95)
# min_abs_corr: minimum purity (correlation among variants in set; > 0.5 is good)
cs <- fit$sets$cs
cat('Number of credible sets:', length(cs), '\n')

# Credible set purity (minimum absolute correlation within set)
# Purity > 0.5: Well-resolved signal
# Purity < 0.5: Signal may be confounded by LD
purity <- fit$sets$purity
print(purity)

# PIPs for all variants
pip <- fit$pip
top_variants <- order(-pip)[1:10]
cat('\nTop 10 variants by PIP:\n')
for (i in top_variants) {
  cat(sprintf('  Variant %d: PIP = %.4f\n', i, pip[i]))
}
```

## SuSiE with Summary Statistics (susie_rss)

**Goal:** Fine-map a GWAS locus using summary statistics and an LD reference matrix (no individual-level data needed).

**Approach:** Compute Z-scores from beta/SE, provide a matched-ancestry LD correlation matrix, and run susie_rss to identify credible sets and PIPs.

```r
library(susieR)

# --- Most common usage: GWAS summary statistics + LD matrix ---
# z: Z-scores (beta / se) for each variant
# R: LD correlation matrix (from matched ancestry reference)
# n: Sample size
# L: Max causal variants

z_scores <- gwas_df$BETA / gwas_df$SE
ld_matrix <- as.matrix(read.table('ld_matrix.ld'))

# Ensure SNP order matches between z-scores and LD matrix
stopifnot(nrow(ld_matrix) == length(z_scores))

fit <- susie_rss(z = z_scores, R = ld_matrix, n = 50000, L = 10)

# Credible sets
cs <- fit$sets$cs
for (i in seq_along(cs)) {
  cat(sprintf('Credible set %d: %d variants, purity = %.3f\n',
              i, length(cs[[i]]), fit$sets$purity[i, 1]))
  cat('  Variants:', paste(gwas_df$SNP[cs[[i]]], collapse = ', '), '\n')
}

# PIPs
gwas_df$PIP <- fit$pip
top_pip <- gwas_df[order(-gwas_df$PIP), ][1:20, c('SNP', 'PIP', 'P')]
print(top_pip)
```

## Choosing L (Number of Causal Variants)

```r
# L = max number of causal signals SuSiE will search for
# Too low: Misses real signals
# Too high: Increases computation but rarely hurts results (SuSiE prunes excess)
#
# Guidelines:
# L = 1: Single causal variant expected
# L = 5: Most GWAS loci
# L = 10: Default, works well for most cases
# L = 20: Very complex loci (e.g., HLA region)

# Compare fits with different L
fit_l5 <- susie_rss(z = z_scores, R = ld_matrix, n = 50000, L = 5)
fit_l10 <- susie_rss(z = z_scores, R = ld_matrix, n = 50000, L = 10)

cat('L=5 credible sets:', length(fit_l5$sets$cs), '\n')
cat('L=10 credible sets:', length(fit_l10$sets$cs), '\n')
```

## LD Reference Panel

```bash
# Generate LD matrix from 1000 Genomes with plink
# Must match ancestry of GWAS sample

# Extract region
plink --bfile 1000G_EUR \
  --chr 6 --from-bp 30000000 --to-bp 31000000 \
  --make-bed --out locus_ref

# Compute correlation matrix
plink --bfile locus_ref \
  --r square --out ld_matrix

# Filter to GWAS SNPs only
plink --bfile locus_ref \
  --extract gwas_snps.txt \
  --r square --out ld_matrix_filtered
```

```r
# Read LD matrix into R
ld <- as.matrix(read.table('ld_matrix.ld'))

# Ensure positive semi-definite (numerical issues can violate this)
# Add small ridge to diagonal if needed
eigenvalues <- eigen(ld, only.values = TRUE)$values
if (any(eigenvalues < 0)) {
  ld <- ld + diag(abs(min(eigenvalues)) + 1e-6, nrow(ld))
}
```

## FINEMAP

**Goal:** Fine-map a locus using an alternative shotgun stochastic search algorithm.

**Approach:** Prepare .z (summary stats), .ld (LD matrix), and .master (config) files, then run FINEMAP to compute per-variant PIPs and causal configurations.

```bash
# FINEMAP: alternative fine-mapping tool using shotgun stochastic search
# Download from http://www.christianbenner.com/

# Required input files:
# 1. .z file: SNP, chromosome, position, allele1, allele2, MAF, beta, se
# 2. .ld file: LD matrix (space-separated, no header)
# 3. .master file: configuration

# Create master file
cat > master.txt << 'EOF'
z;ld;snp;config;cred;log;n_samples
locus.z;locus.ld;locus.snp;locus.config;locus.cred;locus.log;50000
EOF

# Run FINEMAP
finemap --sss --in-files master.txt --n-causal-snps 5
```

```r
# Parse FINEMAP output
finemap_snp <- read.table('locus.snp', header = TRUE)
finemap_snp <- finemap_snp[order(-finemap_snp$prob), ]

cat('Top variants by PIP (FINEMAP):\n')
print(head(finemap_snp[, c('rsid', 'prob', 'log10bf')], 10))

# Credible sets from .cred file
finemap_cred <- read.table('locus.cred', header = TRUE)
```

## Functional Annotation with PolyFun

```r
# PolyFun integrates functional annotations to improve fine-mapping
# Uses LD-score regression to estimate per-SNP heritability
# Provides functionally-informed priors for SuSiE

# After running PolyFun (Python), read prior variances
polyfun_priors <- read.table('polyfun_output.txt', header = TRUE)

# Use priors in SuSiE
fit_informed <- susie_rss(
  z = z_scores, R = ld_matrix, n = 50000, L = 10,
  prior_variance = polyfun_priors$prior_var
)
```

## Visualization

```r
library(ggplot2)

plot_pip <- function(gwas_df, credible_sets = NULL) {
  p <- ggplot(gwas_df, aes(x = POS / 1e6, y = PIP)) +
    geom_point(alpha = 0.5, size = 1.5) +
    geom_hline(yintercept = 0.5, linetype = 'dashed', color = 'orange', alpha = 0.5) +
    geom_hline(yintercept = 0.95, linetype = 'dashed', color = 'red', alpha = 0.5) +
    labs(x = 'Position (Mb)', y = 'Posterior Inclusion Probability',
         title = 'Fine-Mapping Results') +
    theme_minimal()

  if (!is.null(credible_sets)) {
    cs_snps <- unlist(credible_sets)
    gwas_df$in_cs <- seq_len(nrow(gwas_df)) %in% cs_snps
    p <- ggplot(gwas_df, aes(x = POS / 1e6, y = PIP, color = in_cs)) +
      geom_point(alpha = 0.6, size = 1.5) +
      scale_color_manual(values = c('grey60', 'red'), labels = c('No', 'Yes'), name = 'In credible set') +
      geom_hline(yintercept = 0.5, linetype = 'dashed', alpha = 0.3) +
      labs(x = 'Position (Mb)', y = 'PIP', title = 'Fine-Mapping with Credible Sets') +
      theme_minimal()
  }

  p
}

# Combined GWAS + PIP plot
plot_gwas_pip <- function(gwas_df) {
  library(patchwork)

  p_gwas <- ggplot(gwas_df, aes(x = POS / 1e6, y = -log10(P))) +
    geom_point(alpha = 0.4, size = 1) +
    geom_hline(yintercept = -log10(5e-8), linetype = 'dashed', color = 'red', alpha = 0.3) +
    labs(x = NULL, y = '-log10(P)', title = 'GWAS') +
    theme_minimal() + theme(axis.text.x = element_blank())

  p_pip <- ggplot(gwas_df, aes(x = POS / 1e6, y = PIP)) +
    geom_point(alpha = 0.4, size = 1, color = 'steelblue') +
    labs(x = 'Position (Mb)', y = 'PIP', title = 'Fine-Mapping') +
    theme_minimal()

  p_gwas / p_pip
}
```

## Related Skills

- colocalization-analysis - SuSiE-coloc uses fine-mapping credible sets
- mendelian-randomization - Fine-map instrument loci for causal variants
- population-genetics/linkage-disequilibrium - LD matrices for fine-mapping
- variant-calling/variant-annotation - Annotate fine-mapped variants
