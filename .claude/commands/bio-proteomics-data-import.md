# bio-proteomics-data-import

> Load and parse mass spectrometry data formats including mzML, mzXML, and quantification tool outputs like MaxQuant proteinGroups.txt. Use when starting a proteomics analysis with raw or processed MS data. Handles contaminant filtering and missing value assessment.

## Version Compatibility

Reference examples tested with: MSnbase 2.28+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Mass Spectrometry Data Import

**"Load my mass spec data into Python"** → Parse mzML/mzXML raw files or MaxQuant proteinGroups.txt into data structures for programmatic access and downstream analysis.
- Python: `pyopenms.MzMLFile().load()` for raw spectra, `pandas.read_csv()` for search engine outputs
- R: `MSnbase::readMSData()` for raw, `read.delim()` for MaxQuant/Proteome Discoverer

## Loading mzML/mzXML Files with pyOpenMS

**Goal:** Parse raw mass spectrometry data files into memory for programmatic access.

**Approach:** Load mzML/mzXML into an MSExperiment object, then iterate spectra by MS level to access peaks and precursor info.

```python
from pyopenms import MSExperiment, MzMLFile, MzXMLFile

exp = MSExperiment()
MzMLFile().load('sample.mzML', exp)

for spectrum in exp:
    if spectrum.getMSLevel() == 1:
        mz, intensity = spectrum.get_peaks()
    elif spectrum.getMSLevel() == 2:
        precursor = spectrum.getPrecursors()[0]
        precursor_mz = precursor.getMZ()
```

## Loading MaxQuant Output

**Goal:** Import MaxQuant proteinGroups.txt with contaminant and decoy filtering.

**Approach:** Read the TSV file, remove reverse hits, contaminants, and site-only identifications, then extract intensity columns.

```python
import pandas as pd

protein_groups = pd.read_csv('proteinGroups.txt', sep='\t', low_memory=False)

# Filter contaminants and reverse hits
contam_col = 'Potential contaminant' if 'Potential contaminant' in protein_groups.columns else 'Contaminant'
protein_groups = protein_groups[
    (protein_groups.get(contam_col, '') != '+') &
    (protein_groups.get('Reverse', '') != '+') &
    (protein_groups.get('Only identified by site', '') != '+')
]

# Extract intensity columns (LFQ or iBAQ)
intensity_cols = [c for c in protein_groups.columns if c.startswith('LFQ intensity') or c.startswith('iBAQ ')]
if not intensity_cols:
    intensity_cols = [c for c in protein_groups.columns if c.startswith('Intensity ') and 'Intensity L' not in c]
intensities = protein_groups[['Protein IDs', 'Gene names'] + intensity_cols]
```

## Loading Spectronaut/DIA-NN Output

**Goal:** Import DIA-NN long-format report and reshape into a protein-by-sample quantification matrix.

**Approach:** Pivot the report table on protein group and run columns, using MaxLFQ values.

```python
diann_report = pd.read_csv('report.tsv', sep='\t')

# Pivot to protein-level matrix
protein_matrix = diann_report.pivot_table(
    index='Protein.Group', columns='Run', values='PG.MaxLFQ', aggfunc='first'
)
```

## R: Loading with MSnbase

**Goal:** Load raw MS data in R for interactive exploration of spectra and metadata.

**Approach:** Use MSnbase's on-disk reading mode to access spectra and feature metadata without loading all data into memory.

```r
library(MSnbase)

raw_data <- readMSData('sample.mzML', mode = 'onDisk')
spectra <- spectra(raw_data)
header_info <- fData(raw_data)
```

## Missing Value Assessment

**Goal:** Quantify missing value patterns across proteins and samples in an intensity matrix.

**Approach:** Count NaN values per protein and per sample, then compute overall missing percentage.

```python
def assess_missing_values(df, intensity_cols):
    missing_per_protein = df[intensity_cols].isna().sum(axis=1)
    missing_per_sample = df[intensity_cols].isna().sum(axis=0)

    total_missing = df[intensity_cols].isna().sum().sum()
    total_values = df[intensity_cols].size
    missing_pct = 100 * total_missing / total_values

    return {'per_protein': missing_per_protein, 'per_sample': missing_per_sample, 'total_pct': missing_pct}
```

## Related Skills

- quantification - Process imported data for quantification
- peptide-identification - Identify peptides from raw spectra
- expression-matrix/counts-ingest - Similar data loading patterns
