# bio-variant-normalization

> Normalize indel representation and split multiallelic variants using bcftools norm. Use when comparing variants from different callers or preparing VCF for downstream analysis.

## Version Compatibility

Reference examples tested with: bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Variant Normalization

Left-align indels and split multiallelic sites using bcftools norm.

## Why Normalize?

The same variant can be represented multiple ways:

```
# Same deletion, different representations
chr1  100  ATCG  A      (right-aligned)
chr1  100  ATC   A      (left-aligned, normalized)
chr1  101  TCG   T      (different position)
```

Normalization ensures consistent representation for:
- Comparing variants from different callers
- Database lookups (dbSNP, ClinVar)
- Merging VCF files

## bcftools norm

**Goal:** Left-align indels and check reference allele consistency.

**Approach:** Use bcftools norm with a reference FASTA to shift indels to the leftmost position and optionally fix/exclude REF mismatches.

**"Normalize my VCF before comparing callers"** → Left-align indel representations and split multiallelic sites for consistent variant comparison.

### Left-Align Indels

```bash
bcftools norm -f reference.fa input.vcf.gz -Oz -o normalized.vcf.gz
```

Requires reference FASTA to determine left-most representation.

### Check for Normalization Issues

```bash
bcftools norm -f reference.fa -c s input.vcf.gz > /dev/null
# Reports REF allele mismatches
```

Check modes (`-c`):
- `w` - Warn on mismatch (default)
- `e` - Error on mismatch
- `x` - Exclude mismatches
- `s` - Set correct REF from reference

## Multiallelic Sites

**Goal:** Convert multiallelic sites to biallelic records or vice versa.

**Approach:** Use bcftools norm -m flags to split (decompose) or join (merge) multiallelic records.

### Split Multiallelic to Biallelic

```bash
bcftools norm -m-any input.vcf.gz -Oz -o split.vcf.gz
```

Before:
```
chr1  100  .  A  G,T  30  PASS  .  GT  1/2
```

After:
```
chr1  100  .  A  G  30  PASS  .  GT  1/0
chr1  100  .  A  T  30  PASS  .  GT  0/1
```

### Split SNPs Only

```bash
bcftools norm -m-snps input.vcf.gz -Oz -o split_snps.vcf.gz
```

### Split Indels Only

```bash
bcftools norm -m-indels input.vcf.gz -Oz -o split_indels.vcf.gz
```

### Join Biallelic to Multiallelic

```bash
bcftools norm -m+any input.vcf.gz -Oz -o merged.vcf.gz
```

## Split Options

| Option | Description |
|--------|-------------|
| `-m-any` | Split all multiallelic sites |
| `-m-snps` | Split multiallelic SNPs only |
| `-m-indels` | Split multiallelic indels only |
| `-m-both` | Split SNPs and indels separately |
| `-m+any` | Join biallelic sites into multiallelic |
| `-m+snps` | Join biallelic SNPs |
| `-m+indels` | Join biallelic indels |
| `-m+both` | Join SNPs and indels separately |

## Combined Normalization

**Goal:** Left-align indels and split multiallelic sites in a single pass.

**Approach:** Combine -f (reference) and -m-any (split) flags in one bcftools norm invocation.

### Standard Normalization Pipeline

```bash
bcftools norm -f reference.fa -m-any input.vcf.gz -Oz -o normalized.vcf.gz
bcftools index normalized.vcf.gz
```

This:
1. Left-aligns indels
2. Splits multiallelic sites

### Remove Duplicates After Splitting

```bash
bcftools norm -f reference.fa -m-any -d exact input.vcf.gz -Oz -o normalized.vcf.gz
```

Duplicate removal options (`-d`):
- `exact` - Remove exact duplicates
- `snps` - Remove duplicate SNPs
- `indels` - Remove duplicate indels
- `both` - Remove duplicate SNPs and indels
- `all` - Remove all duplicates
- `none` - Keep duplicates (default)

## Fixing Reference Alleles

**Goal:** Correct or remove variants whose REF allele does not match the reference genome.

**Approach:** Use bcftools norm -c with mode s (set correct REF) or x (exclude mismatches).

### Fix Mismatches from Reference

```bash
bcftools norm -f reference.fa -c s input.vcf.gz -Oz -o fixed.vcf.gz
```

This sets REF alleles to match the reference genome.

### Exclude Mismatches

