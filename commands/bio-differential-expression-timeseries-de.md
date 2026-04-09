# bio-differential-expression-timeseries-de

> Analyze time-series RNA-seq data using limma voom with splines, maSigPro, and ImpulseDE2. Identify genes with dynamic expression patterns. Use when analyzing time-series or longitudinal expression data.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, edgeR 4.0+, ggplot2 3.5+, limma 3.58+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Time-Series Differential Expression

Identify genes with significant temporal expression patterns in time-course experiments.

## Approaches

| Method | Best For |
|--------|----------|
| limma with splines | Smooth temporal patterns |
| maSigPro | Multiple time points, regression |
| ImpulseDE2 | Impulse-like patterns |
| DESeq2 LRT | Discrete time comparisons |

## limma with Splines

**Goal:** Identify genes with smooth temporal expression patterns using flexible spline models.

**Approach:** Fit voom-transformed counts with natural spline basis functions in limma, testing spline coefficients for significance.

**"Find genes that change over time in my RNA-seq experiment"** → Model temporal expression using spline regression and test whether spline terms are significantly non-zero.

### Setup

```r
library(limma)
library(edgeR)
library(splines)

# Load count data
counts <- read.table('counts.txt', header=TRUE, row.names=1)
metadata <- read.table('metadata.txt', header=TRUE)

# metadata should have: sample, time, condition, replicate
```

### Basic Time-Series Model

```r
# Create DGEList
dge <- DGEList(counts=counts)
dge <- calcNormFactors(dge)

# Filter low counts
keep <- filterByExpr(dge, group=metadata$condition)
dge <- dge[keep, , keep.lib.sizes=FALSE]

# Design with natural splines
time <- metadata$time
design <- model.matrix(~ ns(time, df=3))

# voom transformation
v <- voom(dge, design, plot=TRUE)

# Fit model
fit <- lmFit(v, design)
fit <- eBayes(fit)

# Test for any temporal effect (all spline terms)
results <- topTable(fit, coef=2:4, number=Inf)
```

### Two Conditions Over Time

```r
# Design for condition-specific time effects
condition <- factor(metadata$condition)
time <- metadata$time

# Interaction model
design <- model.matrix(~ condition * ns(time, df=3))

v <- voom(dge, design, plot=TRUE)
fit <- lmFit(v, design)
fit <- eBayes(fit)

# Genes with different temporal patterns between conditions
# Test interaction terms
results_interaction <- topTable(fit, coef=grep(':', colnames(design)), number=Inf)
```

### Contrasts for Specific Comparisons

```r
# Compare time points within condition
design <- model.matrix(~ 0 + condition:factor(time))
colnames(design) <- gsub(':', '_', colnames(design))

v <- voom(dge, design)
fit <- lmFit(v, design)

# Contrast: Treated_T2 vs Treated_T0
contrast <- makeContrasts(
    early_response = ConditionTreated_time2 - ConditionTreated_time0,
    late_response = ConditionTreated_time6 - ConditionTreated_time0,
    levels = design
)

fit2 <- contrasts.fit(fit, contrast)
fit2 <- eBayes(fit2)
results <- topTable(fit2, coef='early_response', number=Inf)
```

## maSigPro

**Goal:** Identify genes with significant temporal expression profiles using two-step polynomial regression.

**Approach:** Apply global regression to find time-variable genes, then stepwise regression to refine significant profiles and cluster them.

### Installation

```r
BiocManager::install('maSigPro')
```

### Two-Step Regression

```r
library(maSigPro)

# Create experimental design
# Time, Replicate, Group columns required
edesign <- data.frame(
    Time = metadata$time,
    Replicate = metadata$replicate,
    Control = as.numeric(metadata$condition == 'Control'),
    Treatment = as.numeric(metadata$condition == 'Treatment')
)
rownames(edesign) <- metadata$sample

# Normalize counts
dge <- DGEList(counts=counts)
dge <- calcNormFactors(dge)
norm_counts <- cpm(dge, log=TRUE)

# Create design matrix for polynomial regression
design <- make.design.matrix(edesign, degree=3)

# Step 1: Global regression (find time-variable genes)
fit <- p.vector(norm_counts, design, Q=0.05, MT.adjust='BH')

# Step 2: Stepwise regression (find significant profiles)
tstep <- T.fit(fit, step.method='backward', alfa=0.05)

# Get significant genes
sigs <- get.siggenes(tstep, rsq=0.6, vars='groups')

# Visualize clusters
see.genes(sigs$sig.genes, show.fit=TRUE, dis=design$dis,
          cluster.method='hclust', k=9)
```

### Cluster Visualization

```r
# Plot specific clusters
pdf('timeseries_clusters.pdf', width=12, height=10)
see.genes(sigs$sig.genes, show.fit=TRUE, dis=design$dis,
          cluster.method='hclust', k=9,
          newX11=FALSE)
dev.off()

# Get genes per cluster
cluster_genes <- sigs$sig.genes$sig.profiles
```

## ImpulseDE2

**Goal:** Detect genes with transient impulse-like expression patterns (rise then fall, or vice versa).

**Approach:** Fit sigmoid-based impulse models to each gene and test for significant temporal dynamics.

### Installation

```r
BiocManager::install('ImpulseDE2')
```

### Run ImpulseDE2

