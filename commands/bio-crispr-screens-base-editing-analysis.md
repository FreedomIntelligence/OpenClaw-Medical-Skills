# bio-crispr-screens-base-editing-analysis

> Analyzes base editing and prime editing outcomes including editing efficiency, bystander edits, and indel frequencies. Use when quantifying CRISPR base editor results, comparing ABE vs CBE efficiency, or assessing prime editing fidelity.

## Version Compatibility

Reference examples tested with: CRISPResso2 2.2+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Base Editing Analysis

**"Analyze my base editing outcomes"** → Quantify base editing efficiency, bystander edits, and indel frequencies from amplicon sequencing data for CBE, ABE, and prime editing experiments.
- CLI: `CRISPResso --fastq_r1 reads.fq --amplicon_seq ATGC --base_editor_output`

## CRISPResso2 for Base Editing

**Goal:** Quantify base editing efficiency and bystander edits from amplicon sequencing.

**Approach:** Run CRISPResso with --base_editor_output and the expected edited amplicon sequence to measure target base conversion, bystander edits, and indel frequencies.

```bash
# Analyze base editing with expected outcome
CRISPResso --fastq_r1 reads.fq.gz \
    --amplicon_seq ATGCGATCGATCGATCGATCGATCG \
    --guide_seq TCGATCGATCGATCGAT \
    --expected_hdr_amplicon_seq ATGCGATCGATCGTTCGATCGATCG \
    --base_editor_output \
    -o results/
```

## Key Metrics

| Metric | Description |
|--------|-------------|
| Editing efficiency | % reads with target base change |
| Bystander edits | Unintended edits in editing window |
| Indel frequency | Insertions/deletions (should be low) |
| Purity | Target edit without bystanders |

## Base Editor Types

### Cytosine Base Editors (CBE)

```bash
# C->T conversion (or G->A on opposite strand)
CRISPResso --fastq_r1 reads.fq.gz \
    --amplicon_seq $AMPLICON \
    --guide_seq $GUIDE \
    --base_editor_output \
    --conversion_nuc_from C \
    --conversion_nuc_to T
```

### Adenine Base Editors (ABE)

```bash
# A->G conversion (or T->C on opposite strand)
CRISPResso --fastq_r1 reads.fq.gz \
    --amplicon_seq $AMPLICON \
    --guide_seq $GUIDE \
    --base_editor_output \
    --conversion_nuc_from A \
    --conversion_nuc_to G
```

## Prime Editing Analysis

```bash
# Prime editing with pegRNA
CRISPResso --fastq_r1 reads.fq.gz \
    --amplicon_seq $AMPLICON \
    --guide_seq $SPACER \
    --expected_hdr_amplicon_seq $EDITED_AMPLICON \
    --prime_editing_pegRNA_extension_seq $EXTENSION \
    -o prime_edit_results/
```

## Editing Window Analysis

```python
import pandas as pd

# Load CRISPResso quantification
quant = pd.read_csv('CRISPResso_output/Quantification_window_nucleotide_percentage_table.txt',
                    sep='\t')

# Calculate per-position editing
editing_window = quant[(quant['Position'] >= -5) & (quant['Position'] <= 5)]
```

## Quality Thresholds

- Editing efficiency: >30% considered good for most applications
- Indel rate: <5% ideal for base editors
- Bystander rate: depends on application; <10% often acceptable

## Related Skills

- crispr-screens/crispresso-editing - General editing QC
- crispr-screens/library-design - Guide design considerations
- variant-calling/vcf-basics - Downstream variant analysis
