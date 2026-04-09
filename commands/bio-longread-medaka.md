# bio-longread-medaka

> Polish assemblies and call variants from Oxford Nanopore data using medaka. Uses neural networks trained on specific basecaller versions. Use when improving ONT-only assemblies or calling variants from Nanopore data without short-read polishing.

## Version Compatibility

Reference examples tested with: bcftools 1.19+, minimap2 2.26+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Medaka Polishing and Variant Calling

**"Polish my ONT assembly with medaka"** → Use neural networks trained on specific basecaller models to correct assembly errors and call variants from Nanopore data.
- CLI: `medaka_polisher -i reads.fq -d draft.fa -o polished.fa -m r1041_e82_400bps_sup_v5.0.0`

## Basic Consensus Polishing

```bash
# Polish assembly with medaka
medaka_consensus -i reads.fastq.gz \
    -d draft_assembly.fa \
    -o medaka_output \
    -t 4 \
    -m r1041_e82_400bps_sup_v5.0.0
```

## Variant Calling (Haploid)

```bash
# Call variants against reference
medaka_variant \
    -i reads.fastq.gz \
    -r reference.fa \
    -o output_dir \
    -m r1041_e82_400bps_sup_v5.0.0
```

Note: Diploid variant calling has been deprecated in medaka v2.0. For diploid samples, use [Clair3](https://github.com/HKU-BAL/Clair3) instead.

## Step-by-Step Workflow

**Goal:** Polish an ONT assembly or call variants using medaka's neural network models with explicit control over each step.

**Approach:** Align reads with minimap2, run medaka neural network inference on the alignment, then generate either a polished consensus or variant calls from the probability output.

```bash
# 1. Align reads to reference/draft
minimap2 -ax map-ont reference.fa reads.fastq.gz | \
    samtools sort -o aligned.bam
samtools index aligned.bam

# 2. Run neural network inference
medaka inference aligned.bam consensus.hdf \
    --model r1041_e82_400bps_sup_v5.0.0 \
    --threads 2                          # >2 threads has poor scaling

# 3. Create consensus sequence from probabilities
medaka sequence consensus.hdf reference.fa polished.fa

# 4. Call variants from probabilities
medaka vcf reference.fa consensus.hdf variants.vcf
```

## List Available Models

```bash
# See all available models
medaka tools list_models

# Models are named:
# r{pore}_{chemistry}_{speed}bps_{accuracy}_{version}
# e.g., r1041_e82_400bps_sup_v5.0.0
```

## Common Models

| Model | Description |
|-------|-------------|
| r1041_e82_400bps_sup_v5.0.0 | R10.4.1, E8.2, SUP basecalling |
| r1041_e82_400bps_hac_v5.0.0 | R10.4.1, E8.2, HAC basecalling |
| r941_min_sup_g507 | R9.4.1, MinION, SUP |
| r941_min_hac_g507 | R9.4.1, MinION, HAC |

## Choose Model Based on Basecaller

```bash
# Check which basecaller was used in your data
# Then select matching model

# For Guppy/Dorado SUP basecalling on R10.4.1
medaka_consensus -m r1041_e82_400bps_sup_v5.0.0 ...

# For HAC basecalling
medaka_consensus -m r1041_e82_400bps_hac_v5.0.0 ...
```

## Polish Region Only

```bash
# Polish specific region
medaka inference aligned.bam consensus.hdf \
    --model r1041_e82_400bps_sup_v5.0.0 \
    --region chr1:1000000-2000000
```

## Multiple Rounds of Polishing

```bash
# First round
medaka_consensus -i reads.fastq.gz -d draft.fa -o round1 -m model

# Second round (diminishing returns, usually not needed)
medaka_consensus -i reads.fastq.gz -d round1/consensus.fasta -o round2 -m model
```

## Call Variants from Existing BAM

```bash
# If you already have aligned BAM
medaka inference aligned.bam consensus.hdf --model r1041_e82_400bps_sup_v5.0.0
medaka vcf reference.fa consensus.hdf variants.vcf
```

## Filter VCF Output

```bash
# Filter by quality
bcftools filter -i 'QUAL>20' variants.vcf > variants.filtered.vcf

# Get high-confidence calls
bcftools view -i 'FILTER="PASS"' variants.vcf > variants.pass.vcf
```

## Output Files

| File | Description |
|------|-------------|
| consensus.fasta | Polished sequence |
| consensus.hdf | Neural network outputs |
| variants.vcf | Variant calls |
| calls_to_draft.bam | Alignments used |

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| -i | Input reads (FASTQ) |
| -d | Draft assembly/reference |
| -o | Output directory |
| -m | Model name |
| -t | Threads |
| -b | Batch size (GPU memory) |
| --region | Specific region to process |

## GPU Acceleration

```bash
# Enable GPU (if available)
medaka_consensus -i reads.fastq.gz -d draft.fa -o output \
    -m r1041_e82_400bps_sup_v5.0.0 \
    -b 100 \                       # Increase batch size for GPU
    -t 4
```

## Related Skills

- long-read-alignment - Generate input alignments
- structural-variants - Find SVs from polished assembly
- variant-calling/variant-calling - Short-read variant calling comparison
