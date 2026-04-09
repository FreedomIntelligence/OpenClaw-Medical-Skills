# bio-workflows-rnaseq-to-de

> End-to-end RNA-seq workflow from FASTQ files to differential expression results. Covers QC, quantification (Salmon or STAR+featureCounts), and DESeq2 analysis with visualization. Use when running RNA-seq from FASTQ to DE results.

**Available tools:** Read, Bash

# RNA-seq to Differential Expression Workflow

Complete pipeline from raw FASTQ files to differential expression results.

## Workflow Overview

```
FASTQ files
    |
    v
[1. QC & Trimming] -----> fastp
    |
    v
[2. Quantification] ----> Salmon (recommended) or STAR + featureCounts
    |
    v
[3. Import to R] -------> tximport (for Salmon) or direct counts
    |
    v
[4. DE Analysis] -------> DESeq2
    |
    v
[5. Visualization] -----> Volcano, MA, heatmaps
    |
    v
Significant gene list
```

## Primary Path: Salmon + DESeq2

### Step 1: Quality Control with fastp

```bash
# Single sample
fastp -i sample_R1.fastq.gz -I sample_R2.fastq.gz \
    -o sample_R1.trimmed.fq.gz -O sample_R2.trimmed.fq.gz \
    --detect_adapter_for_pe \
    --qualified_quality_phred 20 \
    --length_required 35 \
    --html sample_fastp.html

# Batch processing
for sample in sample1 sample2 sample3; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o trimmed/${sample}_R1.fq.gz -O trimmed/${sample}_R2.fq.gz \
        --detect_adapter_for_pe \
        --html qc/${sample}_fastp.html
done
```

**QC Checkpoint 1:** Check fastp reports
- Q30 bases >80%
- Adapter content <5%
- Duplication rate reasonable for library type

### Step 2: Salmon Quantification

```bash
# Build index (once per transcriptome)
salmon index -t transcriptome.fa -i salmon_index -k 31

# Quantify each sample
for sample in sample1 sample2 sample3; do
    salmon quant -i salmon_index \
        -l A \
        -1 trimmed/${sample}_R1.fq.gz \
        -2 trimmed/${sample}_R2.fq.gz \
        -o quants/${sample} \
        --validateMappings \
        --gcBias \
        --seqBias \
        -p 8
done
```

**QC Checkpoint 2:** Check Salmon logs
- Mapping rate >70%
- >10 million reads mapped

### Step 3: Import with tximport

```r
library(tximport)
library(DESeq2)

# Create tx2gene mapping (Ensembl example)
tx2gene <- read.csv('tx2gene.csv')  # columns: TXNAME, GENEID

# List quantification files
samples <- c('sample1', 'sample2', 'sample3', 'sample4', 'sample5', 'sample6')
files <- file.path('quants', samples, 'quant.sf')
names(files) <- samples

# Import transcript-level estimates
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)

# Create sample metadata
coldata <- data.frame(
    condition = factor(c('control', 'control', 'control', 'treated', 'treated', 'treated')),
    row.names = samples
)
```

### Step 4: DESeq2 Analysis

```r
# Create DESeqDataSet from tximport
dds <- DESeqDataSetFromTximport(txi, colData = coldata, design = ~ condition)

# Pre-filter low count genes
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep,]

# Set reference level
dds$condition <- relevel(dds$condition, ref = 'control')

# Run DESeq2
dds <- DESeq(dds)

# Get results with shrinkage
res <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')

# Summary
summary(res)
```

**QC Checkpoint 3:** Check DESeq2 diagnostics
- Dispersion plot shows expected trend
- PCA separates conditions
- No severe outliers in sample distances

### Step 5: Visualization and Export

```r
library(ggplot2)
library(pheatmap)
library(ggrepel)

# Volcano plot
res_df <- as.data.frame(res)
res_df$gene <- rownames(res_df)
res_df$significant <- res_df$padj < 0.05 & abs(res_df$log2FoldChange) > 1

ggplot(res_df, aes(x = log2FoldChange, y = -log10(pvalue), color = significant)) +
    geom_point(alpha = 0.5) +
    scale_color_manual(values = c('grey', 'red')) +
    theme_minimal() +
    labs(title = 'Volcano Plot', x = 'Log2 Fold Change', y = '-Log10 P-value')

# Heatmap of top genes
vsd <- vst(dds, blind = FALSE)
top_genes <- head(order(res$padj), 50)
pheatmap(assay(vsd)[top_genes,], scale = 'row', show_rownames = FALSE)

# Export significant genes
sig_genes <- subset(res, padj < 0.05 & abs(log2FoldChange) > 1)
write.csv(as.data.frame(sig_genes), 'significant_genes.csv')
```

## Alternative Path: STAR + featureCounts + DESeq2

### Step 2 Alternative: STAR Alignment

