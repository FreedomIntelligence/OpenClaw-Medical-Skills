# bio-gatk-variant-calling

> Variant calling with GATK HaplotypeCaller following best practices. Covers germline SNP/indel calling, GVCF workflow for cohorts, joint genotyping, and variant quality score recalibration (VQSR). Use when calling variants with GATK HaplotypeCaller.

## Version Compatibility

Reference examples tested with: GATK 4.5+, bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# GATK Variant Calling

GATK HaplotypeCaller is the gold standard for germline variant calling. This skill covers the GATK Best Practices workflow.

## Prerequisites

BAM files should be preprocessed:
1. Mark duplicates
2. Base quality score recalibration (BQSR) - optional but recommended

## Single-Sample Calling

**Goal:** Call germline SNPs and indels from a single sample using HaplotypeCaller.

**Approach:** Run local de novo assembly of haplotypes in active regions to detect variants with optional annotation enrichment.

**"Call variants from my BAM file using GATK"** → Perform local haplotype assembly and genotyping on aligned reads using HaplotypeCaller.

### Basic HaplotypeCaller

```bash
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample.bam \
    -O sample.vcf.gz
```

### With Standard Annotations

```bash
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample.bam \
    -O sample.vcf.gz \
    -A Coverage \
    -A QualByDepth \
    -A FisherStrand \
    -A StrandOddsRatio \
    -A MappingQualityRankSumTest \
    -A ReadPosRankSumTest
```

### Target Intervals (Exome/Panel)

```bash
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample.bam \
    -L targets.interval_list \
    -O sample.vcf.gz
```

### Adjust Calling Confidence

```bash
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample.bam \
    -O sample.vcf.gz \
    --standard-min-confidence-threshold-for-calling 20
```

## GVCF Workflow (Recommended for Cohorts)

**Goal:** Enable joint genotyping across a cohort by generating per-sample genomic VCFs.

**Approach:** Call each sample in GVCF mode (-ERC GVCF), combine into a GenomicsDB or merged GVCF, then jointly genotype.

The GVCF workflow enables joint genotyping across samples for better variant calls.

### Step 1: Generate GVCFs per Sample

```bash
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample.bam \
    -O sample.g.vcf.gz \
    -ERC GVCF
```

### Step 2: Combine GVCFs (GenomicsDBImport)

```bash
# Create sample map file
# sample_map.txt:
# sample1    /path/to/sample1.g.vcf.gz
# sample2    /path/to/sample2.g.vcf.gz

gatk GenomicsDBImport \
    --genomicsdb-workspace-path genomicsdb \
    --sample-name-map sample_map.txt \
    -L intervals.interval_list
```

### Alternative: CombineGVCFs (smaller cohorts)

```bash
gatk CombineGVCFs \
    -R reference.fa \
    -V sample1.g.vcf.gz \
    -V sample2.g.vcf.gz \
    -V sample3.g.vcf.gz \
    -O cohort.g.vcf.gz
```

### Step 3: Joint Genotyping

```bash
# From GenomicsDB
gatk GenotypeGVCFs \
    -R reference.fa \
    -V gendb://genomicsdb \
    -O cohort.vcf.gz

# From combined GVCF
gatk GenotypeGVCFs \
    -R reference.fa \
    -V cohort.g.vcf.gz \
    -O cohort.vcf.gz
```

## Variant Quality Score Recalibration (VQSR)

**Goal:** Apply machine learning-based variant filtering using known truth/training sets.

**Approach:** Build a Gaussian mixture model from annotation values at known sites, then apply a sensitivity threshold to classify variants.

Machine learning-based filtering using known variant sites. Requires many variants (WGS preferred).

### SNP Recalibration

```bash
# Build SNP model
gatk VariantRecalibrator \
    -R reference.fa \
    -V cohort.vcf.gz \
    --resource:hapmap,known=false,training=true,truth=true,prior=15.0 hapmap.vcf.gz \
    --resource:omni,known=false,training=true,truth=false,prior=12.0 omni.vcf.gz \
    --resource:1000G,known=false,training=true,truth=false,prior=10.0 1000G.vcf.gz \
    --resource:dbsnp,known=true,training=false,truth=false,prior=2.0 dbsnp.vcf.gz \
    -an QD -an MQ -an MQRankSum -an ReadPosRankSum -an FS -an SOR \
    -mode SNP \
    -O snp.recal \
    --tranches-file snp.tranches

# Apply SNP filter
gatk ApplyVQSR \
    -R reference.fa \
    -V cohort.vcf.gz \
    -O cohort.snp_recal.vcf.gz \
    --recal-file snp.recal \
    --tranches-file snp.tranches \
    --truth-sensitivity-filter-level 99.5 \
    -mode SNP
```

