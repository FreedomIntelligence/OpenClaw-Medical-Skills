# bio-phasing-imputation-imputation-qc

> Quality control of phasing and imputation results. Filter by INFO scores, assess accuracy, and prepare imputed data for downstream analysis. Use when filtering low-quality imputed variants or validating imputation accuracy before GWAS.

**Available tools:** Read, Bash

# Imputation QC

## Extract INFO Scores

```bash
# Beagle DR2 (dosage R-squared)
bcftools query -f '%CHROM\t%POS\t%ID\t%REF\t%ALT\t%INFO/DR2\t%INFO/AF\n' \
    imputed.vcf.gz > info_scores.txt

# Minimac R2
bcftools query -f '%CHROM\t%POS\t%ID\t%REF\t%ALT\t%INFO/R2\t%INFO/MAF\n' \
    imputed.vcf.gz > info_scores.txt

# IMPUTE info
bcftools query -f '%CHROM\t%POS\t%ID\t%INFO\n' imputed.vcf.gz > info_scores.txt
```

## Filter by INFO Score

```bash
# Standard threshold for GWAS
bcftools view -i 'INFO/DR2 > 0.3' imputed.vcf.gz -Oz -o imputed_r2_03.vcf.gz

# Strict threshold for fine-mapping
bcftools view -i 'INFO/DR2 > 0.8' imputed.vcf.gz -Oz -o imputed_r2_08.vcf.gz

# Combined filtering
bcftools view -i 'INFO/DR2 > 0.3 && INFO/AF > 0.01 && INFO/AF < 0.99' \
    imputed.vcf.gz -Oz -o imputed_filtered.vcf.gz
```

## INFO Score Distribution

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load INFO scores
info = pd.read_csv('info_scores.txt', sep='\t',
    names=['CHR', 'POS', 'ID', 'REF', 'ALT', 'R2', 'AF'])

# Distribution plot
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Overall distribution
axes[0].hist(info['R2'], bins=50, edgecolor='black')
axes[0].axvline(0.3, color='red', linestyle='--', label='Threshold 0.3')
axes[0].set_xlabel('INFO Score (R2)')
axes[0].set_ylabel('Count')
axes[0].set_title('INFO Score Distribution')
axes[0].legend()

# R2 by MAF
info['MAF'] = info['AF'].apply(lambda x: min(x, 1-x))
info['MAF_bin'] = pd.cut(info['MAF'], bins=[0, 0.01, 0.05, 0.1, 0.5])
info.boxplot(column='R2', by='MAF_bin', ax=axes[1])
axes[1].set_xlabel('MAF Bin')
axes[1].set_ylabel('INFO Score')
axes[1].set_title('INFO by MAF')

# Scatter
axes[2].scatter(info['MAF'], info['R2'], alpha=0.1, s=1)
axes[2].set_xlabel('Minor Allele Frequency')
axes[2].set_ylabel('INFO Score')
axes[2].set_title('INFO vs MAF')

plt.tight_layout()
plt.savefig('imputation_qc.png', dpi=150)
```

## Summarize Imputation Quality

```bash
# Count variants by quality
bcftools query -f '%INFO/DR2\n' imputed.vcf.gz | \
    awk '{
        if ($1 >= 0.8) high++;
        else if ($1 >= 0.3) med++;
        else low++
    } END {
        print "High quality (R2>=0.8):", high
        print "Medium quality (0.3<=R2<0.8):", med
        print "Low quality (R2<0.3):", low
    }'

# Variants passing filter
echo "Total variants: $(bcftools view -H imputed.vcf.gz | wc -l)"
echo "Passing R2>0.3: $(bcftools view -i 'INFO/DR2>0.3' imputed.vcf.gz -H | wc -l)"
```

## Check Concordance with Typed Variants

```bash
# Extract typed variants from imputed file
bcftools view -i 'INFO/TYPED=1' imputed.vcf.gz -Oz -o typed.vcf.gz

# Compare imputed vs original genotypes
bcftools gtcheck -g original.vcf.gz typed.vcf.gz > concordance.txt

# Parse concordance
grep "^CN" concordance.txt
```

## Python: Comprehensive QC Report

```python
import pandas as pd
import numpy as np

