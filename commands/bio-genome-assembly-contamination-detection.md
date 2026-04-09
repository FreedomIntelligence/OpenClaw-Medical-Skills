# bio-genome-assembly-contamination-detection

> Detect contamination and assess genome quality using CheckM, CheckM2, GTDB-Tk, and GUNC for metagenome-assembled genomes and isolate assemblies. Use when checking assemblies for contamination.

**Available tools:** Read, Bash

# Contamination Detection

## CheckM2 (Recommended)

```bash
# Run CheckM2 on single genome
checkm2 predict --input assembly.fa --output-directory checkm2_output --threads 16

# Run on multiple genomes (directory of FASTAs)
checkm2 predict --input genomes/ --output-directory checkm2_output \
    --threads 16 --extension fa

# Output: quality_report.tsv with Completeness, Contamination, Coding_Density
```

## Interpret CheckM2 Results

```bash
# quality_report.tsv columns:
# Name, Completeness, Contamination, Completeness_Model_Used,
# Translation_Table_Used, Coding_Density, Contig_N50, Average_Gene_Length,
# Genome_Size, GC_Content, Total_Coding_Sequences

# Filter high-quality genomes (MIMAG standards)
awk -F'\t' 'NR==1 || ($2 > 90 && $3 < 5)' quality_report.tsv > high_quality_mags.tsv

# Medium quality
awk -F'\t' 'NR==1 || ($2 >= 50 && $3 < 10)' quality_report.tsv > medium_quality_mags.tsv
```

## CheckM (Original)

```bash
# Run CheckM lineage workflow
checkm lineage_wf -t 16 -x fa genomes/ checkm_output/

# Generate summary
checkm qa checkm_output/lineage.ms checkm_output/ -o 2 -f checkm_summary.tsv --tab_table

# Extended report with marker genes
checkm qa checkm_output/lineage.ms checkm_output/ -o 2 --tab_table \
    -f checkm_extended.tsv
```

## CheckM Plots

```bash
# Completeness vs Contamination plot
checkm bin_qa_plot -x fa checkm_output/ genomes/ plots/

# GC and coding density
checkm coding_plot -x fa checkm_output/ genomes/ plots/

# Marker gene positions
checkm marker_plot -x fa checkm_output/ genomes/ plots/
```

## GTDB-Tk Taxonomic Classification

```bash
# Classify genomes
gtdbtk classify_wf --genome_dir genomes/ --out_dir gtdbtk_output \
    --extension fa --cpus 16

# With species-level ANI
gtdbtk classify_wf --genome_dir genomes/ --out_dir gtdbtk_output \
    --extension fa --cpus 16 --skip_ani_screen

# Output files:
# gtdbtk.bac120.summary.tsv - bacterial classifications
# gtdbtk.ar53.summary.tsv - archaeal classifications
```

## GTDB-Tk De Novo Workflow

```bash
# When genomes may include novel taxa
gtdbtk de_novo_wf --genome_dir genomes/ --out_dir gtdbtk_denovo \
    --bacteria --extension fa --cpus 16
```

## GUNC Chimerism Detection

```bash
# Run GUNC
gunc run -d genomes/ -o gunc_output -t 16 -e .fa

# Output: GUNC.progenomes_2.1.maxCSS_level.tsv
# Key columns: pass.GUNC (true/false), contamination_portion, clade_separation_score

# Filter chimeric genomes
awk -F'\t' '$8 == "False"' GUNC.progenomes_2.1.maxCSS_level.tsv > chimeric_genomes.tsv
```

## GUNC Interpretation

```bash
# GUNC flags genomes as chimeric if:
# - clade_separation_score (CSS) > 0.45
# - contamination_portion > 0.05
# - reference_representation_score > 0.5

# Combine with CheckM2 for full QC
join -t$'\t' -1 1 -2 1 \
    <(sort checkm2_output/quality_report.tsv) \
    <(sort gunc_output/GUNC.progenomes_2.1.maxCSS_level.tsv) \
    > combined_qc.tsv
```

## Comprehensive QC Pipeline

```bash
#!/bin/bash
GENOMES_DIR=$1
OUTPUT_DIR=$2
THREADS=${3:-16}

mkdir -p "$OUTPUT_DIR"

# Run CheckM2
echo "Running CheckM2..."
checkm2 predict --input "$GENOMES_DIR" --output-directory "$OUTPUT_DIR/checkm2" \
    --threads "$THREADS" --extension fa

# Run GUNC
echo "Running GUNC..."
gunc run -d "$GENOMES_DIR" -o "$OUTPUT_DIR/gunc" -t "$THREADS" -e .fa

# Run GTDB-Tk
echo "Running GTDB-Tk..."
gtdbtk classify_wf --genome_dir "$GENOMES_DIR" --out_dir "$OUTPUT_DIR/gtdbtk" \
    --extension fa --cpus "$THREADS"

echo "QC complete!"
```

## Filter by Quality Standards

```python
import pandas as pd

checkm = pd.read_csv('checkm2_output/quality_report.tsv', sep='\t')
gunc = pd.read_csv('gunc_output/GUNC.progenomes_2.1.maxCSS_level.tsv', sep='\t')

merged = checkm.merge(gunc, left_on='Name', right_on='genome', how='left')

# MIMAG High Quality: >90% complete, <5% contamination, not chimeric
hq = merged[(merged['Completeness'] > 90) &
            (merged['Contamination'] < 5) &
            (merged['pass.GUNC'] == True)]

# MIMAG Medium Quality: >50% complete, <10% contamination
mq = merged[(merged['Completeness'] >= 50) &
            (merged['Contamination'] < 10)]

hq.to_csv('high_quality_genomes.tsv', sep='\t', index=False)
mq.to_csv('medium_quality_genomes.tsv', sep='\t', index=False)
```

## Remove Contamination

```bash
# Use MAGpurify to remove contaminating contigs
magpurify phylo-markers genome.fa magpurify_output
magpurify clade-markers genome.fa magpurify_output
magpurify conspecific genome.fa magpurify_output
magpurify tetra-freq genome.fa magpurify_output
magpurify gc-content genome.fa magpurify_output
magpurify known-contam genome.fa magpurify_output
magpurify clean-bin genome.fa magpurify_output cleaned_genome.fa
```

## Detect Foreign Contigs

```bash
# Contig-level taxonomy with CAT
CAT contigs -c assembly.fa -d CAT_database -t CAT_taxonomy \
    -o cat_output -n 16

# Parse results
CAT add_names -i cat_output.contig2classification.txt \
    -o cat_output.contig2classification.named.txt \
    -t CAT_taxonomy --only_official

# Flag contigs with different taxonomy than majority
awk -F'\t' '{print $1, $NF}' cat_output.contig2classification.named.txt | \
    sort | uniq -c | sort -rn
```

## Decontaminate with BlobTools

```bash
# Create BlobDB
blobtools create -i assembly.fa -b aligned.bam -t blast_hits.txt \
    -o blobtools_output

# Generate plots
blobtools plot -i blobtools_output.blobDB.json

# Filter by taxonomy
blobtools view -i blobtools_output.blobDB.json -r all -o filtered
```

## Related Skills

- genome-assembly/assembly-qc - BUSCO and other QC
- genome-assembly/long-read-assembly - Assembly methods
- metagenomics/taxonomic-profiling - Metagenome analysis
