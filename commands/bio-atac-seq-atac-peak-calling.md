# bio-atac-seq-atac-peak-calling

> Call accessible chromatin regions from ATAC-seq data using MACS3 with ATAC-specific parameters. Use when identifying open chromatin regions from aligned ATAC-seq BAM files, different from ChIP-seq peak calling.

## Version Compatibility

Reference examples tested with: Bowtie2 2.5.3+, MACS3 3.0+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# ATAC-seq Peak Calling

**"Call peaks from my ATAC-seq data"** → Identify open chromatin regions using ATAC-specific parameters (no input control, shifted Tn5 cut sites, paired-end mode).
- CLI: `macs3 callpeak -t atac.bam -f BAMPE -g hs --nomodel --shift -75 --extsize 150`

## Basic MACS3 for ATAC-seq

**Goal:** Identify open chromatin regions from ATAC-seq data using ATAC-specific peak calling parameters.

**Approach:** Run MACS3 in paired-end mode with Tn5 shift correction, no model building, and duplicate retention since ATAC-seq generates natural duplicates at accessible sites.

```bash
# Standard ATAC-seq peak calling
macs3 callpeak \
    -t sample.bam \
    -f BAMPE \
    -g hs \
    -n sample \
    --outdir peaks/ \
    -q 0.05 \
    --nomodel \
    --shift -75 \
    --extsize 150 \
    --keep-dup all \
    -B
```

## Key ATAC-seq Parameters

```bash
# Explained parameters
macs3 callpeak \
    -t sample.bam \        # Treatment BAM
    -f BAMPE \             # Paired-end BAM (uses fragment size)
    -g hs \                # Genome size: hs (human), mm (mouse)
    -n sample \            # Output name prefix
    --nomodel \            # Don't build shifting model
    --shift -75 \          # Shift reads to center on Tn5 cut site
    --extsize 150 \        # Extend reads to this size
    --keep-dup all \       # Keep duplicates (ATAC has natural duplicates)
    -B \                   # Generate bedGraph for visualization
    --call-summits         # Call peak summits
```

## Why These Parameters?

| Parameter | Reason |
|-----------|--------|
| --nomodel | ATAC doesn't have control, can't build model |
| --shift -75 | Centers on Tn5 insertion site |
| --extsize 150 | Smooths signal around cut sites |
| --keep-dup all | Tn5 creates duplicate cuts at accessible sites |
| -f BAMPE | Uses actual fragment size from paired-end |

## Paired-End vs Single-End

```bash
# Paired-end (recommended for ATAC)
macs3 callpeak -f BAMPE -t sample.bam ...

# Single-end (less common)
macs3 callpeak -f BAM -t sample.bam \
    --nomodel --shift -75 --extsize 150 ...
```

## Call Peaks on NFR Only

**Goal:** Call peaks using only nucleosome-free fragments for sharper regulatory element detection.

**Approach:** Filter BAM to fragments <100 bp (NFR), then call peaks with adjusted shift/extsize parameters matching the shorter fragment size.

```bash
# First, filter to nucleosome-free reads (<100bp fragments)
samtools view -h sample.bam | \
    awk 'substr($0,1,1)=="@" || ($9>0 && $9<100) || ($9<0 && $9>-100)' | \
    samtools view -b > nfr.bam

# Call peaks on NFR
macs3 callpeak \
    -t nfr.bam \
    -f BAMPE \
    -g hs \
    -n sample_nfr \
    --nomodel \
    --shift -37 \
    --extsize 75 \
    --keep-dup all \
    -q 0.01
```

## Broad Peaks (Optional)

```bash
# For broader accessible regions
macs3 callpeak \
    -t sample.bam \
    -f BAMPE \
    -g hs \
    -n sample_broad \
    --nomodel \
    --shift -75 \
    --extsize 150 \
    --broad \
    --broad-cutoff 0.1
```

## Batch Processing

**Goal:** Call peaks on multiple ATAC-seq samples in one pass.

**Approach:** Loop over BAM files and run MACS3 with consistent ATAC-specific parameters for each sample.

```bash
#!/bin/bash
GENOME=hs  # hs for human, mm for mouse
OUTDIR=peaks

mkdir -p $OUTDIR

for bam in *.bam; do
    sample=$(basename $bam .bam)
    echo "Processing $sample..."

    macs3 callpeak \
        -t $bam \
        -f BAMPE \
        -g $GENOME \
        -n $sample \
        --outdir $OUTDIR \
        --nomodel \
        --shift -75 \
        --extsize 150 \
        --keep-dup all \
        -q 0.05 \
        -B \
        --call-summits
done
```

## Output Files

| File | Description |
|------|-------------|
| _peaks.narrowPeak | Peak locations (BED-like) |
| _summits.bed | Peak summit positions |
| _peaks.xls | Peak statistics (Excel format) |
| _treat_pileup.bdg | Signal track (bedGraph) |
| _control_lambda.bdg | Background (if control provided) |

## narrowPeak Format

```
chr1  100  500  peak1  500  .  10.5  50.2  45.1  200
```

Columns: chrom, start, end, name, score, strand, signalValue, pValue, qValue, summit_offset

## Convert to BigWig

```bash
# Sort bedGraph
sort -k1,1 -k2,2n sample_treat_pileup.bdg > sample.sorted.bdg

# Convert to BigWig
bedGraphToBigWig sample.sorted.bdg chrom.sizes sample.bw
```

## Merge Replicates

```bash
# Pool BAMs before peak calling (recommended for final peaks)
samtools merge -@ 8 merged.bam rep1.bam rep2.bam rep3.bam

# Call peaks on merged
macs3 callpeak -t merged.bam -f BAMPE -g hs -n merged ...
```

## IDR for Replicate Consistency

**Goal:** Identify reproducible peaks across biological replicates using the Irreproducible Discovery Rate framework.

**Approach:** Call peaks on each replicate independently, then run IDR to score peak reproducibility and filter to a high-confidence set.

```bash
# Call peaks on each replicate
macs3 callpeak -t rep1.bam -f BAMPE -g hs -n rep1 ...
macs3 callpeak -t rep2.bam -f BAMPE -g hs -n rep2 ...

# Run IDR
idr --samples rep1_peaks.narrowPeak rep2_peaks.narrowPeak \
    --input-file-type narrowPeak \
    --output-file idr_peaks.txt \
    --plot

# Filter by IDR threshold
awk '$5 >= 540' idr_peaks.txt > reproducible_peaks.bed
```

## Related Skills

- read-alignment/bowtie2-alignment - Align ATAC-seq reads
- atac-seq/atac-qc - Quality control
- chip-seq/peak-calling - ChIP-seq comparison
- genome-intervals/bed-file-basics - Work with peak files
