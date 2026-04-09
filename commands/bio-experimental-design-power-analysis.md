# bio-experimental-design-power-analysis

> Calculates statistical power and minimum sample sizes for RNA-seq, ATAC-seq, and other sequencing experiments. Use when planning experiments, determining how many replicates are needed, or assessing whether a study is adequately powered to detect expected effect sizes.

**Available tools:** Read, Bash

# Power Analysis for Sequencing Experiments

## Core Concept

Power = probability of detecting a true effect. Underpowered studies waste resources; overpowered studies are inefficient.

## RNA-seq Power Analysis

```r
library(RNASeqPower)

# Typical parameters
# - depth: sequencing depth per sample (reads/gene)
# - cv: biological coefficient of variation (0.1-0.4 typical)
# - effect: fold change to detect (1.5 = 50% change)
# - alpha: significance level (0.05 standard)

# Calculate power for given sample size
rnapower(depth = 20, n = 3, cv = 0.4, effect = 2, alpha = 0.05)

# Calculate required samples for target power
rnapower(depth = 20, cv = 0.4, effect = 2, alpha = 0.05, power = 0.8)
```

## CV Guidelines

| Experiment Type | Typical CV | Notes |
|-----------------|------------|-------|
| Cell lines | 0.1-0.2 | Low variability |
| Inbred mice | 0.2-0.3 | Moderate |
| Human samples | 0.3-0.5 | High variability |
| Primary cells | 0.3-0.4 | Donor-dependent |

## ATAC-seq Power (ssizeRNA)

```r
library(ssizeRNA)

# For differential accessibility
size.zhao(m = 10000, m1 = 500, fc = 2, fdr = 0.05, power = 0.8,
          mu = 10, disp = 0.1)
```

## Quick Reference

| Effect Size | Recommended n (CV=0.4) |
|-------------|------------------------|
| 4-fold | 3 per group |
| 2-fold | 5-6 per group |
| 1.5-fold | 10-12 per group |
| 1.25-fold | 20+ per group |

## Related Skills

- experimental-design/sample-size - Detailed sample size calculations
- experimental-design/batch-design - Accounting for batch effects in design
- differential-expression/deseq2-basics - Running the actual DE analysis
