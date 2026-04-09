# bio-chipseq-qc

> ChIP-seq quality control metrics including FRiP (Fraction of Reads in Peaks), cross-correlation analysis (NSC/RSC), library complexity, and IDR (Irreproducibility Discovery Rate) for replicate concordance. Use to assess experiment quality before downstream analysis. Use when assessing ChIP-seq data quality metrics.

## Version Compatibility

Reference examples tested with: MACS3 3.0+, Subread 2.0+, bedtools 2.31+, deepTools 3.5+, pybedtools 0.9+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# ChIP-seq Quality Control

**"Assess the quality of my ChIP-seq experiment"** → Compute FRiP, cross-correlation (NSC/RSC), library complexity, and IDR replicate concordance to evaluate enrichment success.
- CLI: `deeptools plotFingerprint`, `phantompeakqualtools run_spp.R`
- Python: `pysam` + `pybedtools` for custom QC metrics

Quality metrics for assessing ChIP-seq experiment success and replicate reproducibility.

## FRiP (Fraction of Reads in Peaks)

**Goal:** Quantify enrichment strength by measuring the proportion of reads falling within called peaks.

**Approach:** Count reads overlapping peak regions and divide by total mapped reads.

### Calculate FRiP with bedtools

```bash
# Count reads in peaks
reads_in_peaks=$(bedtools intersect -a chip.bam -b peaks.narrowPeak -u | samtools view -c -)
total_reads=$(samtools view -c -F 260 chip.bam)

# Calculate FRiP
frip=$(echo "scale=4; $reads_in_peaks / $total_reads" | bc)
echo "FRiP: $frip"
```

### Calculate FRiP with featureCounts

```bash
# Convert peaks to SAF format
awk 'BEGIN{OFS="\t"} {print $4, $1, $2, $3, "."}' peaks.narrowPeak > peaks.saf

# Count reads in peaks
featureCounts -a peaks.saf -F SAF -o peak_counts.txt chip.bam

# FRiP from summary
grep -v "^#" peak_counts.txt.summary
```

### Calculate FRiP with pysam

```python
import pysam
import pybedtools

def calculate_frip(bam_file, peak_file):
    bam = pysam.AlignmentFile(bam_file, 'rb')
    total_reads = bam.count(read_callback=lambda r: not r.is_unmapped and not r.is_secondary)

    peaks = pybedtools.BedTool(peak_file)
    reads_in_peaks = 0
    for peak in peaks:
        reads_in_peaks += bam.count(peak.chrom, peak.start, peak.end)

    frip = reads_in_peaks / total_reads
    return frip

frip = calculate_frip('chip.bam', 'peaks.narrowPeak')
print(f'FRiP: {frip:.4f}')
```

### FRiP Thresholds

| Target | Minimum FRiP | Good FRiP |
|--------|--------------|-----------|
| TF (narrow) | 0.01 | > 0.05 |
| Histone (broad) | 0.10 | > 0.20 |
| H3K4me3 | 0.05 | > 0.15 |
| H3K27ac | 0.05 | > 0.10 |

## Cross-Correlation Analysis (NSC/RSC)

**Goal:** Assess ChIP enrichment quality by measuring strand cross-correlation signal.

**Approach:** Calculate correlation between forward and reverse strand read coverage at varying shifts to detect fragment-length enrichment.

### Run phantompeakqualtools

```bash
# Run SPP cross-correlation analysis
Rscript run_spp.R \
    -c=chip.bam \
    -savp=chip_cc.pdf \
    -out=chip_cc.txt \
    -odir=qc/

# Output columns:
# 1: filename
# 2: numReads
# 3: estFragLen (estimated fragment length)
# 4: corr_estFragLen
# 5: phantomPeak
# 6: corr_phantomPeak
# 7: argmin_corr (minimum strand shift)
# 8: min_corr
# 9: NSC (Normalized Strand Coefficient)
# 10: RSC (Relative Strand Coefficient)
# 11: QualityTag
```

### Interpret NSC and RSC

```bash
# Parse results
awk -F'\t' '{
    print "Fragment length:", $3
    print "NSC:", $9
    print "RSC:", $10
    print "Quality:", $11
}' chip_cc.txt
```

### NSC/RSC Thresholds

