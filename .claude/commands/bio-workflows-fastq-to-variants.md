# bio-workflows-fastq-to-variants

> End-to-end DNA sequencing workflow from FASTQ files to variant calls. Covers QC, alignment with BWA, BAM processing, and variant calling with bcftools or GATK HaplotypeCaller. Use when calling variants from raw sequencing reads.

**Available tools:** Read, Bash

# FASTQ to Variants Workflow

Complete pipeline from raw DNA sequencing FASTQ files to filtered variant calls.

## Workflow Overview

```
FASTQ files
    |
    v
[1. QC & Trimming] -----> fastp
    |
    v
[2. Alignment] ---------> bwa-mem2
    |
    v
[3. BAM Processing] ----> sort, markdup, index
    |
    v
[4. Variant Calling] ---> bcftools (primary) or GATK
    |
    v
[5. Filtering] ---------> Quality filters
    |
    v
Filtered VCF
```

## Primary Path: BWA + bcftools

### Step 1: Quality Control with fastp

```bash
# Single sample
fastp -i sample_R1.fastq.gz -I sample_R2.fastq.gz \
    -o sample_R1.trimmed.fq.gz -O sample_R2.trimmed.fq.gz \
    --detect_adapter_for_pe \
    --qualified_quality_phred 20 \
    --length_required 50 \
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
- Q30 bases >85% (DNA typically higher quality than RNA)
- Adapter content <1%
- No unusual GC distribution

### Step 2: BWA-MEM2 Alignment

```bash
# Index reference (once)
bwa-mem2 index reference.fa

# Align with read group info
for sample in sample1 sample2 sample3; do
    bwa-mem2 mem -t 8 \
        -R "@RG\tID:${sample}\tSM:${sample}\tPL:ILLUMINA\tLB:lib1" \
        reference.fa \
        trimmed/${sample}_R1.fq.gz \
        trimmed/${sample}_R2.fq.gz \
    | samtools view -bS - > aligned/${sample}.bam
done
```

**QC Checkpoint 2:** Check alignment stats
```bash
samtools flagstat aligned/${sample}.bam
```
- Mapped reads >95%
- Properly paired >90%

### Step 3: BAM Processing

```bash
for sample in sample1 sample2 sample3; do
    # Sort by coordinate
    samtools sort -@ 8 -o aligned/${sample}.sorted.bam aligned/${sample}.bam

    # Mark duplicates (samtools method)
    samtools fixmate -m aligned/${sample}.sorted.bam - | \
        samtools sort -@ 8 - | \
        samtools markdup -@ 8 - aligned/${sample}.markdup.bam

    # Index
    samtools index aligned/${sample}.markdup.bam

    # Cleanup intermediate
    rm aligned/${sample}.bam aligned/${sample}.sorted.bam
done
```

**QC Checkpoint 3:** Check duplication rate
```bash
samtools flagstat aligned/${sample}.markdup.bam | grep "duplicates"
```
- WGS: <30% duplicates
- Exome/targeted: <50% duplicates

### Step 4: Variant Calling with bcftools

```bash
# Single sample calling
bcftools mpileup -Ou -f reference.fa aligned/sample1.markdup.bam | \
    bcftools call -mv -Oz -o variants/sample1.vcf.gz

# Multi-sample calling (joint calling)
bcftools mpileup -Ou -f reference.fa \
    aligned/sample1.markdup.bam \
    aligned/sample2.markdup.bam \
    aligned/sample3.markdup.bam | \
    bcftools call -mv -Oz -o variants/cohort.vcf.gz

bcftools index variants/cohort.vcf.gz
```

### Step 5: Variant Filtering

```bash
# Basic quality filter
bcftools filter -Oz \
    -e 'QUAL<20 || DP<10 || MQ<30' \
    -o variants/cohort.filtered.vcf.gz \
    variants/cohort.vcf.gz

# More stringent filter
bcftools filter -Oz \
    -e 'QUAL<30 || DP<10 || DP>200 || MQ<40 || MQB<0.1' \
    -s "LowQual" \
    -o variants/cohort.filtered.vcf.gz \
    variants/cohort.vcf.gz

