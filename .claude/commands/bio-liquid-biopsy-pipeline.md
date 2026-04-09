# bio-liquid-biopsy-pipeline

> Cell-free DNA analysis pipeline from plasma sequencing to tumor monitoring. Preprocesses cfDNA reads, analyzes fragment patterns, estimates tumor fraction from sWGS, and optionally detects mutations from targeted panels. Use when analyzing liquid biopsy samples for cancer detection or monitoring.

**Available tools:** Read, Bash

# Liquid Biopsy Analysis Pipeline

Complete workflow for cfDNA analysis from sequencing to clinical interpretation.

## Pipeline Overview

```
Pre-analytical QC → cfDNA Preprocessing → Fragment QC
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
   sWGS Branch                        Panel Branch
        ↓                                   ↓
   ichorCNA                          VarDict/smCounter2
   (Tumor Fraction)                  (Mutation Detection)
        ↓                                   ↓
        └─────────────────┬─────────────────┘
                          ↓
                 Longitudinal Tracking
```

## Step 0: Pre-Analytical QC

```python
def check_preanalytical_quality(sample_metadata):
    '''
    Pre-analytical factors critical for cfDNA quality.

    Requirements:
    - Streck tube: up to 7 days at room temperature
    - EDTA tube: process within 6 hours
    - Avoid hemolysis
    - Store extracted DNA at -80C
    '''
    issues = []

    if sample_metadata['tube_type'] == 'EDTA':
        if sample_metadata['processing_delay_hours'] > 6:
            issues.append('EDTA tube processed > 6 hours - risk of gDNA contamination')

    if sample_metadata['hemolysis_score'] > 1:
        issues.append('Hemolysis detected - expect cellular DNA contamination')

    return issues
```

## Step 1: cfDNA Preprocessing with UMI Consensus

```bash
# For UMI-tagged libraries (targeted panels)
# fgbio pipeline

# Extract UMIs
fgbio ExtractUmisFromBam \
    --input raw.bam \
    --output with_umis.bam \
    --read-structure 3M2S+T 3M2S+T \
    --single-tag RX

# Align
bwa mem -t 8 -Y reference.fa with_umis.bam | \
    samtools view -bS - > aligned.bam

# Group by UMI
fgbio GroupReadsByUmi \
    --input aligned.bam \
    --output grouped.bam \
    --strategy adjacency \
    --edits 1

# Consensus calling
fgbio CallMolecularConsensusReads \
    --input grouped.bam \
    --output consensus.bam \
    --min-reads 2

# Filter
fgbio FilterConsensusReads \
    --input consensus.bam \
    --output final.bam \
    --ref reference.fa \
    --min-reads 2
```

## Step 2: Fragment QC Checkpoint

```python
import pysam
import numpy as np

def verify_cfdna_quality(bam_path):
    '''
    QC Checkpoint: Verify cfDNA fragment profile.
    Expected: peak at ~167bp (mononucleosome)
    '''
    bam = pysam.AlignmentFile(bam_path, 'rb')
    sizes = []

    for read in bam.fetch():
        if read.is_proper_pair and not read.is_secondary and read.template_length > 0:
            sizes.append(read.template_length)

    bam.close()
    sizes = np.array(sizes)

    modal_size = np.bincount(sizes[:400]).argmax()
    mono_frac = np.sum((sizes >= 150) & (sizes <= 180)) / len(sizes)

    qc_pass = 150 <= modal_size <= 180 and mono_frac > 0.3

    return {
        'modal_size': modal_size,
        'mononucleosome_fraction': mono_frac,
        'qc_pass': qc_pass,
        'message': 'Good cfDNA profile' if qc_pass else 'Atypical fragment distribution'
    }
```

## Step 3a: Tumor Fraction Estimation (sWGS)

```r
# For shallow WGS data (0.1-1x coverage)
library(ichorCNA)

runIchorCNA(
    WIG = 'sample.wig',
    gcWig = 'gc_hg38_1mb.wig',
    mapWig = 'map_hg38_1mb.wig',
    normalPanel = 'pon_median.rds',
    centromere = 'centromeres.txt',
    outDir = 'ichor_results/',
    id = 'sample_id',
    normal = c(0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99),
    ploidy = c(2, 3),
    maxCN = 5
)
```

## Step 3b: Mutation Detection (Targeted Panel)

