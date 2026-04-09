# bio-atac-seq-nucleosome-positioning

> Extract nucleosome positions from ATAC-seq data using NucleoATAC, ATACseqQC, and fragment analysis. Use when analyzing chromatin organization, identifying nucleosome-free regions at promoters, or characterizing nucleosome occupancy patterns from ATAC-seq fragment size distributions.

## Version Compatibility

Reference examples tested with: Rsamtools 2.18+, matplotlib 3.8+, numpy 1.26+, pyBigWig 0.3+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Nucleosome Positioning

**"Map nucleosome positions from ATAC-seq"** → Separate nucleosome-free and mono-nucleosome fragments by size, then call nucleosome center positions and occupancy scores.
- CLI: `nucleoatac run --bed peaks.bed --bam atac.bam --fasta ref.fa`
- R: `ATACseqQC::splitGAlignmentsByCut()` for fragment separation

Extract nucleosome positions and occupancy from ATAC-seq fragment size patterns.

## Background

ATAC-seq fragments reflect chromatin structure:
- **< 100 bp**: Nucleosome-free regions (NFR)
- **180-247 bp**: Mono-nucleosome
- **315-473 bp**: Di-nucleosome
- **558-615 bp**: Tri-nucleosome

## ATACseqQC (R)

### Installation

```r
BiocManager::install('ATACseqQC')
```

### Fragment Size Distribution

```r
library(ATACseqQC)
library(Rsamtools)

# Read BAM
bamfile <- 'sample.bam'

# Fragment size distribution
fragSize <- fragSizeDist(bamfile, 'sample')

# Nucleosome-free and mono-nucleosome ratios
# Automatic QC metrics
```

### Nucleosome Positioning

**Goal:** Map nucleosome positions around TSS using ATAC-seq fragment size classes.

**Approach:** Read BAM, apply Tn5 shift correction, split fragments into NFR and mono-nucleosome classes by size, then compute signal profiles around TSS.

```r
library(ATACseqQC)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(BSgenome.Hsapiens.UCSC.hg38)

# Get TSS regions
txs <- transcripts(TxDb.Hsapiens.UCSC.hg38.knownGene)
tss <- promoters(txs, upstream=1000, downstream=1000)

# Read BAM
gal <- readBamFile(bamfile, asMates=TRUE, bigFile=TRUE)

# Shift reads (Tn5 offset correction)
gal_shifted <- shiftGAlignmentsList(gal)

# Split by nucleosome-free and nucleosomal
objs <- splitGAlignmentsByCut(gal_shifted, txs=txs,
                               genome=BSgenome.Hsapiens.UCSC.hg38)

# nucleosome-free fragments
nfr <- objs$NussomeFree

# Mono-nucleosome fragments
mono <- objs$mononucleosome

# Signal around TSS
sigs <- featureAlignedSignal(cvglist=objs,
                             feature.gr=tss,
                             upstream=1000,
                             downstream=1000)
```

### V-Plot (Fragment Size vs Position)

```r
# V-plot showing nucleosome positioning around TSS
vp <- vPlot(gal_shifted, tss,
            genome=BSgenome.Hsapiens.UCSC.hg38,
            upstream=1000, downstream=1000)
```

### Footprinting

```r
# Transcription factor footprinting
library(MotifDb)

# Get motif
motif <- query(MotifDb, 'CTCF')[[1]]

# Find motif occurrences
library(motifmatchr)
motif_pos <- matchMotifs(motif, BSgenome.Hsapiens.UCSC.hg38,
                         genome='hg38', out='positions')

# Calculate footprint
fp <- factorFootprints(gal_shifted, motif_pos,
                       genome=BSgenome.Hsapiens.UCSC.hg38,
                       upstream=100, downstream=100)
```

## NucleoATAC (Python)

### Installation

```bash
pip install nucleoatac
```

### Run NucleoATAC

**Goal:** Call precise nucleosome center positions and occupancy scores from ATAC-seq data.

**Approach:** Run NucleoATAC on defined genomic regions with a reference genome, producing nucleosome position calls and occupancy tracks.

```bash
# Call nucleosomes
nucleoatac run --bed regions.bed --bam sample.bam --fasta reference.fa \
    --out nucleoatac_output --cores 8
```

### Output Files

| File | Description |
|------|-------------|
| `.nucpos.bed` | Nucleosome positions |
| `.nucpos.redundant.bed` | All nucleosome calls |
| `.nfrpos.bed` | NFR positions |
| `.occ.bedgraph` | Nucleosome occupancy track |
| `.nucmap_combined.bed` | Combined nucleosome map |

### Visualize Output

```bash
# Convert to bigWig for visualization
bedGraphToBigWig nucleoatac_output.occ.bedgraph chrom.sizes nucleosome_occ.bw
```

## Fragment Analysis (Custom)

### Extract Fragment Sizes

**Goal:** Visualize ATAC-seq fragment size distribution to assess nucleosome periodicity.

