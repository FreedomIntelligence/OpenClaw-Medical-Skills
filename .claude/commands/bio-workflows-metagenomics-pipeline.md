# bio-workflows-metagenomics-pipeline

> End-to-end metagenomics workflow from FASTQ to taxonomic and functional profiles. Covers Kraken2 classification, Bracken abundance estimation, and HUMAnN functional profiling. Use when profiling metagenomic samples.

**Available tools:** Read, Bash

# Metagenomics Pipeline

Complete workflow from metagenomic FASTQ to taxonomic and functional profiles.

## Workflow Overview

```
FASTQ files
    |
    v
[1. QC & Host Removal] --> fastp + Bowtie2
    |
    v
[2. Taxonomic Classification]
    |
    +---> Kraken2 + Bracken (fast, database-dependent)
    |
    +---> MetaPhlAn (marker-based, standardized)
    |
    v
[3. Functional Profiling] --> HUMAnN
    |
    v
Taxonomic profiles + Pathway abundances
```

## Primary Path: Kraken2 + Bracken + HUMAnN

### Step 1: Quality Control and Host Removal

```bash
# QC with fastp
for sample in sample1 sample2 sample3; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o trimmed/${sample}_R1.fq.gz -O trimmed/${sample}_R2.fq.gz \
        --detect_adapter_for_pe \
        --qualified_quality_phred 20 \
        --length_required 50 \
        --html qc/${sample}_fastp.html
done

# Remove host reads (human example)
for sample in sample1 sample2 sample3; do
    bowtie2 -p 8 -x human_index \
        -1 trimmed/${sample}_R1.fq.gz \
        -2 trimmed/${sample}_R2.fq.gz \
        --un-conc-gz host_removed/${sample}_R%.fq.gz \
        > /dev/null 2> qc/${sample}_host_removal.log
done
```

### Step 2A: Kraken2 Classification

```bash
# Classify reads
for sample in sample1 sample2 sample3; do
    kraken2 --db kraken2_db \
        --threads 8 \
        --paired \
        --report kraken/${sample}.report \
        --output kraken/${sample}.output \
        host_removed/${sample}_R1.fq.gz \
        host_removed/${sample}_R2.fq.gz
done
```

### Step 2B: Bracken Abundance Estimation

```bash
# Estimate species abundance
for sample in sample1 sample2 sample3; do
    bracken -d kraken2_db \
        -i kraken/${sample}.report \
        -o bracken/${sample}.species.txt \
        -r 150 \
        -l S \
        -t 10
done

# Combine samples into abundance matrix
combine_bracken_outputs.py \
    --files bracken/*.species.txt \
    -o bracken/combined_species.txt
```

### Step 2C: Alternative - MetaPhlAn Profiling

```bash
# Profile with MetaPhlAn 4
for sample in sample1 sample2 sample3; do
    metaphlan host_removed/${sample}_R1.fq.gz,host_removed/${sample}_R2.fq.gz \
        --bowtie2out metaphlan/${sample}.bowtie2.bz2 \
        --input_type fastq \
        --nproc 8 \
        -o metaphlan/${sample}_profile.txt
done

# Merge profiles
merge_metaphlan_tables.py metaphlan/*_profile.txt > metaphlan/merged_abundance.txt
```

### Step 3: Functional Profiling with HUMAnN

```bash
# Run HUMAnN
for sample in sample1 sample2 sample3; do
    # Concatenate paired reads
    cat host_removed/${sample}_R1.fq.gz host_removed/${sample}_R2.fq.gz > \
        host_removed/${sample}_concat.fq.gz

    humann --input host_removed/${sample}_concat.fq.gz \
        --output humann/${sample} \
        --threads 8 \
        --metaphlan-options "--bowtie2db metaphlan_db"
done

# Normalize and join tables
humann_renorm_table --input humann/sample1/sample1_pathabundance.tsv \
    --output humann/sample1/sample1_pathabundance_cpm.tsv \
    --units cpm

humann_join_tables --input humann \
    --output humann/merged_pathabundance.tsv \
    --file_name pathabundance
```

