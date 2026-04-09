# bio-atac-seq-atac-qc

> Quality control metrics for ATAC-seq data including fragment size distribution, TSS enrichment, FRiP, and library complexity. Use when assessing ATAC-seq library quality before or after peak calling to identify problematic samples.

## Version Compatibility

Reference examples tested with: bedtools 2.31+, deepTools 3.5+, numpy 1.26+, pandas 2.2+, picard 3.1+, pyBigWig 0.3+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# ATAC-seq Quality Control

**"Check the quality of my ATAC-seq library"** → Evaluate fragment size distribution (nucleosome periodicity), TSS enrichment, FRiP, and library complexity to assess chromatin accessibility experiment quality.
- CLI: `deeptools bamPEFragmentSize`, `picard CollectInsertSizeMetrics`
- Python: `pysam` for custom fragment analysis

## Fragment Size Distribution

**Goal:** Assess ATAC-seq library quality by visualizing the characteristic nucleosome periodicity in fragment sizes.

**Approach:** Extract insert sizes from the BAM file using Picard or samtools, producing a distribution that should show NFR (<100 bp) and mono-nucleosome (~200 bp) peaks.

```bash
# Using Picard
java -jar picard.jar CollectInsertSizeMetrics \
    I=sample.bam \
    O=insert_sizes.txt \
    H=insert_sizes.pdf \
    M=0.5

# Using samtools
samtools view -f 66 sample.bam | \
    awk '{print sqrt($9^2)}' | \
    sort | uniq -c | \
    awk '{print $2"\t"$1}' > fragment_sizes.txt
```

## TSS Enrichment Score

**Goal:** Quantify signal enrichment at transcription start sites as a key ATAC-seq quality metric.

**Approach:** Create a TSS BED file, compute a signal matrix around TSS positions using deepTools, then plot the enrichment profile.

```bash
# Using deepTools
# 1. Create TSS BED file (from GTF)
awk '$3=="transcript" {print $1"\t"$4-1"\t"$4"\t"$14"\t"0"\t"$7}' genes.gtf | \
    tr -d '";' | sort -k1,1 -k2,2n > tss.bed

# 2. Compute matrix around TSS
computeMatrix reference-point \
    -S sample.bw \
    -R tss.bed \
    -a 2000 -b 2000 \
    -o tss_matrix.gz

# 3. Plot TSS enrichment
plotProfile -m tss_matrix.gz \
    -o tss_enrichment.png \
    --perGroup
```

## Calculate TSS Enrichment Score

**Goal:** Compute a numeric TSS enrichment score from a bigWig signal track.

**Approach:** Sample signal values in windows around TSS positions, average across all TSSs, then divide center signal by flanking background.

```python
import numpy as np
import pyBigWig

def calculate_tss_enrichment(bigwig_file, tss_bed, flank=2000):
    '''Calculate TSS enrichment score.'''
    bw = pyBigWig.open(bigwig_file)

    signals = []
    for line in open(tss_bed):
        fields = line.strip().split('\t')
        chrom, tss = fields[0], int(fields[1])
        strand = fields[5] if len(fields) > 5 else '+'

        try:
            vals = bw.values(chrom, max(0, tss - flank), tss + flank)
            if strand == '-':
                vals = vals[::-1]
            signals.append(vals)
        except:
            continue

    avg_signal = np.nanmean(signals, axis=0)

    # TSS enrichment = signal at TSS / background
    background = np.nanmean([avg_signal[:100], avg_signal[-100:]])
    tss_signal = np.nanmean(avg_signal[flank-50:flank+50])

    enrichment = tss_signal / background if background > 0 else 0

    return enrichment, avg_signal

enrichment, signal = calculate_tss_enrichment('sample.bw', 'tss.bed')
print(f'TSS Enrichment Score: {enrichment:.2f}')
```

## FRiP (Fraction of Reads in Peaks)

```bash
# Total reads
total=$(samtools view -c -F 4 sample.bam)

# Reads in peaks
in_peaks=$(bedtools intersect -a sample.bam -b peaks.narrowPeak -u | \
    samtools view -c)

# FRiP
frip=$(echo "scale=4; $in_peaks / $total" | bc)
echo "FRiP: $frip"

# Good FRiP for ATAC-seq: >0.2 (20%)
```

## Mitochondrial Read Fraction

```bash
# Mitochondrial reads
mt_reads=$(samtools view -c sample.bam chrM)
total_reads=$(samtools view -c sample.bam)

mt_frac=$(echo "scale=4; $mt_reads / $total_reads" | bc)
echo "Mitochondrial fraction: $mt_frac"

# Ideal: <20%, concerning: >50%
```

## Library Complexity (NRF, PBC1, PBC2)

**Goal:** Measure library complexity to detect over-amplification or low-diversity libraries.

