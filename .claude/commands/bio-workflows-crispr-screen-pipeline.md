# bio-workflows-crispr-screen-pipeline

> End-to-end CRISPR screen analysis from FASTQ to hit genes. Orchestrates guide counting, QC, statistical analysis with MAGeCK, and hit calling with multiple methods. Use when analyzing pooled CRISPR screens from count data to hit calling.

**Available tools:** Read, Bash

# CRISPR Screen Pipeline

## Pipeline Overview

```
FASTQ Files ──> Guide Counting ──> Count Matrix
                                        │
                                        ▼
              ┌─────────────────────────────────────────────┐
              │         crispr-screen-pipeline              │
              ├─────────────────────────────────────────────┤
              │  1. Guide Counting (MAGeCK count)           │
              │  2. QC: Library coverage, gini index        │
              │  3. Gene-level Analysis (MAGeCK RRA/MLE)    │
              │  4. Hit Calling (FDR, effect size)          │
              │  5. Visualization & Reporting               │
              └─────────────────────────────────────────────┘
                                        │
                                        ▼
                    Hit Genes + Volcano/Rank Plots
```

## Complete Workflow

### Step 1: Guide Counting

```bash
# From FASTQ files
mageck count \
    -l library.csv \
    -n experiment \
    --sample-label Day0,Day14_Rep1,Day14_Rep2,Day14_Rep3 \
    --fastq Day0.fastq.gz Day14_Rep1.fastq.gz Day14_Rep2.fastq.gz Day14_Rep3.fastq.gz \
    --trim-5 0 \
    --pdf-report
```

### Step 2: Quality Control

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

counts = pd.read_csv('experiment.count.txt', sep='\t', index_col=0)
counts_numeric = counts.iloc[:, 1:]

qc_stats = {}
for col in counts_numeric.columns:
    total = counts_numeric[col].sum()
    zeros = (counts_numeric[col] == 0).sum()
    gini = calculate_gini(counts_numeric[col].values)
    qc_stats[col] = {'total_reads': total, 'zero_count_guides': zeros, 'gini': gini}

qc_df = pd.DataFrame(qc_stats).T
print('QC Summary:')
print(qc_df)

# Gini index function
def calculate_gini(x):
    x = np.sort(x[x > 0])
    n = len(x)
    cumsum = np.cumsum(x)
    return (2 * np.sum((np.arange(1, n+1) * x)) - (n + 1) * cumsum[-1]) / (n * cumsum[-1])

# QC thresholds
assert qc_df['zero_count_guides'].max() < len(counts) * 0.2, 'Too many zero-count guides'
assert qc_df['gini'].max() < 0.4, 'Gini index too high (uneven distribution)'
print('QC passed!')
```

### Step 3: MAGeCK RRA Analysis (Negative Selection)

```bash
# For dropout/negative selection screens
mageck test \
    -k experiment.count.txt \
    -t Day14_Rep1,Day14_Rep2,Day14_Rep3 \
    -c Day0 \
    -n negative_screen \
    --pdf-report \
    --gene-lfc-method alphamedian
```

### Step 4: MAGeCK MLE (Complex Designs)

```bash
# For screens with multiple conditions
# Design matrix: design.txt
# samplename,baseline,treatment
# Day0,1,0
# Day14_Ctrl,1,0
# Day14_Drug,1,1

mageck mle \
    -k experiment.count.txt \
    -d design.txt \
    -n mle_analysis \
    --threads 8
```

### Step 5: Hit Calling

```python
import pandas as pd

# Load MAGeCK results
gene_summary = pd.read_csv('negative_screen.gene_summary.txt', sep='\t')

# Define hits
gene_summary['neg_hit'] = (gene_summary['neg|fdr'] < 0.05) & (gene_summary['neg|lfc'] < -0.5)
gene_summary['pos_hit'] = (gene_summary['pos|fdr'] < 0.05) & (gene_summary['pos|lfc'] > 0.5)

neg_hits = gene_summary[gene_summary['neg_hit']].sort_values('neg|rank')
pos_hits = gene_summary[gene_summary['pos_hit']].sort_values('pos|rank')

print(f'Negative selection hits (dropout): {len(neg_hits)}')
print(f'Positive selection hits (enriched): {len(pos_hits)}')

