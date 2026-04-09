# bio-proteomics-protein-inference

> Protein grouping and inference from peptide identifications. Use when resolving protein ambiguity from shared peptides. Handles protein groups and protein-level FDR control using parsimony and probabilistic approaches.

## Version Compatibility

Reference examples tested with: pyOpenMS 3.1+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion("<pkg>")` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Protein Inference

**"Resolve protein groups from my peptide identifications"** → Group peptide-spectrum matches into protein groups, resolving shared-peptide ambiguity using parsimony or probabilistic methods, then apply protein-level FDR.
- Python: `pyopenms.ProteinInference()` for parsimony-based grouping
- R: Bioconductor protein inference workflows

## The Protein Inference Problem

Peptides can map to multiple proteins (shared peptides), making protein identification ambiguous.

```python
# Example: Peptide mapping
peptide_to_proteins = {
    'PEPTIDEK': ['P12345', 'P67890'],      # Shared between paralogs
    'UNIQUER': ['P12345'],                  # Unique to P12345
    'ANOTHERONE': ['P12345'],               # Unique to P12345
    'SHAREDK': ['P67890', 'P11111'],        # Shared
}

# P12345 has 2 unique peptides -> confident identification
# P67890 has 0 unique peptides -> subset, may be grouped with P12345
```

## Parsimony Principle

**Goal:** Resolve protein identification ambiguity from shared peptides by finding the minimal protein set explaining all observed peptides.

**Approach:** Build a peptide-to-protein mapping, then greedily select proteins that cover the most unassigned peptides until all peptides are accounted for, producing a minimal explanatory protein list.

```python
def apply_parsimony(peptide_protein_map):
    '''Find minimal set of proteins explaining all peptides'''
    proteins = set()
    for prots in peptide_protein_map.values():
        proteins.update(prots)

    protein_peptides = {p: set() for p in proteins}
    for pep, prots in peptide_protein_map.items():
        for p in prots:
            protein_peptides[p].add(pep)

    covered_peptides = set()
    selected_proteins = []

    # Greedy: select protein covering most uncovered peptides
    while covered_peptides != set(peptide_protein_map.keys()):
        best_protein = max(protein_peptides.keys(),
                          key=lambda p: len(protein_peptides[p] - covered_peptides))
        new_coverage = protein_peptides[best_protein] - covered_peptides
        if not new_coverage:
            break
        selected_proteins.append(best_protein)
        covered_peptides.update(new_coverage)

    return selected_proteins
```

## Protein Groups

```python
def create_protein_groups(peptide_protein_map):
    '''Group proteins with identical peptide evidence'''
    protein_peptides = {}
    for pep, prots in peptide_protein_map.items():
        for p in prots:
            protein_peptides.setdefault(p, set()).add(pep)

    # Group by peptide set
    peptide_set_to_proteins = {}
    for protein, peptides in protein_peptides.items():
        key = frozenset(peptides)
        peptide_set_to_proteins.setdefault(key, []).append(protein)

    groups = []
    for peptides, proteins in peptide_set_to_proteins.items():
        groups.append({
            'proteins': proteins,
            'peptides': list(peptides),
            'n_peptides': len(peptides),
            'is_group': len(proteins) > 1
        })

    return groups
```

## pyOpenMS Protein Inference

```python
from pyopenms import ProteinIdentification, PeptideIdentification
from pyopenms import BasicProteinInferenceAlgorithm

# Load identifications
protein_ids = []
peptide_ids = []
IdXMLFile().load('search_results.idXML', protein_ids, peptide_ids)

# Run inference
inference = BasicProteinInferenceAlgorithm()
inference.run(peptide_ids, protein_ids)

# Results include protein groups and scores
for protein_id in protein_ids:
    for hit in protein_id.getHits():
        accession = hit.getAccession()
        score = hit.getScore()
```

## R: Protein Inference with ProteinInference

```r
library(ProteinInference)

# From peptide-protein mapping
protein_groups <- infer_proteins(
    peptides = psm_data$peptide,
    proteins = psm_data$protein,
    method = 'parsimony'
)

# Count unique peptides per group
protein_groups$n_unique <- sapply(protein_groups$peptides, function(p) {
    sum(sapply(p, function(pep) length(peptide_to_protein[[pep]]) == 1))
})
```

## Protein-Level FDR

```python
def protein_fdr(protein_groups, target_fdr=0.01):
    '''Calculate protein-level FDR from group scores'''
    sorted_groups = sorted(protein_groups, key=lambda x: x['score'], reverse=True)

    target_count = 0
    decoy_count = 0

    for group in sorted_groups:
        if group['is_decoy']:
            decoy_count += 1
        else:
            target_count += 1
        group['fdr'] = decoy_count / target_count if target_count > 0 else 1.0

    # Q-value
    min_fdr = 1.0
    for group in reversed(sorted_groups):
        min_fdr = min(min_fdr, group['fdr'])
        group['qvalue'] = min_fdr

    return [g for g in sorted_groups if g['qvalue'] <= target_fdr and not g['is_decoy']]
```

## Related Skills

- peptide-identification - Input for protein inference
- quantification - Quantify inferred proteins
- database-access/uniprot-access - Protein annotations
