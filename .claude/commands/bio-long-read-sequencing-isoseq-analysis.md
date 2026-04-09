# bio-long-read-sequencing-isoseq-analysis

> Analyze PacBio Iso-Seq data for full-length isoform discovery and quantification. Use when characterizing transcript diversity or identifying novel splice variants.

## Version Compatibility

Reference examples tested with: minimap2 2.26+, pandas 2.2+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Iso-Seq Analysis

**"Analyze full-length isoforms from my Iso-Seq data"** → Process PacBio HiFi reads through CCS generation, primer removal, clustering, and isoform classification to discover novel transcript variants.
- CLI: `isoseq3 refine` → `isoseq3 cluster` → `pbmm2 align` → `sqanti3_qc.py`

## IsoSeq3 Pipeline Overview

```bash
# Full pipeline: subreads -> HQ transcripts
# 1. CCS: Generate circular consensus sequences
# 2. Lima: Remove primers and demultiplex
# 3. Refine: Remove polyA and concatemers
# 4. Cluster: Group into isoforms
# 5. Polish: Generate high-quality consensus (optional with HiFi)
```

## CCS Generation

```bash
# Generate CCS from subreads (skip if using HiFi reads)
ccs input.subreads.bam ccs.bam \
    --min-rq 0.9 \
    --min-passes 3 \
    --num-threads 32

# For HiFi reads, CCS is already done
# Start directly from HiFi reads
```

## Primer Removal with Lima

```bash
# Iso-Seq specific primer removal
lima ccs.bam primers.fasta demux.bam \
    --isoseq \
    --peek-guess \
    --num-threads 16

# Output: demux.primer_5p--primer_3p.bam
# Lima reports also contain demux statistics

# Check lima report
cat demux.lima.summary
```

## Primer File Format

```fasta
>primer_5p
AAGCAGTGGTATCAACGCAGAGTACATGGG
>primer_3p
AAGCAGTGGTATCAACGCAGAGTAC
```

## Refine Full-Length Reads

```bash
# Remove polyA tails and concatemers
isoseq3 refine demux.primer_5p--primer_3p.bam primers.fasta refined.bam \
    --require-polya \
    --min-polya-length 20

# Output: refined.bam (full-length non-chimeric reads)
# Also: refined.filter_summary.json

# Check refinement stats
cat refined.filter_summary.json | jq
```

## Cluster Into Isoforms

```bash
# Cluster similar transcripts
isoseq3 cluster refined.bam clustered.bam \
    --verbose \
    --use-qvs \
    --num-threads 32

# Output files:
# - clustered.bam: Clustered transcripts
# - clustered.hq_transcripts.fasta: High-quality consensus
# - clustered.lq_transcripts.fasta: Low-quality consensus
# - clustered.cluster_report.csv: Cluster membership
```

## Align to Reference

```bash
# Map HQ transcripts to reference genome
minimap2 -ax splice:hq \
    -uf \
    --secondary=no \
    reference.fa \
    clustered.hq_transcripts.fasta \
    | samtools sort -o aligned.bam

samtools index aligned.bam

# For downstream analysis
pbmm2 align reference.fa clustered.bam aligned.bam \
    --preset ISOSEQ \
    --sort
```

## Collapse Redundant Isoforms

```bash
# Collapse mapped transcripts
isoseq3 collapse aligned.bam collapsed.gff

# Output:
# - collapsed.gff: Collapsed transcript models
# - collapsed.abundance.txt: Read counts per isoform
# - collapsed.group.txt: Isoform groupings

# Convert to GTF
gffread collapsed.gff -T -o collapsed.gtf
```

## SQANTI3 Quality Control

```bash
# Classify isoforms against reference annotation
sqanti3_qc.py \
    clustered.hq_transcripts.fasta \
    reference.gtf \
    reference.fa \
    -o sqanti_output \
    --aligner_choice minimap2 \
    --cage_peak cage_peaks.bed \
    --polyA_motif_list polyA_motifs.txt \
    --cpus 16

# Key output files:
# - sqanti_output_classification.txt: Per-isoform metrics
# - sqanti_output_junctions.txt: Splice junction details
# - sqanti_output.params.txt: Run parameters
```

## SQANTI3 Categories

| Category | Code | Description |
|----------|------|-------------|
| Full Splice Match | FSM | All junctions match reference |
| Incomplete Splice Match | ISM | Subset of reference junctions |
| Novel In Catalog | NIC | Novel combination of known junctions |
| Novel Not in Catalog | NNC | Contains novel junction |
| Antisense | AS | Overlaps gene on opposite strand |
| Genic | G | Within gene but no junction match |
| Intergenic | IR | Between genes |
| Fusion | FU | Spans multiple genes |

