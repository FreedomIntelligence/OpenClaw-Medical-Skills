# bio-splicing-pipeline

> End-to-end alternative splicing analysis from FASTQ to differential splicing results. Aligns with STAR 2-pass mode, performs junction QC, runs rMATS-turbo for differential analysis, and generates sashimi visualizations. Use when performing comprehensive splicing analysis from raw RNA-seq data.

**Available tools:** Read, Bash

# Alternative Splicing Analysis Pipeline

Complete workflow from raw RNA-seq to differential splicing results.

## Pipeline Overview

```
FASTQ → Read QC → STAR 2-pass → Junction QC → rMATS-turbo → Results → Visualization
                                    ↓
                            (Optional) IsoformSwitchAnalyzeR
```

## Step 1: Read Quality Control

```bash
# fastp for adapter trimming and quality filtering
fastp \
    -i sample_R1.fastq.gz \
    -I sample_R2.fastq.gz \
    -o sample_clean_R1.fastq.gz \
    -O sample_clean_R2.fastq.gz \
    --detect_adapter_for_pe \
    --thread 8 \
    -h sample_fastp.html
```

## Step 2: STAR 2-Pass Alignment

```bash
# First pass to detect novel junctions
STAR \
    --runThreadN 8 \
    --genomeDir star_index/ \
    --readFilesIn sample_R1.fastq.gz sample_R2.fastq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix sample_pass1_ \
    --outSAMtype BAM Unsorted \
    --outSJfilterOverhangMin 8 8 8 8 \
    --alignSJDBoverhangMin 1

# Generate new index with discovered junctions
# (Combine SJ.out.tab files from all samples)
cat *_SJ.out.tab > combined_SJ.out.tab

# Second pass with combined junctions
STAR \
    --runThreadN 8 \
    --genomeDir star_index/ \
    --readFilesIn sample_R1.fastq.gz sample_R2.fastq.gz \
    --readFilesCommand zcat \
    --sjdbFileChrStartEnd combined_SJ.out.tab \
    --outFileNamePrefix sample_ \
    --outSAMtype BAM SortedByCoordinate \
    --outSJfilterOverhangMin 8 8 8 8 \
    --alignSJDBoverhangMin 1 \
    --quantMode GeneCounts
```

## Step 3: Junction QC Checkpoint

```python
import subprocess

def check_junction_saturation(bam_file, bed_file, output_prefix):
    '''
    QC Checkpoint: Verify junction detection saturation.
    Plateau indicates sufficient depth for splicing analysis.
    '''
    subprocess.run([
        'junction_saturation.py',
        '-i', bam_file,
        '-r', bed_file,
        '-o', output_prefix
    ], check=True)

    # Manual check: curves should plateau
    print(f'Check {output_prefix}.junctionSaturation_plot.pdf')
    print('If curves still rising, consider deeper sequencing')
```

## Step 4: Differential Splicing with rMATS-turbo

```bash
# Create sample list files
# condition1_bams.txt: sample1.bam,sample2.bam,sample3.bam
# condition2_bams.txt: sample4.bam,sample5.bam,sample6.bam

rmats.py \
    --b1 condition1_bams.txt \
    --b2 condition2_bams.txt \
    --gtf annotation.gtf \
    -t paired \
    --readLength 150 \
    --nthread 8 \
    --od rmats_output \
    --tmp rmats_tmp
```

## Step 5: Filter Results

```python
import pandas as pd

def filter_differential_splicing(rmats_dir, event_type='SE',
                                  fdr_cutoff=0.05, dpsi_cutoff=0.1, min_reads=10):
    '''
    Filter rMATS results for significant events.

    Thresholds:
    - |deltaPSI| > 0.1 (lenient) or > 0.2 (stringent)
    - FDR < 0.05
    - Junction reads >= 10
    '''
    jc_file = f'{rmats_dir}/{event_type}.MATS.JC.txt'
    df = pd.read_csv(jc_file, sep='\t')

    significant = df[
        (df['FDR'] < fdr_cutoff) &
        (df['IncLevelDifference'].abs() > dpsi_cutoff)
    ].copy()

    print(f'Significant {event_type} events: {len(significant)}')

    # Sort by significance and effect size
    significant['score'] = -significant['FDR'].apply(lambda x: max(x, 1e-300)).apply(
        lambda x: __import__('numpy').log10(x)
    ) * significant['IncLevelDifference'].abs()

    return significant.sort_values('score', ascending=False)
```

## Step 6: Optional Isoform Switching

```r
library(IsoformSwitchAnalyzeR)

# Import Salmon quantification if available
switchList <- importRdata(
    isoformCountMatrix = counts,
    isoformRepExpression = tpm,
    designMatrix = design,
    isoformExonAnnoation = 'annotation.gtf',
    isoformNtFasta = 'transcripts.fa'
)

# Analyze switches
switchList <- isoformSwitchTestDEXSeq(switchList, reduceToSwitchingGenes = TRUE)
```

## Step 7: Sashimi Visualization

```python
import subprocess

def visualize_top_events(rmats_dir, grouping_file, gtf_file, output_dir, n_top=20):
    '''Generate sashimi plots for top differential events.'''
    import pandas as pd
    from pathlib import Path

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for event_type in ['SE', 'A5SS', 'A3SS', 'MXE', 'RI']:
        jc_file = f'{rmats_dir}/{event_type}.MATS.JC.txt'
        df = pd.read_csv(jc_file, sep='\t')
        sig = df[(df['FDR'] < 0.05) & (df['IncLevelDifference'].abs() > 0.1)]

        for idx, event in sig.head(n_top).iterrows():
            chrom = event['chr']
            start = event.get('upstreamES', event.get('1stExonStart_0base', 0)) - 500
            end = event.get('downstreamEE', event.get('2ndExonEnd', 0)) + 500
            gene = event['geneSymbol']

            subprocess.run([
                'ggsashimi.py',
                '-b', grouping_file,
                '-c', f'{chrom}:{start}-{end}',
                '-o', f'{output_dir}/{event_type}_{gene}',
                '-g', gtf_file,
                '--shrink',
                '--fix-y-scale',
                '-M', '5'
            ], check=True)
```

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

# Configuration
SAMPLES="sample1 sample2 sample3 sample4 sample5 sample6"
CONDITIONS="control control control treatment treatment treatment"
GTF="annotation.gtf"
STAR_INDEX="star_index/"
THREADS=8

# Step 1: QC and trimming
for sample in $SAMPLES; do
    fastp -i ${sample}_R1.fq.gz -I ${sample}_R2.fq.gz \
          -o ${sample}_clean_R1.fq.gz -O ${sample}_clean_R2.fq.gz \
          --thread $THREADS
done

# Step 2: STAR 2-pass alignment
# ... (as above)

# Step 3: Junction QC
for sample in $SAMPLES; do
    junction_saturation.py -i ${sample}.bam -r annotation.bed -o ${sample}_junc
done

# Step 4: rMATS differential splicing
rmats.py --b1 control_bams.txt --b2 treatment_bams.txt \
         --gtf $GTF -t paired --readLength 150 --nthread $THREADS \
         --od rmats_output --tmp rmats_tmp

echo "Pipeline complete. Check rmats_output/ for results."
```

## Related Skills

- alternative-splicing/splicing-quantification - Quantification details
- alternative-splicing/differential-splicing - Analysis methods
- alternative-splicing/sashimi-plots - Visualization
- read-alignment/star-alignment - STAR alignment options