# Stats
bcftools stats variants/cohort.filtered.vcf.gz > variants/vcf_stats.txt
```

**QC Checkpoint 4:** Check variant stats
- Ti/Tv ratio ~2.1 for whole genome
- Ti/Tv ratio ~2.8-3.0 for exome
- >95% overlap with dbSNP for known sites

## Alternative Path: BWA + GATK HaplotypeCaller

### Step 4 Alternative: GATK Variant Calling

```bash
# Create sequence dictionary (once)
gatk CreateSequenceDictionary -R reference.fa

# Index reference (once)
samtools faidx reference.fa

# Base Quality Score Recalibration (BQSR)
gatk BaseRecalibrator \
    -R reference.fa \
    -I aligned/sample1.markdup.bam \
    --known-sites dbsnp.vcf.gz \
    -O recal_data.table

gatk ApplyBQSR \
    -R reference.fa \
    -I aligned/sample1.markdup.bam \
    --bqsr-recal-file recal_data.table \
    -O aligned/sample1.recal.bam

# HaplotypeCaller (per-sample GVCF mode)
gatk HaplotypeCaller \
    -R reference.fa \
    -I aligned/sample1.recal.bam \
    -O variants/sample1.g.vcf.gz \
    -ERC GVCF

# Joint genotyping (for multiple samples)
gatk GenomicsDBImport \
    -V variants/sample1.g.vcf.gz \
    -V variants/sample2.g.vcf.gz \
    -V variants/sample3.g.vcf.gz \
    --genomicsdb-workspace-path genomicsdb \
    -L intervals.bed

gatk GenotypeGVCFs \
    -R reference.fa \
    -V gendb://genomicsdb \
    -O variants/cohort.vcf.gz
```

### Step 5 Alternative: GATK Variant Filtering

```bash
# Hard filtering (for small cohorts)
gatk VariantFiltration \
    -R reference.fa \
    -V variants/cohort.vcf.gz \
    --filter-expression "QD < 2.0" --filter-name "LowQD" \
    --filter-expression "FS > 60.0" --filter-name "HighFS" \
    --filter-expression "MQ < 40.0" --filter-name "LowMQ" \
    --filter-expression "MQRankSum < -12.5" --filter-name "LowMQRS" \
    --filter-expression "ReadPosRankSum < -8.0" --filter-name "LowRPRS" \
    -O variants/cohort.filtered.vcf.gz

# VQSR (for large cohorts >30 samples)
gatk VariantRecalibrator \
    -R reference.fa \
    -V variants/cohort.vcf.gz \
    --resource:hapmap,known=false,training=true,truth=true,prior=15.0 hapmap.vcf.gz \
    --resource:omni,known=false,training=true,truth=false,prior=12.0 omni.vcf.gz \
    --resource:1000G,known=false,training=true,truth=false,prior=10.0 1000G.vcf.gz \
    --resource:dbsnp,known=true,training=false,truth=false,prior=2.0 dbsnp.vcf.gz \
    -an QD -an MQ -an MQRankSum -an ReadPosRankSum -an FS -an SOR \
    -mode SNP \
    -O cohort.snp.recal \
    --tranches-file cohort.snp.tranches

gatk ApplyVQSR \
    -R reference.fa \
    -V variants/cohort.vcf.gz \
    -O variants/cohort.vqsr.vcf.gz \
    --recal-file cohort.snp.recal \
    --tranches-file cohort.snp.tranches \
    -mode SNP \
    --truth-sensitivity-filter-level 99.5
