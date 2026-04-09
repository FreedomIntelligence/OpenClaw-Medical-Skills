# bio-chipseq-peak-calling

> ChIP-seq peak calling using MACS3 (or MACS2). Call narrow peaks for transcription factors or broad peaks for histone modifications. Supports input control, fragment size modeling, and various output formats including narrowPeak and broadPeak BED files. Use when calling peaks from ChIP-seq alignments.

## Version Compatibility

Reference examples tested with: MACS2 2.2+, MACS3 3.0+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Peak Calling with MACS3

**"Call peaks from my ChIP-seq data"** → Identify significantly enriched regions (narrow peaks for TFs, broad peaks for histone marks) by comparing IP signal to input control.
- CLI: `macs3 callpeak -t chip.bam -c input.bam -f BAM -g hs -n sample`

MACS3 is the actively developed successor to MACS2. Commands are identical except the binary name. MACS2 is in maintenance mode.

## Basic Peak Calling

**Goal:** Call enriched regions from ChIP-seq alignments with input control normalization.

**Approach:** Compare treatment BAM signal against input control using MACS3 local Poisson model.

```bash
# Call peaks with input control (recommended)
macs3 callpeak -t chip.bam -c input.bam -f BAM -g hs -n sample --outdir peaks/

# For MACS2 (legacy), replace 'macs3' with 'macs2' - syntax is identical
```

## Without Input Control

**Goal:** Call peaks without a matched input/control sample.

**Approach:** Use MACS3 with genomic background estimation only (less accurate than with control).

```bash
# Not recommended, but possible
macs3 callpeak -t chip.bam -f BAM -g hs -n sample --outdir peaks/
```

## Narrow Peaks (TF, H3K4me3, H3K27ac)

**Goal:** Call sharp, well-defined peaks typical of transcription factors and active histone marks.

**Approach:** Use default narrow peak mode with q-value filtering and genome size correction.

```bash
macs3 callpeak \
    -t chip.bam \
    -c input.bam \
    -f BAM \
    -g hs \                        # hs=human, mm=mouse, ce=worm, dm=fly
    -n sample_narrow \
    --outdir peaks/ \
    -q 0.05                        # q-value threshold
```

## Broad Peaks (H3K36me3, H3K27me3, H3K9me3)

**Goal:** Call diffuse, broad enrichment domains typical of repressive or elongation-associated histone marks.

**Approach:** Enable broad peak mode which links nearby enriched regions into broader domains.

```bash
macs3 callpeak \
    -t chip.bam \
    -c input.bam \
    -f BAM \
    -g hs \
    -n sample_broad \
    --outdir peaks/ \
    --broad \                      # Broad peak mode
    --broad-cutoff 0.1             # Broad peak q-value
```

## Paired-End Data

**Goal:** Call peaks from paired-end sequencing using actual fragment sizes instead of modeled estimates.

**Approach:** Use BAMPE format so MACS3 calculates fragment size from mate pairs directly.

```bash
# MACS3 uses BAMPE format for paired-end
macs3 callpeak \
    -t chip.bam \
    -c input.bam \
    -f BAMPE \                     # Paired-end BAM
    -g hs \
    -n sample_pe \
    --outdir peaks/
```

## Multiple Replicates

**Goal:** Call peaks from multiple biological replicates pooled together for increased statistical power.

**Approach:** Provide all replicate BAMs to MACS3, which internally pools reads before peak calling.

```bash
# Pool replicates (MACS3 handles internally)
macs3 callpeak \
    -t rep1.bam rep2.bam rep3.bam \
    -c input.bam \
    -f BAM \
    -g hs \
    -n pooled \
    --outdir peaks/
```

## Custom Genome Size

**Goal:** Call peaks for non-model organisms without a built-in genome size shortcut.

**Approach:** Provide the effective genome size as a numeric value instead of a species abbreviation.

```bash
# For non-model organisms or custom genomes
macs3 callpeak \
    -t chip.bam \
    -c input.bam \
    -f BAM \
    -g 2.7e9 \                     # Effective genome size in bp
    -n sample \
    --outdir peaks/
```

## Common Genome Sizes

