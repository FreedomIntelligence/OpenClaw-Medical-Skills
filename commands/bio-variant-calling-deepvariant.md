# bio-variant-calling-deepvariant

> Deep learning-based variant calling with Google DeepVariant. Provides high accuracy for germline SNPs and indels from Illumina, PacBio, and ONT data. Use when calling variants with DeepVariant deep learning caller.

## Version Compatibility

Reference examples tested with: GATK 4.5+, bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# DeepVariant Variant Calling

## Installation

**Goal:** Install DeepVariant via Docker or Singularity container.

**Approach:** Pull the pre-built container image matching the target platform (CPU or GPU).

### Docker (Recommended)

```bash
docker pull google/deepvariant:1.6.1

# Or with GPU support
docker pull google/deepvariant:1.6.1-gpu
```

### Singularity

```bash
singularity pull docker://google/deepvariant:1.6.1
```

## Basic Usage

**Goal:** Call germline variants from aligned reads using DeepVariant's deep learning model.

**Approach:** Run the all-in-one `run_deepvariant` wrapper specifying model type, reference, reads, and output paths.

**"Call variants with DeepVariant"** → Convert aligned read pileups into image tensors, classify with a CNN, and output genotyped VCF.

### One-Step Run (run_deepvariant)

```bash
docker run -v "${PWD}:/input" -v "${PWD}/output:/output" \
    google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/run_deepvariant \
    --model_type=WGS \
    --ref=/input/reference.fa \
    --reads=/input/sample.bam \
    --output_vcf=/output/sample.vcf.gz \
    --output_gvcf=/output/sample.g.vcf.gz \
    --num_shards=16
```

### Model Types

| Model | Data Type | Use Case |
|-------|-----------|----------|
| `WGS` | Illumina WGS | Whole genome sequencing |
| `WES` | Illumina WES | Whole exome/targeted |
| `PACBIO` | PacBio HiFi | Long-read HiFi |
| `ONT_R104` | ONT R10.4 | Oxford Nanopore |
| `HYBRID_PACBIO_ILLUMINA` | Mixed | Hybrid assemblies |

## Step-by-Step Workflow

**Goal:** Run DeepVariant in three explicit stages for more control over intermediate outputs.

**Approach:** Generate pileup image tensors (make_examples), classify with the CNN (call_variants), then merge and genotype (postprocess_variants).

For more control, run each step separately:

### Step 1: Make Examples

```bash
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/make_examples \
    --mode calling \
    --ref /data/reference.fa \
    --reads /data/sample.bam \
    --examples /data/examples.tfrecord.gz \
    --gvcf /data/gvcf.tfrecord.gz
```

### Step 2: Call Variants

```bash
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/call_variants \
    --outfile /data/call_variants.tfrecord.gz \
    --examples /data/examples.tfrecord.gz \
    --checkpoint /opt/models/wgs/model.ckpt
```

### Step 3: Postprocess Variants

```bash
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/postprocess_variants \
    --ref /data/reference.fa \
    --infile /data/call_variants.tfrecord.gz \
    --outfile /data/output.vcf.gz \
    --gvcf_outfile /data/output.g.vcf.gz \
    --nonvariant_site_tfrecord_path /data/gvcf.tfrecord.gz
```

## GPU Acceleration

**Goal:** Speed up DeepVariant inference using GPU hardware.

**Approach:** Use the GPU-enabled container image with Docker `--gpus` flag.

```bash
docker run --gpus all -v "${PWD}:/data" \
    google/deepvariant:1.6.1-gpu \
    /opt/deepvariant/bin/run_deepvariant \
    --model_type=WGS \
    --ref=/data/reference.fa \
    --reads=/data/sample.bam \
    --output_vcf=/data/output.vcf.gz \
    --num_shards=16
```

## PacBio HiFi Calling

**Goal:** Call variants from PacBio HiFi long reads.

**Approach:** Use the PACBIO model type which is trained on HiFi read characteristics.

```bash
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/run_deepvariant \
    --model_type=PACBIO \
    --ref=/data/reference.fa \
    --reads=/data/hifi_aligned.bam \
    --output_vcf=/data/hifi_variants.vcf.gz \
    --num_shards=16
```

## ONT Calling

**Goal:** Call variants from Oxford Nanopore long reads.

**Approach:** Use the ONT_R104 model type trained on Nanopore R10.4 chemistry.

```bash
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/run_deepvariant \
    --model_type=ONT_R104 \
    --ref=/data/reference.fa \
    --reads=/data/ont_aligned.bam \
    --output_vcf=/data/ont_variants.vcf.gz \
    --num_shards=16
```

## Exome/Targeted Sequencing

**Goal:** Call variants from exome or targeted panel data.

**Approach:** Use WES model type with a BED file restricting calling to target regions.

```bash
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/run_deepvariant \
    --model_type=WES \
    --ref=/data/reference.fa \
    --reads=/data/exome.bam \
    --regions=/data/targets.bed \
    --output_vcf=/data/exome_variants.vcf.gz \
    --num_shards=8
```