```

## Parameter Recommendations

| Step | Parameter | WGS | Exome/Targeted |
|------|-----------|-----|----------------|
| bwa-mem2 | -t | 8-16 | 8 |
| samtools markdup | - | Required | Required |
| bcftools mpileup | -d | 250 (default) | 1000 |
| bcftools mpileup | -q | 20 | 20 |
| bcftools filter | QUAL | >20 | >30 |
| bcftools filter | DP | >10, <2x mean | >20 |
| GATK | intervals | - | Target BED |

## Choosing Between bcftools and GATK

| Criterion | bcftools | GATK |
|-----------|----------|------|
| Speed | Faster | Slower |
| Memory | Lower | Higher |
| Best for | Germline SNPs/indels | Germline, somatic |
| Cohort size | Any | Scales well |
| BQSR | Not supported | Recommended |
| VQSR | Not supported | For large cohorts |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Low mapping rate | Wrong reference, contamination | Verify reference genome version |
| High duplication | PCR over-amplification, low input | Check library prep, may need more input DNA |
| Low Ti/Tv | False positives | Increase quality filters |
| Missing variants | Too stringent filters, low depth | Relax filters, check coverage |
| Many indels at homopolymers | Sequencing errors | Filter homopolymer regions |

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

# Configuration
THREADS=8
REF="reference.fa"
SAMPLES="sample1 sample2 sample3"
OUTDIR="results"

mkdir -p ${OUTDIR}/{trimmed,aligned,variants,qc}

echo "=== Step 1: QC with fastp ==="
for sample in $SAMPLES; do
    fastp -i ${sample}_R1.fastq.gz -I ${sample}_R2.fastq.gz \
        -o ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        -O ${OUTDIR}/trimmed/${sample}_R2.fq.gz \
        --detect_adapter_for_pe \
        --html ${OUTDIR}/qc/${sample}_fastp.html \
        -w ${THREADS}
done

echo "=== Step 2: Alignment with bwa-mem2 ==="
for sample in $SAMPLES; do
    bwa-mem2 mem -t ${THREADS} \
        -R "@RG\tID:${sample}\tSM:${sample}\tPL:ILLUMINA" \
        ${REF} \
        ${OUTDIR}/trimmed/${sample}_R1.fq.gz \
        ${OUTDIR}/trimmed/${sample}_R2.fq.gz | \
    samtools view -@ ${THREADS} -bS - > ${OUTDIR}/aligned/${sample}.bam
done

echo "=== Step 3: BAM Processing ==="
for sample in $SAMPLES; do
    samtools fixmate -@ ${THREADS} -m ${OUTDIR}/aligned/${sample}.bam - | \
    samtools sort -@ ${THREADS} - | \
    samtools markdup -@ ${THREADS} - ${OUTDIR}/aligned/${sample}.markdup.bam
    samtools index ${OUTDIR}/aligned/${sample}.markdup.bam
    rm ${OUTDIR}/aligned/${sample}.bam
done

echo "=== Step 4: Joint Variant Calling ==="
bcftools mpileup -Ou -f ${REF} ${OUTDIR}/aligned/*.markdup.bam | \
    bcftools call -mv -Oz -o ${OUTDIR}/variants/cohort.vcf.gz
bcftools index ${OUTDIR}/variants/cohort.vcf.gz

echo "=== Step 5: Filtering ==="
bcftools filter -Oz \
    -e 'QUAL<20 || DP<10 || MQ<30' \
    -o ${OUTDIR}/variants/cohort.filtered.vcf.gz \
    ${OUTDIR}/variants/cohort.vcf.gz
bcftools index ${OUTDIR}/variants/cohort.filtered.vcf.gz

echo "=== Stats ==="
bcftools stats ${OUTDIR}/variants/cohort.filtered.vcf.gz > ${OUTDIR}/variants/stats.txt

echo "=== Pipeline Complete ==="
echo "Filtered VCF: ${OUTDIR}/variants/cohort.filtered.vcf.gz"
```

## Related Skills

- read-qc/fastp-workflow - Detailed QC options
- read-alignment/bwa-alignment - BWA-MEM2 parameters
- alignment-files/duplicate-handling - Duplicate marking details
- variant-calling/variant-calling - bcftools calling options
- variant-calling/gatk-variant-calling - GATK HaplotypeCaller details
- variant-calling/filtering-best-practices - Advanced filtering strategies
- variant-calling/variant-annotation - Annotate variants with VEP
