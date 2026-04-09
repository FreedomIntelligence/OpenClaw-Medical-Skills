# bio-workflows-cnv-pipeline

> End-to-end copy number variant detection workflow from BAM files. Covers CNVkit analysis for exome/targeted sequencing with visualization and annotation. Use when detecting copy number alterations from sequencing data.

**Available tools:** Read, Bash

# CNV Pipeline

Complete workflow for detecting copy number variants from exome or targeted sequencing data.

## Workflow Overview

```
BAM files (tumor/normal or germline)
    |
    v
[1. Target Preparation] --> Create/access target BED
    |
    v
[2. Coverage Calculation] --> Read depth per target
    |
    v
[3. Reference Creation] --> Pool of normals
    |
    v
[4. CNV Calling] --------> Log2 ratios, segmentation
    |
    v
[5. Visualization] ------> Scatter plots, heatmaps
    |
    v
[6. Annotation] ---------> Gene-level CNVs
    |
    v
CNV calls with gene annotations
```

## Primary Path: CNVkit

### Step 1: Prepare Target Regions

```bash
# If using exome capture kit BED
cnvkit.py target capture_targets.bed \
    --annotate refFlat.txt \
    --split \
    -o targets.bed

# Access regions (off-target for WGS-like sensitivity)
cnvkit.py access genome.fa \
    -o access.bed

cnvkit.py antitarget targets.bed \
    --access access.bed \
    -o antitargets.bed
```

### Step 2: Calculate Coverage

```bash
# For each sample
for bam in *.bam; do
    sample=$(basename $bam .bam)

    # Target coverage
    cnvkit.py coverage $bam targets.bed \
        -o coverage/${sample}.targetcoverage.cnn

    # Antitarget coverage
    cnvkit.py coverage $bam antitargets.bed \
        -o coverage/${sample}.antitargetcoverage.cnn
done
```

### Step 3: Create Reference (Pool of Normals)

```bash
# From normal samples
cnvkit.py reference \
    coverage/normal*.targetcoverage.cnn \
    coverage/normal*.antitargetcoverage.cnn \
    --fasta genome.fa \
    -o reference.cnn

# Or flat reference (no normals available)
cnvkit.py reference \
    --fasta genome.fa \
    --targets targets.bed \
    --antitargets antitargets.bed \
    -o flat_reference.cnn
```

### Step 4: Call CNVs

```bash
for bam in tumor*.bam; do
    sample=$(basename $bam .bam)

    # Fix and segment
    cnvkit.py fix \
        coverage/${sample}.targetcoverage.cnn \
        coverage/${sample}.antitargetcoverage.cnn \
        reference.cnn \
        -o cnv/${sample}.cnr

    # Segment
    cnvkit.py segment cnv/${sample}.cnr \
        -o cnv/${sample}.cns

    # Call integer copy numbers
    cnvkit.py call cnv/${sample}.cns \
        -o cnv/${sample}.call.cns
done
```

### Step 5: Visualization

```bash
# Scatter plot for single sample
cnvkit.py scatter cnv/tumor1.cnr \
    -s cnv/tumor1.cns \
    -o plots/tumor1_scatter.pdf

# Chromosome-specific
cnvkit.py scatter cnv/tumor1.cnr \
    -s cnv/tumor1.cns \
    -c chr17 \
    -o plots/tumor1_chr17.pdf

# Diagram (chromosome ideogram)
cnvkit.py diagram cnv/tumor1.cnr \
    -s cnv/tumor1.cns \
    -o plots/tumor1_diagram.pdf

# Heatmap for multiple samples
cnvkit.py heatmap cnv/*.cns \
    -o plots/cohort_heatmap.pdf
```

### Step 6: Export and Annotation

```bash
# Export to various formats
cnvkit.py export seg cnv/*.cns -o cnv/cohort.seg
cnvkit.py export vcf cnv/tumor1.call.cns -o cnv/tumor1.vcf

# Gene-level summary
cnvkit.py genemetrics cnv/tumor1.cnr \
    -s cnv/tumor1.cns \
    --threshold 0.2 \
    -o cnv/tumor1_genes.tsv

# Filter for significant CNVs
awk '$6 < -0.4 || $6 > 0.3' cnv/tumor1_genes.tsv > cnv/tumor1_significant_genes.tsv
```

## Batch Processing Script

