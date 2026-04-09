# bio-read-qc-adapter-trimming

> Remove sequencing adapters from FASTQ files using Cutadapt and Trimmomatic. Supports single-end and paired-end reads, Illumina TruSeq, Nextera, and custom adapter sequences. Use when FastQC shows adapter contamination or before alignment of short reads.

## Version Compatibility

Reference examples tested with: FastQC 0.12+, Trimmomatic 0.39+, cutadapt 4.4+, fastp 0.23+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Adapter Trimming

Remove sequencing adapters from reads using Cutadapt (precise, flexible) or Trimmomatic (paired-end optimized).

**"Trim adapters from reads"** → Remove sequencing adapter sequences from FASTQ reads to prevent adapter contamination in downstream alignment.
- CLI: `cutadapt -a ADAPTER -o out.fq in.fq` or `trimmomatic PE` with ILLUMINACLIP
- CLI: `fastp -i in.fq -o out.fq` (auto-detects adapters)

## Common Adapter Sequences

| Platform/Kit | Adapter | Sequence |
|--------------|---------|----------|
| Illumina TruSeq | Read 1 3' | AGATCGGAAGAGCACACGTCTGAACTCCAGTCA |
| Illumina TruSeq | Read 2 3' | AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT |
| Nextera | Transposase | CTGTCTCTTATACACATCT |
| Small RNA | 3' adapter | TGGAATTCTCGGGTGCCAAGG |
| Poly-A | Poly-A tail | AAAAAAAAAAAAAAAA |

## Cutadapt

### Single-End Reads

```bash
# 3' adapter (most common)
cutadapt -a AGATCGGAAGAGC -o trimmed.fastq.gz sample.fastq.gz

# 5' adapter
cutadapt -g ACGTACGT -o trimmed.fastq.gz sample.fastq.gz

# Both ends
cutadapt -a ADAPTER1 -g ADAPTER2 -o trimmed.fastq.gz sample.fastq.gz

# Multiple adapters (tries each)
cutadapt -a ADAPTER1 -a ADAPTER2 -a ADAPTER3 -o trimmed.fastq.gz sample.fastq.gz
```

### Paired-End Reads

```bash
# Basic paired-end
cutadapt -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA \
         -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
         -o trimmed_R1.fastq.gz -p trimmed_R2.fastq.gz \
         sample_R1.fastq.gz sample_R2.fastq.gz

# Short form for Illumina TruSeq (auto-detect)
cutadapt -a AGATCGGAAGAGC -A AGATCGGAAGAGC \
         -o trimmed_R1.fastq.gz -p trimmed_R2.fastq.gz \
         sample_R1.fastq.gz sample_R2.fastq.gz
```

### Adapter Options

```bash
# Error rate (default 0.1 = 10% mismatches allowed)
cutadapt -a ADAPTER -e 0.15 -o out.fq in.fq

# Minimum overlap (default 3)
cutadapt -a ADAPTER -O 5 -o out.fq in.fq

# No indels in adapter alignment
cutadapt -a ADAPTER --no-indels -o out.fq in.fq

# Trim Ns from ends
cutadapt --trim-n -o out.fq in.fq

# Anchored adapters (must be at end)
cutadapt -a ADAPTER$ -o out.fq in.fq
```

### Linked Adapters

```bash
# 5' adapter followed by 3' adapter (same read)
cutadapt -a ADAPTER1...ADAPTER2 -o out.fq in.fq

# Anchored 5' linked to 3'
cutadapt -a ^ADAPTER1...ADAPTER2 -o out.fq in.fq
```

### Filtering After Trimming

```bash
# Minimum length (discard shorter)
cutadapt -a ADAPTER -m 20 -o out.fq in.fq

# Maximum length
cutadapt -a ADAPTER -M 150 -o out.fq in.fq

# Maximum N content
cutadapt -a ADAPTER --max-n 0.1 -o out.fq in.fq

# Discard trimmed reads
cutadapt -a ADAPTER --discard-trimmed -o out.fq in.fq

# Discard untrimmed reads
cutadapt -a ADAPTER --discard-untrimmed -o out.fq in.fq
```

### Paired-End Filtering

```bash
# Both reads must pass minimum length
cutadapt -a ADAPT1 -A ADAPT2 -m 20 \
         -o R1.fq -p R2.fq in_R1.fq in_R2.fq

# Output too-short reads separately
cutadapt -a ADAPT1 -A ADAPT2 -m 20 \
         --too-short-output short_R1.fq --too-short-paired-output short_R2.fq \
         -o R1.fq -p R2.fq in_R1.fq in_R2.fq
```

### Action Options

```bash
# Mask adapter instead of trim (replace with N)
cutadapt -a ADAPTER --action=mask -o out.fq in.fq

# Retain adapter but lowercase
cutadapt -a ADAPTER --action=lowercase -o out.fq in.fq

# Just find adapters, don't modify
cutadapt -a ADAPTER --action=none -o out.fq in.fq
```

## Trimmomatic

### Single-End Mode

```bash
trimmomatic SE -phred33 \
    input.fastq.gz output.fastq.gz \
    ILLUMINACLIP:adapters.fa:2:30:10
```

### Paired-End Mode

```bash
trimmomatic PE -phred33 -threads 4 \
    input_R1.fastq.gz input_R2.fastq.gz \
    output_R1_paired.fastq.gz output_R1_unpaired.fastq.gz \
    output_R2_paired.fastq.gz output_R2_unpaired.fastq.gz \
    ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10
```

### ILLUMINACLIP Parameters

```bash
ILLUMINACLIP:<fastaWithAdapters>:<seed>:<palindrome>:<simple>

# Parameters:
# seed - max mismatches in 16bp seed (usually 2)
# palindrome - threshold for palindrome match (usually 30)
# simple - threshold for simple match (usually 10)

# Example with all options
ILLUMINACLIP:adapters.fa:2:30:10:2:keepBothReads
```

### Built-in Adapter Files

Trimmomatic includes adapter files:
- `TruSeq2-SE.fa` - TruSeq v2 single-end
- `TruSeq2-PE.fa` - TruSeq v2 paired-end
- `TruSeq3-SE.fa` - TruSeq v3 single-end
- `TruSeq3-PE.fa` - TruSeq v3 paired-end
- `TruSeq3-PE-2.fa` - TruSeq v3 PE (palindrome mode)
- `NexteraPE-PE.fa` - Nextera paired-end

### Find Trimmomatic Adapters

```bash
# Find adapter directory
TRIMMOMATIC_JAR=$(which trimmomatic | xargs dirname)/../share/trimmomatic-*/adapters/

# Or with conda
ls $CONDA_PREFIX/share/trimmomatic-*/adapters/
```

## Performance

```bash
# Cutadapt with multiple cores
cutadapt -j 8 -a ADAPTER -o out.fq in.fq

# Trimmomatic threads
trimmomatic PE -threads 8 ...
```

## Verify Trimming

```bash
# Check adapter removal with FastQC
fastqc trimmed.fastq.gz

# Count reads before/after
zcat input.fastq.gz | wc -l
zcat trimmed.fastq.gz | wc -l
```

## Related Skills

- quality-reports - Check adapter content with FastQC
- quality-filtering - Quality trimming after adapter removal
- fastp-workflow - Combined adapter and quality trimming
