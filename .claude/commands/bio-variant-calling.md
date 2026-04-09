# bio-variant-calling

> Call SNPs and indels from aligned reads using bcftools mpileup and call. Use when detecting variants from BAM files or generating VCF from alignments.

## Version Compatibility

Reference examples tested with: bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Variant Calling

Call SNPs and indels from aligned reads using bcftools.

## Basic Workflow

```
BAM file + Reference FASTA
         |
         v
   bcftools mpileup (generate pileup)
         |
         v
   bcftools call (call variants)
         |
         v
   VCF file
```

## bcftools mpileup + call

**Goal:** Detect SNPs and indels from aligned reads using the bcftools pileup-and-call pipeline.

**Approach:** Generate per-position pileup likelihoods with mpileup, then call genotypes with the multiallelic caller.

**"Call variants from my BAM file"** → Generate genotype likelihoods from aligned reads and identify variant sites using a Bayesian caller.

### Basic Variant Calling
```bash
bcftools mpileup -f reference.fa input.bam | bcftools call -mv -o variants.vcf
```

### Output Compressed VCF
```bash
bcftools mpileup -f reference.fa input.bam | bcftools call -mv -Oz -o variants.vcf.gz
bcftools index variants.vcf.gz
```

### Call Specific Region
```bash
bcftools mpileup -f reference.fa -r chr1:1000000-2000000 input.bam | \
    bcftools call -mv -o region.vcf
```

### Call from Multiple BAMs
```bash
bcftools mpileup -f reference.fa sample1.bam sample2.bam sample3.bam | \
    bcftools call -mv -o variants.vcf
```

### BAM List File
```bash
# bams.txt: one BAM path per line
bcftools mpileup -f reference.fa -b bams.txt | bcftools call -mv -o variants.vcf
```

## mpileup Options

**Goal:** Control pileup generation with quality thresholds, annotations, and region restrictions.

**Approach:** Set minimum mapping/base quality, request specific FORMAT/INFO tags, and restrict to target regions.

### Quality Filtering
```bash
bcftools mpileup -f reference.fa \
    -q 20 \           # Min mapping quality
    -Q 20 \           # Min base quality
    input.bam | bcftools call -mv -o variants.vcf
```

### Annotate with Read Depth
```bash
bcftools mpileup -f reference.fa -a DP,AD input.bam | bcftools call -mv -o variants.vcf
```

### Full Annotation Set
```bash
bcftools mpileup -f reference.fa \
    -a FORMAT/DP,FORMAT/AD,FORMAT/ADF,FORMAT/ADR,INFO/AD \
    input.bam | bcftools call -mv -o variants.vcf
```

### Target Regions (BED)
```bash
bcftools mpileup -f reference.fa -R targets.bed input.bam | \
    bcftools call -mv -o variants.vcf
```

### Max Depth
```bash
bcftools mpileup -f reference.fa -d 1000 input.bam | bcftools call -mv -o variants.vcf
```

## call Options

### Calling Models

| Flag | Model | Use Case |
|------|-------|----------|
| `-m` | Multiallelic caller | Default, recommended |
| `-c` | Consensus caller | Legacy, single sample |

### Output Variants Only
```bash
bcftools mpileup -f reference.fa input.bam | bcftools call -mv -o variants.vcf
# -v outputs variant sites only (not reference calls)
```

### Output All Sites
```bash
bcftools mpileup -f reference.fa input.bam | bcftools call -m -o all_sites.vcf
# Without -v, outputs all sites including reference
```

### Ploidy
```bash
# Haploid calling
bcftools mpileup -f reference.fa input.bam | bcftools call -m --ploidy 1 -o variants.vcf

# Specify ploidy file
bcftools mpileup -f reference.fa input.bam | bcftools call -m --ploidy-file ploidy.txt -o variants.vcf
```

### Prior Probability
```bash
# Adjust variant prior (default 1.1e-3)
bcftools mpileup -f reference.fa input.bam | bcftools call -m -P 0.001 -o variants.vcf
```

