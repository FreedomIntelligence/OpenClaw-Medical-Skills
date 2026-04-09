# bio-data-visualization-genome-browser-tracks

> Generate genome browser visualizations using pyGenomeTracks or IGV batch scripting for publication figures. Use when creating publication figures of genomic regions with multiple data tracks.

**Available tools:** Read, Bash

# Genome Browser Tracks

## pyGenomeTracks INI Configuration

```ini
[x-axis]
where = top

[bigwig_coverage]
file = sample.bw
title = Coverage
height = 3
color = #4DBBD5
min_value = 0
max_value = auto

[spacer]
height = 0.5

[peaks]
file = peaks.bed
title = Peaks
color = #E64B35
height = 1
display = collapsed

[genes]
file = genes.gtf
title = Genes
height = 5
fontsize = 10
style = UCSC
color = navy
```

## pyGenomeTracks Command

```bash
# Generate track plot
pyGenomeTracks --tracks tracks.ini --region chr1:1000000-2000000 \
    --outFileName region.png --dpi 300

# Multiple regions
for region in chr1:1000000-2000000 chr2:5000000-6000000; do
    pyGenomeTracks --tracks tracks.ini --region $region \
        --outFileName "${region//:/_}.png" --dpi 300
done
```

## pyGenomeTracks Python API

```python
import pygenometracks.tracks as pygtk
from pygenometracks import plotTracks

# Programmatic track configuration
tracks = '''
[x-axis]
where = top

[bigwig]
file = coverage.bw
title = ChIP-seq
height = 4
color = #4DBBD5

[bed]
file = peaks.narrowPeak
title = Peaks
height = 1
color = #E64B35
'''

# Write config and plot
with open('tracks.ini', 'w') as f:
    f.write(tracks)

# Using command line via subprocess
import subprocess
subprocess.run([
    'pyGenomeTracks',
    '--tracks', 'tracks.ini',
    '--region', 'chr1:1000000-2000000',
    '--outFileName', 'output.png',
    '--dpi', '300'
])
```

## Track Types

### bigWig Coverage

```ini
[bigwig]
file = signal.bw
title = Coverage
height = 4
color = #4DBBD5
min_value = 0
max_value = auto
number_of_bins = 700
nans_to_zeros = true
summary_method = mean
# overlay_previous = share-y  # For overlaying multiple tracks
```

### BED/narrowPeak

```ini
[bed]
file = peaks.narrowPeak
title = Peaks
height = 2
color = #E64B35
display = collapsed  # or stacked, interleaved, triangles
labels = false
# file_type = bed  # auto-detected usually

[bed_links]
file = interactions.bedpe
title = Loops
height = 3
file_type = links
links_type = arcs
color = purple
line_width = 1
```

### Gene Annotations

```ini
[genes]
file = genes.gtf
title = Genes
height = 6
fontsize = 10
style = UCSC  # or flybase
prefered_name = gene_name
merge_transcripts = false
color = navy
border_color = black
# arrow_interval = 2  # Arrow frequency

[genes_bed12]
file = genes.bed12
title = Transcripts
height = 5
fontsize = 8
color = darkblue
```

### Hi-C Matrix

```ini
[hic_matrix]
file = matrix.cool
title = Hi-C
height = 10
depth = 1000000
min_value = 0
max_value = 100
transform = log1p
colormap = RdYlBu_r
show_masked_bins = false
```

## IGV Batch Scripting

```bash
# Create batch script
cat > igv_batch.txt << 'EOF'
new
genome hg38
load sample1.bam
load peaks.bed
snapshotDirectory ./snapshots
goto chr1:1000000-2000000
snapshot region1.png
goto chr2:5000000-6000000
snapshot region2.png
exit
EOF

# Run IGV in batch mode
igv -b igv_batch.txt
```

## IGV Batch Commands

```bash
# Common IGV batch commands
new                          # New session
genome hg38                  # Load genome
load file.bam               # Load track
snapshotDirectory ./out     # Set output dir
goto chr1:1000000-2000000   # Navigate to region
sort base                   # Sort reads
collapse                    # Collapse tracks
expand                      # Expand tracks
squish                      # Squish display
maxPanelHeight 500          # Set panel height
snapshot file.png           # Take screenshot
exit                        # Exit IGV
```

## Gviz (R)

```r
library(Gviz)
library(GenomicRanges)

# Axis track
axTrack <- GenomeAxisTrack()

# Gene track from TxDb
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
grTrack <- GeneRegionTrack(txdb, chromosome = 'chr1', name = 'Genes')

# Data track from BigWig
dTrack <- DataTrack(range = 'coverage.bw', type = 'h',
                    chromosome = 'chr1', name = 'Coverage',
                    col = '#4DBBD5')

# Annotation track from BED
aTrack <- AnnotationTrack(range = 'peaks.bed', name = 'Peaks',
                          chromosome = 'chr1', fill = '#E64B35')

# Plot tracks
plotTracks(list(axTrack, dTrack, aTrack, grTrack),
           from = 1000000, to = 2000000,
           chromosome = 'chr1')

# Save to PDF
pdf('tracks.pdf', width = 10, height = 6)
plotTracks(list(axTrack, dTrack, aTrack, grTrack),
           from = 1000000, to = 2000000)
dev.off()
```

## Multi-Sample Comparison

```ini
# tracks.ini for multiple samples
[x-axis]

[sample1_bw]
file = sample1.bw
title = Sample 1
height = 3
color = #4DBBD5
min_value = 0
max_value = 100

[sample2_bw]
file = sample2.bw
title = Sample 2
height = 3
color = #E64B35
min_value = 0
max_value = 100
overlay_previous = share-y

[spacer]
height = 0.3

[sample1_peaks]
file = sample1_peaks.bed
title = S1 Peaks
height = 1
color = #4DBBD5

[sample2_peaks]
file = sample2_peaks.bed
title = S2 Peaks
height = 1
color = #E64B35
```

## Publication Export

```bash
# High resolution PNG
pyGenomeTracks --tracks tracks.ini --region chr1:1-1000000 \
    --outFileName figure.png --dpi 300 --width 40

# PDF for vector graphics
pyGenomeTracks --tracks tracks.ini --region chr1:1-1000000 \
    --outFileName figure.pdf --width 40

# SVG for editing
pyGenomeTracks --tracks tracks.ini --region chr1:1-1000000 \
    --outFileName figure.svg --width 40
```

## Related Skills

- alignment-files/bam-statistics - Input BAM processing
- chip-seq/peak-calling - Peak files for tracks
- hi-c-analysis/matrix-operations - Hi-C visualization
- data-visualization/multipanel-figures - Combining track figures
