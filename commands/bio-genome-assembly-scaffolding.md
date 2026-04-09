# bio-genome-assembly-scaffolding

> Scaffold contigs into chromosome-level assemblies using Hi-C data with YaHS, 3D-DNA, SALSA2, and validate with BUSCO and contact maps. Use when scaffolding contigs to chromosome-level assemblies.

**Available tools:** Read, Bash

# Genome Scaffolding

## Hi-C Data Preprocessing

```bash
# Align Hi-C reads to draft assembly
bwa index draft_assembly.fa
bwa mem -5SP -t 16 draft_assembly.fa hic_R1.fq.gz hic_R2.fq.gz | \
    samtools view -@ 8 -bhS - > aligned.bam

# Filter for Hi-C contacts (pairtools)
pairtools parse --min-mapq 40 --walks-policy 5unique --max-inter-align-gap 30 \
    --nproc-in 8 --nproc-out 8 --chroms-path draft_assembly.fa.fai aligned.bam | \
    pairtools sort --nproc 8 | \
    pairtools dedup --nproc 8 --mark-dups | \
    pairtools split --output-pairs contacts.pairs.gz
```

## YaHS Scaffolding (Recommended)

```bash
# Index assembly
samtools faidx draft_assembly.fa

# Convert BAM to BED
bedtools bamtobed -i aligned.bam | sort -k4 > aligned.bed

# Run YaHS
yahs draft_assembly.fa aligned.bed -o scaffolds

# Output files:
# scaffolds_scaffolds_final.fa - final scaffolds
# scaffolds_scaffolds_final.agp - AGP file
# scaffolds.bin - contact matrix
```

## YaHS with Error Correction

```bash
# Run with error correction
yahs draft_assembly.fa aligned.bed -o scaffolds --no-contig-ec

# Generate contact map for juicebox
juicer pre scaffolds.bin scaffolds_scaffolds_final.agp draft_assembly.fa.fai | \
    sort -k2,2d -k6,6d -T ./ --parallel=8 -S 50G | \
    awk 'NF' > scaffolds.pre.txt

# Create .hic file
java -Xmx48G -jar juicer_tools.jar pre scaffolds.pre.txt scaffolds.hic \
    <(cut -f1,2 scaffolds_scaffolds_final.fa.fai)
```

## 3D-DNA Pipeline

```bash
# Prepare input (requires Juicer aligned data)
# Run Juicer first to get merged_nodups.txt

# Run 3D-DNA
run-asm-pipeline.sh -r 2 draft_assembly.fa merged_nodups.txt

# Output: draft_assembly.final.fasta

# Generate review assembly for Juicebox
run-asm-pipeline-post-review.sh -r draft_assembly.final.review.assembly \
    draft_assembly.final.fasta merged_nodups.txt
```

## SALSA2 Scaffolding

```bash
# Run SALSA2
python run_pipeline.py -a draft_assembly.fa -l draft_assembly.fa.fai \
    -b aligned.bed -e GATC -o salsa_output -m yes

# With multiple restriction enzymes
python run_pipeline.py -a draft_assembly.fa -l draft_assembly.fa.fai \
    -b aligned.bed -e GATC,GANTC -o salsa_output -m yes -p yes
```

## Generate Contact Map

```bash
# Using cooler
cooler cload pairs -c1 2 -p1 3 -c2 4 -p2 5 \
    draft_assembly.fa.fai:10000 contacts.pairs.gz scaffolds.cool

# Balance matrix
cooler balance scaffolds.cool

# Multi-resolution (mcool)
cooler zoomify scaffolds.cool -o scaffolds.mcool
```

## Visualize with HiGlass

```bash
# Convert to higlass format
clodius aggregate bedfile --chromsizes-filename chrom.sizes \
    --output-file scaffolds.beddb scaffold_boundaries.bed

# Load into higlass server
docker run --detach --publish 8888:80 \
    --volume ~/hg-data:/data \
    higlass/higlass-docker:latest
```

## Manual Curation (Juicebox)

```bash
# Load .hic file in Juicebox Assembly Tools (JBAT)
# Perform manual corrections:
# - Break misjoins
# - Order/orient scaffolds
# - Merge scaffolds

# Export corrected assembly
# File -> Export Assembly -> FASTA
```

## Post-Scaffolding Gap Filling

```bash
# TGS-GapCloser for long-read gap filling
tgsgapcloser --scaff scaffolds.fa --reads ont_reads.fq.gz \
    --output filled --thread 16 --ne

# LR_Gapcloser alternative
LR_Gapcloser.sh -i scaffolds.fa -l ont_reads.fq.gz -t 16 -o gapclosed.fa
```

## Validate Scaffolding

```bash
# Check chromosome-scale contiguity
seqkit stats scaffolds.fa

# BUSCO on scaffolds
busco -i scaffolds.fa -l eukaryota_odb10 -o busco_scaffolds -m genome -c 16

# N50/L50 statistics
assembly-stats scaffolds.fa

# Compare pre/post scaffolding
quast.py draft_assembly.fa scaffolds.fa -o quast_comparison
```

## Check Telomeres

```bash
# Find telomeric repeats (vertebrate TTAGGG)
seqkit locate -i -p 'TTAGGG{10,}' scaffolds.fa > telomeres_forward.bed
seqkit locate -i -p 'CCCTAA{10,}' scaffolds.fa > telomeres_reverse.bed

# Count chromosomes with telomeres on both ends
awk '$2 < 1000' telomeres_forward.bed | cut -f1 | sort -u > left_telomeres.txt
awk -v OFS='\t' 'NR==FNR{len[$1]=$2;next} $3 > len[$1]-1000' \
    scaffolds.fa.fai telomeres_reverse.bed | cut -f1 | sort -u > right_telomeres.txt
comm -12 left_telomeres.txt right_telomeres.txt > complete_chromosomes.txt
```

## Rename to Chromosomes

```bash
# After manual curation, rename scaffolds to chromosomes
awk '/^>/{print ">chr" ++i; next}{print}' scaffolds.fa > chromosomes.fa

# Or with mapping file
seqkit replace -p '(.+)' -r '{kv}' -k name_mapping.tsv scaffolds.fa > chromosomes.fa
```

## Related Skills

- genome-assembly/long-read-assembly - Generate initial contigs
- genome-assembly/assembly-polishing - Polish before scaffolding
- genome-assembly/assembly-qc - Validate final assembly
- hi-c-analysis/hic-data-io - Hi-C data processing
