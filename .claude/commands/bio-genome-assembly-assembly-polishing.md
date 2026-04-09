# bio-genome-assembly-assembly-polishing

> Polish genome assemblies to reduce errors using short reads (Pilon), long reads (Racon), or ONT-specific tools (medaka). Essential for improving long-read assembly accuracy. Use when improving assembly accuracy with polishing tools.

**Available tools:** Read, Bash

# Assembly Polishing

Improve assembly accuracy by correcting errors using additional sequencing data.

## Polishing Strategies

| Tool | Input Reads | Best For |
|------|-------------|----------|
| Pilon | Illumina | Final polishing |
| medaka | ONT | ONT assemblies |
| Racon | Long reads | Quick polishing |
| NextPolish | Both | Combined approach |

## Recommended Workflows

### ONT Assembly
1. Racon (2-3 rounds with ONT)
2. medaka (1 round)
3. Pilon (2-3 rounds with Illumina)

### PacBio CLR Assembly
1. Racon (2-3 rounds)
2. Pilon (2-3 rounds with Illumina)

### PacBio HiFi Assembly
- Often no polishing needed (>99% accuracy)
- Optional Pilon if Illumina available

## Pilon (Illumina Polishing)

### Installation

```bash
conda install -c bioconda pilon
```

### Basic Usage

```bash
# Map short reads to assembly
bwa index assembly.fasta
bwa mem -t 16 assembly.fasta R1.fq.gz R2.fq.gz | samtools sort -o aligned.bam
samtools index aligned.bam

# Run Pilon
pilon --genome assembly.fasta --frags aligned.bam --output polished
```

### Key Options

| Option | Description |
|--------|-------------|
| `--genome` | Input assembly |
| `--frags` | Paired-end BAM |
| `--output` | Output prefix |
| `--changes` | Write changes file |
| `--vcf` | Write VCF of changes |
| `--fix` | What to fix (snps, indels, gaps, all) |
| `--threads` | Threads for alignment |
| `--mindepth` | Min depth for correction |

### Multiple Rounds

```bash
#!/bin/bash
ASSEMBLY=$1
R1=$2
R2=$3
ROUNDS=${4:-3}

current=$ASSEMBLY

for i in $(seq 1 $ROUNDS); do
    echo "=== Pilon round $i ==="
    bwa index $current
    bwa mem -t 16 $current $R1 $R2 | samtools sort -o round${i}.bam
    samtools index round${i}.bam

    pilon --genome $current --frags round${i}.bam --output pilon_round${i} --changes

    current=pilon_round${i}.fasta

    changes=$(wc -l < pilon_round${i}.changes)
    echo "Changes made: $changes"

    if [ $changes -eq 0 ]; then
        echo "No more changes, stopping"
        break
    fi
done

cp $current final_polished.fasta
```

### Fix Specific Issues

```bash
# Only fix SNPs and small indels
pilon --genome assembly.fa --frags aligned.bam --output polished --fix snps,indels

# Only fill gaps
pilon --genome assembly.fa --frags aligned.bam --output polished --fix gaps
```

## medaka (ONT Polishing)

### Installation

```bash
conda install -c bioconda medaka
```

### Basic Usage

```bash
medaka_consensus -i reads.fastq.gz -d assembly.fasta -o medaka_output -t 8
```

### Key Options

| Option | Description |
|--------|-------------|
| `-i` | Input reads |
| `-d` | Draft assembly |
| `-o` | Output directory |
| `-t` | Threads |
| `-m` | Model name |

### Model Selection

```bash
# List available models
medaka tools list_models

# Use specific model (match your basecaller)
medaka_consensus -i reads.fq.gz -d assembly.fa -o output -m r1041_e82_400bps_sup_v5.1.0
```

### Models for Common Chemistries

| Chemistry | Model |
|-----------|-------|
| R10.4.1 + SUP | r1041_e82_400bps_sup_* |
| R10.4.1 + HAC | r1041_e82_400bps_hac_* |
| R9.4.1 + SUP | r941_sup_* |

### Output

```
medaka_output/
├── consensus.fasta    # Polished assembly
├── calls_to_draft.bam # Alignments
└── *.hdf              # Intermediate files
```

## Racon (Long-Read Polishing)

