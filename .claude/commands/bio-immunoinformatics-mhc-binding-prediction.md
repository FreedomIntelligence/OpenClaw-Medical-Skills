# bio-immunoinformatics-mhc-binding-prediction

> Predict peptide-MHC class I and II binding affinity using MHCflurry and NetMHCpan neural network models. Identify potential T-cell epitopes from protein sequences. Use when predicting MHC binding for vaccine design or neoantigen identification.

## Version Compatibility

Reference examples tested with: MHCflurry 2.1+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# MHC Binding Prediction

**"Predict which peptides bind to MHC"** → Predict peptide-MHC class I and II binding affinity using neural network models to identify potential T-cell epitopes from protein sequences.
- Python: `mhcflurry.Class1PresentationPredictor().predict()` for MHC-I
- CLI: `netMHCpan` for alternative MHC-I/II predictions

## MHCflurry Setup

**Goal:** Install MHCflurry and download pre-trained prediction models.

**Approach:** Install via pip and fetch model weights for class I pan-allele or specific allele predictions.

```bash
# Install MHCflurry
pip install mhcflurry

# Download prediction models
mhcflurry-downloads fetch

# Download models for specific alleles
mhcflurry-downloads fetch models_class1_pan
```

## MHCflurry Python API

**Goal:** Predict peptide-MHC binding affinity and presentation scores for a set of peptides.

**Approach:** Load the Class1PresentationPredictor and call predict() with peptide-allele pairs to obtain IC50, percentile rank, and presentation scores.

```python
from mhcflurry import Class1PresentationPredictor

# Load predictor (includes binding and processing scores)
predictor = Class1PresentationPredictor.load()

# Predict for single allele
result = predictor.predict(
    peptides=['SIINFEKL', 'GILGFVFTL', 'NLVPMVATV'],
    alleles=['HLA-A*02:01', 'HLA-A*02:01', 'HLA-A*02:01']
)

# Result columns:
# - mhcflurry_affinity: Predicted IC50 (nM)
# - mhcflurry_affinity_percentile: Percentile rank
# - mhcflurry_presentation_score: Combined binding + processing

print(result)
```

## Interpret Binding Predictions

**Goal:** Classify peptide-MHC binding strength from predicted IC50 values.

**Approach:** Apply standard affinity thresholds (strong <50nM, moderate <500nM, weak <5000nM) to categorize binding.

```python
def interpret_binding(ic50_nm):
    '''Interpret MHC binding affinity

    IC50 thresholds (commonly used):
    - <50 nM: Strong binder (high confidence epitope)
    - 50-500 nM: Moderate binder (potential epitope)
    - 500-5000 nM: Weak binder (unlikely epitope)
    - >5000 nM: Non-binder

    Percentile rank (recommended):
    - <0.5%: Strong binder
    - 0.5-2%: Moderate binder
    - >2%: Weak/non-binder
    '''
    if ic50_nm < 50:
        return 'strong'
    elif ic50_nm < 500:
        return 'moderate'
    elif ic50_nm < 5000:
        return 'weak'
    else:
        return 'non-binder'
```

## Batch Prediction

**Goal:** Predict binding for all peptide-allele combinations in a batch.

**Approach:** Iterate over peptide-allele pairs, call MHCflurry for each combination, and concatenate results into a single DataFrame.

```python
from mhcflurry import Class1PresentationPredictor
import pandas as pd

def predict_binding_batch(peptides, alleles):
    '''Predict binding for multiple peptides and alleles

    Args:
        peptides: List of peptide sequences
        alleles: List of HLA alleles (4-digit format)

    Returns:
        DataFrame with predictions for all combinations
    '''
    predictor = Class1PresentationPredictor.load()

    # Create all combinations
    results = []
    for peptide in peptides:
        for allele in alleles:
            pred = predictor.predict(
                peptides=[peptide],
                alleles=[allele]
            )
            pred['peptide'] = peptide
            pred['allele'] = allele
            results.append(pred)

    return pd.concat(results, ignore_index=True)


# Example usage
peptides = ['SIINFEKL', 'GILGFVFTL', 'NLVPMVATV', 'YMLDLQPETT']
alleles = ['HLA-A*02:01', 'HLA-A*03:01', 'HLA-B*07:02']

predictions = predict_binding_batch(peptides, alleles)
print(predictions[['peptide', 'allele', 'mhcflurry_affinity', 'mhcflurry_affinity_percentile']])
```

