# bio-read-qc-fastp-workflow

> All-in-one read preprocessing with fastp including adapter trimming, quality filtering, deduplication, base correction, and HTML report generation. Use when preprocessing Illumina data and wanting a single fast tool instead of separate Cutadapt, Trimmomatic, and FastQC steps.

## Version Compatibility

Reference examples tested with: FastQC 0.12+, fastp 0.23+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# fastp Workflow

All-in-one preprocessing tool that handles adapter trimming, quality filtering, deduplication, and report generation in a single pass.

**"Preprocess FASTQ reads with fastp"** → Run adapter trimming, quality filtering, and QC reporting in a single pass.
- CLI: `fastp -i R1.fq -I R2.fq -o clean_R1.fq -O clean_R2.fq --html report.html`

## Basic Usage

### Single-End

```bash
fastp -i input.fastq.gz -o output.fastq.gz
```

### Paired-End

```bash
fastp -i R1.fastq.gz -I R2.fastq.gz -o R1_clean.fastq.gz -O R2_clean.fastq.gz
```

### With Custom HTML/JSON Reports

```bash
fastp -i R1.fq.gz -I R2.fq.gz \
      -o R1_clean.fq.gz -O R2_clean.fq.gz \
      -h sample_report.html \
      -j sample_report.json
```

## Adapter Trimming

fastp auto-detects Illumina adapters by default.

```bash
# Auto-detect (default)
fastp -i in.fq -o out.fq

# Specify adapters manually
fastp -i in.fq -o out.fq \
      --adapter_sequence AGATCGGAAGAGCACACGTCTGAACTCCAGTCA

# Paired-end with manual adapters
fastp -i R1.fq -I R2.fq -o R1.out.fq -O R2.out.fq \
      --adapter_sequence AGATCGGAAGAGCACACGTCTGAACTCCAGTCA \
      --adapter_sequence_r2 AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT

# Disable adapter trimming
fastp -i in.fq -o out.fq --disable_adapter_trimming

# Adapter FASTA file
fastp -i in.fq -o out.fq --adapter_fasta adapters.fa
```

## Quality Filtering

```bash
# Per-base quality threshold (default Q15)
fastp -i in.fq -o out.fq -q 20

# Mean read quality threshold
fastp -i in.fq -o out.fq -e 25

# Max unqualified bases percent (default 40)
fastp -i in.fq -o out.fq -q 20 --unqualified_percent_limit 30

# Disable quality filtering
fastp -i in.fq -o out.fq --disable_quality_filtering
```

## Quality Trimming

```bash
# Sliding window from 3' end (recommended)
fastp -i in.fq -o out.fq \
      --cut_right \
      --cut_right_window_size 4 \
      --cut_right_mean_quality 20

# Sliding window from 5' end
fastp -i in.fq -o out.fq \
      --cut_front \
      --cut_front_window_size 4 \
      --cut_front_mean_quality 20

# Both ends
fastp -i in.fq -o out.fq \
      --cut_front --cut_tail \
      --cut_front_window_size 4 \
      --cut_front_mean_quality 20 \
      --cut_tail_window_size 4 \
      --cut_tail_mean_quality 20
```

## Length Filtering

```bash
# Minimum length (default 15)
fastp -i in.fq -o out.fq -l 36

# Maximum length
fastp -i in.fq -o out.fq --length_limit 150

# Required length (discard shorter AND longer)
fastp -i in.fq -o out.fq -l 100 --length_limit 100
```

## Poly-X Trimming

```bash
# Trim poly-G (NovaSeq/NextSeq artifacts) - auto-enabled for these platforms
fastp -i in.fq -o out.fq --trim_poly_g

# Disable poly-G trimming
fastp -i in.fq -o out.fq --disable_trim_poly_g

# Trim poly-X (any homopolymer)
fastp -i in.fq -o out.fq --trim_poly_x

# Custom poly-G minimum length (default 10)
fastp -i in.fq -o out.fq --trim_poly_g --poly_g_min_len 5
```

