# bio-data-visualization-ggplot2-fundamentals

> Create publication-quality scientific figures with ggplot2 including scatter plots, boxplots, heatmaps, and multi-panel layouts. Use when creating static figures for papers, presentations, or reports in R.

**Available tools:** Read, Bash

# ggplot2 Fundamentals

## Basic Structure

```r
library(ggplot2)

# Grammar of graphics: data + aesthetics + geometry
ggplot(data, aes(x = var1, y = var2)) +
    geom_point()
```

## Common Geoms

```r
# Scatter plot
ggplot(df, aes(x, y)) + geom_point()

# Line plot
ggplot(df, aes(x, y)) + geom_line()

# Bar plot
ggplot(df, aes(x, y)) + geom_col()  # y values
ggplot(df, aes(x)) + geom_bar()     # counts

# Boxplot
ggplot(df, aes(group, value)) + geom_boxplot()

# Violin plot
ggplot(df, aes(group, value)) + geom_violin()

# Histogram
ggplot(df, aes(x)) + geom_histogram(bins = 30)

# Density
ggplot(df, aes(x, fill = group)) + geom_density(alpha = 0.5)

# Heatmap
ggplot(df, aes(x, y, fill = value)) + geom_tile()
```

## Aesthetic Mappings

```r
# Color by group
ggplot(df, aes(x, y, color = group)) + geom_point()

# Size by value
ggplot(df, aes(x, y, size = value)) + geom_point()

# Shape by category
ggplot(df, aes(x, y, shape = category)) + geom_point()

# Fill for bars/boxes
ggplot(df, aes(x, y, fill = group)) + geom_boxplot()

# Alpha for transparency
ggplot(df, aes(x, y, alpha = value)) + geom_point()
```

## Publication Theme

```r
theme_publication <- function(base_size = 12) {
    theme_bw(base_size = base_size) +
    theme(
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.border = element_rect(color = 'black', linewidth = 0.5),
        axis.text = element_text(color = 'black'),
        axis.ticks = element_line(color = 'black'),
        legend.key = element_blank(),
        strip.background = element_blank(),
        strip.text = element_text(face = 'bold')
    )
}

# Usage
ggplot(df, aes(x, y)) +
    geom_point() +
    theme_publication()
```

## Color Palettes

```r
library(RColorBrewer)
library(viridis)

# Qualitative (categorical)
scale_color_brewer(palette = 'Set1')
scale_fill_brewer(palette = 'Set2')

# Sequential (continuous)
scale_fill_viridis_c()
scale_color_gradient(low = 'white', high = 'red')

# Diverging
scale_fill_gradient2(low = 'blue', mid = 'white', high = 'red', midpoint = 0)
scale_fill_distiller(palette = 'RdBu')

# Manual colors
scale_color_manual(values = c('Control' = '#1f77b4', 'Treatment' = '#d62728'))
```

## Volcano Plot

```r
volcano_plot <- function(res, fdr = 0.05, lfc = 1) {
    res <- res %>%
        mutate(
            significance = case_when(
                padj < fdr & log2FoldChange > lfc ~ 'Up',
                padj < fdr & log2FoldChange < -lfc ~ 'Down',
                TRUE ~ 'NS'
            )
        )

    ggplot(res, aes(log2FoldChange, -log10(pvalue), color = significance)) +
        geom_point(alpha = 0.6, size = 1) +
        scale_color_manual(values = c('Up' = '#d62728', 'Down' = '#1f77b4', 'NS' = 'grey60')) +
        geom_vline(xintercept = c(-lfc, lfc), linetype = 'dashed', color = 'grey40') +
        geom_hline(yintercept = -log10(fdr), linetype = 'dashed', color = 'grey40') +
        labs(x = 'Log2 Fold Change', y = '-Log10 P-value') +
        theme_publication()
}
```

## MA Plot