```bash
# Build STAR index (once)
STAR --runMode genomeGenerate \
    --genomeDir star_index \
    --genomeFastaFiles genome.fa \
    --sjdbGTFfile genes.gtf \
    --sjdbOverhang 100 \
    --runThreadN 8

# Align each sample
for sample in sample1 sample2 sample3; do
    STAR --genomeDir star_index \
        --readFilesIn trimmed/${sample}_R1.fq.gz trimmed/${sample}_R2.fq.gz \
        --readFilesCommand zcat \
        --outFileNamePrefix aligned/${sample}_ \
        --outSAMtype BAM SortedByCoordinate \
        --quantMode GeneCounts \
        --runThreadN 8
done
```

### Step 3 Alternative: featureCounts

```bash
# Count reads per gene
featureCounts -T 8 -p --countReadPairs \
    -a genes.gtf \
    -o counts.txt \
    aligned/*_Aligned.sortedByCoord.out.bam
```

### Step 4 Alternative: Load Counts Directly

```r
# Load featureCounts output
counts <- read.table('counts.txt', header = TRUE, row.names = 1, skip = 1)
counts <- counts[, 6:ncol(counts)]  # Remove annotation columns
colnames(counts) <- gsub('_Aligned.sortedByCoord.out.bam', '', colnames(counts))

# Create DESeqDataSet directly
dds <- DESeqDataSetFromMatrix(countData = counts, colData = coldata, design = ~ condition)
```

## Parameter Recommendations

| Step | Parameter | Recommendation |
|------|-----------|----------------|
| fastp | --qualified_quality_phred | 20 (standard) |
| fastp | --length_required | 35 for 2x100, 50 for 2x150 |
| Salmon | -l | A (auto-detect library type) |
| Salmon | --gcBias | Enable for better accuracy |
| STAR | --sjdbOverhang | read_length - 1 |
| featureCounts | -s | 0=unstranded, 1=stranded, 2=reversely stranded |
| DESeq2 | lfcShrink type | apeglm (recommended) |
| DESeq2 | alpha | 0.05 (standard significance) |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Low mapping rate (<50%) | Wrong reference, contamination | Check species, run FastQ Screen |
| High duplication | Low complexity library, over-sequencing | Check library prep, may be normal for low-input |
| No DE genes | Low power, batch effects | Add replicates, include batch in design |
| All genes DE | Normalization issue, sample swap | Check sample metadata, rerun normalization |
| Outlier samples | Technical failure, sample swap | Remove or investigate, check PCA |

## Complete Bash Pipeline Script

```bash
#!/bin/bash
set -e

THREADS=8
SAMPLES="sample1 sample2 sample3 sample4 sample5 sample6"
SALMON_INDEX="salmon_index"
OUTDIR="results"

mkdir -p ${OUTDIR}/{trimmed,quants,qc}

# Step 1: QC and trim
for sample in $SAMPLES; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -O ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        --detect_adapter_for_pe \
        --html ${OUTDIR}/qc/${sample}_fastp.html \
        -w ${THREADS}
done

# Step 2: Quantify
for sample in $SAMPLES; do
    salmon quant -i ${SALMON_INDEX} -l A \
        -1 ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -2 ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        -o ${OUTDIR}/quants/${sample} \
        --validateMappings --gcBias -p ${THREADS}
done

echo "Quantification complete. Run R script for DE analysis."
```

## Complete R Analysis Script

```r
library(tximport)
library(DESeq2)
library(apeglm)
library(ggplot2)
library(pheatmap)

# Configuration
samples <- c('sample1', 'sample2', 'sample3', 'sample4', 'sample5', 'sample6')
conditions <- c('control', 'control', 'control', 'treated', 'treated', 'treated')
quant_dir <- 'results/quants'

# Import
tx2gene <- read.csv('tx2gene.csv')
files <- file.path(quant_dir, samples, 'quant.sf')
names(files) <- samples
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)

# DESeq2
coldata <- data.frame(condition = factor(conditions), row.names = samples)
dds <- DESeqDataSetFromTximport(txi, colData = coldata, design = ~ condition)
dds <- dds[rowSums(counts(dds)) >= 10,]
dds$condition <- relevel(dds$condition, ref = 'control')
dds <- DESeq(dds)

# Results
res <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')
sig <- subset(res, padj < 0.05 & abs(log2FoldChange) > 1)

cat('Significant genes:', nrow(sig), '\n')
write.csv(as.data.frame(sig), 'significant_genes.csv')
```

## Related Skills

- read-qc/fastp-workflow - Detailed QC options and parameters
- rna-quantification/alignment-free-quant - Salmon and kallisto details
- rna-quantification/tximport-workflow - tximport options and tx2gene creation
- differential-expression/deseq2-basics - Complete DESeq2 reference
- differential-expression/de-visualization - Advanced visualization options
- pathway-analysis/go-enrichment - Next step: functional enrichment