## N Base Handling

```bash
# Max N bases (default 5)
fastp -i in.fq -o out.fq -n 3

# Disable N filtering
fastp -i in.fq -o out.fq --n_base_limit 50
```

## Deduplication

```bash
# Enable deduplication
fastp -i in.fq -o out.fq --dedup

# Accuracy level (1-6, higher = more memory, default 3)
fastp -i in.fq -o out.fq --dedup --dup_calc_accuracy 4
```

## Base Correction (Paired-End Only)

```bash
# Enable overlap-based correction
fastp -i R1.fq -I R2.fq -o R1.out.fq -O R2.out.fq --correction

# Required overlap length (default 30)
fastp -i R1.fq -I R2.fq -o R1.out.fq -O R2.out.fq \
      --correction --overlap_len_require 20
```

## Paired-End Merge

```bash
# Merge overlapping paired reads
fastp -i R1.fq -I R2.fq \
      --merge --merged_out merged.fq \
      -o R1_unmerged.fq -O R2_unmerged.fq
```

## UMI Processing

```bash
# UMI in read (extract to header)
fastp -i in.fq -o out.fq \
      --umi --umi_loc read1 --umi_len 8

# UMI in separate read
fastp -i R1.fq -I R2.fq -o R1.out.fq -O R2.out.fq \
      --umi --umi_loc index1

# UMI locations: index1, index2, read1, read2, per_index, per_read
```

## Complete Workflow Example

### Standard Illumina Pipeline

```bash
fastp \
    -i raw_R1.fastq.gz -I raw_R2.fastq.gz \
    -o clean_R1.fastq.gz -O clean_R2.fastq.gz \
    --detect_adapter_for_pe \
    --cut_right --cut_right_window_size 4 --cut_right_mean_quality 20 \
    -q 20 -l 36 \
    --thread 8 \
    -h sample_fastp.html -j sample_fastp.json
```

### NovaSeq/NextSeq Pipeline

```bash
fastp \
    -i raw_R1.fastq.gz -I raw_R2.fastq.gz \
    -o clean_R1.fastq.gz -O clean_R2.fastq.gz \
    --detect_adapter_for_pe \
    --trim_poly_g \
    --cut_right --cut_right_window_size 4 --cut_right_mean_quality 20 \
    -q 20 -l 36 \
    --thread 8 \
    -h sample_fastp.html -j sample_fastp.json
```

### RNA-seq Pipeline

```bash
fastp \
    -i raw_R1.fastq.gz -I raw_R2.fastq.gz \
    -o clean_R1.fastq.gz -O clean_R2.fastq.gz \
    --detect_adapter_for_pe \
    --cut_right --cut_right_window_size 4 --cut_right_mean_quality 20 \
    -q 20 -l 50 \
    --thread 8 \
    -h sample_fastp.html -j sample_fastp.json
```

## Output Files

| File | Description |
|------|-------------|
| `*.html` | Interactive HTML report |
| `*.json` | Machine-readable statistics |
| Output FASTQ | Processed reads |

## JSON Report Structure

```python
import json

with open('sample_fastp.json') as f:
    report = json.load(f)

summary = report['summary']
print(f"Total reads: {summary['before_filtering']['total_reads']}")
print(f"Passed reads: {summary['after_filtering']['total_reads']}")
print(f"Q20 rate: {summary['after_filtering']['q20_rate']:.2%}")
print(f"Q30 rate: {summary['after_filtering']['q30_rate']:.2%}")
```

## Performance

```bash
# Set threads (default 3)
fastp -i in.fq -o out.fq --thread 8

# Disable HTML report (faster)
fastp -i in.fq -o out.fq --html /dev/null

# Process from stdin
zcat in.fq.gz | fastp --stdin -o out.fq
```

## Related Skills

- quality-reports - MultiQC can aggregate fastp JSON reports
- adapter-trimming - Cutadapt for complex adapter scenarios
- quality-filtering - Trimmomatic alternative
