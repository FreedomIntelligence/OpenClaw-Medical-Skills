# bio-data-visualization-circos-plots

> Create circular genome visualizations with Circos and pyCircos. Display multi-track data including ideograms, genes, variants, CNVs, and interaction arcs. Use when creating circular genome visualizations.

**Available tools:** Read, Bash

# Circos Plots

Circular genome visualizations for displaying multiple data tracks around chromosome ideograms.

## Tool Options

| Tool | Language | Best For |
|------|----------|----------|
| Circos | Perl/CLI | Publication-quality, complex layouts |
| pyCircos | Python | Programmatic generation, integration |
| circlize | R | Quick plots, Bioconductor integration |

## Circos (Original)

### Installation

```bash
conda install -c bioconda circos
# Or download from http://circos.ca
```

### Basic Configuration

Circos requires configuration files defining the plot structure.

#### circos.conf (main config)

```
# Chromosome definitions
karyotype = data/karyotype.human.hg38.txt

<ideogram>
<spacing>
default = 0.005r
</spacing>
radius = 0.90r
thickness = 20p
fill = yes
</ideogram>

<image>
dir = output
file = circos.png
png = yes
svg = yes
radius = 1500p
</image>

<<include etc/colors_fonts_patterns.conf>>
<<include etc/housekeeping.conf>>
```

### Data Tracks

#### Scatter Plot Track

```
<plots>
<plot>
type = scatter
file = data/scatter.txt
r0 = 0.75r
r1 = 0.85r
min = 0
max = 1
glyph = circle
glyph_size = 8p
color = red
</plot>
</plots>
```

#### Histogram Track

```
<plot>
type = histogram
file = data/histogram.txt
r0 = 0.60r
r1 = 0.74r
min = 0
max = 100
fill_color = blue
</plot>
```

#### Heatmap Track

```
<plot>
type = heatmap
file = data/heatmap.txt
r0 = 0.50r
r1 = 0.59r
color = spectral-9-div
</plot>
```

### Link/Arc Data (Interactions)

```
<links>
<link>
file = data/links.txt
radius = 0.45r
bezier_radius = 0.1r
color = grey_a5
thickness = 2p

<rules>
<rule>
condition = var(intrachr)
color = red
</rule>
</rules>
</link>
</links>
```

### Data File Formats

```
# Scatter/histogram: chr start end value
hs1 1000000 1500000 0.75
hs1 2000000 2500000 0.45

# Links: chr1 start1 end1 chr2 start2 end2
hs1 1000000 1500000 hs5 5000000 5500000
```

### Run Circos

```bash
circos -conf circos.conf
```

## pyCircos (Python)

### Installation

```bash
pip install pyCircos
```

### Basic Genome Plot

```python
from pycircos import Gcircle
import matplotlib.pyplot as plt

# Initialize with genome size
circle = Gcircle()

# Add chromosome data (name, length)
chromosomes = [
    ('chr1', 248956422), ('chr2', 242193529), ('chr3', 198295559),
    ('chr4', 190214555), ('chr5', 181538259), ('chr6', 170805979),
    ('chr7', 159345973), ('chr8', 145138636), ('chr9', 138394717),
    ('chr10', 133797422), ('chr11', 135086622), ('chr12', 133275309)
]

for name, length in chromosomes:
    circle.add_garc(Garc(arc_id=name, size=length, interspace=2,
                         raxis_range=(900, 950), labelposition=80,
                         label_visible=True))

circle.set_garcs()

# Save
fig = circle.figure
fig.savefig('genome_circle.png', dpi=300)
```

### Add Data Tracks

```python
from pycircos import Gcircle, Garc
import numpy as np

circle = Gcircle()

# Add chromosomes
for name, length in chromosomes:
    arc = Garc(arc_id=name, size=length, interspace=3,
               raxis_range=(800, 850), labelposition=60)
    circle.add_garc(arc)

circle.set_garcs()

# Add scatter track
for name, length in chromosomes:
    positions = np.random.randint(0, length, 50)
    values = np.random.random(50)
    circle.scatterplot(name, data=values, positions=positions,
                       raxis_range=(700, 780), facecolor='red',
                       markersize=5)

# Add bar track
for name, length in chromosomes:
    positions = np.linspace(0, length, 100)
    values = np.random.random(100) * 100
    circle.barplot(name, data=values, positions=positions,
                   raxis_range=(600, 680), facecolor='blue')

# Add links
circle.chord_plot(('chr1', 10000000, 20000000),
                  ('chr5', 50000000, 60000000),
                  raxis_range=(0, 550), facecolor='purple', alpha=0.5)

fig = circle.figure
fig.savefig('circos_with_data.png', dpi=300)
```

## circlize (R)

### Installation

```r
install.packages('circlize')
```

### Basic Plot