## Joint Calling with GLnexus

**Goal:** Perform joint genotyping across a cohort from DeepVariant gVCFs.

**Approach:** Generate per-sample gVCFs, then merge and jointly genotype with GLnexus using a DeepVariant-specific config.

For multi-sample cohorts, use gVCFs with GLnexus:

```bash
# Generate gVCFs for each sample
for bam in *.bam; do
    sample=$(basename $bam .bam)
    docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
        /opt/deepvariant/bin/run_deepvariant \
        --model_type=WGS \
        --ref=/data/reference.fa \
        --reads=/data/$bam \
        --output_vcf=/data/${sample}.vcf.gz \
        --output_gvcf=/data/${sample}.g.vcf.gz \
        --num_shards=16
done

# Joint genotyping with GLnexus
docker run -v "${PWD}:/data" quay.io/mlin/glnexus:v1.4.1 \
    /usr/local/bin/glnexus_cli \
    --config DeepVariantWGS \
    /data/*.g.vcf.gz \
    | bcftools view - -Oz -o cohort.vcf.gz
```

## GLnexus Configurations

| Config | Use Case |
|--------|----------|
| `DeepVariantWGS` | Illumina WGS |
| `DeepVariantWES` | Illumina exome |
| `DeepVariant_unfiltered` | Keep all variants |

## Output Quality Metrics

**Goal:** Assess the quality of DeepVariant calls.

**Approach:** Generate summary statistics with bcftools stats and check Ti/Tv ratio as a quality indicator.

```bash
# Variant statistics
bcftools stats output.vcf.gz > stats.txt

# Filter by quality
bcftools view -i 'QUAL>20 && FMT/GQ>20' output.vcf.gz -Oz -o filtered.vcf.gz

# Ti/Tv ratio (expect ~2.0-2.1 for WGS)
bcftools stats output.vcf.gz | grep TSTV
```

## Benchmarking Against Truth Set

**Goal:** Evaluate DeepVariant accuracy against a GIAB truth set.

**Approach:** Run hap.py to compute precision, recall, and F1 for SNPs and indels.

```bash
# Using hap.py for GIAB benchmarking
docker run -v "${PWD}:/data" jmcdani20/hap.py:latest \
    /opt/hap.py/bin/hap.py \
    /data/HG002_GRCh38_truth.vcf.gz \
    /data/deepvariant_output.vcf.gz \
    -r /data/reference.fa \
    -o /data/benchmark \
    --threads 16
```

## Complete Workflow Script

**Goal:** Run DeepVariant end-to-end with indexing and statistics in a single script.

**Approach:** Wrap run_deepvariant, bcftools index, and bcftools stats in a parameterized shell script.

```bash
#!/bin/bash
set -euo pipefail

BAM=$1
REFERENCE=$2
OUTPUT_PREFIX=$3
MODEL_TYPE=${4:-WGS}
THREADS=${5:-16}

echo "=== DeepVariant: ${MODEL_TYPE} mode ==="

docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/run_deepvariant \
    --model_type=${MODEL_TYPE} \
    --ref=/data/${REFERENCE} \
    --reads=/data/${BAM} \
    --output_vcf=/data/${OUTPUT_PREFIX}.vcf.gz \
    --output_gvcf=/data/${OUTPUT_PREFIX}.g.vcf.gz \
    --intermediate_results_dir=/data/${OUTPUT_PREFIX}_tmp \
    --num_shards=${THREADS}

echo "=== Indexing ==="
bcftools index -t ${OUTPUT_PREFIX}.vcf.gz
bcftools index -t ${OUTPUT_PREFIX}.g.vcf.gz

echo "=== Statistics ==="
bcftools stats ${OUTPUT_PREFIX}.vcf.gz > ${OUTPUT_PREFIX}_stats.txt

echo "=== Complete ==="
echo "VCF: ${OUTPUT_PREFIX}.vcf.gz"
echo "gVCF: ${OUTPUT_PREFIX}.g.vcf.gz"
```

## Comparison with Other Callers

| Caller | Speed | Accuracy | Best For |
|--------|-------|----------|----------|
| DeepVariant | Moderate | Highest | Production, benchmarking |
| GATK HaplotypeCaller | Moderate | High | GATK ecosystem |
| bcftools | Fast | Good | Quick analysis |
| Clair3 | Fast | High | Long reads |

## Resource Requirements

| Data Type | Memory | CPU Time (30x WGS) |
|-----------|--------|-------------------|
| WGS | 64 GB | ~4-6 hours |
| WES | 32 GB | ~30 min |
| With GPU | 32 GB | ~1-2 hours (WGS) |

## Related Skills

- variant-calling/gatk-variant-calling - GATK alternative
- variant-calling/variant-calling - bcftools calling
- long-read-sequencing/clair3-variants - Long-read alternative
- variant-calling/filtering-best-practices - Post-calling filtering
