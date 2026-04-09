# bio-proteomics-spectral-libraries

> Build, manage, and search spectral libraries for proteomics. Use when creating or working with spectral libraries for DIA analysis. Covers DDA-based library generation, predicted libraries (Prosit, DeepLC), and library formats.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spectral Library Management

**"Build a spectral library for DIA analysis"** → Create, filter, and manage spectral libraries from DDA experiments or predicted spectra for use in DIA quantification workflows.
- CLI: `spectrast` (TPP) for consensus library building from search results
- CLI: Prosit/DeepLC for deep learning-predicted spectral libraries
- Python: `pandas` for library format conversion and quality filtering

## Build Library from DDA Data

### SpectraST (TPP)

```bash
# Build library from search results
spectrast -cNlibrary.splib -cAC search_results.pep.xml

# Filter library for quality
spectrast -cNfiltered.splib -cAQ library.splib

# Convert to other formats
spectrast -cNlibrary.tsv -cM library.splib
```

### EasyPQP (Skyline/OpenMS)

```bash
# Build library from search results
easypqp library \
    --in psm_results.tsv \
    --out library.pqp \
    --psmtsv \
    --rt_reference irt.tsv

# Convert to TSV format
easypqp convert \
    --in library.pqp \
    --out library.tsv \
    --format openswath
```

### EncyclopeDIA (Walnut)

```bash
# Build chromatogram library from DIA
EncyclopeDIA \
    -i sample1.mzML \
    -i sample2.mzML \
    -l wide_window_library.dlib \
    -f uniprot.fasta \
    -o results

# Search with narrow-window DIA
EncyclopeDIA \
    -i narrow_sample.mzML \
    -l narrow_library.elib \
    -f uniprot.fasta \
    -o search_results
```

## Predicted Libraries

### Prosit (Deep Learning)

```python
# Generate predictions via Prosit API
import requests
import pandas as pd

peptides = pd.DataFrame({
    'modified_sequence': ['PEPTIDEK', 'ANOTHERPEPTIDER'],
    'collision_energy': [30, 30],
    'precursor_charge': [2, 2]
})

# Submit to Prosit server
response = requests.post(
    'https://www.proteomicsdb.org/prosit/api/predict',
    json=peptides.to_dict(orient='records')
)

# Parse response to library format
predictions = response.json()
```

### DeepLC Retention Time Prediction

```python
from deeplc import DeepLC

# Initialize predictor
dlc = DeepLC()

# Predict retention times
peptides = ['PEPTIDEK', 'ANOTHERPEPTIDER']
calibration_peptides = ['GAGSSEPVTGLDAK', 'VEATFGVDESNAK']
calibration_rts = [22.4, 33.1]

# Calibrate and predict
dlc.calibrate_preds(
    seq_df=pd.DataFrame({'seq': calibration_peptides, 'rt': calibration_rts})
)
predicted_rts = dlc.make_preds(seq_df=pd.DataFrame({'seq': peptides}))
```

### MS2PIP Fragmentation Prediction

```python
from ms2pip import Predictor

# Initialize predictor
predictor = Predictor(model='HCD2021')

# Predict fragmentation
peptide_df = pd.DataFrame({
    'peptide': ['PEPTIDEK', 'ANOTHERPEPTIDER'],
    'charge': [2, 2],
    'modifications': ['', '']
})

predictions = predictor.predict(peptide_df)
```

## Library Formats

### DIA-NN TSV Format

```
# Required columns
PrecursorMz    ProductMz    Annotation    ProteinId    GeneName
PeptideSequence    ModifiedSequence    PrecursorCharge
FragmentCharge    FragmentType    FragmentSeriesNumber
NormalizedRetentionTime    LibraryIntensity
```

### OpenSWATH TSV Format