```r
library(circlize)

# Initialize with genome
circos.initializeWithIdeogram(species = 'hg38')

# Add track with data
bed <- data.frame(
    chr = paste0('chr', sample(1:22, 100, replace=TRUE)),
    start = sample(1:1e8, 100),
    end = sample(1:1e8, 100),
    value = runif(100)
)
bed$end <- bed$start + 1e6

circos.genomicTrack(bed, panel.fun = function(region, value, ...) {
    circos.genomicPoints(region, value, pch=16, cex=0.5, col='red')
})

# Add links
link_data <- data.frame(
    chr1 = c('chr1', 'chr3'), start1 = c(1e7, 5e7), end1 = c(2e7, 6e7),
    chr2 = c('chr5', 'chr10'), start2 = c(3e7, 8e7), end2 = c(4e7, 9e7)
)
for (i in 1:nrow(link_data)) {
    circos.link(link_data$chr1[i], c(link_data$start1[i], link_data$end1[i]),
                link_data$chr2[i], c(link_data$start2[i], link_data$end2[i]),
                col = 'grey')
}

circos.clear()
```

### Genomic Density Plot

```r
library(circlize)

circos.initializeWithIdeogram(species = 'hg38', plotType = c('axis', 'labels'))

# Gene density track
circos.genomicDensity(gene_bed, col = 'blue', track.height = 0.1)

# Variant density track
circos.genomicDensity(variant_bed, col = 'red', track.height = 0.1)

# Heatmap track
circos.genomicHeatmap(expression_bed, col = colorRamp2(c(-2, 0, 2), c('blue', 'white', 'red')))

circos.clear()
```

## Common Use Cases

### CNV Visualization

```python
# pyCircos CNV plot
cnv_data = [
    ('chr1', 10000000, 20000000, 2.5),   # Gain
    ('chr3', 50000000, 80000000, 0.5),   # Loss
    ('chr7', 100000000, 120000000, 3.0), # Amplification
]

for chrom, start, end, log2 in cnv_data:
    color = 'red' if log2 > 1.5 else 'blue' if log2 < 0.7 else 'grey'
    circle.barplot(chrom, data=[log2], positions=[(start+end)//2],
                   width=end-start, raxis_range=(600, 700), facecolor=color)
```

### Fusion Genes

```python
# Visualize gene fusions as arcs
fusions = [
    ('chr9', 133600000, 133700000, 'chr22', 23200000, 23300000),  # BCR-ABL
    ('chr2', 42300000, 42500000, 'chr2', 29400000, 29600000),     # EML4-ALK
]

for chr1, s1, e1, chr2, s2, e2 in fusions:
    circle.chord_plot((chr1, s1, e1), (chr2, s2, e2),
                      raxis_range=(0, 500), facecolor='purple', alpha=0.7)
```

### Hi-C Contact Map

```r
library(circlize)

circos.initializeWithIdeogram(chromosome.index = paste0('chr', 1:22))

# Add Hi-C links with color by contact frequency
for (i in 1:nrow(hic_contacts)) {
    col = colorRamp2(c(0, 100), c('grey90', 'red'))(hic_contacts$count[i])
    circos.link(hic_contacts$chr1[i], c(hic_contacts$start1[i], hic_contacts$end1[i]),
                hic_contacts$chr2[i], c(hic_contacts$start2[i], hic_contacts$end2[i]),
                col = col)
}

circos.clear()
```

## Complete Workflow: Variant Summary

```python
from pycircos import Gcircle, Garc
import pandas as pd

# Load data
variants = pd.read_csv('variants.bed', sep='\t', names=['chr', 'start', 'end', 'type'])
cnv = pd.read_csv('cnv.bed', sep='\t', names=['chr', 'start', 'end', 'log2'])

# Initialize
circle = Gcircle()

chromosomes = [('chr' + str(i), size) for i, size in enumerate([
    248956422, 242193529, 198295559, 190214555, 181538259,
    170805979, 159345973, 145138636, 138394717, 133797422,
    135086622, 133275309, 114364328, 107043718, 101991189,
    90338345, 83257441, 80373285, 58617616, 64444167,
    46709983, 50818468
], start=1)]

for name, length in chromosomes:
    arc = Garc(arc_id=name, size=length, interspace=2, raxis_range=(850, 900))
    circle.add_garc(arc)
circle.set_garcs()

# Variant density track
for chrom, length in chromosomes:
    chrom_vars = variants[variants['chr'] == chrom]
    if len(chrom_vars) > 0:
        hist, bins = np.histogram(chrom_vars['start'], bins=50, range=(0, length))
        circle.barplot(chrom, data=hist, positions=bins[:-1],
                       raxis_range=(750, 840), facecolor='steelblue')

# CNV track
for chrom, length in chromosomes:
    chrom_cnv = cnv[cnv['chr'] == chrom]
    for _, row in chrom_cnv.iterrows():
        color = 'red' if row['log2'] > 0.3 else 'blue' if row['log2'] < -0.3 else 'grey'
        circle.fillplot(chrom, data=[abs(row['log2'])],
                        positions=[(row['start'] + row['end']) // 2],
                        raxis_range=(650, 740), facecolor=color)

fig = circle.figure
fig.savefig('genome_summary.png', dpi=300, bbox_inches='tight')
```

## Related Skills

- data-visualization/genome-tracks - Linear genome visualization
- hi-c-analysis/hic-visualization - Hi-C-specific circos
- copy-number/cnv-visualization - CNV visualization
- variant-calling/structural-variant-calling - SV data for circos
