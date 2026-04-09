# bio-metabolomics-metabolite-annotation

> Metabolite identification from m/z and retention time. Covers database matching, MS/MS spectral matching, and confidence level assignment. Use when assigning compound identities to detected features in untargeted metabolomics.

## Version Compatibility

Reference examples tested with: pandas 2.2+, xcms 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolite Annotation

## Database Matching by m/z

**Goal:** Generate putative metabolite identifications by matching observed m/z values against HMDB.

**Approach:** Convert m/z to neutral mass by subtracting adduct mass, then query HMDB within a specified ppm tolerance.

**"Annotate my metabolomics features with compound identities"** → Match detected features against metabolite databases by exact mass, MS/MS spectra, and retention time to assign compound identities with confidence levels.

```r
library(MetaboAnalystR)

# Load feature table
features <- read.csv('feature_table.csv')

# Search HMDB by exact mass
search_hmdb <- function(mz, adduct = '[M+H]+', ppm = 10) {
    # Calculate neutral mass from m/z
    adduct_masses <- list(
        '[M+H]+' = 1.007276,
        '[M+Na]+' = 22.989218,
        '[M-H]-' = -1.007276,
        '[M+Cl]-' = 34.969402
    )

    neutral_mass <- mz - adduct_masses[[adduct]]

    # Query HMDB (or local database)
    # Returns putative matches
    matches <- QueryHMDB(neutral_mass, ppm)
    return(matches)
}

# Apply to all features
annotations <- lapply(features$mz, function(m) search_hmdb(m, '[M+H]+', 10))
```

## MS/MS Spectral Matching

```python
from matchms import calculate_scores
from matchms.importing import load_from_mgf
from matchms.similarity import CosineGreedy

# Load query spectra
queries = list(load_from_mgf('sample_msms.mgf'))

# Load reference library (e.g., GNPS, MassBank)
references = list(load_from_mgf('reference_library.mgf'))

# Calculate similarity scores
similarity = CosineGreedy(tolerance=0.01)
scores = calculate_scores(references, queries, similarity)

# Get best matches
for query_idx, query in enumerate(queries):
    best_match_idx = scores.scores[:, query_idx].argmax()
    best_score = scores.scores[best_match_idx, query_idx]

    if best_score > 0.7:
        ref = references[best_match_idx]
        print(f'{query.get("precursor_mz")}: {ref.get("compound_name")} (score={best_score:.2f})')
```

## SIRIUS + CSI:FingerID

```bash
# Molecular formula and structure prediction
sirius \
    --input sample.ms \
    --output sirius_results \
    --database hmdb \
    formula \
    fingerid

# Output structure:
# sirius_results/
#   compound_1/
#     formula_candidates.tsv
#     fingerid_candidates.tsv
```

## MetFrag In Silico Fragmentation

```r
library(metfRag)

# Configure MetFrag search
settings <- list(
    DatabaseSearchRelativeMassDeviation = 10,
    FragmentPeakMatchAbsoluteMassDeviation = 0.01,
    FragmentPeakMatchRelativeMassDeviation = 10,
    MetFragDatabaseType = 'HMDB',
    NeutralPrecursorMass = 147.0532
)

# Run fragmentation prediction
results <- run.metfrag(settings, spectrum_file = 'query_spectrum.txt')
```

## RT Prediction for Validation

```python
from deepchem.models import GraphConvModel
import pandas as pd

# Use predicted RT to validate annotations
# Compare observed RT with predicted RT from chemical structure

def validate_annotation(observed_rt, smiles, rt_model):
    '''Check if observed RT matches prediction'''
    predicted_rt = rt_model.predict(smiles)
    rt_error = abs(observed_rt - predicted_rt)

    if rt_error < 30:  # seconds
        return 'confident'
    elif rt_error < 60:
        return 'probable'
    else:
        return 'unlikely'
```

## Confidence Levels (MSI)

```r
# Metabolomics Standards Initiative levels
assign_confidence <- function(annotation) {
    if (!is.null(annotation$authentic_standard)) {
        return(1)  # Identified by authentic standard
    } else if (!is.null(annotation$msms_match) && annotation$msms_score > 0.8) {
        return(2)  # MS/MS match to database
    } else if (!is.null(annotation$formula_match)) {
        return(3)  # Formula confirmed
    } else if (!is.null(annotation$mass_match)) {
        return(4)  # Mass match only
    } else {
        return(5)  # Unknown
    }
}

# Apply to annotations
features$confidence_level <- sapply(annotations, assign_confidence)
```

## CAMERA Adduct Annotation

```r
library(CAMERA)

# Identify adduct and isotope patterns
xsa <- xsAnnotate(xcms_set)
xsa <- groupFWHM(xsa, perfwhm = 0.6)
xsa <- findIsotopes(xsa, mzabs = 0.01, ppm = 10)
xsa <- findAdducts(xsa, polarity = 'positive',
                   rules = c('[M+H]+', '[M+Na]+', '[M+K]+', '[M+NH4]+'))

# Get annotated features
annotated <- getPeaklist(xsa)
annotated$adduct  # Adduct assignment
annotated$isotopes  # Isotope group
annotated$pcgroup  # Correlation group
```

## Batch Annotation Pipeline

```r
library(tidyverse)

annotate_features <- function(feature_table, ppm = 10, polarity = 'positive') {
    results <- feature_table %>%
        rowwise() %>%
        mutate(
            # Calculate possible neutral masses
            mass_h = ifelse(polarity == 'positive', mz - 1.007276, mz + 1.007276),

            # Query databases
            hmdb_match = list(query_hmdb(mass_h, ppm)),
            kegg_match = list(query_kegg(mass_h, ppm)),

            # Best match
            best_match = get_best_match(hmdb_match, kegg_match),
            compound_name = best_match$name,
            compound_id = best_match$id,
            mass_error_ppm = (abs(mz - best_match$mz) / mz) * 1e6
        )

    return(results)
}

# Example query functions (implement based on your database access)
query_hmdb <- function(mass, ppm) {
    # Query HMDB API or local database
    # Return list of matches with name, id, formula, mass
}
```

## Export Annotated Results

```r
# Create annotation report
annotation_report <- features %>%
    select(feature_id, mz, rt, compound_name, compound_id,
           formula, confidence_level, mass_error_ppm, adduct) %>%
    arrange(confidence_level, desc(intensity))

write.csv(annotation_report, 'annotated_features.csv', row.names = FALSE)

# Summary
cat('Annotation summary:\n')
cat('  Level 1 (confirmed):', sum(annotation_report$confidence_level == 1), '\n')
cat('  Level 2 (MS/MS match):', sum(annotation_report$confidence_level == 2), '\n')
cat('  Level 3 (formula):', sum(annotation_report$confidence_level == 3), '\n')
cat('  Level 4 (mass only):', sum(annotation_report$confidence_level == 4), '\n')
cat('  Unknown:', sum(annotation_report$confidence_level == 5), '\n')
```

## Related Skills

- xcms-preprocessing - Generate feature table
- pathway-mapping - Map annotated metabolites to pathways
- proteomics/spectral-libraries - Similar spectral matching concepts
