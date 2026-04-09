# data-viz-plots

> Create publication-quality plots and visualizations using matplotlib and seaborn. Works with ANY LLM provider (GPT, Gemini, Claude, etc.).

# Data Visualization (Universal)

## Overview
This skill enables you to create professional scientific visualizations including scatter plots, line charts, heatmaps, violin plots, and more. Unlike cloud-hosted solutions, this skill uses the **matplotlib** and **seaborn** Python libraries and executes **locally** in your environment, making it compatible with **ALL LLM providers** including GPT, Gemini, Claude, DeepSeek, and Qwen.

## When to Use This Skill
- Create publication-quality figures for papers and presentations
- Generate exploratory data analysis (EDA) plots
- Visualize gene expression, QC metrics, or clustering results
- Create multi-panel figures combining different plot types
- Export high-resolution images for reports
- Customize plot aesthetics (colors, fonts, styles)

## How to Use

### Step 1: Import Required Libraries
```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import gridspec
import matplotlib.patches as mpatches

# Set style for publication-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
```

### Step 2: Basic Scatter Plot
```python
# Create figure and axis
fig, ax = plt.subplots(figsize=(6, 5))

# Scatter plot
ax.scatter(x_data, y_data, s=20, alpha=0.6, c='steelblue', edgecolors='k', linewidths=0.5)

# Labels and title
ax.set_xlabel('Gene Expression (log2)', fontsize=12)
ax.set_ylabel('Cell Count', fontsize=12)
ax.set_title('Expression vs. Cell Count', fontsize=14, fontweight='bold')

# Grid and styling
ax.grid(alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save figure
plt.tight_layout()
plt.savefig('scatter_plot.png', dpi=300, bbox_inches='tight')
plt.show()
print("✅ Scatter plot saved to: scatter_plot.png")
```

### Step 3: Line Plot with Multiple Series
```python
fig, ax = plt.subplots(figsize=(8, 5))

# Plot multiple lines
ax.plot(time_points, group1_values, marker='o', label='Group 1', color='#E74C3C', linewidth=2)
ax.plot(time_points, group2_values, marker='s', label='Group 2', color='#3498DB', linewidth=2)
ax.plot(time_points, group3_values, marker='^', label='Group 3', color='#2ECC71', linewidth=2)

# Styling
ax.set_xlabel('Time Point', fontsize=12)
ax.set_ylabel('Expression Level', fontsize=12)
ax.set_title('Gene Expression Over Time', fontsize=14, fontweight='bold')
ax.legend(frameon=True, loc='best', fontsize=10)
ax.grid(alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('line_plot.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Step 4: Box Plot and Violin Plot
```python
# Prepare data (long-form DataFrame)
# df should have columns: 'cluster', 'expression', 'gene', etc.

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Box plot
sns.boxplot(data=df, x='cluster', y='expression', palette='Set2', ax=ax1)
ax1.set_title('Box Plot: Expression by Cluster', fontsize=12, fontweight='bold')
ax1.set_xlabel('Cluster', fontsize=11)
ax1.set_ylabel('Expression Level', fontsize=11)
ax1.tick_params(axis='x', rotation=45)

