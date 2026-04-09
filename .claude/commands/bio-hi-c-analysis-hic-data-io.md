# bio-hi-c-analysis-hic-data-io

> Load, convert, and manipulate Hi-C contact matrices using cooler format. Read .cool/.mcool files, convert from .hic format, access matrix data, and export to different formats. Use when loading or converting Hi-C contact matrices.

## Version Compatibility

Reference examples tested with: cooler 0.9+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Hi-C Data I/O

**"Load my Hi-C contact matrix"** → Read .cool/.mcool/.hic files into Python, access contact pixels, convert between formats, and export subsets.
- Python: `cooler.Cooler('file.mcool::resolutions/10000')`
- CLI: `cooler load`, `hic2cool convert`

Load and manipulate Hi-C contact matrices in cooler format.

## Required Imports

```python
import cooler
import numpy as np
import pandas as pd
```

## Load a Cooler File

```python
# Load a .cool file
clr = cooler.Cooler('matrix.cool')

# Basic info
print(f'Chromosomes: {clr.chromnames}')
print(f'Bin size: {clr.binsize}')
print(f'Number of bins: {clr.info["nbins"]}')
print(f'Sum of counts: {clr.info["sum"]}')
```

## Load Multi-Resolution Cooler (.mcool)

```python
# List available resolutions
resolutions = cooler.fileops.list_coolers('matrix.mcool')
print(f'Available resolutions: {resolutions}')

# Load specific resolution
clr = cooler.Cooler('matrix.mcool::resolutions/10000')
print(f'Loaded at {clr.binsize}bp resolution')
```

## Access Bin Information

```python
# Get bin table (genomic coordinates)
bins = clr.bins()[:]
print(bins.head())
# Columns: chrom, start, end, weight (if balanced)

# Get bins for a chromosome
chr1_bins = clr.bins().fetch('chr1')
print(f'chr1 has {len(chr1_bins)} bins')
```

## Access Pixel (Contact) Information

```python
# Get all contacts as DataFrame
pixels = clr.pixels()[:]
print(pixels.head())
# Columns: bin1_id, bin2_id, count

# Get contacts for a region
region_pixels = clr.pixels().fetch('chr1:0-10000000')
```

## Extract Contact Matrix

```python
# Get matrix for a chromosome
matrix = clr.matrix(balance=True).fetch('chr1')
print(f'Matrix shape: {matrix.shape}')

# Get matrix for a region
region_matrix = clr.matrix(balance=True).fetch('chr1:50000000-60000000')

# Get raw (unbalanced) matrix
raw_matrix = clr.matrix(balance=False).fetch('chr1')

# Sparse matrix for memory efficiency
from scipy import sparse
sparse_matrix = clr.matrix(balance=True, sparse=True).fetch('chr1')
```

## Extract Submatrix (Two Regions)

```python
# Get contacts between two regions
region1 = 'chr1:50000000-60000000'
region2 = 'chr1:70000000-80000000'
submatrix = clr.matrix(balance=True).fetch(region1, region2)
print(f'Submatrix shape: {submatrix.shape}')

# Inter-chromosomal contacts
inter_matrix = clr.matrix(balance=True).fetch('chr1', 'chr2')
```

## Convert from .hic to Cooler

```bash
# Using hic2cool CLI
hic2cool convert input.hic output.mcool -r 0  # All resolutions

# Specific resolution
hic2cool convert input.hic output.cool -r 10000
```

```python
# Python alternative using hic2cool
import hic2cool
hic2cool.hic2cool_convert('input.hic', 'output.mcool', resolution=0)
```

## Convert from Text Formats

```python
# From pairs file to cooler
# First create bins
import bioframe

chromsizes = bioframe.fetch_chromsizes('hg38')
bins = cooler.binnify(chromsizes, binsize=10000)

# Then aggregate pairs
cooler.create_cooler(
    'output.cool',
    bins,
    pixels=None,  # Will be loaded from pairs
    dtypes={'count': int},
)

# Or use cooler cload
# cooler cload pairs -c1 2 -p1 3 -c2 4 -p2 5 chromsizes.txt:10000 pairs.txt output.cool
```

## Create Cooler from Matrix

**Goal:** Convert an in-memory numpy contact matrix into a cooler file for use with cooltools and other Hi-C analysis tools.

**Approach:** Define genomic bins from chromosome sizes, convert the upper-triangle matrix entries into a pixel DataFrame of (bin1_id, bin2_id, count) tuples, and write to a new cooler file.

```python
import cooler
import numpy as np
import bioframe

# Create bins
chromsizes = bioframe.fetch_chromsizes('hg38')
bins = cooler.binnify(chromsizes, binsize=10000)

# Create pixel dataframe from matrix
n_bins = len(bins)
# matrix = np.random.poisson(1, (n_bins, n_bins))  # Your matrix here
# matrix = np.triu(matrix)  # Upper triangle

# Convert to pixels
pixels = []
for i in range(n_bins):
    for j in range(i, n_bins):
        if matrix[i, j] > 0:
            pixels.append({'bin1_id': i, 'bin2_id': j, 'count': matrix[i, j]})

pixels_df = pd.DataFrame(pixels)

# Create cooler
cooler.create_cooler('new.cool', bins, pixels_df)
```

## Merge Cooler Files

```python
# Merge multiple cooler files
cooler.merge_coolers('merged.cool', ['sample1.cool', 'sample2.cool'])
```

## Coarsen Resolution

```python
# Create lower resolution from high resolution
cooler.coarsen_cooler('hires.cool', 'lowres.cool', factor=10)  # 10x coarser

# Or using zoomify for multiple resolutions
cooler.zoomify_cooler('input.cool', 'output.mcool', resolutions=[10000, 50000, 100000, 500000])
```

## Export to Other Formats

```python
# Export matrix to numpy
matrix = clr.matrix(balance=True).fetch('chr1')
np.save('chr1_matrix.npy', matrix)

# Export to text
np.savetxt('chr1_matrix.txt', matrix, delimiter='\t')

# Export pixels to CSV
pixels = clr.pixels()[:]
pixels.to_csv('pixels.csv', index=False)
```

## Dump to Pairs Format

```bash
# Using cooler dump
cooler dump -t pixels --join matrix.cool > pairs.txt

# Dump bins
cooler dump -t bins matrix.cool > bins.txt
```

## Access Metadata

```python
# Get all metadata
print(clr.info)

# Specific metadata
print(f'Genome assembly: {clr.info.get("genome-assembly", "Unknown")}')
print(f'Creation date: {clr.info.get("creation-date", "Unknown")}')

# Check if balanced
if 'weight' in clr.bins().columns:
    print('Matrix has balancing weights')
```

## List Cooler Contents

```python
# For mcool
coolers = cooler.fileops.list_coolers('multi.mcool')
print(f'Available: {coolers}')

# Check if valid cooler
is_valid = cooler.fileops.is_cooler('file.cool')
print(f'Valid cooler: {is_valid}')
```

## Related Skills

- matrix-operations - Balance and normalize matrices
- hic-visualization - Visualize contact matrices
- contact-pairs - Process raw Hi-C pairs
