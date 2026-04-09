# bio-chipseq-super-enhancers

> Identifies super-enhancers from H3K27ac ChIP-seq data using ROSE and related tools. Use when studying cell identity genes, cancer-associated regulatory elements, or master transcription factor binding regions that cluster into large enhancer domains.

## Version Compatibility

Reference examples tested with: GenomicRanges 1.54+, bedtools 2.31+, ggplot2 3.5+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Super-Enhancer Calling

**"Identify super-enhancers from H3K27ac ChIP-seq"** → Stitch nearby enhancer peaks and rank by signal to find large regulatory domains controlling cell identity genes.
- CLI: `ROSE_main.py -g hg38 -i peaks.gff -r chip.bam -c input.bam`

Identify super-enhancers (SEs) - large clusters of enhancers that control cell identity genes.

## Background

Super-enhancers are:
- Large clusters of enhancer regions
- Marked by H3K27ac, Med1, BRD4
- Control cell identity genes
- Often altered in disease/cancer

## ROSE (Rank Ordering of Super-Enhancers)

### Installation

```bash
git clone https://github.com/stjude/ROSE.git
cd ROSE
# Requires samtools, R, bedtools
```

### Input Requirements

1. **BAM file** - H3K27ac ChIP-seq aligned reads
2. **Peak file** - Called peaks (BED or GFF)
3. **Genome annotation** - TSS annotations

### Run ROSE

**Goal:** Identify super-enhancers by stitching nearby enhancer peaks and ranking by H3K27ac signal.

**Approach:** Run ROSE_main.py with a GFF peak file, ChIP-seq BAM, and optional input control to stitch enhancers within 12.5 kb, rank by signal, and identify the inflection point separating super-enhancers from typical enhancers.

```bash
# Basic usage
python ROSE_main.py \
    -g HG38 \
    -i peaks.gff \
    -r h3k27ac.bam \
    -o output_dir \
    -s 12500 \
    -t 2500

# With control/input
python ROSE_main.py \
    -g HG38 \
    -i peaks.gff \
    -r h3k27ac.bam \
    -c input.bam \
    -o output_dir
```

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `-s` | Stitching distance | 12500 bp |
| `-t` | TSS exclusion | 2500 bp |
| `-c` | Control BAM | None |

### Output Files

```
output_dir/
├── *_AllEnhancers.table.txt        # All enhancer regions
├── *_SuperEnhancers.table.txt      # Super-enhancers only
├── *_Enhancers_withSuper.bed       # BED with SE annotation
└── *_Plot_points.png               # Hockey stick plot
```

## Prepare Input Files

### Convert BED to GFF

```bash
# ROSE requires GFF format for peaks
awk 'BEGIN{OFS="\t"} {print $1,"peaks","enhancer",$2,$3,".",$6,".","ID="NR}' \
    peaks.bed > peaks.gff
```

### Filter Peaks for Enhancers

```bash
# Remove promoter peaks (within 2.5kb of TSS)
bedtools intersect -a peaks.bed -b promoters.bed -v > enhancer_peaks.bed
```

## Alternative: HOMER Super-Enhancers

```bash
# Call super-enhancers with HOMER
findPeaks tag_dir/ -style super -o auto

# Or from existing peaks
findPeaks tag_dir/ -style super -i input_tag_dir/ \
    -typical typical_enhancers.txt \
    -superSlope -1000 \
    > super_enhancers.txt
```

## Alternative: SEanalysis

```bash
# R-based analysis
Rscript << 'EOF'
library(SEanalysis)

# Load H3K27ac signal at enhancers
signal <- read.table('enhancer_signal.txt', header=TRUE)

# Rank and identify super-enhancers
se_result <- identifySE(signal$signal, method='ROSE')

# Get super-enhancer IDs
super_enhancers <- signal$id[se_result$is_super]
write.table(super_enhancers, 'super_enhancers.txt', quote=FALSE, row.names=FALSE)
EOF
```

## Custom Hockey Stick Analysis (R)

**Goal:** Classify enhancers as super-enhancers vs typical using a custom hockey stick plot and inflection-point detection.

**Approach:** Rank enhancers by normalized signal, compute the slope at each point, find where the tangent exceeds 1 (inflection point), and classify all enhancers above the inflection as super-enhancers.

