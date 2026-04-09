# bio-epitranscriptomics-merip-preprocessing

> Align and QC MeRIP-seq IP and input samples for m6A analysis. Use when preparing MeRIP-seq data for peak calling or differential methylation analysis.

**Available tools:** Read, Bash

# MeRIP-seq Preprocessing

## Alignment with STAR

```bash
# Build index (once)
STAR --runMode genomeGenerate \
    --genomeDir star_index \
    --genomeFastaFiles genome.fa \
    --sjdbGTFfile genes.gtf

# Align IP and input samples
for sample in IP_rep1 IP_rep2 Input_rep1 Input_rep2; do
    STAR --genomeDir star_index \
        --readFilesIn ${sample}_R1.fastq.gz ${sample}_R2.fastq.gz \
        --readFilesCommand zcat \
        --outSAMtype BAM SortedByCoordinate \
        --outFileNamePrefix ${sample}_
done
```

## QC Metrics

```bash
# Index BAMs
for bam in *Aligned.sortedByCoord.out.bam; do
    samtools index $bam
done

# Check IP enrichment
# Good MeRIP: IP should have peaks, input should be uniform
samtools flagstat IP_rep1_Aligned.sortedByCoord.out.bam
```

## IP/Input Correlation

```python
import deeptools.plotCorrelation as pc

# Check replicate correlation
multiBamSummary bins \
    -b IP_rep1.bam IP_rep2.bam Input_rep1.bam Input_rep2.bam \
    -o results.npz

plotCorrelation -in results.npz \
    --corMethod spearman \
    -o correlation.png
```

## Related Skills

- read-qc/quality-reports - Raw read quality assessment
- read-alignment/star-alignment - General alignment concepts
- m6a-peak-calling - Next step after preprocessing
