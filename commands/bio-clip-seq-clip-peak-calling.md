# bio-clip-seq-clip-peak-calling

> Call protein-RNA binding site peaks from CLIP-seq data using CLIPper, PureCLIP, or Piranha. Use when identifying RBP binding sites from aligned CLIP reads.

**Available tools:** Read, Bash

# CLIP-seq Peak Calling

## CLIPper (Recommended)

```bash
# Basic peak calling
clipper \
    -b deduped.bam \
    -s hg38 \
    -o peaks.bed \
    --save-pickle

# With FDR threshold
clipper \
    -b deduped.bam \
    -s hg38 \
    -o peaks.bed \
    --FDR 0.05 \
    --superlocal

# Specify gene annotations
clipper \
    -b deduped.bam \
    -s hg38 \
    --gene genes.bed \
    -o peaks.bed
```

## CLIPper Options

| Option | Description |
|--------|-------------|
| -b | Input BAM file |
| -s | Species (hg38, mm10) |
| -o | Output BED file |
| --FDR | FDR threshold (default 0.05) |
| --superlocal | Use superlocal background |
| --gene | Custom gene annotation BED |
| --save-pickle | Save intermediate data |

## PureCLIP (HMM-Based)

PureCLIP uses an HMM to model crosslink sites, incorporating enrichment and truncation signals.

```bash
# Installation
conda install -c bioconda pureclip

# Basic peak calling
pureclip \
    -i deduped.bam \
    -bai deduped.bam.bai \
    -g genome.fa \
    -o crosslink_sites.bed \
    -or binding_regions.bed \
    -nt 4

# -nt 4: Number of threads. Adjust based on CPU cores.
# -o: Single-nucleotide crosslink sites
# -or: Broader binding regions
```

### PureCLIP Options

| Option | Description |
|--------|-------------|
| -i | Input BAM file |
| -bai | BAM index file |
| -g | Reference genome FASTA |
| -o | Crosslink sites output |
| -or | Binding regions output |
| -nt | Number of threads |
| -iv | Interval file to restrict analysis |
| -dm | Min distance for merging |

### PureCLIP with Input Control

```bash
# With SMInput control BAM
pureclip \
    -i clip.bam \
    -bai clip.bam.bai \
    -g genome.fa \
    -ibam sminput.bam \
    -ibai sminput.bam.bai \
    -o crosslinks.bed \
    -or regions.bed \
    -nt 8

# -ibam/-ibai: Input control BAM for background modeling
```

### PureCLIP Output

```bash
# Crosslink sites BED contains:
# chr start end name score strand

# Score interpretation:
# Higher scores = more confident crosslink sites

# Filter by score
# score>=3: Medium confidence. Use 5+ for high confidence.
awk '$5 >= 3' crosslink_sites.bed > filtered_sites.bed
```

### PureCLIP for Different CLIP Types

```bash
# eCLIP (recommended settings)
pureclip -i eclip.bam -bai eclip.bam.bai -g genome.fa \
    -o sites.bed -or regions.bed -nt 4 -dm 8

# iCLIP (single-nucleotide resolution)
pureclip -i iclip.bam -bai iclip.bam.bai -g genome.fa \
    -o sites.bed -or regions.bed -nt 4

# PAR-CLIP (T-to-C transitions)
pureclip -i parclip.bam -bai parclip.bam.bai -g genome.fa \
    -o sites.bed -or regions.bed -nt 4
```

## Piranha

```bash
# Basic usage
Piranha -s deduped.bam -o peaks.bed

# With p-value threshold
Piranha -s deduped.bam -o peaks.bed -p 0.01

# Stranded analysis
Piranha -s deduped.bam -o peaks.bed -p 0.01 -u

# Zero-truncated negative binomial
Piranha -s deduped.bam -o peaks.bed -d ZeroTruncatedNegativeBinomial
```

## PEAKachu (for PAR-CLIP)

```bash
# PAR-CLIP specific caller
peakachu adaptive \
    -c control.bam \
    -t treatment.bam \
    -r reference.fa \
    -o peakachu_peaks.gff
```

## MACS3 for CLIP (Alternative)

```bash
# Use narrow peak calling mode
macs3 callpeak \
    -t deduped.bam \
    -f BAM \
    -g hs \
    -n clip_peaks \
    --nomodel \
    --extsize 50 \
    -q 0.01
```

## Strand-Specific Peak Calling

```bash
# Split BAM by strand
samtools view -h -F 16 deduped.bam | samtools view -Sb - > plus_strand.bam
samtools view -h -f 16 deduped.bam | samtools view -Sb - > minus_strand.bam

# Call peaks on each strand
clipper -b plus_strand.bam -s hg38 -o peaks_plus.bed
clipper -b minus_strand.bam -s hg38 -o peaks_minus.bed

# Combine
cat peaks_plus.bed peaks_minus.bed | sort -k1,1 -k2,2n > peaks_all.bed
```

## Filter Peaks

```bash
# By score
awk '$5 >= 10' peaks.bed > peaks_filtered.bed

# By size
awk '($3 - $2) >= 20 && ($3 - $2) <= 200' peaks.bed > peaks_sized.bed

# By read count (if in name field)
awk '$5 >= 5' peaks.bed > peaks_min5reads.bed
```

## Merge Replicates

```bash
# Use bedtools to find consensus peaks
bedtools intersect -a rep1_peaks.bed -b rep2_peaks.bed -wa | \
    sort -u > consensus_peaks.bed

# Require overlap in N replicates
bedtools multiinter -i rep1.bed rep2.bed rep3.bed | \
    awk '$4 >= 2' | \
    bedtools merge > consensus_peaks.bed
```

## Peak Metrics

```python
import pandas as pd

def load_clip_peaks(bed_path):
    peaks = pd.read_csv(bed_path, sep='\t', header=None,
                        names=['chrom', 'start', 'end', 'name', 'score', 'strand'])
    return peaks

def peak_stats(peaks):
    stats = {
        'n_peaks': len(peaks),
        'mean_width': (peaks['end'] - peaks['start']).mean(),
        'median_score': peaks['score'].median(),
        'peaks_per_chrom': peaks.groupby('chrom').size().to_dict()
    }
    return stats

peaks = load_clip_peaks('peaks.bed')
print(peak_stats(peaks))
```

## Quality Metrics

| Metric | Good Value | Description |
|--------|------------|-------------|
| Peak count | 1,000-50,000 | Depends on RBP |
| Peak width | 20-100 nt | Typical for RBP footprint |
| FRiP | >0.1 | Fraction reads in peaks |

## Calculate FRiP

```bash
# Reads in peaks
reads_in_peaks=$(bedtools intersect -a deduped.bam -b peaks.bed -u | samtools view -c -)

# Total reads
total_reads=$(samtools view -c deduped.bam)

# FRiP
frip=$(echo "scale=4; $reads_in_peaks / $total_reads" | bc)
echo "FRiP: $frip"
```

## Related Skills

- clip-alignment - Generate aligned BAM
- clip-preprocessing - UMI deduplication
- binding-site-annotation - Annotate peaks with gene features
- clip-motif-analysis - Find enriched motifs in peaks