| Metric | Marginal | Acceptable | Ideal |
|--------|----------|------------|-------|
| NSC | < 1.05 | 1.05 - 1.1 | > 1.1 |
| RSC | < 0.8 | 0.8 - 1.0 | > 1.0 |
| QualityTag | -2 | 0 | 1 or 2 |

### Plot Cross-Correlation in R

```r
library(spp)

chip_data <- read.bam.tags('chip.bam')
binding_characteristics <- get.binding.characteristics(chip_data, srange=c(50, 500), bin=5)

# Cross-correlation plot
pdf('cc_plot.pdf')
plot(binding_characteristics$cross.correlation, type='l',
     xlab='Strand shift', ylab='Cross-correlation')
abline(v=binding_characteristics$peak$x, col='red')
dev.off()

# Extract metrics
print(paste('Fragment length:', binding_characteristics$peak$x))
```

## Library Complexity (NRF, PBC1, PBC2)

**Goal:** Detect PCR amplification artifacts by measuring library complexity metrics.

**Approach:** Calculate the fraction of unique reads and positional redundancy to assess PCR bottlenecking.

### Calculate with bedtools

```bash
# NRF: Non-Redundant Fraction (unique reads / total reads)
total=$(samtools view -c -F 260 chip.bam)
unique=$(samtools view -F 260 chip.bam | cut -f1-4 | sort -u | wc -l)
nrf=$(echo "scale=4; $unique / $total" | bc)
echo "NRF: $nrf"

# PBC1: PCR Bottleneck Coefficient 1 (M1/Mdistinct)
# M1 = locations with exactly 1 read
# Mdistinct = distinct genomic locations

bedtools bamtobed -i chip.bam | \
    awk '{print $1":"$2"-"$3}' | \
    sort | uniq -c | \
    awk '{
        if($1==1) m1++
        mdist++
    } END {
        print "M1:", m1
        print "Mdistinct:", mdist
        print "PBC1:", m1/mdist
    }'
```

### Library Complexity Thresholds

| Metric | Severe | Mild | None |
|--------|--------|------|------|
| NRF | < 0.5 | 0.5 - 0.8 | > 0.8 |
| PBC1 | < 0.5 | 0.5 - 0.8 | > 0.8 |
| PBC2 | < 1 | 1 - 3 | > 3 |

## IDR (Irreproducibility Discovery Rate)

**Goal:** Assess replicate concordance by measuring consistency of ranked peak lists.

**Approach:** Compare signal-ranked peaks from two replicates using IDR statistical framework to identify reproducible peaks.

### Run IDR Analysis

```bash
# Call peaks on each replicate
macs3 callpeak -t rep1.bam -c input.bam -n rep1 -g hs
macs3 callpeak -t rep2.bam -c input.bam -n rep2 -g hs

# Sort by signal value (column 7)
sort -k7,7nr rep1_peaks.narrowPeak > rep1_sorted.narrowPeak
sort -k7,7nr rep2_peaks.narrowPeak > rep2_sorted.narrowPeak

# Run IDR
idr --samples rep1_sorted.narrowPeak rep2_sorted.narrowPeak \
    --input-file-type narrowPeak \
    --rank signal.value \
    --output-file idr_output.txt \
    --plot idr_plot.pdf \
    --log-output-file idr.log
```

### IDR with Pooled Peaks

```bash
# Call peaks on pooled data
samtools merge -f pooled.bam rep1.bam rep2.bam
macs3 callpeak -t pooled.bam -c input.bam -n pooled -g hs

# Run IDR with oracle
idr --samples rep1_sorted.narrowPeak rep2_sorted.narrowPeak \
    --peak-list pooled_peaks.narrowPeak \
    --input-file-type narrowPeak \
    --rank signal.value \
    --output-file idr_oracle.txt
```

### Interpret IDR Results

```bash
# Count peaks at different IDR thresholds
awk '$5 >= 540' idr_output.txt | wc -l  # IDR < 0.05 (conservative)
awk '$5 >= 415' idr_output.txt | wc -l  # IDR < 0.1 (optimal)

# IDR output columns:
# 1-3: chr, start, end
# 4: name
# 5: scaled IDR (-125 * log2(IDR))
# 6: strand
# 7: signal (from rep1)
# 8: signal (from rep2)
# 9: local IDR
# 10: global IDR
```

### IDR Self-Consistency Check

