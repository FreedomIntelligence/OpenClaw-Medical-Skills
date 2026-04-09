# data-visualization-biomedical

> Publication-quality visualizations for biomedical and genomics data. Use when creating volcano plots, heatmaps, UMAP plots, dot plots, survival curves, forest plots, or multi-panel figures. Includes scanpy, matplotlib, seaborn, plotly workflows with journal-ready aesthetics and proper statistical annotations.

# Biomedical Data Visualization

## Publication-Quality Settings

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Nature/Blood style settings
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 8,
    'axes.labelsize': 8,
    'axes.titlesize': 9,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.linewidth': 0.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
})

# Color palettes
NATURE_COLORS = ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F', '#8491B4']
BLOOD_COLORS = ['#D62728', '#1F77B4', '#2CA02C', '#FF7F0E', '#9467BD', '#8C564B']
```

## Volcano Plot

```python
def volcano_plot(df, log2fc_col='log2FC', pval_col='pval_adj', 
                 gene_col='gene', fc_thresh=1, pval_thresh=0.05,
                 highlight_genes=None, figsize=(4, 4)):
    """Publication-quality volcano plot."""
    fig, ax = plt.subplots(figsize=figsize)
    
    df = df.copy()
    df['-log10pval'] = -np.log10(df[pval_col].clip(lower=1e-300))
    
    # Categorize points
    df['category'] = 'NS'
    df.loc[(df[log2fc_col] > fc_thresh) & (df[pval_col] < pval_thresh), 'category'] = 'Up'
    df.loc[(df[log2fc_col] < -fc_thresh) & (df[pval_col] < pval_thresh), 'category'] = 'Down'
    
    colors = {'NS': '#CCCCCC', 'Up': '#E64B35', 'Down': '#4DBBD5'}
    
    for cat, color in colors.items():
        subset = df[df['category'] == cat]
        ax.scatter(subset[log2fc_col], subset['-log10pval'], 
                   c=color, s=10, alpha=0.7, edgecolors='none', label=cat)
    
    # Add threshold lines
    ax.axhline(-np.log10(pval_thresh), color='grey', linestyle='--', linewidth=0.5)
    ax.axvline(-fc_thresh, color='grey', linestyle='--', linewidth=0.5)
    ax.axvline(fc_thresh, color='grey', linestyle='--', linewidth=0.5)
    
    # Label specific genes
    if highlight_genes:
        for gene in highlight_genes:
            if gene in df[gene_col].values:
                row = df[df[gene_col] == gene].iloc[0]
                ax.annotate(gene, (row[log2fc_col], row['-log10pval']),
                           fontsize=6, ha='center')
    
    ax.set_xlabel('log₂ Fold Change')
    ax.set_ylabel('-log₁₀ Adjusted P-value')
    ax.legend(frameon=False, loc='upper right')
    
    plt.tight_layout()
    return fig, ax
```

## Heatmap with Clustering

```python
import scipy.cluster.hierarchy as sch
from matplotlib.colors import LinearSegmentedColormap

def clustered_heatmap(data, row_labels=None, col_labels=None,
                      cmap='RdBu_r', center=0, figsize=(8, 10),
                      row_cluster=True, col_cluster=True):
    """Hierarchically clustered heatmap."""
    
    # Clustering
    if row_cluster:
        row_linkage = sch.linkage(data, method='ward')
        row_order = sch.dendrogram(row_linkage, no_plot=True)['leaves']
        data = data[row_order, :]
        if row_labels is not None:
            row_labels = [row_labels[i] for i in row_order]
    
    if col_cluster:
        col_linkage = sch.linkage(data.T, method='ward')
        col_order = sch.dendrogram(col_linkage, no_plot=True)['leaves']
        data = data[:, col_order]
        if col_labels is not None:
            col_labels = [col_labels[i] for i in col_order]
    
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(data, aspect='auto', cmap=cmap, 
                   vmin=center-np.abs(data).max(), vmax=center+np.abs(data).max())
    
    if row_labels:
        ax.set_yticks(range(len(row_labels)))
        ax.set_yticklabels(row_labels)
    if col_labels:
        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha='right')
    
    plt.colorbar(im, ax=ax, shrink=0.5, label='Expression (z-score)')
    plt.tight_layout()
    return fig, ax