### Visualization

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Bracken species table
species = pd.read_csv('bracken/combined_species.txt', sep='\t', index_col=0)

# Top 20 species heatmap
top20 = species.sum(axis=1).nlargest(20).index
plt.figure(figsize=(12, 8))
sns.heatmap(species.loc[top20], cmap='viridis', annot=False)
plt.title('Top 20 Species Abundance')
plt.tight_layout()
plt.savefig('top20_species_heatmap.pdf')

# Stacked bar plot
species_norm = species.div(species.sum()) * 100
top10 = species_norm.sum(axis=1).nlargest(10).index
other = species_norm.loc[~species_norm.index.isin(top10)].sum()

plot_data = species_norm.loc[top10].T
plot_data['Other'] = other
plot_data.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.ylabel('Relative Abundance (%)')
plt.legend(bbox_to_anchor=(1.05, 1))
plt.tight_layout()
plt.savefig('species_barplot.pdf')
```

## Parameter Recommendations

| Step | Parameter | Value |
|------|-----------|-------|
| fastp | --length_required | 50 (metagenomic reads) |
| Kraken2 | --confidence | 0.0 (default) or 0.1 |
| Bracken | -r | Read length (e.g., 150) |
| Bracken | -l | S (species) or G (genus) |
| Bracken | -t | 10 (min reads threshold) |
| MetaPhlAn | --min_cu_len | 2000 (default) |
| HUMAnN | --threads | 8+ |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Low classification rate | Database mismatch, novel organisms | Try different database, check sample type |
| High unclassified | Novel microbes, host contamination | Remove host, use larger database |
| High host reads | Incomplete host removal | Use multiple host reference genomes |
| HUMAnN slow | Large files | Increase threads, pre-filter reads |

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

THREADS=8
KRAKEN_DB="kraken2_standard_db"
HOST_INDEX="human_bt2_index"
SAMPLES="sample1 sample2 sample3"
OUTDIR="metagenomics_results"

mkdir -p ${OUTDIR}/{trimmed,host_removed,kraken,bracken,metaphlan,humann,qc}

# Step 1: QC
echo "=== QC ==="
for sample in $SAMPLES; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -O ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        --length_required 50 \
        --html ${OUTDIR}/qc/${sample}_fastp.html -w ${THREADS}
done

# Host removal
echo "=== Host Removal ==="
for sample in $SAMPLES; do
    bowtie2 -p ${THREADS} -x ${HOST_INDEX} \
        -1 ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -2 ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        --un-conc-gz ${OUTDIR}/host_removed/${sample}_R%.fq.gz \
        > /dev/null 2> ${OUTDIR}/qc/${sample}_host.log
done

# Step 2: Kraken2
echo "=== Kraken2 ==="
for sample in $SAMPLES; do
    kraken2 --db ${KRAKEN_DB} --threads ${THREADS} --paired \
        --report ${OUTDIR}/kraken/${sample}.report \
        --output ${OUTDIR}/kraken/${sample}.output \
        ${OUTDIR}/host_removed/${sample}_R1.fq.gz \
        ${OUTDIR}/host_removed/${sample}_R2.fq.gz
done

# Bracken
echo "=== Bracken ==="
for sample in $SAMPLES; do
    bracken -d ${KRAKEN_DB} \
        -i ${OUTDIR}/kraken/${sample}.report \
        -o ${OUTDIR}/bracken/${sample}.species.txt \
        -r 150 -l S -t 10
done

echo "=== Pipeline Complete ==="
echo "Kraken reports: ${OUTDIR}/kraken/"
echo "Bracken abundances: ${OUTDIR}/bracken/"
```

## Related Skills

- metagenomics/kraken-classification - Kraken2 details
- metagenomics/metaphlan-profiling - MetaPhlAn parameters
- metagenomics/abundance-estimation - Bracken options
- metagenomics/functional-profiling - HUMAnN workflow
- metagenomics/metagenome-visualization - Plotting functions
