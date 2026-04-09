# bio-methylation-calling

> Extract methylation calls from Bismark BAM files using bismark_methylation_extractor. Generates per-cytosine reports for CpG, CHG, and CHH contexts. Use when extracting methylation levels from aligned bisulfite sequencing data for downstream analysis.

## Version Compatibility

Reference examples tested with: pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Methylation Calling

**"Extract methylation calls from my Bismark BAM"** → Generate per-cytosine methylation reports (CpG, CHG, CHH contexts) from aligned bisulfite sequencing data.
- CLI: `bismark_methylation_extractor --bedGraph --cytosine_report sample.bam`

## Basic Extraction

```bash
# Extract methylation calls from Bismark BAM
bismark_methylation_extractor --gzip --bedGraph \
    sample_bismark_bt2.bam
```

## Paired-End Extraction

```bash
bismark_methylation_extractor --paired-end --gzip --bedGraph \
    sample_bismark_bt2_pe.bam
```

## Common Options

```bash
bismark_methylation_extractor \
    --paired-end \                 # For paired-end data
    --gzip \                       # Compress output
    --bedGraph \                   # Generate bedGraph file
    --cytosine_report \            # Genome-wide cytosine report
    --genome_folder /path/to/genome/ \  # Required for cytosine_report
    --buffer_size 10G \            # Memory buffer
    --parallel 4 \                 # Parallel extraction
    -o output_dir/ \
    sample.bam
```

## CpG Context Only

```bash
# Most common - extract only CpG methylation
bismark_methylation_extractor \
    --paired-end \
    --no_overlap \                 # Avoid double counting overlapping reads
    --gzip \
    --bedGraph \
    --CX \                         # Also extract CHG/CHH (optional)
    sample.bam
```

## Genome-Wide Cytosine Report

```bash
# Comprehensive report with all CpGs in genome
bismark_methylation_extractor \
    --paired-end \
    --gzip \
    --bedGraph \
    --cytosine_report \
    --genome_folder /path/to/genome/ \
    sample.bam
```

## Strand-Specific Output

```bash
# Default: strand-specific output
# CpG_OT_sample.txt - Original Top strand
# CpG_OB_sample.txt - Original Bottom strand
# CpG_CTOT_sample.txt - Complementary to OT
# CpG_CTOB_sample.txt - Complementary to OB

# Merge strands (CpG methylation is usually symmetric)
bismark_methylation_extractor --merge_non_CpG --gzip sample.bam
```

## Avoid Double-Counting Overlapping Reads

```bash
# For paired-end data with overlapping reads
bismark_methylation_extractor \
    --paired-end \
    --no_overlap \                 # Ignore overlapping portion of read 2
    --gzip \
    sample_pe.bam
```

## Generate Coverage File

```bash
# bismark2bedGraph creates coverage file
bismark_methylation_extractor --bedGraph --gzip sample.bam

# Or run separately
bismark2bedGraph -o sample CpG_context_sample.txt.gz

# Coverage format: chr start end methylation_percentage count_meth count_unmeth
```

## Convert to BigWig for Visualization

```bash
# bedGraph to BigWig (requires UCSC tools)
bedGraphToBigWig sample.bedGraph.gz chrom.sizes sample.bw
```

## M-Bias Plot

```bash
# Check for methylation bias across read positions
bismark_methylation_extractor --paired-end \
    --mbias_only \                 # Only generate M-bias plot
    sample.bam

# Generates sample.M-bias.txt and sample.M-bias_R1.png, sample.M-bias_R2.png
```

## Ignore End Bias

```bash
# Ignore positions with systematic bias (found from M-bias plot)
bismark_methylation_extractor \
    --paired-end \
    --ignore 2 \                   # Ignore first 2 bp of read 1
    --ignore_r2 2 \                # Ignore first 2 bp of read 2
    --ignore_3prime 2 \            # Ignore last 2 bp of read 1
    --ignore_3prime_r2 2 \         # Ignore last 2 bp of read 2
    sample.bam
```

## Output Files

```bash
# Main output files:
# CpG_context_sample.txt.gz      - Per-read CpG methylation
# sample.bismark.cov.gz          - Coverage file
# sample.bedGraph.gz             - bedGraph for visualization
# sample.CpG_report.txt.gz       - Genome-wide CpG report (with --cytosine_report)

# Coverage file format:
# chr  start  end  methylation%  count_methylated  count_unmethylated
```

## Parse Output in Python

```python
import pandas as pd

cov = pd.read_csv('sample.bismark.cov.gz', sep='\t', header=None,
                   names=['chr', 'start', 'end', 'meth_pct', 'count_meth', 'count_unmeth'])
cov['coverage'] = cov['count_meth'] + cov['count_unmeth']
cov_filtered = cov[cov['coverage'] >= 10]
```

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| --paired-end | Paired-end mode |
| --gzip | Compress output |
| --bedGraph | Generate bedGraph |
| --cytosine_report | Full genome cytosine report |
| --genome_folder | Path to genome (for cytosine_report) |
| --CX | Report CHG/CHH contexts |
| --no_overlap | Avoid counting overlapping reads twice |
| --parallel | Parallel extraction threads |
| --mbias_only | Only M-bias analysis |
| --ignore N | Ignore first N bp of read 1 |
| --ignore_r2 N | Ignore first N bp of read 2 |

## Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| CpG_context | Per-read methylation calls | Detailed analysis |
| .bismark.cov | Per-CpG coverage summary | methylKit input |
| .bedGraph | Methylation track | Genome browser |
| .CpG_report | All genome CpGs | Comprehensive analysis |

## Related Skills

- bismark-alignment - Generate input BAM files
- methylkit-analysis - Import coverage files to R
- dmr-detection - Find differentially methylated regions