### Indel Recalibration

```bash
# Build Indel model
gatk VariantRecalibrator \
    -R reference.fa \
    -V cohort.snp_recal.vcf.gz \
    --resource:mills,known=false,training=true,truth=true,prior=12.0 Mills.vcf.gz \
    --resource:dbsnp,known=true,training=false,truth=false,prior=2.0 dbsnp.vcf.gz \
    -an QD -an MQRankSum -an ReadPosRankSum -an FS -an SOR \
    -mode INDEL \
    --max-gaussians 4 \
    -O indel.recal \
    --tranches-file indel.tranches

# Apply Indel filter
gatk ApplyVQSR \
    -R reference.fa \
    -V cohort.snp_recal.vcf.gz \
    -O cohort.vqsr.vcf.gz \
    --recal-file indel.recal \
    --tranches-file indel.tranches \
    --truth-sensitivity-filter-level 99.0 \
    -mode INDEL
```

## Hard Filtering (When VQSR Not Suitable)

**Goal:** Apply fixed-threshold filters when the dataset is too small for VQSR.

**Approach:** Separate SNPs and indels, apply GATK-recommended annotation thresholds, then merge results.

For small datasets, exomes, or single samples where VQSR fails.

### Extract SNPs and Indels

```bash
gatk SelectVariants \
    -R reference.fa \
    -V cohort.vcf.gz \
    --select-type-to-include SNP \
    -O snps.vcf.gz

gatk SelectVariants \
    -R reference.fa \
    -V cohort.vcf.gz \
    --select-type-to-include INDEL \
    -O indels.vcf.gz
```

### Apply Hard Filters

```bash
# Filter SNPs
gatk VariantFiltration \
    -R reference.fa \
    -V snps.vcf.gz \
    -O snps.filtered.vcf.gz \
    --filter-expression "QD < 2.0" --filter-name "QD2" \
    --filter-expression "FS > 60.0" --filter-name "FS60" \
    --filter-expression "MQ < 40.0" --filter-name "MQ40" \
    --filter-expression "MQRankSum < -12.5" --filter-name "MQRankSum-12.5" \
    --filter-expression "ReadPosRankSum < -8.0" --filter-name "ReadPosRankSum-8" \
    --filter-expression "SOR > 3.0" --filter-name "SOR3"

# Filter Indels
gatk VariantFiltration \
    -R reference.fa \
    -V indels.vcf.gz \
    -O indels.filtered.vcf.gz \
    --filter-expression "QD < 2.0" --filter-name "QD2" \
    --filter-expression "FS > 200.0" --filter-name "FS200" \
    --filter-expression "ReadPosRankSum < -20.0" --filter-name "ReadPosRankSum-20" \
    --filter-expression "SOR > 10.0" --filter-name "SOR10"
```

### Merge Filtered Variants

```bash
gatk MergeVcfs \
    -I snps.filtered.vcf.gz \
    -I indels.filtered.vcf.gz \
    -O cohort.filtered.vcf.gz
```

## Base Quality Score Recalibration (BQSR)

**Goal:** Correct systematic errors in base quality scores before variant calling.

**Approach:** Model quality score errors at known variant sites with BaseRecalibrator, then apply corrections with ApplyBQSR.

Preprocessing step to correct systematic errors in base quality scores.

### Step 1: BaseRecalibrator

```bash
gatk BaseRecalibrator \
    -R reference.fa \
    -I sample.bam \
    --known-sites dbsnp.vcf.gz \
    --known-sites known_indels.vcf.gz \
    -O recal_data.table
```

### Step 2: ApplyBQSR

```bash
gatk ApplyBQSR \
    -R reference.fa \
    -I sample.bam \
    --bqsr-recal-file recal_data.table \
    -O sample.recal.bam
```

## Parallel Processing

**Goal:** Reduce wall-clock time for variant calling on large datasets.

**Approach:** Scatter by chromosome or interval, run HaplotypeCaller in parallel, then gather results.

