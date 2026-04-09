# bio-population-genetics-plink-basics

> PLINK file formats, format conversion, and quality control filtering for population genetics. Convert between VCF, BED/BIM/FAM, and PED/MAP formats, apply MAF, genotyping rate, and HWE filters using PLINK 1.9 and 2.0. Use when working with PLINK format files or running QC.

**Available tools:** Read, Bash

# PLINK Basics

File formats, conversion, and quality control filtering with PLINK 1.9 and 2.0.

## File Formats

### Binary Format (Recommended)

| File | Contents |
|------|----------|
| `.bed` | Binary genotype data |
| `.bim` | Variant information (chr, ID, cM, pos, A1, A2) |
| `.fam` | Sample information (FID, IID, father, mother, sex, pheno) |

### PLINK 2.0 Format

| File | Contents |
|------|----------|
| `.pgen` | Binary genotype data (compressed) |
| `.pvar` | Variant information |
| `.psam` | Sample information |

### Text Format (Legacy)

| File | Contents |
|------|----------|
| `.ped` | Genotypes (FID, IID, father, mother, sex, pheno, genotypes) |
| `.map` | Variant positions (chr, ID, cM, pos) |

## Format Conversion

### VCF to PLINK Binary

```bash
# PLINK 1.9
plink --vcf input.vcf.gz --make-bed --out output

# PLINK 2.0
plink2 --vcf input.vcf.gz --make-bed --out output

# With sample ID handling
plink2 --vcf input.vcf.gz --double-id --make-bed --out output
```

### PLINK Binary to VCF

```bash
# PLINK 1.9
plink --bfile input --recode vcf --out output

# PLINK 2.0
plink2 --bfile input --export vcf --out output

# Compressed VCF
plink2 --bfile input --export vcf bgz --out output
```

### PED/MAP to Binary (PLINK 1.9 Only)

```bash
# PLINK 1.9 (PLINK 2.0 doesn't support .ped/.map directly)
plink --file input --make-bed --out output
```

### Binary to PED/MAP

```bash
# PLINK 1.9
plink --bfile input --recode --out output

# PLINK 2.0
plink2 --bfile input --export ped --out output
```

### PLINK 1.9 to 2.0 Format

```bash
# Convert to PGEN format
plink2 --bfile input --make-pgen --out output

# Convert back to BED
plink2 --pfile input --make-bed --out output
```

## Quality Control Filtering

### MAF Filter (Minor Allele Frequency)

```bash
# Remove variants with MAF < 0.01
plink --bfile input --maf 0.01 --make-bed --out output

# PLINK 2.0
plink2 --bfile input --maf 0.01 --make-bed --out output

# Remove rare variants (MAF < 0.05)
plink2 --bfile input --maf 0.05 --make-bed --out output
```

### Genotyping Rate Filters

```bash
# Per-variant missing rate (remove if >5% missing)
plink2 --bfile input --geno 0.05 --make-bed --out output

# Per-sample missing rate (remove if >5% missing)
plink2 --bfile input --mind 0.05 --make-bed --out output
```

### Hardy-Weinberg Equilibrium Filter

```bash
# Remove variants with HWE p-value < 1e-6
plink2 --bfile input --hwe 1e-6 --make-bed --out output

# Different threshold for cases vs controls
plink2 --bfile input --hwe 1e-6 --hwe-all --make-bed --out output
```

### Combined QC Pipeline

```bash
# Standard QC filtering
plink2 --bfile input \
    --maf 0.01 \
    --geno 0.05 \
    --mind 0.05 \
    --hwe 1e-6 \
    --make-bed --out qc_filtered
```

## Sample and Variant Selection

### Keep/Remove Samples

```bash
# Keep specific samples (samples.txt: FID IID per line)
plink2 --bfile input --keep samples.txt --make-bed --out output

# Remove specific samples
plink2 --bfile input --remove samples.txt --make-bed --out output

# Keep single sample
plink2 --bfile input --keep-fam sample_id --make-bed --out output
```

### Extract/Exclude Variants

```bash
# Extract specific variants (variants.txt: variant IDs)
plink2 --bfile input --extract variants.txt --make-bed --out output

# Exclude specific variants
plink2 --bfile input --exclude variants.txt --make-bed --out output

# Extract by range
plink2 --bfile input --extract range chr1:1000000-2000000 --make-bed --out output
```

### Chromosome Selection