# Save hit lists
neg_hits.to_csv('negative_hits.csv', index=False)
pos_hits.to_csv('positive_hits.csv', index=False)
```

### Step 6: Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

# Volcano plot
fig, ax = plt.subplots(figsize=(10, 8))
x = gene_summary['neg|lfc']
y = -np.log10(gene_summary['neg|fdr'] + 1e-10)

colors = ['red' if h else 'blue' if p else 'gray'
          for h, p in zip(gene_summary['neg_hit'], gene_summary['pos_hit'])]
ax.scatter(x, y, c=colors, alpha=0.5, s=20)

ax.axhline(-np.log10(0.05), linestyle='--', color='black', alpha=0.5)
ax.axvline(-0.5, linestyle='--', color='black', alpha=0.5)
ax.axvline(0.5, linestyle='--', color='black', alpha=0.5)

ax.set_xlabel('Log2 Fold Change')
ax.set_ylabel('-Log10(FDR)')
ax.set_title('CRISPR Screen Volcano Plot')
plt.tight_layout()
plt.savefig('volcano_plot.png', dpi=150)
```

## Complete R Workflow

```r
library(MAGeCKFlute)
library(ggplot2)

# Load MAGeCK results
gene_summary <- read.delim('negative_screen.gene_summary.txt')
sgrna_summary <- read.delim('negative_screen.sgrna_summary.txt')

# QC with MAGeCKFlute
FluteMLE(mle_output = 'mle_analysis.gene_summary.txt',
         treatname = 'treatment',
         proj = 'crispr_screen',
         pathview.top = 10)

# Or for RRA results
FluteRRA(gene_summary = gene_summary,
         sgrna_summary = sgrna_summary,
         proj = 'rra_analysis')

# Custom rank plot
gene_summary$rank <- rank(gene_summary$`neg.score`)
gene_summary$is_hit <- gene_summary$`neg.fdr` < 0.05

ggplot(gene_summary, aes(x = rank, y = -log10(`neg.fdr` + 1e-10), color = is_hit)) +
    geom_point(alpha = 0.5) +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed') +
    scale_color_manual(values = c('gray', 'red')) +
    theme_bw() +
    labs(title = 'Gene Rank Plot', x = 'Rank', y = '-Log10(FDR)')
ggsave('rank_plot.png', width = 10, height = 6)
```

## BAGEL2 Alternative (Essential Genes)

```bash
# Calculate Bayes Factor for essentiality
BAGEL.py bf \
    -i experiment.count.txt \
    -o bagel_output \
    -e CEGv2.txt \
    -n NEGv1.txt \
    -c Day0 \
    -s Day14_Rep1,Day14_Rep2,Day14_Rep3

# Precision-recall analysis
BAGEL.py pr \
    -i bagel_output.bf \
    -o bagel_pr \
    -e CEGv2.txt \
    -n NEGv1.txt
```

## QC Checkpoints

| Stage | Check | Action if Failed |
|-------|-------|------------------|
| Counting | >70% mapping rate | Check library/trimming |
| Zero guides | <20% | Check sequencing depth |
| Gini index | <0.4 | Check for amplification bias |
| Replicates | r > 0.8 | Check experimental consistency |
| Controls | Separate in PCA | Check screen worked |

## Workflow Variants

### Positive Selection Screen
```bash
# For enrichment screens (e.g., drug resistance)
mageck test \
    -k counts.txt \
    -t Resistant_Rep1,Resistant_Rep2 \
    -c Sensitive \
    -n positive_screen \
    --gene-lfc-method alphamedian
```

### CRISPRi/CRISPRa
```bash
# Same workflow, different interpretation
# CRISPRi: negative LFC = gene promotes phenotype
# CRISPRa: positive LFC = gene promotes phenotype
mageck test -k counts.txt -t Treated -c Control -n crispri_screen
```

## Related Skills

- crispr-screens/screen-qc - Detailed QC metrics
- crispr-screens/mageck-analysis - MAGeCK parameters
- crispr-screens/hit-calling - Hit calling methods
- crispr-screens/crispresso-editing - Individual editing analysis
- crispr-screens/library-design - sgRNA selection and library design
- crispr-screens/batch-correction - Multi-batch normalization
- pathway-analysis/go-enrichment - Pathway enrichment of hits
