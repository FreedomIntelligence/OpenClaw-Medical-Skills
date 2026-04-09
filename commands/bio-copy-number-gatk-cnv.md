# bio-copy-number-gatk-cnv

> Call copy number variants using GATK best practices workflow. Supports both somatic (tumor-normal) and germline CNV detection from WGS or WES data. Use when following GATK best practices or integrating CNV calling with other GATK variant pipelines.

## Version Compatibility

Reference examples tested with: GATK 4.5+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# GATK CNV Workflow

**"Call CNVs using GATK best practices"** → Collect read counts, build a panel of normals, denoise tumor coverage, model segments with allelic counts, and call copy ratio states.
- CLI: `gatk CollectReadCounts` → `gatk DenoiseReadCounts` → `gatk ModelSegments` → `gatk CallCopyRatioSegments`

## Somatic CNV Workflow Overview

```
1. PreprocessIntervals → intervals.interval_list
2. CollectReadCounts → sample.counts.hdf5
3. CreateReadCountPanelOfNormals → pon.hdf5
4. DenoiseReadCounts → sample.denoised.tsv
5. CollectAllelicCounts → sample.allelicCounts.tsv
6. ModelSegments → sample.modelFinal.seg
7. CallCopyRatioSegments → sample.called.seg
```

## Step 1: Preprocess Intervals

**Goal:** Prepare genomic intervals for read counting, handling both WES and WGS modes.

**Approach:** Use PreprocessIntervals to bin or merge target intervals with appropriate padding.

```bash
# For WES/targeted
gatk PreprocessIntervals \
    -R reference.fa \
    -L targets.interval_list \
    --bin-length 0 \
    --interval-merging-rule OVERLAPPING_ONLY \
    -O preprocessed.interval_list

# For WGS
gatk PreprocessIntervals \
    -R reference.fa \
    --bin-length 1000 \
    --padding 0 \
    -O wgs.interval_list
```

## Step 2: Collect Read Counts

**Goal:** Count reads per interval for each sample.

**Approach:** Run CollectReadCounts on each BAM against the preprocessed intervals.

```bash
# For each sample
gatk CollectReadCounts \
    -R reference.fa \
    -I sample.bam \
    -L preprocessed.interval_list \
    --interval-merging-rule OVERLAPPING_ONLY \
    -O sample.counts.hdf5
```

## Step 3: Create Panel of Normals

**Goal:** Build a reference panel from multiple normal samples for denoising.

**Approach:** Combine normal sample count HDF5 files into a single panel-of-normals using PCA-based denoising.

```bash
# Combine multiple normal samples
gatk CreateReadCountPanelOfNormals \
    -I normal1.counts.hdf5 \
    -I normal2.counts.hdf5 \
    -I normal3.counts.hdf5 \
    --minimum-interval-median-percentile 5.0 \
    -O cnv_pon.hdf5
```

## Step 4: Denoise Read Counts

**Goal:** Remove systematic noise from tumor read counts using the panel of normals.

**Approach:** Apply DenoiseReadCounts with the PoN to produce standardized and denoised copy ratio profiles.

```bash
# Using panel of normals
gatk DenoiseReadCounts \
    -I tumor.counts.hdf5 \
    --count-panel-of-normals cnv_pon.hdf5 \
    --standardized-copy-ratios tumor.standardized.tsv \
    --denoised-copy-ratios tumor.denoised.tsv
```

## Step 5: Collect Allelic Counts

**Goal:** Capture allele-specific information at known heterozygous SNP sites for LOH detection.

**Approach:** Run CollectAllelicCounts against common SNP sites to generate allelic count profiles.

```bash
# From known SNP sites (for LOH detection)
gatk CollectAllelicCounts \
    -R reference.fa \
    -I tumor.bam \
    -L common_snps.vcf \
    -O tumor.allelicCounts.tsv
```

## Step 6: Model Segments

**Goal:** Jointly segment copy ratio and allelic data to identify CNV regions.

**Approach:** Run ModelSegments with denoised ratios and allelic counts from both tumor and matched normal.

```bash
# Somatic with matched normal allelic counts
gatk ModelSegments \
    --denoised-copy-ratios tumor.denoised.tsv \
    --allelic-counts tumor.allelicCounts.tsv \
    --normal-allelic-counts normal.allelicCounts.tsv \
    --output-prefix tumor \
    -O results/

# Output files: tumor.cr.seg, tumor.modelFinal.seg, tumor.hets.tsv
```

## Step 7: Call Copy Ratio Segments

**Goal:** Assign amplification, deletion, or neutral calls to each segment.

**Approach:** Apply CallCopyRatioSegments to convert continuous log2 ratios into discrete CN states.

