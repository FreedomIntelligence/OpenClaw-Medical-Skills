# bio-variant-calling-structural-variant-calling

> Call structural variants (SVs) from short-read sequencing using Manta, Delly, and LUMPY. Detects deletions, insertions, inversions, duplications, and translocations that are too large for standard SNV callers. Use when detecting structural variants from short-read data.

## Version Compatibility

Reference examples tested with: bcftools 1.19+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structural Variant Calling (Short Reads)

**"Call structural variants from my WGS data"** → Detect large genomic rearrangements (deletions, insertions, inversions, duplications, translocations) using split-read and discordant-pair evidence.
- CLI: `configManta.py` (Manta), `delly call`, `lumpyexpress`/`smoove call`

## Manta (Recommended)

```bash
# Configure Manta run (creates runWorkflow.py)
configManta.py \
    --bam sample.bam \
    --referenceFasta reference.fa \
    --runDir manta_run

# Execute
manta_run/runWorkflow.py -j 8

# Output: manta_run/results/variants/
# - diploidSV.vcf.gz (germline SVs)
# - candidateSV.vcf.gz (all candidates)
# - candidateSmallIndels.vcf.gz (small indels)
```

## Manta Tumor-Normal Mode

```bash
# Somatic SV calling
configManta.py \
    --tumorBam tumor.bam \
    --normalBam normal.bam \
    --referenceFasta reference.fa \
    --runDir manta_somatic

manta_somatic/runWorkflow.py -j 8

# Output includes:
# - somaticSV.vcf.gz (somatic SVs)
# - diploidSV.vcf.gz (germline SVs)
```

## Manta Options

```bash
# WES mode (for exome data)
configManta.py \
    --bam sample.bam \
    --referenceFasta reference.fa \
    --exome \                          # Use exome settings
    --callRegions regions.bed.gz \     # Restrict to regions
    --runDir manta_exome

# RNA-seq mode
configManta.py \
    --bam rnaseq.bam \
    --referenceFasta reference.fa \
    --rna \                            # RNA-seq mode
    --runDir manta_rna
```

## Delly

```bash
# Call SVs
delly call \
    -g reference.fa \
    -o sv_calls.bcf \
    sample.bam

# Convert to VCF
bcftools view sv_calls.bcf > sv_calls.vcf

# Multiple samples (joint calling)
delly call \
    -g reference.fa \
    -o joint_svs.bcf \
    sample1.bam sample2.bam sample3.bam
```

## Delly Somatic Mode

```bash
# Call with tumor-normal
delly call \
    -g reference.fa \
    -o svs.bcf \
    tumor.bam normal.bam

# Create sample file
echo -e "tumor\ttumor\nnormal\tcontrol" > samples.tsv

# Filter for somatic
delly filter \
    -f somatic \
    -o somatic_svs.bcf \
    -s samples.tsv \
    svs.bcf
```

## Delly SV Types

```bash
# Call specific SV type
delly call -t DEL -g ref.fa -o deletions.bcf sample.bam
delly call -t DUP -g ref.fa -o duplications.bcf sample.bam
delly call -t INV -g ref.fa -o inversions.bcf sample.bam
delly call -t BND -g ref.fa -o translocations.bcf sample.bam
delly call -t INS -g ref.fa -o insertions.bcf sample.bam
```

## LUMPY

```bash
# Extract split reads and discordant pairs
samtools view -b -F 1294 sample.bam > discordant.bam
samtools view -h sample.bam | \
    /path/to/lumpy-sv/scripts/extractSplitReads_BwaMem -i stdin | \
    samtools view -Sb - > splitters.bam

# Run LUMPY
lumpyexpress \
    -B sample.bam \
    -S splitters.bam \
    -D discordant.bam \
    -o lumpy_svs.vcf
```

## Smoove (LUMPY Wrapper)

```bash
# Simplified LUMPY workflow
smoove call \
    --name sample \
    --fasta reference.fa \
    --outdir smoove_output \
    -p 8 \
    sample.bam

# Output: smoove_output/sample-smoove.genotyped.vcf.gz
```

## Merge Multiple Callers

**Goal:** Increase confidence in SV calls by requiring support from multiple callers.

**Approach:** Run 2-3 callers independently, then merge callsets with SURVIVOR requiring agreement on breakpoint proximity and SV type.

```bash
# Use SURVIVOR to merge callsets
# Create file listing VCFs
ls manta_svs.vcf delly_svs.vcf lumpy_svs.vcf > vcf_list.txt

# Merge with parameters
SURVIVOR merge vcf_list.txt 1000 2 1 1 0 50 merged_svs.vcf

# Parameters: max_dist min_callers type_agree strand_agree estimate_dist min_size
```

## Filter SV Calls

```bash
# Filter by quality
bcftools view -i 'QUAL >= 20' svs.vcf > svs.filtered.vcf

# Filter by size
bcftools view -i 'ABS(SVLEN) >= 50' svs.vcf > svs.min50.vcf

# Filter by SV type
bcftools view -i 'SVTYPE="DEL"' svs.vcf > deletions.vcf
bcftools view -i 'SVTYPE="INS"' svs.vcf > insertions.vcf
bcftools view -i 'SVTYPE="INV"' svs.vcf > inversions.vcf
bcftools view -i 'SVTYPE="DUP"' svs.vcf > duplications.vcf
bcftools view -i 'SVTYPE="BND"' svs.vcf > translocations.vcf

# Keep only PASS
bcftools view -f PASS svs.vcf > svs.pass.vcf
```

## Annotate SVs

```bash
# AnnotSV annotation
AnnotSV \
    -SVinputFile svs.vcf \
    -genomeBuild GRCh38 \
    -outputFile annotated_svs

# Output includes: genes, DGV, gnomAD-SV, ClinVar
```

## SV Types

| Type | Code | Description |
|------|------|-------------|
| Deletion | DEL | Sequence removed |
| Insertion | INS | Sequence inserted |
| Inversion | INV | Sequence reversed |
| Duplication | DUP | Sequence duplicated |
| Translocation | BND | Breakend (inter-chromosomal) |

## Comparison: Manta vs Delly vs LUMPY

| Feature | Manta | Delly | LUMPY |
|---------|-------|-------|-------|
| Speed | Fast | Medium | Medium |
| Sensitivity | High | High | High |
| Small SVs | Good | Moderate | Good |
| Large SVs | Good | Good | Good |
| RNA-seq | Yes | No | No |
| Somatic | Yes | Yes | Limited |

## Coverage Guidelines

| Coverage | Detection Ability |
|----------|-------------------|
| 10x | Large SVs (>1kb) |
| 30x | Most SVs |
| 50x+ | Small SVs, better breakpoints |

## Long-Read SV Callers

For long-read data (ONT/PacBio HiFi), use specialized callers with higher sensitivity:

| Caller | Best For | Notes |
|--------|----------|-------|
| CuteSV | ONT/HiFi | Fast, accurate for all SV types |
| Sniffles2 | ONT/HiFi | Population-scale, multisample |
| PBSV | PacBio | Official PacBio caller |

See **long-read-sequencing/structural-variants** for long-read SV workflows.

## Related Skills

- long-read-sequencing/structural-variants - Long-read SV calling
- copy-number/cnvkit-analysis - Copy number variants
- variant-calling/filtering-best-practices - Filter VCF files
- alignment-files/alignment-filtering - Prepare BAM files
