# bio-long-read-sequencing-nanopore-methylation

> Calls DNA methylation from Oxford Nanopore sequencing data using signal-level analysis. Use when detecting 5mC or 6mA modifications directly from nanopore reads without bisulfite conversion.

## Version Compatibility

Reference examples tested with: methylKit 1.28+, minimap2 2.26+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Nanopore Methylation Calling

**"Call methylation from my Nanopore reads"** → Extract 5mC/6mA modification probabilities from basecalled reads and summarize per-site methylation frequencies.
- CLI: `modkit pileup aligned.bam methylation.bed --ref ref.fa`

## Modern Workflow (modkit)

ONT's modkit is the recommended tool for methylation analysis from basecalled data.

### Extract Methylation from BAM

```bash
# Assumes BAM has MM/ML tags from dorado basecalling
modkit pileup input.bam methylation.bed \
    --ref reference.fa \
    --cpg \
    --combine-strands
```

### Output Format

```
# bedMethyl format
chr1  1000  1001  .  10  +  1000  1001  0,0,0  10  80.5
# Columns: chrom, start, end, name, score, strand, thickStart, thickEnd,
#          itemRgb, coverage, percent_modified
```

## Basecalling with Methylation

```bash
# Dorado basecalling with 5mC model
dorado basecaller dna_r10.4.1_e8.2_400bps_sup@v4.2.0 \
    pod5_dir/ \
    --modified-bases 5mCG \
    > calls.bam

# Index and align
samtools fastq calls.bam | \
    minimap2 -ax map-ont -y reference.fa - | \
    samtools sort -o aligned.bam
samtools index aligned.bam
```

## Region-Specific Analysis

```bash
# CpG islands only
modkit pileup aligned.bam cpg_islands.bed \
    --ref reference.fa \
    --cpg \
    --include-bed cpg_islands.bed

# Promoter regions
modkit pileup aligned.bam promoters.bed \
    --ref reference.fa \
    --cpg \
    --include-bed promoters.bed
```

## Sample Summary

```bash
# Get modification summary statistics
modkit summary aligned.bam

# Output includes:
# - Total reads with modifications
# - Modification types detected
# - Fraction modified per type
```

## Differential Methylation

```bash
# Create BED files for each sample
modkit pileup sample1.bam sample1.bed --ref ref.fa --cpg
modkit pileup sample2.bam sample2.bed --ref ref.fa --cpg

# Compare with methylKit or DSS in R
```

## Quality Considerations

- Minimum coverage: 10x for reliable calls
- Modified base probability threshold: 0.5 default, adjust as needed
- Combine strands for CpG (symmetric methylation)

## Related Skills

- long-read-sequencing/basecalling - Dorado basecalling
- methylation-analysis/methylation-calling - General methylation concepts
- methylation-analysis/dmr-detection - Differential methylation
