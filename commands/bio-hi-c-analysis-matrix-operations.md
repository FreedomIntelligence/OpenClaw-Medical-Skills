# bio-hi-c-analysis-matrix-operations

> Balance, normalize, and transform Hi-C contact matrices using cooler and cooltools. Apply iterative correction (ICE), compute expected values, and generate observed/expected matrices. Use when normalizing or transforming Hi-C matrices.

## Version Compatibility

Reference examples tested with: cooler 0.9+, cooltools 0.6+, numpy 1.26+, pandas 2.2+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Hi-C Matrix Operations

**"Normalize my Hi-C contact matrix"** → Apply iterative correction (ICE/KR balancing), compute distance-decay expected values, and generate observed/expected ratio matrices.
- Python: `cooler.balance_cooler(clr)`, `cooltools.expected_cis(clr)`

Balance, normalize, and transform contact matrices.

## Required Imports

```python
import cooler
import cooltools
import numpy as np
import pandas as pd
```

## Matrix Balancing (ICE)

```python
# Balance a cooler file (iterative correction)
cooler.balance_cooler('matrix.cool', store=True, cis_only=True)

# The balanced weights are stored in the 'weight' column
clr = cooler.Cooler('matrix.cool')
weights = clr.bins()['weight'][:]
print(f'Balanced weights range: {weights.min():.4f} - {weights.max():.4f}')
```

## Balance with CLI

```bash
# Balance using cooler CLI
cooler balance matrix.cool --cis-only --force

# Check balance status
cooler info matrix.cool | grep "weight"
```

## Access Balanced vs Raw Matrix

```python
clr = cooler.Cooler('matrix.cool')

# Balanced (normalized) matrix
balanced = clr.matrix(balance=True).fetch('chr1')

# Raw (count) matrix
raw = clr.matrix(balance=False).fetch('chr1')

print(f'Raw sum: {raw.sum():.0f}')
print(f'Balanced sum: {np.nansum(balanced):.4f}')
```

## Compute Expected Values

```python
import cooltools

clr = cooler.Cooler('matrix.cool')

# Compute expected (average by distance)
expected = cooltools.expected_cis(clr, ignore_diags=2)
print(expected.head())
# Columns: region1, region2, dist, n_valid, count.sum, balanced.sum, balanced.avg
```

## Observed/Expected Matrix

**Goal:** Remove the distance-dependent decay from a contact matrix so that enriched interactions (loops, compartments) stand out above the background.

**Approach:** Compute the average contact frequency at each genomic distance (expected), then divide each observed pixel by its distance-matched expected value to produce an O/E ratio matrix.

```python
import cooltools

clr = cooler.Cooler('matrix.cool')

# Compute expected
expected = cooltools.expected_cis(clr, ignore_diags=2)

# Get O/E matrix for a region
def get_oe_matrix(clr, region, expected_df):
    matrix = clr.matrix(balance=True).fetch(region)
    n = matrix.shape[0]

    # Get expected values for this chromosome
    chrom = region.split(':')[0]
    exp_chr = expected_df[expected_df['region1'] == chrom]
    exp_values = exp_chr.set_index('dist')['balanced.avg']

    # Create expected matrix
    expected_matrix = np.zeros_like(matrix)
    for i in range(n):
        for j in range(n):
            dist = abs(i - j)
            if dist in exp_values.index:
                expected_matrix[i, j] = exp_values[dist]

    # Compute O/E
    oe = matrix / expected_matrix
    oe[expected_matrix == 0] = np.nan

    return oe

oe_matrix = get_oe_matrix(clr, 'chr1', expected)
```

## Using cooltools for O/E

```python
import cooltools

clr = cooler.Cooler('matrix.cool')

# Compute expected
expected = cooltools.expected_cis(clr, ignore_diags=2)

# Get O/E normalized matrix
# cooltools provides this through the snipping module
from cooltools.lib import snip

# For a specific region pair
region1 = ('chr1', 50000000, 60000000)
region2 = ('chr1', 50000000, 60000000)

# Snippet
snippet = snip.snip_pileup(
    clr.matrix(balance=True),
    region1,
    region2,
    exp_func=None,  # Add expected function for O/E
)
```

## Log Transform

```python
# Log2 transform of O/E matrix
log_oe = np.log2(oe_matrix)
log_oe[np.isinf(log_oe)] = np.nan

print(f'Log2(O/E) range: {np.nanmin(log_oe):.2f} to {np.nanmax(log_oe):.2f}')
```

## Distance Decay Normalization

```python
def distance_normalize(matrix, decay_func=None):
    '''Normalize by expected distance decay'''
    n = matrix.shape[0]
    normalized = np.zeros_like(matrix)

    for diag in range(n):
        diag_values = np.diag(matrix, diag)
        expected = np.nanmean(diag_values) if decay_func is None else decay_func(diag)
        if expected > 0:
            for i in range(n - diag):
                normalized[i, i + diag] = matrix[i, i + diag] / expected
                normalized[i + diag, i] = matrix[i + diag, i] / expected

    return normalized
```

## Aggregate Multiple Replicates

```python
# Sum matrices from multiple replicates
files = ['rep1.cool', 'rep2.cool', 'rep3.cool']
matrices = []

for f in files:
    clr = cooler.Cooler(f)
    m = clr.matrix(balance=False).fetch('chr1')
    matrices.append(m)

# Sum raw matrices
summed = np.sum(matrices, axis=0)

# Then balance the summed result
```

## Smooth Matrix

```python
from scipy.ndimage import uniform_filter

# Apply smoothing
smoothed = uniform_filter(matrix, size=3, mode='constant')

# Gaussian smoothing
from scipy.ndimage import gaussian_filter
smoothed_gauss = gaussian_filter(matrix, sigma=1)
```

## Downsample/Coarsen Matrix

```python
def coarsen_matrix(matrix, factor):
    '''Coarsen matrix by summing bins'''
    n = matrix.shape[0]
    new_n = n // factor
    coarse = np.zeros((new_n, new_n))

    for i in range(new_n):
        for j in range(new_n):
            coarse[i, j] = np.nansum(matrix[
                i*factor:(i+1)*factor,
                j*factor:(j+1)*factor
            ])

    return coarse

coarse_matrix = coarsen_matrix(matrix, factor=10)
```

## Correlation Matrix

```python
# Compute correlation matrix (for compartment analysis)
from scipy.stats import pearsonr

def correlation_matrix(matrix):
    '''Compute Pearson correlation between rows'''
    n = matrix.shape[0]
    corr = np.zeros((n, n))

    # Remove rows with all NaN
    valid_rows = ~np.all(np.isnan(matrix), axis=1)
    valid_matrix = matrix[valid_rows][:, valid_rows]

    for i in range(valid_matrix.shape[0]):
        for j in range(valid_matrix.shape[0]):
            mask = ~(np.isnan(valid_matrix[i]) | np.isnan(valid_matrix[j]))
            if mask.sum() > 2:
                corr[i, j], _ = pearsonr(valid_matrix[i, mask], valid_matrix[j, mask])

    return corr

corr = correlation_matrix(oe_matrix)
```

## Save Modified Matrix

```python
# Save matrix as numpy array
np.save('processed_matrix.npy', oe_matrix)

# Create new cooler with modified values
# (More complex, usually work with existing files)
```

## Related Skills

- hic-data-io - Load and access cooler files
- compartment-analysis - Use O/E matrices for compartments
- hic-visualization - Visualize processed matrices