```bash
# Split one sample and check self-consistency
samtools view -s 0.5 chip.bam -b > pseudo_rep1.bam
samtools view -s 2.5 chip.bam -b > pseudo_rep2.bam

# Call peaks on pseudo-replicates
macs3 callpeak -t pseudo_rep1.bam -c input.bam -n pseudo1 -g hs
macs3 callpeak -t pseudo_rep2.bam -c input.bam -n pseudo2 -g hs

# Run IDR
idr --samples pseudo1_peaks.narrowPeak pseudo2_peaks.narrowPeak \
    --input-file-type narrowPeak \
    --output-file self_idr.txt
```

### IDR Quality Guidelines

| Comparison | Expected IDR Peaks | Notes |
|------------|-------------------|-------|
| True replicates | > 70% of pooled | Biological concordance |
| Pseudo-replicates | > 80% of sample | Technical consistency |
| Rep vs Pooled | ~100% of rep peaks | Subset relationship |

## deepTools QC Metrics

**Goal:** Visualize ChIP enrichment and sample correlation using deepTools fingerprint and correlation plots.

**Approach:** Generate cumulative read coverage curves and pairwise sample correlation matrices from BAM files.

### plotFingerprint

```bash
# Assess enrichment with fingerprint plot
plotFingerprint \
    -b chip.bam input.bam \
    --labels ChIP Input \
    -o fingerprint.pdf \
    --outRawCounts fingerprint.tab \
    --outQualityMetrics fingerprint_qc.txt

# Good ChIP shows curve shifted right of diagonal
# Input follows diagonal
```

### computeMatrix and plotProfile

```bash
# TSS enrichment
computeMatrix reference-point \
    -S chip.bw \
    -R genes.bed \
    --referencePoint TSS \
    -a 3000 -b 3000 \
    -o matrix.gz

plotProfile \
    -m matrix.gz \
    -o tss_enrichment.pdf \
    --perGroup
```

### plotCorrelation

```bash
# Sample correlation
multiBamSummary bins \
    -b rep1.bam rep2.bam rep3.bam \
    -o results.npz

plotCorrelation \
    -in results.npz \
    --corMethod spearman \
    --whatToPlot heatmap \
    -o correlation.pdf \
    --outFileCorMatrix correlation.tab
```

## Complete QC Pipeline

**Goal:** Run all major ChIP-seq QC metrics in a single automated script.

**Approach:** Combine FRiP, cross-correlation, library complexity, and fingerprint analysis into one pipeline.

```bash
#!/bin/bash
sample=$1
input=$2
peaks=$3

echo "=== ChIP-seq QC Report: $sample ===" > qc_report.txt

# FRiP
reads_in_peaks=$(bedtools intersect -a $sample -b $peaks -u | samtools view -c -)
total_reads=$(samtools view -c -F 260 $sample)
frip=$(echo "scale=4; $reads_in_peaks / $total_reads" | bc)
echo "FRiP: $frip" >> qc_report.txt

# Cross-correlation
Rscript run_spp.R -c=$sample -out=cc.txt -odir=.
nsc=$(cut -f9 cc.txt)
rsc=$(cut -f10 cc.txt)
echo "NSC: $nsc" >> qc_report.txt
echo "RSC: $rsc" >> qc_report.txt

# Library complexity
unique=$(samtools view -F 260 $sample | cut -f1-4 | sort -u | wc -l)
nrf=$(echo "scale=4; $unique / $total_reads" | bc)
echo "NRF: $nrf" >> qc_report.txt

# Fingerprint
plotFingerprint -b $sample $input -o fingerprint.pdf --outQualityMetrics fingerprint_qc.txt

cat qc_report.txt
```

## QC Summary Table

| Metric | Tool | Ideal Value |
|--------|------|-------------|
| FRiP | bedtools/featureCounts | > 0.05 (TF), > 0.1 (histone) |
| NSC | phantompeakqualtools | > 1.1 |
| RSC | phantompeakqualtools | > 1.0 |
| NRF | samtools/bedtools | > 0.8 |
| PBC1 | bedtools | > 0.8 |
| IDR (replicates) | idr | > 70% concordance |

## Related Skills

- peak-calling - Call peaks before QC analysis
- alignment-files - BAM statistics and filtering
- differential-binding - Compare conditions after QC
- atac-seq/atac-qc - Similar QC for ATAC-seq
