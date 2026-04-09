# bio-workflows-genome-assembly-pipeline

> End-to-end genome assembly workflow from reads to polished assembly with QC. Supports short reads (SPAdes), long reads (Flye), and hybrid approaches. Use when assembling genomes from raw reads.

**Available tools:** Read, Bash

# Genome Assembly Pipeline

Complete workflow from sequencing reads to polished, quality-assessed genome assembly.

## Workflow Overview

```
Reads (short and/or long)
    |
    v
[1. QC & Filtering] -----> fastp, NanoPlot
    |
    v
[2. Assembly] -----------> SPAdes (short) or Flye (long)
    |
    v
[3. Polishing] ----------> Pilon (short) or medaka (long)
    |
    v
[4. QC Assessment] ------> QUAST, BUSCO
    |
    v
Final polished assembly
```

## Path A: Short-Read Assembly (SPAdes)

### Step 1: QC

```bash
fastp -i reads_R1.fastq.gz -I reads_R2.fastq.gz \
    -o trimmed_R1.fq.gz -O trimmed_R2.fq.gz \
    --detect_adapter_for_pe \
    --qualified_quality_phred 20 \
    --length_required 50 \
    --html qc_report.html
```

### Step 2: Assembly with SPAdes

```bash
# Standard bacterial assembly
spades.py \
    -1 trimmed_R1.fq.gz \
    -2 trimmed_R2.fq.gz \
    -o spades_output \
    --careful \
    -t 16 \
    -m 64

# For isolate genomes
spades.py --isolate \
    -1 trimmed_R1.fq.gz \
    -2 trimmed_R2.fq.gz \
    -o spades_output \
    -t 16
```

### Step 3: Polishing with Pilon

```bash
# Align reads to assembly
bwa index spades_output/scaffolds.fasta
bwa mem -t 16 spades_output/scaffolds.fasta \
    trimmed_R1.fq.gz trimmed_R2.fq.gz | \
    samtools sort -@ 4 -o aligned.bam
samtools index aligned.bam

# Polish
pilon --genome spades_output/scaffolds.fasta \
    --frags aligned.bam \
    --output polished \
    --threads 16
```

## Path B: Long-Read Assembly (Flye)

### Step 1: QC

```bash
# NanoPlot for long-read QC
NanoPlot --fastq reads.fastq.gz \
    --outdir nanoplot_output \
    --threads 8
```

### Step 2: Assembly with Flye

```bash
# ONT raw reads
flye --nano-raw reads.fastq.gz \
    --out-dir flye_output \
    --threads 16 \
    --genome-size 5m

# ONT HQ reads (sup/dna_r10)
flye --nano-hq reads.fastq.gz \
    --out-dir flye_output \
    --threads 16 \
    --genome-size 5m

# PacBio HiFi
flye --pacbio-hifi reads.fastq.gz \
    --out-dir flye_output \
    --threads 16 \
    --genome-size 5m
```

### Step 3: Polishing with medaka

```bash
# Polish with medaka (for ONT)
medaka_consensus \
    -i reads.fastq.gz \
    -d flye_output/assembly.fasta \
    -o medaka_output \
    -t 16 \
    -m r1041_e82_400bps_sup_v4.3.0  # Match your basecalling model
```

## Path C: Hybrid Assembly

```bash
# Flye with long reads, then polish with short reads
flye --nano-hq long_reads.fastq.gz \
    --out-dir flye_output \
    --threads 16 \
    --genome-size 5m

# Polish with short reads using Pilon
bwa index flye_output/assembly.fasta
bwa mem -t 16 flye_output/assembly.fasta \
    short_R1.fq.gz short_R2.fq.gz | \
    samtools sort -@ 4 -o aligned.bam
samtools index aligned.bam

pilon --genome flye_output/assembly.fasta \
    --frags aligned.bam \
    --output hybrid_polished \
    --threads 16
```

