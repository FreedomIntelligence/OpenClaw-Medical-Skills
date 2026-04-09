# bio-variant-calling-joint-calling

> Joint genotype calling across multiple samples using GATK CombineGVCFs and GenotypeGVCFs. Essential for cohort studies, population genetics, and leveraging VQSR. Use when performing joint genotyping across multiple samples.

## Version Compatibility

Reference examples tested with: GATK 4.5+, bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Joint Calling

**"Joint genotype my cohort samples"** → Combine per-sample gVCFs into a single cohort callset with consistent genotyping across all sites, enabling VQSR and population-level analysis.
- CLI: `gatk HaplotypeCaller -ERC GVCF` → `gatk GenomicsDBImport` → `gatk GenotypeGVCFs`

## Why Joint Calling?

- **Improved sensitivity** - Leverage information across samples
- **Consistent genotyping** - Same sites called across all samples
- **VQSR eligible** - Requires cohort for machine learning filtering
- **Population analysis** - Allele frequencies across cohort

## Workflow Overview

```
Sample BAMs
    │
    ├── HaplotypeCaller (per-sample, -ERC GVCF)
    │   └── sample1.g.vcf.gz, sample2.g.vcf.gz, ...
    │
    ├── CombineGVCFs or GenomicsDBImport
    │   └── Combine into cohort database
    │
    ├── GenotypeGVCFs
    │   └── Joint genotyping
    │
    └── VQSR or Hard Filtering
        └── Final VCF
```

## Step 1: Per-Sample gVCF Generation

```bash
# Generate gVCF for each sample
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample1.bam \
    -O sample1.g.vcf.gz \
    -ERC GVCF

# With intervals (faster)
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample1.bam \
    -O sample1.g.vcf.gz \
    -ERC GVCF \
    -L intervals.bed
```

### Batch Processing

```bash
# Process all samples
for bam in *.bam; do
    sample=$(basename $bam .bam)
    gatk HaplotypeCaller \
        -R reference.fa \
        -I $bam \
        -O ${sample}.g.vcf.gz \
        -ERC GVCF &
done
wait
```

## Step 2a: CombineGVCFs (Small Cohorts)

For <100 samples:

```bash
gatk CombineGVCFs \
    -R reference.fa \
    -V sample1.g.vcf.gz \
    -V sample2.g.vcf.gz \
    -V sample3.g.vcf.gz \
    -O cohort.g.vcf.gz
```

### From Sample Map

```bash
# Create sample map file
# sample1    /path/to/sample1.g.vcf.gz
# sample2    /path/to/sample2.g.vcf.gz

ls *.g.vcf.gz | while read f; do
    echo -e "$(basename $f .g.vcf.gz)\t$f"
done > sample_map.txt

# Combine with -V for each
gatk CombineGVCFs \
    -R reference.fa \
    $(cat sample_map.txt | cut -f2 | sed 's/^/-V /') \
    -O cohort.g.vcf.gz
```

## Step 2b: GenomicsDBImport (Large Cohorts)

For >100 samples, use GenomicsDB:

```bash
# Create sample map
ls *.g.vcf.gz | while read f; do
    echo -e "$(basename $f .g.vcf.gz)\t$f"
done > sample_map.txt

# Import to GenomicsDB (per chromosome for parallelism)
gatk GenomicsDBImport \
    --sample-name-map sample_map.txt \
    --genomicsdb-workspace-path genomicsdb_chr1 \
    -L chr1 \
    --reader-threads 4

# Or all chromosomes
for chr in {1..22} X Y; do
    gatk GenomicsDBImport \
        --sample-name-map sample_map.txt \
        --genomicsdb-workspace-path genomicsdb_chr${chr} \
        -L chr${chr} &
done
wait
```

### Update GenomicsDB with New Samples

```bash
gatk GenomicsDBImport \
    --genomicsdb-update-workspace-path genomicsdb_chr1 \
    --sample-name-map new_samples.txt \
    -L chr1
```

## Step 3: GenotypeGVCFs

### From Combined gVCF

```bash
gatk GenotypeGVCFs \
    -R reference.fa \
    -V cohort.g.vcf.gz \
    -O cohort.vcf.gz
```

### From GenomicsDB

```bash
gatk GenotypeGVCFs \
    -R reference.fa \
    -V gendb://genomicsdb_chr1 \
    -O chr1.vcf.gz

# All chromosomes
for chr in {1..22} X Y; do
    gatk GenotypeGVCFs \
        -R reference.fa \
        -V gendb://genomicsdb_chr${chr} \
        -O chr${chr}.vcf.gz &
done
wait

# Merge chromosomes
bcftools concat chr{1..22}.vcf.gz chrX.vcf.gz chrY.vcf.gz \
    -Oz -o cohort.vcf.gz
```

### With Allele-Specific Annotations

```bash
gatk GenotypeGVCFs \
    -R reference.fa \
    -V gendb://genomicsdb \
    -O cohort.vcf.gz \
    -G StandardAnnotation \
    -G AS_StandardAnnotation
```

## Step 4: Filtering

### VQSR (Recommended for >30 Samples)

