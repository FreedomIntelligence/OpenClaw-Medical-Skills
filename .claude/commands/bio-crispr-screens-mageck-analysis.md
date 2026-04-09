# bio-crispr-screens-mageck-analysis

> MAGeCK (Model-based Analysis of Genome-wide CRISPR-Cas9 Knockout) for pooled CRISPR screen analysis. Covers count normalization, gene ranking, and pathway analysis. Use when identifying essential genes, drug targets, or resistance mechanisms from dropout or enrichment screens.

## Version Compatibility

Reference examples tested with: MAGeCK 0.5+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# MAGeCK CRISPR Screen Analysis

**"Analyze my pooled CRISPR screen with MAGeCK"** → Count sgRNA reads, normalize across samples, and rank genes by enrichment or depletion using the MAGeCK robust rank aggregation algorithm.
- CLI: `mageck count` → `mageck test` for standard analysis
- CLI: `mageck mle` for multi-condition designs

## Count sgRNAs from FASTQ

**Goal:** Quantify sgRNA representation from raw sequencing data.

**Approach:** Map FASTQ reads to the sgRNA library sequences with MAGeCK count, producing a normalized count matrix and QC summary across all samples.

```bash
# Count reads mapping to sgRNA library
mageck count \
    -l library.csv \
    -n experiment \
    --sample-label Day0,Treated1,Treated2,Control1,Control2 \
    --fastq Day0.fastq.gz Treated1.fastq.gz Treated2.fastq.gz Control1.fastq.gz Control2.fastq.gz \
    --norm-method median

# Output files:
# experiment.count.txt - normalized counts
# experiment.count_normalized.txt - normalized counts
# experiment.countsummary.txt - QC summary
```

## Library File Format

```
# library.csv (tab-separated)
sgRNA_ID	Gene	Sequence
BRCA1_1	BRCA1	ATGGATTTATCTGCTCTTCG
BRCA1_2	BRCA1	CAGCAGATACTTGATGCATC
TP53_1	TP53	CCATTGTTCAATATCGTCCG
...
```

## MAGeCK Test (RRA Algorithm)

**Goal:** Identify genes significantly enriched or depleted between treatment and control conditions.

**Approach:** Run MAGeCK test with robust rank aggregation, which ranks sgRNAs by fold change, tests whether per-gene sgRNA rankings deviate from uniform, and reports gene-level significance with FDR correction.

```bash
# Compare treatment vs control
mageck test \
    -k experiment.count.txt \
    -t Treated1,Treated2 \
    -c Control1,Control2 \
    -n results \
    --norm-method median \
    --gene-test-fdr-threshold 0.25

# Output files:
# results.gene_summary.txt - gene-level results
# results.sgrna_summary.txt - sgRNA-level results
```

## MAGeCK MLE (Maximum Likelihood)

**Goal:** Estimate gene effects in complex experimental designs with multiple conditions or covariates.

**Approach:** Define a design matrix specifying sample-condition relationships, then run MAGeCK MLE which fits a generalized linear model to estimate per-gene beta scores (effect sizes) for each condition.

```bash
# Create design matrix
# design.txt:
# Samples    baseline    treatment
# Day0       1           0
# Control1   1           0
# Control2   1           0
# Treated1   1           1
# Treated2   1           1

mageck mle \
    -k experiment.count.txt \
    -d design.txt \
    -n mle_results \
    --norm-method median

# Output: mle_results.gene_summary.txt with beta scores
```

## Interpret Results

**Goal:** Extract significant essential and resistance genes from MAGeCK output.

**Approach:** Load the gene summary table, filter by negative-selection FDR for dropout/essential genes and positive-selection FDR for enriched/resistance genes, and rank by MAGeCK score.

```python
import pandas as pd

# Load gene summary
genes = pd.read_csv('results.gene_summary.txt', sep='\t')

# Negative selection (dropout/essential)
essential = genes[(genes['neg|fdr'] < 0.05)].sort_values('neg|rank')
print(f'Essential genes (dropout): {len(essential)}')
print(essential[['id', 'neg|score', 'neg|fdr']].head(20))

# Positive selection (enrichment/resistance)
resistant = genes[(genes['pos|fdr'] < 0.05)].sort_values('pos|rank')
print(f'Resistance genes (enriched): {len(resistant)}')
print(resistant[['id', 'pos|score', 'pos|fdr']].head(20))
```

## Visualize Results

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

genes = pd.read_csv('results.gene_summary.txt', sep='\t')

# Volcano plot
fig, ax = plt.subplots(figsize=(10, 8))

x = genes['neg|lfc']
y = -np.log10(genes['neg|fdr'])

colors = ['red' if fdr < 0.05 else 'gray' for fdr in genes['neg|fdr']]
ax.scatter(x, y, c=colors, alpha=0.5, s=10)

# Label top hits
top_hits = genes[genes['neg|fdr'] < 0.01].nsmallest(10, 'neg|rank')
for _, row in top_hits.iterrows():
    ax.annotate(row['id'], (row['neg|lfc'], -np.log10(row['neg|fdr'])))

ax.axhline(-np.log10(0.05), linestyle='--', color='black', alpha=0.5)
ax.set_xlabel('Log2 Fold Change')
ax.set_ylabel('-log10(FDR)')
ax.set_title('MAGeCK Negative Selection')
plt.savefig('mageck_volcano.png', dpi=150)
```

## MAGeCK Pathway Analysis

```bash
# Gene set enrichment on screen results
mageck pathway \
    -g results.gene_summary.txt \
    -c go_biological_process.gmt \
    -n pathway_results \
    --pathway-fdr-threshold 0.25
```

## Time-Course Screens

```bash
# Compare multiple timepoints
mageck mle \
    -k timecourse.count.txt \
    -d timecourse_design.txt \
    -n timecourse_results

# Design matrix for time course:
# Samples    baseline    day7    day14
# Day0       1           0       0
# Day7_R1    1           1       0
# Day7_R2    1           1       0
# Day14_R1   1           0       1
# Day14_R2   1           0       1
```

## CRISPR Activation (CRISPRa) Screens

```bash
# For CRISPRa, focus on positive selection
mageck test \
    -k crispra.count.txt \
    -t Activated1,Activated2 \
    -c Control1,Control2 \
    -n crispra_results

# Hits are genes where activation causes phenotype
# Use pos|fdr and pos|score columns
```

## MAGeCK-VISPR (Visualization)

```bash
# Generate interactive report
mageck-vispr run \
    -n vispr_report \
    -c config.yaml

# config.yaml example:
# experiment: screen_name
# assembly: hg38
# species: homo_sapiens
# targets: library.csv
# sgrnas: experiment.count.txt
# samples:
#   - Day0
#   - Treated1
```

## Related Skills

- screen-qc - Quality control before MAGeCK
- hit-calling - Alternative hit calling methods
- pathway-analysis/gsea - Downstream enrichment analysis
