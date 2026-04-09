# bio-clip-seq-binding-site-annotation

> Annotate CLIP-seq binding sites to genomic features including 3'UTR, 5'UTR, CDS, introns, and ncRNAs. Use when characterizing where an RBP binds in transcripts.

**Available tools:** Read, Bash

# Binding Site Annotation

## Using ChIPseeker (R)

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

peaks <- readPeakFile('peaks.bed')
anno <- annotatePeak(peaks, TxDb = txdb)

plotAnnoPie(anno)
```

## Using BEDTools

```bash
# Annotate to UTRs
bedtools intersect -a peaks.bed -b 3utr.bed -wa -wb > peaks_3utr.bed
```

## Python Annotation

```python
import pandas as pd

def annotate_peaks(peaks_bed, annotation_gtf):
    '''Annotate peaks to genomic features'''
    # Load peaks and annotations
    # Intersect and categorize
    pass
```

## Related Skills

- clip-peak-calling - Get peaks
- genome-intervals/interval-arithmetic - Intersect peaks with genomic features
