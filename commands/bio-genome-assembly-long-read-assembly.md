# bio-genome-assembly-long-read-assembly

> De novo genome assembly from Oxford Nanopore or PacBio long reads using Flye and Canu. Produces highly contiguous assemblies suitable for complete bacterial genomes and resolving complex regions. Use when assembling genomes from ONT or PacBio reads.

**Available tools:** Read, Bash

# Long-Read Assembly

Assemble genomes from Oxford Nanopore (ONT) or PacBio long reads for highly contiguous assemblies.

## Tool Comparison

| Tool | Speed | Memory | Best For |
|------|-------|--------|----------|
| Flye | Fast | Moderate | General purpose, bacteria, ONT |
| Canu | Slow | High | High accuracy, complex genomes |
| Wtdbg2 | Very fast | Low | Draft assemblies |

> **Note:** For PacBio HiFi data, see the dedicated **hifi-assembly** skill which covers hifiasm.

## Flye

### Installation

```bash
conda install -c bioconda flye
```

### Basic Usage

```bash
# Oxford Nanopore
flye --nano-raw reads.fastq.gz --out-dir flye_output --threads 16

# PacBio CLR
flye --pacbio-raw reads.fastq.gz --out-dir flye_output --threads 16

# PacBio HiFi
flye --pacbio-hifi reads.fastq.gz --out-dir flye_output --threads 16
```

### Read Type Options

| Option | Read Type |
|--------|-----------|
| `--nano-raw` | ONT regular reads |
| `--nano-corr` | ONT corrected reads |
| `--nano-hq` | ONT Q20+ reads (Guppy 5+) |
| `--pacbio-raw` | PacBio CLR |
| `--pacbio-corr` | PacBio corrected |
| `--pacbio-hifi` | PacBio HiFi/CCS |

### Key Options

| Option | Description |
|--------|-------------|
| `--out-dir` | Output directory |
| `--threads` | Number of threads |
| `--genome-size` | Estimated genome size (e.g., 5m, 100m) |
| `--iterations` | Polishing iterations (default: 1) |
| `--meta` | Metagenome mode |
| `--plasmids` | Recover plasmids |
| `--keep-haplotypes` | Don't collapse haplotypes |
| `--scaffold` | Enable scaffolding |

### Genome Size Estimation

```bash
# Estimate if unknown
flye --nano-raw reads.fq.gz --out-dir output --genome-size 5m

# Size formats: 1000, 1k, 1m, 1g
```

### Output Files

```
flye_output/
├── assembly.fasta       # Final assembly
├── assembly_graph.gfa   # Assembly graph
├── assembly_info.txt    # Contig statistics
└── flye.log             # Log file
```

### Bacterial Assembly

```bash
flye \
    --nano-raw bacteria.fastq.gz \
    --out-dir bacteria_assembly \
    --genome-size 5m \
    --threads 16
```

### Metagenome Assembly

```bash
flye \
    --nano-raw metagenome.fastq.gz \
    --out-dir meta_assembly \
    --meta \
    --threads 32
```

### With Plasmid Recovery

```bash
flye \
    --nano-raw isolate.fastq.gz \
    --out-dir assembly \
    --plasmids \
    --threads 16
```

## Canu

### Installation

```bash
conda install -c bioconda canu
```

### Basic Usage

```bash
# ONT reads
canu -p assembly -d canu_output genomeSize=5m -nanopore reads.fastq.gz

# PacBio HiFi
canu -p assembly -d canu_output genomeSize=5m -pacbio-hifi reads.fastq.gz
```

### Key Options

| Option | Description |
|--------|-------------|
| `-p` | Assembly prefix |
| `-d` | Output directory |
| `genomeSize=` | Estimated size (required) |
| `maxThreads=` | Max threads |
| `maxMemory=` | Max memory (e.g., 64g) |
| `useGrid=false` | Disable grid execution |
| `correctedErrorRate=` | Expected error rate |

### Read Type Options

| Option | Read Type |
|--------|-----------|
| `-nanopore` | ONT reads |
| `-nanopore-raw` | ONT raw (deprecated) |
| `-pacbio` | PacBio CLR |
| `-pacbio-hifi` | PacBio HiFi/CCS |

### Fast Mode

```bash
canu -p asm -d output genomeSize=5m \
    -nanopore reads.fq.gz \
    useGrid=false \
    maxThreads=16 \
    maxMemory=32g
```

### High-Quality Mode (PacBio HiFi)

```bash
canu -p asm -d output genomeSize=5m \
    -pacbio-hifi reads.fq.gz \
    correctedErrorRate=0.01
```

### Output Files

```
canu_output/
├── assembly.contigs.fasta   # Contigs
├── assembly.unassembled.fasta
├── assembly.report
└── assembly.seqStore/
```

## Wtdbg2 (Fast Draft)

### Installation

```bash
conda install -c bioconda wtdbg
```

### Basic Usage

```bash
# Assemble
wtdbg2 -x ont -g 5m -t 16 -i reads.fq.gz -o draft

# Consensus
wtpoa-cns -t 16 -i draft.ctg.lay.gz -o draft.ctg.fa
```

### Platform Presets

| Preset | Platform |
|--------|----------|
| `-x ont` | ONT R9 |
| `-x ccs` | PacBio HiFi |
| `-x rs` | PacBio CLR |
| `-x sq` | ONT R10 |

## Complete Workflows

### ONT Bacterial Assembly

```bash
#!/bin/bash
set -euo pipefail

READS=$1
OUTDIR=$2
SIZE=${3:-5m}

echo "=== ONT Bacterial Assembly ==="

# Flye assembly
flye \
    --nano-raw $READS \
    --out-dir ${OUTDIR}/flye \
    --genome-size $SIZE \
    --threads 16

# Stats
echo "Assembly statistics:"
cat ${OUTDIR}/flye/assembly_info.txt

echo "Assembly: ${OUTDIR}/flye/assembly.fasta"
```

### Hybrid Assembly (Long + Short)

```bash
#!/bin/bash
set -euo pipefail

LONG=$1
SHORT_R1=$2
SHORT_R2=$3
OUTDIR=$4

# 1. Long-read assembly with Flye
flye --nano-raw $LONG --out-dir ${OUTDIR}/flye --genome-size 5m --threads 16

# 2. Polish with short reads (Pilon)
# See assembly-polishing skill
```

## Quality Expectations

| Metric | Bacterial | Eukaryotic |
|--------|-----------|------------|
| Contigs | 1-10 | 100-1000+ |
| N50 | >1 Mb | Variable |
| Complete chromosomes | Often | Rare |

## Troubleshooting

### Low Contiguity
- Check coverage (need >30x)
- Try increasing iterations in Flye
- Consider supplementing with short reads

### Memory Issues
- Use Flye (more memory efficient)
- Reduce threads
- Filter reads by length/quality

### Misassemblies
- Polish with Pilon/medaka
- Validate with short reads
- Check for contamination

## Related Skills

- hifi-assembly - PacBio HiFi assembly with hifiasm
- assembly-polishing - Polish long-read assemblies
- assembly-qc - QUAST and BUSCO assessment
- short-read-assembly - Hybrid with Illumina
- long-read-sequencing - Read QC and alignment
