# data-stats-analysis

> Perform statistical tests, hypothesis testing, correlation analysis, and multiple testing corrections using scipy and statsmodels. Works with ANY LLM provider (GPT, Gemini, Claude, etc.).

# Statistical Analysis (Universal)

## Overview
This skill enables you to perform rigorous statistical analyses including t-tests, ANOVA, correlation analysis, hypothesis testing, and multiple testing corrections. Unlike cloud-hosted solutions, this skill uses standard Python statistical libraries (**scipy**, **statsmodels**, **numpy**) and executes **locally** in your environment, making it compatible with **ALL LLM providers** including GPT, Gemini, Claude, DeepSeek, and Qwen.

## When to Use This Skill
- Compare means between groups (t-tests, ANOVA)
- Test for correlations between variables
- Perform hypothesis testing with p-value calculation
- Apply multiple testing corrections (FDR, Bonferroni)
- Calculate statistical summaries and confidence intervals
- Test for normality and distribution fitting
- Perform non-parametric tests (Mann-Whitney, Kruskal-Wallis)

## How to Use

### Step 1: Import Required Libraries
```python
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import ttest_ind, mannwhitneyu, pearsonr, spearmanr
from scipy.stats import f_oneway, kruskal, chi2_contingency
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportions_ztest
import warnings
warnings.filterwarnings('ignore')
```

### Step 2: Two-Sample t-Test
```python
# Compare means between two groups
# group1, group2: arrays of numeric values

# Perform independent t-test
t_statistic, p_value = ttest_ind(group1, group2)

print(f"t-statistic: {t_statistic:.4f}")
print(f"p-value: {p_value:.4e}")

if p_value < 0.05:
    print("✅ Significant difference between groups (p < 0.05)")
else:
    print("❌ No significant difference (p >= 0.05)")

# With equal variance assumption check
# Levene's test for equal variances
_, levene_p = stats.levene(group1, group2)
if levene_p < 0.05:
    # Use Welch's t-test (unequal variances)
    t_stat, p_val = ttest_ind(group1, group2, equal_var=False)
    print(f"Welch's t-test p-value: {p_val:.4e}")
else:
    print("Equal variances assumed")
```

### Step 3: One-Way ANOVA
```python
# Compare means across multiple groups
# groups: list of arrays, e.g., [group1, group2, group3]

# Perform one-way ANOVA
f_statistic, p_value = f_oneway(*groups)

print(f"F-statistic: {f_statistic:.4f}")
print(f"p-value: {p_value:.4e}")

if p_value < 0.05:
    print("✅ Significant difference between groups (p < 0.05)")
    print("Note: Use post-hoc tests to identify which groups differ")
else:
    print("❌ No significant difference between groups")

# Post-hoc pairwise t-tests with Bonferroni correction
from itertools import combinations

group_names = ['Group A', 'Group B', 'Group C']
pairwise_results = []

for (name1, data1), (name2, data2) in combinations(zip(group_names, groups), 2):
    _, p = ttest_ind(data1, data2)
    pairwise_results.append({
        'comparison': f'{name1} vs {name2}',
        'p_value': p
    })

# Apply Bonferroni correction
pairwise_df = pd.DataFrame(pairwise_results)
n_tests = len(pairwise_df)
pairwise_df['p_adjusted'] = pairwise_df['p_value'] * n_tests
pairwise_df['p_adjusted'] = pairwise_df['p_adjusted'].clip(upper=1.0)

print("\nPairwise Comparisons (Bonferroni-corrected):")
print(pairwise_df)
```

### Step 4: Correlation Analysis
```python
# Pearson correlation (linear relationships)
r_pearson, p_pearson = pearsonr(variable1, variable2)

print(f"Pearson correlation: r = {r_pearson:.4f}, p = {p_pearson:.4e}")

# Spearman correlation (monotonic relationships, robust to outliers)
r_spearman, p_spearman = spearmanr(variable1, variable2)

print(f"Spearman correlation: ρ = {r_spearman:.4f}, p = {p_spearman:.4e}")

# Interpretation
if abs(r_pearson) < 0.3:
    strength = "weak"
elif abs(r_pearson) < 0.7:
    strength = "moderate"
else:
    strength = "strong"

direction = "positive" if r_pearson > 0 else "negative"
print(f"Interpretation: {strength} {direction} correlation")

if p_pearson < 0.05:
    print("✅ Statistically significant (p < 0.05)")
else:
    print("❌ Not statistically significant")
```