def imputation_qc_report(info_file, output_prefix):
    '''Generate comprehensive imputation QC report.'''
    info = pd.read_csv(info_file, sep='\t',
        names=['CHR', 'POS', 'ID', 'REF', 'ALT', 'R2', 'AF'])

    # Calculate MAF
    info['MAF'] = info['AF'].apply(lambda x: min(x, 1-x))

    # Basic statistics
    stats = {
        'total_variants': len(info),
        'mean_r2': info['R2'].mean(),
        'median_r2': info['R2'].median(),
        'variants_r2_03': (info['R2'] >= 0.3).sum(),
        'variants_r2_08': (info['R2'] >= 0.8).sum(),
        'pct_r2_03': 100 * (info['R2'] >= 0.3).mean(),
        'pct_r2_08': 100 * (info['R2'] >= 0.8).mean(),
    }

    # By MAF bin
    maf_bins = [(0, 0.001), (0.001, 0.01), (0.01, 0.05), (0.05, 0.5)]
    for low, high in maf_bins:
        mask = (info['MAF'] >= low) & (info['MAF'] < high)
        stats[f'mean_r2_maf_{low}_{high}'] = info.loc[mask, 'R2'].mean()
        stats[f'n_variants_maf_{low}_{high}'] = mask.sum()

    # By chromosome
    chr_stats = info.groupby('CHR').agg({
        'R2': ['mean', 'count'],
        'MAF': 'mean'
    }).round(3)

    # Write reports
    with open(f'{output_prefix}_summary.txt', 'w') as f:
        for k, v in stats.items():
            f.write(f'{k}: {v}\n')

    chr_stats.to_csv(f'{output_prefix}_by_chrom.txt', sep='\t')

    return stats, chr_stats

stats, chr_stats = imputation_qc_report('info_scores.txt', 'imputation_qc')
```

## Compare Multiple Imputation Runs

```python
def compare_imputations(vcf1, vcf2, output):
    '''Compare INFO scores between two imputation runs.'''
    import subprocess

    # Extract INFO from both
    cmd1 = f"bcftools query -f '%CHROM:%POS\t%INFO/DR2\n' {vcf1}"
    cmd2 = f"bcftools query -f '%CHROM:%POS\t%INFO/DR2\n' {vcf2}"

    info1 = pd.read_csv(subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE).stdout,
        sep='\t', names=['ID', 'R2_1'])
    info2 = pd.read_csv(subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE).stdout,
        sep='\t', names=['ID', 'R2_2'])

    merged = info1.merge(info2, on='ID')
    merged['R2_diff'] = merged['R2_1'] - merged['R2_2']

    # Correlation
    corr = merged['R2_1'].corr(merged['R2_2'])
    print(f'Correlation between R2 scores: {corr:.4f}')

    return merged
```

## Hardy-Weinberg Filter

```bash
# Calculate HWE p-values (PLINK2)
plink2 --vcf imputed.vcf.gz \
    --hardy \
    --out hwe_check

# Filter extreme HWE deviations
plink2 --vcf imputed.vcf.gz \
    --hwe 1e-6 \
    --make-pgen \
    --out imputed_hwe_filtered
```

## Final QC Pipeline

```bash
#!/bin/bash
# Complete post-imputation QC

INPUT=$1
OUTPUT=$2

# 1. Filter by INFO score
bcftools view -i 'INFO/DR2 > 0.3' $INPUT -Oz -o ${OUTPUT}_r2.vcf.gz

# 2. Filter by MAF
bcftools view -i 'INFO/AF > 0.01 && INFO/AF < 0.99' \
    ${OUTPUT}_r2.vcf.gz -Oz -o ${OUTPUT}_maf.vcf.gz

# 3. Remove duplicates
bcftools norm -d all ${OUTPUT}_maf.vcf.gz -Oz -o ${OUTPUT}_nodup.vcf.gz

# 4. Index
bcftools index ${OUTPUT}_nodup.vcf.gz

# 5. Final stats
echo "Input variants: $(bcftools view -H $INPUT | wc -l)"
echo "After R2 filter: $(bcftools view -H ${OUTPUT}_r2.vcf.gz | wc -l)"
echo "After MAF filter: $(bcftools view -H ${OUTPUT}_maf.vcf.gz | wc -l)"
echo "Final variants: $(bcftools view -H ${OUTPUT}_nodup.vcf.gz | wc -l)"
```

## Quality Thresholds by Application

| Application | R2 Threshold | MAF Threshold | Notes |
|-------------|--------------|---------------|-------|
| GWAS discovery | 0.3 | 0.01 | Standard |
| GWAS replication | 0.5 | 0.01 | More stringent |
| Fine-mapping | 0.8 | 0.001 | High accuracy needed |
| Polygenic scores | 0.9 | 0.01 | Very high accuracy |
| Meta-analysis | 0.5 | Study-specific | Match across studies |

## Related Skills

- phasing-imputation/genotype-imputation - Generate imputed data
- variant-calling/filtering-best-practices - VCF filtering operations
- population-genetics/association-testing - GWAS with imputed data
