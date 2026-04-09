# bio-crispr-screens-batch-correction

> Batch effect correction for CRISPR screens. Covers normalization across batches, technical replicate handling, and batch-aware analysis. Use when combining screens from multiple batches or correcting systematic technical variation.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, MAGeCK 0.5+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scikit-learn 1.4+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Batch Correction

**"Correct batch effects in my CRISPR screens"** → Normalize and harmonize sgRNA count data across screen batches to remove systematic technical variation while preserving biological signal.
- Python: `scipy`/`sklearn` for median normalization and batch correction
- CLI: `mageck test` with batch-aware design

## Median Normalization

**Goal:** Remove systematic library-size differences between batches.

**Approach:** Scale each sample within a batch so that sample medians match a global median, correcting for sequencing depth variation.

```python
import numpy as np
import pandas as pd
from scipy import stats

def median_normalize(counts_df, batch_column='batch'):
    '''Normalize counts to median within each batch.'''
    normalized = counts_df.copy()

    guide_columns = [c for c in counts_df.columns if c not in [batch_column, 'gene', 'guide']]

    for batch in counts_df[batch_column].unique():
        batch_mask = counts_df[batch_column] == batch
        batch_data = counts_df.loc[batch_mask, guide_columns]

        sample_medians = batch_data.median(axis=0)
        global_median = sample_medians.median()

        scale_factors = global_median / sample_medians
        normalized.loc[batch_mask, guide_columns] = batch_data * scale_factors

    return normalized

counts_df = pd.read_csv('screen_counts.csv')
normalized = median_normalize(counts_df, 'batch')
```

## Size Factor Normalization

```python
def size_factor_normalize(counts_df, reference='geometric_mean'):
    '''DESeq2-style size factor normalization.'''
    guide_cols = [c for c in counts_df.columns if c.startswith('sample_')]
    counts = counts_df[guide_cols].values

    counts_nonzero = np.where(counts == 0, np.nan, counts)

    if reference == 'geometric_mean':
        log_counts = np.log(counts_nonzero)
        geometric_mean = np.exp(np.nanmean(log_counts, axis=1))
    else:
        geometric_mean = counts_nonzero.mean(axis=1)

    ratios = counts_nonzero / geometric_mean[:, np.newaxis]
    size_factors = np.nanmedian(ratios, axis=0)

    normalized_counts = counts / size_factors
    normalized_df = counts_df.copy()
    normalized_df[guide_cols] = normalized_counts

    return normalized_df, size_factors

normalized, size_factors = size_factor_normalize(counts_df)
print('Size factors:', size_factors)
```

## Quantile Normalization

```python
def quantile_normalize(counts_df, guide_cols=None):
    '''Quantile normalization across samples.'''
    if guide_cols is None:
        guide_cols = [c for c in counts_df.columns if c.startswith('sample_')]

    data = counts_df[guide_cols].values.copy()

    sorted_data = np.sort(data, axis=0)
    mean_values = sorted_data.mean(axis=1)

    ranks = np.argsort(np.argsort(data, axis=0), axis=0)
    normalized = mean_values[ranks]

    result = counts_df.copy()
    result[guide_cols] = normalized

    return result

qn_counts = quantile_normalize(counts_df)
```

## Control-Based Normalization

```python
def normalize_to_controls(counts_df, control_genes, method='median'):
    '''Normalize using non-targeting or negative control guides.'''
    guide_cols = [c for c in counts_df.columns if c.startswith('sample_')]

    is_control = counts_df['gene'].isin(control_genes)
    control_data = counts_df.loc[is_control, guide_cols]

    if method == 'median':
        control_values = control_data.median(axis=0)
    elif method == 'mean':
        control_values = control_data.mean(axis=0)
    elif method == 'sum':
        control_values = control_data.sum(axis=0)

    reference = control_values.median()
    scale_factors = reference / control_values

    normalized = counts_df.copy()
    normalized[guide_cols] = counts_df[guide_cols] * scale_factors

    return normalized, scale_factors

nontargeting = counts_df[counts_df['gene'].str.startswith('NonTargeting')]['gene'].unique()
normalized, factors = normalize_to_controls(counts_df, nontargeting)
```

## Batch Effect Removal with ComBat

**Goal:** Remove batch effects using empirical Bayes adjustment while preserving biological signal.

**Approach:** Log-transform counts, apply pyCombat with a batch vector, and back-transform to count space.

```python
def combat_correction(counts_df, batch_vector, guide_cols=None):
    '''ComBat batch correction for count data.'''
    from combat.pycombat import pycombat

    if guide_cols is None:
        guide_cols = [c for c in counts_df.columns if c.startswith('sample_')]

    data = counts_df[guide_cols].values.T

    log_data = np.log2(data + 1)
    corrected = pycombat(log_data, batch_vector)
    corrected_counts = np.power(2, corrected) - 1
    corrected_counts = np.maximum(corrected_counts, 0)

    result = counts_df.copy()
    result[guide_cols] = corrected_counts.T

    return result

batches = [1, 1, 1, 2, 2, 2]
corrected = combat_correction(counts_df, batches)
```

