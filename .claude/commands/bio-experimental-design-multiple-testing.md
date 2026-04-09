# bio-experimental-design-multiple-testing

> Applies multiple testing correction methods including FDR, Bonferroni, and q-value for genomics data. Use when filtering differential expression results, setting significance thresholds, or choosing between correction methods for different study designs.

**Available tools:** Read, Bash

# Multiple Testing Correction

## The Problem

Testing 20,000 genes at p < 0.05 yields ~1,000 false positives by chance. Correction is essential.

## Common Methods

### Bonferroni (Most Conservative)

```r
# Strict family-wise error rate control
p_adj <- p.adjust(pvalues, method = 'bonferroni')
# Threshold: alpha / n_tests
# Use for: small gene sets, confirmatory studies
```

### Benjamini-Hochberg FDR (Standard)

```r
# Controls false discovery rate
p_adj <- p.adjust(pvalues, method = 'BH')
# Most common for genomics
# FDR 0.05 = expect 5% of significant results to be false
```

### q-value (Recommended for Large-Scale)

```r
library(qvalue)
qobj <- qvalue(pvalues)
qvalues <- qobj$qvalues
pi0 <- qobj$pi0  # Estimated proportion of true nulls

# q-value directly estimates FDR for each gene
# More powerful than BH when many true positives exist
```

## Method Selection Guide

| Scenario | Recommended Method | Threshold |
|----------|-------------------|-----------|
| Genome-wide DE | BH or q-value | FDR < 0.05 |
| Candidate genes | Bonferroni | p < 0.05/n |
| Exploratory | BH | FDR < 0.10 |
| Validation study | Bonferroni | p < 0.05/n |
| GWAS | Bonferroni | p < 5e-8 |

## Python Equivalent

```python
from statsmodels.stats.multitest import multipletests

# Benjamini-Hochberg
rejected, pvals_corrected, _, _ = multipletests(pvalues, method='fdr_bh')

# Bonferroni
rejected, pvals_corrected, _, _ = multipletests(pvalues, method='bonferroni')
```

## Interpreting Results

- **FDR 0.05**: Among genes called significant, ~5% are false positives
- **FDR 0.01**: More stringent, fewer false positives but more false negatives
- **padj vs qvalue**: Both estimate FDR; q-value is slightly more powerful

## Related Skills

- differential-expression/de-results - Applying corrections to DE output
- population-genetics/association-testing - GWAS significance thresholds
- pathway-analysis/go-enrichment - Correcting enrichment p-values