```bash
#!/bin/bash
set -e

TARGETS="targets.bed"
REFERENCE="reference.cnn"
OUTDIR="cnv_results"

mkdir -p ${OUTDIR}/{coverage,cnv,plots}

# Process all tumor samples
for bam in tumor*.bam; do
    sample=$(basename $bam .bam)
    echo "Processing ${sample}..."

    # Coverage
    cnvkit.py coverage $bam ${TARGETS} \
        -o ${OUTDIR}/coverage/${sample}.targetcoverage.cnn

    # Fix
    cnvkit.py fix \
        ${OUTDIR}/coverage/${sample}.targetcoverage.cnn \
        ${OUTDIR}/coverage/${sample}.antitargetcoverage.cnn \
        ${REFERENCE} \
        -o ${OUTDIR}/cnv/${sample}.cnr

    # Segment
    cnvkit.py segment ${OUTDIR}/cnv/${sample}.cnr \
        -o ${OUTDIR}/cnv/${sample}.cns

    # Call
    cnvkit.py call ${OUTDIR}/cnv/${sample}.cns \
        -o ${OUTDIR}/cnv/${sample}.call.cns

    # Plot
    cnvkit.py scatter ${OUTDIR}/cnv/${sample}.cnr \
        -s ${OUTDIR}/cnv/${sample}.cns \
        -o ${OUTDIR}/plots/${sample}.pdf
done

# Cohort heatmap
cnvkit.py heatmap ${OUTDIR}/cnv/*.cns -o ${OUTDIR}/plots/heatmap.pdf
```

## Germline CNV Calling

```bash
# For germline analysis (no tumor-normal)
cnvkit.py batch sample*.bam \
    --normal normal*.bam \
    --targets targets.bed \
    --fasta genome.fa \
    --output-reference reference.cnn \
    --output-dir cnv_output \
    --scatter --diagram

# Or use flat reference
cnvkit.py batch sample.bam \
    --method hybrid \
    --targets targets.bed \
    --fasta genome.fa \
    --output-dir cnv_output
```

## Parameter Recommendations

| Step | Parameter | Value |
|------|-----------|-------|
| target | --split | Yes (for WES) |
| segment | --method | cbs (default) |
| call | --ploidy | 2 (adjust if known) |
| call | --purity | Estimate if tumor |
| genemetrics | --threshold | 0.2 |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Noisy signal | Low coverage | Increase sequencing depth |
| No CNVs | Flat reference, normal sample | Check reference creation |
| Many small CNVs | Over-segmentation | Increase segment min size |
| Batch effects | Different capture kits | Match samples to correct reference |

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

GENOME="genome.fa"
TARGETS="capture_targets.bed"
REFFLAT="refFlat.txt"
NORMAL_BAMS="normal*.bam"
TUMOR_BAMS="tumor*.bam"
OUTDIR="cnv_results"

mkdir -p ${OUTDIR}/{coverage,cnv,plots,annotation}

# Step 1: Prepare targets
cnvkit.py target ${TARGETS} --annotate ${REFFLAT} --split -o ${OUTDIR}/targets.bed
cnvkit.py access ${GENOME} -o ${OUTDIR}/access.bed
cnvkit.py antitarget ${OUTDIR}/targets.bed --access ${OUTDIR}/access.bed -o ${OUTDIR}/antitargets.bed

# Step 2: Coverage (normals)
for bam in ${NORMAL_BAMS}; do
    sample=$(basename $bam .bam)
    cnvkit.py coverage $bam ${OUTDIR}/targets.bed -o ${OUTDIR}/coverage/${sample}.targetcoverage.cnn
    cnvkit.py coverage $bam ${OUTDIR}/antitargets.bed -o ${OUTDIR}/coverage/${sample}.antitargetcoverage.cnn
done

# Step 3: Reference
cnvkit.py reference ${OUTDIR}/coverage/normal*.cnn --fasta ${GENOME} -o ${OUTDIR}/reference.cnn

# Step 4-5: Process tumors
for bam in ${TUMOR_BAMS}; do
    sample=$(basename $bam .bam)
    cnvkit.py coverage $bam ${OUTDIR}/targets.bed -o ${OUTDIR}/coverage/${sample}.targetcoverage.cnn
    cnvkit.py coverage $bam ${OUTDIR}/antitargets.bed -o ${OUTDIR}/coverage/${sample}.antitargetcoverage.cnn
    cnvkit.py fix ${OUTDIR}/coverage/${sample}.targetcoverage.cnn \
        ${OUTDIR}/coverage/${sample}.antitargetcoverage.cnn \
        ${OUTDIR}/reference.cnn -o ${OUTDIR}/cnv/${sample}.cnr
    cnvkit.py segment ${OUTDIR}/cnv/${sample}.cnr -o ${OUTDIR}/cnv/${sample}.cns
    cnvkit.py call ${OUTDIR}/cnv/${sample}.cns -o ${OUTDIR}/cnv/${sample}.call.cns
    cnvkit.py scatter ${OUTDIR}/cnv/${sample}.cnr -s ${OUTDIR}/cnv/${sample}.cns -o ${OUTDIR}/plots/${sample}.pdf
    cnvkit.py genemetrics ${OUTDIR}/cnv/${sample}.cnr -s ${OUTDIR}/cnv/${sample}.cns -o ${OUTDIR}/annotation/${sample}_genes.tsv
done

echo "Pipeline complete. Results in ${OUTDIR}/"
```

## Related Skills

- copy-number/cnvkit-analysis - CNVkit details
- copy-number/cnv-visualization - Plotting options
- copy-number/cnv-annotation - Gene annotations
- copy-number/gatk-cnv - GATK alternative