# Violin plot
sns.violinplot(data=df, x='cluster', y='expression', palette='muted', ax=ax2, inner='quartile')
ax2.set_title('Violin Plot: Expression Distribution', fontsize=12, fontweight='bold')
ax2.set_xlabel('Cluster', fontsize=11)
ax2.set_ylabel('Expression Level', fontsize=11)
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('box_violin_plot.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Step 5: Heatmap
```python
# Prepare data matrix (rows=genes, columns=samples or clusters)
# gene_expression_matrix: pandas DataFrame or numpy array

fig, ax = plt.subplots(figsize=(8, 6))

# Create heatmap
sns.heatmap(
    gene_expression_matrix,
    cmap='viridis',
    cbar_kws={'label': 'Expression'},
    xticklabels=True,
    yticklabels=True,
    linewidths=0.5,
    linecolor='gray',
    ax=ax
)

ax.set_title('Gene Expression Heatmap', fontsize=14, fontweight='bold')
ax.set_xlabel('Samples', fontsize=12)
ax.set_ylabel('Genes', fontsize=12)

plt.tight_layout()
plt.savefig('heatmap.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Step 6: Bar Plot with Error Bars
```python
fig, ax = plt.subplots(figsize=(7, 5))

# Data
categories = ['Cluster 0', 'Cluster 1', 'Cluster 2', 'Cluster 3']
means = [120, 85, 200, 150]
errors = [15, 10, 25, 20]

# Bar plot
bars = ax.bar(categories, means, yerr=errors, capsize=5,
               color=['#E74C3C', '#3498DB', '#2ECC71', '#F39C12'],
               edgecolor='black', linewidth=1.2, alpha=0.8)

# Labels
ax.set_ylabel('Cell Count', fontsize=12)
ax.set_title('Cell Counts by Cluster', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(means) * 1.3)

# Add value labels on bars
for bar, mean in zip(bars, means):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 5,
            f'{mean}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('bar_plot.png', dpi=300, bbox_inches='tight')
plt.show()
```

## Advanced Features

### Multi-Panel Figure
```python
# Create complex layout
fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)

# Panel A: Scatter
ax1 = fig.add_subplot(gs[0, :2])
ax1.scatter(x_data, y_data, c=cluster_labels, cmap='tab10', s=10, alpha=0.6)
ax1.set_title('A. UMAP Projection', fontsize=12, fontweight='bold', loc='left')
ax1.set_xlabel('UMAP1')
ax1.set_ylabel('UMAP2')

# Panel B: Violin
ax2 = fig.add_subplot(gs[0, 2])
sns.violinplot(data=df, y='expression', palette='Set2', ax=ax2)
ax2.set_title('B. Expression', fontsize=12, fontweight='bold', loc='left')

# Panel C: Heatmap
ax3 = fig.add_subplot(gs[1, :])
sns.heatmap(matrix, cmap='coolwarm', center=0, ax=ax3, cbar_kws={'label': 'Z-score'})
ax3.set_title('C. Gene Expression Heatmap', fontsize=12, fontweight='bold', loc='left')

