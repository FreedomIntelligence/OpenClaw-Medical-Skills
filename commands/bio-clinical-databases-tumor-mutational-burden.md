# bio-clinical-databases-tumor-mutational-burden

> Calculate tumor mutational burden from panel or WES data with proper normalization and clinical thresholds. Use when assessing immunotherapy eligibility or characterizing tumor immunogenicity.

## Version Compatibility

Reference examples tested with: Ensembl VEP 111+, SnpEff 5.2+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Tumor Mutational Burden

**"Calculate TMB from my tumor sequencing data"** → Compute tumor mutational burden as nonsynonymous coding mutations per megabase with proper panel normalization for immunotherapy eligibility assessment.
- Python: `cyvcf2` for VCF parsing + variant counting per panel region

## TMB Calculation from VCF (Ensembl VEP 111+)

**Goal:** Calculate tumor mutational burden as nonsynonymous coding mutations per megabase from a somatic VCF.

**Approach:** Iterate through VCF variants, filter for coding nonsynonymous consequences via VEP/SnpEff annotations, and divide count by panel size.

```python
from cyvcf2 import VCF

def calculate_tmb(vcf_path, panel_size_mb):
    '''Calculate TMB (mutations per megabase)

    Args:
        vcf_path: Path to somatic VCF
        panel_size_mb: Capture region size in megabases

    Returns:
        TMB value (mutations/Mb)
    '''
    vcf = VCF(vcf_path)
    mutation_count = 0

    for variant in vcf:
        # Count nonsynonymous coding mutations
        # Adjust filters based on VCF annotation format
        if is_coding_nonsynonymous(variant):
            mutation_count += 1

    tmb = mutation_count / panel_size_mb
    return tmb

def is_coding_nonsynonymous(variant):
    '''Check if variant is coding nonsynonymous

    Adjust logic based on your VCF annotation tool:
    - VEP: CSQ field
    - SnpEff: ANN field
    - Funcotator: FUNCOTATION field
    '''
    # Example for VEP annotation
    csq = variant.INFO.get('CSQ', '')
    if not csq:
        return False

    # Check consequence types
    nonsynonymous = ['missense_variant', 'nonsense', 'frameshift',
                     'inframe_insertion', 'inframe_deletion', 'stop_gained',
                     'stop_lost', 'start_lost']

    for transcript in csq.split(','):
        fields = transcript.split('|')
        consequence = fields[1] if len(fields) > 1 else ''
        if any(ns in consequence for ns in nonsynonymous):
            return True
    return False
```

## Panel-Specific TMB (Ensembl VEP 111+)

**Goal:** Calculate TMB normalized to known gene panel capture region sizes.

**Approach:** Look up the panel's megabase coverage from a reference table and pass to the TMB calculator.

```python
# Common panel sizes (in megabases)
# Check your specific panel's capture region size
PANEL_SIZES_MB = {
    'FoundationOne CDx': 0.8,
    'MSK-IMPACT': 1.14,
    'TruSight Oncology 500': 1.94,
    'Oncomine Comprehensive': 1.5,
    'WES (exome)': 30.0,  # Approximate coding region
    'WGS': 3000.0,        # Approximate
}

def calculate_tmb_panel(vcf_path, panel_name):
    '''Calculate TMB for known panel'''
    if panel_name not in PANEL_SIZES_MB:
        raise ValueError(f'Unknown panel: {panel_name}')
    return calculate_tmb(vcf_path, PANEL_SIZES_MB[panel_name])
```

## TMB with Variant Filtering (Ensembl VEP 111+)

**Goal:** Calculate TMB with quality and germline filters to reduce false positives.

**Approach:** Apply VAF, depth, and gnomAD population frequency filters before counting coding nonsynonymous variants.

```python
def calculate_tmb_filtered(vcf_path, panel_size_mb, min_vaf=0.05, min_depth=100):
    '''Calculate TMB with quality filters

    Args:
        vcf_path: Path to somatic VCF
        panel_size_mb: Panel size in Mb
        min_vaf: Minimum variant allele frequency (default 5%)
        min_depth: Minimum read depth (default 100)

    Filters:
    - VAF >= 5%: Reduce false positives from sequencing errors
    - Depth >= 100: Ensure reliable variant calls
    - Exclude known polymorphisms (gnomAD AF > 1%)
    - Include only coding nonsynonymous
    '''
    vcf = VCF(vcf_path)
    mutation_count = 0

    for variant in vcf:
        # Quality filters
        depth = variant.INFO.get('DP', 0)
        vaf = get_vaf(variant)

        if depth < min_depth:
            continue
        if vaf < min_vaf:
            continue

        # Exclude germline polymorphisms
        gnomad_af = variant.INFO.get('gnomAD_AF', 0)
        if gnomad_af > 0.01:
            continue

        # Count coding nonsynonymous
        if is_coding_nonsynonymous(variant):
            mutation_count += 1

    return mutation_count / panel_size_mb

def get_vaf(variant):
    '''Extract variant allele frequency from variant'''
    # Format depends on caller (e.g., Mutect2, Strelka)
    # Mutect2 format: AD field in genotype
    try:
        ad = variant.format('AD')[0]  # First sample
        if sum(ad) > 0:
            return ad[1] / sum(ad)
    except:
        pass
    return 0
```

