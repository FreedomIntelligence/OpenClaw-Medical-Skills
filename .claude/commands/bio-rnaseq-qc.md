# bio-rnaseq-qc

> RNA-seq specific quality control including rRNA contamination detection, strandedness verification, gene body coverage, and transcript integrity metrics. Use when validating RNA-seq libraries before differential expression analysis.

## Version Compatibility

Reference examples tested with: NCBI BLAST+ 2.15+, numpy 1.26+, picard 3.1+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# RNA-seq Quality Control

RNA-seq specific QC metrics beyond general read quality.

**"Check RNA-seq alignment quality"** → Assess gene body coverage, read distribution (exonic/intronic/intergenic), strand specificity, and rRNA contamination rate.
- CLI: `infer_experiment.py`, `read_distribution.py` (RSeQC)
- CLI: `picard CollectRnaSeqMetrics`

## rRNA Contamination Detection

High rRNA content indicates failed rRNA depletion or polyA selection.

### SortMeRNA (NCBI BLAST+)

```bash
sortmerna \
    --ref rRNA_databases/smr_v4.3_default_db.fasta \
    --reads sample.fastq.gz \
    --aligned rRNA_reads \
    --other non_rRNA_reads \
    --fastx \
    --threads 8

rrna_count=$(grep -c "^@" rRNA_reads.fastq 2>/dev/null || echo 0)
total_count=$(zcat sample.fastq.gz | grep -c "^@")
rrna_pct=$(echo "scale=2; $rrna_count / $total_count * 100" | bc)
echo "rRNA: ${rrna_pct}%"
```

### BLAST Against rRNA (NCBI BLAST+)

```bash
seqkit sample -n 10000 sample.fastq.gz | seqkit fq2fa > sample_10k.fasta
blastn -query sample_10k.fasta -db rrna_db -outfmt 6 -evalue 1e-10 -max_target_seqs 1 | wc -l
```

### Expected rRNA Levels

| Library Type | Expected rRNA |
|--------------|---------------|
| PolyA selected | < 5% |
| rRNA depleted | < 10% |
| Total RNA | 50-80% |

## Strandedness Verification

### RSeQC infer_experiment (NCBI BLAST+)

```bash
infer_experiment.py -i aligned.bam -r genes.bed
```

### Output Interpretation

```
Fraction of reads explained by "1++,1--,2+-,2-+": 0.9856  # Forward stranded
Fraction of reads explained by "1+-,1-+,2++,2--": 0.0144  # Reverse (should be low)
```

### Strand Inference

| Tool Setting | 1++,1--,2+-,2-+ | 1+-,1-+,2++,2-- |
|--------------|-----------------|-----------------|
| Forward (dUTP) | ~0 | ~1 |
| Reverse (Illumina) | ~1 | ~0 |
| Unstranded | ~0.5 | ~0.5 |

### Salmon Strandedness (NCBI BLAST+)

```bash
salmon quant -i index -l A -r sample.fastq.gz -o quant/
grep "library_types" quant/lib_format_counts.json
```

## Gene Body Coverage

Check for 3' or 5' bias indicating RNA degradation.

### RSeQC geneBody_coverage (NCBI BLAST+)

```bash
geneBody_coverage.py \
    -i aligned.bam \
    -r housekeeping_genes.bed \
    -o coverage
```

### Interpretation

| Pattern | Indicates |
|---------|-----------|
| Even coverage | Good quality |
| 3' bias | Degradation or polyA artifacts |
| 5' bias | Incomplete reverse transcription |
| Steep drop | Severe degradation |

## Read Distribution

### RSeQC read_distribution (NCBI BLAST+)

```bash
read_distribution.py -i aligned.bam -r genes.bed > distribution.txt
```

### Expected Distribution

| Region | Good Library |
|--------|--------------|
| CDS_Exons | 60-80% |
| UTRs | 10-20% |
| Introns | 5-20% |
| Intergenic | < 10% |

## Transcript Integrity Number (TIN)

Measure of RNA degradation per transcript.

### RSeQC tin (NCBI BLAST+)

```bash
tin.py -i aligned.bam -r genes.bed > tin_scores.txt
```

### TIN Interpretation

| TIN Score | Quality |
|-----------|---------|
| > 70 | Good |
| 50-70 | Moderate |
| < 50 | Poor |

## Duplication Rate

### Picard MarkDuplicates (NCBI BLAST+)

```bash
java -jar picard.jar MarkDuplicates \
    I=aligned.bam \
    O=marked.bam \
    M=dup_metrics.txt \
    REMOVE_DUPLICATES=false

grep -A 1 "LIBRARY" dup_metrics.txt | tail -1 | cut -f9
```

### RNA-seq Expected Duplication

| Library | Expected |
|---------|----------|
| High complexity | < 20% |
| Low input | 20-50% |
| Concerning | > 50% |

## Insert Size (Paired-End)

### Picard CollectInsertSizeMetrics (NCBI BLAST+)

```bash
java -jar picard.jar CollectInsertSizeMetrics \
    I=aligned.bam \
    O=insert_metrics.txt \
    H=insert_histogram.pdf
```

## Saturation Analysis

### Subsampling Analysis