```bash
# For deep targeted sequencing
# Use UMI-consensus BAM from Step 1

vardict-java \
    -G reference.fa \
    -f 0.005 \
    -N sample_id \
    -b consensus.bam \
    -c 1 -S 2 -E 3 -g 4 \
    panel.bed | \
teststrandbias.R | \
var2vcf_valid.pl \
    -N sample_id \
    -E \
    -f 0.005 \
    > sample.vcf
```

## Step 4: CHIP Filtering

```python
CHIP_GENES = ['DNMT3A', 'TET2', 'ASXL1', 'PPM1D', 'JAK2', 'SF3B1', 'SRSF2', 'TP53']

def filter_chip(variants_df, chip_genes=CHIP_GENES):
    '''
    Filter out clonal hematopoiesis variants.
    Critical for elderly patients (>5% have CHIP).
    '''
    chip = variants_df[variants_df['gene'].isin(chip_genes)]
    somatic = variants_df[~variants_df['gene'].isin(chip_genes)]

    print(f'Potential CHIP variants: {len(chip)}')
    print(f'Likely somatic: {len(somatic)}')

    return somatic, chip
```

## Step 5: Fragmentomics Analysis (Optional)

```python
import finaletoolkit as ft

def run_fragmentomics(bam_path, output_prefix):
    '''
    DELFI-style fragmentation analysis.
    Use FinaleToolkit (MIT license, not DELFI software).
    '''
    fragments = ft.read_fragments(bam_path)

    profile = ft.calculate_fragmentation_profile(
        fragments,
        bin_size=5_000_000,
        short_range=(100, 150),
        long_range=(151, 220)
    )

    profile.to_csv(f'{output_prefix}_frag_profile.csv')
    return profile
```

## Step 6: Longitudinal Tracking

```python
import pandas as pd
import numpy as np

def track_longitudinal(samples_df):
    '''
    Track ctDNA over treatment.

    samples_df columns: [sample_id, timepoint, tumor_fraction, mutations...]
    '''
    samples_df = samples_df.sort_values('timepoint')

    baseline = samples_df.iloc[0]['tumor_fraction']
    samples_df['log2_fc'] = np.log2(samples_df['tumor_fraction'] / baseline)

    nadir = samples_df['tumor_fraction'].min()

    response = 'unknown'
    if nadir < 0.001:
        response = 'Complete molecular response'
    elif nadir < baseline * 0.01:
        response = 'Major molecular response (>2 log)'
    elif nadir < baseline * 0.5:
        response = 'Partial molecular response'

    return samples_df, response
```

## Complete Pipeline Script

```python
def run_liquid_biopsy_pipeline(sample_config):
    '''
    Complete liquid biopsy analysis pipeline.

    sample_config: dict with keys:
        - bam_file: Input BAM
        - data_type: 'swgs' or 'panel'
        - reference: Reference FASTA
        - bed_file: Panel BED (for panel data)
        - output_dir: Output directory
    '''
    results = {}

    # Step 1: Preprocess (if UMI data)
    if sample_config.get('has_umis'):
        preprocessed_bam = preprocess_with_fgbio(sample_config['bam_file'])
    else:
        preprocessed_bam = sample_config['bam_file']

    # Step 2: Fragment QC
    frag_qc = verify_cfdna_quality(preprocessed_bam)
    if not frag_qc['qc_pass']:
        print(f"WARNING: {frag_qc['message']}")
    results['fragment_qc'] = frag_qc

    # Step 3: Analysis based on data type
    if sample_config['data_type'] == 'swgs':
        # Tumor fraction estimation
        results['tumor_fraction'] = run_ichorcna(preprocessed_bam)
    elif sample_config['data_type'] == 'panel':
        # Mutation detection
        variants = call_variants(preprocessed_bam, sample_config['bed_file'])
        somatic, chip = filter_chip(variants)
        results['variants'] = somatic
        results['chip_variants'] = chip

    # Step 4: Optional fragmentomics
    if sample_config.get('run_fragmentomics'):
        results['fragmentomics'] = run_fragmentomics(preprocessed_bam)

    return results
```

## Related Skills

- liquid-biopsy/cfdna-preprocessing - Preprocessing details
- liquid-biopsy/tumor-fraction-estimation - ichorCNA analysis
- liquid-biopsy/ctdna-mutation-detection - Variant calling
- liquid-biopsy/fragment-analysis - Fragmentomics
- liquid-biopsy/longitudinal-monitoring - Serial tracking