```r
library(ImpulseDE2)
library(DESeq2)

# Create annotation
dfAnnotation <- data.frame(
    Sample = colnames(counts),
    Time = metadata$time,
    Condition = metadata$condition,
    Batch = metadata$batch
)

# Run ImpulseDE2
impulse_results <- runImpulseDE2(
    matCountData = as.matrix(counts),
    dfAnnotation = dfAnnotation,
    boolCaseCtrl = TRUE,
    vecConfounders = c('Batch'),
    scaNProc = 4
)

# Get significant genes
sig_genes <- impulse_results$dfImpulseDE2Results[
    impulse_results$dfImpulseDE2Results$padj < 0.05, ]
```

## DESeq2 Likelihood Ratio Test

**Goal:** Test for any temporal effect across discrete time points without assuming a smooth curve.

**Approach:** Compare a full model with time terms against a reduced model using a likelihood ratio test.

```r
library(DESeq2)

# Design with time as factor
dds <- DESeqDataSetFromMatrix(
    countData = counts,
    colData = metadata,
    design = ~ condition + time + condition:time
)

# LRT: test if time has any effect
dds_lrt <- DESeq(dds, test='LRT', reduced = ~ condition)
results_lrt <- results(dds_lrt)

# Genes with significant temporal pattern
sig_time <- results_lrt[results_lrt$padj < 0.05 & !is.na(results_lrt$padj), ]
```

## Visualization

**Goal:** Display temporal expression trajectories for top significant genes across conditions.

**Approach:** Plot per-gene expression over time with loess smoothing, faceted or as a grid of individual gene plots.

### Expression Profiles

```r
library(ggplot2)

plot_gene_timeseries <- function(gene, counts, metadata) {
    gene_data <- data.frame(
        time = metadata$time,
        condition = metadata$condition,
        expression = as.numeric(counts[gene, ])
    )

    ggplot(gene_data, aes(time, expression, color = condition, group = condition)) +
        geom_point(size = 2) +
        geom_smooth(method = 'loess', se = TRUE, alpha = 0.2) +
        labs(title = gene, x = 'Time', y = 'log2(CPM)') +
        theme_bw()
}

# Plot top genes
top_genes <- head(rownames(results)[order(results$adj.P.Val)], 9)
plots <- lapply(top_genes, plot_gene_timeseries, counts = norm_counts, metadata = metadata)
library(patchwork)
wrap_plots(plots, ncol = 3)
```

### Heatmap with Time Order

```r
library(pheatmap)

# Get significant genes
sig_genes <- rownames(results)[results$adj.P.Val < 0.05]

# Order samples by time
sample_order <- order(metadata$time, metadata$condition)
mat <- norm_counts[sig_genes, sample_order]

# Scale rows
mat_scaled <- t(scale(t(mat)))

# Annotation
anno_col <- data.frame(
    Time = metadata$time[sample_order],
    Condition = metadata$condition[sample_order],
    row.names = colnames(mat)
)

pheatmap(mat_scaled,
         annotation_col = anno_col,
         cluster_cols = FALSE,
         show_rownames = FALSE,
         color = colorRampPalette(c('blue', 'white', 'red'))(100))
```

## Complete Workflow

**Goal:** Run an end-to-end time-series DE analysis combining limma splines and maSigPro.

**Approach:** Normalize and filter counts, fit both models in parallel, then union the significant gene sets.

```r
library(limma)
library(edgeR)
library(splines)
library(maSigPro)

# Load data
counts <- read.table('counts.txt', header=TRUE, row.names=1)
metadata <- read.table('metadata.txt', header=TRUE, row.names=1)

# Normalize
dge <- DGEList(counts=counts)
dge <- calcNormFactors(dge)
keep <- filterByExpr(dge, group=metadata$condition)
dge <- dge[keep, , keep.lib.sizes=FALSE]
norm_counts <- cpm(dge, log=TRUE)

# Method 1: limma with splines
design <- model.matrix(~ metadata$condition * ns(metadata$time, df=3))
v <- voom(dge, design, plot=TRUE)
fit <- lmFit(v, design)
fit <- eBayes(fit)

# Genes with condition-specific temporal patterns
interaction_terms <- grep(':', colnames(design))
results_limma <- topTable(fit, coef=interaction_terms, number=Inf)
sig_limma <- rownames(results_limma)[results_limma$adj.P.Val < 0.05]

# Method 2: maSigPro
edesign <- data.frame(
    Time = metadata$time,
    Replicate = 1:nrow(metadata),
    Control = as.numeric(metadata$condition == 'Control'),
    Treatment = as.numeric(metadata$condition == 'Treatment')
)
rownames(edesign) <- rownames(metadata)

design_masig <- make.design.matrix(edesign, degree=3)
fit_masig <- p.vector(norm_counts, design_masig, Q=0.05)
tstep <- T.fit(fit_masig, step.method='backward')
sigs <- get.siggenes(tstep, rsq=0.6, vars='groups')

# Combine results
all_sig <- union(sig_limma, rownames(sigs$sig.genes$sig.profiles))
cat('Significant genes:', length(all_sig), '\n')
```

## Related Skills

- differential-expression/deseq2-basics - Standard DE analysis
- differential-expression/de-visualization - Visualize results
- differential-expression/batch-correction - Handle batch effects
- pathway-analysis/go-enrichment - Functional analysis of clusters
- temporal-genomics/circadian-rhythms - Circadian rhythm detection for time-course data
- temporal-genomics/temporal-clustering - Cluster genes by temporal expression profile
- temporal-genomics/trajectory-modeling - GAM trajectory fitting for temporal expression data
- temporal-genomics/temporal-grn - Dynamic GRN inference from bulk time-series data
