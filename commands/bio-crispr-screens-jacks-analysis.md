# bio-crispr-screens-jacks-analysis

> JACKS (Joint Analysis of CRISPR/Cas9 Knockout Screens) for modeling sgRNA efficacy and gene essentiality. Use when analyzing multiple CRISPR screens simultaneously or when accounting for variable sgRNA efficiency across experiments.

## Version Compatibility

Reference examples tested with: MAGeCK 0.5+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# JACKS CRISPR Screen Analysis

**"Analyze multiple CRISPR screens jointly with JACKS"** → Model sgRNA efficacy and gene essentiality simultaneously across multiple screens, accounting for variable guide efficiency.
- Python: `jacks.infer_JACKS()` for joint analysis across experiments

JACKS jointly models sgRNA efficacy and gene essentiality across multiple experiments. It infers both gene-level fitness effects and sgRNA-specific efficiency.

## Installation

```bash
pip install jacks
# or
git clone https://github.com/felicityallen/JACKS.git
cd JACKS && pip install -e .
```

## Input File Formats

### Count Data

```
# counts.txt (tab-separated)
sgRNA	Gene	Sample1	Sample2	Sample3	Control1	Control2
sgRNA1	GENE_A	100	120	90	80	85
sgRNA2	GENE_A	200	180	210	150	160
sgRNA3	GENE_B	50	45	55	60	58
...
```

### Replicate Map

```
# replicatemap.txt
Sample1	Experiment1	Day14
Sample2	Experiment1	Day14
Sample3	Experiment2	Day14
Control1	Experiment1	Day0
Control2	Experiment2	Day0
```

### Guide-Gene Map

```
# guidemap.txt
sgRNA1	GENE_A
sgRNA2	GENE_A
sgRNA3	GENE_B
sgRNA4	GENE_B
...
```

## Basic JACKS Analysis

### Command Line

```bash
# Run JACKS
python -m jacks.run_JACKS \
    counts.txt \
    replicatemap.txt \
    guidemap.txt \
    output_prefix \
    --ctrl_sample_pattern "Day0" \
    --ctrl_sample_pattern_column "Condition"
```

### Python API

**Goal:** Run JACKS joint analysis to simultaneously model sgRNA efficacy and gene essentiality across experiments.

**Approach:** Load count data, guide-gene mapping, and replicate map; separate control and treatment samples; then run MCMC inference to estimate gene fitness effects and per-sgRNA efficiency.

```python
from jacks import infer
import pandas as pd

# Load data
counts = pd.read_csv('counts.txt', sep='\t', index_col=0)
guide_gene_map = pd.read_csv('guidemap.txt', sep='\t', header=None, names=['sgRNA', 'Gene'])
replicate_map = pd.read_csv('replicatemap.txt', sep='\t', header=None,
                             names=['Sample', 'Experiment', 'Condition'])

# Separate control and treatment samples
ctrl_samples = replicate_map[replicate_map['Condition'] == 'Day0']['Sample'].tolist()
treatment_samples = replicate_map[replicate_map['Condition'] == 'Day14']['Sample'].tolist()

# Run JACKS inference
# n_iterations=10000: MCMC iterations. Increase for final analysis.
# burn_in=1000: Burn-in period. Should be ~10% of iterations.
jacks_results = infer.run_inference(
    counts,
    guide_gene_map,
    treatment_samples,
    ctrl_samples,
    n_iterations=10000,
    burn_in=1000
)
```

## Output Files

| File | Description |
|------|-------------|
| `_gene_JACKS_results.txt` | Gene-level essentiality scores |
| `_grna_JACKS_results.txt` | sgRNA-level efficacy estimates |
| `_jacks_full_data.pickle` | Full model for downstream analysis |

## Interpret Gene Results

**Goal:** Classify genes as essential or enriched from JACKS output scores.

**Approach:** Load the gene results table, filter by JACKS score direction and FDR significance, and rank to identify top essential (negative effect) and enriched (positive effect) genes.

```python
import pandas as pd
import numpy as np

# Load gene results
genes = pd.read_csv('output_gene_JACKS_results.txt', sep='\t')

# JACKS score: negative = essential (dropout), positive = enriched
# Columns: gene, X1 (effect), X2 (std), fdr_log10

# Essential genes (significant negative effect)
# fdr_threshold=-1: log10(FDR) < -1 means FDR < 0.1
essential = genes[(genes['X1'] < 0) & (genes['fdr_log10'] < -1)]
essential = essential.sort_values('X1')
print(f'Essential genes: {len(essential)}')
print(essential.head(20))

# Enriched genes
enriched = genes[(genes['X1'] > 0) & (genes['fdr_log10'] < -1)]
enriched = enriched.sort_values('X1', ascending=False)
print(f'Enriched genes: {len(enriched)}')
```

## sgRNA Efficacy Analysis

**Goal:** Assess sgRNA performance to identify low-efficacy guides for library optimization.

**Approach:** Load per-sgRNA efficacy estimates from JACKS output, flag guides below an efficacy threshold, and aggregate by gene to evaluate library-level guide quality.

