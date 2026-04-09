# bio-epitranscriptomics-m6a-differential

> Identify differential m6A methylation between conditions from MeRIP-seq. Use when comparing epitranscriptomic changes between treatment groups or cell states.

**Available tools:** Read, Bash

# Differential m6A Analysis

## exomePeak2 Differential Analysis

```r
library(exomePeak2)

# Define sample design
# condition: factor for comparison
design <- data.frame(
    condition = factor(c('ctrl', 'ctrl', 'treat', 'treat'))
)

# Differential peak calling
result <- exomePeak2(
    bam_ip = c('ctrl_IP1.bam', 'ctrl_IP2.bam', 'treat_IP1.bam', 'treat_IP2.bam'),
    bam_input = c('ctrl_Input1.bam', 'ctrl_Input2.bam', 'treat_Input1.bam', 'treat_Input2.bam'),
    gff = 'genes.gtf',
    genome = 'hg38',
    experiment_design = design
)

# Get differential sites
diff_sites <- results(result, contrast = c('condition', 'treat', 'ctrl'))
```

## QNB for Differential Methylation

```r
library(QNB)

# Requires count matrices from peak regions
# IP and input counts per sample
qnb_result <- qnbtest(
    IP_count_matrix,
    Input_count_matrix,
    group = c(1, 1, 2, 2)  # 1=ctrl, 2=treat
)

# Filter significant
# padj < 0.05, |log2FC| > 1
sig <- qnb_result[qnb_result$padj < 0.05 & abs(qnb_result$log2FC) > 1, ]
```

## Visualization

```r
library(ggplot2)

# Volcano plot
ggplot(diff_sites, aes(x = log2FoldChange, y = -log10(padj))) +
    geom_point(aes(color = padj < 0.05 & abs(log2FoldChange) > 1)) +
    geom_hline(yintercept = -log10(0.05), linetype = 'dashed') +
    geom_vline(xintercept = c(-1, 1), linetype = 'dashed')
```

## Related Skills

- m6a-peak-calling - Identify peaks first
- differential-expression/de-results - Similar statistical concepts
- modification-visualization - Plot differential sites
