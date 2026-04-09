# bio-variant-calling-filtering-best-practices

> Comprehensive variant filtering including GATK VQSR, hard filters, bcftools expressions, and quality metric interpretation for SNPs and indels. Use when filtering variants using GATK best practices.

## Version Compatibility

Reference examples tested with: GATK 4.5+, bcftools 1.19+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Variant Filtering Best Practices

## Filter Selection Decision Tree

```
Is dataset large enough for VQSR? (>30 exomes or WGS)
├── Yes → Use VQSR (machine learning)
└── No → Use hard filters
    ├── Germline → GATK recommended thresholds
    └── Somatic → Caller-specific filters + manual review
```

## GATK Hard Filter Thresholds

**Goal:** Apply GATK-recommended annotation thresholds to separate true variants from artifacts.

**Approach:** Use VariantFiltration with per-metric filter expressions for SNPs and indels separately.

**"Filter my variants using GATK best practices"** → Apply fixed annotation thresholds (QD, FS, MQ, SOR, RankSum) to flag low-quality variants.

```bash
# SNPs
gatk VariantFiltration \
    -R reference.fa \
    -V raw_snps.vcf \
    -O filtered_snps.vcf \
    --filter-expression "QD < 2.0" --filter-name "QD2" \
    --filter-expression "FS > 60.0" --filter-name "FS60" \
    --filter-expression "MQ < 40.0" --filter-name "MQ40" \
    --filter-expression "MQRankSum < -12.5" --filter-name "MQRankSum-12.5" \
    --filter-expression "ReadPosRankSum < -8.0" --filter-name "ReadPosRankSum-8" \
    --filter-expression "SOR > 3.0" --filter-name "SOR3"

# Indels
gatk VariantFiltration \
    -R reference.fa \
    -V raw_indels.vcf \
    -O filtered_indels.vcf \
    --filter-expression "QD < 2.0" --filter-name "QD2" \
    --filter-expression "FS > 200.0" --filter-name "FS200" \
    --filter-expression "ReadPosRankSum < -20.0" --filter-name "ReadPosRankSum-20" \
    --filter-expression "SOR > 10.0" --filter-name "SOR10"
```

## Understanding Quality Metrics

| Metric | Meaning | Good Value |
|--------|---------|------------|
| QD | Quality by Depth | >2 (variant quality normalized by depth) |
| FS | Fisher Strand | <60 SNP, <200 indel (strand bias) |
| MQ | Mapping Quality | >40 (RMS mapping quality) |
| MQRankSum | MQ Rank Sum | >-12.5 (ref vs alt mapping quality) |
| ReadPosRankSum | Read Position | >-8 (position in read bias) |
| SOR | Strand Odds Ratio | <3 SNP, <10 indel (strand bias) |
| DP | Depth | Sample-specific, avoid extremes |
| GQ | Genotype Quality | >20 (confidence in genotype) |

## bcftools filter

**Goal:** Filter variants using bcftools expression syntax with soft or hard removal.

**Approach:** Use -e (exclude) or -i (include) with expressions on QUAL, INFO, and FORMAT fields; use -s for soft filtering.

### Soft vs Hard Filtering

```bash
# Hard filter (remove variants)
bcftools filter -e 'QUAL<30' input.vcf.gz -o filtered.vcf

# Soft filter (mark, don't remove)
bcftools filter -s 'LowQual' -e 'QUAL<30' input.vcf.gz -o marked.vcf
# Variants failing filter get "LowQual" in FILTER column

# Include instead of exclude
bcftools filter -i 'QUAL>=30' input.vcf.gz -o filtered.vcf
```

### Expression Syntax

| Operator | Meaning |
|----------|---------|
| `<`, `<=`, `>`, `>=` | Comparison |
| `=`, `==` | Equals |
| `!=` | Not equals |
| `&&`, `\|\|` | AND, OR |
| `!` | NOT |

### Aggregate Functions

| Function | Description |
|----------|-------------|
| `MIN(x)` | Minimum across samples |
| `MAX(x)` | Maximum across samples |
| `AVG(x)` | Average across samples |
| `SUM(x)` | Sum across samples |

### Common bcftools Filters

```bash
# Basic quality filter
bcftools filter -i 'QUAL>30 && DP>10' input.vcf -o filtered.vcf

# Complex filter with multiple metrics
bcftools filter -i 'QUAL>30 && INFO/DP>10 && INFO/DP<500 && \
    (INFO/FS<60 || INFO/FS=".") && INFO/MQ>40' input.vcf -o filtered.vcf

# Genotype-level filters
bcftools filter -i 'FMT/DP>10 && FMT/GQ>20' input.vcf -o filtered.vcf

# Remove filtered sites
bcftools view -f PASS input.vcf -o passed.vcf

# Keep only biallelic SNPs
bcftools view -m2 -M2 -v snps input.vcf -o biallelic_snps.vcf

# Check for missing values
bcftools filter -e 'QUAL="."' input.vcf.gz  # Exclude missing QUAL
bcftools filter -i 'INFO/DP!="."' input.vcf.gz  # Include only if DP exists
```

