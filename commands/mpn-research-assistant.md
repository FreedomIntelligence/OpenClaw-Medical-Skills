# mpn-research-assistant

> Myeloproliferative neoplasm (MPN) research expertise including JAK2/CALR/MPL mutations, myelofibrosis, polycythemia vera, essential thrombocythemia. Use for MPN literature search, driver mutation analysis, PPM1D pathway analysis, fibrosis markers, megakaryocyte biology, clinical trial data interpretation, and translational research.

# MPN Research Assistant

## Disease Classification

### WHO 2022 Classification
- **Polycythemia Vera (PV)**: JAK2V617F (95%), JAK2 exon 12 (3%)
- **Essential Thrombocythemia (ET)**: JAK2V617F (55%), CALR (25%), MPL (5%)
- **Primary Myelofibrosis (PMF)**: JAK2V617F (55%), CALR (25%), MPL (8%)
- **Pre-PMF**: Early fibrotic stage, better prognosis
- **Overt PMF**: Grade 2-3 fibrosis, splenomegaly

### Driver Mutations

| Mutation | Gene Location | Mechanism | VAF Significance |
|----------|--------------|-----------|------------------|
| JAK2V617F | 9p24.1 | Constitutive JAK-STAT activation | >50% → poor prognosis |
| CALR (type 1) | 19p13.2 | 52bp deletion, MPL activation | Better prognosis |
| CALR (type 2) | 19p13.2 | 5bp insertion, MPL activation | Intermediate |
| MPL W515L/K | 1p34.2 | TPO-independent signaling | Thrombocytosis |

### High Molecular Risk (HMR) Mutations
- ASXL1, EZH2, SRSF2, IDH1/2, U2AF1
- ≥2 HMR mutations = very high risk

## PPM1D Pathway Analysis

### Expression Patterns
- 83.9-fold overexpression vs normal donors (p=0.0002)
- JAK2V617F+ > CALR+ expression (43.4x vs 13.4x, p=0.01)
- Mutation frequency: 1.9% (8th most common in MPNs)

### Therapeutic Targets
```python
ppm1d_targets = {
    'PPM1D inhibitors': ['GSK2830371', 'SL-176'],
    'MDM2 inhibitors': ['navtemadlin (KRT-232)', 'idasanutlin'],
    'Combination': ['PPM1D + MDM2 (synergistic)'],
}

# p53 pathway restoration
mechanism = """
PPM1D inhibition → ↑p53 phosphorylation → 
↑p53 stabilization → ↑DNA damage response → 
↑apoptosis in mutant clones
"""
```

### Clinical Trial Data (BOREAS)
- Navtemadlin: 15% SVR35, 24% TSS50
- CD34+ reduction: 68-76% at 24-36 weeks
- VAF reduction: 21% achieved ≥50% decrease
- Fibrosis improvement: 45% by one grade

## Megakaryocyte Subtypes in MPNs

```python
mk_subtypes = {
    'Endomitotic MKs': {
        'markers': ['ITGA2B', 'GP1BA', 'PF4', 'TUBB1'],
        'function': 'Polyploidization',
        'mpn_change': 'Dysregulated endomitosis'
    },
    'Platelet-Generating MKs': {
        'markers': ['VWF', 'F2R', 'GP9', 'SELP'],
        'function': 'Proplatelet formation',
        'mpn_change': 'Abnormal platelet production'
    },
    'HSC Niche-Supporting MKs': {
        'markers': ['THPO', 'IGF1', 'CXCL12', 'ANGPT1'],
        'function': 'HSC maintenance',
        'mpn_change': 'Disrupted niche signaling'
    },
    'Inflammatory MKs': {
        'markers': ['S100A8', 'S100A9', 'CHI3L1', 'CXCL8'],
        'function': 'Inflammation',
        'mpn_change': 'Expanded in MF'
    }
}
```

## Fibrosis Markers

### Psaila 2020 Fibrosis Gene Signature
```python
fibrosis_genes = [
    'TGFB1', 'IL12A', 'IL1B', 'RAB37', 'TIMP1', 'APIP', 'PF4V1', 'VEGFA',
    'FBLN2', 'SFRP1', 'COL6A2', 'COL4A2', 'COL5A1', 'PDGFRB', 'LOXL2', 'RUNX2'
]

# ECM remodeling
ecm_markers = ['COL1A1', 'COL3A1', 'FN1', 'LAMA1', 'LAMB1']

# Profibrotic cytokines
cytokines = ['TGFB1', 'PDGF', 'VEGFA', 'IL1B', 'IL6', 'TNF']
```

## Prognostic Scoring Systems

### MIPSS70+ v2.0 (Myelofibrosis)

| Variable | Points |
|----------|--------|
| Hemoglobin <10 g/dL | 2 |
| Blasts ≥2% | 1 |
| Constitutional symptoms | 2 |
| Absence of CALR type-1 | 2 |
| HMR mutations | 2 each |
| Unfavorable karyotype | 3 |

### Risk Categories
- Very Low: 0-1 points (10yr OS: 92%)
- Low: 2-4 points
- Intermediate: 5-8 points
- High: 9-11 points
- Very High: ≥12 points

## Data Integration Template

```python
def create_mpn_patient_matrix(clinical_df, mutations_df, 
                               cytokines_df, flow_df, degs_df):
    """Integrate multi-modal MPN patient data."""
    
    # Merge clinical
    matrix = clinical_df.copy()
    
    # Add mutation status
    driver_muts = ['JAK2', 'CALR', 'MPL']
    hmr_muts = ['ASXL1', 'EZH2', 'SRSF2', 'IDH1', 'IDH2']
    
    for mut in driver_muts + hmr_muts:
        if mut in mutations_df.columns:
            matrix[f'{mut}_status'] = mutations_df[mut]
    
    # Calculate HMR count
    matrix['HMR_count'] = matrix[[f'{m}_status' for m in hmr_muts 
                                   if f'{m}_status' in matrix.columns]].sum(axis=1)
    
    # Add cytokine data
    for cyto in ['TGFB1', 'IL6', 'IL8']:
        if cyto in cytokines_df.columns:
            matrix[f'{cyto}_level'] = cytokines_df[cyto]
    
    # Add flow cytometry
    matrix['CD34_percent'] = flow_df['CD34_positive_percent']
    
    return matrix
```

## Key References

```python
key_papers = {
    'Williams_2022': 'Blood: Phylogenetic reconstruction of MPN evolution',
    'Psaila_2020': 'Nature Medicine: Single-cell profiling of MF megakaryocytes',
    'Mascarenhas_2022': 'Blood Advances: Idasanutlin in PV',
    'BOREAS_2024': 'Phase III navtemadlin in MF',
    'Marcellino_iPSC': 'PPM1D iPSC modeling in MPNs',
    'Kanagal-Shamanna': 'Mod Pathol: i(17q) in MDS/MPN'
}
```

## PubMed Search Templates

```python
mpn_search_queries = {
    'ppm1d_mpn': '"PPM1D"[Title/Abstract] AND ("myeloproliferative"[Title/Abstract] OR "myelofibrosis"[Title/Abstract])',
    'single_cell_mpn': '"single-cell"[Title/Abstract] AND "myeloproliferative neoplasm"[Title/Abstract]',
    'jak2_calr': '(JAK2V617F OR "CALR mutation") AND myeloproliferative',
    'fibrosis_mk': 'megakaryocyte[Title/Abstract] AND fibrosis[Title/Abstract] AND myelofibrosis'
}
```

See `references/mpn_clinical_trials.md` for ongoing trials.
See `references/mpn_mutations_database.md` for complete mutation catalog.
