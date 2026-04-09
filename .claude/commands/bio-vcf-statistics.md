# bio-vcf-statistics

> Generate variant statistics, sample concordance, and quality metrics using bcftools stats and gtcheck. Use when evaluating variant quality, comparing samples, or summarizing VCF contents.

## Version Compatibility

Reference examples tested with: bcftools 1.19+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# VCF Statistics

Generate statistics and quality metrics using bcftools.

## Statistics Tools

| Command | Purpose |
|---------|---------|
| `bcftools stats` | Comprehensive variant statistics |
| `bcftools gtcheck` | Sample concordance and relatedness |
| `bcftools query` | Custom summaries |

## bcftools stats

**Goal:** Generate comprehensive variant statistics including counts, Ti/Tv ratio, and quality distributions.

**Approach:** Run bcftools stats and parse section-tagged output lines (SN, TSTV, AF, QUAL, DP).

**"How many variants are in this VCF?"** → Compute summary counts, substitution types, and quality distributions from variant records.

### Basic Statistics

```bash
bcftools stats input.vcf.gz > stats.txt
```

### View Key Metrics

```bash
bcftools stats input.vcf.gz | grep "^SN"
```

Output sections:
- `SN` - Summary numbers
- `TSTV` - Transitions/transversions
- `SiS` - Singleton stats
- `AF` - Allele frequency distribution
- `QUAL` - Quality distribution
- `IDD` - Indel distribution
- `ST` - Substitution types
- `DP` - Depth distribution

### Summary Numbers (SN)

```bash
bcftools stats input.vcf.gz | grep "^SN" | cut -f3-
```

Reports:
- Number of samples
- Number of records
- Number of SNPs
- Number of indels
- Number of multiallelic sites
- Number of multiallelic SNPs

### Transition/Transversion Ratio

```bash
bcftools stats input.vcf.gz | grep "^TSTV"
```

Expected Ti/Tv ratio:
- Whole genome: ~2.0-2.1
- Exome: ~2.8-3.3

### Per-Sample Statistics

```bash
bcftools stats -s - input.vcf.gz > per_sample.txt
```

### Compare Two VCFs

```bash
bcftools stats input1.vcf.gz input2.vcf.gz > comparison.txt
```

### Region-Specific Stats

```bash
bcftools stats -r chr1:1000000-2000000 input.vcf.gz > region_stats.txt
```

### Exome Statistics

```bash
bcftools stats -R exome.bed input.vcf.gz > exome_stats.txt
```

## Plotting Statistics

**Goal:** Visualize variant statistics as publication-quality plots.

**Approach:** Pipe bcftools stats output to plot-vcfstats to generate PDF and PNG plots.

### Generate Plots

```bash
bcftools stats input.vcf.gz > stats.txt
plot-vcfstats -p output_dir stats.txt
```

Creates:
- `output_dir/summary.pdf`
- Individual PNG files

### Comparison Plots

```bash
bcftools stats file1.vcf.gz file2.vcf.gz > comparison.txt
plot-vcfstats -p comparison_dir comparison.txt
```

## bcftools gtcheck

**Goal:** Verify sample identity and detect sample swaps by comparing genotype concordance.

**Approach:** Use bcftools gtcheck to compute pairwise discordance rates between samples or against a reference panel.

### Check Sample Identity

```bash
bcftools gtcheck -g reference.vcf.gz query.vcf.gz
```

Reports concordance between samples.

### Detect Sample Swaps

```bash
bcftools gtcheck -G 1 input.vcf.gz > relatedness.txt
```

Compares all samples pairwise.

### Output Format

```
DC  0  sample1  sample2  0.95  1234  1200
```

Fields:
- DC: Data type (discordance)
- Index
- Sample 1
- Sample 2
- Discordance rate
- Sites compared
- Discordant sites

### Check Against Reference Panel

```bash
bcftools gtcheck -g 1000genomes.vcf.gz unknown_sample.vcf.gz
```

## Quick Statistics with Query

**Goal:** Compute targeted summary statistics using bcftools query and shell tools.

**Approach:** Extract specific fields with bcftools query/view and aggregate with awk for counts, means, and distributions.

### Count Variants

```bash
bcftools view -H input.vcf.gz | wc -l
```

### Count by Type

```bash
# SNPs
bcftools view -v snps -H input.vcf.gz | wc -l

# Indels
bcftools view -v indels -H input.vcf.gz | wc -l
```

### Count PASS Variants

```bash
bcftools view -f PASS -H input.vcf.gz | wc -l
```

### Quality Distribution

```bash
bcftools query -f '%QUAL\n' input.vcf.gz | \
    awk '{sum+=$1; count++} END {print "Mean QUAL:", sum/count}'
```

### Depth Distribution

```bash
bcftools query -f '%INFO/DP\n' input.vcf.gz | \
    awk '{sum+=$1; count++} END {print "Mean DP:", sum/count}'
```

### Genotype Counts

```bash
# Count heterozygous sites per sample
bcftools query -f '[%GT\t]\n' input.vcf.gz | \
    awk -F'\t' '{for(i=1;i<=NF;i++) if($i=="0/1" || $i=="0|1") het[i]++}
        END {for(i in het) print "Sample", i, "het:", het[i]}'
```

### Allele Frequency Spectrum

```bash
bcftools query -f '%INFO/AF\n' input.vcf.gz | \
    awk '{
        if($1<0.01) rare++
        else if($1<0.05) low++
        else if($1<0.5) common++
        else freq++
    } END {
        print "Rare (<1%):", rare
        print "Low (1-5%):", low
        print "Common (5-50%):", common
        print "Frequent (>50%):", freq
    }'
```

