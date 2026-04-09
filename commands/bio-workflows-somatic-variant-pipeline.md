# bio-workflows-somatic-variant-pipeline

> End-to-end somatic variant calling from tumor-normal paired samples using Mutect2 or Strelka2. Covers preprocessing, variant calling, filtering, and annotation for cancer genomics. Use when calling somatic mutations from tumor-normal pairs.

**Available tools:** Read, Bash

# Somatic Variant Pipeline

Complete workflow for calling somatic mutations from tumor-normal paired samples.

## Pipeline Overview

```
Tumor BAM + Normal BAM
    │
    ├── Preprocessing (if needed)
    │   └── MarkDuplicates, BQSR
    │
    ├── Variant Calling
    │   ├── Mutect2 (GATK) - SNVs + indels
    │   └── Strelka2 - SNVs + indels (faster)
    │
    ├── Filtering
    │   ├── FilterMutectCalls
    │   ├── Contamination estimation
    │   └── Orientation bias filtering
    │
    ├── Annotation
    │   ├── Funcotator / VEP
    │   └── Cancer-specific databases
    │
    └── Output: Filtered somatic VCF
```

## Mutect2 Workflow (GATK)

### Step 1: Panel of Normals (Optional but Recommended)

```bash
# Create PON from multiple normal samples
for normal in normal1.bam normal2.bam normal3.bam; do
    sample=$(basename $normal .bam)
    gatk Mutect2 \
        -R reference.fa \
        -I $normal \
        --max-mnp-distance 0 \
        -O ${sample}.vcf.gz
done

# Combine into PON
gatk GenomicsDBImport \
    -R reference.fa \
    --genomicsdb-workspace-path pon_db \
    -V normal1.vcf.gz \
    -V normal2.vcf.gz \
    -V normal3.vcf.gz \
    -L intervals.bed

gatk CreateSomaticPanelOfNormals \
    -R reference.fa \
    -V gendb://pon_db \
    -O pon.vcf.gz
```

### Step 2: Call Somatic Variants

```bash
gatk Mutect2 \
    -R reference.fa \
    -I tumor.bam \
    -I normal.bam \
    -normal normal_sample_name \
    --germline-resource af-only-gnomad.vcf.gz \
    --panel-of-normals pon.vcf.gz \
    --f1r2-tar-gz f1r2.tar.gz \
    -O unfiltered.vcf.gz
```

### Step 3: Learn Orientation Bias

```bash
gatk LearnReadOrientationModel \
    -I f1r2.tar.gz \
    -O read-orientation-model.tar.gz
```

### Step 4: Calculate Contamination

```bash
gatk GetPileupSummaries \
    -I tumor.bam \
    -V small_exac_common.vcf.gz \
    -L small_exac_common.vcf.gz \
    -O tumor_pileups.table

gatk GetPileupSummaries \
    -I normal.bam \
    -V small_exac_common.vcf.gz \
    -L small_exac_common.vcf.gz \
    -O normal_pileups.table

gatk CalculateContamination \
    -I tumor_pileups.table \
    -matched normal_pileups.table \
    -O contamination.table \
    --tumor-segmentation segments.table
```

### Step 5: Filter Variants

```bash
gatk FilterMutectCalls \
    -R reference.fa \
    -V unfiltered.vcf.gz \
    --contamination-table contamination.table \
    --tumor-segmentation segments.table \
    --ob-priors read-orientation-model.tar.gz \
    -O filtered.vcf.gz

# Extract PASS variants
bcftools view -f PASS filtered.vcf.gz -Oz -o somatic_final.vcf.gz
```

## Strelka2 Workflow (Faster Alternative)

```bash
# Configure
configureStrelkaSomaticWorkflow.py \
    --normalBam normal.bam \
    --tumorBam tumor.bam \
    --referenceFasta reference.fa \
    --runDir strelka_run

# Execute
strelka_run/runWorkflow.py -m local -j 16

# Output files
# strelka_run/results/variants/somatic.snvs.vcf.gz
# strelka_run/results/variants/somatic.indels.vcf.gz

# Merge SNVs and indels
bcftools concat \
    strelka_run/results/variants/somatic.snvs.vcf.gz \
    strelka_run/results/variants/somatic.indels.vcf.gz \
    -a -Oz -o strelka_somatic.vcf.gz
```

## Annotation

### Funcotator (GATK)

```bash
gatk Funcotator \
    -R reference.fa \
    -V somatic_final.vcf.gz \
    -O annotated.vcf.gz \
    --output-file-format VCF \
    --data-sources-path funcotator_dataSources.v1.7 \
    --ref-version hg38
```

### VEP with Cancer Databases

