# bio-differential-splicing

> Detects differential alternative splicing between conditions using rMATS-turbo (BAM-based) or SUPPA2 diffSplice (TPM-based). Reports events with FDR-corrected significance and delta PSI effect sizes. Use when comparing splicing patterns between treatment groups, tissues, or disease states.

## Version Compatibility

Reference examples tested with: STAR 2.7.11+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Differential Splicing

Detect differential alternative splicing events between experimental conditions.

## Tool Comparison

| Tool | Input | Approach | Strengths |
|------|-------|----------|-----------|
| rMATS-turbo | BAM | Junction counting | Novel junctions, statistical model |
| SUPPA2 | TPM | Transcript ratios | Speed, isoform-aware |
| leafcutter | BAM | Intron clustering | Novel events, no annotation bias |

## rMATS-turbo Analysis

**Goal:** Detect statistically significant differential splicing events between two conditions from BAM files.

**Approach:** Run rMATS-turbo on condition-grouped BAMs, then filter results by FDR and delta PSI thresholds.

**"Find differential splicing between conditions"** -> Compare junction-level inclusion across sample groups with statistical testing.
- CLI/Python: `rmats.py` + pandas filtering (rMATS-turbo)
- Python/CLI: `suppa.py diffSplice` (SUPPA2, TPM-based)
- R: `leafcutter_ds.R` (leafcutter, annotation-free)

```bash
# Create sample lists (one BAM path per line)
# condition1_bams.txt: /path/to/sample1.bam, /path/to/sample2.bam, ...
# condition2_bams.txt: /path/to/sample3.bam, /path/to/sample4.bam, ...

rmats.py \
    --b1 condition1_bams.txt \
    --b2 condition2_bams.txt \
    --gtf annotation.gtf \
    -t paired \
    --readLength 150 \
    --nthread 8 \
    --od rmats_output \
    --tmp rmats_tmp
```

```python
import pandas as pd

# Load results for skipped exons
se = pd.read_csv('rmats_output/SE.MATS.JC.txt', sep='\t')

# Filter significant differential splicing events
# |deltaPSI| > 0.1 (lenient) or > 0.2 (stringent)
# FDR < 0.05
significant = se[
    (se['FDR'] < 0.05) &
    (se['IncLevelDifference'].abs() > 0.1)
].copy()

print(f'{len(significant)} significant SE events')
print(significant[['GeneID', 'geneSymbol', 'IncLevelDifference', 'FDR']].head(10))

# Additional filtering by junction read support
# Require at least 10 reads supporting each junction type
significant = significant[
    (significant['IJC_SAMPLE_1'].str.split(',').apply(lambda x: min(map(int, x))) >= 10) |
    (significant['SJC_SAMPLE_1'].str.split(',').apply(lambda x: min(map(int, x))) >= 10)
]
```

## SUPPA2 Differential Analysis

**Goal:** Identify differential splicing from transcript quantification without alignment.

**Approach:** Compare per-event PSI distributions between conditions using SUPPA2 empirical p-value calculation.

```python
import subprocess

# Requires PSI files from suppa.py psiPerEvent
# TPM file with samples from both conditions

# Run differential splicing
subprocess.run([
    'suppa.py', 'diffSplice',
    '-m', 'empirical',  # Empirical p-value calculation
    '-i', 'events_SE_strict.ioe',
    '-p', 'condition1.psi', 'condition2.psi',
    '-e', 'condition1.tpm', 'condition2.tpm',
    '-o', 'diff_SE'
], check=True)

# Load results
import pandas as pd
diff = pd.read_csv('diff_SE.dpsi', sep='\t', index_col=0)

# SUPPA2 tends to be more stringent
significant = diff[
    (diff['p-value'] < 0.05) &
    (diff['dPSI'].abs() > 0.1)
]
```

## leafcutter Analysis

**Goal:** Detect differential intron usage without relying on transcript annotation.

**Approach:** Extract junctions from BAMs, cluster introns by shared splice sites, then test differential usage between groups.

```r
library(leafcutter)

# Convert BAMs to junction files
# leafcutter_bam_to_junc.sh uses regtools
system('for bam in *.bam; do
    regtools junctions extract -a 8 -m 50 -s 0 $bam -o ${bam%.bam}.junc
done')

# Create junction file list
writeLines(list.files(pattern = '\\.junc$'), 'juncfiles.txt')

# Cluster introns
system('python leafcutter_cluster_regtools.py -j juncfiles.txt -o leafcutter')

# Run differential analysis
groups <- data.frame(
    sample = c('sample1', 'sample2', 'sample3', 'sample4'),
    group = c('control', 'control', 'treatment', 'treatment')
)
write.table(groups, 'groups.txt', sep = '\t', quote = FALSE, row.names = FALSE)

# Differential intron usage
system('leafcutter_ds.R --num_threads 4 leafcutter_perind_numers.counts.gz groups.txt')
```

## Significance Thresholds

| Stringency | deltaPSI | FDR | Use Case |
|------------|----------|-----|----------|
| Lenient | > 0.1 | < 0.05 | Discovery, exploratory |
| Standard | > 0.15 | < 0.05 | Publication |
| Stringent | > 0.2 | < 0.01 | High-confidence set |

## Result Prioritization

**Goal:** Rank differential splicing events by combined statistical and biological significance.

**Approach:** Compute a composite score from FDR and effect size, then select top-scoring events for follow-up.

```python
# Prioritize by effect size and significance
significant['score'] = -np.log10(significant['FDR']) * significant['IncLevelDifference'].abs()
top_events = significant.nlargest(50, 'score')

# Annotate with gene function
# Consider protein domain disruption, NMD sensitivity
```

## Related Skills

- splicing-quantification - Calculate PSI values first
- isoform-switching - Functional consequence analysis
- sashimi-plots - Visualize significant events
- read-alignment/star-alignment - STAR 2-pass alignment required
