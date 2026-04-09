# bio-proteomics-peptide-identification

> Peptide-spectrum matching and protein identification from MS/MS data. Use when identifying peptides from tandem mass spectra. Covers database searching, spectral library matching, and FDR estimation using target-decoy approaches.

## Version Compatibility

Reference examples tested with: MSnbase 2.28+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Peptide Identification

**"Identify peptides from my MS/MS spectra"** → Match tandem mass spectra against a protein database to identify peptide sequences, then control false discovery rate using target-decoy competition.
- Python: `pyopenms` for in-memory database search and PSM handling
- CLI: `comet`, `MSFragger`, `X!Tandem` for high-throughput database searching
- R: `MSnbase::readMSData()` for importing search results

## Database Search with pyOpenMS

**Goal:** Identify peptide sequences from tandem mass spectra by matching against a protein database.

**Approach:** Load a FASTA database, perform in-silico tryptic digestion to generate theoretical peptides, then match experimental spectra against theoretical fragment ion patterns to identify peptide-spectrum matches (PSMs).

```python
from pyopenms import MSExperiment, MzMLFile, FASTAFile, ProteaseDigestion
from pyopenms import ModificationsDB, AASequence

# Load FASTA database
fasta_entries = []
FASTAFile().load('uniprot_human.fasta', fasta_entries)

# In-silico digestion
digestion = ProteaseDigestion()
digestion.setEnzyme('Trypsin')
digestion.setMissedCleavages(2)

peptides = []
for entry in fasta_entries:
    seq = AASequence.fromString(entry.sequence)
    result = []
    digestion.digest(seq, result)
    peptides.extend([(entry.identifier, str(p)) for p in result])
```

## Working with Search Results (idXML)

```python
from pyopenms import IdXMLFile, ProteinIdentification, PeptideIdentification

protein_ids = []
peptide_ids = []
IdXMLFile().load('search_results.idXML', protein_ids, peptide_ids)

for pep_id in peptide_ids:
    rt = pep_id.getRT()
    mz = pep_id.getMZ()
    for hit in pep_id.getHits():
        sequence = hit.getSequence()
        score = hit.getScore()
        charge = hit.getCharge()
```

## FDR Estimation (Target-Decoy)

```python
def calculate_fdr(scores, is_decoy, score_threshold):
    above_threshold = scores >= score_threshold
    n_target = ((~is_decoy) & above_threshold).sum()
    n_decoy = (is_decoy & above_threshold).sum()
    fdr = n_decoy / n_target if n_target > 0 else 1.0
    return fdr

def find_score_at_fdr(scores, is_decoy, target_fdr=0.01):
    sorted_scores = np.sort(scores)[::-1]
    for threshold in sorted_scores:
        fdr = calculate_fdr(scores, is_decoy, threshold)
        if fdr <= target_fdr:
            return threshold
    return sorted_scores[-1]
```

## R: Search Result Processing

```r
library(MSnbase)

# Read mzIdentML results
psms <- readMzIdData('results.mzid')

# Filter to 1% FDR
psms_filtered <- psms[psms$qvalue <= 0.01, ]

# Unique peptides per protein
peptide_counts <- table(psms_filtered$accession)
```

## Spectral Library Search

```python
from pyopenms import SpectraSTSearchAlgorithm, MSExperiment

# Load spectral library
library = MSExperiment()
MzMLFile().load('spectral_library.mzML', library)

# Match query spectra against library
# Returns similarity scores and library matches
```

## Related Skills

- data-import - Load raw MS data before identification
- protein-inference - Group peptides to proteins
- ptm-analysis - Identify modified peptides
