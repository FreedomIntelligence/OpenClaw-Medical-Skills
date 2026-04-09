# bio-data-visualization-multipanel-figures

> Combine multiple plots into publication-ready multi-panel figures using patchwork, cowplot, or matplotlib GridSpec with shared legends and panel labels. Use when combining multiple plots into publication figures.

**Available tools:** Read, Bash

# Multi-Panel Figure Assembly

## patchwork Basics

```r
library(patchwork)

p1 <- ggplot(df, aes(x, y)) + geom_point()
p2 <- ggplot(df, aes(group, value)) + geom_boxplot()
p3 <- ggplot(df, aes(x)) + geom_histogram()

# Horizontal
p1 + p2 + p3

# Vertical
p1 / p2 / p3

# Mixed layouts
(p1 | p2) / p3
(p1 + p2) / (p3 + p4)
```

## Panel Labels

```r
# Automatic labels
(p1 + p2 + p3) + plot_annotation(tag_levels = 'A')

# Custom labels
(p1 + p2 + p3) + plot_annotation(tag_levels = list(c('A', 'B', 'C')))

# Label styling
(p1 + p2) + plot_annotation(
    tag_levels = 'A',
    tag_prefix = '(',
    tag_suffix = ')',
    theme = theme(plot.tag = element_text(face = 'bold', size = 14))
)
```

## Layout Control

```r
# Width ratios
p1 + p2 + plot_layout(widths = c(2, 1))

# Height ratios
p1 / p2 + plot_layout(heights = c(1, 2))

# Complex grid
layout <- "
AAB
AAB
CCC
"
p1 + p2 + p3 + plot_layout(design = layout)

# Fixed dimensions
p1 + p2 + plot_layout(widths = unit(c(5, 3), 'cm'))
```

## Shared Legends

```r
# Collect legends
(p1 + p2 + p3) + plot_layout(guides = 'collect')

# Position at bottom
(p1 + p2) + plot_layout(guides = 'collect') &
    theme(legend.position = 'bottom')

# Keep individual legends
(p1 + p2) + plot_layout(guides = 'keep')
```

## Inset Plots

```r
# Add inset
p1 + inset_element(p2, left = 0.6, bottom = 0.6, right = 1, top = 1)

# Multiple insets
p1 +
    inset_element(p2, 0.6, 0.6, 1, 1) +
    inset_element(p3, 0.02, 0.6, 0.4, 1)
```

## cowplot Alternative

```r
library(cowplot)

# Simple grid
plot_grid(p1, p2, p3, ncol = 3, labels = 'AUTO')

# With labels
plot_grid(p1, p2, labels = c('A', 'B'), label_size = 14)

# Relative widths
plot_grid(p1, p2, rel_widths = c(2, 1))

# Nested grids
top_row <- plot_grid(p1, p2, ncol = 2)
bottom_row <- p3
plot_grid(top_row, bottom_row, nrow = 2, labels = c('', 'C'))
```

## Shared Axes

```r
library(patchwork)

# Same axis limits
(p1 + p2) & xlim(0, 10) & ylim(0, 100)

# Same theme
(p1 + p2 + p3) & theme_minimal()

# Same color scale
(p1 + p2) & scale_color_viridis_d()
```

## Empty Spaces

```r
# Add blank panel
p1 + plot_spacer() + p2

# With layout
layout <- "
AB#
CCC
"
p1 + p2 + p3 + plot_layout(design = layout)
```

## Titles and Captions

```r
(p1 + p2 + p3) +
    plot_annotation(
        title = 'Main Title',
        subtitle = 'Subtitle text',
        caption = 'Data source: ...',
        theme = theme(
            plot.title = element_text(face = 'bold', size = 16),
            plot.subtitle = element_text(size = 12, color = 'grey40')
        )
    )
```

## Saving Multi-Panel Figures

```r
# Combine and save
combined <- (p1 | p2) / (p3 | p4) +
    plot_annotation(tag_levels = 'A') &
    theme(plot.tag = element_text(face = 'bold'))

ggsave('figure.pdf', combined, width = 10, height = 8)
ggsave('figure.png', combined, width = 10, height = 8, dpi = 300)

# For specific journal dimensions
ggsave('figure.pdf', combined, width = 180, height = 150, units = 'mm')
```

## Complex Publication Figure

```r
# Create themed plots
theme_pub <- theme_bw(base_size = 10) +
    theme(
        panel.grid = element_blank(),
        legend.position = 'none'
    )

p_volcano <- create_volcano(res) + theme_pub + ggtitle('Volcano Plot')
p_pca <- create_pca(vsd) + theme_pub + ggtitle('PCA')
p_heatmap <- wrap_elements(pheatmap_grob)
p_boxplot <- create_boxplot(expr_df) + theme_pub + ggtitle('Expression')

# Assemble
figure <- (p_volcano | p_pca) / (p_heatmap | p_boxplot) +
    plot_annotation(tag_levels = 'A') +
    plot_layout(guides = 'collect') &
    theme(
        plot.tag = element_text(face = 'bold', size = 12),
        legend.position = 'bottom'
    )

ggsave('Figure1.pdf', figure, width = 180, height = 160, units = 'mm')
```

## matplotlib GridSpec (Python)

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(12, 8))
gs = GridSpec(2, 3, figure=fig)

ax1 = fig.add_subplot(gs[0, 0])    # Top left
ax2 = fig.add_subplot(gs[0, 1:])   # Top right, spans 2 columns
ax3 = fig.add_subplot(gs[1, :])    # Bottom, spans all columns

# Add plots to each axis
ax1.plot(x, y)
ax2.scatter(x, y)
ax3.bar(x, y)

plt.tight_layout()
```

## matplotlib Panel Labels

```python
# Add panel labels
for ax, label in zip([ax1, ax2, ax3], ['A', 'B', 'C']):
    ax.text(-0.1, 1.1, label, transform=ax.transAxes,
            fontsize=14, fontweight='bold', va='top')
```

## matplotlib Subfigures

```python
# matplotlib 3.4+ subfigures for complex layouts
fig = plt.figure(figsize=(12, 8))
subfigs = fig.subfigures(1, 2, width_ratios=[2, 1])

axs_left = subfigs[0].subplots(2, 1)
ax_right = subfigs[1].subplots(1, 1)
```

## Publication Export

```python
# Python
fig.savefig('figure1.pdf', bbox_inches='tight')
fig.savefig('figure1.png', dpi=300, bbox_inches='tight')
```

## Related Skills

- data-visualization/ggplot2-fundamentals - Individual plots
- reporting/rmarkdown-reports - Figures in documents
- differential-expression/de-visualization - DE-specific plots