```r
ma_plot <- function(res, fdr = 0.05) {
    res <- res %>%
        mutate(significant = padj < fdr)

    ggplot(res, aes(log10(baseMean), log2FoldChange, color = significant)) +
        geom_point(alpha = 0.5, size = 1) +
        scale_color_manual(values = c('TRUE' = 'red', 'FALSE' = 'grey60')) +
        geom_hline(yintercept = 0, color = 'black') +
        labs(x = 'Log10 Mean Expression', y = 'Log2 Fold Change') +
        theme_publication()
}
```

## Boxplot with Points

```r
ggplot(df, aes(group, value, fill = group)) +
    geom_boxplot(outlier.shape = NA, alpha = 0.7) +
    geom_jitter(width = 0.2, alpha = 0.5, size = 1) +
    scale_fill_brewer(palette = 'Set2') +
    labs(x = NULL, y = 'Expression') +
    theme_publication() +
    theme(legend.position = 'none')
```

## Faceting

```r
# Wrap by one variable
ggplot(df, aes(x, y)) +
    geom_point() +
    facet_wrap(~ group, scales = 'free')

# Grid by two variables
ggplot(df, aes(x, y)) +
    geom_point() +
    facet_grid(rows = vars(condition), cols = vars(timepoint))
```

## Labels and Text

```r
library(ggrepel)

ggplot(res, aes(log2FoldChange, -log10(pvalue))) +
    geom_point() +
    geom_text_repel(
        data = subset(res, padj < 0.01),
        aes(label = gene),
        max.overlaps = 20,
        size = 3
    )
```

## Multi-Panel Figures

```r
library(patchwork)

p1 <- ggplot(df, aes(x, y)) + geom_point()
p2 <- ggplot(df, aes(group, value)) + geom_boxplot()
p3 <- ggplot(df, aes(x)) + geom_histogram()

# Combine horizontally
p1 + p2 + p3

# Combine with layout
(p1 | p2) / p3

# Add labels
(p1 + p2 + p3) + plot_annotation(tag_levels = 'A')

# Shared legend
(p1 + p2) + plot_layout(guides = 'collect')
```

## Saving Figures

```r
# For publication (300 DPI)
ggsave('figure.pdf', p, width = 7, height = 5, units = 'in')
ggsave('figure.png', p, width = 7, height = 5, units = 'in', dpi = 300)
ggsave('figure.tiff', p, width = 7, height = 5, units = 'in', dpi = 300, compression = 'lzw')

# For presentations
ggsave('figure.png', p, width = 10, height = 6, dpi = 150)
```

## Axis Formatting

```r
library(scales)

# Scientific notation
scale_y_continuous(labels = scientific)

# Comma separators
scale_x_continuous(labels = comma)

# Log scale
scale_y_log10(labels = trans_format('log10', math_format(10^.x)))

# Percent
scale_y_continuous(labels = percent)

# Limits
coord_cartesian(xlim = c(0, 10), ylim = c(0, 100))

# Breaks
scale_x_continuous(breaks = seq(0, 10, 2))
```

## Legend Customization

```r
# Position
theme(legend.position = 'bottom')
theme(legend.position = 'none')
theme(legend.position = c(0.8, 0.2))

# Title
labs(color = 'Condition', fill = 'Group')
guides(color = guide_legend(title = 'Condition'))

# Order
scale_color_discrete(limits = c('Control', 'Treatment'))
```

## Heatmap with pheatmap

```r
library(pheatmap)
library(RColorBrewer)

pheatmap(
    mat,
    scale = 'row',
    color = colorRampPalette(rev(brewer.pal(9, 'RdBu')))(100),
    cluster_rows = TRUE,
    cluster_cols = TRUE,
    show_rownames = TRUE,
    show_colnames = TRUE,
    annotation_col = annotation_df,
    fontsize = 8,
    filename = 'heatmap.pdf',
    width = 8,
    height = 10
)
```

## Related Skills

- differential-expression/de-visualization - DE-specific plots
- pathway-analysis/enrichment-visualization - Enrichment plots
- reporting/rmarkdown-reports - Figures in reports
