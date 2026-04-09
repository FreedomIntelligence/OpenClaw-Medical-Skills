# bio-proteomics-quantification

> Protein quantification from mass spectrometry data including label-free (LFQ, intensity-based), isobaric labeling (TMT, iTRAQ), and metabolic labeling (SILAC) approaches. Use when extracting protein abundances from MS data for differential analysis.

## Version Compatibility

Reference examples tested with: MSnbase 2.28+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Protein Quantification

**"Quantify proteins from my mass spec data"** → Extract protein abundances from MS data using label-free (LFQ, spectral counting), isobaric labeling (TMT, iTRAQ), or metabolic labeling (SILAC) approaches.
- R: `MSstats::dataProcess()` for feature-to-protein summarization
- Python: `pandas` for MaxLFQ-style normalization and ratio calculation
- R: `MSnbase` for isobaric tag reporter ion extraction

## Label-Free Quantification (LFQ)

### Intensity-Based (MaxLFQ Algorithm)

```python
import pandas as pd
import numpy as np

def maxlfq_normalize(intensities):
    '''Simplified MaxLFQ normalization'''
    log_int = np.log2(intensities.replace(0, np.nan))

    # Median centering per sample
    sample_medians = log_int.median(axis=0)
    global_median = sample_medians.median()
    normalized = log_int - sample_medians + global_median

    return normalized
```

### Spectral Counting

```python
def spectral_count_normalize(counts, total_spectra):
    '''Normalized spectral abundance factor (NSAF)'''
    # Divide by protein length, then by total
    nsaf = counts / total_spectra
    return nsaf / nsaf.sum()
```

## TMT/iTRAQ Quantification

```r
library(MSnbase)

# Load reporter ion data
tmt_data <- readMSnSet('tmt_data.txt')

# Normalize with reference channel
tmt_normalized <- normalize(tmt_data, method = 'center.median')

# Summarize to protein level
protein_data <- combineFeatures(tmt_normalized, groupBy = fData(tmt_data)$protein,
                                 fun = 'median')
```

### Python TMT Processing

```python
def extract_tmt_intensities(spectrum, reporter_mz, tolerance=0.003):
    '''Extract TMT reporter ion intensities'''
    mz, intensity = spectrum.get_peaks()
    tmt_intensities = {}

    for channel, target_mz in reporter_mz.items():
        mask = np.abs(mz - target_mz) < tolerance
        if mask.any():
            tmt_intensities[channel] = intensity[mask].max()
        else:
            tmt_intensities[channel] = 0

    return tmt_intensities

TMT_10PLEX = {'126': 126.127726, '127N': 127.124761, '127C': 127.131081,
              '128N': 128.128116, '128C': 128.134436, '129N': 129.131471,
              '129C': 129.137790, '130N': 130.134825, '130C': 130.141145,
              '131': 131.138180}
```

## SILAC Quantification

```python
def calculate_silac_ratio(heavy_intensity, light_intensity):
    '''Calculate SILAC H/L ratio'''
    if light_intensity > 0 and heavy_intensity > 0:
        return np.log2(heavy_intensity / light_intensity)
    return np.nan

# Typical mass shifts
SILAC_SHIFTS = {
    'Arg10': 10.008269,  # 13C6 15N4 Arginine
    'Lys8': 8.014199,    # 13C6 15N2 Lysine
    'Arg6': 6.020129,    # 13C6 Arginine
    'Lys6': 6.020129     # 13C6 Lysine
}
```

## MSstats Workflow (R)

**Goal:** Convert MaxQuant output into normalized protein-level abundance estimates using MSstats feature-to-protein summarization.

**Approach:** Reformat MaxQuant evidence and proteinGroups files into MSstats input format, then apply median equalization normalization with Tukey's median polish for protein-level summarization.

```r
library(MSstats)

# Prepare input from MaxQuant
maxquant_input <- MaxQtoMSstatsFormat(
    evidence = read.table('evidence.txt', sep = '\t', header = TRUE),
    proteinGroups = read.table('proteinGroups.txt', sep = '\t', header = TRUE),
    annotation = read.csv('annotation.csv')
)

# Process and normalize
processed <- dataProcess(maxquant_input, normalization = 'equalizeMedians',
                         summaryMethod = 'TMP', censoredInt = 'NA')

# Protein-level summary
protein_summary <- quantification(processed)
```

## Related Skills

- data-import - Load MS data before quantification
- differential-abundance - Statistical testing after quantification
- expression-matrix/counts-ingest - Similar matrix handling
