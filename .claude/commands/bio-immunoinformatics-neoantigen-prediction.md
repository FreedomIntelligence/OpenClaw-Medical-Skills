# bio-immunoinformatics-neoantigen-prediction

> Identify tumor neoantigens from somatic mutations using pVACtools for personalized cancer immunotherapy. Predict mutant peptides that bind patient HLA and may elicit T-cell responses. Use when identifying vaccine targets or checkpoint inhibitor response biomarkers from tumor sequencing data.

## Version Compatibility

Reference examples tested with: Ensembl VEP 111+, MHCflurry 2.1+, pVACtools 4.1+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Neoantigen Prediction

**"Identify neoantigens from my tumor mutations"** → Predict mutant peptides from somatic variants that bind patient HLA alleles and may elicit T-cell responses for personalized cancer immunotherapy.
- CLI: `pvacseq run` with VEP-annotated VCF and patient HLA types (pVACtools)

## pVACtools Pipeline (Ensembl VEP 111+)

**Goal:** Install pVACtools and its IEDB prediction engine dependencies.

**Approach:** Install via pip (optionally in a dedicated conda environment) and download IEDB tools for binding prediction.

```bash
# Install pVACtools
pip install pvactools

# Or use conda for dependencies
conda create -n pvactools python=3.8
conda activate pvactools
pip install pvactools

# Download IEDB tools
pvactools download_iedb_tools
```

## pVACseq Workflow (Ensembl VEP 111+)

**Goal:** Run the full pVACseq neoantigen prediction pipeline on a VEP-annotated VCF.

**Approach:** Provide annotated VCF with patient HLA alleles and select binding prediction algorithms; pVACseq generates mutant peptides and predicts MHC binding.

```bash
# Run pVACseq on annotated VCF
pvacseq run \
    annotated.vcf \
    sample_name \
    "HLA-A*02:01,HLA-A*24:02,HLA-B*07:02,HLA-B*44:02" \
    MHCflurry MHCnuggetsI \
    output_dir \
    -e1 8,9,10,11 \
    --iedb-install-directory /path/to/iedb

# Key parameters:
# -e1: Epitope lengths for MHC-I (8-11)
# -e2: Epitope lengths for MHC-II (15)
# --binding-threshold: IC50 cutoff (default 500)
# --percentile-threshold: Alternative cutoff
```

## VCF Annotation Requirements (Ensembl VEP 111+)

**Goal:** Annotate somatic VCF with transcript consequences and amino acid changes required by pVACseq.

**Approach:** Run Ensembl VEP with Downstream and Wildtype plugins to produce a VCF containing protein-level mutation annotations.

```bash
# pVACseq requires VEP-annotated VCF
# Must include transcript and amino acid changes

# Run VEP first
vep -i somatic.vcf -o annotated.vcf \
    --cache --offline \
    --format vcf --vcf \
    --plugin Downstream \
    --plugin Wildtype \
    --terms SO \
    --symbol
```

## Parse pVACseq Results

**Goal:** Parse pVACseq output and calculate the differential agretopicity index (DAI) for candidate neoantigens.

**Approach:** Load TSV results, filter by binding threshold, and compute WT/MT binding ratio to identify mutations that create new epitopes.

```python
import pandas as pd

def parse_pvacseq_results(results_file):
    '''Parse pVACseq output

    Key columns:
    - Mutation: Gene and amino acid change
    - HLA Allele: Patient HLA presenting this peptide
    - MT Epitope Seq: Mutant peptide sequence
    - WT Epitope Seq: Wild-type peptide sequence
    - Median MT Score: Binding affinity (nM)
    - Median WT Score: WT binding (for agretopicity)
    - Tumor DNA VAF: Variant allele frequency
    - Gene Expression: If RNA-seq available
    '''
    df = pd.read_csv(results_file, sep='\t')

    # Filter by binding threshold
    strong_binders = df[df['Median MT Score'] < 500]

    return strong_binders


def calculate_agretopicity(df):
    '''Calculate agretopicity (DAI) score

    Agretopicity = ratio of WT to MT binding
    Higher agretopicity means MT binds better than WT
    indicating mutation creates new epitope

    DAI (Differential Agretopicity Index):
    - >1: Mutant binds better (favorable)
    - ~1: Similar binding (less likely immunogenic)
    - <1: WT binds better (unfavorable)
    '''
    df = df.copy()
    df['agretopicity'] = df['Median WT Score'] / df['Median MT Score']

    # High agretopicity = mutation improves binding
    df['dai_favorable'] = df['agretopicity'] > 1

    return df
```

## Prioritize Neoantigens (Ensembl VEP 111+)

**Goal:** Rank neoantigen candidates for vaccine design by combining binding, clonality, and expression evidence.

