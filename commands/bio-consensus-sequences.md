# bio-consensus-sequences

> Generate consensus FASTA sequences by applying VCF variants to a reference using bcftools consensus. Use when creating sample-specific reference sequences or reconstructing haplotypes.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, bcftools 1.19+, bedtools 2.31+, minimap2 2.26+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Consensus Sequences

**"Generate a consensus sequence from my VCF"** → Apply called variants to a reference FASTA, producing a sample-specific genome with optional haplotype selection and low-coverage masking.
- CLI: `bcftools consensus -f reference.fa input.vcf.gz`
- Python: `cyvcf2` + `Bio.SeqIO` for simple SNP-only cases

## Basic Usage

### Generate Consensus

```bash
bcftools consensus -f reference.fa input.vcf.gz > consensus.fa
```

### Specify Sample

```bash
bcftools consensus -f reference.fa -s sample1 input.vcf.gz > sample1.fa
```

### Output to File

```bash
bcftools consensus -f reference.fa -o consensus.fa input.vcf.gz
```

## Haplotype Selection

### First Haplotype Only

```bash
bcftools consensus -f reference.fa -H 1 input.vcf.gz > haplotype1.fa
```

### Second Haplotype Only

```bash
bcftools consensus -f reference.fa -H 2 input.vcf.gz > haplotype2.fa
```

### Haplotype Options

| Option | Description |
|--------|-------------|
| `-H 1` | First haplotype |
| `-H 2` | Second haplotype |
| `-H A` | Apply all ALT alleles |
| `-H R` | Apply REF alleles where heterozygous |
| `-I` | Apply IUPAC ambiguity codes (separate flag) |

## IUPAC Codes for Heterozygous Sites

```bash
bcftools consensus -f reference.fa -I input.vcf.gz > consensus_iupac.fa
```

Heterozygous sites encoded with IUPAC ambiguity codes:
- A/G → R
- C/T → Y
- A/C → M
- G/T → K
- A/T → W
- C/G → S

## Missing Data Handling

### Mark Missing as N

```bash
bcftools consensus -f reference.fa -M N input.vcf.gz > consensus.fa
```

### Mark Low Coverage as N

Using a mask BED file:

```bash
# Create mask from depth
samtools depth input.bam | awk '$3<10 {print $1"\t"$2-1"\t"$2}' > low_coverage.bed

# Apply mask
bcftools consensus -f reference.fa -m low_coverage.bed input.vcf.gz > consensus.fa
```

### Mask Options

| Option | Description |
|--------|-------------|
| `-m FILE` | Mask regions in BED file with N |
| `-M CHAR` | Character for masked regions (default N) |

## Region Selection

### Specific Region

```bash
bcftools consensus -f reference.fa -r chr1:1000-2000 input.vcf.gz > region.fa
```

### Multiple Regions

Use with BED file to extract multiple regions.

## Chain Files

### Generate Chain File

```bash
bcftools consensus -f reference.fa -c chain.txt input.vcf.gz > consensus.fa
```

Chain files map coordinates between reference and consensus:
- Useful for liftover of annotations
- Required when indels change sequence length

### Chain File Format

```
chain score ref_name ref_size ref_strand ref_start ref_end query_name query_size query_strand query_start query_end id
```

## Sample-Specific Consensus

### For Each Sample

```bash
for sample in $(bcftools query -l input.vcf.gz); do
    bcftools consensus -f reference.fa -s "$sample" input.vcf.gz > "${sample}.fa"
done
```

### Both Haplotypes

```bash
sample="sample1"
bcftools consensus -f reference.fa -s "$sample" -H 1 input.vcf.gz > "${sample}_hap1.fa"
bcftools consensus -f reference.fa -s "$sample" -H 2 input.vcf.gz > "${sample}_hap2.fa"
```

## Filtering Before Consensus

### PASS Variants Only

```bash
bcftools view -f PASS input.vcf.gz | \
    bcftools consensus -f reference.fa > consensus.fa
```

### High-Quality Variants Only

```bash
bcftools filter -i 'QUAL>=30 && INFO/DP>=10' input.vcf.gz | \
    bcftools consensus -f reference.fa > consensus.fa
```

### SNPs Only

```bash
bcftools view -v snps input.vcf.gz | \
    bcftools consensus -f reference.fa > consensus_snps.fa
```

## Sequence Naming

### Default Naming

Output uses reference sequence names.

### Custom Prefix

```bash
bcftools consensus -f reference.fa -p "sample1_" input.vcf.gz > consensus.fa
```

Sequences named: `sample1_chr1`, `sample1_chr2`, etc.