## Sample Statistics

**Goal:** Compute per-sample variant counts, genotype distributions, and missingness rates.

**Approach:** Use bcftools query/view/stats per sample to tabulate sample-level metrics.

### List Samples

```bash
bcftools query -l input.vcf.gz
```

### Count Samples

```bash
bcftools query -l input.vcf.gz | wc -l
```

### Per-Sample Variant Counts

```bash
for sample in $(bcftools query -l input.vcf.gz); do
    count=$(bcftools view -s "$sample" -H input.vcf.gz | \
        bcftools view -c 1 -H | wc -l)
    echo "$sample: $count"
done
```

### Missing Genotypes per Sample

```bash
bcftools stats -s - input.vcf.gz | grep "^PSC"
```

## cyvcf2 Statistics

**Goal:** Compute variant statistics programmatically in Python for custom analyses.

**Approach:** Iterate variants with cyvcf2, accumulate counts by type, and compute quality/genotype distributions with numpy.

### Basic Counts

```python
from cyvcf2 import VCF

stats = {'snps': 0, 'indels': 0, 'other': 0}

for variant in VCF('input.vcf.gz'):
    if variant.is_snp:
        stats['snps'] += 1
    elif variant.is_indel:
        stats['indels'] += 1
    else:
        stats['other'] += 1

print(f'SNPs: {stats["snps"]}')
print(f'Indels: {stats["indels"]}')
print(f'Other: {stats["other"]}')
```

### Quality Statistics

```python
from cyvcf2 import VCF
import numpy as np

quals = []
for variant in VCF('input.vcf.gz'):
    if variant.QUAL:
        quals.append(variant.QUAL)

quals = np.array(quals)
print(f'Mean QUAL: {np.mean(quals):.1f}')
print(f'Median QUAL: {np.median(quals):.1f}')
print(f'Min QUAL: {np.min(quals):.1f}')
print(f'Max QUAL: {np.max(quals):.1f}')
```

### Genotype Distribution

```python
from cyvcf2 import VCF

vcf = VCF('input.vcf.gz')
samples = vcf.samples

hom_ref = [0] * len(samples)
het = [0] * len(samples)
hom_alt = [0] * len(samples)
missing = [0] * len(samples)

for variant in vcf:
    for i, gt in enumerate(variant.gt_types):
        if gt == 0:
            hom_ref[i] += 1
        elif gt == 1:
            het[i] += 1
        elif gt == 3:
            hom_alt[i] += 1
        else:
            missing[i] += 1

for i, sample in enumerate(samples):
    print(f'{sample}: HOM_REF={hom_ref[i]}, HET={het[i]}, HOM_ALT={hom_alt[i]}, MISS={missing[i]}')
```

### Transition/Transversion Calculation

```python
from cyvcf2 import VCF

transitions = 0
transversions = 0

ti_pairs = {('A', 'G'), ('G', 'A'), ('C', 'T'), ('T', 'C')}

for variant in VCF('input.vcf.gz'):
    if not variant.is_snp:
        continue
    ref = variant.REF
    alt = variant.ALT[0]
    if (ref, alt) in ti_pairs:
        transitions += 1
    else:
        transversions += 1

ratio = transitions / transversions if transversions > 0 else 0
print(f'Transitions: {transitions}')
print(f'Transversions: {transversions}')
print(f'Ti/Tv ratio: {ratio:.2f}')
```

## Common Workflows

**Goal:** Run standard QC and comparison workflows for variant call evaluation.

**Approach:** Combine bcftools stats, grep, and plot-vcfstats for before/after filtering comparisons and sample relatedness checks.

### Quality Control Report

```bash
# Generate stats
bcftools stats input.vcf.gz > stats.txt

# Extract key metrics
echo "=== VCF Summary ==="
grep "^SN" stats.txt | cut -f3-

echo ""
echo "=== Ti/Tv Ratio ==="
grep "^TSTV" stats.txt | cut -f5

# Generate plots
plot-vcfstats -p qc_plots stats.txt
```

### Compare Before/After Filtering

```bash
bcftools stats raw.vcf.gz filtered.vcf.gz > comparison.txt

echo "=== Before Filtering ==="
grep "^SN.*raw" comparison.txt | cut -f3-

echo ""
echo "=== After Filtering ==="
grep "^SN.*filtered" comparison.txt | cut -f3-
```

### Sample Relatedness Check

```bash
bcftools gtcheck -G 1 cohort.vcf.gz > relatedness.txt
cat relatedness.txt
```

## Quick Reference

| Task | Command |
|------|---------|
| Full stats | `bcftools stats input.vcf.gz` |
| Summary only | `bcftools stats input.vcf.gz \| grep "^SN"` |
| Ti/Tv ratio | `bcftools stats input.vcf.gz \| grep "^TSTV"` |
| Per-sample | `bcftools stats -s - input.vcf.gz` |
| Compare VCFs | `bcftools stats file1.vcf.gz file2.vcf.gz` |
| Sample check | `bcftools gtcheck -G 1 input.vcf.gz` |
| Plot stats | `plot-vcfstats -p dir stats.txt` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `No data` | Empty VCF | Check if VCF has variants |
| `plot-vcfstats not found` | Not installed | Install with bcftools |
| `Cannot open` | Invalid VCF | Check file format |

## Related Skills

- vcf-basics - View and query VCF files
- filtering-best-practices - Evaluate filter impact
- vcf-manipulation - Compare call sets
- variant-calling - Assess calling quality