## SQANTI3 Filtering

```bash
# Filter artifacts using SQANTI3 rules
sqanti3_filter.py \
    sqanti_output_classification.txt \
    --isoforms clustered.hq_transcripts.fasta \
    --gtf collapsed.gtf \
    --faa predicted_proteins.faa \
    -o sqanti_filtered

# Custom filtering
python << 'EOF'
import pandas as pd

classification = pd.read_csv('sqanti_output_classification.txt', sep='\t')

# Keep FSM, ISM, NIC with evidence
keep = classification[
    (classification['structural_category'].isin(['full-splice_match', 'incomplete-splice_match', 'novel_in_catalog'])) &
    (classification['FL'] >= 2) &
    (classification['bite'] == 'FALSE')
]
keep['isoform'].to_csv('filtered_isoforms.txt', index=False, header=False)
EOF
```

## Quantification with Pigeon

```bash
# PacBio's isoform quantification tool
pigeon classify \
    aligned.bam \
    reference.gtf \
    reference.fa \
    -o pigeon_output

# Produces count matrix and classification
pigeon report pigeon_output_classification.txt
```

## TAMA for Annotation Merge

```bash
# Merge Iso-Seq with reference annotation
# First, convert to TAMA format
tama_format_convert.py \
    -i collapsed.gtf \
    -f gtf \
    -o isoseq.bed

# Create file list
echo -e "isoseq.bed\tcapped\t1\t1" > file_list.txt
echo -e "reference.bed\tcapped\t1\t2" >> file_list.txt

# Merge annotations
tama_merge.py \
    -f file_list.txt \
    -p merged \
    -a 50 \
    -z 50 \
    -m 10
```

## Python Processing

**Goal:** Summarize Iso-Seq clustering results including isoform counts, read support, and transcript lengths.

**Approach:** Parse the cluster report CSV for per-isoform read counts and extract sequence lengths from the HQ FASTA.

```python
import pysam
import pandas as pd

def parse_cluster_report(report_path):
    df = pd.read_csv(report_path)
    isoform_counts = df.groupby('cluster_id').size()
    return isoform_counts

def get_transcript_lengths(fasta_path):
    lengths = {}
    with pysam.FastxFile(fasta_path) as fh:
        for entry in fh:
            lengths[entry.name] = len(entry.sequence)
    return lengths

def summarize_isoseq(cluster_report, hq_fasta):
    counts = parse_cluster_report(cluster_report)
    lengths = get_transcript_lengths(hq_fasta)

    print(f'Total isoforms: {len(counts)}')
    print(f'Median support: {counts.median():.0f} reads')
    print(f'Mean length: {sum(lengths.values())/len(lengths):.0f} bp')

    return counts, lengths
```

## Differential Isoform Usage

```r
library(IsoformSwitchAnalyzeR)

# Import SQANTI3 results
switchList <- importIsoformExpression(
    isoformCountMatrix = 'counts.txt',
    isoformRepExpression = 'tpm.txt',
    designMatrix = design
)

# Add SQANTI3 annotations
switchList <- addORFfromFASTA(
    switchList,
    orfs = 'sqanti_corrected.fasta'
)

# Analyze switching
switchList <- isoformSwitchTestDEXSeq(switchList)

# Extract significant switches
sig_switches <- switchList$isoformSwitchAnalysis[
    switchList$isoformSwitchAnalysis$padj < 0.05,
]
```

## Quality Metrics

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| CCS passes | >3 | 2-3 | <2 |
| Full-length % | >80% | 60-80% | <60% |
| Clustering rate | >90% | 80-90% | <80% |
| FSM % | >50% | 30-50% | <30% |
| Novel isoforms | 10-30% | 30-50% | >50% (suspect) |

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Low full-length % | Primer issues | Check primer sequences |
| High concatemer % | Library prep | Increase SMRTbell cleanup |
| Few FSM | Poor reference | Use comprehensive GTF |
| High NNC % | Novel biology or artifacts | Validate with orthogonal data |
| Low clustering | High diversity | Reduce clustering stringency |

## Docker/Singularity

```bash
# Using PacBio Docker images
docker run -v /data:/data \
    quay.io/biocontainers/isoseq3:4.0.0--h9ee0642_0 \
    isoseq3 cluster /data/refined.bam /data/clustered.bam

# SQANTI3 in Singularity
singularity exec sqanti3.sif \
    sqanti3_qc.py input.fa ref.gtf ref.fa -o output
```

## Related Skills

- long-read-sequencing/basecalling - ONT/PacBio basics
- rna-quantification/alignment-free-quant - Expression analysis
- genome-intervals/gtf-gff-handling - GTF/GFF handling
- differential-expression/timeseries-de - Differential isoform usage