```bash
vep -i somatic_final.vcf.gz -o annotated.vcf \
    --vcf --cache --offline \
    --assembly GRCh38 \
    --everything \
    --plugin CADD,cadd_scores.tsv.gz \
    --custom cosmic.vcf.gz,COSMIC,vcf,exact,0,CNT \
    --fork 4
```

## Complete Pipeline Script

```bash
#!/bin/bash
set -euo pipefail

TUMOR_BAM=$1
NORMAL_BAM=$2
NORMAL_NAME=$3
REFERENCE=$4
OUTPUT_PREFIX=$5
GNOMAD=$6
PON=$7
THREADS=16

echo "=== Step 1: Mutect2 calling ==="
gatk Mutect2 \
    -R $REFERENCE \
    -I $TUMOR_BAM \
    -I $NORMAL_BAM \
    -normal $NORMAL_NAME \
    --germline-resource $GNOMAD \
    --panel-of-normals $PON \
    --f1r2-tar-gz ${OUTPUT_PREFIX}_f1r2.tar.gz \
    --native-pair-hmm-threads $THREADS \
    -O ${OUTPUT_PREFIX}_unfiltered.vcf.gz

echo "=== Step 2: Learn orientation bias ==="
gatk LearnReadOrientationModel \
    -I ${OUTPUT_PREFIX}_f1r2.tar.gz \
    -O ${OUTPUT_PREFIX}_orientation.tar.gz

echo "=== Step 3: Pileup summaries ==="
gatk GetPileupSummaries \
    -I $TUMOR_BAM \
    -V $GNOMAD \
    -L $GNOMAD \
    -O ${OUTPUT_PREFIX}_tumor_pileups.table

gatk GetPileupSummaries \
    -I $NORMAL_BAM \
    -V $GNOMAD \
    -L $GNOMAD \
    -O ${OUTPUT_PREFIX}_normal_pileups.table

echo "=== Step 4: Calculate contamination ==="
gatk CalculateContamination \
    -I ${OUTPUT_PREFIX}_tumor_pileups.table \
    -matched ${OUTPUT_PREFIX}_normal_pileups.table \
    -O ${OUTPUT_PREFIX}_contamination.table \
    --tumor-segmentation ${OUTPUT_PREFIX}_segments.table

echo "=== Step 5: Filter variants ==="
gatk FilterMutectCalls \
    -R $REFERENCE \
    -V ${OUTPUT_PREFIX}_unfiltered.vcf.gz \
    --contamination-table ${OUTPUT_PREFIX}_contamination.table \
    --tumor-segmentation ${OUTPUT_PREFIX}_segments.table \
    --ob-priors ${OUTPUT_PREFIX}_orientation.tar.gz \
    -O ${OUTPUT_PREFIX}_filtered.vcf.gz

echo "=== Step 6: Extract PASS variants ==="
bcftools view -f PASS ${OUTPUT_PREFIX}_filtered.vcf.gz \
    -Oz -o ${OUTPUT_PREFIX}_somatic.vcf.gz
bcftools index -t ${OUTPUT_PREFIX}_somatic.vcf.gz

echo "=== Step 7: Statistics ==="
bcftools stats ${OUTPUT_PREFIX}_somatic.vcf.gz > ${OUTPUT_PREFIX}_stats.txt

echo "=== Pipeline complete ==="
echo "Somatic variants: ${OUTPUT_PREFIX}_somatic.vcf.gz"
echo "Stats: ${OUTPUT_PREFIX}_stats.txt"
```

## Tumor-Only Mode

When matched normal is unavailable:

```bash
gatk Mutect2 \
    -R reference.fa \
    -I tumor.bam \
    --germline-resource af-only-gnomad.vcf.gz \
    --panel-of-normals pon.vcf.gz \
    -O tumor_only.vcf.gz
```

Note: Higher false positive rate without matched normal.

## Key Resources

| Resource | Purpose |
|----------|---------|
| gnomAD AF-only | Germline filtering |
| Panel of Normals | Technical artifact removal |
| COSMIC | Known cancer mutations |
| Funcotator data sources | Functional annotation |

## Quality Metrics

```bash
# Variant counts by filter status
bcftools query -f '%FILTER\n' filtered.vcf.gz | sort | uniq -c

# Ti/Tv ratio (expect ~2-3 for somatic)
bcftools stats filtered.vcf.gz | grep TSTV

# Variant allele frequency distribution
bcftools query -f '%AF\n' somatic_final.vcf.gz | \
    awk '{print int($1*100)/100}' | sort -n | uniq -c
```

## Related Skills

- variant-calling/gatk-variant-calling - Germline variant calling
- variant-calling/filtering-best-practices - Filtering strategies
- variant-calling/variant-annotation - VEP/SnpEff annotation
- copy-number/cnvkit-analysis - Somatic CNV calling
- variant-calling/variant-annotation - Germline pipeline
