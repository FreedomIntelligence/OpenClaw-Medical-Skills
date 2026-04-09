# bio-tcr-bcr-analysis-immcantation-analysis

> Analyze BCR repertoires for somatic hypermutation, clonal lineages, and B cell phylogenetics using the Immcantation framework. Use when studying B cell affinity maturation, germinal center dynamics, or antibody evolution.

## Version Compatibility

Reference examples tested with: MiXCR 4.6+, ggplot2 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Immcantation Analysis

**"Analyze B cell repertoire evolution and clonal lineages"** → Study somatic hypermutation, build B cell phylogenies, and track affinity maturation using the Immcantation framework for BCR repertoire analysis.
- R: `alakazam::plotMutability()`, `dowser::buildPhylipLineage()`, `scoper::spectralClones()`

Requires Immcantation suite: alakazam 1.3+, shazam 1.2+, scoper 1.3+, dowser 2.0+, tigger 1.1+.

## Load and Format Data

**Goal:** Import AIRR-formatted repertoire data into the Immcantation framework for downstream analysis.

**Approach:** Read Change-O/AIRR tab-delimited files into R data frames with required V(D)J annotation columns.

```r
library(alakazam)
library(shazam)
library(dplyr)

# Load AIRR-formatted data (from MiXCR, IMGT/HighV-QUEST, etc.)
db <- readChangeoDb('clones_airr.tsv')

# Required columns:
# sequence_id, sequence, v_call, d_call, j_call, junction, junction_aa
```

## Clonal Clustering

**Goal:** Group B cell sequences into clonal lineages based on junction sequence similarity.

**Approach:** Apply hierarchical clustering on nucleotide distance of junction regions with a threshold-based cutoff.

```r
library(scoper)

# Assign clones based on junction similarity
# Threshold typically 0.15-0.2 (15-20% nucleotide distance)
db <- hierarchicalClones(
    db,
    threshold = 0.15,
    method = 'nt',
    linkage = 'single'
)

# Count clones
clone_sizes <- countClones(db, groups = 'sample_id')
```

## Somatic Hypermutation Analysis

**Goal:** Quantify somatic hypermutation rates across replacement and silent categories for each clone.

**Approach:** Compare observed sequences to germline alignments using the S5F targeting model to count and classify mutations.

```r
# Calculate mutation frequencies
db <- observedMutations(
    db,
    sequenceColumn = 'sequence_alignment',
    germlineColumn = 'germline_alignment_d_mask',
    regionDefinition = IMGT_V,
    mutationDefinition = MUTATION_SCHEMES$S5F
)

# Mutation frequency columns added:
# mu_count_seq_r, mu_count_seq_s (replacement/silent mutations)
# mu_freq_seq_r, mu_freq_seq_s (frequencies)

# Summarize by clone
mutation_summary <- db %>%
    group_by(clone_id) %>%
    summarize(
        mean_mu = mean(mu_freq_seq_r, na.rm = TRUE),
        n_sequences = n()
    )
```

## Selection Analysis

**Goal:** Test whether observed replacement/silent mutation ratios deviate from neutral expectation, indicating positive or negative selection.

**Approach:** Estimate BASELINe selection strength (sigma) by comparing observed R/S ratios to a null model of somatic hypermutation targeting.

```r
library(shazam)

# Test for selection pressure
# Compares observed R/S ratio to expected under neutrality
baseline <- estimateBaseline(
    db,
    sequenceColumn = 'sequence_alignment',
    germlineColumn = 'germline_alignment_d_mask',
    testStatistic = 'focused',
    regionDefinition = IMGT_V,
    nproc = 4
)

# Summarize selection
selection <- summarizeBaseline(baseline, returnType = 'df')

# Positive sigma = positive selection (beneficial mutations retained)
# Negative sigma = negative selection (deleterious mutations removed)
```

## Build Clonal Lineage Trees

**Goal:** Reconstruct phylogenetic lineage trees for each B cell clone to visualize affinity maturation pathways.

**Approach:** Build maximum parsimony trees from clonal sequence alignments using PHYLIP's dnapars algorithm via dowser.

```r
library(dowser)

# Build lineage trees for each clone
# Requires multiple sequences per clone
clones_multi <- db %>%
    group_by(clone_id) %>%
    filter(n() >= 3) %>%
    ungroup()

# Build trees using maximum parsimony
trees <- buildPhylipLineage(
    clones_multi,
    phylip_exec = 'dnapars',
    rm_temp = TRUE
)

# Plot a tree
plotTrees(trees[[1]])
```

## Germline Inference

**Goal:** Discover novel V gene alleles and correct V gene assignments using individual-level genotyping.

**Approach:** Infer novel alleles from mutation patterns with TIgGER, build a personalized genotype, and reassign allele calls.

```r
library(tigger)

# Infer novel V gene alleles
novel <- findNovelAlleles(
    db,
    germline_db = 'IMGT_Human_IGHV.fasta',
    nproc = 4
)

# Genotype the individual
genotype <- inferGenotype(db, germline_db = 'IMGT_Human_IGHV.fasta')

# Correct V gene calls
db <- reassignAlleles(db, genotype)
```

## Visualization

**Goal:** Generate summary plots of mutation frequencies and V gene usage across samples.

**Approach:** Plot mutation frequency distributions with ggplot2 histograms and V gene usage bar charts via alakazam helpers.

```r
# Plot mutation frequency distribution
library(ggplot2)

ggplot(db, aes(x = mu_freq_seq_r)) +
    geom_histogram(bins = 50) +
    facet_wrap(~ sample_id) +
    labs(x = 'Replacement Mutation Frequency', y = 'Count')

# Plot V gene usage
v_usage <- countGenes(db, gene = 'v_call', groups = 'sample_id')
plotGeneUsage(v_usage, gene = 'v_call')
```

## Related Skills

- mixcr-analysis - Generate input clonotype data
- vdjtools-analysis - Diversity metrics (TCR-focused)
- phylogenetics/tree-io - General tree concepts
