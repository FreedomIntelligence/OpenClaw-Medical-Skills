# bio-longread-structural-variants

> Detect structural variants from long-read alignments using Sniffles, cuteSV, and SVIM. Use when detecting deletions, insertions, inversions, translocations, or complex rearrangements from ONT or PacBio data, especially those missed by short-read methods.

## Version Compatibility

Reference examples tested with: bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structural Variant Detection

**"Call structural variants from my long reads"** → Detect large deletions, insertions, inversions, duplications, and translocations with precise breakpoint resolution from ONT or PacBio alignments.
- CLI: `sniffles --input aligned.bam --vcf svs.vcf`, `cuteSV aligned.bam ref.fa svs.vcf output/`

## Sniffles2 - Basic SV Calling

```bash
# Call SVs from aligned BAM
sniffles --input aligned.bam \
    --vcf structural_variants.vcf \
    --reference reference.fa \
    --threads 4
```

## Sniffles2 - Common Options

```bash
sniffles --input aligned.bam \
    --vcf structural_variants.vcf \
    --reference reference.fa \
    --threads 8 \
    --minsupport 3 \               # Min supporting reads
    --minsvlen 50 \                # Min SV length
    --mapq 20 \                    # Min mapping quality
    --output-rnames \              # Include read names
    --mosaic                       # Detect mosaic SVs
```

## Sniffles2 - Population Calling

**Goal:** Jointly call and genotype structural variants across a cohort of long-read samples for population-level SV analysis.

**Approach:** Generate per-sample SNF signature files from individual BAMs, then merge and jointly genotype all samples in a single Sniffles2 call.

```bash
# Step 1: Call SVs per sample with SNF output
sniffles --input sample1.bam --snf sample1.snf --reference reference.fa
sniffles --input sample2.bam --snf sample2.snf --reference reference.fa

# Step 2: Merge and genotype
sniffles --input sample1.snf sample2.snf \
    --vcf population_svs.vcf \
    --reference reference.fa
```

## cuteSV - Alternative Caller

```bash
# cuteSV SV calling
cuteSV aligned.bam reference.fa output.vcf work_dir/ \
    --threads 8 \
    --min_support 3 \
    --min_size 50 \
    --genotype
```

## cuteSV - ONT Optimized

```bash
# Settings optimized for ONT
cuteSV aligned.bam reference.fa output.vcf work_dir/ \
    --threads 8 \
    --max_cluster_bias_INS 100 \
    --diff_ratio_merging_INS 0.3 \
    --max_cluster_bias_DEL 100 \
    --diff_ratio_merging_DEL 0.3 \
    --genotype
```

## cuteSV - PacBio HiFi Optimized

```bash
# Settings optimized for HiFi
cuteSV aligned.bam reference.fa output.vcf work_dir/ \
    --threads 8 \
    --max_cluster_bias_INS 1000 \
    --diff_ratio_merging_INS 0.9 \
    --max_cluster_bias_DEL 1000 \
    --diff_ratio_merging_DEL 0.5 \
    --genotype
```

## SVIM - Another Alternative

```bash
# SVIM for ONT data
svim alignment output_dir/ aligned.bam reference.fa \
    --insertion_sequences \
    --read_names \
    --sample sample_name
```

## pbsv - PacBio Specific

```bash
# Discover signatures
pbsv discover aligned.bam signatures.svsig.gz

# Call SVs
pbsv call reference.fa signatures.svsig.gz structural_variants.vcf
```

## Filter SV Calls

```bash
# Filter by quality and size
bcftools filter -i 'QUAL>=20 && ABS(SVLEN)>=50' svs.vcf > svs.filtered.vcf

# Keep only PASS
bcftools view -f PASS svs.vcf > svs.pass.vcf

# Filter specific SV types
bcftools view -i 'SVTYPE="DEL"' svs.vcf > deletions.vcf
bcftools view -i 'SVTYPE="INS"' svs.vcf > insertions.vcf
```

## Merge Multiple Callers

```bash
# Use SURVIVOR to merge SV callsets
SURVIVOR merge sample_files.txt 1000 2 1 1 0 50 merged_svs.vcf

# sample_files.txt contains VCF paths, one per line
# Parameters: max_distance, min_callers, type_agree, strand_agree, est_distance, min_size
```

## Annotate SVs

```bash
# Annotate with AnnotSV
AnnotSV -SVinputFile svs.vcf \
    -genomeBuild GRCh38 \
    -outputFile annotated_svs

# Or with bcftools
bcftools annotate -a gnomad_sv.vcf.gz -c INFO svs.vcf > svs.annotated.vcf
```

## SV Types

| Type | Code | Description |
|------|------|-------------|
| Deletion | DEL | Sequence removed |
| Insertion | INS | Sequence added |
| Inversion | INV | Sequence inverted |
| Duplication | DUP | Sequence duplicated |
| Translocation | BND | Breakend (complex) |

## Key Parameters - Sniffles2

| Parameter | Default | Description |
|-----------|---------|-------------|
| --minsupport | auto | Min supporting reads |
| --minsvlen | 50 | Min SV length |
| --mapq | 20 | Min mapping quality |
| --reference | none | Reference (for INS sequences) |
| --tandem-repeats | none | BED of tandem repeats |
| --mosaic | off | Detect mosaic SVs |

## Key Parameters - cuteSV

| Parameter | Default | Description |
|-----------|---------|-------------|
| --min_support | 10 | Min supporting reads |
| --min_size | 30 | Min SV length |
| --max_size | 100000 | Max SV length |
| --genotype | off | Output genotypes |
| --report_readid | off | Report read IDs |

## Coverage Guidelines

| Coverage | SV Detection |
|----------|--------------|
| 5-10x | Large SVs (>1kb) |
| 10-20x | Most SVs |
| 20-30x | High confidence |
| >30x | Mosaic/rare SVs |

## Related Skills

- long-read-alignment - Generate input BAM
- medaka-polishing - Polish assembly with SVs
- variant-calling/structural-variant-calling - Short-read SV comparison
