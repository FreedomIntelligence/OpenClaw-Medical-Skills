# bio-workflows-hic-pipeline

> End-to-end Hi-C analysis workflow from contact pairs to compartments, TADs, and loops. Covers cooler matrices, cooltools analysis, and visualization. Use when processing Hi-C data to compartments and TADs.

**Available tools:** Read, Bash

# Hi-C Pipeline

Complete workflow for Hi-C chromosome conformation capture analysis.

## Workflow Overview

```
Hi-C FASTQ files
    |
    v
[1. Alignment & Pairs] --> bwa-mem2 + pairtools
    |
    v
[2. Matrix Generation] --> cooler
    |
    v
[3. Normalization] -----> ICE balancing
    |
    v
[4. Compartments] ------> Eigenvector analysis
    |
    v
[5. TADs] --------------> Insulation score
    |
    v
[6. Loops] -------------> Dot calling
    |
    v
Hi-C features
```

## Step 1: Alignment and Pair Processing

```bash
# Align Hi-C reads (each end separately, then combine)
bwa-mem2 mem -SP5M -t 16 reference.fa reads_R1.fastq.gz | \
    pairtools parse --min-mapq 40 --walks-policy 5unique \
    --max-inter-align-gap 30 --nproc-in 8 --nproc-out 8 \
    --chroms-path reference.genome | \
    pairtools sort --nproc 16 --tmpdir ./tmp | \
    pairtools dedup --nproc-in 8 --nproc-out 8 \
    --mark-dups --output-stats stats.txt | \
    pairtools split --nproc-in 8 --output-pairs sample.pairs.gz

# Alternative: align both ends
bwa-mem2 mem -SP5M -t 16 reference.fa \
    reads_R1.fastq.gz reads_R2.fastq.gz | \
    pairtools parse --min-mapq 40 --walks-policy 5unique \
    --max-inter-align-gap 30 --chroms-path reference.genome | \
    pairtools sort | \
    pairtools dedup --mark-dups --output-stats stats.txt | \
    pairtools split --output-pairs sample.pairs.gz
```

**QC Checkpoint:** Check pair statistics
- Valid pairs >50% of total
- Cis pairs >70% (intra-chromosomal)
- Duplicate rate reasonable

## Step 2: Generate Contact Matrix

```bash
# Create cooler file at multiple resolutions
cooler cload pairs \
    -c1 2 -p1 3 -c2 4 -p2 5 \
    reference.genome:1000 \
    sample.pairs.gz \
    sample.1000.cool

# Multi-resolution (mcool)
cooler zoomify sample.1000.cool \
    -r 1000,2000,5000,10000,25000,50000,100000,250000,500000,1000000 \
    -o sample.mcool
```

## Step 3: Normalization (ICE Balancing)

```python
import cooler
import cooltools

# Load matrix
clr = cooler.Cooler('sample.mcool::resolutions/10000')

# Balance (ICE normalization)
cooltools.balance_cooler(clr, store=True, mad_max=5)

# Or via command line
# cooler balance sample.mcool::resolutions/10000
```

## Step 4: Compartment Analysis

```python
import cooler
import cooltools
import numpy as np

# Load balanced matrix
clr = cooler.Cooler('sample.mcool::resolutions/100000')

# Calculate expected (for O/E)
expected = cooltools.expected_cis(clr, view_df=None, nproc=4)

# Compute eigenvector (compartments)
eig = cooltools.eigs_cis(
    clr,
    phasing_track='gc_content.bw',  # Optional: orient by GC
    n_eigs=3,
    nproc=4
)

# A/B compartments
eig_values, eig_vectors = eig
compartments = eig_vectors[['E1']].copy()
compartments['compartment'] = np.where(compartments['E1'] > 0, 'A', 'B')
compartments.to_csv('compartments.tsv', sep='\t')
```

## Step 5: TAD Detection

```python
import cooltools

# Load matrix at TAD resolution
clr = cooler.Cooler('sample.mcool::resolutions/10000')

# Calculate insulation score
insulation = cooltools.insulation(clr, window_bp=[100000, 200000, 500000])

# Call boundaries
boundaries = cooltools.find_boundaries(insulation)
boundaries.to_csv('tad_boundaries.tsv', sep='\t')

# Alternative: use HiCExplorer
# hicFindTADs -m sample.h5 --outPrefix tads --correctForMultipleTesting fdr
```