## bcftools view Filtering

**Goal:** Select variants by type, region, or sample using bcftools view.

**Approach:** Use type flags (-v/-V), region flags (-r/-R), and sample flags (-s/-S) for structured subsetting.

### Filter by Variant Type

```bash
# SNPs only
bcftools view -v snps input.vcf.gz -o snps.vcf.gz

# Indels only
bcftools view -v indels input.vcf.gz -o indels.vcf.gz

# Exclude SNPs
bcftools view -V snps input.vcf.gz -o no_snps.vcf.gz
```

### Filter by Region

```bash
bcftools view -r chr1:1000000-2000000 input.vcf.gz -o region.vcf.gz

# Multiple regions
bcftools view -r chr1:1000-2000,chr2:3000-4000 input.vcf.gz
```

### Filter by Samples

```bash
# Include samples
bcftools view -s sample1,sample2 input.vcf.gz -o subset.vcf.gz

# Exclude samples
bcftools view -s ^sample3,sample4 input.vcf.gz -o subset.vcf.gz
```

## Depth Filtering

**Goal:** Remove variants at extreme depth values that suggest mapping artifacts or duplications.

**Approach:** Calculate depth percentiles, then filter to the middle 90% of the distribution.

```bash
# Calculate depth percentiles
bcftools query -f '%DP\n' input.vcf | \
    sort -n | \
    awk '{a[NR]=$1} END {print "5th:", a[int(NR*0.05)], "95th:", a[int(NR*0.95)]}'

# Filter to middle 90% of depth distribution
bcftools filter -i 'INFO/DP>10 && INFO/DP<200' input.vcf -o depth_filtered.vcf
```

## Allele Frequency Filters

**Goal:** Filter variants by minor allele frequency and allelic balance.

**Approach:** Apply thresholds on INFO/AF for population frequency and AD ratios for heterozygote balance.

```bash
# Minor allele frequency filter (population data)
bcftools filter -i 'INFO/AF>0.01 && INFO/AF<0.99' input.vcf -o maf_filtered.vcf

# Allele balance for heterozygotes
bcftools filter -i 'GT="het" -> (AD[1]/(AD[0]+AD[1]) > 0.2 && AD[1]/(AD[0]+AD[1]) < 0.8)' \
    input.vcf -o ab_filtered.vcf
```

## Region-Based Filtering

**Goal:** Include or exclude variants based on genomic region annotations.

**Approach:** Use bcftools view with BED files to restrict to target regions or exclude blacklisted areas.

```bash
# Exclude problematic regions
bcftools view -T ^blacklist.bed input.vcf -o filtered.vcf

# Keep only exonic regions
bcftools view -R exons.bed input.vcf -o exonic.vcf
```

## Sample-Level Filtering

**Goal:** Remove low-quality samples and sites with excessive missing genotypes.

**Approach:** Compute per-sample missingness with bcftools stats, exclude failing samples, and filter sites by F_MISSING threshold.

```bash
# Missing genotype rate per sample
bcftools stats -s - input.vcf | grep ^PSC | cut -f3,14

# Filter samples with >10% missing
bcftools view -S good_samples.txt input.vcf -o sample_filtered.vcf

# Filter sites with >5% missing genotypes
bcftools filter -i 'F_MISSING<0.05' input.vcf -o site_filtered.vcf
```

## Variant Type-Specific Filters

**Goal:** Apply different quality thresholds to SNPs and indels.

**Approach:** Separate by type, apply type-appropriate thresholds (e.g., FS<60 for SNPs, FS<200 for indels), then merge back.

```bash
# Separate SNPs and indels for different filters
bcftools view -v snps input.vcf -o snps.vcf
bcftools view -v indels input.vcf -o indels.vcf

# Apply different thresholds
bcftools filter -i 'QUAL>30 && INFO/FS<60' snps.vcf -o snps_filtered.vcf
bcftools filter -i 'QUAL>30 && INFO/FS<200' indels.vcf -o indels_filtered.vcf

# Merge back
bcftools concat snps_filtered.vcf indels_filtered.vcf | bcftools sort -o merged.vcf
```

## Multi-Step Pipeline Filtering

**Goal:** Chain multiple filter criteria in a single pipeline with optional soft filter labels.

**Approach:** Pipe through successive bcftools filter commands, using -s for named soft filters and -f PASS for final hard extraction.

