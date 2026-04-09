# bio-tcr-bcr-analysis-repertoire-visualization

> Create publication-quality visualizations of immune repertoire data including circos plots, clone tracking, diversity plots, and network graphs. Use when generating figures for repertoire comparisons, clonal dynamics, or V(D)J gene usage.

## Version Compatibility

Reference examples tested with: MiXCR 4.6+, VDJtools 1.2.1+, ggplot2 3.5+, matplotlib 3.8+, pandas 2.2+, scanpy 1.10+, seaborn 0.13+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Repertoire Visualization

**"Visualize my immune repertoire data"** → Create publication-quality figures for TCR/BCR repertoires including circos plots, V(D)J gene usage heatmaps, diversity plots, and clonal tracking across samples.
- CLI: `vdjtools PlotFancyVJUsage` for circos-style V-J plots
- Python: `matplotlib`/`seaborn` for custom repertoire visualizations

## Circos Plots (V-J Gene Usage)

### VDJtools

```bash
# Generate V-J usage circos plot
vdjtools PlotFancyVJUsage \
    -m metadata.txt \
    output_dir/

# Generates PDF circos plots showing V-J pairing frequencies
```

### Python with pyCircos

```python
import pandas as pd
import matplotlib.pyplot as plt
from pycircos import Gcircle

def plot_vj_circos(clone_df):
    '''Create circos plot of V-J usage'''
    # Count V-J pairs
    vj_counts = clone_df.groupby(['v_gene', 'j_gene']).size().reset_index(name='count')

    # Create circos
    circle = Gcircle()

    # Add arcs for each V and J gene
    v_genes = vj_counts['v_gene'].unique()
    j_genes = vj_counts['j_gene'].unique()

    # Add sectors and links
    # ... (complex setup)

    circle.save('vj_circos.pdf')
```

### R with circlize

```r
library(circlize)

plot_vj_circos <- function(clone_df) {
    # Prepare adjacency matrix
    vj_matrix <- table(clone_df$v_gene, clone_df$j_gene)

    # Create circos plot
    chordDiagram(
        vj_matrix,
        transparency = 0.5,
        annotationTrack = c("grid", "name")
    )
}
```

## Clone Tracking Over Time

```python
import pandas as pd
import matplotlib.pyplot as plt

def plot_clone_tracking(clones_by_time, top_n=10):
    '''Track top clones across timepoints'''

    # Get top clones by total frequency
    total_freq = clones_by_time.groupby('cdr3_aa')['frequency'].sum()
    top_clones = total_freq.nlargest(top_n).index

    fig, ax = plt.subplots(figsize=(10, 6))

    for clone in top_clones:
        clone_data = clones_by_time[clones_by_time['cdr3_aa'] == clone]
        ax.plot(clone_data['timepoint'], clone_data['frequency'],
                marker='o', label=clone[:20])

    ax.set_xlabel('Timepoint')
    ax.set_ylabel('Clone Frequency')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('clone_tracking.pdf')
```

## Diversity Plots

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_diversity_comparison(diversity_df, metric='shannon'):
    '''Compare diversity between groups'''

    fig, ax = plt.subplots(figsize=(8, 6))

    sns.boxplot(
        data=diversity_df,
        x='condition',
        y=metric,
        ax=ax
    )
    sns.stripplot(
        data=diversity_df,
        x='condition',
        y=metric,
        color='black',
        alpha=0.5,
        ax=ax
    )

    ax.set_ylabel(f'{metric.capitalize()} Diversity')
    plt.savefig('diversity_comparison.pdf')
```

## Overlap Heatmap

```python
def plot_overlap_heatmap(overlap_matrix):
    '''Plot pairwise repertoire overlap'''
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        overlap_matrix,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        ax=ax
    )

    ax.set_title('Repertoire Overlap (Jaccard Index)')
    plt.tight_layout()
    plt.savefig('overlap_heatmap.pdf')
```

## Spectratype Plot

```python
def plot_spectratype(clone_df, group_col=None):
    '''Plot CDR3 length distribution'''

    fig, ax = plt.subplots(figsize=(10, 6))

    clone_df['cdr3_length'] = clone_df['cdr3_nt'].str.len()

    if group_col:
        for group, data in clone_df.groupby(group_col):
            ax.hist(data['cdr3_length'], bins=range(20, 80, 3),
                    alpha=0.5, label=group, density=True)
        ax.legend()
    else:
        ax.hist(clone_df['cdr3_length'], bins=range(20, 80, 3))

    ax.set_xlabel('CDR3 Length (nt)')
    ax.set_ylabel('Density')
    ax.set_title('CDR3 Length Distribution (Spectratype)')
    plt.savefig('spectratype.pdf')
```

## Clonotype Network

```python
import networkx as nx

def plot_clone_network(clone_df, similarity_threshold=0.8):
    '''Create network of similar clonotypes'''
    from Levenshtein import ratio

    G = nx.Graph()

    clones = clone_df['cdr3_aa'].unique()

    # Add nodes
    for clone in clones:
        freq = clone_df[clone_df['cdr3_aa'] == clone]['frequency'].sum()
        G.add_node(clone, size=freq)

    # Add edges for similar clones
    for i, c1 in enumerate(clones):
        for c2 in clones[i+1:]:
            sim = ratio(c1, c2)
            if sim >= similarity_threshold:
                G.add_edge(c1, c2, weight=sim)

    # Draw network
    fig, ax = plt.subplots(figsize=(12, 12))
    pos = nx.spring_layout(G)

    sizes = [G.nodes[n]['size'] * 1000 for n in G.nodes()]
    nx.draw(G, pos, node_size=sizes, with_labels=False, ax=ax)

    plt.savefig('clone_network.pdf')
```

## Related Skills

- vdjtools-analysis - Generate input data
- mixcr-analysis - Generate clonotype tables
- data-visualization/ggplot2-fundamentals - General plotting concepts
