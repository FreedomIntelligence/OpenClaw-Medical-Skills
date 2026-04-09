# bio-copy-number-cnv-visualization

> Visualize copy number profiles, segments, and compare across samples. Create publication-quality plots of CNV data from CNVkit, GATK, or other callers. Use when creating genome-wide CNV plots, sample heatmaps, or chromosome-level visualizations.

## Version Compatibility

Reference examples tested with: GATK 4.5+, ggplot2 3.5+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, seaborn 0.13+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# CNV Visualization

**"Plot my copy number profile"** → Create genome-wide scatter plots, segmentation views, and multi-sample heatmaps from CNV caller output.
- CLI: `cnvkit.py scatter`, `cnvkit.py diagram`, `cnvkit.py heatmap`
- Python: `matplotlib` for custom CNV plots
- R: `ggplot2` for publication figures

## CNVkit Built-in Plots

**Goal:** Generate standard CNV visualizations directly from CNVkit output files.

**Approach:** Use CNVkit scatter, diagram, and heatmap commands for quick visual inspection.

```bash
# Scatter plot with segments
cnvkit.py scatter sample.cnr -s sample.cns -o scatter.png

# Scatter for specific chromosome
cnvkit.py scatter sample.cnr -s sample.cns -c chr17 -o chr17_scatter.png

# Ideogram diagram
cnvkit.py diagram sample.cnr -s sample.cns -o diagram.pdf

# Heatmap across samples
cnvkit.py heatmap *.cns -o cohort_heatmap.pdf

# Heatmap for specific region
cnvkit.py heatmap *.cns -c chr17:7500000-7700000 -o tp53_region.pdf
```

## Python: Genome-wide Profile

**Goal:** Create a genome-wide CNV scatter plot with colored segments across all chromosomes.

**Approach:** Calculate cumulative genomic positions, plot log2 ratios as gray dots, and overlay colored segment lines.

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_cnv_profile(cnr_file, cns_file, output=None):
    '''Plot genome-wide CNV profile with segments.'''
    cnr = pd.read_csv(cnr_file, sep='\t')
    cns = pd.read_csv(cns_file, sep='\t')

    fig, ax = plt.subplots(figsize=(16, 4))

    # Chromosome positions
    chroms = [f'chr{i}' for i in range(1, 23)] + ['chrX', 'chrY']
    chrom_order = {c: i for i, c in enumerate(chroms)}
    cnr['chrom_num'] = cnr['chromosome'].map(chrom_order)
    cnr = cnr.dropna(subset=['chrom_num'])

    # Calculate cumulative position
    chrom_sizes = cnr.groupby('chromosome')['end'].max()
    cumsum = 0
    chrom_starts = {}
    for chrom in chroms:
        if chrom in chrom_sizes.index:
            chrom_starts[chrom] = cumsum
            cumsum += chrom_sizes[chrom]

    cnr['cumpos'] = cnr.apply(lambda x: chrom_starts.get(x['chromosome'], 0) + x['start'], axis=1)

    # Plot bins
    ax.scatter(cnr['cumpos'], cnr['log2'], s=1, c='gray', alpha=0.5)

    # Plot segments
    for _, seg in cns.iterrows():
        if seg['chromosome'] in chrom_starts:
            start = chrom_starts[seg['chromosome']] + seg['start']
            end = chrom_starts[seg['chromosome']] + seg['end']
            color = 'red' if seg['log2'] > 0.2 else ('blue' if seg['log2'] < -0.2 else 'green')
            ax.hlines(seg['log2'], start, end, colors=color, linewidth=2)

    # Chromosome boundaries
    for i, chrom in enumerate(chroms):
        if chrom in chrom_starts:
            ax.axvline(chrom_starts[chrom], color='lightgray', linewidth=0.5)
            if i % 2 == 0:
                ax.text(chrom_starts[chrom], ax.get_ylim()[1], chrom.replace('chr', ''),
                    fontsize=8, ha='left')

    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_ylabel('Log2 Copy Ratio')
    ax.set_xlabel('Genomic Position')
    ax.set_ylim(-2, 2)
    plt.tight_layout()

    if output:
        plt.savefig(output, dpi=150)
    return fig, ax
```

## Python: Single Chromosome Plot

**Goal:** Visualize the CNV profile of a single chromosome at higher resolution.

**Approach:** Filter bins and segments to one chromosome, plot with gain/loss/neutral color coding.

```python
def plot_chromosome(cnr, cns, chrom, ax=None):
    '''Plot CNV profile for single chromosome.'''
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 3))

    cnr_chr = cnr[cnr['chromosome'] == chrom].copy()
    cns_chr = cns[cns['chromosome'] == chrom].copy()

    # Plot bins
    ax.scatter(cnr_chr['start'] / 1e6, cnr_chr['log2'], s=5, c='gray', alpha=0.5)

    # Plot segments
    for _, seg in cns_chr.iterrows():
        color = 'red' if seg['log2'] > 0.3 else ('blue' if seg['log2'] < -0.3 else 'darkgreen')
        ax.hlines(seg['log2'], seg['start']/1e6, seg['end']/1e6, colors=color, linewidth=3)

    ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
    ax.axhline(0.5, color='red', linewidth=0.5, linestyle=':')
    ax.axhline(-0.5, color='blue', linewidth=0.5, linestyle=':')
    ax.set_xlabel(f'{chrom} Position (Mb)')
    ax.set_ylabel('Log2 Ratio')
    ax.set_title(chrom)
    return ax
