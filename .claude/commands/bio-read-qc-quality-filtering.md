# bio-read-qc-quality-filtering

> Filter reads by quality scores, length, and N content using Trimmomatic and fastp. Apply sliding window trimming, remove low-quality bases from read ends, and discard reads below thresholds. Use when reads have poor quality tails or require minimum quality for downstream analysis.

## Version Compatibility

Reference examples tested with: Trimmomatic 0.39+, cutadapt 4.4+, fastp 0.23+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Quality Filtering

Trim low-quality bases and filter reads using Trimmomatic sliding window or fastp quality filtering.

**"Filter reads by quality"** → Remove low-quality bases and discard reads below quality/length thresholds.
- CLI: `trimmomatic PE` with SLIDINGWINDOW and MINLEN options
- CLI: `fastp --qualified_quality_phred 20 --length_required 50`

## Trimmomatic Quality Operations

### Single-End Mode

```bash
trimmomatic SE -phred33 \
    input.fastq.gz output.fastq.gz \
    LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36
```

### Paired-End Mode

```bash
trimmomatic PE -phred33 -threads 4 \
    input_R1.fastq.gz input_R2.fastq.gz \
    output_R1_paired.fastq.gz output_R1_unpaired.fastq.gz \
    output_R2_paired.fastq.gz output_R2_unpaired.fastq.gz \
    LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36
```

### Trimmomatic Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| LEADING | LEADING:Q | Remove leading bases below quality Q |
| TRAILING | TRAILING:Q | Remove trailing bases below quality Q |
| SLIDINGWINDOW | SLIDINGWINDOW:W:Q | Cut when W-bp window average < Q |
| MINLEN | MINLEN:L | Discard reads shorter than L |
| CROP | CROP:L | Cut read to max length L |
| HEADCROP | HEADCROP:N | Remove first N bases |
| AVGQUAL | AVGQUAL:Q | Drop read if average quality < Q |
| MAXINFO | MAXINFO:L:S | Balance length and quality |
| TOPHRED33 | TOPHRED33 | Convert to Phred33 encoding |
| TOPHRED64 | TOPHRED64 | Convert to Phred64 encoding |

### Common Trimmomatic Recipes

```bash
# Standard quality trimming
trimmomatic SE input.fq output.fq \
    SLIDINGWINDOW:4:20 MINLEN:36

# Aggressive 3' trimming
trimmomatic SE input.fq output.fq \
    TRAILING:20 SLIDINGWINDOW:4:20 MINLEN:36

# Trim both ends, strict filtering
trimmomatic SE input.fq output.fq \
    LEADING:10 TRAILING:10 SLIDINGWINDOW:4:25 MINLEN:50

# Keep fixed length (for some tools)
trimmomatic SE input.fq output.fq \
    CROP:100 MINLEN:100

# Remove first 10 bases (e.g., random primers)
trimmomatic SE input.fq output.fq \
    HEADCROP:10 MINLEN:36
```

### SLIDINGWINDOW Details

```bash
SLIDINGWINDOW:<windowSize>:<requiredQuality>

# Scan from 5' to 3'
# Cut when average quality in window drops below threshold
# Common settings: 4:15, 4:20, 5:20

# Conservative (keep more, lower quality)
SLIDINGWINDOW:4:15

# Moderate
SLIDINGWINDOW:4:20

# Strict (keep less, higher quality)
SLIDINGWINDOW:4:25
```

## fastp Quality Filtering

### Basic Quality Filtering

```bash
# Quality filtering (default Q15)
fastp -i in.fq -o out.fq

# Custom quality threshold
fastp -i in.fq -o out.fq -q 20

# Sliding window from 5' end
fastp -i in.fq -o out.fq --cut_front --cut_front_window_size 4 --cut_front_mean_quality 20

# Sliding window from 3' end
fastp -i in.fq -o out.fq --cut_tail --cut_tail_window_size 4 --cut_tail_mean_quality 20

# Aggressive right-side trimming (recommended)
fastp -i in.fq -o out.fq --cut_right --cut_right_window_size 4 --cut_right_mean_quality 20
```

### fastp Quality Options

```bash
# Global mean quality filter
fastp -i in.fq -o out.fq -q 20 -e 25
# -q: per-base quality threshold
# -e: average quality threshold for entire read

# Unqualified bases threshold
fastp -i in.fq -o out.fq --unqualified_percent_limit 40
# Discard if >40% bases below quality threshold

# N base filtering
fastp -i in.fq -o out.fq -n 5
# Discard reads with >5 N bases
```

### Paired-End with fastp

```bash
fastp -i R1.fq -I R2.fq -o out_R1.fq -O out_R2.fq \
    --cut_right \
    --cut_right_window_size 4 \
    --cut_right_mean_quality 20 \
    -q 20 -l 36
```

### Length Filtering

```bash
# Trimmomatic
trimmomatic SE input.fq output.fq MINLEN:50

# fastp
fastp -i in.fq -o out.fq -l 50          # min length
fastp -i in.fq -o out.fq --length_limit 150  # max length
```

## Cutadapt Quality Trimming

```bash
# Trim 3' end below Q20
cutadapt -q 20 -o out.fq in.fq

# Trim both ends
cutadapt -q 20,20 -o out.fq in.fq

# With minimum length
cutadapt -q 20 -m 36 -o out.fq in.fq

# Paired-end
cutadapt -q 20 -m 36 -o R1.fq -p R2.fq in_R1.fq in_R2.fq
```

## Combined Adapter + Quality Trimming

### Trimmomatic Full Pipeline

```bash
trimmomatic PE -threads 4 -phred33 \
    R1.fq.gz R2.fq.gz \
    R1_paired.fq.gz R1_unpaired.fq.gz \
    R2_paired.fq.gz R2_unpaired.fq.gz \
    ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads \
    LEADING:3 TRAILING:3 SLIDINGWINDOW:4:20 MINLEN:36
```

### Cutadapt Full Pipeline

```bash
cutadapt \
    -a AGATCGGAAGAGC -A AGATCGGAAGAGC \
    -q 20 -m 36 \
    -o R1_trimmed.fq.gz -p R2_trimmed.fq.gz \
    R1.fq.gz R2.fq.gz
```

## Poly-G Trimming (NovaSeq/NextSeq)

NextSeq and NovaSeq use two-color chemistry, causing poly-G artifacts at read ends.

```bash
# fastp auto-detects and trims poly-G
fastp -i in.fq -o out.fq --trim_poly_g

# Disable auto-detection
fastp -i in.fq -o out.fq --disable_trim_poly_g

# Trimmomatic (manual approach)
# Add poly-G to adapter file
```

## Quality Thresholds

| Phred | Error Rate | Use Case |
|-------|------------|----------|
| Q10 | 10% | Very lenient |
| Q15 | 3% | fastp default |
| Q20 | 1% | Common threshold |
| Q25 | 0.3% | Strict |
| Q30 | 0.1% | Very strict |

## Related Skills

- adapter-trimming - Remove adapters before quality filtering
- quality-reports - Check quality before/after filtering
- fastp-workflow - All-in-one preprocessing
