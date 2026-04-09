# bio-chipseq-visualization

> Visualize ChIP-seq data using deepTools, Gviz, and ChIPseeker. Create heatmaps, profile plots, and genome browser tracks. Visualize signal around peaks, TSS, or custom regions. Use when visualizing ChIP-seq signal and peaks.

## Version Compatibility

Reference examples tested with: GenomicRanges 1.54+, deepTools 3.5+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# ChIP-seq Visualization

**"Create a heatmap of ChIP-seq signal around peaks"** → Generate signal heatmaps, profile plots, and genome browser tracks showing enrichment patterns around genomic features.
- CLI: `deeptools computeMatrix reference-point` → `plotHeatmap`
- R: `Gviz`, `ChIPseeker::plotAvgProf()`

## deepTools - Compute Matrix

**Goal:** Build a signal matrix of ChIP-seq coverage around reference points for downstream heatmaps and profiles.

**Approach:** Use computeMatrix to extract bigWig signal values in windows around genomic features like TSS.

```bash
# Compute signal matrix around TSS
computeMatrix reference-point \
    --referencePoint TSS \
    -b 3000 -a 3000 \              # 3kb upstream and downstream
    -R genes.bed \                  # Reference regions
    -S sample.bw \                  # Signal file (bigWig)
    -o matrix.gz \
    --outFileSortedRegions sorted_genes.bed
```

## deepTools - Scale-Regions

**Goal:** Visualize ChIP signal across gene bodies scaled to a uniform length.

**Approach:** Scale all gene regions to equal size and compute signal with flanking windows.

```bash
# Signal across gene bodies
computeMatrix scale-regions \
    -R genes.bed \
    -S sample1.bw sample2.bw \
    -b 3000 -a 3000 \              # Flanking regions
    -m 5000 \                       # Scaled body length
    -o matrix_scaled.gz
```

## deepTools - Heatmap

**Goal:** Generate a heatmap of ChIP-seq signal intensity across genomic regions.

**Approach:** Render the precomputed signal matrix as a clustered heatmap with optional profile summary.

```bash
# Generate heatmap from matrix
plotHeatmap \
    -m matrix.gz \
    -o heatmap.png \
    --colorMap RdBu \
    --whatToShow 'heatmap and colorbar' \
    --zMin -3 --zMax 3

# With profile on top
plotHeatmap \
    -m matrix.gz \
    -o heatmap_with_profile.png \
    --plotTitle 'H3K4me3 Signal' \
    --heatmapHeight 15 \
    --refPointLabel TSS
```

## deepTools - Profile Plot

**Goal:** Display average ChIP-seq signal profiles across genomic regions for sample comparison.

**Approach:** Plot mean signal from the computed matrix, optionally overlaying multiple samples.

```bash
# Average profile plot
plotProfile \
    -m matrix.gz \
    -o profile.png \
    --plotTitle 'Average Signal Profile' \
    --perGroup

# Multiple samples comparison
plotProfile \
    -m matrix_multi.gz \
    -o profile_compare.png \
    --colors red blue green \
    --plotTitle 'Sample Comparison'
```

## Create BigWig from BAM

**Goal:** Convert BAM alignments to normalized bigWig signal tracks for visualization.

**Approach:** Use bamCoverage for single-sample normalization or bamCompare for log2 ratio of ChIP over input.

```bash
# Normalized bigWig (CPM)
bamCoverage \
    -b sample.bam \
    -o sample.bw \
    --normalizeUsing CPM \
    --binSize 10 \
    --numberOfProcessors 8

# With input subtraction
bamCompare \
    -b1 chip.bam \
    -b2 input.bam \
    -o chip_vs_input.bw \
    --operation log2ratio \
    --binSize 50
```

## ChIPseeker Profile Heatmap (R)

**Goal:** Visualize peak distribution around TSS using ChIPseeker tag matrices and profile plots.

**Approach:** Build a tag density matrix from peak locations relative to promoter windows, then plot as heatmap or average profile.

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

# Load peaks
peaks <- readPeakFile('sample_peaks.narrowPeak')

# Get promoter regions
promoter <- getPromoters(TxDb = txdb, upstream = 3000, downstream = 3000)

# Compute tag matrix
tagMatrix <- getTagMatrix(peaks, windows = promoter)

