# bio-data-visualization-interactive-visualization

> Create interactive HTML plots with plotly and bokeh for exploratory data analysis and web-based sharing of omics visualizations. Use when building zoomable, hoverable plots for data exploration or web dashboards.

**Available tools:** Read, Bash

# Interactive Visualization

## plotly (Python)

```python
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Scatter plot
fig = px.scatter(df, x='PC1', y='PC2', color='condition', hover_data=['sample'],
                 title='PCA Plot')
fig.write_html('pca_interactive.html')
fig.show()
```

## Interactive Volcano Plot

```python
import plotly.express as px

df['neg_log_pval'] = -np.log10(df['pvalue'])
df['significant'] = (df['padj'] < 0.05) & (abs(df['log2FoldChange']) > 1)

fig = px.scatter(df, x='log2FoldChange', y='neg_log_pval',
                 color='significant', hover_name='gene',
                 hover_data=['baseMean', 'padj'],
                 color_discrete_map={True: 'red', False: 'grey'},
                 title='Interactive Volcano Plot')

fig.add_hline(y=-np.log10(0.05), line_dash='dash', line_color='grey')
fig.add_vline(x=-1, line_dash='dash', line_color='grey')
fig.add_vline(x=1, line_dash='dash', line_color='grey')

fig.update_layout(xaxis_title='Log2 Fold Change', yaxis_title='-Log10 P-value')
fig.write_html('volcano_interactive.html')
```

## Interactive Heatmap

```python
import plotly.express as px

fig = px.imshow(df, color_continuous_scale='RdBu_r', aspect='auto',
                labels=dict(x='Samples', y='Genes', color='Expression'))
fig.update_xaxes(tickangle=45)
fig.write_html('heatmap_interactive.html')
```

## plotly with Subplots

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(rows=1, cols=2, subplot_titles=('PCA', 'Volcano'))

fig.add_trace(go.Scatter(x=df['PC1'], y=df['PC2'], mode='markers',
                          marker=dict(color=df['condition'].map({'Control': 'blue', 'Treatment': 'red'})),
                          text=df['sample'], name='PCA'), row=1, col=1)

fig.add_trace(go.Scatter(x=de['log2FC'], y=-np.log10(de['pvalue']), mode='markers',
                          marker=dict(color=de['significant'].map({True: 'red', False: 'grey'})),
                          text=de['gene'], name='Volcano'), row=1, col=2)

fig.update_layout(height=500, width=1000, showlegend=False)
fig.write_html('combined_interactive.html')
```

## plotly (R)

```r
library(plotly)

# From ggplot2
p <- ggplot(df, aes(PC1, PC2, color = condition, text = sample)) +
    geom_point()
ggplotly(p)

# Native plotly
plot_ly(df, x = ~PC1, y = ~PC2, color = ~condition, text = ~sample,
        type = 'scatter', mode = 'markers') %>%
    layout(title = 'PCA Plot')
```

## Interactive MA Plot

```r
library(plotly)

de_results$text <- paste0('Gene: ', de_results$gene, '<br>',
                           'baseMean: ', round(de_results$baseMean, 2), '<br>',
                           'log2FC: ', round(de_results$log2FoldChange, 2), '<br>',
                           'padj: ', formatC(de_results$padj, format = 'e', digits = 2))

plot_ly(de_results, x = ~log10(baseMean), y = ~log2FoldChange,
        color = ~(padj < 0.05), colors = c('grey', 'red'),
        text = ~text, hoverinfo = 'text',
        type = 'scatter', mode = 'markers', marker = list(size = 5, opacity = 0.6)) %>%
    layout(title = 'MA Plot',
           xaxis = list(title = 'Log10 Mean Expression'),
           yaxis = list(title = 'Log2 Fold Change'))
```

## Linked Brushing

```python
import plotly.express as px
from plotly.subplots import make_subplots

fig = px.scatter_matrix(df, dimensions=['PC1', 'PC2', 'PC3'], color='condition')
fig.write_html('scatter_matrix.html')
```

## bokeh (Python)

```python
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, HoverTool

output_file('pca_bokeh.html')

source = ColumnDataSource(df)

p = figure(title='PCA Plot', x_axis_label='PC1', y_axis_label='PC2',
           tools='pan,wheel_zoom,box_zoom,reset,hover,save')

p.circle('PC1', 'PC2', source=source, size=10, alpha=0.6,
         color='color', legend_field='condition')

hover = p.select(dict(type=HoverTool))
hover.tooltips = [('Sample', '@sample'), ('Condition', '@condition')]

save(p)
```

## bokeh with Widgets

```python
from bokeh.layouts import column
from bokeh.models import Select
from bokeh.io import curdoc

select = Select(title='Color by:', value='condition',
                options=['condition', 'batch', 'cluster'])

def update(attr, old, new):
    p.circle.glyph.fill_color = new

select.on_change('value', update)
curdoc().add_root(column(select, p))
```

## Save Interactive Plots

```python
# plotly
fig.write_html('plot.html')
fig.write_json('plot.json')

# bokeh
from bokeh.io import save, export_png
save(p, filename='plot.html')
export_png(p, filename='plot.png')  # requires selenium
```

## Embed in Jupyter

```python
# plotly - works automatically in Jupyter
fig.show()

# bokeh
from bokeh.io import output_notebook, show
output_notebook()
show(p)
```

## Related Skills

- data-visualization/ggplot2-fundamentals - Static plots
- data-visualization/specialized-omics-plots - Omics-specific plots
- reporting/quarto-reports - Embed in reports
