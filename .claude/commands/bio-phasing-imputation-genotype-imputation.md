# bio-phasing-imputation-genotype-imputation

> Impute missing genotypes using reference panels with Beagle or Minimac4. Use when increasing variant density for GWAS, harmonizing data across genotyping platforms, or inferring variants not directly typed in array data.

**Available tools:** Read, Bash

# Genotype Imputation

## Beagle Imputation

```bash
# Basic imputation
java -jar beagle.jar \
    gt=study.vcf.gz \
    ref=reference_panel.vcf.gz \
    map=genetic_map.txt \
    out=imputed

# Output: imputed.vcf.gz with imputed genotypes
```

## Beagle with Options

```bash
java -Xmx32g -jar beagle.jar \
    gt=study.vcf.gz \
    ref=reference_panel.vcf.gz \
    map=genetic_map.txt \
    out=imputed \
    nthreads=8 \
    gp=true \              # Output genotype probabilities
    ap=true \              # Output allele probabilities
    impute=true \          # Perform imputation (default)
    ne=20000               # Effective population size
```

## Impute Per Chromosome

```bash
for chr in {1..22}; do
    java -Xmx32g -jar beagle.jar \
        gt=study.chr${chr}.vcf.gz \
        ref=ref.chr${chr}.vcf.gz \
        map=genetic_maps/plink.chr${chr}.GRCh38.map \
        out=imputed.chr${chr} \
        gp=true \
        nthreads=8
done

# Concatenate
bcftools concat imputed.chr*.vcf.gz -Oz -o imputed.all.vcf.gz
bcftools index imputed.all.vcf.gz
```

## IMPUTE5 (Alternative)

```bash
# Newer IMPUTE software
impute5 \
    --h reference.bcf \
    --m genetic_map.txt \
    --g study.vcf.gz \
    --r chr22 \
    --o imputed.chr22.vcf.gz \
    --threads 8
```

## Minimac4 (Michigan Imputation Server)

```bash
# Often used via web server, but can run locally
minimac4 \
    --refHaps reference.m3vcf.gz \
    --haps study.vcf.gz \
    --prefix imputed \
    --format GT,DS,GP \
    --cpus 8
```

## Input Preparation

```bash
# 1. Align to reference (strand, allele order)
bcftools +fixref study.vcf.gz -Oz -o fixed.vcf.gz -- \
    -f reference.fa -m flip

# 2. Filter to sites in reference
bcftools isec -n=2 -w1 fixed.vcf.gz reference_sites.vcf.gz \
    -Oz -o study_overlap.vcf.gz

# 3. Phase first (if not already phased)
java -jar beagle.jar gt=study_overlap.vcf.gz out=phased

# 4. Then impute
java -jar beagle.jar gt=phased.vcf.gz ref=reference.vcf.gz out=imputed
```

## Extract Imputation Quality

```bash
# INFO/DR2 or INFO/R2 contains imputation quality
bcftools query -f '%CHROM\t%POS\t%ID\t%INFO/DR2\n' imputed.vcf.gz > info_scores.txt

# Filter by quality
bcftools view -i 'INFO/DR2 > 0.3' imputed.vcf.gz -Oz -o imputed_filtered.vcf.gz
```

## Output Formats

| Format | Field | Description |
|--------|-------|-------------|
| GT | 0\|0, 0\|1, 1\|1 | Hard-called genotype |
| DS | 0.0-2.0 | Dosage (expected ALT allele count) |
| GP | 0.0-1.0,0.0-1.0,0.0-1.0 | Genotype probabilities (AA,AB,BB) |
| DR2/R2 | 0.0-1.0 | Imputation quality score |

## Using Dosages for GWAS

```python
import pandas as pd

# Extract dosages
# bcftools query -f '%CHROM\t%POS\t%ID[\t%DS]\n' imputed.vcf.gz > dosages.txt

dosages = pd.read_csv('dosages.txt', sep='\t')

# Dosage-based association (treats uncertainty)
# Use --dosage in PLINK2 or similar
```

```bash
# PLINK2 with dosages
plink2 --vcf imputed.vcf.gz dosage=DS \
    --glm \
    --pheno phenotypes.txt \
    --out gwas_results
```

## Quality Thresholds

| Analysis | Minimum INFO/R2 |
|----------|-----------------|
| GWAS discovery | 0.3 |
| GWAS fine-mapping | 0.8 |
| Meta-analysis | 0.5 |
| Polygenic scores | 0.9 |

## Key Parameters

| Parameter | Beagle | Description |
|-----------|--------|-------------|
| gt | input VCF | Study genotypes |
| ref | reference VCF | Reference panel |
| map | genetic map | Recombination map |
| gp | true/false | Output genotype probs |
| ne | 20000 | Effective population size |
| nthreads | N | CPU threads |
| window | 40 | Window size (cM) |

## Imputation Servers

For large-scale imputation, consider web-based servers:
- **Michigan Imputation Server**: imputationserver.sph.umich.edu
- **TOPMed Imputation Server**: imputation.biodatacatalyst.nhlbi.nih.gov
- **Sanger Imputation Server**: imputation.sanger.ac.uk

```bash
# Prepare input for server
# Most require VCF.GZ per chromosome
for chr in {1..22}; do
    bcftools view -r chr${chr} study.vcf.gz -Oz -o study.chr${chr}.vcf.gz
done
```

## Related Skills

- phasing-imputation/haplotype-phasing - Pre-phasing step
- phasing-imputation/reference-panels - Reference panel setup
- phasing-imputation/imputation-qc - Quality control
- population-genetics/association-testing - GWAS with imputed data