## Common Workflows

**Goal:** Generate consensus sequences for downstream analyses like phylogenetics, viral surveillance, or gene-level comparison.

**Approach:** Filter variants to high-quality calls, apply per-sample consensus generation, mask low-coverage regions with N, then combine for multi-sample workflows.

### Phylogenetic Analysis Preparation

```bash
# For each sample, generate consensus
mkdir -p consensus
for sample in $(bcftools query -l cohort.vcf.gz); do
    bcftools view -s "$sample" cohort.vcf.gz | \
        bcftools view -c 1 | \
        bcftools consensus -f reference.fa > "consensus/${sample}.fa"
done

# Combine for alignment
cat consensus/*.fa > all_samples.fa
```

### Viral Genome Assembly

```bash
# Apply high-quality variants only
bcftools filter -i 'QUAL>=30 && INFO/DP>=20' variants.vcf.gz | \
    bcftools view -f PASS | \
    bcftools consensus -f reference.fa -M N > consensus.fa
```

### Gene-Specific Consensus

```bash
# Extract gene region
bcftools consensus -f reference.fa -r chr1:1000000-1010000 \
    -s sample1 variants.vcf.gz > gene.fa
```

### Masked Low-Coverage Regions

```bash
# Create mask from coverage
samtools depth -a input.bam | \
    awk '$3<5 {print $1"\t"$2-1"\t"$2}' | \
    bedtools merge > low_coverage.bed

# Generate consensus with mask
bcftools consensus -f reference.fa -m low_coverage.bed \
    variants.vcf.gz > consensus.fa
```

## Verify Consensus

### Check Differences

```bash
# Align consensus to reference
minimap2 -a reference.fa consensus.fa | samtools view -bS > alignment.bam

# Or simple comparison
diff <(grep -v "^>" reference.fa) <(grep -v "^>" consensus.fa) | head
```

### Count Changes

```bash
# Number of differences
bcftools view -H input.vcf.gz | wc -l
```

## Handling Overlapping Variants

bcftools consensus handles overlapping variants automatically:
- Applies variants in order
- Warns about conflicts

Check for warnings:
```bash
bcftools consensus -f reference.fa input.vcf.gz 2>&1 | grep -i warn
```

## cyvcf2 Consensus (Simple Cases)

### Manual Consensus Generation

```python
from cyvcf2 import VCF
from Bio import SeqIO

# Load reference
ref_dict = {rec.id: str(rec.seq) for rec in SeqIO.parse('reference.fa', 'fasta')}

# Apply variants (SNPs only, simplified)
vcf = VCF('input.vcf.gz')
changes = {}

for variant in vcf:
    if variant.is_snp and len(variant.ALT) == 1:
        chrom = variant.CHROM
        pos = variant.POS - 1  # 0-based
        if chrom not in changes:
            changes[chrom] = {}
        changes[chrom][pos] = variant.ALT[0]

# Apply changes
for chrom, positions in changes.items():
    seq = list(ref_dict[chrom])
    for pos, alt in positions.items():
        seq[pos] = alt
    ref_dict[chrom] = ''.join(seq)

# Write output
with open('consensus.fa', 'w') as f:
    for chrom, seq in ref_dict.items():
        f.write(f'>{chrom}\n{seq}\n')
```

Note: Use `bcftools consensus` for production - handles indels and edge cases properly.

## Quick Reference

| Task | Command |
|------|---------|
| Basic consensus | `bcftools consensus -f ref.fa in.vcf.gz` |
| Specific sample | `bcftools consensus -f ref.fa -s sample in.vcf.gz` |
| Haplotype 1 | `bcftools consensus -f ref.fa -H 1 in.vcf.gz` |
| IUPAC codes | `bcftools consensus -f ref.fa -I in.vcf.gz` |
| With mask | `bcftools consensus -f ref.fa -m mask.bed in.vcf.gz` |
| Generate chain | `bcftools consensus -f ref.fa -c chain.txt in.vcf.gz` |
| Specific region | `bcftools consensus -f ref.fa -r chr1:1-1000 in.vcf.gz` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `not indexed` | VCF not indexed | Run `bcftools index` |
| `sequence not found` | Chromosome mismatch | Check chromosome names |
| `overlapping records` | Variants overlap | Usually OK, check warnings |
| `REF does not match` | Wrong reference | Use same reference as caller |

## Related Skills

- variant-calling - Generate VCF for consensus
- filtering-best-practices - Filter variants before consensus
- variant-normalization - Normalize indels first
- alignment-files/reference-operations - Reference manipulation
