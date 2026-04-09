# bio-experimental-design-sample-size

> Estimates required sample sizes for differential expression, ChIP-seq, methylation, and proteomics studies. Use when budgeting experiments, writing grant proposals, or determining minimum replicates needed to achieve statistical significance for expected effect sizes.

**Available tools:** Read, Bash

# Sample Size Estimation

## RNA-seq Sample Size

```r
library(ssizeRNA)

# Estimate sample size for RNA-seq
# m = total genes, m1 = expected DE genes
# fc = fold change, fdr = target FDR
result <- ssizeRNA_single(nGenes = 20000, pi0 = 0.9, m = 200,
                          mu = 10, disp = 0.1, fc = 2,
                          fdr = 0.05, power = 0.8)
result$ssize  # Required n per group
```

## DESeq2-based Estimation

```r
library(DESeq2)

# From pilot data
dds_pilot <- DESeqDataSetFromMatrix(pilot_counts, colData, ~condition)
dds_pilot <- DESeq(dds_pilot)

# Extract dispersion estimates for power calculation
dispersions <- mcols(dds_pilot)$dispGeneEst
median_disp <- median(dispersions, na.rm = TRUE)
# Use median_disp in power calculations
```

## Single-cell Sample Size

```r
library(powsimR)

# Estimate for scRNA-seq
# Accounts for dropout and cell-to-cell variability
params <- estimateParam(pilot_sce)
power <- simulateDE(params, n1 = 100, n2 = 100,
                    p.DE = 0.1, pLFC = 1)
```

## Sample Size by Assay Type

| Assay | Min Recommended | For Small Effects |
|-------|-----------------|-------------------|
| Bulk RNA-seq | 3 | 6-12 |
| scRNA-seq | 3 samples, 1000 cells | 6+ samples |
| ATAC-seq | 2 | 4-6 |
| ChIP-seq | 2 | 3-4 |
| Proteomics | 3 | 6-10 |
| Methylation | 4 | 8-12 |

## Budget Optimization

When resources are limited, prioritize:
1. Biological replicates over technical replicates
2. More samples over deeper sequencing (after ~20M reads for RNA-seq)
3. Balanced designs (equal n per group)

## Related Skills

- experimental-design/power-analysis - Power calculations
- experimental-design/batch-design - Optimal batch assignment
- single-cell/preprocessing - scRNA-seq experimental design