## Clinical TMB Thresholds (Ensembl VEP 111+)

**Goal:** Classify a TMB value as TMB-High or TMB-Low based on clinical cutoffs.

**Approach:** Compare the TMB value against FDA-approved or study-specific thresholds (10, 16, or 20 mut/Mb).

```python
def classify_tmb(tmb_value, threshold='FDA'):
    '''Classify TMB as high or low

    Clinical thresholds:
    - FDA (pembrolizumab): 10 mut/Mb
    - ESMO: 10 mut/Mb
    - Some studies use 16, 20 mut/Mb for specific cancers

    Note: Panel-specific thresholds may differ
    '''
    thresholds = {
        'FDA': 10,
        'conservative': 16,
        'strict': 20
    }

    cutoff = thresholds.get(threshold, 10)

    if tmb_value >= cutoff:
        return 'TMB-High'
    else:
        return 'TMB-Low'

# Example
tmb = 12.5
status = classify_tmb(tmb)
print(f'TMB: {tmb} mut/Mb -> {status}')
```

## TMB by Variant Type (Ensembl VEP 111+)

**Goal:** Break down TMB by mutation type (missense, nonsense, frameshift, etc.) for detailed characterization.

**Approach:** Classify each variant by consequence type, count per category, and compute TMB from nonsynonymous subtotal.

```python
def detailed_tmb_analysis(vcf_path, panel_size_mb):
    '''Calculate TMB broken down by variant type'''
    vcf = VCF(vcf_path)

    counts = {
        'missense': 0,
        'nonsense': 0,
        'frameshift': 0,
        'inframe_indel': 0,
        'splice': 0,
        'synonymous': 0,
        'other': 0
    }

    for variant in vcf:
        vtype = classify_variant_type(variant)
        counts[vtype] = counts.get(vtype, 0) + 1

    # TMB typically excludes synonymous
    nonsynonymous_count = sum(v for k, v in counts.items()
                               if k != 'synonymous' and k != 'other')

    results = {
        'counts': counts,
        'total_nonsynonymous': nonsynonymous_count,
        'tmb': nonsynonymous_count / panel_size_mb,
        'panel_size_mb': panel_size_mb
    }
    return results
```

## TMB vs MSI Comparison (Ensembl VEP 111+)

**Goal:** Assess concordance between TMB status and microsatellite instability for immunotherapy biomarker evaluation.

**Approach:** Cross-tabulate TMB-High/Low with MSI-H/MSS to identify concordant and discordant cases.

```python
def tmb_msi_concordance(tmb_value, msi_status):
    '''Compare TMB with MSI status

    MSI-H tumors typically have high TMB (>10-20 mut/Mb)
    TMB-H and MSI-H are correlated but not identical:
    - ~80% MSI-H are TMB-H
    - Many TMB-H are MSS (especially smoking-related)

    Both predict immunotherapy response
    '''
    tmb_high = tmb_value >= 10

    if msi_status == 'MSI-H' and tmb_high:
        return 'Concordant TMB-H/MSI-H'
    elif msi_status == 'MSI-H' and not tmb_high:
        return 'Discordant MSI-H/TMB-L (uncommon)'
    elif msi_status == 'MSS' and tmb_high:
        return 'TMB-H/MSS (e.g., smoking-related)'
    else:
        return 'TMB-L/MSS'
```

## Batch TMB Calculation

**Goal:** Calculate TMB for an entire cohort of samples and export results with clinical classification.

**Approach:** Iterate over VCF files in a directory, compute filtered TMB for each, and collect into a summary DataFrame.

```python
import pandas as pd
from pathlib import Path

def batch_tmb(vcf_dir, panel_size_mb, output_file):
    '''Calculate TMB for multiple samples'''
    results = []

    for vcf_path in Path(vcf_dir).glob('*.vcf.gz'):
        sample_id = vcf_path.stem.replace('.vcf', '')
        tmb = calculate_tmb_filtered(str(vcf_path), panel_size_mb)
        status = classify_tmb(tmb)

        results.append({
            'sample': sample_id,
            'tmb': round(tmb, 2),
            'status': status
        })

    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    return df
```

## Related Skills

- variant-calling/somatic-variant-calling - Input variants
- variant-calling/clinical-interpretation - ACMG/AMP classification
- variant-calling/variant-annotation - VEP/SnpEff annotation
