# bio-alignment-validation

> Validate alignment quality with insert size distribution, proper pairing rates, GC bias, strand balance, and other post-alignment metrics. Use when verifying alignment data quality before variant calling or quantification.

**Available tools:** Read, Bash

# Alignment Validation

Post-alignment quality control to verify alignment quality and identify issues.

## Insert Size Distribution

Insert size should match library preparation protocol.

### samtools stats

```bash
samtools stats input.bam > stats.txt
grep "^IS" stats.txt | cut -f2,3 > insert_sizes.txt
```

### Picard CollectInsertSizeMetrics

```bash
java -jar picard.jar CollectInsertSizeMetrics \
    I=input.bam \
    O=insert_metrics.txt \
    H=insert_histogram.pdf
```

### Expected Insert Sizes

| Library Type | Expected Size |
|--------------|---------------|
| Standard WGS | 300-500 bp |
| PCR-free | 350-550 bp |
| RNA-seq | 150-300 bp |
| ChIP-seq | 150-300 bp |
| ATAC-seq | Multimodal |

### Python Insert Size Analysis

```python
import pysam
import numpy as np
import matplotlib.pyplot as plt

def get_insert_sizes(bam_file, max_reads=100000):
    sizes = []
    bam = pysam.AlignmentFile(bam_file, 'rb')
    for i, read in enumerate(bam.fetch()):
        if i >= max_reads:
            break
        if read.is_proper_pair and not read.is_secondary and read.template_length > 0:
            sizes.append(read.template_length)
    bam.close()
    return sizes

sizes = get_insert_sizes('sample.bam')
print(f'Median insert size: {np.median(sizes):.0f}')
print(f'Mean insert size: {np.mean(sizes):.0f}')
print(f'Std dev: {np.std(sizes):.0f}')

plt.hist(sizes, bins=100, range=(0, 1000))
plt.xlabel('Insert Size')
plt.ylabel('Count')
plt.savefig('insert_size_dist.pdf')
```

## Proper Pairing Rate

Percentage of reads correctly paired.

### samtools flagstat

```bash
samtools flagstat input.bam

samtools flagstat input.bam | grep "properly paired"
```

### Calculate Pairing Rate

```bash
proper=$(samtools view -c -f 2 input.bam)
mapped=$(samtools view -c -F 4 input.bam)
rate=$(echo "scale=4; $proper / $mapped * 100" | bc)
echo "Proper pairing rate: ${rate}%"
```

### Expected Rates

| Metric | Good | Marginal | Poor |
|--------|------|----------|------|
| Proper pair | > 90% | 80-90% | < 80% |
| Mapped | > 95% | 90-95% | < 90% |
| Singletons | < 5% | 5-10% | > 10% |

## GC Bias

GC content correlation with coverage.

### Picard CollectGcBiasMetrics

```bash
java -jar picard.jar CollectGcBiasMetrics \
    I=input.bam \
    O=gc_bias_metrics.txt \
    CHART=gc_bias_chart.pdf \
    S=gc_summary.txt \
    R=reference.fa
```

### deepTools computeGCBias

```bash
computeGCBias \
    -b input.bam \
    --effectiveGenomeSize 2913022398 \
    -g hg38.2bit \
    -o gc_bias.txt \
    --biasPlot gc_bias.pdf
```

### Interpret GC Bias

| Issue | Symptom |
|-------|---------|
| Under-representation | Low GC coverage drops |
| Over-representation | High GC coverage elevated |
| PCR bias | Strong correlation |

## Strand Balance

Forward and reverse strand should be balanced.

### Calculate Strand Ratio

```bash
forward=$(samtools view -c -F 16 input.bam)
reverse=$(samtools view -c -f 16 input.bam)
echo "Forward: $forward"
echo "Reverse: $reverse"
ratio=$(echo "scale=4; $forward / $reverse" | bc)
echo "F/R ratio: $ratio"
```

### Check Strand Bias per Chromosome

```bash
for chr in chr1 chr2 chr3; do
    fwd=$(samtools view -c -F 16 input.bam $chr)
    rev=$(samtools view -c -f 16 input.bam $chr)
    echo "$chr: F=$fwd R=$rev ratio=$(echo "scale=2; $fwd/$rev" | bc)"
done
```

## Mapping Quality Distribution

### Extract MAPQ Distribution

```bash
samtools view input.bam | cut -f5 | sort -n | uniq -c | sort -k2 -n
```

### Calculate Mean MAPQ

```bash
samtools view input.bam | awk '{sum+=$5; count++} END {print "Mean MAPQ:", sum/count}'
```

### MAPQ Thresholds

| MAPQ | Meaning |
|------|---------|
| 0 | Multi-mapper |
| 1-10 | Low confidence |
| 20-30 | Moderate |
| 40+ | High confidence |
| 60 | Unique (BWA) |

## Chromosome Coverage Balance

### Calculate Per-Chromosome Coverage

```bash
samtools idxstats input.bam | awk '{print $1, $3/$2}' | head -25
```

### Check for Aneuploidy/Contamination

```bash
samtools idxstats input.bam | awk '$3 > 0 {
    sum += $3
    len[$1] = $2
    reads[$1] = $3
} END {
    for (chr in reads) {
        expected = len[chr] / sum * reads[chr]
        ratio = reads[chr] / expected
        if (ratio < 0.8 || ratio > 1.2) print chr, ratio
    }
}'
```

