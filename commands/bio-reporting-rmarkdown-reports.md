# bio-reporting-rmarkdown-reports

> Create reproducible bioinformatics analysis reports with R Markdown including code, results, and visualizations in HTML, PDF, or Word format. Use when generating analysis reports with RMarkdown.

**Available tools:** Read, Bash

# R Markdown Reports

## Basic Document Structure

```yaml
---
title: "RNA-seq Analysis Report"
author: "Your Name"
date: "`r Sys.Date()`"
output:
  html_document:
    toc: true
    toc_float: true
    code_folding: hide
    theme: cosmo
---
```

## Setup Chunk

````r
```{r setup, include=FALSE}
knitr::opts_chunk$set(
    echo = TRUE,
    message = FALSE,
    warning = FALSE,
    fig.width = 10,
    fig.height = 6,
    fig.align = 'center'
)
library(tidyverse)
library(DESeq2)
library(pheatmap)
```
````

## Code Chunk Options

````r
```{r analysis, echo=TRUE, results='hide'}
# echo: show code
# results: 'hide', 'asis', 'markup'
# include: FALSE hides chunk entirely
# eval: FALSE shows code but doesn't run
# cache: TRUE caches results
```
````

## Parameterized Reports

```yaml
---
title: "Sample Report"
params:
  sample_id: "sample1"
  count_file: "counts.csv"
  fdr_threshold: 0.05
---
```

````r
```{r}
counts <- read.csv(params$count_file)
sample <- params$sample_id
fdr <- params$fdr_threshold
```
````

```r
# Render with parameters
rmarkdown::render('report.Rmd', params = list(sample_id = 'sample2', fdr_threshold = 0.01))

# Batch render
samples <- c('sample1', 'sample2', 'sample3')
for (s in samples) {
    rmarkdown::render('report.Rmd', params = list(sample_id = s),
                       output_file = paste0(s, '_report.html'))
}
```

## Tables

````r
```{r}
# Basic kable table
knitr::kable(head(results), caption = 'Top DE genes')

# Interactive table with DT
library(DT)
datatable(results, filter = 'top', options = list(pageLength = 10))

# Formatted table with kableExtra
library(kableExtra)
results %>%
    head(10) %>%
    kable() %>%
    kable_styling(bootstrap_options = c('striped', 'hover')) %>%
    row_spec(which(results$padj < 0.01), bold = TRUE, color = 'red')
```
````

## Figures

````r
```{r volcano-plot, fig.cap="Volcano plot of differential expression"}
ggplot(results, aes(log2FoldChange, -log10(pvalue))) +
    geom_point(aes(color = padj < 0.05)) +
    theme_minimal()
```
````

## Inline Code

```markdown
We identified `r sum(res$padj < 0.05, na.rm=TRUE)` significantly
DE genes (FDR < 0.05) out of `r nrow(res)` tested.
```

## Child Documents

```yaml
---
title: "Main Report"
---
```

````r
```{r child='methods.Rmd'}
```

```{r child='results.Rmd'}
```
````

## PDF Output

```yaml
---
output:
  pdf_document:
    toc: true
    number_sections: true
    fig_caption: true
    latex_engine: xelatex
---
```

## HTML with Tabs

````r
## Results {.tabset}

### PCA Plot
```{r}
plotPCA(vsd, intgroup = 'condition')
```

### Heatmap
```{r}
pheatmap(assay(vsd)[top_genes, ])
```
````

## Caching Long Computations

````r
```{r deseq-analysis, cache=TRUE, cache.extra=tools::md5sum('counts.csv')}
# Cached unless counts.csv changes
dds <- DESeqDataSetFromMatrix(counts, metadata, ~ condition)
dds <- DESeq(dds)
```

```{r downstream, dependson='deseq-analysis'}
# Re-runs when deseq-analysis cache changes
res <- results(dds)
```
````

## Custom CSS

```yaml
---
output:
  html_document:
    css: custom.css
---
```

```css
/* custom.css */
body { font-family: 'Helvetica', sans-serif; }
h1 { color: #2c3e50; }
.figure { margin: 20px auto; }
```

## Complete Report Template

````markdown
---
title: "RNA-seq Analysis Report"
author: "Bioinformatics Core"
date: "`r Sys.Date()`"
output:
  html_document:
    toc: true
    toc_float: true
    code_folding: hide
params:
  count_file: "counts.csv"
  metadata_file: "metadata.csv"
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE, message = FALSE, warning = FALSE)
library(DESeq2)
library(tidyverse)
library(pheatmap)
library(DT)
```

## Data Overview

```{r load-data}
counts <- read.csv(params$count_file, row.names = 1)
metadata <- read.csv(params$metadata_file, row.names = 1)
```

Loaded `r nrow(counts)` genes across `r ncol(counts)` samples.

## Differential Expression

```{r de-analysis, cache=TRUE}
dds <- DESeqDataSetFromMatrix(counts, metadata, ~ condition)
dds <- DESeq(dds)
res <- results(dds) %>% as.data.frame() %>% arrange(padj)
```

## Results

```{r results-table}
datatable(res %>% filter(padj < 0.05), options = list(pageLength = 10))
```
````

## Related Skills

- reporting/quarto-reports - Modern alternative
- data-visualization/ggplot2-fundamentals - Figure creation
- differential-expression/de-visualization - Analysis plots