```

## Python: Cohort Heatmap

**Goal:** Compare CNV patterns across multiple samples in a single heatmap.

**Approach:** Load segment files for all samples, build a matrix of log2 ratios, and render with seaborn diverging colormap.

```python
import seaborn as sns

def plot_cnv_heatmap(cns_files, region=None, output=None):
    '''Create heatmap of CNVs across samples.'''
    # Load all samples
    data = {}
    for f in cns_files:
        sample = f.replace('.cns', '').split('/')[-1]
        cns = pd.read_csv(f, sep='\t')
        if region:
            chrom, coords = region.split(':')
            start, end = map(int, coords.split('-'))
            cns = cns[(cns['chromosome'] == chrom) &
                     (cns['start'] >= start) & (cns['end'] <= end)]
        data[sample] = cns.set_index(['chromosome', 'start', 'end'])['log2']

    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(12, max(4, len(cns_files) * 0.3)))
    sns.heatmap(df.T, cmap='RdBu_r', center=0, vmin=-2, vmax=2,
        xticklabels=False, ax=ax)
    ax.set_xlabel('Genomic Position')
    ax.set_ylabel('Sample')

    if output:
        plt.savefig(output, dpi=150, bbox_inches='tight')
    return fig, ax
```

## R: ggplot2 Visualization

**Goal:** Create a faceted genome-wide CNV profile using ggplot2.

**Approach:** Plot bins as points with segment overlays, faceted by chromosome with free x-scales.

```r
library(ggplot2)
library(dplyr)

plot_cnv_profile <- function(cnr_file, cns_file) {
    cnr <- read.delim(cnr_file)
    cns <- read.delim(cns_file)

    # Order chromosomes
    chr_order <- c(paste0('chr', 1:22), 'chrX', 'chrY')
    cnr$chromosome <- factor(cnr$chromosome, levels=chr_order)
    cns$chromosome <- factor(cns$chromosome, levels=chr_order)

    p <- ggplot() +
        geom_point(data=cnr, aes(x=start, y=log2), size=0.1, alpha=0.3) +
        geom_segment(data=cns, aes(x=start, xend=end, y=log2, yend=log2,
            color=ifelse(log2 > 0.3, 'Gain', ifelse(log2 < -0.3, 'Loss', 'Neutral'))),
            size=1) +
        facet_grid(~chromosome, scales='free_x', space='free_x') +
        scale_color_manual(values=c('Gain'='red', 'Loss'='blue', 'Neutral'='green')) +
        geom_hline(yintercept=0, linetype='dashed') +
        ylim(-2, 2) +
        theme_minimal() +
        theme(axis.text.x=element_blank(),
              panel.spacing=unit(0, 'lines'),
              strip.text=element_text(size=6)) +
        labs(x='', y='Log2 Copy Ratio', color='')

    return(p)
}
```

## Circos-style Plot

**Goal:** Display CNV data as a circular genome plot.

**Approach:** Map segments to polar coordinates, render gain/loss bars around the genome circle using matplotlib polar projection.

```python
def plot_circos_cnv(cns_file, output=None):
    '''Create circular CNV plot.'''
    import matplotlib.patches as mpatches

    cns = pd.read_csv(cns_file, sep='\t')

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})

    chroms = [f'chr{i}' for i in range(1, 23)] + ['chrX', 'chrY']
    chrom_sizes = {'chr1': 249e6, 'chr2': 243e6, 'chr3': 198e6}  # Add all sizes

    total_size = sum(chrom_sizes.get(c, 50e6) for c in chroms)
    cumsum = 0

    for chrom in chroms:
        size = chrom_sizes.get(chrom, 50e6)
        cns_chr = cns[cns['chromosome'] == chrom]

        for _, seg in cns_chr.iterrows():
            theta_start = 2 * np.pi * (cumsum + seg['start']) / total_size
            theta_end = 2 * np.pi * (cumsum + seg['end']) / total_size
            r = 0.5 + seg['log2'] * 0.3

            color = 'red' if seg['log2'] > 0.3 else ('blue' if seg['log2'] < -0.3 else 'gray')
            ax.bar((theta_start + theta_end) / 2, r - 0.3, width=theta_end - theta_start,
                bottom=0.3, color=color, alpha=0.7)

        cumsum += size

    ax.set_ylim(0, 1)
    ax.axis('off')

    if output:
        plt.savefig(output, dpi=150, bbox_inches='tight')
    return fig, ax
```

## GATK Plot Commands

**Goal:** Generate GATK-native CNV plots showing denoised ratios and modeled segments.

**Approach:** Run PlotDenoisedCopyRatios and PlotModeledSegments on GATK CNV output files.

```bash
# Denoised copy ratios
gatk PlotDenoisedCopyRatios \
    --standardized-copy-ratios sample.standardized.tsv \
    --denoised-copy-ratios sample.denoised.tsv \
    --sequence-dictionary reference.dict \
    --output-prefix sample \
    -O plots/

# Modeled segments with allelic info
gatk PlotModeledSegments \
    --denoised-copy-ratios sample.denoised.tsv \
    --allelic-counts sample.hets.tsv \
    --segments sample.modelFinal.seg \
    --sequence-dictionary reference.dict \
    --output-prefix sample \
    -O plots/
```

## Related Skills

- copy-number/cnvkit-analysis - Generate CNV calls
- copy-number/gatk-cnv - GATK CNV workflow
- copy-number/cnv-annotation - Add gene annotations