**Approach:** Extract template lengths from properly paired reads, then plot the histogram with NFR and mono-nucleosome cutoff markers.

```python
import pysam
import numpy as np
import matplotlib.pyplot as plt

bam = pysam.AlignmentFile('sample.bam', 'rb')

fragment_sizes = []
for read in bam.fetch():
    if read.is_proper_pair and read.is_read1:
        frag_size = abs(read.template_length)
        if 0 < frag_size < 1000:
            fragment_sizes.append(frag_size)

bam.close()

# Plot distribution
plt.figure(figsize=(10, 6))
plt.hist(fragment_sizes, bins=200, edgecolor='none', alpha=0.7)
plt.axvline(100, color='red', linestyle='--', label='NFR cutoff')
plt.axvline(180, color='blue', linestyle='--', label='Mono-nuc start')
plt.xlabel('Fragment Size (bp)')
plt.ylabel('Count')
plt.legend()
plt.savefig('fragment_distribution.png', dpi=300)
```

### Split by Fragment Size

```bash
# Extract nucleosome-free reads
samtools view -h sample.bam | \
    awk '$9 > -100 && $9 < 100 || $1 ~ /^@/' | \
    samtools view -b > nfr.bam

# Extract mono-nucleosome reads
samtools view -h sample.bam | \
    awk '($9 >= 180 && $9 <= 247) || ($9 <= -180 && $9 >= -247) || $1 ~ /^@/' | \
    samtools view -b > mono_nuc.bam
```

### Signal Around Features

```python
import pysam
import numpy as np
import pyBigWig

def signal_around_sites(bam_file, sites, upstream=1000, downstream=1000):
    bam = pysam.AlignmentFile(bam_file, 'rb')
    window_size = upstream + downstream
    signal = np.zeros(window_size)

    for chrom, pos, strand in sites:
        start = pos - upstream if strand == '+' else pos - downstream
        end = pos + downstream if strand == '+' else pos + upstream

        for read in bam.fetch(chrom, max(0, start), end):
            if read.is_proper_pair and read.is_read1:
                frag_center = read.reference_start + abs(read.template_length) // 2
                rel_pos = frag_center - start
                if 0 <= rel_pos < window_size:
                    signal[rel_pos] += 1

    bam.close()
    return signal / len(sites)

# Load TSS sites
tss_sites = []  # Load from GTF
nfr_signal = signal_around_sites('nfr.bam', tss_sites)
mono_signal = signal_around_sites('mono_nuc.bam', tss_sites)
```

## DANPOS

### Installation

```bash
conda install -c bioconda danpos
```

### Run DANPOS

```bash
# Single sample
danpos.py dpos sample.bam -o danpos_output

# Compare conditions
danpos.py dpeak -b treatment.bam -c control.bam -o danpos_diff
```

## Complete Workflow

**Goal:** Run end-to-end nucleosome positioning analysis from BAM to heatmaps and V-plots.

**Approach:** Read BAM, shift reads for Tn5 offset, split fragments by size class, compute signal profiles around TSS, and generate heatmaps and V-plots.

```r
library(ATACseqQC)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(BSgenome.Hsapiens.UCSC.hg38)

bamfile <- 'sample.bam'

# 1. Fragment size QC
fragSize <- fragSizeDist(bamfile, 'sample')
pdf('fragment_size.pdf')
plot(fragSize)
dev.off()

# 2. Read and shift
gal <- readBamFile(bamfile, asMates=TRUE, bigFile=TRUE)
gal_shifted <- shiftGAlignmentsList(gal)

# 3. Get TSS regions
txs <- transcripts(TxDb.Hsapiens.UCSC.hg38.knownGene)
tss <- promoters(txs, upstream=2000, downstream=2000)

# 4. Split by fragment size
objs <- splitGAlignmentsByCut(gal_shifted, txs=txs,
                               genome=BSgenome.Hsapiens.UCSC.hg38)

# 5. Calculate signals
sigs <- featureAlignedSignal(cvglist=objs,
                             feature.gr=tss,
                             upstream=2000,
                             downstream=2000)

# 6. Plot heatmap
pdf('nucleosome_heatmap.pdf', width=8, height=10)
featureAlignedHeatmap(sigs, tss, upstream=2000, downstream=2000)
dev.off()

# 7. V-plot
pdf('vplot.pdf')
vPlot(gal_shifted, tss, genome=BSgenome.Hsapiens.UCSC.hg38,
      upstream=1000, downstream=1000)
dev.off()

# 8. Export nucleosome-free and nucleosomal BAMs
export(objs$NuclsomeFree, 'nfr.bam')
export(objs$mononucleosome, 'mono_nucleosome.bam')
```

## Related Skills

- atac-seq/atac-peak-calling - Call accessibility peaks
- atac-seq/atac-qc - Quality control metrics
- atac-seq/footprinting - TF footprinting
- chip-seq/peak-annotation - Annotate nucleosome positions
