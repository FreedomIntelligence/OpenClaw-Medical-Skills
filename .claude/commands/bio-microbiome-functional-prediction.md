# bio-microbiome-functional-prediction

> Predict metagenome functional content from 16S rRNA marker gene data using PICRUSt2. Infer KEGG, MetaCyc, and EC abundances from ASV tables. Use when functional profiling is needed from 16S data without shotgun metagenomics sequencing.

## Version Compatibility

Reference examples tested with: Biostrings 2.70+, ggplot2 3.5+, pandas 2.2+, phyloseq 1.46+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Functional Prediction with PICRUSt2

**"Predict functional pathways from my 16S data"** → Infer metagenome functional content from marker gene (16S/ITS) ASV tables using phylogenetic placement and gene content prediction.
- CLI: `picrust2_pipeline.py -s seqs.fna -i table.biom -o output/`

## Prepare Input Files

```r
library(phyloseq)
library(Biostrings)

ps <- readRDS('phyloseq_object.rds')

# Export ASV table (samples as columns)
otu <- as.data.frame(otu_table(ps))
if (!taxa_are_rows(ps)) otu <- t(otu)
write.table(otu, 'asv_table.tsv', sep = '\t', quote = FALSE)

# Export ASV sequences as FASTA
seqs <- refseq(ps)  # Or extract from ASV names if stored there
writeXStringSet(seqs, 'asv_seqs.fasta')
```

## Run PICRUSt2 Pipeline

```bash
# Full pipeline (place sequences, predict functions, metagenome inference)
picrust2_pipeline.py \
    -s asv_seqs.fasta \
    -i asv_table.tsv \
    -o picrust2_output \
    -p 4 \
    --stratified \
    --per_sequence_contrib

# Output files:
# - pathway_abundance.tsv (MetaCyc pathways)
# - KO_metagenome_out/pred_metagenome_unstrat.tsv (KEGG orthologs)
# - EC_metagenome_out/pred_metagenome_unstrat.tsv (EC numbers)
```

## Step-by-Step Pipeline

**Goal:** Predict functional metagenome content from 16S ASVs using the full PICRUSt2 pipeline with explicit control over each step.

**Approach:** Place ASV sequences into a reference tree, predict gene content via hidden-state prediction, infer per-sample metagenome abundances, and reconstruct MetaCyc pathways.

```bash
# 1. Place sequences in reference tree
place_seqs.py -s asv_seqs.fasta -o placed_seqs.tre -p 4

# 2. Hidden state prediction (gene content)
hsp.py -i 16S -t placed_seqs.tre -o marker_nsti_predicted.tsv -m pic -n

# 3. Predict gene families (KO)
hsp.py -i KO -t placed_seqs.tre -o KO_predicted.tsv -m pic

# 4. Metagenome inference
metagenome_pipeline.py \
    -i asv_table.tsv \
    -m marker_nsti_predicted.tsv \
    -f KO_predicted.tsv \
    -o KO_metagenome_out \
    --strat_out

# 5. Pathway inference
pathway_pipeline.py \
    -i KO_metagenome_out/pred_metagenome_contrib.tsv \
    -o pathway_output \
    -p 4
```

## Quality Control: NSTI

```python
import pandas as pd

# NSTI = Nearest Sequenced Taxon Index
# Lower = more reliable prediction (< 2 is acceptable)
nsti = pd.read_csv('marker_nsti_predicted.tsv', sep='\t')
print(f'Mean NSTI: {nsti["metadata_NSTI"].mean():.3f}')
print(f'ASVs with NSTI > 2: {(nsti["metadata_NSTI"] > 2).sum()}')
```

## Analyze Pathway Output

```r
library(ggplot2)

pathways <- read.delim('picrust2_output/pathways_out/path_abun_unstrat.tsv', row.names = 1)
metadata <- read.csv('sample_metadata.csv', row.names = 1)

# Normalize to relative abundance
pathways_rel <- sweep(pathways, 2, colSums(pathways), '/')

# Differential pathway analysis (use ALDEx2 or similar)
library(ALDEx2)
groups <- metadata[colnames(pathways), 'Group']
pathway_aldex <- aldex(as.data.frame(t(pathways)), groups, mc.samples = 128)
```

## Add Pathway Descriptions

```bash
# Map pathway IDs to names
add_descriptions.py \
    -i pathway_abundance.tsv \
    -m METACYC \
    -o pathway_abundance_described.tsv
```

## KEGG Module Analysis

```r
# Analyze KEGG modules instead of individual KOs
ko_table <- read.delim('KO_metagenome_out/pred_metagenome_unstrat.tsv', row.names = 1)

# Use KEGGREST for module mapping
library(KEGGREST)
modules <- keggLink('module', 'ko')
```

## Limitations

- Predictions based on phylogenetic placement
- Novel taxa (high NSTI) have unreliable predictions
- 16S resolution limits species-level accuracy
- Cannot detect horizontal gene transfer events

## Related Skills

- amplicon-processing - Generate ASV input
- metagenomics/functional-profiling - Direct shotgun-based profiling
- pathway-analysis/kegg-pathways - KEGG pathway enrichment