## Batch-Aware Log-Fold Change

```python
def batch_aware_lfc(counts_df, treatment_cols, control_cols, batch_vector):
    '''Calculate LFC accounting for batch structure.'''
    batches = np.unique(batch_vector)

    lfc_by_batch = []
    for batch in batches:
        batch_treat = [c for c, b in zip(treatment_cols, batch_vector) if b == batch and c in treatment_cols]
        batch_ctrl = [c for c, b in zip(control_cols, batch_vector) if b == batch and c in control_cols]

        if len(batch_treat) == 0 or len(batch_ctrl) == 0:
            continue

        treat_mean = counts_df[batch_treat].mean(axis=1)
        ctrl_mean = counts_df[batch_ctrl].mean(axis=1)

        batch_lfc = np.log2((treat_mean + 1) / (ctrl_mean + 1))
        lfc_by_batch.append(batch_lfc)

    combined_lfc = pd.concat(lfc_by_batch, axis=1).mean(axis=1)
    lfc_var = pd.concat(lfc_by_batch, axis=1).var(axis=1)

    return combined_lfc, lfc_var
```

## Replicate Correlation Check

```python
def check_replicate_correlation(counts_df, sample_cols, replicate_groups):
    '''Check correlation between replicates.'''
    correlations = []

    for group, replicates in replicate_groups.items():
        if len(replicates) < 2:
            continue

        for i in range(len(replicates)):
            for j in range(i+1, len(replicates)):
                r1, r2 = replicates[i], replicates[j]
                if r1 in sample_cols and r2 in sample_cols:
                    log_r1 = np.log2(counts_df[r1] + 1)
                    log_r2 = np.log2(counts_df[r2] + 1)

                    corr, pval = stats.pearsonr(log_r1, log_r2)
                    correlations.append({
                        'group': group,
                        'rep1': r1,
                        'rep2': r2,
                        'pearson_r': corr,
                        'pvalue': pval
                    })

    return pd.DataFrame(correlations)

replicate_groups = {
    'treatment_batch1': ['sample_1', 'sample_2'],
    'treatment_batch2': ['sample_4', 'sample_5'],
    'control_batch1': ['sample_3'],
    'control_batch2': ['sample_6']
}

corr_df = check_replicate_correlation(counts_df, counts_df.columns[3:], replicate_groups)
print(corr_df)
```

## Batch QC Metrics

**Goal:** Quantify batch effect magnitude to determine whether correction is needed.

**Approach:** Run PCA on log-transformed counts, compute between-batch vs within-batch variance ratio, and assess whether batch structure dominates the first principal components.

```python
def batch_qc_metrics(counts_df, batch_vector, sample_cols):
    '''Calculate batch-related QC metrics.'''
    from sklearn.decomposition import PCA
    from scipy.spatial.distance import pdist

    log_counts = np.log2(counts_df[sample_cols].values.T + 1)

    pca = PCA(n_components=min(5, len(sample_cols)))
    pcs = pca.fit_transform(log_counts)

    batch_labels = np.array(batch_vector)
    unique_batches = np.unique(batch_labels)

    if len(unique_batches) > 1:
        batch_means = [pcs[batch_labels == b].mean(axis=0) for b in unique_batches]
        batch_separation = np.mean(pdist(batch_means))

        within_batch_var = np.mean([pcs[batch_labels == b].var() for b in unique_batches])
        between_batch_var = np.var(batch_means, axis=0).sum()

        batch_effect_ratio = between_batch_var / (within_batch_var + 1e-10)
    else:
        batch_separation = 0
        batch_effect_ratio = 0

    return {
        'batch_separation': batch_separation,
        'batch_effect_ratio': batch_effect_ratio,
        'pca_variance_explained': pca.explained_variance_ratio_,
        'n_batches': len(unique_batches)
    }

qc = batch_qc_metrics(counts_df, [1,1,1,2,2,2], sample_cols)
print(f"Batch effect ratio: {qc['batch_effect_ratio']:.2f}")
```

## Visualization

```python
import matplotlib.pyplot as plt

def plot_batch_effect(counts_df, batch_vector, sample_cols, output_file):
    '''Visualize batch effects with PCA.'''
    from sklearn.decomposition import PCA

    log_counts = np.log2(counts_df[sample_cols].values.T + 1)

    pca = PCA(n_components=2)
    pcs = pca.fit_transform(log_counts)

    fig, ax = plt.subplots(figsize=(8, 6))

    for batch in np.unique(batch_vector):
        mask = np.array(batch_vector) == batch
        ax.scatter(pcs[mask, 0], pcs[mask, 1], label=f'Batch {batch}', s=100)

    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
    ax.legend()
    ax.set_title('PCA - Batch Effects')

    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()

plot_batch_effect(counts_df, [1,1,1,2,2,2], sample_cols, 'batch_pca.png')
```

## Related Skills

- mageck-analysis - Batch-aware MAGeCK analysis
- screen-qc - Quality control before correction
- hit-calling - Analysis after batch correction
- library-design - Control guide design