```bash
gatk CallCopyRatioSegments \
    -I results/tumor.cr.seg \
    -O results/tumor.called.seg
```

## Plotting

**Goal:** Visualize denoised copy ratios and modeled segments with allelic information.

**Approach:** Use GATK PlotDenoisedCopyRatios and PlotModeledSegments to generate standardized plots.

```bash
# Plot copy ratios and segments
gatk PlotDenoisedCopyRatios \
    --standardized-copy-ratios tumor.standardized.tsv \
    --denoised-copy-ratios tumor.denoised.tsv \
    --sequence-dictionary reference.dict \
    --minimum-contig-length 46709983 \
    --output-prefix tumor \
    -O plots/

# Plot segments with allelic information
gatk PlotModeledSegments \
    --denoised-copy-ratios tumor.denoised.tsv \
    --allelic-counts results/tumor.hets.tsv \
    --segments results/tumor.modelFinal.seg \
    --sequence-dictionary reference.dict \
    --minimum-contig-length 46709983 \
    --output-prefix tumor \
    -O plots/
```

## Germline CNV Workflow

```bash
# For germline: use cohort mode
# 1. Collect counts (same as above)

# 2. Determine contig ploidy
gatk DetermineGermlineContigPloidy \
    -I sample1.counts.hdf5 \
    -I sample2.counts.hdf5 \
    --model cohort_ploidy_model \
    --contig-ploidy-priors ploidy_priors.tsv \
    -O ploidy-calls/

# 3. Call germline CNVs
gatk GermlineCNVCaller \
    --run-mode COHORT \
    -I sample1.counts.hdf5 \
    -I sample2.counts.hdf5 \
    --contig-ploidy-calls ploidy-calls/ploidy_calls \
    --annotated-intervals annotated_intervals.tsv \
    --output-prefix cohort \
    -O germline_cnv_calls/

# 4. Post-process calls per sample
gatk PostprocessGermlineCNVCalls \
    --calls-shard-path germline_cnv_calls/cohort-calls \
    --model-shard-path germline_cnv_calls/cohort-model \
    --sample-index 0 \
    --contig-ploidy-calls ploidy-calls/ploidy_calls \
    --sequence-dictionary reference.dict \
    --output-genotyped-intervals sample1.genotyped.tsv \
    --output-denoised-copy-ratios sample1.denoised.tsv \
    -O sample1_segments.vcf
```

## Complete Somatic Pipeline Script

```bash
#!/bin/bash
REFERENCE=reference.fa
INTERVALS=targets.interval_list
PON=cnv_pon.hdf5
SNP_SITES=common_snps.vcf
TUMOR=$1
NORMAL=$2
OUTDIR=$3

mkdir -p $OUTDIR

# Collect read counts
gatk CollectReadCounts -R $REFERENCE -I $TUMOR -L $INTERVALS \
    -O $OUTDIR/tumor.counts.hdf5
gatk CollectReadCounts -R $REFERENCE -I $NORMAL -L $INTERVALS \
    -O $OUTDIR/normal.counts.hdf5

# Denoise
gatk DenoiseReadCounts -I $OUTDIR/tumor.counts.hdf5 \
    --count-panel-of-normals $PON \
    --standardized-copy-ratios $OUTDIR/tumor.standardized.tsv \
    --denoised-copy-ratios $OUTDIR/tumor.denoised.tsv

# Allelic counts
gatk CollectAllelicCounts -R $REFERENCE -I $TUMOR -L $SNP_SITES \
    -O $OUTDIR/tumor.allelicCounts.tsv
gatk CollectAllelicCounts -R $REFERENCE -I $NORMAL -L $SNP_SITES \
    -O $OUTDIR/normal.allelicCounts.tsv

# Model and call
gatk ModelSegments \
    --denoised-copy-ratios $OUTDIR/tumor.denoised.tsv \
    --allelic-counts $OUTDIR/tumor.allelicCounts.tsv \
    --normal-allelic-counts $OUTDIR/normal.allelicCounts.tsv \
    --output-prefix tumor -O $OUTDIR/

gatk CallCopyRatioSegments -I $OUTDIR/tumor.cr.seg -O $OUTDIR/tumor.called.seg
```

## Key Output Files

| File | Description |
|------|-------------|
| .counts.hdf5 | Raw read counts per interval |
| .denoised.tsv | Denoised log2 copy ratios |
| .modelFinal.seg | Segmented copy ratios with confidence |
| .called.seg | Final called segments with CN state |
| .hets.tsv | Heterozygous SNP allelic counts |

## Related Skills

- copy-number/cnvkit-analysis - Alternative CNV caller
- copy-number/cnv-visualization - Plotting results
- alignment-files/bam-statistics - Input BAM QC
- variant-calling/variant-calling - SNP calling for allelic counts
