# bio-clip-seq-clip-alignment

> Align CLIP-seq reads to the genome with crosslink site awareness. Use when mapping preprocessed CLIP reads for peak calling.

**Available tools:** Read, Bash

# CLIP-seq Alignment

## STAR Alignment

```bash
STAR --runMode alignReads \
    --genomeDir STAR_index \
    --readFilesIn trimmed.fq.gz \
    --readFilesCommand zcat \
    --outFilterMultimapNmax 1 \
    --outFilterMismatchNmax 1 \
    --alignEndsType EndToEnd \
    --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix clip_
```

## Bowtie2 Alternative

```bash
bowtie2 -x genome_index \
    -U trimmed.fq.gz \
    --very-sensitive \
    -p 8 \
    | samtools view -bS - \
    | samtools sort -o aligned.bam
```

## Post-Alignment Processing

```bash
# Index
samtools index aligned.bam

# Deduplicate with UMIs
umi_tools dedup \
    --stdin=aligned.bam \
    --stdout=deduped.bam
```

## Related Skills

- clip-preprocessing - Prepare reads
- clip-peak-calling - Call peaks