```bash
bcftools norm -f reference.fa -c x input.vcf.gz -Oz -o clean.vcf.gz
```

Removes variants where REF doesn't match reference.

## Atomize Complex Variants

**Goal:** Decompose multi-nucleotide polymorphisms (MNPs) into individual SNP records.

**Approach:** Use bcftools norm --atomize to break complex substitutions into atomic single-base changes.

### Split MNPs to SNPs

```bash
bcftools norm --atomize input.vcf.gz -Oz -o atomized.vcf.gz
```

Before:
```
chr1  100  .  ATG  GCA  30  PASS
```

After:
```
chr1  100  .  A  G  30  PASS
chr1  101  .  T  C  30  PASS
chr1  102  .  G  A  30  PASS
```

### Atomize and Left-Align

```bash
bcftools norm -f reference.fa --atomize input.vcf.gz -Oz -o atomized.vcf.gz
```

## Old to New Format

### Update VCF Version

```bash
bcftools norm --old-rec-tag OLD input.vcf.gz -Oz -o updated.vcf.gz
```

Tags original record for reference.

## Common Workflows

**Goal:** Apply normalization as a preprocessing step for downstream analyses.

**Approach:** Normalize both VCFs identically before comparison, annotation, or GWAS preparation.

### Before Comparing Callers

```bash
# Normalize both VCFs the same way
for vcf in caller1.vcf.gz caller2.vcf.gz; do
    base=$(basename "$vcf" .vcf.gz)
    bcftools norm -f reference.fa -m-any "$vcf" -Oz -o "${base}.norm.vcf.gz"
    bcftools index "${base}.norm.vcf.gz"
done

# Now compare
bcftools isec -p comparison caller1.norm.vcf.gz caller2.norm.vcf.gz
```

### Before Database Annotation

```bash
bcftools norm -f reference.fa -m-any variants.vcf.gz -Oz -o normalized.vcf.gz
bcftools index normalized.vcf.gz
# Now annotate against dbSNP, ClinVar, etc.
```

### Prepare for GWAS

```bash
bcftools norm -f reference.fa -m-any -d exact input.vcf.gz | \
    bcftools view -v snps -Oz -o gwas_ready.vcf.gz
bcftools index gwas_ready.vcf.gz
```

## cyvcf2 Normalization Check

**Goal:** Assess how many variants require normalization before running bcftools norm.

**Approach:** Iterate with cyvcf2 and count multiallelic sites and complex (MNP) variants.

### Check if Variants Need Normalization

```python
from cyvcf2 import VCF

def needs_normalization(variant):
    # Check for multiallelic
    if len(variant.ALT) > 1:
        return True

    # Check for complex variants (potential MNPs)
    ref, alt = variant.REF, variant.ALT[0]
    if len(ref) > 1 and len(alt) > 1 and len(ref) == len(alt):
        return True

    return False

count = 0
for variant in VCF('input.vcf.gz'):
    if needs_normalization(variant):
        count += 1

print(f'Variants needing normalization: {count}')
```

### Count Multiallelic Sites

```python
from cyvcf2 import VCF

multiallelic = 0
total = 0

for variant in VCF('input.vcf.gz'):
    total += 1
    if len(variant.ALT) > 1:
        multiallelic += 1

print(f'Total variants: {total}')
print(f'Multiallelic sites: {multiallelic}')
print(f'Percentage: {multiallelic/total*100:.1f}%')
```

## Quick Reference

| Task | Command |
|------|---------|
| Left-align indels | `bcftools norm -f ref.fa in.vcf.gz` |
| Split multiallelic | `bcftools norm -m-any in.vcf.gz` |
| Join to multiallelic | `bcftools norm -m+any in.vcf.gz` |
| Full normalization | `bcftools norm -f ref.fa -m-any in.vcf.gz` |
| Fix REF alleles | `bcftools norm -f ref.fa -c s in.vcf.gz` |
| Remove duplicates | `bcftools norm -d exact in.vcf.gz` |
| Atomize MNPs | `bcftools norm --atomize in.vcf.gz` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `REF does not match` | Wrong reference | Use same reference as caller |
| `not sorted` | Unsorted input | Run `bcftools sort` first |
| `duplicate records` | Same position twice | Use `-d` to remove |

## Related Skills

- variant-calling - Generate VCF files
- filtering-best-practices - Filter after normalization
- vcf-manipulation - Compare normalized VCFs
- variant-annotation - Annotate normalized variants