```bash
# Single chromosome
plink2 --bfile input --chr 22 --make-bed --out chr22

# Multiple chromosomes
plink2 --bfile input --chr 1-22 --make-bed --out autosomes

# Exclude chromosome
plink2 --bfile input --not-chr 23,24,25,26 --make-bed --out autosomes
```

## Allele Frequency

```bash
# PLINK 1.9 (MAF-based)
plink --bfile input --freq --out output

# PLINK 2.0 (ALT allele frequency - not MAF!)
plink2 --bfile input --freq --out output

# PLINK 2.0 with MAF
plink2 --bfile input --freq cols=+mac,+mafreq --out output
```

## Missing Data Statistics

```bash
# Per-sample and per-variant missing rates
plink2 --bfile input --missing --out output

# Output files:
# output.smiss - sample missing rates
# output.vmiss - variant missing rates
```

## Sex Check

Verify reported sex matches X chromosome heterozygosity.

```bash
# PLINK 1.9
plink --bfile input --check-sex --out sex_check

# PLINK 2.0
plink2 --bfile input --split-par hg38 --check-sex --out sex_check
```

### Interpret Results

```python
import pandas as pd

sex = pd.read_csv('sex_check.sexcheck', sep='\s+')

problems = sex[sex['STATUS'] == 'PROBLEM']
print(f'Sex mismatches: {len(problems)}')

# F statistic: <0.2 = female, >0.8 = male, between = ambiguous
# PEDSEX: reported sex (1=male, 2=female, 0=unknown)
# SNPSEX: inferred sex (1=male, 2=female, 0=undetermined)
```

### Update or Remove

```bash
# Update sex from check results
plink2 --bfile input --update-sex sex_check.sexcheck col-num=4 --make-bed --out updated

# Remove sex mismatches
awk '$5 == "PROBLEM" {print $1, $2}' sex_check.sexcheck > sex_problems.txt
plink2 --bfile input --remove sex_problems.txt --make-bed --out output
```

## Sample Information

### Update Phenotypes

```bash
# phenotypes.txt: FID IID pheno (1=control, 2=case, -9=missing)
plink2 --bfile input --pheno phenotypes.txt --make-bed --out output

# Quantitative phenotype
plink2 --bfile input --pheno phenotypes.txt --make-bed --out output
```

### Update Sex

```bash
# sex.txt: FID IID sex (1=male, 2=female, 0=unknown)
plink2 --bfile input --update-sex sex.txt --make-bed --out output
```

### Update Sample IDs

```bash
# ids.txt: old_FID old_IID new_FID new_IID
plink2 --bfile input --update-ids ids.txt --make-bed --out output
```

## Merging Datasets

```bash
# Merge two datasets (PLINK 1.9)
plink --bfile data1 --bmerge data2.bed data2.bim data2.fam --make-bed --out merged

# Merge list of datasets
plink --bfile data1 --merge-list merge_list.txt --make-bed --out merged
# merge_list.txt contains: data2.bed data2.bim data2.fam (one set per line)

# Handle strand flips
plink --bfile data1 --bmerge data2 --make-bed --out merged
# If error: plink --bfile data2 --flip missnps.txt --make-bed --out data2_flipped
```

## Variant Information

### Set Variant IDs

```bash
# Set ID based on position
plink2 --bfile input --set-all-var-ids @:#:\$r:\$a --make-bed --out output
# Format: chr:pos:ref:alt
```

### Update Variant Names

```bash
# update.txt: old_id new_id
plink2 --bfile input --update-name update.txt --make-bed --out output
```

## PLINK 2.0 vs 1.9 Summary

| Feature | PLINK 2.0 | PLINK 1.9 |
|---------|-----------|-----------|
| Status | Current | Legacy |
| Command | `plink2` | `plink` |
| Format | `.pgen/.pvar/.psam` | `.bed/.bim/.fam` |
| Speed | Faster | Baseline |
| Memory | More efficient | Higher for large data |
| Export VCF | `--export vcf` | `--recode vcf` |
| Frequency output | ALT frequency | MAF |
| Missing output | `.smiss/.vmiss` | `.imiss/.lmiss` |
| PED/MAP support | No (convert via 1.9) | Yes (`--file`) |

## Related Skills

- association-testing - GWAS with filtered data
- population-structure - PCA after QC
- variant-calling/vcf-basics - VCF format before conversion