### Step 5: Multiple Testing Correction
```python
# Scenario: Testing 1000 genes for differential expression
# p_values: array of p-values from individual tests

# Method 1: Benjamini-Hochberg FDR correction (recommended)
reject_fdr, p_adjusted_fdr, _, _ = multipletests(p_values, alpha=0.05, method='fdr_bh')

# Method 2: Bonferroni correction (more conservative)
reject_bonf, p_adjusted_bonf, _, _ = multipletests(p_values, alpha=0.05, method='bonferroni')

# Create results DataFrame
results_df = pd.DataFrame({
    'gene': gene_names,
    'p_value': p_values,
    'q_value_fdr': p_adjusted_fdr,
    'p_adjusted_bonferroni': p_adjusted_bonf,
    'significant_fdr': reject_fdr,
    'significant_bonf': reject_bonf
})

# Summary
print(f"Original significant (p < 0.05): {(p_values < 0.05).sum()}")
print(f"Significant after FDR correction: {reject_fdr.sum()}")
print(f"Significant after Bonferroni correction: {reject_bonf.sum()}")

# Save results
results_df.to_csv('statistical_results.csv', index=False)
print("✅ Results saved to: statistical_results.csv")
```

### Step 6: Non-Parametric Tests
```python
# Use when data is not normally distributed

# Mann-Whitney U test (alternative to t-test)
u_statistic, p_value_mw = mannwhitneyu(group1, group2, alternative='two-sided')

print(f"Mann-Whitney U test:")
print(f"U-statistic: {u_statistic:.4f}")
print(f"p-value: {p_value_mw:.4e}")

# Kruskal-Wallis H test (alternative to ANOVA)
h_statistic, p_value_kw = kruskal(*groups)

print(f"\nKruskal-Wallis H test:")
print(f"H-statistic: {h_statistic:.4f}")
print(f"p-value: {p_value_kw:.4e}")
```

## Advanced Features

### Normality Testing
```python
from scipy.stats import shapiro, normaltest, kstest

# Test if data follows normal distribution

# Shapiro-Wilk test (best for n < 5000)
stat_sw, p_sw = shapiro(data)
print(f"Shapiro-Wilk test: W={stat_sw:.4f}, p={p_sw:.4e}")

# D'Agostino-Pearson test
stat_dp, p_dp = normaltest(data)
print(f"D'Agostino-Pearson test: stat={stat_dp:.4f}, p={p_dp:.4e}")

# Interpretation
if p_sw < 0.05:
    print("❌ Data does NOT follow normal distribution (p < 0.05)")
    print("→ Recommendation: Use non-parametric tests (Mann-Whitney, Kruskal-Wallis)")
else:
    print("✅ Data appears normally distributed (p >= 0.05)")
    print("→ OK to use parametric tests (t-test, ANOVA)")
```

### Chi-Square Test for Contingency Tables
```python
# Test independence between categorical variables
# contingency_table: 2D array (rows=categories1, columns=categories2)

# Example: Cell type distribution across conditions
contingency_table = np.array([
    [50, 30, 20],  # Condition A: T cells, B cells, NK cells
    [40, 45, 15],  # Condition B
    [35, 25, 40]   # Condition C
])

chi2, p_value, dof, expected = chi2_contingency(contingency_table)

print(f"Chi-square statistic: {chi2:.4f}")
print(f"p-value: {p_value:.4e}")
print(f"Degrees of freedom: {dof}")
print(f"\nExpected frequencies:\n{expected}")

if p_value < 0.05:
    print("✅ Significant association between variables (p < 0.05)")
else:
    print("❌ No significant association")
```

