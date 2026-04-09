# bio-proteomics-differential-abundance

> Statistical testing for differentially abundant proteins between conditions. Covers limma and MSstats workflows with multiple testing correction. Use when identifying proteins with significant abundance changes between experimental groups.

## Version Compatibility

Reference examples tested with: R stats (base), ggplot2 3.5+, limma 3.58+, numpy 1.26+, pandas 2.2+, scipy 1.12+, statsmodels 0.14+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Differential Protein Abundance

**"Find differentially abundant proteins between my conditions"** → Perform statistical testing on quantified protein intensities to identify proteins with significant abundance changes between experimental groups.
- R: `MSstats::groupComparison()` for feature-level mixed models
- R: `limma::eBayes()` for empirical Bayes moderated t-tests on protein-level data
- Python: `scipy.stats.ttest_ind()` with `statsmodels` FDR correction

## MSstats Group Comparison (R stats (base)+)

**Goal:** Identify differentially abundant proteins between experimental conditions using feature-level mixed models or moderated t-tests.

**Approach:** Define contrast matrices for pairwise comparisons, run MSstats groupComparison (or limma eBayes for protein-level data), then filter results by adjusted p-value and log2 fold change thresholds.

```r
library(MSstats)

# After dataProcess()
comparison_matrix <- matrix(c(1, -1, 0, 0,
                               1, 0, -1, 0,
                               0, 1, -1, 0),
                             nrow = 3, byrow = TRUE)
rownames(comparison_matrix) <- c('Treatment1-Control', 'Treatment2-Control', 'Treatment1-Treatment2')
colnames(comparison_matrix) <- c('Control', 'Treatment1', 'Treatment2', 'Treatment3')

results <- groupComparison(contrast.matrix = comparison_matrix, data = processed)

# Significant proteins
sig_proteins <- results$ComparisonResult[results$ComparisonResult$adj.pvalue < 0.05 &
                                          abs(results$ComparisonResult$log2FC) > 1, ]
```

## limma for Proteomics (R stats (base)+)

```r
library(limma)

# Log2 intensities matrix (proteins x samples)
design <- model.matrix(~ 0 + condition, data = sample_info)
colnames(design) <- levels(sample_info$condition)

fit <- lmFit(protein_matrix, design)

contrast_matrix <- makeContrasts(Treatment - Control, levels = design)
fit2 <- contrasts.fit(fit, contrast_matrix)
fit2 <- eBayes(fit2)

results <- topTable(fit2, number = Inf, adjust.method = 'BH')
sig_results <- results[results$adj.P.Val < 0.05 & abs(results$logFC) > 1, ]
```

## QFeatures/proDA (Modern Alternative)

```r
library(QFeatures)
library(proDA)

# proDA handles missing values probabilistically
fit <- proDA(protein_matrix, design = ~ condition, data = sample_info)

# Test differential abundance
results <- test_diff(fit, contrast = 'conditionTreatment')
results$adj_pval <- p.adjust(results$pval, method = 'BH')
sig_results <- results[results$adj_pval < 0.05 & abs(results$diff) > 1, ]
```

## Python: scipy/statsmodels

```python
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

def differential_test(intensities, group1_cols, group2_cols):
    results = []
    for protein in intensities.index:
        g1 = intensities.loc[protein, group1_cols].dropna()
        g2 = intensities.loc[protein, group2_cols].dropna()

        if len(g1) >= 2 and len(g2) >= 2:
            stat, pval = stats.ttest_ind(g1, g2)
            log2fc = g2.mean() - g1.mean()
            results.append({'protein': protein, 'log2FC': log2fc, 'pvalue': pval})

    df = pd.DataFrame(results)
    df['adj_pvalue'] = multipletests(df['pvalue'], method='fdr_bh')[1]
    return df

# Significance thresholds
sig = results[(results['adj_pvalue'] < 0.05) & (abs(results['log2FC']) > 1)]
```

## Visualization (R stats (base)+)

```r
# Volcano plot
library(ggplot2)

ggplot(results, aes(x = log2FC, y = -log10(adj.P.Val))) +
    geom_point(aes(color = significant), alpha = 0.6) +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed') +
    geom_vline(xintercept = c(-1, 1), linetype = 'dashed') +
    scale_color_manual(values = c('grey', 'red')) +
    theme_minimal()
```

## Related Skills

- quantification - Prepare normalized data for testing
- differential-expression/deseq2-basics - Similar concepts for RNA-seq
- data-visualization/specialized-omics-plots - Volcano plots, MA plots
