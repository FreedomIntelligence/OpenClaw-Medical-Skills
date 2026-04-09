# bio-multi-omics-similarity-network

> Similarity Network Fusion (SNF) for patient stratification using multi-omics data. Integrates multiple data types into a unified patient similarity network. Use when performing patient stratification or integrating multi-omics data into unified similarity networks.

## Version Compatibility

Reference examples tested with: scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Similarity Network Fusion

**"Stratify patients using multi-omics data"** → Fuse omics-specific patient similarity networks into a unified network for subtype discovery and clustering.
- R: `SNFtool::SNF()` to fuse networks, `spectralClustering()` for subtyping

## Basic SNF Workflow

**Goal:** Fuse multiple omics-specific patient similarity networks into a single unified network.

**Approach:** Compute per-omics distance and affinity matrices, then iteratively fuse with SNF.

```r
library(SNFtool)

# Load omics data (samples x features)
data1 <- as.matrix(read.csv('rnaseq.csv', row.names = 1))
data2 <- as.matrix(read.csv('methylation.csv', row.names = 1))
data3 <- as.matrix(read.csv('mirna.csv', row.names = 1))

# Ensure matching samples
common <- Reduce(intersect, list(rownames(data1), rownames(data2), rownames(data3)))
data1 <- data1[common, ]
data2 <- data2[common, ]
data3 <- data3[common, ]

# Compute distance matrices
dist1 <- dist2(as.matrix(data1), as.matrix(data1))
dist2 <- dist2(as.matrix(data2), as.matrix(data2))
dist3 <- dist2(as.matrix(data3), as.matrix(data3))

# Construct affinity matrices
# K = number of neighbors, alpha = hyperparameter
K <- 20
alpha <- 0.5

aff1 <- affinityMatrix(dist1, K, alpha)
aff2 <- affinityMatrix(dist2, K, alpha)
aff3 <- affinityMatrix(dist3, K, alpha)

# Fuse networks
# T = number of iterations
fused <- SNF(list(aff1, aff2, aff3), K = K, t = 20)
```

## Cluster Patients

**Goal:** Identify patient subtypes from the fused similarity network using spectral clustering.

**Approach:** Estimate optimal cluster count from the fused graph, then apply spectral clustering.

```r
# Determine optimal number of clusters
estimateNumberOfClustersGivenGraph(fused, NUMC = 2:10)

# Spectral clustering
num_clusters <- 3
clusters <- spectralClustering(fused, num_clusters)

# Add to sample metadata
sample_info <- data.frame(
    Sample = rownames(data1),
    Cluster = factor(clusters)
)
```

## Visualize Network

**Goal:** Display the fused patient network as a graph and heatmap with cluster annotations.

**Approach:** Convert the fused matrix to an igraph object, filter weak edges, and render with cluster coloring.

```r
library(igraph)

# Convert to igraph
g <- graph_from_adjacency_matrix(fused, mode = 'undirected', weighted = TRUE, diag = FALSE)

# Remove weak edges
threshold <- quantile(E(g)$weight, 0.9)
g_filtered <- delete_edges(g, E(g)[weight < threshold])

# Plot
V(g_filtered)$color <- clusters
plot(g_filtered, vertex.size = 5, vertex.label = NA,
     edge.width = E(g_filtered)$weight * 2,
     main = 'SNF Patient Network')

# Heatmap
library(pheatmap)
pheatmap(fused, cluster_rows = TRUE, cluster_cols = TRUE,
         annotation_row = sample_info['Cluster'],
         show_rownames = FALSE, show_colnames = FALSE)
```

## Normalized Mutual Information

**Goal:** Evaluate clustering quality by comparing SNF clusters against known subtypes and single-omics baselines.

**Approach:** Compute NMI between predicted clusters and true labels for fused vs individual affinity networks.

