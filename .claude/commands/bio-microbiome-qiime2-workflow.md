# bio-microbiome-qiime2-workflow

> QIIME2 command-line workflow for 16S/ITS amplicon analysis. Alternative to DADA2/phyloseq R workflow with built-in provenance tracking. Use when preferring CLI over R, needing reproducible provenance, or working within QIIME2 ecosystem.

## Version Compatibility

Reference examples tested with: DADA2 1.30+, MAFFT 7.520+, QIIME2 2024.2+, phyloseq 1.46+, scanpy 1.10+, scikit-learn 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# QIIME2 Amplicon Workflow

**"Run my amplicon analysis through QIIME2"** → Process 16S/ITS amplicon data end-to-end using the QIIME2 CLI with built-in provenance tracking, from import through denoising, taxonomy, and diversity analysis.
- CLI: `qiime dada2 denoise-paired`, `qiime diversity core-metrics-phylogenetic`

## Import Data

```bash
# Import paired-end FASTQ with manifest
qiime tools import \
    --type 'SampleData[PairedEndSequencesWithQuality]' \
    --input-path manifest.tsv \
    --output-path demux.qza \
    --input-format PairedEndFastqManifestPhred33V2

# View demultiplexed summary
qiime demux summarize \
    --i-data demux.qza \
    --o-visualization demux.qzv
```

## Denoise with DADA2

```bash
# DADA2 denoising (creates ASV table + representative sequences)
qiime dada2 denoise-paired \
    --i-demultiplexed-seqs demux.qza \
    --p-trunc-len-f 240 \
    --p-trunc-len-r 160 \
    --p-trim-left-f 0 \
    --p-trim-left-r 0 \
    --p-max-ee-f 2 \
    --p-max-ee-r 2 \
    --p-n-threads 0 \
    --o-table table.qza \
    --o-representative-sequences rep-seqs.qza \
    --o-denoising-stats denoising-stats.qza

# View denoising stats
qiime metadata tabulate \
    --m-input-file denoising-stats.qza \
    --o-visualization denoising-stats.qzv
```

## Alternative: Deblur Denoising

```bash
# Quality filter first
qiime quality-filter q-score \
    --i-demux demux.qza \
    --o-filtered-sequences demux-filtered.qza \
    --o-filter-stats filter-stats.qza

# Deblur denoise
qiime deblur denoise-16S \
    --i-demultiplexed-seqs demux-filtered.qza \
    --p-trim-length 250 \
    --p-sample-stats \
    --o-representative-sequences rep-seqs-deblur.qza \
    --o-table table-deblur.qza \
    --o-stats deblur-stats.qza
```

## Taxonomy Assignment

```bash
# Download pre-trained classifier (SILVA 138)
# wget https://data.qiime2.org/2024.5/common/silva-138-99-nb-classifier.qza

# Classify with sklearn naive Bayes
qiime feature-classifier classify-sklearn \
    --i-classifier silva-138-99-nb-classifier.qza \
    --i-reads rep-seqs.qza \
    --o-classification taxonomy.qza

# Visualize taxonomy
qiime metadata tabulate \
    --m-input-file taxonomy.qza \
    --o-visualization taxonomy.qzv

# Taxonomic barplot
qiime taxa barplot \
    --i-table table.qza \
    --i-taxonomy taxonomy.qza \
    --m-metadata-file metadata.tsv \
    --o-visualization taxa-barplot.qzv
```

## Phylogenetic Tree

```bash
# Build phylogeny with MAFFT + FastTree
qiime phylogeny align-to-tree-mafft-fasttree \
    --i-sequences rep-seqs.qza \
    --o-alignment aligned-rep-seqs.qza \
    --o-masked-alignment masked-aligned-rep-seqs.qza \
    --o-tree unrooted-tree.qza \
    --o-rooted-tree rooted-tree.qza
```

## Diversity Analysis

```bash
# Core metrics (alpha + beta diversity)
qiime diversity core-metrics-phylogenetic \
    --i-phylogeny rooted-tree.qza \
    --i-table table.qza \
    --p-sampling-depth 10000 \
    --m-metadata-file metadata.tsv \
    --output-dir core-metrics-results

# Alpha diversity significance
qiime diversity alpha-group-significance \
    --i-alpha-diversity core-metrics-results/shannon_vector.qza \
    --m-metadata-file metadata.tsv \
    --o-visualization shannon-significance.qzv

# Beta diversity significance (PERMANOVA)
qiime diversity beta-group-significance \
    --i-distance-matrix core-metrics-results/weighted_unifrac_distance_matrix.qza \
    --m-metadata-file metadata.tsv \
    --m-metadata-column Group \
    --p-method permanova \
    --o-visualization weighted-unifrac-permanova.qzv
```

## Differential Abundance (ANCOM)

**Goal:** Identify taxa with significantly different abundances between groups using QIIME2's ANCOM implementation.

**Approach:** Collapse the feature table to genus level, add pseudocounts for log-ratio computation, and run ANCOM to test for differential abundance per taxon.

```bash
# Collapse to genus level
qiime taxa collapse \
    --i-table table.qza \
    --i-taxonomy taxonomy.qza \
    --p-level 6 \
    --o-collapsed-table table-l6.qza

# Add pseudocount and run ANCOM
qiime composition add-pseudocount \
    --i-table table-l6.qza \
    --o-composition-table comp-table-l6.qza

qiime composition ancom \
    --i-table comp-table-l6.qza \
    --m-metadata-file metadata.tsv \
    --m-metadata-column Group \
    --o-visualization ancom-l6.qzv
```

## Export to R/Python

```bash
# Export feature table to BIOM
qiime tools export \
    --input-path table.qza \
    --output-path exported

# Convert BIOM to TSV
biom convert \
    -i exported/feature-table.biom \
    -o feature-table.tsv \
    --to-tsv

# Export taxonomy
qiime tools export \
    --input-path taxonomy.qza \
    --output-path exported

# Export tree
qiime tools export \
    --input-path rooted-tree.qza \
    --output-path exported
```

## Manifest File Format

```
# manifest.tsv (tab-separated)
sample-id	forward-absolute-filepath	reverse-absolute-filepath
sample1	/path/to/sample1_R1.fastq.gz	/path/to/sample1_R2.fastq.gz
sample2	/path/to/sample2_R1.fastq.gz	/path/to/sample2_R2.fastq.gz
```

## Metadata File Format

```
# metadata.tsv (tab-separated)
sample-id	Group	Timepoint
sample1	Treatment	Day0
sample2	Control	Day0
sample3	Treatment	Day7
```

## Related Skills

- amplicon-processing - DADA2 R workflow alternative
- taxonomy-assignment - More database options
- diversity-analysis - phyloseq R alternative
- differential-abundance - ALDEx2/ANCOM-BC in R
