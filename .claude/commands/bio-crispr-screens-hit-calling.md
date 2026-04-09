# bio-crispr-screens-hit-calling

> Statistical methods for calling hits in CRISPR screens. Covers MAGeCK, BAGEL2, drugZ, and custom approaches for identifying essential and resistance genes. Use when identifying significant genes from screen count data after QC passes.

## Version Compatibility

Reference examples tested with: MAGeCK 0.5+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scipy 1.12+, statsmodels 0.14+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# CRISPR Screen Hit Calling

**"Identify essential genes from my CRISPR screen"** → Call significant gene hits from sgRNA count data using statistical methods that account for guide-level variability and multiple testing.
- CLI: `BAGEL.py bf` for Bayes factor essentiality scoring
- Python: `drugZ` for fold-change based analysis

## BAGEL2 Analysis

**Goal:** Identify essential genes using Bayesian classification against reference gene sets.

**Approach:** Calculate sgRNA fold changes, compute Bayes Factors using known essential and non-essential gene sets as training data, and assess precision-recall at different thresholds.

```bash
# BAGEL2 for Bayesian gene essentiality
# Uses reference essential/non-essential genes

# Calculate fold changes
bagel2 fc \
    -i counts.txt \
    -o foldchange.txt \
    -c Control1,Control2 \
    -t Treatment1,Treatment2

# Calculate Bayes Factor
bagel2 bf \
    -i foldchange.txt \
    -o bayes_factor.txt \
    -e essential_genes.txt \
    -n nonessential_genes.txt \
    -c 1  # Number of bootstrap iterations

# Precision-recall analysis
bagel2 pr \
    -i bayes_factor.txt \
    -o precision_recall.txt \
    -e essential_genes.txt \
    -n nonessential_genes.txt
```

## DrugZ Analysis

```bash
# DrugZ for drug screens (synergy/resistance)
drugz.py \
    -i counts.txt \
    -o drugz_output.txt \
    -c Control1,Control2 \
    -x Treatment1,Treatment2 \
    --remove-genes Control_genes.txt

# Output columns:
# Gene, sumZ (combined z-score), normZ, pval_synth (synthetic lethal), pval_supp (suppressor)
```

## Custom Hit Calling in Python

**Goal:** Call screen hits using a z-score approach without external tools.

**Approach:** RPM-normalize counts, compute per-sgRNA log2 fold changes, aggregate to gene level, derive z-scores from the null distribution, and apply FDR correction.

```python
import pandas as pd
import numpy as np
from scipy import stats

# Load counts
counts = pd.read_csv('counts.txt', sep='\t', index_col=0)
genes = counts['Gene']
ctrl_cols = ['Control1', 'Control2']
treat_cols = ['Treatment1', 'Treatment2']

# Normalize (reads per million)
def rpm_normalize(df):
    return df / df.sum() * 1e6

ctrl_rpm = rpm_normalize(counts[ctrl_cols])
treat_rpm = rpm_normalize(counts[treat_cols])

# Log2 fold change per sgRNA
lfc = np.log2((treat_rpm.mean(axis=1) + 1) / (ctrl_rpm.mean(axis=1) + 1))

# Aggregate to gene level
gene_lfc = pd.DataFrame({'Gene': genes, 'LFC': lfc}).groupby('Gene')['LFC'].agg(['mean', 'std', 'count'])
gene_lfc.columns = ['mean_lfc', 'std_lfc', 'n_sgrnas']

# Z-score based on null distribution (non-targeting controls or all genes)
null_mean = gene_lfc['mean_lfc'].median()
null_std = gene_lfc['mean_lfc'].std()
gene_lfc['z_score'] = (gene_lfc['mean_lfc'] - null_mean) / null_std
gene_lfc['pvalue'] = 2 * stats.norm.sf(abs(gene_lfc['z_score']))
from statsmodels.stats.multitest import multipletests
_, gene_lfc['fdr'], _, _ = multipletests(gene_lfc['pvalue'], method='fdr_bh')

# Call hits
essential = gene_lfc[(gene_lfc['z_score'] < -2) & (gene_lfc['fdr'] < 0.1)]
resistance = gene_lfc[(gene_lfc['z_score'] > 2) & (gene_lfc['fdr'] < 0.1)]

print(f'Essential genes: {len(essential)}')
print(f'Resistance genes: {len(resistance)}')
```

## Robust Rank Aggregation (MAGeCK-style)

**Goal:** Rank genes by combining evidence across multiple sgRNAs using the RRA algorithm.

**Approach:** Rank sgRNA-level p-values, compute per-gene RRA scores using beta-distribution modeling of rank uniformity, and select genes with significantly non-uniform guide rankings.

