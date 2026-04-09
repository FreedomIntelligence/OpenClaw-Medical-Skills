# bio-genome-assembly-metagenome-assembly

> Metagenome assembly from long reads using metaFlye and metaSPAdes with binning strategies. Use when reconstructing genomes from microbial communities, recovering metagenome-assembled genomes (MAGs), or resolving strain-level variation in complex samples.

**Available tools:** Read, Bash

# Metagenome Assembly

## Overview

Metagenome assembly reconstructs genomes from mixed microbial communities. Long reads enable recovery of complete circular genomes and resolution of strain-level differences.

## metaFlye (Long Reads)

```bash
# ONT metagenome assembly
flye --nano-raw reads.fastq.gz \
    --meta \
    --out-dir flye_meta \
    --threads 32

# PacBio HiFi metagenome
flye --pacbio-hifi reads.hifi.fastq.gz \
    --meta \
    --out-dir flye_meta_hifi \
    --threads 32

# Key output files:
# assembly.fasta - assembled contigs
# assembly_graph.gfa - assembly graph
# assembly_info.txt - contig statistics
```

## metaSPAdes (Short Reads)

```bash
# Illumina paired-end metagenome
metaspades.py -1 R1.fastq.gz -2 R2.fastq.gz \
    -o spades_meta \
    -t 32 \
    -m 500

# With multiple libraries
metaspades.py \
    --pe1-1 lib1_R1.fq.gz --pe1-2 lib1_R2.fq.gz \
    --pe2-1 lib2_R1.fq.gz --pe2-2 lib2_R2.fq.gz \
    -o spades_meta -t 32
```

## Hybrid Assembly

```bash
# Combine short and long reads
flye --nano-raw ont_reads.fastq.gz \
    --meta \
    --out-dir flye_hybrid \
    --threads 32

# Polish with short reads
pilon --genome flye_hybrid/assembly.fasta \
    --frags short_reads.bam \
    --output polished \
    --threads 16
```

## Key Parameters

### metaFlye

| Parameter | Description |
|-----------|-------------|
| --meta | Metagenome mode (handles uneven coverage) |
| --min-overlap | Minimum overlap for assembly (default: auto) |
| --genome-size | Estimated total size (optional for meta) |
| --iterations | Polishing iterations (default: 1) |
| --keep-haplotypes | Preserve strain variants |

### metaSPAdes

| Parameter | Description |
|-----------|-------------|
| -m | Memory limit in GB |
| --only-assembler | Skip error correction |
| -k | K-mer sizes (auto-selected by default) |
| --phred-offset | Quality encoding (33 or 64) |

## Binning Workflow

```bash
# Step 1: Map reads back to assembly
minimap2 -ax map-ont -t 32 assembly.fasta reads.fastq.gz | \
    samtools sort -o mapped.bam -

# Step 2: Generate depth file
jgi_summarize_bam_contig_depths --outputDepth depth.txt mapped.bam

# Step 3: Bin with MetaBAT2
metabat2 -i assembly.fasta -a depth.txt -o bins/bin -t 32

# Step 4: Assess bin quality with CheckM2
checkm2 predict --input bins/ --output-directory checkm2_out -x fa --threads 32
```

## SemiBin2 (Deep Learning Binning)

```bash
# Single-sample binning
SemiBin2 single_easy_bin \
    -i assembly.fasta \
    -b mapped.bam \
    -o semibin_out \
    --environment global

# Multi-sample binning (better for time-series)
SemiBin2 multi_easy_bin \
    -i assembly.fasta \
    -b sample1.bam sample2.bam sample3.bam \
    -o semibin_multi
```

## Quality Assessment

```bash
# Assembly stats
seqkit stats assembly.fasta

# CheckM2 for bin completeness
checkm2 predict -i bins/ -o checkm2_out -x fa -t 32

# GTDB-Tk for taxonomic classification
gtdbtk classify_wf --genome_dir bins/ --out_dir gtdbtk_out --cpus 32

# QUAST for assembly metrics
metaquast.py -o metaquast_out assembly.fasta -t 32
```

## Circular Genome Detection

```bash
# Flye marks circular contigs in assembly_info.txt
grep "Y" flye_meta/assembly_info.txt | cut -f1 > circular_contigs.txt

# Extract circular contigs
seqkit grep -f circular_contigs.txt assembly.fasta > circular_genomes.fasta
```

## Python Pipeline

```python
import subprocess
from pathlib import Path
import pandas as pd

def run_metaflye(reads, output_dir, read_type='nano-raw', threads=32):
    cmd = ['flye', f'--{read_type}', reads, '--meta', '--out-dir', output_dir, '--threads', str(threads)]
    subprocess.run(cmd, check=True)
    return Path(output_dir) / 'assembly.fasta'

def run_binning(assembly, bam, output_dir, threads=32):
    depth_file = Path(output_dir) / 'depth.txt'
    subprocess.run(['jgi_summarize_bam_contig_depths', '--outputDepth', str(depth_file), bam], check=True)

    bins_dir = Path(output_dir) / 'bins'
    bins_dir.mkdir(exist_ok=True)
    subprocess.run(['metabat2', '-i', assembly, '-a', str(depth_file), '-o', str(bins_dir / 'bin'), '-t', str(threads)], check=True)

    return bins_dir

def assess_bins(bins_dir, output_dir, threads=32):
    subprocess.run(['checkm2', 'predict', '--input', str(bins_dir), '--output-directory', output_dir, '-x', 'fa', '--threads', str(threads)], check=True)

    results = pd.read_csv(Path(output_dir) / 'quality_report.tsv', sep='\t')
    high_quality = results[(results['Completeness'] > 90) & (results['Contamination'] < 5)]
    return high_quality

# Example workflow
assembly = run_metaflye('ont_reads.fq.gz', 'flye_out')
bins = run_binning(str(assembly), 'mapped.bam', 'binning_out')
hq_bins = assess_bins(bins, 'checkm2_out')
print(f'High-quality MAGs: {len(hq_bins)}')
```

## Expected Outputs

| Metric | Good Assembly |
|--------|---------------|
| N50 | >50 kb |
| Largest contig | >1 Mb |
| HQ MAGs (>90% complete, <5% contam) | Varies by sample |
| Circular genomes | Sample dependent |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Few long contigs | Increase read depth or length |
| High chimeric rate | Use --keep-haplotypes in Flye |
| Poor binning | Add more samples for differential coverage |
| Missing taxa | Check read QC; consider targeted enrichment |

## Related Skills

- genome-assembly/contamination-detection - CheckM2/GUNC
- metagenomics/taxonomic-profiling - Kraken2/Bracken
- metagenomics/functional-profiling - HUMAnN
- long-read-sequencing/read-qc - Input quality control