```bash
# SNPs
gatk VariantRecalibrator \
    -R reference.fa \
    -V cohort.vcf.gz \
    --resource:hapmap,known=false,training=true,truth=true,prior=15.0 hapmap.vcf.gz \
    --resource:omni,known=false,training=true,truth=false,prior=12.0 omni.vcf.gz \
    --resource:1000G,known=false,training=true,truth=false,prior=10.0 1000G.vcf.gz \
    --resource:dbsnp,known=true,training=false,truth=false,prior=2.0 dbsnp.vcf.gz \
    -an QD -an MQ -an MQRankSum -an ReadPosRankSum -an FS -an SOR \
    -mode SNP \
    -O snps.recal \
    --tranches-file snps.tranches

gatk ApplyVQSR \
    -R reference.fa \
    -V cohort.vcf.gz \
    --recal-file snps.recal \
    --tranches-file snps.tranches \
    -mode SNP \
    --truth-sensitivity-filter-level 99.5 \
    -O cohort.snps.vcf.gz

# Indels
gatk VariantRecalibrator \
    -R reference.fa \
    -V cohort.snps.vcf.gz \
    --resource:mills,known=false,training=true,truth=true,prior=12.0 mills.vcf.gz \
    --resource:dbsnp,known=true,training=false,truth=false,prior=2.0 dbsnp.vcf.gz \
    -an QD -an MQRankSum -an ReadPosRankSum -an FS -an SOR \
    -mode INDEL \
    -O indels.recal \
    --tranches-file indels.tranches

gatk ApplyVQSR \
    -R reference.fa \
    -V cohort.snps.vcf.gz \
    --recal-file indels.recal \
    --tranches-file indels.tranches \
    -mode INDEL \
    --truth-sensitivity-filter-level 99.0 \
    -O cohort.filtered.vcf.gz
```

### Hard Filtering (Small Cohorts)

```bash
# See filtering-best-practices skill
gatk VariantFiltration \
    -R reference.fa \
    -V cohort.vcf.gz \
    --filter-expression "QD < 2.0" --filter-name "QD2" \
    --filter-expression "FS > 60.0" --filter-name "FS60" \
    --filter-expression "MQ < 40.0" --filter-name "MQ40" \
    -O cohort.filtered.vcf.gz
```

## Complete Pipeline Script

**Goal:** Run the full joint calling workflow from BAMs to filtered cohort VCF.

**Approach:** Generate per-sample gVCFs, import into GenomicsDB, joint genotype, then index and compute statistics.

```bash
#!/bin/bash
set -euo pipefail

REFERENCE=$1
OUTPUT_DIR=$2
THREADS=16

mkdir -p $OUTPUT_DIR/{gvcfs,genomicsdb,vcfs}

echo "=== Step 1: Generate gVCFs ==="
for bam in data/*.bam; do
    sample=$(basename $bam .bam)
    gatk HaplotypeCaller \
        -R $REFERENCE \
        -I $bam \
        -O $OUTPUT_DIR/gvcfs/${sample}.g.vcf.gz \
        -ERC GVCF &

    # Limit parallelism
    while [ $(jobs -r | wc -l) -ge $THREADS ]; do sleep 1; done
done
wait

echo "=== Step 2: Create sample map ==="
ls $OUTPUT_DIR/gvcfs/*.g.vcf.gz | while read f; do
    echo -e "$(basename $f .g.vcf.gz)\t$(realpath $f)"
done > $OUTPUT_DIR/sample_map.txt

echo "=== Step 3: GenomicsDBImport ==="
gatk GenomicsDBImport \
    --sample-name-map $OUTPUT_DIR/sample_map.txt \
    --genomicsdb-workspace-path $OUTPUT_DIR/genomicsdb \
    -L intervals.bed \
    --reader-threads 4

echo "=== Step 4: Joint genotyping ==="
gatk GenotypeGVCFs \
    -R $REFERENCE \
    -V gendb://$OUTPUT_DIR/genomicsdb \
    -O $OUTPUT_DIR/vcfs/cohort.vcf.gz

echo "=== Step 5: Index ==="
bcftools index -t $OUTPUT_DIR/vcfs/cohort.vcf.gz

echo "=== Statistics ==="
bcftools stats $OUTPUT_DIR/vcfs/cohort.vcf.gz > $OUTPUT_DIR/vcfs/cohort_stats.txt

echo "=== Complete ==="
echo "Joint VCF: $OUTPUT_DIR/vcfs/cohort.vcf.gz"
```

## Tips

### Memory for Large Cohorts

```bash
# Increase Java heap
gatk --java-options "-Xmx64g" GenotypeGVCFs ...

# Batch size for GenomicsDBImport
gatk GenomicsDBImport --batch-size 50 ...
```

### Incremental Updates

```bash
# Add new samples to existing database
gatk GenomicsDBImport \
    --genomicsdb-update-workspace-path existing_db \
    --sample-name-map new_samples.txt
```

## Related Skills

- variant-calling/gatk-variant-calling - Single-sample calling
- variant-calling/filtering-best-practices - VQSR and hard filtering
- population-genetics/plink-basics - Population analysis of joint calls
- workflows/fastq-to-variants - End-to-end germline pipeline
