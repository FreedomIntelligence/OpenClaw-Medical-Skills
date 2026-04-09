# bio-isoform-switching

> Analyzes isoform switching events and functional consequences using IsoformSwitchAnalyzeR. Predicts protein domain changes, NMD sensitivity, ORF alterations, and coding potential shifts between conditions. Use when investigating how splicing changes affect protein function.

## Version Compatibility

Reference examples tested with: Salmon 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Isoform Switching Analysis

Identify isoform switches and predict their functional consequences on protein structure and function.

## IsoformSwitchAnalyzeR Workflow

**Goal:** Identify genes where the dominant isoform switches between conditions.

**Approach:** Import Salmon quantification, filter low-expression isoforms, and test for isoform usage changes with DEXSeq-based statistics.

**"Analyze isoform switching"** -> Import transcript quantification, test for dominant isoform changes, and assess functional consequences.
- R: `IsoformSwitchAnalyzeR` (importRdata + isoformSwitchTestDEXSeq)

```r
library(IsoformSwitchAnalyzeR)

# Import transcript quantification from Salmon
salmonQuant <- importIsoformExpression(
    parentDir = 'salmon_quant/',
    addIsofomIdAsColumn = TRUE
)

# Create switch analysis object
switchAnalyzeRlist <- importRdata(
    isoformCountMatrix = salmonQuant$counts,
    isoformRepExpression = salmonQuant$abundance,
    designMatrix = data.frame(
        sampleID = colnames(salmonQuant$counts),
        condition = c('control', 'control', 'control', 'treatment', 'treatment', 'treatment')
    ),
    isoformExonAnnoation = 'annotation.gtf',
    isoformNtFasta = 'transcripts.fa'
)

# Filter lowly expressed isoforms
switchAnalyzeRlist <- preFilter(
    switchAnalyzeRlist,
    geneExpressionCutoff = 1,  # Minimum TPM
    isoformExpressionCutoff = 0,
    removeSingleIsoformGenes = TRUE
)

# Test for isoform switches
switchAnalyzeRlist <- isoformSwitchTestDEXSeq(
    switchAnalyzeRlist,
    reduceToSwitchingGenes = TRUE
)
```

## Functional Annotation

**Goal:** Predict how isoform switches alter protein domains, coding potential, and localization.

**Approach:** Extract isoform sequences, run external annotation tools (CPC2, Pfam, SignalP, IUPred2), and import results back into the switch analysis object.

```r
# Extract sequences for external analysis
switchAnalyzeRlist <- extractSequence(
    switchAnalyzeRlist,
    pathToOutput = 'sequences/',
    writeToFile = TRUE
)

# Run external tools and import results:
# - CPC2 for coding potential
# - Pfam for protein domains
# - SignalP for signal peptides
# - IUPred2 for intrinsic disorder

# After running external tools, import results
switchAnalyzeRlist <- analyzeCPC2(
    switchAnalyzeRlist,
    pathToCPC2resultFile = 'cpc2_results.txt',
    removeNoncodinORFs = TRUE
)

switchAnalyzeRlist <- analyzePFAM(
    switchAnalyzeRlist,
    pathToPFAMresultFile = 'pfam_results.txt'
)

switchAnalyzeRlist <- analyzeSignalP(
    switchAnalyzeRlist,
    pathToSignalPresultFile = 'signalp_results.txt'
)

switchAnalyzeRlist <- analyzeIUPred2A(
    switchAnalyzeRlist,
    pathToIUPred2AresultFile = 'iupred2_results.txt'
)
```

## Consequence Analysis

**Goal:** Determine which isoform switches cause functional changes (NMD, domain loss, coding potential shifts).

**Approach:** Run analyzeSwitchConsequences across multiple consequence types and extract switches with confirmed functional impact.

```r
# Analyze functional consequences of switches
switchAnalyzeRlist <- analyzeSwitchConsequences(
    switchAnalyzeRlist,
    consequencesToAnalyze = c(
        'intron_retention',
        'coding_potential',
        'ORF_seq_similarity',
        'NMD_status',
        'domains_identified',
        'signal_peptide_identified'
    ),
    dIFcutoff = 0.1,  # Minimum isoform fraction change
    showProgress = TRUE
)

# Extract significant switches
significantSwitches <- extractSwitchSummary(
    switchAnalyzeRlist,
    filterForConsequences = TRUE
)

print(significantSwitches)
```

## Visualization

**Goal:** Visualize isoform switch events and summarize functional consequence patterns.

**Approach:** Generate per-gene switch plots showing isoform usage changes, and create global summaries of consequence enrichment.

```r
# Plot individual gene switches
switchPlot(
    switchAnalyzeRlist,
    gene = 'GENE_OF_INTEREST',
    condition1 = 'control',
    condition2 = 'treatment'
)

# Summary of consequence types
extractConsequenceSummary(
    switchAnalyzeRlist,
    consequencesToAnalyze = 'all',
    plotGenes = FALSE
)

# Enrichment of consequences
extractConsequenceEnrichment(
    switchAnalyzeRlist,
    consequencesToAnalyze = 'all'
)
```

## Significance Thresholds

| Parameter | Default | Description |
|-----------|---------|-------------|
| Switch q-value | < 0.05 | Significance of isoform switch |
| dIF (delta isoform fraction) | > 0.1 | Minimum usage change |
| Consequence q-value | < 0.05 | Significance of consequence |

## Consequence Types

| Consequence | Impact |
|-------------|--------|
| NMD sensitive | Transcript targeted for degradation |
| Domain loss/gain | Altered protein function |
| ORF disruption | Truncated/altered protein |
| Signal peptide loss | Changed localization |
| Coding potential loss | Switch to non-coding |

## Related Skills

- differential-splicing - Identify differential events first
- splicing-quantification - PSI-level analysis
- pathway-analysis/go-enrichment - Pathway enrichment of switching genes
