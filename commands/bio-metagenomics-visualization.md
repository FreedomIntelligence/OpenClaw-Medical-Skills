# bio-metagenomics-visualization

> Visualize metagenomic profiles using R (phyloseq, microbiome) and Python (matplotlib, seaborn). Create stacked bar plots, heatmaps, PCA plots, and diversity analyses. Use when creating publication-quality figures from MetaPhlAn, Bracken, or other taxonomic profiling output.

## Version Compatibility

Reference examples tested with: MetaPhlAn 4.1+, ggplot2 3.5+, matplotlib 3.8+, pandas 2.2+, phyloseq 1.46+, scanpy 1.10+, scikit-learn 1.4+, scipy 1.12+, seaborn 0.13+, vegan 2.6+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metagenome Visualization

**"Visualize the taxonomic composition of my metagenomes"** → Create publication-quality figures (stacked bars, heatmaps, ordination plots) from taxonomic profiling output to compare community composition across samples.
- R: `phyloseq::plot_bar()`, `microbiome` package
- Python: `matplotlib`/`seaborn` with pandas for custom compositions

## Python - Stacked Bar Plot

```python
import pandas as pd
import matplotlib.pyplot as plt

abundance = pd.read_csv('merged_abundance.txt', sep='\t', index_col=0)
abundance = abundance[abundance.index.str.contains('s__')]
abundance.index = abundance.index.str.split('|').str[-1].str.replace('s__', '')

top_n = 10
top_species = abundance.sum(axis=1).nlargest(top_n).index
abundance_top = abundance.loc[top_species]
abundance_top.loc['Other'] = abundance.drop(top_species).sum()

abundance_top.T.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='tab20')
plt.xlabel('Sample')
plt.ylabel('Relative Abundance (%)')
plt.title('Species Composition')
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig('stacked_bar.png', dpi=300)
```

## Python - Heatmap

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

abundance = pd.read_csv('merged_abundance.txt', sep='\t', index_col=0)
abundance = abundance[abundance.index.str.contains('s__')]
abundance.index = abundance.index.str.split('|').str[-1].str.replace('s__', '')

top_species = abundance.sum(axis=1).nlargest(20).index
abundance_top = abundance.loc[top_species]

plt.figure(figsize=(12, 10))
sns.heatmap(abundance_top, cmap='YlOrRd', annot=False, cbar_kws={'label': 'Abundance (%)'})
plt.xlabel('Sample')
plt.ylabel('Species')
plt.title('Species Abundance Heatmap')
plt.tight_layout()
plt.savefig('heatmap.png', dpi=300)
```

## Python - PCA

```python
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

abundance = pd.read_csv('merged_abundance.txt', sep='\t', index_col=0).T

scaler = StandardScaler()
abundance_scaled = scaler.fit_transform(abundance)

pca = PCA(n_components=2)
pca_result = pca.fit_transform(abundance_scaled)

plt.figure(figsize=(8, 6))
plt.scatter(pca_result[:, 0], pca_result[:, 1])
for i, sample in enumerate(abundance.index):
    plt.annotate(sample, (pca_result[i, 0], pca_result[i, 1]))
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
plt.title('PCA of Sample Composition')
plt.savefig('pca.png', dpi=300)
```

## R - phyloseq Setup

**Goal:** Convert a MetaPhlAn merged abundance table into a phyloseq object for ecological analysis and visualization in R.

**Approach:** Filter to species-level rows, clean taxonomy names, build an OTU table and sample metadata data frame, and assemble into a phyloseq object.

```r
library(phyloseq)
library(ggplot2)
library(vegan)

# From MetaPhlAn merged table
abundance <- read.table('merged_abundance.txt', sep = '\t', header = TRUE, row.names = 1)

# Filter to species level
species <- abundance[grepl('s__', rownames(abundance)), ]
rownames(species) <- sapply(strsplit(rownames(species), '\\|'), tail, 1)
rownames(species) <- gsub('s__', '', rownames(species))

# Create phyloseq object
otu <- otu_table(as.matrix(species), taxa_are_rows = TRUE)

# Sample metadata (create or load)
sample_data <- data.frame(
    Sample = colnames(species),
    Group = c('Control', 'Control', 'Treatment', 'Treatment'),
    row.names = colnames(species)
)
samp <- sample_data(sample_data)

ps <- phyloseq(otu, samp)
```

## R - Stacked Bar Plot

```r
library(phyloseq)
library(ggplot2)

# Top taxa
top_taxa <- names(sort(taxa_sums(ps), decreasing = TRUE))[1:10]
ps_top <- prune_taxa(top_taxa, ps)

# Stacked bar
plot_bar(ps_top, fill = 'Species') +
    geom_bar(stat = 'identity', position = 'stack') +
    theme_minimal() +
    labs(x = 'Sample', y = 'Relative Abundance (%)') +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
```

## R - Ordination (PCoA)

```r
library(phyloseq)
library(ggplot2)

# Bray-Curtis distance
ord <- ordinate(ps, method = 'PCoA', distance = 'bray')

# Plot ordination
plot_ordination(ps, ord, color = 'Group') +
    geom_point(size = 4) +
    stat_ellipse() +
    theme_minimal() +
    labs(title = 'PCoA of Sample Composition')
```

## R - Alpha Diversity

```r
library(phyloseq)
library(ggplot2)

# Calculate diversity metrics
alpha_div <- estimate_richness(ps, measures = c('Shannon', 'Simpson', 'Observed'))

# Add metadata
alpha_div$Group <- sample_data(ps)$Group

# Plot
ggplot(alpha_div, aes(x = Group, y = Shannon, fill = Group)) +
    geom_boxplot() +
    geom_jitter(width = 0.1) +
    theme_minimal() +
    labs(title = 'Alpha Diversity by Group', y = 'Shannon Index')
```

## R - Beta Diversity (PERMANOVA)

```r
library(vegan)

# Get abundance matrix
abundance_matrix <- as(otu_table(ps), 'matrix')
if (taxa_are_rows(ps)) abundance_matrix <- t(abundance_matrix)

# Calculate Bray-Curtis distance
dist_bc <- vegdist(abundance_matrix, method = 'bray')

# PERMANOVA
groups <- sample_data(ps)$Group
permanova <- adonis2(dist_bc ~ groups, permutations = 999)
permanova
```

## Krona Chart

```bash
# From Kraken2 report
ktImportTaxonomy -q 1 -t 5 kraken_report.txt -o krona_chart.html

# From MetaPhlAn
metaphlan2krona.py -p profile.txt -k krona_profile.txt
ktImportText krona_profile.txt -o krona_metaphlan.html
```

## Key Packages

### Python

| Package | Purpose |
|---------|---------|
| matplotlib | General plotting |
| seaborn | Statistical visualizations |
| scikit-learn | PCA, clustering |
| scipy | Statistical tests |

### R

| Package | Purpose |
|---------|---------|
| phyloseq | Microbiome data handling |
| vegan | Community ecology |
| ggplot2 | Visualization |
| microbiome | Additional analyses |

## Related Skills

- kraken-classification - Generate input data
- metaphlan-profiling - Generate input data
- abundance-estimation - Process Kraken output