```

## Scanpy Visualization Enhancements

```python
import scanpy as sc

def enhanced_dotplot(adata, genes, groupby, figsize=(10, 8)):
    """Enhanced dot plot with proper visibility."""
    sc.pl.dotplot(
        adata, var_names=genes, groupby=groupby,
        expression_cutoff=0.0001,
        mean_only_expressed=False,
        standard_scale='None',
        smallest_dot=0.1,
        dot_max=1.0,
        cmap='Reds',
        colorbar_title='Mean expression',
        size_title='Fraction of cells (%)',
        figsize=figsize,
        show=False
    )
    plt.tight_layout()
    return plt.gcf()

def multi_batch_umap(adata, color_by, batch_key='batch', figsize_per=(4, 4)):
    """UMAP plots per batch."""
    batches = adata.obs[batch_key].unique()
    n_batches = len(batches)
    
    fig, axes = plt.subplots(1, n_batches, 
                              figsize=(figsize_per[0]*n_batches, figsize_per[1]))
    if n_batches == 1:
        axes = [axes]
    
    for ax, batch in zip(axes, batches):
        adata_batch = adata[adata.obs[batch_key] == batch]
        sc.pl.umap(adata_batch, color=color_by, ax=ax, show=False,
                   title=f'{batch}')
    
    plt.tight_layout()
    return fig
```

## Statistical Annotation

```python
from scipy import stats

def add_significance(ax, x1, x2, y, h, p_value):
    """Add significance bar to plot."""
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], 'k-', linewidth=0.5)
    
    if p_value < 0.0001:
        sig = '****'
    elif p_value < 0.001:
        sig = '***'
    elif p_value < 0.01:
        sig = '**'
    elif p_value < 0.05:
        sig = '*'
    else:
        sig = 'ns'
    
    ax.text((x1+x2)/2, y+h, sig, ha='center', va='bottom', fontsize=8)
```

## Multi-Panel Figure Assembly

```python
from matplotlib.gridspec import GridSpec

def create_figure_panel(n_rows, n_cols, width_ratios=None, height_ratios=None):
    """Create multi-panel figure."""
    fig = plt.figure(figsize=(3*n_cols, 3*n_rows))
    gs = GridSpec(n_rows, n_cols, figure=fig,
                  width_ratios=width_ratios or [1]*n_cols,
                  height_ratios=height_ratios or [1]*n_rows,
                  wspace=0.3, hspace=0.3)
    
    axes = []
    for i in range(n_rows):
        row = []
        for j in range(n_cols):
            ax = fig.add_subplot(gs[i, j])
            row.append(ax)
        axes.append(row)
    
    return fig, axes

def label_panels(axes, labels=None, fontsize=12, fontweight='bold'):
    """Add A, B, C... labels to panels."""
    if labels is None:
        labels = [chr(65+i) for i in range(len(axes))]  # A, B, C...
    
    for ax, label in zip(axes, labels):
        ax.text(-0.15, 1.05, label, transform=ax.transAxes,
                fontsize=fontsize, fontweight=fontweight, va='top')
```

## Export for Journals

```python
def save_figure(fig, filename, formats=['pdf', 'png', 'svg']):
    """Save in multiple formats for journals."""
    for fmt in formats:
        fig.savefig(f"{filename}.{fmt}", format=fmt, dpi=300, 
                    bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Saved: {filename}.{{{'|'.join(formats)}}}")
```

See `references/color_guidelines.md` for accessibility standards.
See `scripts/figure_templates.py` for pre-built templates.
