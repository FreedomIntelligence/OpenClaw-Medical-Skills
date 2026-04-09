# bio-crispr-screens-screen-qc

> Quality control for pooled CRISPR screens. Covers library representation, read distribution, replicate correlation, and essential gene recovery. Use when assessing screen quality before hit calling or diagnosing poor screen performance.

## Version Compatibility

Reference examples tested with: MAGeCK 0.5+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scikit-learn 1.4+, seaborn 0.13+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# CRISPR Screen Quality Control

**"Check the quality of my CRISPR screen"** → Assess screen quality through library representation, Gini index, replicate correlation, and essential gene recovery metrics before hit calling.
- Python: `pandas` + `matplotlib` for QC metrics and diagnostic plots

## Load Count Data

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load MAGeCK count output
counts = pd.read_csv('screen.count.txt', sep='\t', index_col=0)
genes = counts['Gene']
count_matrix = counts.drop('Gene', axis=1)

print(f'sgRNAs: {len(count_matrix)}')
print(f'Genes: {genes.nunique()}')
print(f'Samples: {count_matrix.columns.tolist()}')
```

## Library Representation

**Goal:** Assess whether the sgRNA library is adequately represented across all samples.

**Approach:** Count zero-count and low-count sgRNAs per sample, flagging samples where dropout exceeds quality thresholds (>1% zero-count is warning, >5% is failure).

```python
# Zero-count sgRNAs per sample
zero_counts = (count_matrix == 0).sum()
zero_pct = zero_counts / len(count_matrix) * 100

print('Zero-count sgRNAs per sample:')
for sample, pct in zero_pct.items():
    status = 'OK' if pct < 1 else 'WARNING' if pct < 5 else 'FAIL'
    print(f'  {sample}: {pct:.2f}% [{status}]')

# Low-count sgRNAs (<30 reads)
low_counts = (count_matrix < 30).sum()
low_pct = low_counts / len(count_matrix) * 100
print('\nLow-count sgRNAs (<30 reads):')
for sample, pct in low_pct.items():
    print(f'  {sample}: {pct:.2f}%')
```

## Read Distribution (Gini Index)

**Goal:** Quantify how evenly reads are distributed across sgRNAs within each sample.

**Approach:** Calculate the Gini index (0 = perfect equality, 1 = complete inequality) from sorted non-zero counts, where values below 0.2 indicate good uniformity.

```python
def gini_index(x):
    '''Calculate Gini index (0=perfect equality, 1=complete inequality)'''
    x = np.sort(x[x > 0])
    n = len(x)
    cumx = np.cumsum(x)
    return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n

gini_values = count_matrix.apply(gini_index)
print('\nGini index per sample (lower is better, <0.2 ideal):')
for sample, gini in gini_values.items():
    status = 'OK' if gini < 0.2 else 'WARNING' if gini < 0.3 else 'FAIL'
    print(f'  {sample}: {gini:.3f} [{status}]')
```

## Read Count Distribution

```python
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Log read count distribution
for sample in count_matrix.columns:
    log_counts = np.log10(count_matrix[sample] + 1)
    axes[0].hist(log_counts, bins=50, alpha=0.5, label=sample)
axes[0].set_xlabel('Log10(counts + 1)')
axes[0].set_ylabel('sgRNAs')
axes[0].set_title('Read Count Distribution')
axes[0].legend()

# Cumulative distribution
for sample in count_matrix.columns:
    sorted_counts = np.sort(count_matrix[sample])[::-1]
    cumsum = np.cumsum(sorted_counts) / sorted_counts.sum()
    axes[1].plot(np.arange(len(cumsum)) / len(cumsum) * 100, cumsum * 100, label=sample)
axes[1].set_xlabel('% of sgRNAs (ranked)')
axes[1].set_ylabel('% of total reads')
axes[1].set_title('Cumulative Read Distribution')
axes[1].legend()

plt.tight_layout()
plt.savefig('qc_distribution.png', dpi=150)
```

## Replicate Correlation

**Goal:** Verify that biological and technical replicates are concordant.

**Approach:** Compute pairwise Pearson correlations on log-transformed counts, display as a heatmap, and flag replicate pairs with correlation below 0.8.

```python
# Correlation matrix
log_counts = np.log10(count_matrix + 1)
corr_matrix = log_counts.corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', vmin=0.5, vmax=1,
            square=True, fmt='.2f')