## Common Pipelines

**Goal:** Run production-ready variant calling workflows for single-sample and multi-sample analyses.

**Approach:** Chain mpileup and call with quality filters, annotations, and compressed output, optionally parallelized by chromosome.

### Standard SNP/Indel Calling
```bash
bcftools mpileup -Ou -f reference.fa \
    -q 20 -Q 20 \
    -a FORMAT/DP,FORMAT/AD \
    input.bam | \
bcftools call -mv -Oz -o variants.vcf.gz

bcftools index variants.vcf.gz
```

### Multi-sample Calling
```bash
bcftools mpileup -Ou -f reference.fa \
    -a FORMAT/DP,FORMAT/AD \
    sample1.bam sample2.bam sample3.bam | \
bcftools call -mv -Oz -o cohort.vcf.gz

bcftools index cohort.vcf.gz
```

### Calling with Regions
```bash
bcftools mpileup -Ou -f reference.fa \
    -R targets.bed \
    -a FORMAT/DP,FORMAT/AD \
    input.bam | \
bcftools call -mv -Oz -o targets.vcf.gz
```

### Parallel by Chromosome
```bash
for chr in chr1 chr2 chr3; do
    bcftools mpileup -Ou -f reference.fa -r "$chr" input.bam | \
        bcftools call -mv -Oz -o "${chr}.vcf.gz" &
done
wait

# Concatenate results
bcftools concat -Oz -o all.vcf.gz chr*.vcf.gz
bcftools index all.vcf.gz
```

## Annotation Tags

### INFO Tags
| Tag | Description |
|-----|-------------|
| `DP` | Total read depth |
| `AD` | Allelic depths |
| `MQ` | Mapping quality |
| `FS` | Fisher strand bias |
| `SGB` | Segregation based metric |

### FORMAT Tags
| Tag | Description |
|-----|-------------|
| `GT` | Genotype |
| `DP` | Read depth per sample |
| `AD` | Allelic depths per sample |
| `ADF` | Forward strand allelic depths |
| `ADR` | Reverse strand allelic depths |
| `GQ` | Genotype quality |
| `PL` | Phred-scaled likelihoods |

### Request Specific Annotations
```bash
bcftools mpileup -f reference.fa \
    -a FORMAT/DP,FORMAT/AD,FORMAT/SP,INFO/AD \
    input.bam | bcftools call -mv -o variants.vcf
```

## Performance Options

**Goal:** Speed up variant calling for large datasets.

**Approach:** Use multi-threading and uncompressed BCF piping to reduce I/O overhead.

### Multi-threading
```bash
bcftools mpileup -f reference.fa --threads 4 input.bam | \
    bcftools call -mv --threads 4 -o variants.vcf
```

### Uncompressed BCF for Speed
```bash
bcftools mpileup -Ou -f reference.fa input.bam | bcftools call -mv -Ou | \
    bcftools filter -Oz -o filtered.vcf.gz
```

## Quick Reference

| Task | Command |
|------|---------|
| Basic calling | `bcftools mpileup -f ref.fa in.bam \| bcftools call -mv -o out.vcf` |
| With quality filter | `bcftools mpileup -f ref.fa -q 20 -Q 20 in.bam \| bcftools call -mv` |
| Region | `bcftools mpileup -f ref.fa -r chr1:1-1000 in.bam \| bcftools call -mv` |
| Multi-sample | `bcftools mpileup -f ref.fa s1.bam s2.bam \| bcftools call -mv` |
| With annotations | `bcftools mpileup -f ref.fa -a DP,AD in.bam \| bcftools call -mv` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `no FASTA reference` | Missing -f | Add `-f reference.fa` |
| `reference mismatch` | Wrong reference | Use same reference as alignment |
| `no variants called` | Low quality/depth | Lower quality thresholds |

## Related Skills

- vcf-basics - View and query resulting VCF
- filtering-best-practices - Filter variants by quality
- variant-normalization - Normalize indels
- alignment-files/pileup-generation - Alternative pileup generation