### Confidence Intervals
```python
from scipy.stats import t as t_dist

def calculate_confidence_interval(data, confidence=0.95):
    """Calculate confidence interval for mean"""
    n = len(data)
    mean = np.mean(data)
    std_err = stats.sem(data)  # Standard error of mean

    # t-distribution critical value
    t_crit = t_dist.ppf((1 + confidence) / 2, df=n-1)

    margin_error = t_crit * std_err
    ci_lower = mean - margin_error
    ci_upper = mean + margin_error

    return mean, ci_lower, ci_upper

# Usage
mean, ci_low, ci_high = calculate_confidence_interval(data, confidence=0.95)

print(f"Mean: {mean:.4f}")
print(f"95% CI: [{ci_low:.4f}, {ci_high:.4f}]")
```

### Effect Size Calculation
```python
def cohens_d(group1, group2):
    """Calculate Cohen's d effect size"""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))

    # Cohen's d
    d = (np.mean(group1) - np.mean(group2)) / pooled_std

    return d

# Usage
effect_size = cohens_d(group1, group2)
print(f"Cohen's d: {effect_size:.4f}")

# Interpretation
if abs(effect_size) < 0.2:
    print("Effect size: negligible")
elif abs(effect_size) < 0.5:
    print("Effect size: small")
elif abs(effect_size) < 0.8:
    print("Effect size: medium")
else:
    print("Effect size: large")
```

## Common Use Cases

### Differential Gene Expression Statistical Testing
```python
# Compare gene expression between two conditions
# gene_expression_df: rows=genes, columns=samples
# condition_labels: array indicating which condition each sample belongs to

results = []

for gene in gene_expression_df.index:
    # Get expression values for each condition
    cond1_expr = gene_expression_df.loc[gene, condition_labels == 'Condition1']
    cond2_expr = gene_expression_df.loc[gene, condition_labels == 'Condition2']

    # t-test
    t_stat, p_val = ttest_ind(cond1_expr, cond2_expr)

    # Log2 fold change
    log2fc = np.log2(cond2_expr.mean() / cond1_expr.mean())

    results.append({
        'gene': gene,
        'log2FC': log2fc,
        'p_value': p_val,
        'mean_cond1': cond1_expr.mean(),
        'mean_cond2': cond2_expr.mean()
    })

deg_results = pd.DataFrame(results)

# Apply FDR correction
_, deg_results['q_value'], _, _ = multipletests(
    deg_results['p_value'],
    alpha=0.05,
    method='fdr_bh'
)

# Filter significant genes
significant_genes = deg_results[
    (deg_results['q_value'] < 0.05) &
    (abs(deg_results['log2FC']) > 1)
]

print(f"✅ Identified {len(significant_genes)} differentially expressed genes")
print(f"   - Upregulated: {(significant_genes['log2FC'] > 1).sum()}")
print(f"   - Downregulated: {(significant_genes['log2FC'] < -1).sum()}")

# Save
significant_genes.to_csv('deg_results.csv', index=False)
```

### Cluster Enrichment Analysis
```python
# Test if a cell type is enriched in a specific cluster
# total_cells: total number of cells
# cluster_cells: number of cells in cluster
# celltype_total: total cells of this type
# celltype_in_cluster: cells of this type in cluster

from scipy.stats import fisher_exact

# Create contingency table
contingency = [
    [celltype_in_cluster, cluster_cells - celltype_in_cluster],  # In cluster
    [celltype_total - celltype_in_cluster, total_cells - cluster_cells - (celltype_total - celltype_in_cluster)]  # Not in cluster
]

odds_ratio, p_value = fisher_exact(contingency, alternative='greater')

print(f"Odds ratio: {odds_ratio:.4f}")
print(f"p-value: {p_value:.4e}")

if p_value < 0.05 and odds_ratio > 1:
    print(f"✅ Cell type is significantly ENRICHED in cluster (p < 0.05)")
elif p_value < 0.05 and odds_ratio < 1:
    print(f"⚠️ Cell type is significantly DEPLETED in cluster (p < 0.05)")
else:
    print("❌ No significant enrichment/depletion")
```