# Heatmap
tagHeatmap(tagMatrix, xlim = c(-3000, 3000), color = 'red')

# Profile plot
plotAvgProf(tagMatrix, xlim = c(-3000, 3000), xlab = 'Distance from TSS (bp)',
            ylab = 'Peak Count Frequency')

# With confidence interval
plotAvgProf2(tagMatrix, xlim = c(-3000, 3000), conf = 0.95)
```

## Gviz - Genome Browser Tracks (R)

**Goal:** Create publication-quality genome browser views combining signal tracks, gene models, and ideograms.

**Approach:** Layer Gviz track objects (ideogram, axis, data, gene) and render a specific genomic region.

```r
library(Gviz)
library(GenomicRanges)

# Define region
chr <- 'chr1'
start <- 1000000
end <- 1100000

# Ideogram track
itrack <- IdeogramTrack(genome = 'hg38', chromosome = chr)

# Genome axis
gtrack <- GenomeAxisTrack()

# Data track from bigWig
dtrack <- DataTrack(
    range = 'sample.bw',
    genome = 'hg38',
    type = 'histogram',
    name = 'ChIP Signal',
    col.histogram = 'darkblue',
    fill.histogram = 'darkblue'
)

# Gene track
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
grtrack <- GeneRegionTrack(txdb, genome = 'hg38', chromosome = chr, name = 'Genes')

# Plot
plotTracks(list(itrack, gtrack, dtrack, grtrack),
           from = start, to = end, chromosome = chr)
```

## Multiple Samples in Gviz

**Goal:** Compare ChIP-seq signal from multiple samples in a single browser view.

**Approach:** Create separate DataTrack objects per sample and stack them in the plotTracks call.

```r
# Create data tracks for each sample
dtrack1 <- DataTrack(range = 'control.bw', genome = 'hg38', name = 'Control',
                      type = 'histogram', col.histogram = 'blue', fill.histogram = 'blue')
dtrack2 <- DataTrack(range = 'treatment.bw', genome = 'hg38', name = 'Treatment',
                      type = 'histogram', col.histogram = 'red', fill.histogram = 'red')

plotTracks(list(itrack, gtrack, dtrack1, dtrack2, grtrack),
           from = start, to = end, chromosome = chr)
```

## EnrichedHeatmap (R)

**Goal:** Generate customizable heatmaps of ChIP signal around genomic features using ComplexHeatmap framework.

**Approach:** Normalize bigWig signal to a matrix around target sites and render with EnrichedHeatmap.

```r
library(EnrichedHeatmap)
library(rtracklayer)

# Load signal and regions
signal <- import('sample.bw')
tss <- promoters(txdb, upstream = 0, downstream = 1)

# Normalize to matrix
mat <- normalizeToMatrix(signal, tss, extend = 3000, mean_mode = 'w0', w = 50)

# Heatmap
EnrichedHeatmap(mat, name = 'Signal', col = c('white', 'red'))
```

## IGV Batch Screenshot

**Goal:** Automate genome browser screenshots at specific loci without manual interaction.

**Approach:** Write an IGV batch script that loads tracks, navigates to regions, and saves snapshots.

```bash
# Create IGV batch script
cat > igv_batch.txt << 'EOF'
new
genome hg38
load sample.bw
load peaks.bed
goto chr1:1000000-1100000
snapshot region1.png
goto chr2:50000000-51000000
snapshot region2.png
exit
EOF

# Run IGV in batch mode
igv.sh -b igv_batch.txt
```

## Key Tools Comparison

| Tool | Type | Best For |
|------|------|----------|
| deepTools | CLI | Large-scale heatmaps, profiles |
| ChIPseeker | R | Peak-centric visualization |
| Gviz | R | Publication-quality browser |
| EnrichedHeatmap | R | Customizable heatmaps |
| IGV | GUI | Interactive exploration |

## deepTools Key Commands

| Command | Purpose |
|---------|---------|
| bamCoverage | BAM to bigWig |
| bamCompare | Compare two BAMs |
| computeMatrix | Signal matrix |
| plotHeatmap | Heatmap visualization |
| plotProfile | Profile plot |
| multiBigwigSummary | Compare multiple bigWigs |
| plotCorrelation | Sample correlation |

## Related Skills

- peak-calling - Generate peaks for visualization
- peak-annotation - Annotation pie charts
- alignment-files - Prepare BAM files