**Approach:** Calculate NRF (unique/total reads), PBC1 (1-read locations / all locations), and PBC2 (1-read / 2-read locations) using Picard or custom counting.

```bash
# Using Picard EstimateLibraryComplexity
java -jar picard.jar EstimateLibraryComplexity \
    I=sample.bam \
    O=complexity.txt

# Or calculate from BAM
# NRF = unique reads / total reads
# PBC1 = locations with exactly 1 read / locations with >= 1 read
# PBC2 = locations with exactly 1 read / locations with exactly 2 reads
```

```python
import pysam

def calculate_complexity(bam_file):
    '''Calculate library complexity metrics.'''
    bam = pysam.AlignmentFile(bam_file, 'rb')

    positions = {}
    total = 0
    for read in bam.fetch():
        if read.is_unmapped or read.is_secondary:
            continue
        total += 1
        pos = (read.reference_name, read.reference_start)
        positions[pos] = positions.get(pos, 0) + 1

    distinct = len(positions)
    m1 = sum(1 for v in positions.values() if v == 1)
    m2 = sum(1 for v in positions.values() if v == 2)

    nrf = distinct / total if total > 0 else 0
    pbc1 = m1 / distinct if distinct > 0 else 0
    pbc2 = m1 / m2 if m2 > 0 else 0

    return {'NRF': nrf, 'PBC1': pbc1, 'PBC2': pbc2}
```

## deepTools QC

```bash
# Fingerprint plot (assesses enrichment)
plotFingerprint \
    -b sample.bam \
    --labels sample \
    -o fingerprint.png

# Correlation between replicates
multiBamSummary bins \
    -b sample1.bam sample2.bam \
    -o results.npz

plotCorrelation \
    -in results.npz \
    --corMethod pearson \
    --whatToPlot heatmap \
    -o correlation.png
```

## ATACseqQC (R)

```r
library(ATACseqQC)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

# Read BAM
bamfile <- 'sample.bam'

# Fragment size distribution
fragSizeDist(bamfile, 'fragment_size.pdf')

# TSS enrichment
tsse <- TSSEscore(bamfile, TxDb.Hsapiens.UCSC.hg38.knownGene)
print(paste('TSS Enrichment:', round(tsse$TSSEscore, 2)))

# Nucleosome positioning
nucs <- nucleosomePositioningScore(bamfile, TxDb.Hsapiens.UCSC.hg38.knownGene)
```

## Comprehensive QC Report

**Goal:** Generate a single QC summary combining all major ATAC-seq quality metrics.

**Approach:** Run samtools and bedtools commands to collect total reads, mapping rate, mitochondrial fraction, FRiP, and peak count, then write a consolidated report.

```python
import subprocess
import pandas as pd

def atac_qc_report(bam_file, peaks_file, output_prefix):
    '''Generate comprehensive ATAC-seq QC report.'''
    metrics = {}

    # Total reads
    result = subprocess.check_output(f'samtools view -c -F 4 {bam_file}', shell=True)
    metrics['total_reads'] = int(result.strip())

    # Mapped reads
    result = subprocess.check_output(f'samtools view -c -F 4 -F 256 {bam_file}', shell=True)
    metrics['mapped_reads'] = int(result.strip())

    # Mitochondrial reads
    result = subprocess.check_output(f'samtools view -c {bam_file} chrM', shell=True)
    metrics['mt_reads'] = int(result.strip())
    metrics['mt_fraction'] = metrics['mt_reads'] / metrics['total_reads']

    # Reads in peaks (FRiP)
    result = subprocess.check_output(
        f'bedtools intersect -a {bam_file} -b {peaks_file} -u | samtools view -c', shell=True)
    metrics['reads_in_peaks'] = int(result.strip())
    metrics['frip'] = metrics['reads_in_peaks'] / metrics['total_reads']

    # Peak count
    result = subprocess.check_output(f'wc -l < {peaks_file}', shell=True)
    metrics['peak_count'] = int(result.strip())

    # Write report
    with open(f'{output_prefix}_qc.txt', 'w') as f:
        for k, v in metrics.items():
            if isinstance(v, float):
                f.write(f'{k}: {v:.4f}\n')
            else:
                f.write(f'{k}: {v}\n')

    return metrics
```

## QC Thresholds

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| TSS Enrichment | >10 | 5-10 | <5 |
| FRiP | >0.3 | 0.1-0.3 | <0.1 |
| MT Fraction | <0.1 | 0.1-0.3 | >0.3 |
| NRF | >0.9 | 0.8-0.9 | <0.8 |
| PBC1 | >0.9 | 0.7-0.9 | <0.7 |

## Related Skills

- atac-seq/atac-peak-calling - Peak calling
- alignment-files/bam-statistics - Alignment QC
- chip-seq/chipseq-visualization - Visualization approaches
