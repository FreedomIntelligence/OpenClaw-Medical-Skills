# bio-data-visualization-genome-tracks

> Create genome browser-style visualizations showing multiple data tracks (coverage, peaks, genes) using pyGenomeTracks, Gviz, and IGV. Use when visualizing genomic data at specific loci with multiple aligned tracks.

**Available tools:** Read, Bash

# Genome Track Visualization

## pyGenomeTracks (Python/CLI)

```bash
# Create tracks configuration file
cat > tracks.ini << 'EOF'
[bigwig]
file = coverage.bw
title = Coverage
height = 4
color = #4DBBD5
min_value = 0

[spacer]
height = 0.5

[peaks]
file = peaks.bed
title = Peaks
color = #E64B35
height = 2
labels = false

[spacer]
height = 0.5

[genes]
file = genes.gtf
title = Genes
height = 5
fontsize = 10
style = flybase
color = #3C5488

[x-axis]
EOF

# Generate plot
pyGenomeTracks --tracks tracks.ini --region chr1:1000000-2000000 \
    --outFileName tracks.png --dpi 150
```

## pyGenomeTracks with Multiple Samples

```ini
[sample1 coverage]
file = sample1.bw
title = Sample 1
height = 3
color = #4DBBD5
min_value = 0
max_value = auto

[sample2 coverage]
file = sample2.bw
title = Sample 2
height = 3
color = #E64B35
min_value = 0
max_value = auto

[sample1 peaks]
file = sample1_peaks.narrowPeak
title = Sample 1 Peaks
color = #4DBBD5
height = 1
file_type = narrowPeak

[sample2 peaks]
file = sample2_peaks.narrowPeak
title = Sample 2 Peaks
color = #E64B35
height = 1
file_type = narrowPeak
```

## pyGenomeTracks Programmatic

```python
import pygenometracks.tracks as pygtk

tracks = pygtk.PlotTracks('tracks.ini', fig_width=40, dpi=150)
tracks.plot('output.png', 'chr1', 1000000, 2000000)
```

## Gviz (R)

```r
library(Gviz)
library(GenomicRanges)

# Genome axis
gtrack <- GenomeAxisTrack()

# Ideogram
itrack <- IdeogramTrack(genome = 'hg38', chromosome = 'chr1')

# Gene model
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
grtrack <- GeneRegionTrack(txdb, genome = 'hg38', chromosome = 'chr1',
                            name = 'Genes', transcriptAnnotation = 'symbol')

# Data track from BigWig
dtrack <- DataTrack(range = 'coverage.bw', genome = 'hg38', chromosome = 'chr1',
                     name = 'Coverage', type = 'histogram', col.histogram = '#4DBBD5')

# Annotation track from BED
atrack <- AnnotationTrack(range = 'peaks.bed', genome = 'hg38', chromosome = 'chr1',
                           name = 'Peaks', fill = '#E64B35')

# Plot tracks
plotTracks(list(itrack, gtrack, dtrack, atrack, grtrack),
           from = 1000000, to = 2000000, sizes = c(1, 1, 3, 1, 3))
```

## Gviz with Multiple Samples

```r
# Create overlay data track
dtrack1 <- DataTrack(range = 'sample1.bw', name = 'Sample1', col = '#4DBBD5')
dtrack2 <- DataTrack(range = 'sample2.bw', name = 'Sample2', col = '#E64B35')

overlay <- OverlayTrack(trackList = list(dtrack1, dtrack2))

plotTracks(list(gtrack, overlay, grtrack), from = 1000000, to = 2000000,
           type = 'histogram', legend = TRUE)
```

## Gviz Customization

```r
# Highlight regions
ht <- HighlightTrack(trackList = list(dtrack, atrack),
                      start = c(1200000, 1500000),
                      end = c(1300000, 1600000),
                      chromosome = 'chr1')

# Custom display parameters
displayPars(dtrack) <- list(
    background.title = '#3C5488',
    fontcolor.title = 'white',
    col.axis = 'black',
    ylim = c(0, 100)
)

plotTracks(list(gtrack, ht, grtrack), from = 1000000, to = 2000000)
```

## IGV.js (Web)

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/igv@3.0.0/dist/igv.min.js"></script>
</head>
<body>
    <div id="igv-div"></div>
    <script>
        var options = {
            genome: "hg38",
            locus: "chr1:1,000,000-2,000,000",
            tracks: [
                {
                    name: "Coverage",
                    url: "coverage.bw",
                    type: "wig",
                    color: "#4DBBD5"
                },
                {
                    name: "Peaks",
                    url: "peaks.bed",
                    type: "annotation",
                    color: "#E64B35"
                }
            ]
        };
        igv.createBrowser(document.getElementById('igv-div'), options);
    </script>
</body>
</html>
```

## Create BigWig from BAM

```bash
# Using deepTools
bamCoverage -b sample.bam -o coverage.bw \
    --binSize 10 --normalizeUsing RPKM --effectiveGenomeSize 2913022398

# Using bedtools + wigToBigWig
bedtools genomecov -bg -ibam sample.bam > coverage.bedGraph
sort -k1,1 -k2,2n coverage.bedGraph > coverage.sorted.bedGraph
bedGraphToBigWig coverage.sorted.bedGraph chrom.sizes coverage.bw
```

## Multi-Region Plot

```bash
# pyGenomeTracks with BED regions
pyGenomeTracks --tracks tracks.ini --BED regions.bed \
    --outFileName multi_region.pdf --dpi 150
```

```r
# Gviz with multiple regions
regions <- GRanges(seqnames = 'chr1', ranges = IRanges(start = c(1e6, 2e6), end = c(1.5e6, 2.5e6)))

pdf('multi_region.pdf', width = 10, height = 8)
for (i in seq_along(regions)) {
    plotTracks(track_list, from = start(regions[i]), to = end(regions[i]))
}
dev.off()
```

## Related Skills

- genome-intervals/bigwig-tracks - BigWig file handling
- chip-seq/chipseq-visualization - ChIP-specific tracks
- hi-c-analysis/hic-visualization - Hi-C contact maps