```bash
for frac in 0.1 0.25 0.5 0.75 1.0; do
    samtools view -bs $frac aligned.bam > sub_${frac}.bam
    featureCounts -a genes.gtf -o counts_${frac}.txt sub_${frac}.bam
    detected=$(awk '$7 > 0' counts_${frac}.txt | wc -l)
    echo "$frac: $detected genes"
done
```

## Picard CollectRnaSeqMetrics

Comprehensive RNA-seq metrics from Picard.

```bash
java -jar picard.jar CollectRnaSeqMetrics \
    I=aligned.bam \
    O=rnaseq_metrics.txt \
    REF_FLAT=refFlat.txt \
    STRAND=SECOND_READ_TRANSCRIPTION_STRAND \
    RIBOSOMAL_INTERVALS=rRNA.interval_list
```

### Key Metrics

| Metric | Description |
|--------|-------------|
| PCT_CODING_BASES | % in coding regions |
| PCT_UTR_BASES | % in UTRs |
| PCT_INTRONIC_BASES | % in introns |
| PCT_INTERGENIC_BASES | % intergenic |
| PCT_RIBOSOMAL_BASES | % rRNA |
| MEDIAN_5PRIME_TO_3PRIME_BIAS | 3' bias |

## MultiQC Report

Aggregate all QC metrics.

```bash
multiqc fastqc/ star_output/ featurecounts/ -o multiqc_report/
```

## Complete RNA-seq QC Pipeline (NCBI BLAST+)

**Goal:** Generate a comprehensive RNA-seq QC report covering strandedness, read distribution, gene body coverage, transcript integrity, duplication, and RNA-seq metrics.

**Approach:** Run RSeQC tools (infer_experiment, read_distribution, geneBody_coverage, TIN) and Picard (MarkDuplicates, CollectRnaSeqMetrics) sequentially, appending all results to a single summary report file.

```bash
#!/bin/bash
SAMPLE=$1
BAM=$2
GENES_BED=$3
REF_FLAT=$4

echo "=== RNA-seq QC: $SAMPLE ===" > qc_report.txt

echo -e "\n--- Strandedness ---" >> qc_report.txt
infer_experiment.py -i $BAM -r $GENES_BED >> qc_report.txt

echo -e "\n--- Read Distribution ---" >> qc_report.txt
read_distribution.py -i $BAM -r $GENES_BED >> qc_report.txt

echo -e "\n--- Gene Body Coverage ---" >> qc_report.txt
geneBody_coverage.py -i $BAM -r $GENES_BED -o coverage

echo -e "\n--- TIN Scores ---" >> qc_report.txt
tin.py -i $BAM -r $GENES_BED > tin.txt
awk '{sum+=$3; count++} END {print "Mean TIN:", sum/count}' tin.txt >> qc_report.txt

echo -e "\n--- Duplication ---" >> qc_report.txt
java -jar picard.jar MarkDuplicates I=$BAM O=/dev/null M=dup.txt 2>/dev/null
grep -A 1 "LIBRARY" dup.txt | tail -1 | awk '{print "Duplication rate:", $9}' >> qc_report.txt

echo -e "\n--- RNA-seq Metrics ---" >> qc_report.txt
java -jar picard.jar CollectRnaSeqMetrics I=$BAM O=rnaseq.txt REF_FLAT=$REF_FLAT STRAND=SECOND_READ_TRANSCRIPTION_STRAND 2>/dev/null
grep -A 2 "## METRICS CLASS" rnaseq.txt >> qc_report.txt

cat qc_report.txt
```

## Python QC Summary

```python
import pysam
import numpy as np
from collections import Counter

def rnaseq_qc(bam_file, sample_size=100000):
    bam = pysam.AlignmentFile(bam_file, 'rb')

    strand_counts = Counter()
    insert_sizes = []

    for i, read in enumerate(bam.fetch()):
        if i >= sample_size:
            break
        if not read.is_unmapped:
            if read.is_read1:
                if read.is_reverse:
                    strand_counts['1-'] += 1
                else:
                    strand_counts['1+'] += 1
            if read.is_proper_pair and read.template_length > 0:
                insert_sizes.append(read.template_length)

    bam.close()

    total = sum(strand_counts.values())
    print(f'Read 1 forward: {strand_counts["1+"]/total:.2%}')
    print(f'Read 1 reverse: {strand_counts["1-"]/total:.2%}')

    if insert_sizes:
        print(f'Median insert: {np.median(insert_sizes):.0f}')

rnaseq_qc('aligned.bam')
```

## QC Thresholds Summary

| Metric | Good | Warning | Fail |
|--------|------|---------|------|
| Mapping rate | > 85% | 70-85% | < 70% |
| rRNA % | < 10% | 10-20% | > 20% |
| Exonic % | > 60% | 40-60% | < 40% |
| Duplication | < 20% | 20-40% | > 40% |
| Mean TIN | > 70 | 50-70 | < 50 |
| 3' bias | < 1.5 | 1.5-2 | > 2 |

## Related Skills

- quality-reports - General FastQC
- fastp-workflow - Read trimming
- alignment-files/alignment-validation - General BAM QC
- rna-quantification/featurecounts-counting - Quantification after QC