### Scatter by Interval

```bash
# Split calling across intervals
for interval in chr{1..22} chrX chrY; do
    gatk HaplotypeCaller \
        -R reference.fa \
        -I sample.bam \
        -L $interval \
        -O sample.${interval}.g.vcf.gz \
        -ERC GVCF &
done
wait

# Gather GVCFs
gatk GatherVcfs \
    -I sample.chr1.g.vcf.gz \
    -I sample.chr2.g.vcf.gz \
    ... \
    -O sample.g.vcf.gz
```

### Native Pairwise Parallelism

```bash
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample.bam \
    -O sample.vcf.gz \
    --native-pair-hmm-threads 4
```

## CNN Score Variant Filter (Deep Learning)

**Goal:** Filter variants using a deep learning model as an alternative to VQSR.

**Approach:** Score variants with CNNScoreVariants using reference context, then filter by tranche sensitivity.

Alternative to VQSR using convolutional neural network.

### Score Variants

```bash
gatk CNNScoreVariants \
    -R reference.fa \
    -V cohort.vcf.gz \
    -O cohort.cnn_scored.vcf.gz \
    --tensor-type reference
```

### Filter by CNN Score

```bash
gatk FilterVariantTranches \
    -V cohort.cnn_scored.vcf.gz \
    -O cohort.cnn_filtered.vcf.gz \
    --resource hapmap.vcf.gz \
    --resource mills.vcf.gz \
    --info-key CNN_1D \
    --snp-tranche 99.95 \
    --indel-tranche 99.4
```

## Complete Single-Sample Pipeline

**Goal:** Run the full GATK best practices workflow from BQSR through filtered variants.

**Approach:** Chain BaseRecalibrator, ApplyBQSR, HaplotypeCaller (GVCF mode), GenotypeGVCFs, and hard filtering.

```bash
#!/bin/bash
SAMPLE=$1
REF=reference.fa
DBSNP=dbsnp.vcf.gz
KNOWN_INDELS=known_indels.vcf.gz

# BQSR
gatk BaseRecalibrator -R $REF -I ${SAMPLE}.bam \
    --known-sites $DBSNP --known-sites $KNOWN_INDELS \
    -O ${SAMPLE}.recal.table

gatk ApplyBQSR -R $REF -I ${SAMPLE}.bam \
    --bqsr-recal-file ${SAMPLE}.recal.table \
    -O ${SAMPLE}.recal.bam

# Call variants
gatk HaplotypeCaller -R $REF -I ${SAMPLE}.recal.bam \
    -O ${SAMPLE}.g.vcf.gz -ERC GVCF

# Single-sample genotyping
gatk GenotypeGVCFs -R $REF -V ${SAMPLE}.g.vcf.gz \
    -O ${SAMPLE}.vcf.gz

# Hard filter
gatk VariantFiltration -R $REF -V ${SAMPLE}.vcf.gz \
    -O ${SAMPLE}.filtered.vcf.gz \
    --filter-expression "QD < 2.0" --filter-name "LowQD" \
    --filter-expression "FS > 60.0" --filter-name "HighFS" \
    --filter-expression "MQ < 40.0" --filter-name "LowMQ"
```

## Key Annotations

| Annotation | Description | Good Values |
|------------|-------------|-------------|
| QD | Quality by Depth | > 2.0 |
| FS | Fisher Strand | < 60 (SNP), < 200 (Indel) |
| SOR | Strand Odds Ratio | < 3 (SNP), < 10 (Indel) |
| MQ | Mapping Quality | > 40 |
| MQRankSum | MQ Rank Sum Test | > -12.5 |
| ReadPosRankSum | Read Position Rank Sum | > -8.0 (SNP), > -20.0 (Indel) |

## Resource Files

| Resource | Use |
|----------|-----|
| dbSNP | Known variants (prior=2.0) |
| HapMap | Training/truth SNPs (prior=15.0) |
| Omni | Training SNPs (prior=12.0) |
| 1000G SNPs | Training SNPs (prior=10.0) |
| Mills Indels | Training/truth indels (prior=12.0) |

## Related Skills

- variant-calling - bcftools alternative
- alignment-files - BAM preprocessing
- filtering-best-practices - Post-calling filtering
- variant-normalization - Normalize before annotation
- vep-snpeff-annotation - Annotate final calls
