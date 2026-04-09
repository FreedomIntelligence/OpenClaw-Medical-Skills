# bio-microbiome-diversity-analysis

> Alpha and beta diversity analysis for microbiome data. Calculate within-sample richness, evenness, and between-sample dissimilarity with phyloseq and vegan. Use when comparing community composition across samples or testing for group differences in microbiome structure.

## Version Compatibility

Reference examples tested with: R stats (base), ggplot2 3.5+, phyloseq 1.46+, scanpy 1.10+, vegan 2.6+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Diversity Analysis

**"Compare microbial diversity across my samples"** → Calculate alpha diversity (within-sample richness/evenness) and beta diversity (between-sample dissimilarity) to test for community composition differences across groups.
- R: `phyloseq::estimate_richness()` for alpha, `phyloseq::ordinate()` for beta
- R: `vegan::adonis2()` for PERMANOVA testing

## Create phyloseq Object

```r
library(phyloseq)
library(vegan)
library(ggplot2)

seqtab <- readRDS('seqtab_nochim.rds')
taxa <- readRDS('taxa.rds')
metadata <- read.csv('sample_metadata.csv', row.names = 1)

ps <- phyloseq(otu_table(seqtab, taxa_are_rows = FALSE),
               tax_table(taxa),
               sample_data(metadata))
taxa_names(ps) <- paste0('ASV', seq(ntaxa(ps)))
```

## Alpha Diversity

```r
# Calculate multiple metrics
alpha_div <- estimate_richness(ps, measures = c('Observed', 'Chao1', 'Shannon', 'Simpson'))
alpha_div$SampleID <- rownames(alpha_div)
alpha_div <- merge(alpha_div, sample_data(ps), by = 'row.names')

# Statistical test
kruskal.test(Shannon ~ Group, data = alpha_div)

# Pairwise comparisons
pairwise.wilcox.test(alpha_div$Shannon, alpha_div$Group, p.adjust.method = 'BH')
```

## Alpha Diversity Plots

```r
plot_richness(ps, x = 'Group', measures = c('Observed', 'Shannon')) +
    geom_boxplot() +
    theme_minimal()

# Custom plot
ggplot(alpha_div, aes(x = Group, y = Shannon, fill = Group)) +
    geom_boxplot() +
    geom_jitter(width = 0.2, alpha = 0.5) +
    theme_minimal() +
    labs(y = 'Shannon Diversity Index')
```

## Faith's Phylogenetic Diversity

**Goal:** Calculate phylogenetic alpha diversity (Faith's PD) from ASV data by building a de novo phylogeny and summing branch lengths.

**Approach:** Align ASV sequences with DECIPHER, construct a neighbor-joining tree with phangorn, root at midpoint, and compute PD using picante.

```r
library(picante)

# Requires phylogenetic tree in phyloseq object
# Build tree from ASV sequences
library(DECIPHER)
library(phangorn)

seqs <- refseq(ps)
alignment <- AlignSeqs(seqs, anchor = NA)
phang_align <- phyDat(as(alignment, 'matrix'), type = 'DNA')
dm <- dist.ml(phang_align)
tree <- NJ(dm)
tree <- midpoint(tree)
phy_tree(ps) <- tree

# Calculate Faith's PD
otu_mat <- as.matrix(t(otu_table(ps)))
faith_pd <- pd(otu_mat, phy_tree(ps), include.root = TRUE)
alpha_div$PD <- faith_pd$PD
```

## Rarefaction Curves

```r
# Check if sequencing depth is adequate
rarecurve_data <- vegan::rarecurve(t(otu_table(ps)), step = 100, sample = min(sample_sums(ps)))

# ggplot version with ggrare (install from GitHub)
# devtools::install_github('gauravsk/ranacapa')
library(ranacapa)
p_rare <- ggrare(ps, step = 100, color = 'Group', se = FALSE)
p_rare + theme_minimal() + labs(title = 'Rarefaction Curves')
```

## Rarefaction

```r
# Check sequencing depth
sample_sums(ps)

# Rarefy to minimum depth
ps_rarefied <- rarefy_even_depth(ps, sample.size = min(sample_sums(ps)),
                                  rngseed = 42, replace = FALSE)
```

## Beta Diversity

```r
# Calculate distance matrices
bray <- phyloseq::distance(ps, method = 'bray')       # Bray-Curtis
jaccard <- phyloseq::distance(ps, method = 'jaccard') # Jaccard
unifrac <- UniFrac(ps, weighted = TRUE)               # Weighted UniFrac (requires tree)

# Ordination
ord_bray <- ordinate(ps, method = 'PCoA', distance = bray)

# Plot
plot_ordination(ps, ord_bray, color = 'Group') +
    stat_ellipse(level = 0.95) +
    theme_minimal()
```

## PERMANOVA

```r
# Test for group differences
metadata <- data.frame(sample_data(ps))
permanova_result <- adonis2(bray ~ Group, data = metadata, permutations = 999)
permanova_result

# With covariates
adonis2(bray ~ Group + Age + Sex, data = metadata, permutations = 999)
```

## Beta Dispersion

```r
# Test homogeneity of dispersions (assumption of PERMANOVA)
beta_disp <- betadisper(bray, metadata$Group)
permutest(beta_disp)
plot(beta_disp)
```

## NMDS Ordination

```r
ord_nmds <- ordinate(ps, method = 'NMDS', distance = bray)

# Check stress
ord_nmds$stress  # Should be < 0.2

plot_ordination(ps, ord_nmds, color = 'Group') +
    theme_minimal()
```

## Distance Metrics Comparison

| Metric | Type | Considers Abundance | Phylogeny |
|--------|------|---------------------|-----------|
| Bray-Curtis | Quantitative | Yes | No |
| Jaccard | Binary | No | No |
| UniFrac (unweighted) | Binary | No | Yes |
| UniFrac (weighted) | Quantitative | Yes | Yes |

## Related Skills

- amplicon-processing - Generate ASV table
- differential-abundance - Identify taxa driving differences
- data-visualization/ggplot2-fundamentals - Custom diversity plots
- ecological-genomics/biodiversity-metrics - Hill number coverage-based rarefaction for ecological data
- ecological-genomics/community-ecology - Constrained ordination and indicator species
