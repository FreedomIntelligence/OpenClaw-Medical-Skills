# bio-data-visualization-specialized-omics-plots

> Reusable plotting functions for common omics visualizations. Custom ggplot2/matplotlib implementations of volcano, MA, PCA, enrichment dotplots, boxplots, and survival curves. Use when creating volcano, MA, or enrichment plots.

**Available tools:** Read, Bash

# Specialized Omics Plots

## Scope

This skill provides **reusable plotting functions** for common omics visualizations that can be applied across different analysis types:
- Volcano plots (any DE result)
- MA plots (any log-fold-change data)
- PCA plots (any high-dimensional data)
- Enrichment dotplots (manual, not enrichplot)
- Expression boxplots with statistics
- Survival curves

**For DESeq2/edgeR built-in functions** (plotMA, plotPCA, plotDispEsts), see `differential-expression/de-visualization`.
**For enrichplot-specific functions** (dotplot, cnetplot, emapplot, gseaplot2), see `pathway-analysis/enrichment-visualization`.

## Volcano Plot (R)

```r
library(ggplot2)
library(ggrepel)

volcano_plot <- function(res, fdr = 0.05, lfc = 1, top_n = 10) {
    res <- res %>%
        mutate(
            significance = case_when(
                padj < fdr & log2FoldChange > lfc ~ 'Up',
                padj < fdr & log2FoldChange < -lfc ~ 'Down',
                TRUE ~ 'NS'
            ),
            label = ifelse(rank(padj) <= top_n & significance != 'NS', gene, '')
        )

    ggplot(res, aes(log2FoldChange, -log10(pvalue), color = significance)) +
        geom_point(alpha = 0.6, size = 1.5) +
        geom_text_repel(aes(label = label), color = 'black', size = 3, max.overlaps = 20) +
        scale_color_manual(values = c('Up' = '#E64B35', 'Down' = '#4DBBD5', 'NS' = 'grey60')) +
        geom_vline(xintercept = c(-lfc, lfc), linetype = 'dashed', color = 'grey40') +
        geom_hline(yintercept = -log10(fdr), linetype = 'dashed', color = 'grey40') +
        labs(x = expression(Log[2]~Fold~Change), y = expression(-Log[10]~P-value)) +
        theme_bw() + theme(panel.grid = element_blank())
}
```

## Volcano Plot (Python)

```python
import matplotlib.pyplot as plt
import numpy as np

def volcano_plot(df, fdr=0.05, lfc=1, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    sig_up = (df['padj'] < fdr) & (df['log2FoldChange'] > lfc)
    sig_down = (df['padj'] < fdr) & (df['log2FoldChange'] < -lfc)
    ns = ~(sig_up | sig_down)

    ax.scatter(df.loc[ns, 'log2FoldChange'], -np.log10(df.loc[ns, 'pvalue']),
               c='grey', alpha=0.5, s=10, label='NS')
    ax.scatter(df.loc[sig_up, 'log2FoldChange'], -np.log10(df.loc[sig_up, 'pvalue']),
               c='#E64B35', alpha=0.7, s=15, label='Up')
    ax.scatter(df.loc[sig_down, 'log2FoldChange'], -np.log10(df.loc[sig_down, 'pvalue']),
               c='#4DBBD5', alpha=0.7, s=15, label='Down')

    ax.axhline(-np.log10(fdr), ls='--', c='grey', lw=0.8)
    ax.axvline(-lfc, ls='--', c='grey', lw=0.8)
    ax.axvline(lfc, ls='--', c='grey', lw=0.8)

    ax.set_xlabel('Log2 Fold Change')
    ax.set_ylabel('-Log10 P-value')
    ax.legend()
    return ax
```

## MA Plot (R)

```r
ma_plot <- function(res, fdr = 0.05) {
    res <- res %>%
        mutate(significant = padj < fdr & !is.na(padj))

    ggplot(res, aes(log10(baseMean), log2FoldChange, color = significant)) +
        geom_point(alpha = 0.5, size = 1) +
        scale_color_manual(values = c('FALSE' = 'grey60', 'TRUE' = '#E64B35')) +
        geom_hline(yintercept = 0, color = 'black', linewidth = 0.5) +
        labs(x = expression(Log[10]~Mean~Expression), y = expression(Log[2]~Fold~Change)) +
        theme_bw() + theme(panel.grid = element_blank(), legend.position = 'none')
}
```

