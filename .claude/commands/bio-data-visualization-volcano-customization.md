# bio-data-visualization-volcano-customization

> Create publication-ready volcano plots with custom thresholds, gene labels, and highlighting using ggplot2, EnhancedVolcano, or matplotlib. Use when visualizing differential expression or association results with gene annotations.

**Available tools:** Read, Bash

# Volcano Plot Customization

## ggplot2 Basic Volcano

```r
library(ggplot2)
library(ggrepel)

# Add significance category column
df$significance <- case_when(
    df$padj < 0.05 & df$log2FoldChange > 1 ~ 'Up',
    df$padj < 0.05 & df$log2FoldChange < -1 ~ 'Down',
    TRUE ~ 'NS'
)

ggplot(df, aes(x = log2FoldChange, y = -log10(pvalue))) +
    geom_point(aes(color = significance), alpha = 0.6, size = 1.5) +
    scale_color_manual(values = c(Up = '#E64B35', Down = '#4DBBD5', NS = 'gray70')) +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed', color = 'gray40') +
    geom_vline(xintercept = c(-1, 1), linetype = 'dashed', color = 'gray40') +
    theme_classic() +
    labs(x = 'log2 Fold Change', y = '-log10(p-value)', color = 'Regulation')
```

## ggplot2 with Gene Labels

```r
# Label top significant genes
top_genes <- df %>%
    filter(padj < 0.05, abs(log2FoldChange) > 1) %>%
    arrange(pvalue) %>%
    head(20)

ggplot(df, aes(x = log2FoldChange, y = -log10(pvalue))) +
    geom_point(aes(color = significance), alpha = 0.6, size = 1.5) +
    scale_color_manual(values = c(Up = '#E64B35', Down = '#4DBBD5', NS = 'gray70')) +
    geom_text_repel(
        data = top_genes,
        aes(label = gene),
        size = 3,
        max.overlaps = 20,
        box.padding = 0.5,
        segment.color = 'gray50'
    ) +
    theme_classic()

# Label specific genes of interest
genes_of_interest <- c('TP53', 'BRCA1', 'MYC', 'EGFR')
highlight_df <- df %>% filter(gene %in% genes_of_interest)

ggplot(df, aes(x = log2FoldChange, y = -log10(pvalue))) +
    geom_point(aes(color = significance), alpha = 0.4, size = 1.5) +
    geom_point(data = highlight_df, color = 'black', size = 3) +
    geom_text_repel(data = highlight_df, aes(label = gene), fontface = 'bold') +
    theme_classic()
```

## EnhancedVolcano (R)

```r
library(EnhancedVolcano)

# Basic EnhancedVolcano
EnhancedVolcano(df,
    lab = df$gene,
    x = 'log2FoldChange',
    y = 'pvalue',
    pCutoff = 0.05,
    FCcutoff = 1,
    title = 'Treatment vs Control',
    subtitle = 'DE genes highlighted')

# Customized EnhancedVolcano
EnhancedVolcano(df,
    lab = df$gene,
    x = 'log2FoldChange',
    y = 'pvalue',
    pCutoff = 0.05,
    FCcutoff = 1,
    xlim = c(-5, 5),
    ylim = c(0, 50),
    pointSize = 2,
    labSize = 3,
    colAlpha = 0.6,
    col = c('gray70', '#4DBBD5', '#00A087', '#E64B35'),
    legendLabels = c('NS', 'Log2FC', 'p-value', 'p-value and Log2FC'),
    legendPosition = 'right',
    drawConnectors = TRUE,
    widthConnectors = 0.5,
    maxoverlapsConnectors = 20,
    selectLab = genes_of_interest,  # Only label specific genes
    boxedLabels = TRUE)
```

## EnhancedVolcano with Custom Keyvals

```r
# Custom point colors by category
keyvals <- ifelse(df$log2FoldChange > 2 & df$padj < 0.01, '#E64B35',
           ifelse(df$log2FoldChange < -2 & df$padj < 0.01, '#4DBBD5',
           ifelse(df$padj < 0.05, '#00A087', 'gray70')))
names(keyvals)[keyvals == '#E64B35'] <- 'Highly Up'
names(keyvals)[keyvals == '#4DBBD5'] <- 'Highly Down'
names(keyvals)[keyvals == '#00A087'] <- 'Moderate'
names(keyvals)[keyvals == 'gray70'] <- 'NS'

EnhancedVolcano(df,
    lab = df$gene,
    x = 'log2FoldChange',
    y = 'pvalue',
    colCustom = keyvals,
    legendPosition = 'right')
```

## matplotlib Volcano (Python)

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(8, 6))

# Color by significance
colors = np.where((df['padj'] < 0.05) & (df['log2FoldChange'] > 1), '#E64B35',
         np.where((df['padj'] < 0.05) & (df['log2FoldChange'] < -1), '#4DBBD5', 'gray'))

ax.scatter(df['log2FoldChange'], -np.log10(df['pvalue']),
           c=colors, alpha=0.6, s=20, edgecolors='none')

# Threshold lines
ax.axhline(-np.log10(0.05), color='gray', linestyle='--', linewidth=1)
ax.axvline(-1, color='gray', linestyle='--', linewidth=1)
ax.axvline(1, color='gray', linestyle='--', linewidth=1)

ax.set_xlabel('log2 Fold Change')
ax.set_ylabel('-log10(p-value)')
plt.tight_layout()
```

## matplotlib with Labels

```python
from adjustText import adjust_text

# Get top genes to label
top_idx = df.nsmallest(15, 'pvalue').index

fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(df['log2FoldChange'], -np.log10(df['pvalue']), c=colors, alpha=0.5, s=15)

# Add labels with adjust_text to avoid overlaps
texts = []
for idx in top_idx:
    texts.append(ax.text(df.loc[idx, 'log2FoldChange'],
                         -np.log10(df.loc[idx, 'pvalue']),
                         df.loc[idx, 'gene'],
                         fontsize=8))

adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
plt.tight_layout()
```

## Threshold Customization

```r
# Standard thresholds
# FC > 1 (2-fold change): Common for RNA-seq, may miss subtle changes
# FC > 0.58 (~1.5-fold): More sensitive, use for subtle effects
# padj < 0.05: Standard FDR threshold
# padj < 0.01: Stringent, fewer false positives
# padj < 0.1: Relaxed, use for exploratory analysis

# Adjust thresholds based on your data
pval_threshold <- 0.05
fc_threshold <- 1  # log2 scale

df$significance <- case_when(
    df$padj < pval_threshold & df$log2FoldChange > fc_threshold ~ 'Up',
    df$padj < pval_threshold & df$log2FoldChange < -fc_threshold ~ 'Down',
    TRUE ~ 'NS'
)
```

## Save Publication-Ready Volcano

```r
# R - high resolution
ggsave('volcano.pdf', width = 8, height = 6)
ggsave('volcano.png', width = 8, height = 6, dpi = 300)

# EnhancedVolcano returns ggplot object
p <- EnhancedVolcano(df, lab = df$gene, x = 'log2FoldChange', y = 'pvalue')
ggsave('volcano.pdf', p, width = 10, height = 8)
```

```python
# Python
plt.savefig('volcano.pdf', bbox_inches='tight')
plt.savefig('volcano.png', dpi=300, bbox_inches='tight')
```

## Related Skills

- differential-expression/de-visualization - DE-specific plots
- data-visualization/ggplot2-fundamentals - General ggplot2
- data-visualization/color-palettes - Color selection
