# bio-basecalling

> Convert raw Nanopore signal data (FAST5/POD5) to nucleotide sequences using Dorado basecaller. Covers model selection, GPU acceleration, modified base detection, and quality filtering. Use when processing raw Nanopore data before alignment. Guppy is deprecated; use Dorado for all new analyses.

## Version Compatibility

Reference examples tested with: samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Nanopore Basecalling

**"Basecall my Nanopore data"** → Convert raw electrical signal (FAST5/POD5) into nucleotide sequences with quality scores, optionally detecting modified bases.
- CLI: `dorado basecaller sup pod5/ > calls.bam` (recommended), `dorado basecaller sup,5mCG_5hmCG pod5/` (with modifications)

Convert raw electrical signal from Nanopore sequencing into nucleotide sequences.

## Dorado (Recommended)

Dorado is ONT's current production basecaller, replacing Guppy. It offers better accuracy and speed.

### Basic Basecalling

```bash
dorado basecaller sup pod5_dir/ > calls.bam
```

### Choose Model

```bash
dorado basecaller fast pod5_dir/ > calls.bam
dorado basecaller hac pod5_dir/ > calls.bam
dorado basecaller sup pod5_dir/ > calls.bam
```

### Model Speed vs Accuracy

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| fast | Fastest | Lower | Quick preview |
| hac | Medium | High | General use |
| sup | Slowest | Highest | Publication quality |

### Specific Model Version

```bash
dorado download --model dna_r10.4.1_e8.2_400bps_sup@v5.1.0
dorado basecaller dna_r10.4.1_e8.2_400bps_sup@v5.1.0 pod5_dir/ > calls.bam
```

### List Available Models

```bash
dorado download --list
```

### Output FASTQ Instead of BAM

```bash
dorado basecaller sup pod5_dir/ --emit-fastq > calls.fastq
```

### Modified Base Detection

```bash
dorado basecaller sup,5mCG_5hmCG pod5_dir/ > calls_mods.bam
dorado basecaller sup,5mCG pod5_dir/ > calls_5mc.bam
dorado basecaller sup,6mA pod5_dir/ > calls_6ma.bam
```

### GPU Selection

```bash
dorado basecaller sup pod5_dir/ --device cuda:0 > calls.bam
dorado basecaller sup pod5_dir/ --device cuda:0,1 > calls.bam
dorado basecaller sup pod5_dir/ --device cpu > calls.bam
```

### Batch Size for Memory

```bash
dorado basecaller sup pod5_dir/ --batchsize 64 > calls.bam
```

### Duplex Calling

```bash
dorado duplex sup pod5_dir/ > duplex.bam
```

### Demultiplexing During Basecalling

```bash
dorado basecaller sup pod5_dir/ --kit-name SQK-NBD114-24 > calls.bam
dorado demux calls.bam --output-dir demuxed/ --kit-name SQK-NBD114-24
```

### Trim Adapters

```bash
dorado basecaller sup pod5_dir/ --trim adapters > calls.bam
dorado basecaller sup pod5_dir/ --no-trim > calls_untrimmed.bam
```

### Resume Interrupted Run

```bash
dorado basecaller sup pod5_dir/ --resume-from calls.bam > calls_complete.bam
```

## Guppy (Deprecated - Legacy Only)

Guppy is deprecated and no longer receiving updates. Use Dorado for all new analyses. Guppy examples below are only for maintaining legacy pipelines.

### Basic Basecalling

```bash
guppy_basecaller \
    -i fast5_dir/ \
    -s output_dir/ \
    -c dna_r10.4.1_e8.2_400bps_sup.cfg \
    --device cuda:0
```

### CPU Mode

```bash
guppy_basecaller \
    -i fast5_dir/ \
    -s output_dir/ \
    -c dna_r10.4.1_e8.2_400bps_fast.cfg \
    --num_callers 8 \
    --cpu_threads_per_caller 4
```

### High Accuracy Model

```bash
guppy_basecaller \
    -i fast5_dir/ \
    -s output_dir/ \
    -c dna_r10.4.1_e8.2_400bps_hac.cfg \
    --device cuda:0
```

### Super Accuracy Model

```bash
guppy_basecaller \
    -i fast5_dir/ \
    -s output_dir/ \
    -c dna_r10.4.1_e8.2_400bps_sup.cfg \
    --device cuda:0
```

### List Available Configs

```bash
guppy_basecaller --print_workflows
ls /opt/ont/guppy/data/*.cfg
```

### Modified Base Calling

```bash
guppy_basecaller \
    -i fast5_dir/ \
    -s output_dir/ \
    -c dna_r10.4.1_e8.2_400bps_modbases_5mc_cg_sup.cfg \
    --device cuda:0
```

### Barcoding During Basecalling

```bash
guppy_basecaller \
    -i fast5_dir/ \
    -s output_dir/ \
    -c dna_r10.4.1_e8.2_400bps_sup.cfg \
    --device cuda:0 \
    --barcode_kits SQK-NBD114-24
```