## PCA Plot (R)

```r
pca_plot <- function(vsd, intgroup = 'condition', ntop = 500) {
    rv <- rowVars(assay(vsd))
    select <- order(rv, decreasing = TRUE)[seq_len(min(ntop, length(rv)))]
    pca <- prcomp(t(assay(vsd)[select, ]))
    percentVar <- round(100 * pca$sdev^2 / sum(pca$sdev^2), 1)

    pca_df <- data.frame(PC1 = pca$x[, 1], PC2 = pca$x[, 2], colData(vsd))

    ggplot(pca_df, aes(PC1, PC2, color = .data[[intgroup]])) +
        geom_point(size = 3) +
        stat_ellipse(level = 0.95, linetype = 'dashed') +
        labs(x = paste0('PC1 (', percentVar[1], '%)'),
             y = paste0('PC2 (', percentVar[2], '%)')) +
        theme_bw() + theme(panel.grid = element_blank())
}
```

## PCA Plot (Python)

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def pca_plot(df, metadata, color_by, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    pca = PCA(n_components=2)
    pcs = pca.fit_transform(df.T)

    for group in metadata[color_by].unique():
        mask = metadata[color_by] == group
        ax.scatter(pcs[mask, 0], pcs[mask, 1], label=group, alpha=0.8, s=50)

    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    ax.legend()
    return ax
```

## Dotplot for Enrichment (R)

```r
library(ggplot2)

enrichment_dotplot <- function(enrich_result, top_n = 20) {
    df <- enrich_result %>%
        arrange(p.adjust) %>%
        head(top_n) %>%
        mutate(Description = factor(Description, levels = rev(Description)),
               GeneRatio_numeric = sapply(strsplit(GeneRatio, '/'), function(x) as.numeric(x[1])/as.numeric(x[2])))

    ggplot(df, aes(GeneRatio_numeric, Description, size = Count, color = p.adjust)) +
        geom_point() +
        scale_color_gradient(low = '#E64B35', high = '#4DBBD5', trans = 'log10') +
        scale_size_continuous(range = c(3, 10)) +
        labs(x = 'Gene Ratio', y = NULL, color = 'Adj. P-value', size = 'Count') +
        theme_bw() + theme(panel.grid.major.y = element_blank())
}
```

## Boxplot with Statistics (R)

```r
library(ggpubr)

expression_boxplot <- function(df, gene, group_var) {
    ggboxplot(df, x = group_var, y = gene, color = group_var,
              add = 'jitter', palette = 'npg') +
        stat_compare_means(method = 't.test', label = 'p.signif') +
        labs(y = paste0(gene, ' Expression')) +
        theme(legend.position = 'none')
}
```

## UMAP/tSNE Plot (Python)

```python
import scanpy as sc
import matplotlib.pyplot as plt

def umap_plot(adata, color, ax=None, **kwargs):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    sc.pl.umap(adata, color=color, ax=ax, show=False, **kwargs)
    return ax

# With custom styling
sc.pl.umap(adata, color='leiden', palette='tab20', frameon=False,
           title='', legend_loc='on data', legend_fontsize=8)
```

## Correlation Plot (R)

```r
library(corrplot)

cor_mat <- cor(t(top_genes_mat), method = 'pearson')
corrplot(cor_mat, method = 'color', type = 'lower', order = 'hclust',
         tl.col = 'black', tl.cex = 0.7, col = colorRampPalette(c('#4DBBD5', 'white', '#E64B35'))(100))
```

## Violin Plot with Split (R)

```r
ggplot(df, aes(cluster, expression, fill = condition)) +
    geom_split_violin(alpha = 0.7) +
    geom_boxplot(width = 0.2, position = position_dodge(0.5), outlier.shape = NA) +
    scale_fill_manual(values = c('#4DBBD5', '#E64B35')) +
    theme_bw()
```

## Survival Curves (R)

```r
library(survival)
library(survminer)

fit <- survfit(Surv(time, status) ~ group, data = df)
ggsurvplot(fit, data = df, risk.table = TRUE, pval = TRUE,
           palette = c('#4DBBD5', '#E64B35'),
           legend.labs = c('Low', 'High'))
```

## Related Skills

- data-visualization/ggplot2-fundamentals - Base plotting
- data-visualization/color-palettes - Color selection
- differential-expression/de-visualization - DE-specific plots
- pathway-analysis/enrichment-visualization - Enrichment plots