```python
from scipy.stats import rankdata, norm
import numpy as np

def rra_score(ranks, n_total):
    '''Calculate RRA score for a set of ranks'''
    k = len(ranks)
    sorted_ranks = np.sort(ranks)
    rho = sorted_ranks / n_total

    # Beta distribution p-values
    from scipy.stats import beta
    pvals = [beta.cdf(rho[i], i + 1, k - i) for i in range(k)]

    # Return minimum p-value (most significant)
    return min(pvals)

# Apply to each gene
def calculate_gene_rra(sgrna_pvals, genes, n_total):
    results = []
    for gene in genes.unique():
        gene_pvals = sgrna_pvals[genes == gene]
        gene_ranks = rankdata(gene_pvals)
        rra = rra_score(gene_ranks, len(gene_pvals))
        results.append({'gene': gene, 'rra_score': rra, 'n_sgrnas': len(gene_pvals)})
    return pd.DataFrame(results)
```

## Second-Best sgRNA Method

```python
# Conservative approach: use second-best sgRNA per gene
# Reduces false positives from single outlier sgRNAs

def second_best_lfc(lfc_series, genes):
    '''Return second-most extreme LFC per gene'''
    results = []
    for gene in genes.unique():
        gene_lfc = lfc_series[genes == gene].sort_values()
        if len(gene_lfc) >= 2:
            # For dropout, use second smallest (second most negative)
            results.append({'gene': gene, 'second_best_lfc': gene_lfc.iloc[1]})
        else:
            results.append({'gene': gene, 'second_best_lfc': gene_lfc.iloc[0]})
    return pd.DataFrame(results)

second_best = second_best_lfc(lfc, genes)
```

## Compare Methods

**Goal:** Identify high-confidence hits by requiring agreement across multiple analysis methods.

**Approach:** Load gene-level results from MAGeCK, BAGEL2, and DrugZ, merge on gene name, and flag consensus hits called by two or more methods.

```python
# Load results from different methods
mageck = pd.read_csv('mageck.gene_summary.txt', sep='\t')
bagel = pd.read_csv('bagel_bf.txt', sep='\t')
drugz = pd.read_csv('drugz_output.txt', sep='\t')

# Merge on gene
merged = mageck[['id', 'neg|fdr']].rename(columns={'id': 'gene', 'neg|fdr': 'mageck_fdr'})
merged = merged.merge(bagel[['Gene', 'BF']].rename(columns={'Gene': 'gene', 'BF': 'bagel_bf'}), on='gene')
merged = merged.merge(drugz[['GENE', 'fdr_synth']].rename(columns={'GENE': 'gene', 'fdr_synth': 'drugz_fdr'}), on='gene')

# Consensus hits
merged['mageck_hit'] = merged['mageck_fdr'] < 0.1
merged['bagel_hit'] = merged['bagel_bf'] > 5  # BF > 5 suggests essential
merged['drugz_hit'] = merged['drugz_fdr'] < 0.1

merged['consensus'] = merged['mageck_hit'].astype(int) + merged['bagel_hit'].astype(int) + merged['drugz_hit'].astype(int)

# High confidence hits called by 2+ methods
high_conf = merged[merged['consensus'] >= 2]
print(f'High confidence hits (2+ methods): {len(high_conf)}')
```

## Time-Course Analysis

```python
# For screens with multiple timepoints
def time_course_hits(counts, timepoints, genes):
    '''Identify genes with consistent depletion over time'''
    lfc_by_time = {}

    for t in timepoints:
        t0_cols = [c for c in counts.columns if 'T0' in c]
        t_cols = [c for c in counts.columns if f'T{t}' in c]

        t0_mean = counts[t0_cols].mean(axis=1)
        t_mean = counts[t_cols].mean(axis=1)

        lfc_by_time[t] = np.log2((t_mean + 1) / (t0_mean + 1))

    # Aggregate and check for consistent direction
    lfc_df = pd.DataFrame(lfc_by_time)
    lfc_df['Gene'] = genes

    gene_summary = lfc_df.groupby('Gene').mean()
    gene_summary['all_negative'] = (gene_summary < 0).all(axis=1)
    gene_summary['trend'] = gene_summary.apply(lambda x: np.polyfit(range(len(timepoints)), x[:-1], 1)[0], axis=1)

    return gene_summary[gene_summary['all_negative']].sort_values('trend')
```

## Visualize Results

```python
import matplotlib.pyplot as plt

# Rank plot
fig, ax = plt.subplots(figsize=(10, 6))

results = pd.read_csv('mageck.gene_summary.txt', sep='\t')
results = results.sort_values('neg|score')
results['rank'] = range(1, len(results) + 1)

ax.scatter(results['rank'], -np.log10(results['neg|fdr']),
           c=['red' if fdr < 0.05 else 'gray' for fdr in results['neg|fdr']],
           alpha=0.5, s=10)

# Label top hits
top = results[results['neg|fdr'] < 0.01].head(10)
for _, row in top.iterrows():
    ax.annotate(row['id'], (row['rank'], -np.log10(row['neg|fdr'])))

ax.axhline(-np.log10(0.05), linestyle='--', color='black')
ax.set_xlabel('Gene Rank')
ax.set_ylabel('-log10(FDR)')
ax.set_title('CRISPR Screen Hits')
plt.savefig('hit_ranking.png', dpi=150)
```

## Related Skills

- mageck-analysis - MAGeCK workflow
- screen-qc - QC before hit calling
- pathway-analysis/go-enrichment - Functional analysis of hits
