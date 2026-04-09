# ngs-analysis

> Next-generation sequencing data analysis pipelines including bulk RNA-seq, scRNA-seq preprocessing, variant calling, and quality control. Use when working with FASTQ files, alignment (STAR, BWA), quantification (featureCounts, Salmon), DESeq2/edgeR analysis, or building NGS pipelines. Supports GEO/SRA data retrieval.

# NGS Data Analysis Pipelines

## Data Retrieval from GEO/SRA

```bash
# Install SRA toolkit
conda install -c bioconda sra-tools

# Download SRA files
prefetch SRR12345678
fastq-dump --split-files --gzip SRR12345678

# Parallel download with fasterq-dump
fasterq-dump --split-files -e 8 SRR12345678
gzip SRR12345678_*.fastq
```

## Quality Control

```bash
# FastQC
fastqc -t 8 -o fastqc_output/ *.fastq.gz

# MultiQC aggregation
multiqc fastqc_output/ -o multiqc_report/

# Trimming with fastp
fastp -i R1.fastq.gz -I R2.fastq.gz \
    -o R1_trimmed.fastq.gz -O R2_trimmed.fastq.gz \
    --detect_adapter_for_pe --thread 8 \
    --html fastp_report.html
```

## Bulk RNA-seq Pipeline

### Alignment with STAR

```bash
# Build index (once)
STAR --runMode genomeGenerate \
    --genomeDir star_index/ \
    --genomeFastaFiles genome.fa \
    --sjdbGTFfile genes.gtf \
    --runThreadN 16

# Alignment
STAR --runThreadN 16 \
    --genomeDir star_index/ \
    --readFilesIn R1.fastq.gz R2.fastq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate \
    --quantMode GeneCounts
```

### Quantification with featureCounts

```bash
featureCounts -T 8 -p -B -C \
    -a genes.gtf \
    -o counts.txt \
    *.bam
```

### Salmon Pseudo-alignment

```bash
# Index
salmon index -t transcripts.fa -i salmon_index -k 31

# Quantification
salmon quant -i salmon_index -l A \
    -1 R1.fastq.gz -2 R2.fastq.gz \
    -p 8 -o salmon_quant/
```

## Differential Expression with DESeq2

```r
library(DESeq2)
library(tidyverse)

# Load counts
counts <- read.table("counts.txt", header=TRUE, row.names=1)
coldata <- read.csv("sample_info.csv", row.names=1)

# Create DESeq object
dds <- DESeqDataSetFromMatrix(
    countData = counts,
    colData = coldata,
    design = ~ condition
)

# Filter low counts
keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep,]

# Run DESeq2
dds <- DESeq(dds)
res <- results(dds, contrast=c("condition", "treatment", "control"))
res_df <- as.data.frame(res) %>%
    rownames_to_column("gene") %>%
    filter(!is.na(padj)) %>%
    arrange(padj)

# Significant genes
sig_genes <- res_df %>%
    filter(padj < 0.05, abs(log2FoldChange) > 1)

write.csv(res_df, "DEG_results.csv", row.names=FALSE)
```

## Variant Calling (Somatic)

```bash
# BWA-MEM2 alignment
bwa-mem2 index reference.fa
bwa-mem2 mem -t 16 reference.fa R1.fq.gz R2.fq.gz | \
    samtools sort -@ 8 -o aligned.bam

# Mark duplicates
gatk MarkDuplicates -I aligned.bam -O marked.bam -M metrics.txt

# BQSR
gatk BaseRecalibrator -R ref.fa -I marked.bam \
    --known-sites known_sites.vcf -O recal.table
gatk ApplyBQSR -R ref.fa -I marked.bam \
    --bqsr-recal-file recal.table -O recal.bam

# Mutect2 for somatic variants
gatk Mutect2 -R ref.fa -I tumor.bam -I normal.bam \
    -normal normal_sample -O somatic.vcf.gz
```

## Python Integration

```python
import pandas as pd
import subprocess
from pathlib import Path

def run_pipeline(fastq_dir, output_dir, genome_index):
    """Run complete RNA-seq pipeline"""
    fastq_files = list(Path(fastq_dir).glob("*_R1.fastq.gz"))
    
    for r1 in fastq_files:
        sample = r1.stem.replace("_R1.fastq", "")
        r2 = r1.parent / f"{sample}_R2.fastq.gz"
        
        # STAR alignment
        cmd = f"""
        STAR --runThreadN 16 --genomeDir {genome_index} \
            --readFilesIn {r1} {r2} --readFilesCommand zcat \
            --outFileNamePrefix {output_dir}/{sample}_ \
            --outSAMtype BAM SortedByCoordinate
        """
        subprocess.run(cmd, shell=True, check=True)
```

See `references/conda_envs.md` for environment setup.
See `scripts/batch_pipeline.py` for parallel processing.