### Output BAM

```bash
guppy_basecaller \
    -i fast5_dir/ \
    -s output_dir/ \
    -c dna_r10.4.1_e8.2_400bps_sup.cfg \
    --device cuda:0 \
    --bam_out \
    --index
```

## POD5 File Handling

POD5 is the new format replacing FAST5.

### Convert FAST5 to POD5

```bash
pod5 convert fast5 fast5_dir/*.fast5 --output pod5_dir/
```

### Merge POD5 Files

```bash
pod5 merge pod5_dir/*.pod5 --output merged.pod5
```

### Inspect POD5

```bash
pod5 inspect reads input.pod5
pod5 inspect summary input.pod5
```

### Subset POD5

```bash
pod5 subset input.pod5 --output subset.pod5 --read-id-file read_ids.txt
```

## Quality Filtering

### Filter with Chopper (After Basecalling)

```bash
gunzip -c calls.fastq.gz | chopper -q 10 -l 500 | gzip > filtered.fastq.gz
```

### Filter by Quality Score

```bash
gunzip -c calls.fastq.gz | \
    awk 'BEGIN{OFS="\n"} {h=$0; getline seq; getline plus; getline qual;
         split(h, a, " "); split(a[4], q, "=");
         if(q[2] >= 10) print h, seq, plus, qual}' | \
    gzip > q10_filtered.fastq.gz
```

### NanoFilt (Alternative)

```bash
gunzip -c calls.fastq.gz | NanoFilt -q 10 -l 500 | gzip > filtered.fastq.gz
```

## Basecalling QC

### NanoPlot

```bash
NanoPlot --fastq calls.fastq.gz -o qc_report/ --plots hex dot
NanoPlot --bam calls.bam -o qc_report/
```

### pycoQC (From Sequencing Summary)

```bash
pycoQC -f sequencing_summary.txt -o pycoqc_report.html
```

### Basic Stats

```bash
seqkit stats calls.fastq.gz

awk 'NR%4==2 {sum+=length($0); count++} END {print "Reads:", count, "Mean length:", sum/count}' calls.fastq
```

## Model Selection Guide

### R10.4.1 Chemistry (Current)

| Model | Use |
|-------|-----|
| dna_r10.4.1_e8.2_400bps_fast | Quick analysis |
| dna_r10.4.1_e8.2_400bps_hac | Routine work |
| dna_r10.4.1_e8.2_400bps_sup | High accuracy |

### R9.4.1 Chemistry (Legacy)

| Model | Use |
|-------|-----|
| dna_r9.4.1_450bps_fast | Quick analysis |
| dna_r9.4.1_450bps_hac | Routine work |
| dna_r9.4.1_450bps_sup | High accuracy |

## Complete Pipeline

**Goal:** Run the full Nanopore basecalling pipeline from raw signal data through quality-filtered reads with a QC report.

**Approach:** Convert FAST5 to POD5 if needed, basecall with Dorado, convert to FASTQ, filter with chopper, and generate NanoPlot QC.

```bash
#!/bin/bash
INPUT=$1
OUTPUT=$2
MODEL=${3:-sup}

mkdir -p $OUTPUT

if [ -d "$INPUT/fast5" ]; then
    echo "Converting FAST5 to POD5..."
    pod5 convert fast5 $INPUT/fast5/*.fast5 --output $OUTPUT/pod5/
    INPUT_DIR="$OUTPUT/pod5"
else
    INPUT_DIR="$INPUT"
fi

echo "Basecalling with $MODEL model..."
dorado basecaller $MODEL $INPUT_DIR > $OUTPUT/calls.bam

echo "Converting to FASTQ..."
samtools fastq $OUTPUT/calls.bam | gzip > $OUTPUT/calls.fastq.gz

echo "Filtering..."
gunzip -c $OUTPUT/calls.fastq.gz | chopper -q 10 -l 500 | gzip > $OUTPUT/filtered.fastq.gz

echo "QC report..."
NanoPlot --fastq $OUTPUT/filtered.fastq.gz -o $OUTPUT/qc/

echo "Done!"
```

## GPU Requirements

| Model | VRAM Required | Speed (R10.4.1) |
|-------|--------------|-----------------|
| fast | 4 GB | ~450 bases/s |
| hac | 8 GB | ~200 bases/s |
| sup | 12 GB | ~50 bases/s |

## Troubleshooting

### Out of Memory

```bash
dorado basecaller sup pod5_dir/ --batchsize 32 > calls.bam
```

### Slow CPU Basecalling

```bash
dorado basecaller fast pod5_dir/ --device cpu > calls.bam
```

### Check GPU Usage

```bash
nvidia-smi -l 1
watch -n 1 nvidia-smi
```

## Related Skills

- long-read-alignment - Align basecalled reads
- long-read-qc - QC after basecalling
- medaka-polishing - Polish using basecalled reads
- structural-variants - SV detection from long reads
