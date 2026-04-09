# bio-workflows-tcr-pipeline

> End-to-end TCR/BCR repertoire analysis from FASTQ to clonotype diversity metrics. Use when analyzing immune repertoire sequencing data from bulk or single-cell experiments.

**Available tools:** Read, Bash

# TCR/BCR Analysis Pipeline

## Pipeline Overview

```
FASTQ → MiXCR align → Assemble → Export → VDJtools diversity → Visualization
```

## Step 1: MiXCR Processing

```bash
# Align reads to V(D)J segments
mixcr align -s hsa -p rna-seq \
    R1.fastq.gz R2.fastq.gz \
    aligned.vdjca

# Assemble clonotypes
mixcr assemble aligned.vdjca clones.clns

# Export
mixcr exportClones clones.clns clones.txt
```

## Step 2: VDJtools Analysis

```bash
# Convert to VDJtools format
vdjtools Convert -S mixcr clones.txt vdjtools/

# Diversity metrics
vdjtools CalcDiversityStats vdjtools/clones.txt diversity/

# Sample overlap
vdjtools CalcPairwiseDistances vdjtools/*.txt overlap/
```

## Step 3: Visualization

```bash
# Spectratype plot
vdjtools PlotFancySpectratype vdjtools/clones.txt spectra/

# V usage
vdjtools PlotFancyVJUsage vdjtools/clones.txt usage/
```

## QC Checkpoints

1. **After alignment**: Check V/J assignment rate (>70% typical)
2. **After assembly**: Verify clonotype count and coverage
3. **After diversity**: Compare metrics to expected range

## Related Skills

- tcr-bcr-analysis/mixcr-analysis - Detailed MiXCR usage
- tcr-bcr-analysis/vdjtools-analysis - Diversity metrics
- tcr-bcr-analysis/repertoire-visualization - Plots
