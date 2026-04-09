# bio-ribo-seq-translation-efficiency

> Calculate translation efficiency (TE) as the ratio of ribosome occupancy to mRNA abundance. Use when comparing translational regulation between conditions or identifying genes with altered translation independent of transcription.

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Translation Efficiency

**"Calculate translation efficiency from my Ribo-seq and RNA-seq"** → Compute the ratio of ribosome occupancy to mRNA abundance per gene to identify translational regulation independent of transcription changes.
- R: `riborex` for differential TE with DESeq2 backend
- Python: Ribo-seq/RNA-seq count ratio with statistical testing

## Concept

Translation Efficiency (TE) = Ribo-seq reads / RNA-seq reads

- TE > 1: Efficiently translated (more ribosomes per mRNA)
- TE < 1: Poorly translated
- Changes in TE indicate translational regulation

## Calculate TE with Plastid

```python
from plastid import BAMGenomeArray, GTF2_TranscriptAssembler
import pandas as pd
import numpy as np

def calculate_te(riboseq_bam, rnaseq_bam, gtf_path):
    '''Calculate translation efficiency per gene'''
    # Load transcripts
    transcripts = list(GTF2_TranscriptAssembler(gtf_path))

    # Load alignments
    ribo = BAMGenomeArray(riboseq_bam)
    rna = BAMGenomeArray(rnaseq_bam)

    results = []
    for tx in transcripts:
        if tx.cds_start is None:
            continue

        # Get CDS region
        cds = tx.get_cds()

        # Count reads
        ribo_counts = ribo.count_in_region(cds)
        rna_counts = rna.count_in_region(tx)  # Full transcript for RNA-seq

        # Normalize by length
        cds_length = sum(len(seg) for seg in cds)
        tx_length = tx.length

        ribo_rpk = ribo_counts / (cds_length / 1000)
        rna_rpk = rna_counts / (tx_length / 1000)

        if rna_rpk > 0:
            te = ribo_rpk / rna_rpk
        else:
            te = np.nan

        results.append({
            'gene': tx.get_gene(),
            'transcript': tx.get_name(),
            'ribo_counts': ribo_counts,
            'rna_counts': rna_counts,
            'te': te
        })

    return pd.DataFrame(results)
```

## Differential TE with riborex

```r
library(riborex)

# Load count matrices
# Rows = genes, columns = samples
ribo_counts <- read.csv('ribo_counts.csv', row.names = 1)
rna_counts <- read.csv('rna_counts.csv', row.names = 1)

# Sample information
sample_info <- data.frame(
    sample = colnames(ribo_counts),
    condition = factor(c('control', 'control', 'treated', 'treated'))
)

# Run riborex
results <- riborex(
    rnaCntTable = rna_counts,
    riboCntTable = ribo_counts,
    rnaCond = sample_info$condition,
    riboCond = sample_info$condition
)

# Significant differential TE
sig_te <- results[results$padj < 0.05, ]
```

## Using DESeq2 Interaction Model

**Goal:** Test for differential translation efficiency between conditions using a formal statistical framework that separates transcriptional from translational regulation.

**Approach:** Combine Ribo-seq and RNA-seq counts into one matrix, fit a DESeq2 model with a condition-by-assay interaction term, and extract the interaction coefficient which represents differential TE.

```r
library(DESeq2)

# Combine Ribo-seq and RNA-seq counts
counts <- cbind(ribo_counts, rna_counts)

# Design matrix with interaction term
coldata <- data.frame(
    condition = factor(rep(c('ctrl', 'ctrl', 'treat', 'treat'), 2)),
    assay = factor(rep(c('ribo', 'rna'), each = 4)),
    row.names = colnames(counts)
)

dds <- DESeqDataSetFromMatrix(
    countData = counts,
    colData = coldata,
    design = ~ condition + assay + condition:assay
)

dds <- DESeq(dds)

# The interaction term tests for differential TE
res_te <- results(dds, name = 'conditiontreat.assayribo')
```

## Normalize Counts

```python
def normalize_counts(counts_df, method='tpm'):
    '''Normalize count matrix'''
    if method == 'tpm':
        # TPM normalization
        rpk = counts_df.div(counts_df['length'] / 1000, axis=0)
        scale = rpk.sum(axis=0) / 1e6
        tpm = rpk.div(scale, axis=1)
        return tpm

    elif method == 'rpkm':
        # RPKM normalization
        total = counts_df.sum(axis=0)
        rpm = counts_df / total * 1e6
        rpkm = rpm.div(counts_df['length'] / 1000, axis=0)
        return rpkm

def calculate_te_matrix(ribo_tpm, rna_tpm):
    '''Calculate TE from normalized matrices'''
    # Add pseudocount to avoid division by zero
    te = (ribo_tpm + 0.1) / (rna_tpm + 0.1)
    return np.log2(te)  # Log2 TE
```

## Interpretation

| Log2 TE Change | Interpretation |
|----------------|----------------|
| > 1 | Strong translational activation |
| 0.5 - 1 | Moderate activation |
| -0.5 - 0.5 | No significant change |
| -1 - -0.5 | Moderate repression |
| < -1 | Strong translational repression |

## Related Skills

- rna-quantification - Get RNA-seq counts
- differential-expression - Compare expression
- orf-detection - Identify translated ORFs