## Scan Protein Sequence

**Goal:** Identify all potential MHC-I epitopes within a protein by scanning overlapping peptide windows.

**Approach:** Generate all k-mers (8-11aa) from the protein, predict binding for each against target alleles, and retain those below the 2% percentile rank cutoff.

```python
def scan_protein_for_epitopes(protein_seq, alleles, peptide_lengths=[8, 9, 10, 11]):
    '''Scan protein for potential MHC epitopes

    MHC-I typically binds 8-11mer peptides
    Most common: 9-mers

    Returns all peptides with predicted binding
    '''
    from mhcflurry import Class1PresentationPredictor

    predictor = Class1PresentationPredictor.load()

    epitopes = []
    for length in peptide_lengths:
        for i in range(len(protein_seq) - length + 1):
            peptide = protein_seq[i:i + length]

            for allele in alleles:
                pred = predictor.predict(peptides=[peptide], alleles=[allele])

                if pred['mhcflurry_affinity_percentile'].values[0] < 2.0:
                    epitopes.append({
                        'peptide': peptide,
                        'position': i + 1,
                        'length': length,
                        'allele': allele,
                        'affinity_nM': pred['mhcflurry_affinity'].values[0],
                        'percentile': pred['mhcflurry_affinity_percentile'].values[0]
                    })

    return pd.DataFrame(epitopes)
```

## MHC Class II Prediction

**Goal:** Predict MHC class II binding for longer peptides (13-25aa) relevant to CD4+ T-cell responses.

**Approach:** Query the IEDB NetMHCIIpan API since MHCflurry focuses on class I; submit peptide-allele pairs and parse results.

```python
def predict_mhc_ii(peptides, alleles):
    '''Predict MHC class II binding

    MHC-II binds longer peptides (13-25 aa)
    Binding core is ~9aa but flanking regions matter

    Note: MHCflurry focuses on class I
    For class II, use NetMHCIIpan or IEDB tools
    '''
    # NetMHCIIpan via IEDB API
    import requests

    url = 'http://tools-cluster-interface.iedb.org/tools_api/mhcii/'

    results = []
    for peptide in peptides:
        for allele in alleles:
            params = {
                'method': 'netmhciipan_ba',
                'sequence_text': peptide,
                'allele': allele,
                'length': '15'
            }

            response = requests.post(url, data=params)
            # Parse response...

    return results
```

## Common HLA Alleles

**Goal:** Define population-representative HLA allele sets for broad epitope coverage analysis.

**Approach:** Use curated lists of the most frequent HLA-A and HLA-B alleles covering ~85% of the Caucasian population.

```python
# Most common HLA-A alleles (cover ~85% of population)
COMMON_HLA_A = [
    'HLA-A*02:01',  # ~30% Caucasian
    'HLA-A*01:01',  # ~15%
    'HLA-A*03:01',  # ~13%
    'HLA-A*24:02',  # ~10%
    'HLA-A*11:01',  # ~8%
]

# Most common HLA-B alleles
COMMON_HLA_B = [
    'HLA-B*07:02',
    'HLA-B*08:01',
    'HLA-B*44:02',
    'HLA-B*15:01',
    'HLA-B*35:01',
]

def get_patient_alleles(hla_typing_result):
    '''Parse HLA typing result

    Patients have 2 alleles per locus (one from each parent)
    Format: HLA-A*02:01, HLA-A*24:02
    '''
    # Typically 6 alleles: 2 HLA-A, 2 HLA-B, 2 HLA-C
    return hla_typing_result.split(',')
```

## Related Skills

- immunoinformatics/neoantigen-prediction - Tumor neoantigen discovery
- immunoinformatics/epitope-prediction - B-cell epitope prediction
- clinical-databases/hla-typing - Determine patient HLA type