### Batch Effect Detection
```python
# Test if there's a batch effect using ANOVA
# gene_expression: DataFrame with genes as rows, samples as columns
# batch_labels: array indicating batch for each sample

batch_effect_results = []

for gene in gene_expression.index:
    # Get expression values for each batch
    batches = [
        gene_expression.loc[gene, batch_labels == batch]
        for batch in np.unique(batch_labels)
    ]

    # ANOVA test
    f_stat, p_val = f_oneway(*batches)

    batch_effect_results.append({
        'gene': gene,
        'f_statistic': f_stat,
        'p_value': p_val
    })

batch_df = pd.DataFrame(batch_effect_results)

# Apply FDR correction
_, batch_df['q_value'], _, _ = multipletests(batch_df['p_value'], alpha=0.05, method='fdr_bh')

# Count genes with batch effects
genes_with_batch_effect = (batch_df['q_value'] < 0.05).sum()

print(f"Genes with significant batch effect: {genes_with_batch_effect} ({genes_with_batch_effect/len(batch_df)*100:.1f}%)")

if genes_with_batch_effect > len(batch_df) * 0.1:
    print("⚠️ WARNING: Strong batch effect detected (>10% genes affected)")
    print("→ Recommendation: Apply batch correction (ComBat, Harmony, etc.)")
else:
    print("✅ Minimal batch effect")
```

## Best Practices

1. **Check Assumptions**: Always test normality before using parametric tests (t-test, ANOVA)
2. **Multiple Testing**: Apply FDR or Bonferroni correction when testing many hypotheses
3. **Effect Size**: Report effect sizes (Cohen's d) alongside p-values
4. **Sample Size**: Ensure adequate sample size for statistical power
5. **Outliers**: Check for and handle outliers appropriately
6. **Non-Parametric Alternatives**: Use when assumptions are violated (Mann-Whitney instead of t-test)
7. **Report Details**: Always report test used, test statistic, p-value, and correction method
8. **Visualization**: Combine statistical tests with visualizations (box plots, violin plots)

## Troubleshooting

### Issue: "Warning: p-value is very small"
**Solution**: This is normal for highly significant results. Report as p < 0.001 or use scientific notation
```python
if p_value < 0.001:
    print(f"p < 0.001")
else:
    print(f"p = {p_value:.4f}")
```

### Issue: "Division by zero in effect size calculation"
**Solution**: Check for zero variance (all values identical)
```python
if np.std(group1) == 0 or np.std(group2) == 0:
    print("Cannot calculate effect size: zero variance in one or both groups")
else:
    d = cohens_d(group1, group2)
```

### Issue: "Test fails with NaN values"
**Solution**: Remove or impute NaN values before testing
```python
# Remove NaN
group1_clean = group1[~np.isnan(group1)]
group2_clean = group2[~np.isnan(group2)]

# Or filter in DataFrame
df_clean = df.dropna(subset=['column_name'])
```

### Issue: "Insufficient sample size warning"
**Solution**: Minimum sample sizes for reliable tests:
- t-test: n ≥ 30 per group (or ≥ 5 if normally distributed)
- ANOVA: n ≥ 20 per group
- Correlation: n ≥ 30 total

```python
if len(group1) < 30 or len(group2) < 30:
    print("⚠️ Warning: Small sample size. Results may not be reliable.")
    print("Consider using non-parametric tests or collecting more data.")
```

## Technical Notes

- **Libraries**: Uses `scipy.stats` and `statsmodels` (widely supported, stable)
- **Execution**: Runs locally in the agent's sandbox
- **Compatibility**: Works with ALL LLM providers (GPT, Gemini, Claude, DeepSeek, Qwen, etc.)
- **Performance**: Most tests complete in milliseconds; large-scale testing (>10K genes) takes 1-5 seconds
- **Precision**: Uses double-precision floating point (numpy default)
- **Corrections**: FDR (Benjamini-Hochberg) recommended for genomics; Bonferroni for small numbers of tests

## References
- scipy.stats documentation: https://docs.scipy.org/doc/scipy/reference/stats.html
- statsmodels documentation: https://www.statsmodels.org/stable/index.html
- Multiple testing: https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html
- Statistical testing guide: https://docs.scipy.org/doc/scipy/tutorial/stats.html
