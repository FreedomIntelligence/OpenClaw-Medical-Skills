# bio-phasing-imputation-haplotype-phasing

> Phase genotypes into haplotypes using Beagle or SHAPEIT. Resolves which alleles are inherited together on each chromosome. Use when preparing VCF files for imputation, HLA typing, or population genetic analyses requiring phased haplotypes.

**Available tools:** Read, Bash

# Haplotype Phasing

## Beagle 5.4 Phasing (Recommended)

```bash
# Download Beagle 5.4
wget https://faculty.washington.edu/browning/beagle/beagle.22Jul22.46e.jar

# Basic phasing
java -jar beagle.22Jul22.46e.jar \
    gt=input.vcf.gz \
    out=phased

# Output: phased.vcf.gz (phased genotypes)

# With genetic map (improves accuracy)
java -jar beagle.22Jul22.46e.jar \
    gt=input.vcf.gz \
    map=plink.chr22.GRCh38.map \
    out=phased
```

## Beagle Options

```bash
java -jar beagle.22Jul22.46e.jar \
    gt=input.vcf.gz \
    out=phased \
    map=genetic_map.txt \
    nthreads=8 \
    window=40 \
    overlap=4 \
    ne=20000 \              # Effective population size
    seed=12345              # For reproducibility
```

## Phase Per Chromosome

```bash
# Process each chromosome separately
for chr in {1..22}; do
    java -Xmx16g -jar beagle.jar \
        gt=input.chr${chr}.vcf.gz \
        map=genetic_maps/plink.chr${chr}.GRCh38.map \
        out=phased.chr${chr} \
        nthreads=8
done

# Concatenate chromosomes
bcftools concat phased.chr*.vcf.gz -Oz -o phased.all.vcf.gz
bcftools index phased.all.vcf.gz
```

## SHAPEIT5 Phasing (for Large Datasets)

```bash
# Phase common variants first
shapeit5_phase_common \
    --input input.vcf.gz \
    --map genetic_map.txt \
    --output phased_common.bcf \
    --thread 8 \
    --log phased.log

# Then phase rare variants
shapeit5_phase_rare \
    --input input.vcf.gz \
    --scaffold phased_common.bcf \
    --map genetic_map.txt \
    --output phased.bcf \
    --thread 8
```

## SHAPEIT5 with Reference Panel

```bash
# Improves phasing using reference haplotypes
shapeit5_phase_common \
    --input input.vcf.gz \
    --reference reference_panel.bcf \
    --map genetic_map.txt \
    --output phased.bcf \
    --thread 8
```

## Beagle with Reference Panel

```bash
# Use reference panel for better phasing
java -jar beagle.22Jul22.46e.jar \
    gt=input.vcf.gz \
    ref=reference.vcf.gz \
    map=genetic_map.txt \
    out=phased \
    nthreads=8
```

## Input Preparation

```bash
# Filter variants before phasing
bcftools view -m2 -M2 -v snps input.vcf.gz -Oz -o biallelic_snps.vcf.gz

# Remove missing genotypes (optional)
bcftools view -g ^miss biallelic_snps.vcf.gz -Oz -o no_missing.vcf.gz

# Normalize (important!)
bcftools norm -f reference.fa -Oz -o normalized.vcf.gz input.vcf.gz
```

## Check Phasing Results

```bash
# View phased genotypes (| instead of /)
bcftools query -f '%CHROM\t%POS\t[%GT\t]\n' phased.vcf.gz | head

# Unphased: 0/1
# Phased: 0|1 or 1|0

# Count phased vs unphased
bcftools query -f '[%GT\n]' phased.vcf.gz | grep -c '|'
```

## Genetic Maps

```bash
# Download genetic maps (GRCh38)
wget https://faculty.washington.edu/browning/beagle/genetic_maps/plink.GRCh38.map.zip
unzip plink.GRCh38.map.zip

# Format: chromosome position rate(cM/Mb) genetic_position(cM)
# chr1 55550 2.981822 0.000000
```

## Key Parameters

| Parameter | Beagle | SHAPEIT5 | Description |
|-----------|--------|----------|-------------|
| Threads | nthreads | --thread | CPU threads |
| Window | window | --window | Analysis window size |
| Eff. pop size | ne | --effective-size | For LD modeling |
| Seed | seed | --seed | Random seed |

## Memory Requirements

| Dataset Size | Beagle Memory | SHAPEIT5 Memory |
|--------------|--------------|-----------------|
| 1,000 samples | 8 GB | 4 GB |
| 10,000 samples | 32 GB | 16 GB |
| 100,000 samples | 64+ GB | 32 GB |

## Phasing Accuracy Metrics

- **Switch error rate**: Rate of phase switches vs truth
- **Mismatch error rate**: Overall haplotype differences
- Measure using trio data or known haplotypes

## Related Skills

- phasing-imputation/genotype-imputation - Impute after phasing
- phasing-imputation/reference-panels - Get reference data
- variant-calling/filtering-best-practices - Prepare input VCF
- population-genetics/linkage-disequilibrium - LD analysis