plt.savefig('multi_panel_figure.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Custom Color Palette
```python
# Define custom colors
custom_palette = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6']

# Use in seaborn
sns.set_palette(custom_palette)

# Or create color dict for specific mapping
color_dict = {
    'T cells': '#E74C3C',
    'B cells': '#3498DB',
    'Monocytes': '#2ECC71',
    'NK cells': '#F39C12'
}

# Use in scatter plot
for cell_type, color in color_dict.items():
    mask = df['celltype'] == cell_type
    ax.scatter(df.loc[mask, 'x'], df.loc[mask, 'y'],
               c=color, label=cell_type, s=20, alpha=0.7)
ax.legend()
```

### Density Plot
```python
from scipy.stats import gaussian_kde

fig, ax = plt.subplots(figsize=(8, 6))

# Calculate density
xy = np.vstack([x_data, y_data])
z = gaussian_kde(xy)(xy)

# Sort points by density for better visualization
idx = z.argsort()
x, y, z = x_data[idx], y_data[idx], z[idx]

# Scatter with density colors
scatter = ax.scatter(x, y, c=z, s=20, cmap='viridis', alpha=0.6, edgecolors='none')
plt.colorbar(scatter, ax=ax, label='Density')

ax.set_xlabel('UMAP1', fontsize=12)
ax.set_ylabel('UMAP2', fontsize=12)
ax.set_title('Density Scatter Plot', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('density_plot.png', dpi=300, bbox_inches='tight')
plt.show()
```

## Common Use Cases

### QC Metrics Visualization
```python
# Assuming adata.obs has QC columns: n_genes, n_counts, percent_mito

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot 1: Histogram of genes per cell
axes[0].hist(adata.obs['n_genes'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
axes[0].axvline(adata.obs['n_genes'].median(), color='red', linestyle='--', label='Median')
axes[0].set_xlabel('Genes per Cell', fontsize=11)
axes[0].set_ylabel('Frequency', fontsize=11)
axes[0].set_title('Genes per Cell Distribution', fontsize=12, fontweight='bold')
axes[0].legend()

# Plot 2: Scatter UMI vs Genes
axes[1].scatter(adata.obs['n_counts'], adata.obs['n_genes'],
                s=5, alpha=0.5, c='coral')
axes[1].set_xlabel('UMI Counts', fontsize=11)
axes[1].set_ylabel('Genes Detected', fontsize=11)
axes[1].set_title('UMIs vs Genes', fontsize=12, fontweight='bold')

# Plot 3: Violin plot of mitochondrial percentage
sns.violinplot(y=adata.obs['percent_mito'], ax=axes[2], color='lightgreen')
axes[2].axhline(y=20, color='red', linestyle='--', label='20% threshold')
axes[2].set_ylabel('Mitochondrial %', fontsize=11)
axes[2].set_title('Mitochondrial Content', fontsize=12, fontweight='bold')
axes[2].legend()

plt.tight_layout()
plt.savefig('qc_metrics.png', dpi=300, bbox_inches='tight')
plt.show()
```

### UMAP/tSNE Visualization
```python
# Assuming adata.obsm['X_umap'] exists and adata.obs['clusters'] exists

fig, ax = plt.subplots(figsize=(8, 7))

# Get unique clusters
clusters = adata.obs['clusters'].unique()
n_clusters = len(clusters)

# Generate colors
colors = plt.cm.tab20(np.linspace(0, 1, n_clusters))

# Plot each cluster
for i, cluster in enumerate(clusters):
    mask = adata.obs['clusters'] == cluster
    ax.scatter(
        adata.obsm['X_umap'][mask, 0],
        adata.obsm['X_umap'][mask, 1],
        c=[colors[i]],
        label=f'Cluster {cluster}',
        s=10,
        alpha=0.7,
        edgecolors='none'
    )

ax.set_xlabel('UMAP1', fontsize=12)
ax.set_ylabel('UMAP2', fontsize=12)
ax.set_title('UMAP Projection by Cluster', fontsize=14, fontweight='bold')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, fontsize=9)

plt.tight_layout()
plt.savefig('umap_clusters.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Gene Expression Dot Plot
```python
# genes: list of gene names
# clusters: list of cluster IDs
# Create matrix: rows=genes, columns=clusters with mean expression and % expressing

fig, ax = plt.subplots(figsize=(10, 6))

# Prepare data
from matplotlib.colors import Normalize

# dot_size_matrix: % cells expressing (0-100)
# color_matrix: mean expression level

for i, gene in enumerate(genes):
    for j, cluster in enumerate(clusters):
        # Size proportional to % expressing
        size = dot_size_matrix[i, j] * 5  # Scale factor
        # Color by expression level
        color_val = color_matrix[i, j]

        ax.scatter(j, i, s=size, c=[color_val], cmap='Reds',
                   vmin=0, vmax=color_matrix.max(),
                   edgecolors='black', linewidths=0.5)

# Labels
ax.set_xticks(range(len(clusters)))
ax.set_xticklabels(clusters, rotation=45, ha='right')
ax.set_yticks(range(len(genes)))
ax.set_yticklabels(genes)
ax.set_xlabel('Cluster', fontsize=12)
ax.set_ylabel('Gene', fontsize=12)
ax.set_title('Marker Gene Expression', fontsize=14, fontweight='bold')

# Colorbar
norm = Normalize(vmin=0, vmax=color_matrix.max())
sm = plt.cm.ScalarMappable(cmap='Reds', norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, pad=0.02)
cbar.set_label('Mean Expression', rotation=270, labelpad=15)

plt.tight_layout()
plt.savefig('gene_dotplot.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Volcano Plot (DEG Analysis)
```python
# Assuming deg_df has columns: gene, log2FC, pvalue

fig, ax = plt.subplots(figsize=(8, 7))

# Calculate -log10(pvalue)
deg_df['-log10_pvalue'] = -np.log10(deg_df['pvalue'])

# Classify genes
deg_df['significant'] = 'Not Significant'
deg_df.loc[(deg_df['log2FC'] > 1) & (deg_df['pvalue'] < 0.05), 'significant'] = 'Up-regulated'
deg_df.loc[(deg_df['log2FC'] < -1) & (deg_df['pvalue'] < 0.05), 'significant'] = 'Down-regulated'

# Plot
for category, color in zip(['Not Significant', 'Up-regulated', 'Down-regulated'],
                            ['gray', 'red', 'blue']):
    mask = deg_df['significant'] == category
    ax.scatter(deg_df.loc[mask, 'log2FC'],
               deg_df.loc[mask, '-log10_pvalue'],
               c=color, label=category, s=20, alpha=0.6, edgecolors='none')

# Threshold lines
ax.axvline(x=1, color='black', linestyle='--', linewidth=1, alpha=0.5)
ax.axvline(x=-1, color='black', linestyle='--', linewidth=1, alpha=0.5)
ax.axhline(y=-np.log10(0.05), color='black', linestyle='--', linewidth=1, alpha=0.5)

# Labels
ax.set_xlabel('log2 Fold Change', fontsize=12)
ax.set_ylabel('-log10(p-value)', fontsize=12)
ax.set_title('Volcano Plot: Differential Expression', fontsize=14, fontweight='bold')
ax.legend(frameon=True, loc='upper right')

plt.tight_layout()
plt.savefig('volcano_plot.png', dpi=300, bbox_inches='tight')
plt.show()
```

## Best Practices

1. **Figure Size**: Use appropriate dimensions for target medium (papers: 6-8 inches wide, posters: larger)
2. **DPI**: Save at 300 DPI for publications, 150 DPI for presentations
3. **Colors**: Use colorblind-friendly palettes (e.g., `viridis`, `Set2`, `tab10`)
4. **Fonts**: Keep font sizes readable (titles: 12-14pt, labels: 10-12pt, ticks: 8-10pt)
5. **Transparency**: Use alpha for overlapping points to show density
6. **Layout**: Always call `plt.tight_layout()` before saving to prevent label clipping
7. **File Format**: PNG for general use, SVG for vector graphics (editable in Illustrator)
8. **Close Figures**: Call `plt.close()` after saving to free memory when generating many plots

## Troubleshooting

### Issue: "Figure too cluttered with many points"
**Solution**: Use transparency and smaller point sizes
```python
ax.scatter(x, y, s=5, alpha=0.3, edgecolors='none')
```

### Issue: "Legend overlaps with data"
**Solution**: Place legend outside the plot area
```python
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
```

### Issue: "Labels are cut off in saved figure"
**Solution**: Use `bbox_inches='tight'`
```python
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
```

### Issue: "Colors don't match between plots"
**Solution**: Define color palette once and reuse
```python
PALETTE = {'Group A': '#E74C3C', 'Group B': '#3498DB'}
# Use PALETTE in all plots
```

### Issue: "Heatmap text too small"
**Solution**: Adjust figure size or font size
```python
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(data, ax=ax, annot_kws={'fontsize': 8})
```

## Technical Notes

- **Libraries**: Uses `matplotlib` and `seaborn` (widely supported, stable)
- **Execution**: Runs locally in the agent's sandbox
- **Compatibility**: Works with ALL LLM providers (GPT, Gemini, Claude, DeepSeek, Qwen, etc.)
- **File Formats**: Supports PNG, PDF, SVG, JPEG
- **Performance**: Typical plot generation takes <1 second for standard plots, 2-5 seconds for complex multi-panel figures
- **Memory**: Keep figure count reasonable; close figures after saving if generating many plots

## References
- Matplotlib documentation: https://matplotlib.org/stable/contents.html
- Seaborn documentation: https://seaborn.pydata.org/
- Matplotlib gallery: https://matplotlib.org/stable/gallery/index.html
- Seaborn gallery: https://seaborn.pydata.org/examples/index.html