### Installation

```bash
conda install -c bioconda racon
```

### Basic Usage

```bash
# Map reads to assembly
minimap2 -ax map-ont assembly.fasta reads.fastq.gz > aligned.sam

# Polish
racon -t 16 reads.fastq.gz aligned.sam assembly.fasta > polished.fasta
```

### Multiple Rounds

```bash
#!/bin/bash
ASSEMBLY=$1
READS=$2
ROUNDS=${3:-3}

current=$ASSEMBLY

for i in $(seq 1 $ROUNDS); do
    echo "=== Racon round $i ==="
    minimap2 -ax map-ont $current $READS > round${i}.sam
    racon -t 16 $READS round${i}.sam $current > racon_round${i}.fasta
    current=racon_round${i}.fasta
done

cp $current racon_polished.fasta
```

### Key Options

| Option | Description |
|--------|-------------|
| `-t` | Threads |
| `-m` | Match score (default: 3) |
| `-x` | Mismatch score (default: -5) |
| `-g` | Gap penalty (default: -4) |
| `-w` | Window size (default: 500) |

## Complete Polishing Workflow

### ONT Assembly Polishing

```bash
#!/bin/bash
set -euo pipefail

ASSEMBLY=$1      # Flye assembly
ONT_READS=$2     # ONT reads
ILLUMINA_R1=$3   # Illumina R1
ILLUMINA_R2=$4   # Illumina R2
OUTDIR=$5

mkdir -p $OUTDIR

# Step 1: Racon polishing (2 rounds)
echo "=== Racon Polishing ==="
current=$ASSEMBLY
for i in 1 2; do
    minimap2 -ax map-ont $current $ONT_READS > ${OUTDIR}/racon_${i}.sam
    racon -t 16 $ONT_READS ${OUTDIR}/racon_${i}.sam $current > ${OUTDIR}/racon_${i}.fasta
    current=${OUTDIR}/racon_${i}.fasta
done

# Step 2: medaka polishing
echo "=== medaka Polishing ==="
medaka_consensus -i $ONT_READS -d $current -o ${OUTDIR}/medaka -t 8
current=${OUTDIR}/medaka/consensus.fasta

# Step 3: Pilon polishing (2 rounds)
echo "=== Pilon Polishing ==="
for i in 1 2; do
    bwa index $current
    bwa mem -t 16 $current $ILLUMINA_R1 $ILLUMINA_R2 | samtools sort -o ${OUTDIR}/pilon_${i}.bam
    samtools index ${OUTDIR}/pilon_${i}.bam
    pilon --genome $current --frags ${OUTDIR}/pilon_${i}.bam --output ${OUTDIR}/pilon_${i}
    current=${OUTDIR}/pilon_${i}.fasta
done

cp $current ${OUTDIR}/final_polished.fasta
echo "Done: ${OUTDIR}/final_polished.fasta"
```

## NextPolish (Combined Approach)

### Installation

```bash
conda install -c bioconda nextpolish
```

### Usage

```bash
# Create config file
cat > run.cfg << EOF
[General]
job_type = local
job_prefix = nextPolish
task = best
rewrite = yes
rerun = 3
parallel_jobs = 2
multithread_jobs = 8
genome = assembly.fasta
genome_size = auto
workdir = ./01_rundir
[lgs_option]
lgs_fofn = lgs.fofn
lgs_options = -min_read_len 1k -max_depth 100
lgs_minimap2_options = -x map-ont
[sgs_option]
sgs_fofn = sgs.fofn
sgs_options = -max_depth 100
EOF

# File of filenames
ls reads.fastq.gz > lgs.fofn
ls R1.fq.gz R2.fq.gz > sgs.fofn

# Run
nextPolish run.cfg
```

## Quality Assessment

After polishing, assess improvement:

```bash
# Compare to reference (if available)
quast.py -r reference.fa original.fa polished.fa -o quast_comparison

# Check error rate
minimap2 -ax map-ont polished.fa reads.fq.gz | samtools stats | grep "error rate"
```

## Related Skills

- long-read-assembly - Initial assembly
- short-read-assembly - Source of polishing reads
- assembly-qc - Assess polishing improvement
- long-read-sequencing - medaka variant calling