```r
library(ggplot2)

# Load enhancer signal data
enhancers <- read.table('enhancer_signal.txt', header=TRUE)

# Rank by signal
enhancers <- enhancers[order(enhancers$signal), ]
enhancers$rank <- 1:nrow(enhancers)

# Find inflection point (tangent = 1)
# Normalize ranks and signal to 0-1
enhancers$rank_norm <- enhancers$rank / max(enhancers$rank)
enhancers$signal_norm <- enhancers$signal / max(enhancers$signal)

# Calculate slope at each point
n <- nrow(enhancers)
slopes <- diff(enhancers$signal_norm) / diff(enhancers$rank_norm)
inflection <- which(slopes > 1)[1]

# Classify
enhancers$type <- ifelse(enhancers$rank >= inflection, 'Super-Enhancer', 'Typical')

# Plot
ggplot(enhancers, aes(rank, signal, color = type)) +
    geom_point(size = 0.5) +
    scale_color_manual(values = c('Super-Enhancer' = 'red', 'Typical' = 'grey60')) +
    geom_vline(xintercept = inflection, linetype = 'dashed') +
    labs(x = 'Enhancer Rank', y = 'H3K27ac Signal', title = 'Super-Enhancer Identification') +
    theme_bw()

ggsave('hockey_stick_plot.pdf', width = 8, height = 6)

# Output super-enhancers
super_enhancers <- enhancers[enhancers$type == 'Super-Enhancer', ]
write.table(super_enhancers, 'super_enhancers.txt', sep = '\t', quote = FALSE, row.names = FALSE)
```

## Calculate Enhancer Signal

```bash
# Get H3K27ac signal at peak regions
bedtools multicov -bams h3k27ac.bam -bed enhancer_peaks.bed > enhancer_counts.txt

# Normalize by peak size
awk 'BEGIN{OFS="\t"} {
    size = $3 - $2
    rpm = ($NF / TOTAL_READS) * 1e6
    rpkm = rpm / (size / 1000)
    print $0, rpkm
}' enhancer_counts.txt > enhancer_signal.txt
```

## Downstream Analysis

### Gene Assignment

```bash
# Assign super-enhancers to nearest genes
bedtools closest -a super_enhancers.bed -b genes.bed -d > se_gene_assignment.txt
```

### Compare Conditions

**Goal:** Find super-enhancers gained or lost between two experimental conditions.

**Approach:** Convert super-enhancer tables to GRanges objects and use subsetByOverlaps with invert to identify condition-specific super-enhancers.

```r
# Load SE from two conditions
se1 <- read.table('condition1_SE.txt', header=TRUE)
se2 <- read.table('condition2_SE.txt', header=TRUE)

# Find differential super-enhancers
library(GenomicRanges)
gr1 <- makeGRangesFromDataFrame(se1)
gr2 <- makeGRangesFromDataFrame(se2)

# Gained in condition 2
gained <- subsetByOverlaps(gr2, gr1, invert=TRUE)

# Lost in condition 2
lost <- subsetByOverlaps(gr1, gr2, invert=TRUE)
```

### Enrichment of Disease Variants

```bash
# Check if GWAS SNPs enriched in super-enhancers
bedtools intersect -a gwas_snps.bed -b super_enhancers.bed -wa -wb > snps_in_SE.txt

# Calculate enrichment
total_snps=$(wc -l < gwas_snps.bed)
snps_in_se=$(wc -l < snps_in_SE.txt)
se_coverage=$(awk '{sum += $3-$2} END {print sum}' super_enhancers.bed)
genome_size=3000000000

expected=$(echo "$total_snps * $se_coverage / $genome_size" | bc -l)
enrichment=$(echo "$snps_in_se / $expected" | bc -l)
echo "Enrichment: $enrichment"
```

## Complete Workflow

```bash
#!/bin/bash
set -euo pipefail

H3K27AC_BAM=$1
PEAKS_BED=$2
OUTPUT_DIR=$3

mkdir -p $OUTPUT_DIR

echo "=== Convert peaks to GFF ==="
awk 'BEGIN{OFS="\t"} {print $1,"peaks","enhancer",$2,$3,".",$6,".","ID="NR}' \
    $PEAKS_BED > $OUTPUT_DIR/peaks.gff

echo "=== Run ROSE ==="
python ROSE_main.py \
    -g HG38 \
    -i $OUTPUT_DIR/peaks.gff \
    -r $H3K27AC_BAM \
    -o $OUTPUT_DIR \
    -s 12500 \
    -t 2500

echo "=== Summary ==="
n_typical=$(grep -c "Typical" $OUTPUT_DIR/*_AllEnhancers.table.txt || echo 0)
n_super=$(wc -l < $OUTPUT_DIR/*_SuperEnhancers.table.txt)

echo "Typical enhancers: $n_typical"
echo "Super-enhancers: $n_super"
```

## Related Skills

- chip-seq/peak-calling - Call H3K27ac peaks first
- chip-seq/peak-annotation - Annotate SE to genes
- chip-seq/differential-binding - Compare SE between conditions
- data-visualization/genome-tracks - Visualize SE regions