```r
# Compare with known labels
true_labels <- read.csv('phenotype.csv')$Subtype

# NMI score
nmi <- calNMI(clusters, true_labels)
cat('NMI:', nmi, '\n')

# Compare individual vs fused
nmi_rna <- calNMI(spectralClustering(aff1, num_clusters), true_labels)
nmi_meth <- calNMI(spectralClustering(aff2, num_clusters), true_labels)
nmi_mirna <- calNMI(spectralClustering(aff3, num_clusters), true_labels)

cat('NMI RNA only:', nmi_rna, '\n')
cat('NMI Methylation only:', nmi_meth, '\n')
cat('NMI miRNA only:', nmi_mirna, '\n')
cat('NMI Fused:', nmi, '\n')
```

## Feature Ranking with SNF

**Goal:** Rank features by their contribution to the SNF-derived patient clusters.

**Approach:** Perform ANOVA per feature across cluster assignments, ranking by F-statistic p-value.

```r
# Rank features by their contribution to clustering
# Using network-based method

# For each omics layer
rank_features <- function(data, clusters) {
    # Calculate feature importance based on cluster separation
    f_values <- apply(data, 2, function(x) {
        summary(aov(x ~ factor(clusters)))[[1]][1, 4]
    })
    f_values[is.na(f_values)] <- 1
    names(sort(f_values))
}

top_rna <- rank_features(data1, clusters)
top_meth <- rank_features(data2, clusters)
```

## Survival Analysis with Clusters

**Goal:** Assess clinical relevance of SNF clusters by comparing survival outcomes between subtypes.

**Approach:** Fit Kaplan-Meier curves per cluster and test significance with the log-rank test.

```r
library(survival)
library(survminer)

# Load survival data
surv_data <- read.csv('survival.csv')
surv_data$Cluster <- clusters[match(surv_data$Sample, rownames(data1))]

# Kaplan-Meier
fit <- survfit(Surv(Time, Event) ~ Cluster, data = surv_data)

ggsurvplot(fit, data = surv_data, pval = TRUE,
           risk.table = TRUE, palette = 'jco',
           title = 'SNF Cluster Survival')

# Log-rank test
survdiff(Surv(Time, Event) ~ Cluster, data = surv_data)
```

## Parameter Tuning

**Goal:** Optimize SNF hyperparameters (K neighbors, alpha) for best clustering performance.

**Approach:** Grid search over K and alpha values, evaluating each combination by NMI against known labels.

```r
# Grid search over K and alpha
K_range <- c(10, 20, 30)
alpha_range <- c(0.3, 0.5, 0.8)

results <- expand.grid(K = K_range, alpha = alpha_range, NMI = NA)

for (i in 1:nrow(results)) {
    aff1 <- affinityMatrix(dist1, results$K[i], results$alpha[i])
    aff2 <- affinityMatrix(dist2, results$K[i], results$alpha[i])
    aff3 <- affinityMatrix(dist3, results$K[i], results$alpha[i])

    fused <- SNF(list(aff1, aff2, aff3), K = results$K[i], t = 20)
    clusters <- spectralClustering(fused, num_clusters)
    results$NMI[i] <- calNMI(clusters, true_labels)
}

best <- results[which.max(results$NMI), ]
cat('Best parameters: K =', best$K, ', alpha =', best$alpha, '\n')
```

## Integration with Clinical Features

**Goal:** Incorporate clinical variables as an additional data view in the SNF fusion.

**Approach:** Encode clinical features numerically, compute a clinical affinity matrix, and include it in the SNF fusion step.

```r
# Add clinical features as another view
clinical <- read.csv('clinical.csv', row.names = 1)
clinical_numeric <- model.matrix(~ . - 1, data = clinical)

dist_clinical <- dist2(clinical_numeric, clinical_numeric)
aff_clinical <- affinityMatrix(dist_clinical, K, alpha)

# Fuse all including clinical
fused_with_clinical <- SNF(list(aff1, aff2, aff3, aff_clinical), K = K, t = 20)
```

## Related Skills

- mofa-integration - Factor-based integration
- mixomics-analysis - Supervised integration
- single-cell/clustering - Single-cell clustering methods
