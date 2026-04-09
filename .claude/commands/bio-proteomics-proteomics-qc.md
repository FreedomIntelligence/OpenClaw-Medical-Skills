# bio-proteomics-proteomics-qc

> Quality control and assessment for proteomics data. Use when evaluating proteomics data quality before downstream analysis. Covers sample metrics, missing value patterns, replicate correlation, batch effects, and intensity distributions.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+, limma 3.58+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scikit-learn 1.4+, scipy 1.12+, seaborn 0.13+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Proteomics Quality Control

**"Check the quality of my proteomics data"** → Assess data quality through identification rates, missing value patterns, replicate correlation, intensity distributions, and batch effect detection before downstream analysis.
- Python: `pandas` + `matplotlib`/`seaborn` for QC metrics and visualization
- R: `limma::plotMDS()`, correlation heatmaps, CV distributions

## Sample Quality Metrics

```python
import pandas as pd
import numpy as np

def sample_qc_metrics(intensity_matrix):
    '''Calculate per-sample QC metrics'''
    metrics = pd.DataFrame(index=intensity_matrix.columns)
    metrics['n_proteins'] = intensity_matrix.notna().sum()
    metrics['median_intensity'] = intensity_matrix.median()
    metrics['mean_intensity'] = intensity_matrix.mean()
    metrics['cv'] = intensity_matrix.std() / intensity_matrix.mean()
    metrics['missing_pct'] = 100 * intensity_matrix.isna().sum() / len(intensity_matrix)
    return metrics

qc = sample_qc_metrics(log2_intensities)
print(qc)
```

## Replicate Correlation

```python
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

def replicate_correlation(intensity_matrix, sample_groups):
    '''Calculate within-group correlations'''
    corr_matrix = intensity_matrix.corr(method='pearson')

    # Mask for within-group comparisons
    results = []
    for group in sample_groups.unique():
        group_samples = sample_groups[sample_groups == group].index
        for i, s1 in enumerate(group_samples):
            for s2 in group_samples[i+1:]:
                r = corr_matrix.loc[s1, s2]
                results.append({'group': group, 'sample1': s1, 'sample2': s2, 'correlation': r})

    return pd.DataFrame(results)

# Heatmap
sns.clustermap(intensity_matrix.corr(), cmap='RdBu_r', center=0, vmin=-1, vmax=1,
               figsize=(10, 10), annot=False)
plt.savefig('correlation_heatmap.pdf')
```

## Missing Value Patterns

```python
import missingno as msno

def analyze_missing_patterns(intensity_matrix):
    '''Analyze missing value patterns'''
    # Missing value matrix visualization
    msno.matrix(intensity_matrix, figsize=(12, 8))
    plt.savefig('missing_pattern.pdf')

    # Missing by sample
    missing_per_sample = intensity_matrix.isna().sum() / len(intensity_matrix) * 100

    # Missing by protein
    missing_per_protein = intensity_matrix.isna().sum(axis=1) / intensity_matrix.shape[1] * 100

    # Check for systematic patterns
    return {'per_sample': missing_per_sample, 'per_protein': missing_per_protein}
```

## Batch Effect Detection with PCA

**Goal:** Detect batch effects in proteomics data by testing whether processing batches explain significant variance in the principal components.

**Approach:** Impute missing values, scale the intensity matrix, run PCA, then test the association of each top PC with batch labels using one-way ANOVA.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def detect_batch_effects(intensity_matrix, sample_info, batch_col='batch'):
    '''PCA to detect batch effects'''
    # Impute for PCA (temporary)
    imputed = intensity_matrix.fillna(intensity_matrix.median())
    scaled = StandardScaler().fit_transform(imputed.T)

    pca = PCA(n_components=5)
    pcs = pca.fit_transform(scaled)
    pc_df = pd.DataFrame(pcs, columns=[f'PC{i+1}' for i in range(5)], index=intensity_matrix.columns)
    pc_df = pc_df.join(sample_info)

    # Check batch association with PCs
    from scipy.stats import f_oneway
    for pc in ['PC1', 'PC2', 'PC3']:
        groups = [pc_df[pc_df[batch_col] == b][pc] for b in pc_df[batch_col].unique()]
        stat, pval = f_oneway(*groups)
        print(f'{pc} ~ {batch_col}: F={stat:.2f}, p={pval:.4f}')

    return pc_df, pca.explained_variance_ratio_
```

## R: QC with limma

```r
library(limma)
library(ggplot2)

# Intensity distribution
plotDensities(protein_matrix, legend = FALSE, main = 'Intensity Distributions')

# MA plots between samples
for (i in 2:ncol(protein_matrix)) {
    plotMA(protein_matrix[, c(1, i)], main = paste('MA:', colnames(protein_matrix)[i]))
}

# MDS plot (similar to PCA)
plotMDS(protein_matrix, col = as.numeric(sample_info$condition))
```

## Coefficient of Variation

```python
def calculate_cv(intensity_matrix, sample_groups):
    '''Calculate CV within groups'''
    cv_results = []
    for group in sample_groups.unique():
        group_samples = sample_groups[sample_groups == group].index
        group_data = intensity_matrix[group_samples]

        # CV per protein
        cv = group_data.std(axis=1) / group_data.mean(axis=1) * 100
        cv_results.append({'group': group, 'median_cv': cv.median(), 'mean_cv': cv.mean()})

    return pd.DataFrame(cv_results)

# Technical replicates should have CV < 20%
# Biological replicates typically 20-40%
```

## Digestion Efficiency

```python
def check_digestion(evidence_df):
    '''Check digestion efficiency from MaxQuant evidence.txt'''
    # Missed cleavages distribution
    mc_dist = evidence_df['Missed cleavages'].value_counts(normalize=True) * 100
    print('Missed cleavage distribution:')
    print(mc_dist)

    # Good digestion: >80% with 0 missed cleavages
    if mc_dist.get(0, 0) < 80:
        print('Warning: Poor digestion efficiency (<80% fully cleaved)')

    return mc_dist
```

## QC Report Summary

```python
def generate_qc_report(intensity_matrix, sample_info):
    '''Generate comprehensive QC summary'''
    report = {
        'n_samples': intensity_matrix.shape[1],
        'n_proteins': intensity_matrix.shape[0],
        'median_proteins_per_sample': intensity_matrix.notna().sum().median(),
        'overall_missing_pct': 100 * intensity_matrix.isna().sum().sum() / intensity_matrix.size,
        'median_correlation': intensity_matrix.corr().values[np.triu_indices_from(intensity_matrix.corr(), k=1)].mean(),
    }

    # Flags
    report['flags'] = []
    if report['overall_missing_pct'] > 30:
        report['flags'].append('High missing values (>30%)')
    if report['median_correlation'] < 0.9:
        report['flags'].append('Low replicate correlation (<0.9)')

    return report
```

## Related Skills

- data-import - Load data before QC
- quantification - Normalization after QC
- differential-abundance - Analysis after QC passes
- data-visualization/heatmaps-clustering - QC heatmaps
