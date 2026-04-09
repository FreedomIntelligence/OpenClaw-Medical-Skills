# bio-atac-seq-footprinting

> Detect transcription factor binding sites through footprinting analysis in ATAC-seq data using TOBIAS. Use when identifying TF occupancy patterns within accessible regions, as TF binding protects DNA from Tn5 cutting.

## Version Compatibility

Reference examples tested with: bedtools 2.31+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, pyBigWig 0.3+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# TF Footprinting

**"Identify TF binding footprints in my ATAC-seq data"** → Detect protected DNA regions within accessible chromatin where bound transcription factors block Tn5 insertion.
- CLI: `TOBIAS ATACorrect` → `TOBIAS FootprintScores` → `TOBIAS BINDetect`

## TOBIAS Workflow

**Goal:** Identify transcription factor binding footprints within accessible chromatin regions.

**Approach:** Correct Tn5 insertion bias, compute per-base footprint scores, then detect bound/unbound TF motif sites using the three-step TOBIAS pipeline.

```bash
# 1. Correct Tn5 bias
tobias ATACorrect \
    --bam sample.bam \
    --genome genome.fa \
    --peaks peaks.bed \
    --outdir corrected/ \
    --cores 8

# 2. Calculate footprint scores
tobias FootprintScores \
    --signal corrected/sample_corrected.bw \
    --regions peaks.bed \
    --output footprints.bw \
    --cores 8

# 3. Bind TF motifs
tobias BINDetect \
    --motifs JASPAR_motifs.pfm \
    --signals footprints.bw \
    --genome genome.fa \
    --peaks peaks.bed \
    --outdir bindetect_output/ \
    --cores 8
```

## TOBIAS Differential Footprinting

**Goal:** Compare TF binding between two conditions to identify regulators with differential activity.

**Approach:** Provide two bias-corrected signal tracks to BINDetect, which scores each motif site for differential binding between conditions.

```bash
# Compare conditions
tobias BINDetect \
    --motifs JASPAR_motifs.pfm \
    --signals condition1.bw condition2.bw \
    --genome genome.fa \
    --peaks consensus_peaks.bed \
    --outdir differential_footprints/ \
    --cond_names condition1 condition2 \
    --cores 8

# Output includes:
# - Differential binding scores
# - Per-TF statistics
# - Bound/unbound site predictions
```

## Download JASPAR Motifs

```bash
# Download JASPAR motifs
wget https://jaspar.genereg.net/download/data/2022/CORE/JASPAR2022_CORE_vertebrates_non-redundant_pfms_jaspar.txt
mv JASPAR2022_CORE_vertebrates_non-redundant_pfms_jaspar.txt JASPAR_motifs.pfm
```

## Prepare Input Files

```bash
# Ensure BAM is sorted and indexed
samtools sort -@ 8 sample.bam -o sample.sorted.bam
samtools index sample.sorted.bam

# Filter peaks (remove blacklist, size filter)
bedtools intersect -v -a peaks.narrowPeak -b blacklist.bed | \
    awk '$3-$2 >= 100 && $3-$2 <= 5000' > filtered_peaks.bed
```

## HINT-ATAC Alternative

```bash
# RGT suite HINT-ATAC
rgt-hint footprinting \
    --atac-seq \
    --organism hg38 \
    --output-prefix sample \
    sample.bam peaks.bed
```

## PIQ Footprinting

```r
# PIQ (another footprinting tool)
library(PIQ)

# Load data
bam <- 'sample.bam'
pwms <- readMotifs('JASPAR_motifs.pfm')

# Run footprinting
piq_results <- piq(bam, pwms, genome='hg38')
```

## Aggregate Footprint Plots

```bash
# TOBIAS PlotAggregate
tobias PlotAggregate \
    --TFBS bindetect_output/*/beds/*_bound.bed \
    --signals corrected/sample_corrected.bw \
    --output aggregate_footprints.pdf \
    --share_y \
    --plot_boundaries
```

## Python: Custom Footprint Analysis

**Goal:** Extract and visualize aggregate ATAC-seq signal around predicted TF binding sites.

**Approach:** Sample bigWig signal values in windows centered on motif sites, average across all sites, and plot the characteristic V-shaped footprint.

```python
import pyBigWig
import numpy as np
import pandas as pd
from pyfaidx import Fasta

def extract_footprint_signal(bigwig_file, bed_file, flank=100):
    '''Extract signal around binding sites.'''
    bw = pyBigWig.open(bigwig_file)

    signals = []
    for line in open(bed_file):
        fields = line.strip().split('\t')
        chrom, start, end = fields[0], int(fields[1]), int(fields[2])
        center = (start + end) // 2

        try:
            vals = bw.values(chrom, center - flank, center + flank)
            if vals:
                signals.append(vals)
        except:
            continue

    avg_signal = np.nanmean(signals, axis=0)
    return avg_signal

def plot_footprint(signal, output_file):
    '''Plot aggregate footprint.'''
    import matplotlib.pyplot as plt

    x = np.arange(-len(signal)//2, len(signal)//2)

    plt.figure(figsize=(8, 4))
    plt.plot(x, signal, 'b-', linewidth=2)
    plt.axvline(0, color='red', linestyle='--', alpha=0.5)
    plt.xlabel('Distance from motif center (bp)')
    plt.ylabel('ATAC-seq signal')
    plt.title('Aggregate Footprint')
    plt.savefig(output_file, dpi=150)
    plt.close()
```

## Scan for Motifs

```bash
# Find motif occurrences in peaks
# Using FIMO (MEME suite)
fimo --oc fimo_output motifs.meme peaks.fa

# Or HOMER
findMotifsGenome.pl peaks.bed hg38 motif_analysis/ -find motif.motif
```

## Interpret Footprint Depth

| Footprint Depth | Interpretation |
|-----------------|----------------|
| Deep footprint | Strong TF binding |
| Shallow footprint | Weak/transient binding |
| No footprint | No binding or wrong motif |
| Shoulders only | Nucleosome positioning |

## Quality Considerations

```bash
# Footprinting requires:
# - High read depth (>50M reads)
# - NFR-enriched signal (filter for <100bp fragments)
# - Good Tn5 bias correction

# Extract NFR reads
samtools view -h sample.bam | \
    awk 'substr($0,1,1)=="@" || ($9>0 && $9<100) || ($9<0 && $9>-100)' | \
    samtools view -b > nfr.bam
```

## Differential TF Activity

```python
def compare_footprints(tf_name, cond1_bw, cond2_bw, motif_bed):
    '''Compare TF footprints between conditions.'''
    sig1 = extract_footprint_signal(cond1_bw, motif_bed)
    sig2 = extract_footprint_signal(cond2_bw, motif_bed)

    # Calculate footprint depth
    depth1 = np.nanmean(sig1[:30]) - np.nanmin(sig1[40:60])
    depth2 = np.nanmean(sig2[:30]) - np.nanmin(sig2[40:60])

    diff = depth2 - depth1

    return {
        'TF': tf_name,
        'depth_cond1': depth1,
        'depth_cond2': depth2,
        'difference': diff
    }
```

## TOBIAS Output Files

| File | Description |
|------|-------------|
| *_corrected.bw | Bias-corrected signal |
| *_footprints.bw | Footprint scores |
| *_bound.bed | Predicted bound sites |
| *_unbound.bed | Predicted unbound sites |
| *_overview.txt | Per-TF statistics |

## Related Skills

- atac-seq/atac-peak-calling - Generate peaks
- atac-seq/atac-qc - Verify data quality
- chip-seq/peak-annotation - Annotate binding sites
- sequence-manipulation/motif-search - Find motifs
