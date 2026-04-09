# bio-data-visualization-upset-plots

> Create UpSet plots to visualize set intersections as an alternative to Venn diagrams using UpSetR or upsetplot. Use when comparing overlapping gene sets, peak sets, or sample groups with more than 3 sets.

**Available tools:** Read, Bash

# UpSet Plots

## UpSetR (R) - Basic Plot

```r
library(UpSetR)

# From binary matrix (rows = elements, columns = sets)
upset(fromExpression(data), order.by = 'freq', nsets = 6)

# From list of sets
gene_sets <- list(
    SetA = c('Gene1', 'Gene2', 'Gene3', 'Gene4'),
    SetB = c('Gene2', 'Gene3', 'Gene5', 'Gene6'),
    SetC = c('Gene1', 'Gene3', 'Gene6', 'Gene7'),
    SetD = c('Gene3', 'Gene4', 'Gene7', 'Gene8')
)
upset(fromList(gene_sets), order.by = 'freq', nsets = 4)
```

## UpSetR Customization

```r
# Customized appearance
upset(fromList(gene_sets),
      nsets = 6,
      nintersects = 40,
      order.by = 'freq',
      decreasing = TRUE,
      mb.ratio = c(0.6, 0.4),  # Matrix to bar ratio
      point.size = 3,
      line.size = 1.5,
      mainbar.y.label = 'Intersection Size',
      sets.x.label = 'Set Size',
      text.scale = c(1.5, 1.3, 1.3, 1, 1.5, 1.3),
      set_size.show = TRUE,
      set_size.scale_max = 500)

# Custom set colors
upset(fromList(gene_sets),
      sets.bar.color = c('#E64B35', '#4DBBD5', '#00A087', '#3C5488'),
      main.bar.color = '#7E6148',
      matrix.color = '#7E6148')
```

## UpSetR with Queries

```r
# Highlight specific intersections
upset(fromList(gene_sets),
      order.by = 'freq',
      queries = list(
          list(query = intersects,
               params = list('SetA', 'SetB'),
               color = '#E64B35',
               active = TRUE),
          list(query = intersects,
               params = list('SetA', 'SetC', 'SetD'),
               color = '#4DBBD5',
               active = TRUE)
      ))

# Highlight elements matching criteria
# Requires attribute data frame with element names as row names
upset(fromList(gene_sets),
      queries = list(
          list(query = elements,
               params = list('logFC', 1, 2),  # column, min, max
               color = 'red',
               active = TRUE)
      ))
```

## UpSetR with Metadata Boxplots

```r
# Add attribute plots below intersection matrix
# Requires data frame with set membership columns + attribute columns
upset(data,
      order.by = 'freq',
      boxplot.summary = c('logFC', 'pvalue'))

# Custom attribute plots
upset(data,
      order.by = 'freq',
      attribute.plots = list(
          gridrows = 50,
          plots = list(
              list(plot = histogram, x = 'logFC', queries = FALSE),
              list(plot = scatter_plot, x = 'logFC', y = 'pvalue', queries = TRUE)
          ),
          ncols = 2
      ))
```

## upsetplot (Python) - Basic

```python
from upsetplot import from_memberships, plot, UpSet
import matplotlib.pyplot as plt

# From membership lists
memberships = [
    ['SetA', 'SetB'],
    ['SetA'],
    ['SetB', 'SetC'],
    ['SetA', 'SetB', 'SetC'],
    ['SetC'],
    ['SetA', 'SetC']
]
data = from_memberships(memberships)

# Basic plot
plot(data, show_counts=True)
plt.savefig('upset.png', dpi=150, bbox_inches='tight')
```

## upsetplot from DataFrame

```python
import pandas as pd
from upsetplot import from_contents, UpSet

# From dict of sets
gene_sets = {
    'SetA': ['Gene1', 'Gene2', 'Gene3', 'Gene4'],
    'SetB': ['Gene2', 'Gene3', 'Gene5', 'Gene6'],
    'SetC': ['Gene1', 'Gene3', 'Gene6', 'Gene7']
}
data = from_contents(gene_sets)

upset = UpSet(data, subset_size='count', show_counts=True, sort_by='cardinality')
upset.plot()
plt.savefig('upset.png', dpi=150, bbox_inches='tight')
```

## upsetplot Customization

```python
from upsetplot import UpSet

upset = UpSet(data,
              subset_size='count',
              show_counts=True,
              show_percentages=True,
              sort_by='cardinality',  # or 'degree'
              sort_categories_by='cardinality',
              facecolor='#4DBBD5',
              element_size=40,
              intersection_plot_elements=10)

fig = plt.figure(figsize=(12, 8))
upset.plot(fig=fig)
```

## upsetplot with Metadata

```python
# Add data attributes for additional plots
df = pd.DataFrame({
    'SetA': [True, True, False, True, False],
    'SetB': [True, False, True, True, False],
    'SetC': [False, True, True, False, True],
    'logFC': [1.2, -0.8, 2.1, 0.5, -1.5],
    'pvalue': [0.01, 0.05, 0.001, 0.2, 0.03]
})
df = df.set_index(['SetA', 'SetB', 'SetC'])

upset = UpSet(df, subset_size='count')
upset.add_stacked_bars(by='significant', colors=['gray', 'red'])
# Or: upset.add_catplot(value='logFC', kind='box')
upset.plot()
```

## Save UpSet Plots

```r
# R - to PDF
pdf('upset_plot.pdf', width = 10, height = 6)
upset(fromList(gene_sets), order.by = 'freq')
dev.off()

# R - to PNG
png('upset_plot.png', width = 10, height = 6, units = 'in', res = 300)
upset(fromList(gene_sets), order.by = 'freq')
dev.off()
```

```python
# Python
fig = plt.figure(figsize=(10, 6))
upset.plot(fig=fig)
plt.savefig('upset.pdf', bbox_inches='tight')
plt.savefig('upset.png', dpi=300, bbox_inches='tight')
```

## Related Skills

- data-visualization/heatmaps-clustering - Alternative for smaller sets
- pathway-analysis/enrichment-visualization - Gene set overlaps
- differential-expression/de-results - DE gene set comparisons