```python
import pandas as pd

# Convert to OpenSWATH format
library = pd.DataFrame({
    'PrecursorMz': precursor_mz,
    'ProductMz': product_mz,
    'LibraryIntensity': intensity,
    'NormalizedRetentionTime': rt,
    'PrecursorCharge': charge,
    'ProductCharge': 1,
    'FragmentType': ion_type,  # 'b' or 'y'
    'FragmentSeriesNumber': ion_num,
    'ModifiedPeptideSequence': mod_seq,
    'PeptideSequence': sequence,
    'ProteinId': protein,
    'GeneName': gene,
    'Decoy': 0
})

library.to_csv('library_openswath.tsv', sep='\t', index=False)
```

### Spectronaut Library Format

```
# Key columns for Spectronaut
ModifiedPeptide    StrippedPeptide    PrecursorCharge
PrecursorMz    iRT    FragmentLossType
FragmentCharge    FragmentType    FragmentNumber
RelativeIntensity    FragmentMz    ProteinGroups
Genes    ProteinIds
```

## Library QC

```python
import pandas as pd

library = pd.read_csv('library.tsv', sep='\t')

# Basic statistics
print(f"Precursors: {library['ModifiedSequence'].nunique()}")
print(f"Proteins: {library['ProteinId'].nunique()}")
print(f"Transitions per precursor: {len(library) / library['ModifiedSequence'].nunique():.1f}")

# RT distribution
import matplotlib.pyplot as plt
rts = library.groupby('ModifiedSequence')['NormalizedRetentionTime'].first()
plt.hist(rts, bins=50)
plt.xlabel('Normalized RT')
plt.ylabel('Precursors')
plt.savefig('rt_distribution.png')

# Charge state distribution
charges = library.groupby('ModifiedSequence')['PrecursorCharge'].first()
print(charges.value_counts())
```

## Merge Libraries

**Goal:** Combine multiple spectral libraries into a single non-redundant library, keeping the highest-quality spectra for each precursor.

**Approach:** Concatenate library tables, rank precursors by total fragment intensity, and deduplicate by keeping the best-scoring entry per precursor-fragment combination.

```python
import pandas as pd

# Load libraries
lib1 = pd.read_csv('library1.tsv', sep='\t')
lib2 = pd.read_csv('library2.tsv', sep='\t')

# Concatenate and remove duplicates
# Keep entry with highest total intensity per precursor
combined = pd.concat([lib1, lib2])

# Calculate total intensity per precursor
precursor_intensity = combined.groupby('ModifiedSequence')['LibraryIntensity'].sum()

# Keep best precursor entries
combined['total_int'] = combined['ModifiedSequence'].map(precursor_intensity)
combined = combined.sort_values('total_int', ascending=False)
combined = combined.drop_duplicates(subset=['ModifiedSequence', 'FragmentType', 'FragmentSeriesNumber'])
combined = combined.drop('total_int', axis=1)

combined.to_csv('merged_library.tsv', sep='\t', index=False)
```

## iRT Calibration

```python
# Biognosys iRT peptides for retention time calibration
IRT_PEPTIDES = {
    'LGGNEQVTR': -24.92,
    'GAGSSEPVTGLDAK': 0.00,  # Reference
    'VEATFGVDESNAK': 12.39,
    'YILAGVENSK': 19.79,
    'TPVISGGPYEYR': 28.71,
    'TPVITGAPYEYR': 33.38,
    'DGLDAASYYAPVR': 42.26,
    'ADVTPADFSEWSK': 54.62,
    'GTFIIDPGGVIR': 70.52,
    'GTFIIDPAAVIR': 87.23,
    'LFLQFGAQGSPFLK': 100.00
}

# Convert iRT to normalized RT
def irt_to_nrt(irt, gradient_length=60):
    '''Convert iRT to normalized RT (0-1 scale)'''
    return (irt + 24.92) / 124.92  # Scale to 0-1
```

## Related Skills

- dia-analysis - Use libraries in DIA workflows
- peptide-identification - Generate search results for library building
- data-import - Load MS data for library generation
