# bio-read-alignment-star-alignment

> Align RNA-seq reads with STAR (Spliced Transcripts Alignment to a Reference). Supports two-pass mode for novel splice junction discovery. Use when aligning RNA-seq data requiring splice-aware alignment.

**Available tools:** Read, Bash

# STAR RNA-seq Alignment

## Generate Genome Index

```bash
# Basic index generation
STAR --runMode genomeGenerate \
    --runThreadN 8 \
    --genomeDir star_index/ \
    --genomeFastaFiles reference.fa \
    --sjdbGTFfile annotation.gtf \
    --sjdbOverhang 100    # Read length - 1
```

## Index with Specific Read Length

```bash
# For 150bp reads, use sjdbOverhang=149
STAR --runMode genomeGenerate \
    --runThreadN 8 \
    --genomeDir star_index_150/ \
    --genomeFastaFiles reference.fa \
    --sjdbGTFfile annotation.gtf \
    --sjdbOverhang 149
```

## Basic Alignment

```bash
# Paired-end alignment
STAR --runThreadN 8 \
    --genomeDir star_index/ \
    --readFilesIn reads_1.fq.gz reads_2.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate
```

## Single-End Alignment

```bash
STAR --runThreadN 8 \
    --genomeDir star_index/ \
    --readFilesIn reads.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate
```

## Two-Pass Mode

```bash
# Two-pass mode for better novel junction detection
STAR --runThreadN 8 \
    --genomeDir star_index/ \
    --readFilesIn r1.fq.gz r2.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate \
    --twopassMode Basic
```

## Quantification Mode

```bash
# Output gene counts (like featureCounts)
STAR --runThreadN 8 \
    --genomeDir star_index/ \
    --readFilesIn r1.fq.gz r2.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate \
    --quantMode GeneCounts
```

Output: `sample_ReadsPerGene.out.tab` with columns:
1. Gene ID
2. Unstranded counts
3. Forward strand counts
4. Reverse strand counts

## ENCODE Options

```bash
# ENCODE recommended settings
STAR --runThreadN 8 \
    --genomeDir star_index/ \
    --readFilesIn r1.fq.gz r2.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate \
    --outSAMunmapped Within \
    --outSAMattributes NH HI AS NM MD \
    --outFilterType BySJout \
    --outFilterMultimapNmax 20 \
    --outFilterMismatchNmax 999 \
    --outFilterMismatchNoverReadLmax 0.04 \
    --alignIntronMin 20 \
    --alignIntronMax 1000000 \
    --alignMatesGapMax 1000000 \
    --alignSJoverhangMin 8 \
    --alignSJDBoverhangMin 1
```

## Fusion Detection

```bash
# For chimeric/fusion detection
STAR --runThreadN 8 \
    --genomeDir star_index/ \
    --readFilesIn r1.fq.gz r2.fq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate \
    --chimSegmentMin 12 \
    --chimJunctionOverhangMin 8 \
    --chimOutType Junctions WithinBAM SoftClip \
    --chimMainSegmentMultNmax 1
```

## Output Files

| File | Description |
|------|-------------|
| *Aligned.sortedByCoord.out.bam | Sorted BAM file |
| *Log.final.out | Alignment summary statistics |
| *Log.out | Detailed log |
| *SJ.out.tab | Splice junctions |
| *ReadsPerGene.out.tab | Gene counts (if --quantMode) |
| *Chimeric.out.junction | Fusion candidates (if chimeric) |

## Memory Requirements

```bash
# Reduce memory for limited systems
STAR --genomeLoad NoSharedMemory \
    --limitBAMsortRAM 10000000000 \  # 10GB for sorting
    ...

# For very large genomes, limit during index generation
STAR --runMode genomeGenerate \
    --limitGenomeGenerateRAM 31000000000 \  # 31GB
    ...
```

## Shared Memory Mode

```bash
# Load genome into shared memory (for multiple samples)
STAR --genomeLoad LoadAndExit --genomeDir star_index/

# Run alignments (faster startup)
STAR --genomeLoad LoadAndKeep --genomeDir star_index/ ...

# Remove from memory when done
STAR --genomeLoad Remove --genomeDir star_index/
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| --runThreadN | 1 | Number of threads |
| --sjdbOverhang | 100 | Read length - 1 |
| --outFilterMultimapNmax | 10 | Max multi-mapping |
| --alignIntronMax | 0 | Max intron size |
| --outFilterMismatchNmax | 10 | Max mismatches |
| --outSAMtype | SAM | Output format |
| --quantMode | - | GeneCounts for counting |
| --twopassMode | None | Basic for two-pass |

## Related Skills

- rna-quantification/featurecounts-counting - Alternative counting
- rna-quantification/alignment-free-quant - Salmon/kallisto alternative
- differential-expression/deseq2-basics - Downstream DE analysis
- read-qc/fastp-workflow - Preprocess reads
