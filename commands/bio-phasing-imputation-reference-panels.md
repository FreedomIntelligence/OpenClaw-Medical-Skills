# bio-phasing-imputation-reference-panels

> Download, prepare, and manage reference panels for phasing and imputation. Covers 1000 Genomes, HRC, and TOPMed panels. Use when setting up imputation infrastructure or selecting appropriate reference panels for target populations.

**Available tools:** Read, Bash

# Reference Panels

## 1000 Genomes Phase 3 (GRCh38)

```bash
# Download from IGSR
BASE_URL="http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20201028_3202_phased"

for chr in {1..22}; do
    wget ${BASE_URL}/CCDG_14151_B01_GRM_WGS_2020-08-05_chr${chr}.filtered.shapeit2-duohmm-phased.vcf.gz
    wget ${BASE_URL}/CCDG_14151_B01_GRM_WGS_2020-08-05_chr${chr}.filtered.shapeit2-duohmm-phased.vcf.gz.tbi
done
```

## Subset by Population

```bash
# Download sample info
wget http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/1000G_2504_high_coverage.sequence.index

# Create population sample lists
grep "EUR" samples.txt | cut -f1 > european_samples.txt
grep "AFR" samples.txt | cut -f1 > african_samples.txt
grep "EAS" samples.txt | cut -f1 > east_asian_samples.txt

# Subset reference to specific population
bcftools view -S european_samples.txt \
    1000GP.chr22.vcf.gz \
    -Oz -o 1000GP_EUR.chr22.vcf.gz
```

## Convert to Beagle Format

```bash
# Beagle uses VCF directly, but ensure proper format
bcftools view -m2 -M2 -v snps reference.vcf.gz | \
    bcftools annotate --set-id '%CHROM:%POS:%REF:%ALT' | \
    bgzip > reference_beagle.vcf.gz
bcftools index reference_beagle.vcf.gz
```

## Convert to IMPUTE5 Format

```bash
# IMPUTE5 uses its own format
imp5Converter \
    --h reference.vcf.gz \
    --r chr22 \
    --o reference.chr22.imp5
```

## HRC Reference Panel

```bash
# HRC requires registration at EGA
# After access granted:

# Download from EGA using pyega3
pip install pyega3
pyega3 -cf credentials.json fetch EGAD00001002729

# HRC contains 32,470 samples (mostly European)
```

## TOPMed Reference Panel

```bash
# TOPMed available through imputation servers
# Or download from dbGaP with appropriate access

# Use via Michigan Imputation Server:
# 1. Upload study VCF
# 2. Select "TOPMed r2" as reference
# 3. Download imputed results
```

## Genetic Maps

```bash
# Beagle format (GRCh38) - from Browning lab
wget https://faculty.washington.edu/browning/beagle/genetic_maps/plink.GRCh38.map.zip
unzip plink.GRCh38.map.zip -d genetic_maps/

# SHAPEIT5 format (recommended for SHAPEIT5)
wget https://github.com/odelaneau/shapeit5/raw/main/maps/genetic_maps.b38.tar.gz
tar xzf genetic_maps.b38.tar.gz
```

## Check Reference Panel

```bash
# Basic stats
bcftools stats reference.vcf.gz | head -50

# Sample count
bcftools query -l reference.vcf.gz | wc -l

# Variant count
bcftools view -H reference.vcf.gz | wc -l

# Check chromosomes
bcftools index -s reference.vcf.gz
```

## Lift Over Reference Panel

```bash
# GRCh37 to GRCh38
# Using Picard
java -jar picard.jar LiftoverVcf \
    I=reference_hg19.vcf.gz \
    O=reference_hg38.vcf.gz \
    CHAIN=hg19ToHg38.over.chain.gz \
    REJECT=rejected.vcf \
    R=hg38.fa

# Or using CrossMap
CrossMap.py vcf hg19ToHg38.chain reference_hg19.vcf hg38.fa reference_hg38.vcf
```

## Align Study to Reference

```bash
# Check strand concordance
bcftools +fixref study.vcf.gz -Oz -o study_fixed.vcf.gz -- \
    -f reference.fa \
    -i reference_panel.vcf.gz \
    -m flip

# Statistics on fixes
bcftools +fixref study.vcf.gz -- -f reference.fa -m stats
```

## Filter Reference Panel

```bash
# Remove singletons (appear in only 1 sample)
bcftools view -c 2 reference.vcf.gz -Oz -o reference_no_singletons.vcf.gz

# Filter by MAF
bcftools view -q 0.001:minor reference.vcf.gz -Oz -o reference_maf001.vcf.gz

# Remove indels (SNPs only)
bcftools view -v snps reference.vcf.gz -Oz -o reference_snps.vcf.gz
```

## Merge Custom Panel with 1000G

```bash
# If you have additional reference samples
bcftools merge \
    1000GP.chr22.vcf.gz \
    custom_reference.chr22.vcf.gz \
    -Oz -o combined_reference.chr22.vcf.gz

# Ensure matching variants first
bcftools isec -n=2 \
    1000GP.chr22.vcf.gz \
    custom_reference.chr22.vcf.gz \
    -p isec_output
```

## Reference Panel Comparison

| Panel | Samples | Variants | Populations |
|-------|---------|----------|-------------|
| 1000G Phase 3 | 2,504 | 88M | 26 global |
| HRC r1.1 | 32,470 | 40M | European-heavy |
| TOPMed r2 | 97,256 | 308M | 60% European, diverse |
| UK10K | 3,781 | 42M | British |

## Related Skills

- phasing-imputation/haplotype-phasing - Use panels for phasing
- phasing-imputation/genotype-imputation - Use panels for imputation
- variant-calling/vcf-manipulation - VCF file operations