## Step 6: Loop Calling

```python
import cooltools

# Load high-resolution matrix
clr = cooler.Cooler('sample.mcool::resolutions/10000')

# Call loops using expected
expected = cooltools.expected_cis(clr)
loops = cooltools.dots(
    clr,
    expected,
    max_loci_separation=2000000,
    nproc=4
)

loops.to_csv('loops.tsv', sep='\t')

# Alternative: use chromosight
# chromosight detect --pattern loops sample.mcool::resolutions/10000 loops
```

## Step 7: Visualization

```python
import matplotlib.pyplot as plt
import cooltools.lib.plotting

# Plot contact matrix region
fig, ax = plt.subplots(figsize=(10, 10))
cooltools.lib.plotting.pcolormesh_45deg(
    ax, clr.matrix(balance=True).fetch('chr1:50000000-60000000'),
    start=50000000, resolution=clr.binsize
)
ax.set_aspect('equal')
plt.savefig('hic_matrix.pdf')

# Plot with TADs
from matplotlib.patches import Polygon
# Add TAD boundaries as triangles
```

## Complete Pipeline Script

```bash
#!/bin/bash
set -e

THREADS=16
REF="reference.fa"
GENOME="reference.genome"
R1="sample_R1.fastq.gz"
R2="sample_R2.fastq.gz"
OUTDIR="hic_results"

mkdir -p ${OUTDIR}/{pairs,cool,analysis}

# Step 1: Alignment and pairs
echo "=== Alignment ==="
bwa-mem2 mem -SP5M -t ${THREADS} ${REF} ${R1} ${R2} | \
    pairtools parse --min-mapq 40 --walks-policy 5unique \
    --chroms-path ${GENOME} | \
    pairtools sort --nproc ${THREADS} --tmpdir ./tmp | \
    pairtools dedup --mark-dups --output-stats ${OUTDIR}/pairs/stats.txt | \
    pairtools split --output-pairs ${OUTDIR}/pairs/sample.pairs.gz

# Step 2: Generate matrix
echo "=== Matrix Generation ==="
cooler cload pairs -c1 2 -p1 3 -c2 4 -p2 5 \
    ${GENOME}:1000 ${OUTDIR}/pairs/sample.pairs.gz ${OUTDIR}/cool/sample.1000.cool

cooler zoomify ${OUTDIR}/cool/sample.1000.cool \
    -r 1000,5000,10000,25000,50000,100000,500000 \
    -o ${OUTDIR}/cool/sample.mcool

# Step 3: Balance
echo "=== Balancing ==="
for res in 10000 25000 100000; do
    cooler balance ${OUTDIR}/cool/sample.mcool::resolutions/${res}
done

echo "=== Pipeline Complete ==="
echo "Run Python script for compartments, TADs, and loops"
```

## Python Analysis Script

```python
import cooler
import cooltools
import pandas as pd
import os

outdir = 'hic_results/analysis'
os.makedirs(outdir, exist_ok=True)

# Compartments (100kb)
print('Compartments...')
clr = cooler.Cooler('hic_results/cool/sample.mcool::resolutions/100000')
eig_values, eig_vectors = cooltools.eigs_cis(clr, n_eigs=3)
eig_vectors.to_csv(f'{outdir}/compartments.tsv', sep='\t')

# TADs (10kb)
print('TADs...')
clr = cooler.Cooler('hic_results/cool/sample.mcool::resolutions/10000')
insulation = cooltools.insulation(clr, window_bp=[100000, 200000])
insulation.to_csv(f'{outdir}/insulation.tsv', sep='\t')

# Loops (10kb)
print('Loops...')
expected = cooltools.expected_cis(clr)
loops = cooltools.dots(clr, expected, nproc=4)
loops.to_csv(f'{outdir}/loops.tsv', sep='\t')

print(f'Results saved to {outdir}/')
```

## Related Skills

- hi-c-analysis/hic-data-io - Cooler file operations
- hi-c-analysis/contact-pairs - Pairtools processing
- hi-c-analysis/compartment-analysis - A/B compartments
- hi-c-analysis/tad-detection - TAD calling methods
- hi-c-analysis/loop-calling - Loop detection
- hi-c-analysis/hic-visualization - Plotting matrices