```python
import pandas as pd

# Load sgRNA results
guides = pd.read_csv('output_grna_JACKS_results.txt', sep='\t')

# Efficacy scores range from 0 (ineffective) to 1 (highly effective)
# X1 column contains efficacy estimates

# Identify poor sgRNAs
# efficacy<0.3: sgRNAs with low efficacy. Consider removal in future libraries.
poor_guides = guides[guides['X1'] < 0.3]
print(f'Low efficacy guides: {len(poor_guides)}')

# Group by gene to assess library quality
gene_efficacy = guides.groupby('Gene')['X1'].agg(['mean', 'std', 'count'])
gene_efficacy = gene_efficacy.sort_values('mean')
print(gene_efficacy.head(20))
```

## Visualization

### Gene Effect Plot

```python
import matplotlib.pyplot as plt
import numpy as np

genes = pd.read_csv('output_gene_JACKS_results.txt', sep='\t')

fig, ax = plt.subplots(figsize=(10, 8))

# Color by significance
colors = ['red' if fdr < -1 else 'gray' for fdr in genes['fdr_log10']]

ax.scatter(genes['X1'], -genes['fdr_log10'], c=colors, alpha=0.5, s=10)
ax.axhline(1, linestyle='--', color='black', alpha=0.5)  # FDR = 0.1
ax.axvline(0, linestyle='-', color='gray', alpha=0.3)

ax.set_xlabel('JACKS Score (negative = essential)')
ax.set_ylabel('-log10(FDR)')
ax.set_title('JACKS Gene Essentiality')

# Label top hits
top = genes[genes['fdr_log10'] < -2].nsmallest(10, 'X1')
for _, row in top.iterrows():
    ax.annotate(row['gene'], (row['X1'], -row['fdr_log10']))

plt.savefig('jacks_volcano.png', dpi=150)
```

### sgRNA Efficacy Distribution

```python
import matplotlib.pyplot as plt

guides = pd.read_csv('output_grna_JACKS_results.txt', sep='\t')

plt.figure(figsize=(8, 5))
plt.hist(guides['X1'], bins=50, edgecolor='black')
plt.axvline(0.5, color='red', linestyle='--', label='Efficacy = 0.5')
plt.xlabel('sgRNA Efficacy')
plt.ylabel('Count')
plt.title('sgRNA Efficacy Distribution')
plt.legend()
plt.savefig('sgrna_efficacy.png', dpi=150)
```

## Multi-Screen Analysis

JACKS strength is joint analysis across experiments.

```python
# Define multiple experiments in replicate map
# replicatemap.txt:
# Sample        Experiment    Condition
# Screen1_T1   Screen1       Treatment
# Screen1_T2   Screen1       Treatment
# Screen1_C1   Screen1       Control
# Screen2_T1   Screen2       Treatment
# Screen2_T2   Screen2       Treatment
# Screen2_C1   Screen2       Control

# JACKS will learn shared sgRNA efficacy across screens
# while estimating screen-specific gene effects
```

## Comparing JACKS vs MAGeCK

| Feature | JACKS | MAGeCK |
|---------|-------|--------|
| sgRNA efficacy modeling | Yes | No |
| Multi-experiment joint analysis | Yes | Limited |
| Statistical framework | Bayesian | MLE/RRA |
| Speed | Slower | Faster |
| Best for | Multiple screens | Single screen |

## Advanced Options

```python
from jacks import infer

# Run with custom parameters
results = infer.run_inference(
    counts,
    guide_gene_map,
    treatment_samples,
    ctrl_samples,
    n_iterations=50000,     # 50000: Publication quality. 10000 for exploration.
    burn_in=5000,           # 5000: 10% of iterations.
    apply_w_hp=True,        # Hierarchical prior on efficacy
    fixed_w=False,          # Learn sgRNA efficacy (set True to fix at 1)
    w_alpha=0.5,            # Prior shape for efficacy
    w_beta=0.5              # Prior rate for efficacy
)
```

## Integration with Other Tools

### Compare with MAGeCK

```python
import pandas as pd

jacks = pd.read_csv('jacks_gene_results.txt', sep='\t')
mageck = pd.read_csv('mageck.gene_summary.txt', sep='\t')

# Merge results
merged = pd.merge(jacks, mageck, left_on='gene', right_on='id')

# Compare rankings
from scipy.stats import spearmanr
corr, pval = spearmanr(merged['X1'], merged['neg|score'])
print(f'Spearman correlation: {corr:.3f} (p={pval:.2e})')
```

### Use sgRNA Efficacy for Library Design

```python
# Extract high-efficacy guides for future libraries
guides = pd.read_csv('output_grna_JACKS_results.txt', sep='\t')

# efficacy>0.7: High efficacy sgRNAs for optimized libraries.
good_guides = guides[guides['X1'] > 0.7][['sgRNA', 'Gene', 'X1']]
good_guides.to_csv('high_efficacy_guides.csv', index=False)
```

## Related Skills

- mageck-analysis - Alternative screen analysis method
- hit-calling - Statistical hit identification
- screen-qc - Quality control before analysis
- batch-correction - Handle batch effects in multi-screen data
