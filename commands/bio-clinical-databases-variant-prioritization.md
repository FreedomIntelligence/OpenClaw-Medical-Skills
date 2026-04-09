# bio-clinical-databases-variant-prioritization

> Filter and prioritize variants by pathogenicity, population frequency, and clinical evidence for rare disease analysis. Use when identifying candidate disease-causing variants from exome or genome sequencing.

## Version Compatibility

Reference examples tested with: pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Variant Prioritization

**"Prioritize candidate disease variants from my exome data"** → Filter and rank variants by pathogenicity scores, population frequency, inheritance pattern, and clinical evidence to identify candidate disease-causing mutations.
- Python: `pandas` for multi-criteria filtering with ACMG/AMP classification logic

## Basic Filtering Pipeline

**Goal:** Filter variants to retain rare, potentially pathogenic candidates for rare disease analysis.

**Approach:** Apply gnomAD population frequency and ClinVar significance filters, retaining pathogenic, VUS, and unannotated variants.

```python
import pandas as pd

def prioritize_variants(df, gnomad_af_col='gnomad_af', clinvar_col='clinvar_sig'):
    '''Basic variant prioritization pipeline

    Filters:
    1. Rare in population (gnomAD AF < 0.01)
    2. Pathogenic/likely pathogenic in ClinVar OR VUS with low AF
    '''
    # Filter rare variants (ACMG PM2: AF < 1%)
    rare = df[df[gnomad_af_col].isna() | (df[gnomad_af_col] < 0.01)]

    # Prioritize by ClinVar
    pathogenic_terms = ['Pathogenic', 'Likely_pathogenic', 'Pathogenic/Likely_pathogenic']
    prioritized = rare[
        rare[clinvar_col].isin(pathogenic_terms) |
        rare[clinvar_col].isna() |  # No ClinVar = needs review
        (rare[clinvar_col] == 'Uncertain_significance')
    ]

    return prioritized
```

## ACMG-Style Filtering

**Goal:** Score variants using ACMG-style evidence criteria for pathogenicity assessment.

**Approach:** Evaluate PM2 (population rarity) and PVS1 (loss-of-function) evidence, then compute a weighted priority score.

```python
def acmg_filter(df):
    '''Apply ACMG-style filtering criteria

    Strong pathogenic evidence:
    - PVS1: Null variant in gene where LOF is disease mechanism
    - PS1: Same amino acid change as established pathogenic
    - PS3: Functional studies support damaging effect

    Moderate evidence:
    - PM1: Located in mutational hot spot
    - PM2: Absent/rare in population databases (AF < 0.01)
    - PM5: Novel missense at position of known pathogenic
    '''
    # PM2: Rare in gnomAD
    df['pm2'] = df['gnomad_af'].isna() | (df['gnomad_af'] < 0.01)

    # PVS1: Loss of function variants
    lof_consequences = ['frameshift', 'stop_gained', 'splice_donor', 'splice_acceptor']
    df['pvs1'] = df['consequence'].isin(lof_consequences)

    # Score based on evidence
    df['priority_score'] = df['pm2'].astype(int) + df['pvs1'].astype(int) * 2

    return df.sort_values('priority_score', ascending=False)
```

## Multi-Database Prioritization

**Goal:** Prioritize variants using aggregated evidence from ClinVar, gnomAD, CADD, and REVEL in a single query.

**Approach:** Fetch annotations via myvariant.info, then compute a composite priority score weighting clinical, population, and computational evidence.

