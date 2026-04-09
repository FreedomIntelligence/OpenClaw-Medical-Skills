# bio-genome-assembly-short-read-assembly

> De novo genome assembly from Illumina short reads using SPAdes. Covers bacterial, fungal, and small eukaryotic genome assembly, as well as metagenome and transcriptome assembly modes. Use when assembling genomes from Illumina reads.

**Available tools:** Read, Bash

# Short-Read Assembly

Assemble genomes from Illumina paired-end or single-end reads using SPAdes.

## SPAdes Overview

SPAdes (St. Petersburg genome Assembler) uses de Bruijn graph approach with multiple k-mer sizes for robust assembly.

### Installation

```bash
conda install -c bioconda spades
```

## Basic Usage

### Paired-End Assembly

```bash
spades.py -1 R1.fastq.gz -2 R2.fastq.gz -o output_dir
```

### Single-End Assembly

```bash
spades.py -s reads.fastq.gz -o output_dir
```

### With Unpaired Reads

```bash
spades.py -1 R1.fastq.gz -2 R2.fastq.gz -s unpaired.fastq.gz -o output_dir
```

## Assembly Modes

### Isolate Mode (Default for Bacteria)

```bash
spades.py --isolate -1 R1.fq.gz -2 R2.fq.gz -o isolate_assembly
```

Best for single-organism isolates with uniform coverage.

### Careful Mode

```bash
spades.py --careful -1 R1.fq.gz -2 R2.fq.gz -o careful_assembly
```

Reduces misassemblies at cost of speed. Recommended for small genomes.

### Meta Mode (Metagenomes)

```bash
spades.py --meta -1 R1.fq.gz -2 R2.fq.gz -o meta_assembly
```

For mixed microbial communities with varying coverage.

### RNA Mode (Transcriptomes)

```bash
spades.py --rna -1 R1.fq.gz -2 R2.fq.gz -o rna_assembly
```

Assembles transcripts from RNA-seq data.

### Plasmid Mode

```bash
spades.py --plasmid -1 R1.fq.gz -2 R2.fq.gz -o plasmid_assembly
```

Extracts plasmid sequences from bacterial isolates.

## Key Options

| Option | Description |
|--------|-------------|
| `-o <dir>` | Output directory |
| `-t <#>` | Number of threads (default: 16) |
| `-m <#>` | Memory limit in GB (default: 250) |
| `-k <#,#,...>` | K-mer sizes (auto by default) |
| `--careful` | Reduce misassemblies |
| `--isolate` | Isolate mode for uniform coverage |
| `--meta` | Metagenome mode |
| `--rna` | RNA-seq assembly |
| `--cov-cutoff <#>` | Coverage cutoff (default: off) |
| `--only-assembler` | Skip error correction |
| `--continue` | Resume interrupted run |

## Multiple Libraries

### Paired Libraries with Different Insert Sizes

```bash
spades.py \
    --pe1-1 short_R1.fq.gz --pe1-2 short_R2.fq.gz \
    --pe2-1 long_R1.fq.gz --pe2-2 long_R2.fq.gz \
    -o output_dir
```

### With Mate Pairs

```bash
spades.py \
    --pe1-1 paired_R1.fq.gz --pe1-2 paired_R2.fq.gz \
    --mp1-1 mate_R1.fq.gz --mp1-2 mate_R2.fq.gz \
    -o output_dir
```

### With PacBio/Nanopore (Hybrid)

```bash
spades.py \
    -1 illumina_R1.fq.gz -2 illumina_R2.fq.gz \
    --pacbio pacbio.fq.gz \
    -o hybrid_assembly

# Or with Nanopore
spades.py \
    -1 illumina_R1.fq.gz -2 illumina_R2.fq.gz \
    --nanopore nanopore.fq.gz \
    -o hybrid_assembly
```

## K-mer Selection

### Auto Selection (Recommended)

SPAdes automatically selects appropriate k-mers based on read length.

### Manual K-mer Specification

```bash
# For 150bp reads
spades.py -k 21,33,55,77 -1 R1.fq.gz -2 R2.fq.gz -o output

# For 250bp reads
spades.py -k 21,33,55,77,99,127 -1 R1.fq.gz -2 R2.fq.gz -o output
```

## Output Files

```
output_dir/
├── scaffolds.fasta     # Final scaffolds (use this)
├── contigs.fasta       # Contigs before scaffolding
├── assembly_graph.gfa  # Assembly graph
├── spades.log          # Log file
├── params.txt          # Parameters used
└── K*/                 # Intermediate k-mer assemblies
```

### Scaffold FASTA Headers

```
>NODE_1_length_500000_cov_50.5
```

- `NODE_1` - Contig/scaffold ID
- `length_500000` - Sequence length
- `cov_50.5` - Average k-mer coverage

## Memory and Performance

### Reduce Memory Usage

```bash
# Limit memory to 32GB
spades.py -m 32 -1 R1.fq.gz -2 R2.fq.gz -o output

# Use fewer threads
spades.py -t 8 -1 R1.fq.gz -2 R2.fq.gz -o output
```

### Resume Interrupted Assembly

```bash
spades.py --continue -o output_dir
```

### Skip Error Correction

```bash
# If reads already corrected
spades.py --only-assembler -1 R1.fq.gz -2 R2.fq.gz -o output
```

## Complete Workflows

### Bacterial Genome Assembly

```bash
#!/bin/bash
set -euo pipefail

R1=$1
R2=$2
OUTDIR=$3
THREADS=${4:-16}

echo "=== Bacterial Genome Assembly ==="

# Run SPAdes in isolate mode
spades.py \
    --isolate \
    --careful \
    -t $THREADS \
    -1 $R1 -2 $R2 \
    -o $OUTDIR

# Basic stats
echo "Assembly statistics:"
grep -c "^>" ${OUTDIR}/scaffolds.fasta
seqkit stats ${OUTDIR}/scaffolds.fasta
```

### Metagenome Assembly

```bash
#!/bin/bash
set -euo pipefail

R1=$1
R2=$2
OUTDIR=$3

spades.py \
    --meta \
    -t 32 \
    -m 200 \
    -1 $R1 -2 $R2 \
    -o $OUTDIR

echo "Metagenome assembly complete: ${OUTDIR}/scaffolds.fasta"
```

### Transcriptome Assembly

```bash
spades.py \
    --rna \
    -t 16 \
    -1 rnaseq_R1.fq.gz -2 rnaseq_R2.fq.gz \
    -o transcriptome_assembly
```

## Alternative Assemblers

| Assembler | Best For |
|-----------|----------|
| SPAdes | Small genomes, bacteria, fungi |
| MEGAHIT | Metagenomes (memory efficient) |
| ABySS | Large genomes |
| Velvet | Legacy, small genomes |
| Trinity | Transcriptomes |

### MEGAHIT (Alternative for Metagenomes)

```bash
megahit -1 R1.fq.gz -2 R2.fq.gz -o megahit_output -t 16
```

## Troubleshooting

### Out of Memory

- Reduce `-m` limit
- Use `--meta` mode (more memory efficient)
- Try MEGAHIT instead

### Poor Assembly

- Check read quality with FastQC
- Trim adapters and low-quality bases
- Increase coverage if possible
- Try `--careful` mode

### Long Runtime

- Reduce k-mer values
- Use `--only-assembler` if reads pre-corrected
- Increase threads

## Related Skills

- read-qc - Preprocess reads before assembly
- assembly-polishing - Polish assembly with Pilon
- assembly-qc - Assess with QUAST/BUSCO
- long-read-assembly - Long-read alternatives