| Genome | Flag | Effective Size |
|--------|------|----------------|
| Human | hs | 2.7e9 |
| Mouse | mm | 1.87e9 |
| C. elegans | ce | 9e7 |
| D. melanogaster | dm | 1.2e8 |

## Fixed Fragment Size

**Goal:** Call peaks when fragment size modeling fails or a specific extension size is needed.

**Approach:** Bypass model building and specify a fixed read extension size manually.

```bash
# If modeling fails or for ATAC-seq
macs3 callpeak \
    -t chip.bam \
    -c input.bam \
    -f BAM \
    -g hs \
    --nomodel \                    # Skip model building
    --extsize 200 \                # Fixed extension size
    -n sample \
    --outdir peaks/
```

## Generate Signal Tracks

**Goal:** Produce normalized signal tracks for genome browser visualization alongside peak calls.

**Approach:** Enable bedGraph output with signal-per-million-reads normalization, then convert to bigWig.

```bash
# Generate bedGraph and bigWig files
macs3 callpeak \
    -t chip.bam \
    -c input.bam \
    -f BAM \
    -g hs \
    -n sample \
    --outdir peaks/ \
    -B \                           # Generate bedGraph
    --SPMR                         # Signal per million reads

# Convert to bigWig (requires UCSC tools)
sort -k1,1 -k2,2n peaks/sample_treat_pileup.bdg > peaks/sample.sorted.bdg
bedGraphToBigWig peaks/sample.sorted.bdg chrom.sizes peaks/sample.bw
```

## Local Lambda for Broad Marks

**Goal:** Improve broad peak calling by disabling the genome-wide lambda estimate.

**Approach:** Use --nolambda to rely solely on local background estimation for very broad domains.

```bash
# Recommended for very broad marks
macs3 callpeak \
    -t chip.bam \
    -c input.bam \
    -f BAM \
    -g hs \
    --broad \
    --nolambda \                   # Use local lambda only
    -n sample \
    --outdir peaks/
```

## Cutoff Analysis

**Goal:** Evaluate how different significance thresholds affect the number of called peaks.

**Approach:** Run MACS3 cutoff analysis mode to generate a table of peak counts at various q-value cutoffs.

```bash
# Test different q-value cutoffs
macs3 callpeak \
    -t chip.bam \
    -c input.bam \
    -f BAM \
    -g hs \
    --cutoff-analysis \            # Generate cutoff analysis file
    -n sample \
    --outdir peaks/
```

## Output Files

| File | Description |
|------|-------------|
| *_peaks.narrowPeak | Peak coordinates (BED6+4) |
| *_peaks.broadPeak | Broad peak coordinates |
| *_summits.bed | Peak summit positions |
| *_model.r | R script for model visualization |
| *_treat_pileup.bdg | Treatment signal (with -B) |
| *_control_lambda.bdg | Control signal (with -B) |

## narrowPeak Format

```
chr1  100  200  peak_1  100  .  5.2  10.5  8.3  50
```
Columns: chr, start, end, name, score, strand, signalValue, pValue, qValue, peak

## Filter Peaks

**Goal:** Post-filter called peaks by statistical significance or signal strength.

**Approach:** Use awk on narrowPeak columns to apply q-value or signal-value cutoffs.

```bash
# Filter by q-value
awk '$9 > 2' peaks.narrowPeak > peaks.filtered.narrowPeak  # -log10(q) > 2 means q < 0.01

# Sort by signal strength
sort -k7,7nr peaks.narrowPeak > peaks.sorted.narrowPeak
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| -t | required | Treatment BAM file(s) |
| -c | none | Control BAM file(s) |
| -f | AUTO | Format (BAM, BAMPE, BED) |
| -g | hs | Genome size |
| -n | NA | Output prefix |
| -q | 0.05 | Q-value cutoff |
| -p | none | P-value cutoff (overrides -q) |
| --broad | false | Broad peak calling |
| --nomodel | false | Skip model building |
| --extsize | 200 | Extension size (with --nomodel) |
| -B | false | Generate bedGraph |
| --SPMR | false | Signal per million reads |

## Related Skills

- peak-annotation - Annotate peaks to genes
- differential-binding - Compare peaks between conditions
- alignment-files - Prepare BAM files
- chipseq-visualization - Visualize peaks