**Approach:** Apply sequential filters (binding affinity, VAF, expression) and compute a composite priority score weighting inverse IC50, VAF, and agretopicity.

```python
def prioritize_neoantigens(df, vaf_threshold=0.1, expression_threshold=1.0):
    '''Prioritize neoantigens for vaccine design

    Criteria for good neoantigen candidates:
    1. Strong MHC binding (IC50 < 500nM, ideally < 50nM)
    2. High agretopicity (MT binds better than WT)
    3. High tumor VAF (clonal, present in most tumor cells)
    4. Expressed in tumor (if RNA-seq available)
    5. Not in tolerogenic region (self-similarity check)

    Typical pipeline returns 10-50 candidates per patient
    '''
    candidates = df.copy()

    # Filter by binding
    candidates = candidates[candidates['Median MT Score'] < 500]

    # Filter by VAF (clonal mutations preferred)
    if 'Tumor DNA VAF' in candidates.columns:
        candidates = candidates[candidates['Tumor DNA VAF'] >= vaf_threshold]

    # Filter by expression
    if 'Gene Expression' in candidates.columns:
        candidates = candidates[candidates['Gene Expression'] >= expression_threshold]

    # Calculate priority score
    # Lower binding affinity = better
    # Higher VAF = better
    # Higher agretopicity = better
    candidates['priority_score'] = (
        (1 / candidates['Median MT Score']) *
        candidates.get('Tumor DNA VAF', 1) *
        candidates.get('agretopicity', 1)
    )

    return candidates.sort_values('priority_score', ascending=False)
```

## Alternative: Manual Neoantigen Pipeline (Ensembl VEP 111+)

**Goal:** Predict neoantigens without pVACtools by directly extracting mutant peptides from an annotated VCF and predicting MHC binding.

**Approach:** Parse VEP annotations from VCF via cyvcf2, generate mutant peptides around each coding mutation, and predict binding with MHCflurry.

```python
def manual_neoantigen_pipeline(vcf_file, hla_alleles, reference_fasta):
    '''Simplified neoantigen prediction without pVACtools

    Steps:
    1. Extract coding mutations from VCF
    2. Generate mutant protein sequences
    3. Extract peptides around mutation
    4. Predict MHC binding
    '''
    from cyvcf2 import VCF
    from mhcflurry import Class1PresentationPredictor

    vcf = VCF(vcf_file)
    predictor = Class1PresentationPredictor.load()

    neoantigens = []

    for variant in vcf:
        # Get amino acid change from VEP annotation
        if 'CSQ' not in variant.INFO:
            continue

        # Parse consequence and extract mutant peptides
        # ... (implementation depends on annotation format)

        # For each mutant peptide, predict binding
        for peptide in mutant_peptides:
            for allele in hla_alleles:
                pred = predictor.predict(peptides=[peptide], alleles=[allele])
                if pred['mhcflurry_affinity'].values[0] < 500:
                    neoantigens.append({
                        'variant': f'{variant.CHROM}:{variant.POS}',
                        'peptide': peptide,
                        'allele': allele,
                        'affinity': pred['mhcflurry_affinity'].values[0]
                    })

    return neoantigens
```

## Neoantigen Quality Metrics (Ensembl VEP 111+)

**Goal:** Assess neoantigen quality across multiple dimensions and produce a composite confidence score.

**Approach:** Normalize binding affinity, agretopicity, clonality, and expression to 0-1 scales and combine with domain-informed weights.

```python
def assess_neoantigen_quality(neoantigen):
    '''Assess multiple quality metrics for neoantigen

    Returns composite quality score considering:
    - Binding affinity
    - Agretopicity
    - Clonality (VAF)
    - Expression
    - Self-similarity
    '''
    scores = {}

    # Binding (0-1, lower IC50 = higher score)
    ic50 = neoantigen.get('Median MT Score', 500)
    scores['binding'] = 1 - min(ic50 / 5000, 1)

    # Agretopicity (0-1)
    dai = neoantigen.get('agretopicity', 1)
    scores['agretopicity'] = min(dai / 10, 1)

    # Clonality (0-1)
    vaf = neoantigen.get('Tumor DNA VAF', 0.5)
    scores['clonality'] = vaf

    # Expression (0-1, log scale)
    import math
    expr = neoantigen.get('Gene Expression', 1)
    scores['expression'] = min(math.log10(expr + 1) / 3, 1)

    # Composite score
    weights = {'binding': 0.3, 'agretopicity': 0.3, 'clonality': 0.2, 'expression': 0.2}
    composite = sum(scores[k] * weights[k] for k in weights)

    return composite, scores
```

## Related Skills

- immunoinformatics/mhc-binding-prediction - MHC binding details
- immunoinformatics/immunogenicity-scoring - Prioritization
- variant-calling/variant-calling - Input somatic mutations