## Mismatch Rate

### Picard CollectAlignmentSummaryMetrics

```bash
java -jar picard.jar CollectAlignmentSummaryMetrics \
    I=input.bam \
    R=reference.fa \
    O=alignment_summary.txt
```

### Key Metrics

| Metric | Description | Good Value |
|--------|-------------|------------|
| PCT_PF_READS_ALIGNED | Mapped % | > 95% |
| PF_MISMATCH_RATE | Mismatches | < 1% |
| PF_INDEL_RATE | Indels | < 0.1% |
| STRAND_BALANCE | Strand ratio | ~0.5 |

## Comprehensive Validation Script

```bash
#!/bin/bash
BAM=$1
REF=$2
NAME=$(basename $BAM .bam)
OUTDIR=${3:-qc}

mkdir -p $OUTDIR

echo "=== Alignment Validation: $NAME ===" | tee $OUTDIR/report.txt

echo -e "\n--- Flagstat ---" | tee -a $OUTDIR/report.txt
samtools flagstat $BAM | tee -a $OUTDIR/report.txt

echo -e "\n--- Mapping Rate ---" | tee -a $OUTDIR/report.txt
mapped=$(samtools view -c -F 4 $BAM)
total=$(samtools view -c $BAM)
rate=$(echo "scale=2; $mapped / $total * 100" | bc)
echo "Mapping rate: ${rate}%" | tee -a $OUTDIR/report.txt

echo -e "\n--- Proper Pairing ---" | tee -a $OUTDIR/report.txt
proper=$(samtools view -c -f 2 $BAM)
pair_rate=$(echo "scale=2; $proper / $mapped * 100" | bc)
echo "Proper pairing: ${pair_rate}%" | tee -a $OUTDIR/report.txt

echo -e "\n--- Insert Size ---" | tee -a $OUTDIR/report.txt
samtools stats $BAM | grep "insert size average" | tee -a $OUTDIR/report.txt

echo -e "\n--- Strand Balance ---" | tee -a $OUTDIR/report.txt
fwd=$(samtools view -c -F 16 $BAM)
rev=$(samtools view -c -f 16 $BAM)
strand_ratio=$(echo "scale=3; $fwd / $rev" | bc)
echo "Forward: $fwd, Reverse: $rev, Ratio: $strand_ratio" | tee -a $OUTDIR/report.txt

echo -e "\n--- Chromosome Coverage ---" | tee -a $OUTDIR/report.txt
samtools idxstats $BAM | head -25 | tee -a $OUTDIR/report.txt

echo -e "\nReport: $OUTDIR/report.txt"
```

## Python Validation Module

```python
import pysam
import numpy as np
from collections import Counter

class AlignmentValidator:
    def __init__(self, bam_file):
        self.bam = pysam.AlignmentFile(bam_file, 'rb')

    def mapping_rate(self):
        stats = self.bam.get_index_statistics()
        mapped = sum(s.mapped for s in stats)
        unmapped = sum(s.unmapped for s in stats)
        return mapped / (mapped + unmapped) * 100

    def proper_pair_rate(self, sample_size=100000):
        proper = 0
        paired = 0
        for i, read in enumerate(self.bam.fetch()):
            if i >= sample_size:
                break
            if read.is_paired:
                paired += 1
                if read.is_proper_pair:
                    proper += 1
        return proper / paired * 100 if paired > 0 else 0

    def mapq_distribution(self, sample_size=100000):
        mapqs = []
        for i, read in enumerate(self.bam.fetch()):
            if i >= sample_size:
                break
            if not read.is_unmapped:
                mapqs.append(read.mapping_quality)
        return Counter(mapqs)

    def strand_balance(self, sample_size=100000):
        forward = 0
        reverse = 0
        for i, read in enumerate(self.bam.fetch()):
            if i >= sample_size:
                break
            if not read.is_unmapped:
                if read.is_reverse:
                    reverse += 1
                else:
                    forward += 1
        return forward / (forward + reverse) if (forward + reverse) > 0 else 0.5

    def report(self):
        print(f'Mapping rate: {self.mapping_rate():.1f}%')
        print(f'Proper pairing: {self.proper_pair_rate():.1f}%')
        print(f'Strand balance: {self.strand_balance():.3f}')

        mapq_dist = self.mapq_distribution()
        high_qual = sum(v for k, v in mapq_dist.items() if k >= 30)
        total = sum(mapq_dist.values())
        print(f'High MAPQ (>=30): {high_qual/total*100:.1f}%')

    def close(self):
        self.bam.close()

validator = AlignmentValidator('sample.bam')
validator.report()
validator.close()
```

## Quality Thresholds Summary

| Metric | Good | Warning | Fail |
|--------|------|---------|------|
| Mapping rate | > 95% | 90-95% | < 90% |
| Proper pairing | > 90% | 80-90% | < 80% |
| Duplicate rate | < 10% | 10-20% | > 20% |
| Strand balance | 0.48-0.52 | 0.45-0.55 | Outside |
| Mean MAPQ | > 40 | 30-40 | < 30 |
| GC bias | < 1.2x | 1.2-1.5x | > 1.5x |

## Related Skills

- bam-statistics - Basic flagstat and depth
- duplicate-handling - Mark/remove duplicates
- alignment-filtering - Filter low-quality reads
- chip-seq/chipseq-qc - ChIP-specific metrics
