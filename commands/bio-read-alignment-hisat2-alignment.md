# bio-read-alignment-hisat2-alignment

> Align RNA-seq reads with HISAT2, a memory-efficient splice-aware aligner. Use when STAR's memory requirements are too high or for general RNA-seq alignment.

**Available tools:** Read, Bash

# HISAT2 RNA-seq Alignment

## Build Index

```bash
# Basic index (no annotation)
hisat2-build -p 8 reference.fa hisat2_index

# Index with splice sites and exons (recommended)
hisat2_extract_splice_sites.py annotation.gtf > splice_sites.txt
hisat2_extract_exons.py annotation.gtf > exons.txt

hisat2-build -p 8 \
    --ss splice_sites.txt \
    --exon exons.txt \
    reference.fa hisat2_index
```

## Basic Alignment

```bash
# Paired-end reads
hisat2 -p 8 -x hisat2_index \
    -1 reads_1.fq.gz -2 reads_2.fq.gz \
    -S aligned.sam

# Single-end reads
hisat2 -p 8 -x hisat2_index \
    -U reads.fq.gz \
    -S aligned.sam
```

## Direct to Sorted BAM

```bash
# Pipe to samtools
hisat2 -p 8 -x hisat2_index \
    -1 r1.fq.gz -2 r2.fq.gz | \
    samtools sort -@ 4 -o aligned.sorted.bam -

samtools index aligned.sorted.bam
```

## Stranded Libraries

```bash
# Forward stranded (e.g., Ligation)
hisat2 -p 8 -x hisat2_index \
    --rna-strandness FR \
    -1 r1.fq.gz -2 r2.fq.gz -S aligned.sam

# Reverse stranded (e.g., dUTP, TruSeq - most common)
hisat2 -p 8 -x hisat2_index \
    --rna-strandness RF \
    -1 r1.fq.gz -2 r2.fq.gz -S aligned.sam

# Single-end stranded
hisat2 -p 8 -x hisat2_index \
    --rna-strandness F \    # or R for reverse
    -U reads.fq.gz -S aligned.sam
```

## Novel Splice Junction Discovery

```bash
# Output novel splice junctions
hisat2 -p 8 -x hisat2_index \
    --novel-splicesite-outfile novel_splices.txt \
    -1 r1.fq.gz -2 r2.fq.gz -S aligned.sam

# Use known + novel junctions for subsequent alignments
hisat2 -p 8 -x hisat2_index \
    --novel-splicesite-infile novel_splices.txt \
    -1 r1.fq.gz -2 r2.fq.gz -S aligned.sam
```

## Two-Pass Alignment (Manual)

```bash
# Pass 1: Discover junctions from all samples
for r1 in *_R1.fq.gz; do
    r2=${r1/_R1/_R2}
    base=$(basename $r1 _R1.fq.gz)
    hisat2 -p 8 -x hisat2_index \
        --novel-splicesite-outfile ${base}_splices.txt \
        -1 $r1 -2 $r2 -S /dev/null
done

# Combine and filter junctions
cat *_splices.txt | sort -u > combined_splices.txt

# Pass 2: Realign with all junctions
for r1 in *_R1.fq.gz; do
    r2=${r1/_R1/_R2}
    base=$(basename $r1 _R1.fq.gz)
    hisat2 -p 8 -x hisat2_index \
        --novel-splicesite-infile combined_splices.txt \
        -1 $r1 -2 $r2 | \
        samtools sort -@ 4 -o ${base}.sorted.bam -
done
```

## Read Group Information

```bash
hisat2 -p 8 -x hisat2_index \
    --rg-id sample1 \
    --rg SM:sample1 \
    --rg PL:ILLUMINA \
    --rg LB:lib1 \
    -1 r1.fq.gz -2 r2.fq.gz -S aligned.sam
```

## Downstream Quantification

```bash
# Output name-sorted BAM for htseq-count
hisat2 -p 8 -x hisat2_index -1 r1.fq.gz -2 r2.fq.gz | \
    samtools sort -n -@ 4 -o aligned.namesorted.bam -

# Or coordinate-sorted for featureCounts
hisat2 -p 8 -x hisat2_index -1 r1.fq.gz -2 r2.fq.gz | \
    samtools sort -@ 4 -o aligned.sorted.bam -
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| -p | 1 | Number of threads |
| -x | - | Index basename |
| --rna-strandness | unstranded | FR/RF/F/R |
| --dta | off | Downstream transcriptome assembly |
| --dta-cufflinks | off | For Cufflinks |
| --min-intronlen | 20 | Minimum intron length |
| --max-intronlen | 500000 | Maximum intron length |
| -k | 5 | Max alignments to report |

## For StringTie/Cufflinks

```bash
# Use --dta for StringTie
hisat2 -p 8 -x hisat2_index \
    --dta \
    -1 r1.fq.gz -2 r2.fq.gz | \
    samtools sort -@ 4 -o aligned.sorted.bam -
```

## Alignment Summary

```bash
# HISAT2 prints summary to stderr
hisat2 -p 8 -x hisat2_index -1 r1.fq.gz -2 r2.fq.gz -S aligned.sam 2> summary.txt
```

Example:
```
50000000 reads; of these:
  50000000 (100.00%) were paired; of these:
    2500000 (5.00%) aligned concordantly 0 times
    45000000 (90.00%) aligned concordantly exactly 1 time
    2500000 (5.00%) aligned concordantly >1 times
95.00% overall alignment rate
```

## Memory Comparison

| Aligner | Human Genome Memory |
|---------|-------------------|
| STAR | ~30GB |
| HISAT2 | ~8GB |

## Related Skills

- read-alignment/star-alignment - Alternative with more features
- rna-quantification/featurecounts-counting - Count aligned reads
- rna-quantification/alignment-free-quant - Skip alignment entirely
- differential-expression/deseq2-basics - Downstream DE analysis