## Step 4: Quality Assessment

### QUAST

```bash
quast.py polished.fasta \
    -r reference.fasta \
    -g genes.gff \
    -o quast_output \
    -t 8

# Without reference
quast.py polished.fasta \
    -o quast_output \
    -t 8
```

### BUSCO

```bash
# Download lineage database
busco --download bacteria_odb10

# Run BUSCO
busco -i polished.fasta \
    -l bacteria_odb10 \
    -o busco_output \
    -m genome \
    -c 8
```

## Parameter Recommendations

| Tool | Parameter | Bacteria | Eukaryote |
|------|-----------|----------|-----------|
| SPAdes | --careful | Yes | Optional |
| SPAdes | -m | 64GB | 256GB+ |
| Flye | --genome-size | 5m | Species-specific |
| Flye | --meta | If metagenome | No |
| BUSCO | -l | bacteria_odb10 | eukaryota_odb10 |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Fragmented assembly | Low coverage, repetitive genome | Increase coverage, use long reads |
| Low N50 | Short reads only | Add long reads for scaffolding |
| Low BUSCO | Incomplete assembly, wrong lineage | Check coverage, try different lineage |
| Assembly too large | Contamination, heterozygosity | Filter reads, check for contamination |

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

THREADS=16
GENOME_SIZE="5m"
LONG_READS="long_reads.fastq.gz"
SHORT_R1="short_R1.fastq.gz"
SHORT_R2="short_R2.fastq.gz"
BUSCO_LINEAGE="bacteria_odb10"
OUTDIR="assembly_results"

mkdir -p ${OUTDIR}/{qc,assembly,polished,quast,busco}

# Step 1: QC
echo "=== QC ==="
NanoPlot --fastq ${LONG_READS} --outdir ${OUTDIR}/qc/nanoplot -t ${THREADS}
fastp -i ${SHORT_R1} -I ${SHORT_R2} \
    -o ${OUTDIR}/qc/short_R1.fq.gz -O ${OUTDIR}/qc/short_R2.fq.gz \
    --html ${OUTDIR}/qc/fastp.html

# Step 2: Assembly with Flye
echo "=== Assembly ==="
flye --nano-hq ${LONG_READS} \
    --out-dir ${OUTDIR}/assembly \
    --threads ${THREADS} \
    --genome-size ${GENOME_SIZE}

# Step 3: Polish with short reads
echo "=== Polishing ==="
bwa index ${OUTDIR}/assembly/assembly.fasta
bwa mem -t ${THREADS} ${OUTDIR}/assembly/assembly.fasta \
    ${OUTDIR}/qc/short_R1.fq.gz ${OUTDIR}/qc/short_R2.fq.gz | \
    samtools sort -@ 4 -o ${OUTDIR}/polished/aligned.bam
samtools index ${OUTDIR}/polished/aligned.bam

pilon --genome ${OUTDIR}/assembly/assembly.fasta \
    --frags ${OUTDIR}/polished/aligned.bam \
    --output ${OUTDIR}/polished/final \
    --threads ${THREADS}

# Step 4: QC
echo "=== Quality Assessment ==="
quast.py ${OUTDIR}/polished/final.fasta -o ${OUTDIR}/quast -t ${THREADS}
busco -i ${OUTDIR}/polished/final.fasta -l ${BUSCO_LINEAGE} \
    -o busco -m genome -c ${THREADS} --out_path ${OUTDIR}

echo "=== Assembly Complete ==="
echo "Final assembly: ${OUTDIR}/polished/final.fasta"
cat ${OUTDIR}/quast/report.txt
```

## Related Skills

- genome-assembly/short-read-assembly - SPAdes details
- genome-assembly/long-read-assembly - Flye, Canu, Hifiasm
- genome-assembly/assembly-polishing - Pilon, medaka, Racon
- genome-assembly/assembly-qc - QUAST, BUSCO metrics
