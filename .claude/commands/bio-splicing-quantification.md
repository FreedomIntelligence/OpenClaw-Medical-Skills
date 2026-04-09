# bio-splicing-quantification

> Quantifies alternative splicing events (PSI/percent spliced in) from RNA-seq using SUPPA2 from transcript TPM or rMATS-turbo from BAM files. Calculates inclusion levels for skipped exons, alternative splice sites, mutually exclusive exons, and retained introns. Use when measuring splice site usage or isoform ratios from RNA-seq data.

## Version Compatibility

Reference examples tested with: kallisto 0.50+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Splicing Quantification

Quantify alternative splicing events as PSI (percent spliced in) values from RNA-seq data.

## Event Types

| Type | Code | Description |
|------|------|-------------|
| Skipped exon | SE | Exon inclusion/exclusion |
| Alternative 5' splice site | A5SS | Alternative donor site |
| Alternative 3' splice site | A3SS | Alternative acceptor site |
| Mutually exclusive exons | MXE | One of two exons included |
| Retained intron | RI | Intron retention |

## Tool Selection

### SUPPA2 (transcript TPM-based)
- Input: Transcript TPM from Salmon/kallisto
- Faster, requires transcript quantification
- Better for isoform-level analysis

### rMATS-turbo (BAM-based)
- Input: Aligned BAM files
- Junction read counting
- Better for novel junction discovery

## SUPPA2 Workflow

**Goal:** Calculate PSI values for all splicing event types from transcript-level quantification.

**Approach:** Generate event definitions from GTF annotation, then compute per-event PSI from transcript TPM using SUPPA2.

**"Quantify splicing from RNA-seq"** -> Extract splicing events from annotation, then calculate inclusion ratios from transcript abundance.
- Python/CLI: `suppa.py generateEvents` + `suppa.py psiPerEvent` (SUPPA2)
- CLI: `rmats.py` with `--statoff` (rMATS-turbo, BAM-based)

```python
import subprocess
import pandas as pd

gtf_file = 'annotation.gtf'
tpm_file = 'transcript_tpm.tsv'
output_prefix = 'events'

# Step 1: Generate splicing events from annotation
subprocess.run([
    'suppa.py', 'generateEvents',
    '-i', gtf_file,
    '-o', output_prefix,
    '-f', 'ioe',  # IOE format for PSI calculation
    '-e', 'SE', 'SS', 'MX', 'RI', 'FL'  # All event types
], check=True)

# Step 2: Calculate PSI values
for event_type in ['SE', 'A5', 'A3', 'MX', 'RI']:
    ioe_file = f'{output_prefix}_{event_type}_strict.ioe'
    subprocess.run([
        'suppa.py', 'psiPerEvent',
        '-i', ioe_file,
        '-e', tpm_file,
        '-o', f'psi_{event_type}'
    ], check=True)

# Load and examine PSI values
psi_se = pd.read_csv('psi_SE.psi', sep='\t', index_col=0)
print(f'Quantified {len(psi_se)} skipped exon events')
print(psi_se.head())
```

## rMATS-turbo Workflow

**Goal:** Quantify splicing events directly from aligned BAM files using junction read counting.

**Approach:** Run rMATS-turbo on paired BAM groups with annotation, then parse inclusion level columns from output.

```bash
# rMATS-turbo for BAM-based quantification
rmats.py \
    --b1 condition1_bams.txt \
    --b2 condition2_bams.txt \
    --gtf annotation.gtf \
    -t paired \
    --readLength 150 \
    --nthread 8 \
    --od output_dir \
    --tmp tmp_dir \
    --statoff  # Use for quantification only, no differential testing
```

```python
import pandas as pd

# Load rMATS output
se_jc = pd.read_csv('output_dir/SE.MATS.JC.txt', sep='\t')

# Calculate average PSI across samples
# IncLevel columns contain PSI values per sample
inc_cols = [c for c in se_jc.columns if c.startswith('IncLevel')]
se_jc['mean_PSI'] = se_jc[inc_cols].mean(axis=1)

# Filter for reliable events (sufficient junction reads)
# Minimum 10-20 junction reads recommended for reliable PSI
se_jc['total_junction_reads'] = se_jc['IJC_SAMPLE_1'] + se_jc['SJC_SAMPLE_1']
reliable_events = se_jc[se_jc['total_junction_reads'] >= 20]
print(f'{len(reliable_events)} events with sufficient coverage')
```

## Quality Thresholds

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Junction reads | >= 10-20 | Minimum for reliable PSI estimation |
| PSI range | 0.1-0.9 | Events outside this range are nearly constitutive |
| Missing values | < 50% samples | High missingness indicates low expression |

## Output Interpretation

PSI values range from 0 to 1:
- PSI = 1.0: Event fully included (e.g., exon always present)
- PSI = 0.5: Equal inclusion/exclusion
- PSI = 0.0: Event fully excluded (e.g., exon always skipped)

## Related Skills

- differential-splicing - Compare PSI between conditions
- rna-quantification/alignment-free-quant - Generate transcript TPM for SUPPA2
- read-alignment/star-alignment - Align reads with junction detection