```python
import myvariant

def annotate_and_prioritize(variants):
    '''Annotate variants and apply prioritization'''
    mv = myvariant.MyVariantInfo()

    # Fetch annotations
    results = mv.getvariants(
        variants,
        fields=[
            'clinvar.clinical_significance',
            'clinvar.review_status',
            'gnomad_exome.af.af',
            'cadd.phred',
            'dbnsfp.revel.score'
        ]
    )

    records = []
    for r in results:
        clinvar = r.get('clinvar', {})
        gnomad = r.get('gnomad_exome', {})
        cadd = r.get('cadd', {})
        revel = r.get('dbnsfp', {}).get('revel', {})

        records.append({
            'variant': r.get('query'),
            'clinvar_sig': clinvar.get('clinical_significance'),
            'clinvar_stars': clinvar.get('review_status'),
            'gnomad_af': gnomad.get('af', {}).get('af'),
            'cadd_phred': cadd.get('phred'),
            'revel_score': revel.get('score') if isinstance(revel, dict) else None
        })

    df = pd.DataFrame(records)
    return prioritize_with_scores(df)

def prioritize_with_scores(df):
    '''Apply multi-evidence prioritization'''
    # Computational predictions
    # CADD phred > 20 suggests deleteriousness
    # REVEL > 0.5 suggests pathogenicity
    df['cadd_deleterious'] = df['cadd_phred'].fillna(0) > 20
    df['revel_pathogenic'] = df['revel_score'].fillna(0) > 0.5

    # Rare in population
    df['is_rare'] = df['gnomad_af'].isna() | (df['gnomad_af'] < 0.01)

    # ClinVar pathogenic
    pathogenic = ['Pathogenic', 'Likely_pathogenic']
    df['clinvar_pathogenic'] = df['clinvar_sig'].apply(
        lambda x: any(p in str(x) for p in pathogenic) if pd.notna(x) else False
    )

    # Priority score
    df['priority'] = (
        df['clinvar_pathogenic'].astype(int) * 10 +
        df['is_rare'].astype(int) * 3 +
        df['cadd_deleterious'].astype(int) * 2 +
        df['revel_pathogenic'].astype(int) * 2
    )

    return df.sort_values('priority', ascending=False)
```

## Inheritance-Based Filtering

**Goal:** Filter variants by expected inheritance pattern (autosomal dominant, recessive, or X-linked).

**Approach:** Select heterozygous ultra-rare variants for AD, or homozygous plus compound heterozygous candidates for AR.

```python
def filter_by_inheritance(df, inheritance='AD'):
    '''Filter variants by inheritance pattern

    AD: Autosomal dominant - heterozygous variants
    AR: Autosomal recessive - homozygous or compound het
    XL: X-linked
    '''
    if inheritance == 'AD':
        # Dominant: heterozygous, rare
        return df[(df['zygosity'] == 'HET') & (df['gnomad_af'] < 0.0001)]

    elif inheritance == 'AR':
        # Recessive: homozygous or two variants in same gene
        hom = df[df['zygosity'] == 'HOM']

        # Find genes with 2+ het variants (compound het candidates)
        het = df[df['zygosity'] == 'HET']
        compound_genes = het['gene'].value_counts()
        compound_genes = compound_genes[compound_genes >= 2].index
        compound_het = het[het['gene'].isin(compound_genes)]

        return pd.concat([hom, compound_het])

    return df
```

## Output Priority Tiers

**Goal:** Assign clinical interpretation tiers (1-4) for structured reporting of prioritized variants.

**Approach:** Combine ClinVar pathogenicity, population rarity, and computational predictions to classify into strong, potential, uncertain, or benign tiers.

```python
def assign_tiers(df):
    '''Assign clinical interpretation tiers

    Tier 1: Strong pathogenic evidence
    Tier 2: Potential pathogenic
    Tier 3: Uncertain significance
    Tier 4: Likely benign
    '''
    def get_tier(row):
        if row['clinvar_pathogenic'] and row['is_rare']:
            return 1
        elif row['is_rare'] and (row['cadd_deleterious'] or row['revel_pathogenic']):
            return 2
        elif row['is_rare']:
            return 3
        else:
            return 4

    df['tier'] = df.apply(get_tier, axis=1)
    return df
```

## Related Skills

- clinvar-lookup - ClinVar pathogenicity queries
- gnomad-frequencies - Population frequency filtering
- variant-calling/clinical-interpretation - ACMG classification
- variant-calling/filtering-best-practices - Quality filtering