plt.title('Replicate Correlation (log10 counts)')
plt.tight_layout()
plt.savefig('qc_correlation.png', dpi=150)

# Check replicate pairs
print('\nReplicate correlations:')
for i, col1 in enumerate(count_matrix.columns):
    for col2 in count_matrix.columns[i+1:]:
        r = corr_matrix.loc[col1, col2]
        status = 'OK' if r > 0.8 else 'WARNING' if r > 0.6 else 'FAIL'
        print(f'  {col1} vs {col2}: r={r:.3f} [{status}]')
```

## Essential Gene Recovery

**Goal:** Confirm that the screen detects known essential genes as a positive control for screen quality.

**Approach:** Load reference essential gene sets, score genes by MAGeCK negative-selection rank, and compute the AUROC for separating essential from non-essential genes.

```python
# Load known essential genes (e.g., from Hart et al. or DepMap)
essential_genes = set(pd.read_csv('essential_genes.txt', header=None)[0])
nonessential_genes = set(pd.read_csv('nonessential_genes.txt', header=None)[0])

# Load MAGeCK results
results = pd.read_csv('screen.gene_summary.txt', sep='\t')

# Check recovery in T0 vs later timepoint
present_essential = results[results['id'].isin(essential_genes)]
present_nonessential = results[results['id'].isin(nonessential_genes)]

# ROC-like analysis
from sklearn.metrics import roc_auc_score

y_true = results['id'].isin(essential_genes).astype(int)
y_score = -results['neg|score']  # More negative = more essential

if y_true.sum() > 0:
    auc = roc_auc_score(y_true, y_score)
    print(f'\nEssential gene recovery AUC: {auc:.3f}')
    status = 'EXCELLENT' if auc > 0.9 else 'GOOD' if auc > 0.8 else 'FAIR' if auc > 0.7 else 'POOR'
    print(f'Status: {status}')
```

## sgRNA Performance

```python
# sgRNAs per gene
sgrnas_per_gene = genes.value_counts()
print(f'\nsgRNAs per gene: mean={sgrnas_per_gene.mean():.1f}, min={sgrnas_per_gene.min()}, max={sgrnas_per_gene.max()}')

# Check for genes with few sgRNAs
few_sgrnas = sgrnas_per_gene[sgrnas_per_gene < 3]
if len(few_sgrnas) > 0:
    print(f'WARNING: {len(few_sgrnas)} genes have <3 sgRNAs')
```

## Sample Normalization Check

```python
# Total reads per sample
total_reads = count_matrix.sum()
print('\nTotal reads per sample:')
for sample, total in total_reads.items():
    print(f'  {sample}: {total:,}')

# Check for major imbalances
cv = total_reads.std() / total_reads.mean()
print(f'\nCoefficient of variation: {cv:.3f}')
if cv > 0.5:
    print('WARNING: Large variation in sequencing depth')
```

## QC Summary Report

**Goal:** Generate a comprehensive pass/fail QC summary for a CRISPR screen.

**Approach:** Aggregate zero-count percentage, mean Gini index, and minimum replicate correlation into a single report, applying quality thresholds to determine overall screen status.

```python
def generate_qc_report(count_matrix, genes):
    report = {
        'total_sgrnas': len(count_matrix),
        'total_genes': genes.nunique(),
        'samples': len(count_matrix.columns),
        'zero_count_pct': (count_matrix == 0).sum().mean() / len(count_matrix) * 100,
        'gini_mean': count_matrix.apply(gini_index).mean(),
        'replicate_corr_min': np.log10(count_matrix + 1).corr().min().min(),
    }

    print('=== QC Summary ===')
    for key, value in report.items():
        if isinstance(value, float):
            print(f'{key}: {value:.3f}')
        else:
            print(f'{key}: {value}')

    # Overall status
    passes = []
    passes.append(report['zero_count_pct'] < 5)
    passes.append(report['gini_mean'] < 0.25)
    passes.append(report['replicate_corr_min'] > 0.7)

    status = 'PASS' if all(passes) else 'FAIL'
    print(f'\nOverall QC: {status}')

    return report

report = generate_qc_report(count_matrix, genes)
```

## Related Skills

- mageck-analysis - Run MAGeCK after QC
- hit-calling - Downstream analysis
- read-qc/quality-reports - General NGS QC