```bash
bcftools filter -e 'QUAL<30' input.vcf.gz | \
    bcftools filter -e 'INFO/DP<10' | \
    bcftools view -v snps -Oz -o filtered_snps.vcf.gz

# Named soft filters
bcftools filter -s 'LowQual' -e 'QUAL<30' input.vcf.gz | \
    bcftools filter -s 'LowDepth' -e 'INFO/DP<10' -Oz -o marked.vcf.gz

# Later, remove all filtered variants
bcftools view -f PASS marked.vcf.gz -Oz -o pass_only.vcf.gz
```

## Somatic Variant Filters

**Goal:** Filter somatic variants from tumor-normal calling with caller-specific criteria.

**Approach:** Use GATK FilterMutectCalls with contamination/segmentation tables, then apply additional bcftools thresholds on TLOD and VAF.

```bash
# Mutect2 specific
gatk FilterMutectCalls \
    -R reference.fa \
    -V mutect2_raw.vcf \
    --contamination-table contamination.table \
    --tumor-segmentation segments.table \
    -O mutect2_filtered.vcf

# Additional somatic filters
bcftools filter -i 'INFO/TLOD>6.3 && FMT/AF[0]>0.05 && FMT/DP[0]>20' \
    mutect2_filtered.vcf -o somatic_final.vcf
```

## Python Filtering (cyvcf2)

**Goal:** Filter variants programmatically in Python for custom multi-metric criteria.

**Approach:** Iterate with cyvcf2, evaluate QUAL/INFO/FORMAT fields per variant, and write passing records with Writer.

```python
from cyvcf2 import VCF, Writer
import numpy as np

vcf = VCF('input.vcf.gz')
writer = Writer('filtered.vcf', vcf)

for variant in vcf:
    qual = variant.QUAL or 0
    dp = variant.INFO.get('DP', 0)
    fs = variant.INFO.get('FS', 0)
    mq = variant.INFO.get('MQ', 0)

    if qual >= 30 and dp >= 10 and fs <= 60 and mq >= 40:
        writer.write_record(variant)

writer.close()
vcf.close()
```

### Filter by Genotype

```python
from cyvcf2 import VCF, Writer

vcf = VCF('input.vcf.gz')
writer = Writer('filtered.vcf', vcf)

for variant in vcf:
    # Keep if at least one sample is heterozygous
    # gt_types: 0=HOM_REF, 1=HET, 2=UNKNOWN, 3=HOM_ALT
    if 1 in variant.gt_types:
        writer.write_record(variant)

writer.close()
vcf.close()
```

### Filter by Sample Depth

```python
from cyvcf2 import VCF, Writer
import numpy as np

vcf = VCF('input.vcf.gz')
writer = Writer('filtered.vcf', vcf)

for variant in vcf:
    depths = variant.format('DP')
    if depths is not None and np.min(depths) >= 10:
        writer.write_record(variant)

writer.close()
vcf.close()
```

## Validate Filtering

**Goal:** Assess the impact of filtering on variant quality and retention.

**Approach:** Compare before/after bcftools stats, check Ti/Tv ratio improvement, and count variants per filter label.

```bash
# Compare before/after stats
bcftools stats input.vcf > before_stats.txt
bcftools stats filtered.vcf > after_stats.txt

# Ti/Tv ratio (should be ~2.1 for WGS, ~2.8-3.3 for exomes)
bcftools stats filtered.vcf | grep 'TSTV'

# Count variants per filter
bcftools query -f '%FILTER\n' filtered.vcf | sort | uniq -c
```

## Quick Reference

| Task | Command |
|------|---------|
| Quality filter | `bcftools filter -e 'QUAL<30' in.vcf.gz` |
| Depth filter | `bcftools filter -e 'INFO/DP<10' in.vcf.gz` |
| SNPs only | `bcftools view -v snps in.vcf.gz` |
| Indels only | `bcftools view -v indels in.vcf.gz` |
| PASS only | `bcftools view -f PASS in.vcf.gz` |
| Soft filter | `bcftools filter -s 'LowQ' -e 'QUAL<30' in.vcf.gz` |
| Region | `bcftools view -r chr1:1-1000 in.vcf.gz` |
| Biallelic | `bcftools view -m2 -M2 in.vcf.gz` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `no such INFO tag` | Tag not in VCF | Check header with `bcftools view -h` |
| `syntax error` | Invalid expression | Check operator syntax (`\|\|` not `or`) |
| `empty output` | Filter too strict | Relax thresholds |

## Related Skills

- variant-calling/variant-calling - Generate VCF files
- variant-calling/gatk-variant-calling - GATK VQSR
- variant-calling/variant-annotation - Annotation after filtering
- variant-calling/vcf-statistics - Evaluate filter effects
