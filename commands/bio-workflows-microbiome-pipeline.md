# bio-workflows-microbiome-pipeline

> End-to-end 16S amplicon workflow from FASTQ reads to differential abundance. Orchestrates DADA2 ASV inference, taxonomy assignment, diversity analysis, and compositional testing with ALDEx2. Use when processing 16S/ITS amplicon data.

**Available tools:** Read, Bash

# Microbiome Pipeline

## Pipeline Overview

```
Paired-End FASTQ (16S V4)
           │
           ▼
┌──────────────────────────────────────────────────┐
│              microbiome-pipeline                 │
├──────────────────────────────────────────────────┤
│  1. Quality Filtering (DADA2 filterAndTrim)     │
│  2. Error Learning & Denoising                   │
│  3. Merge Pairs & Remove Chimeras                │
│  4. Taxonomy Assignment (SILVA)                  │
│  5. Create phyloseq Object                       │
│  6. Alpha/Beta Diversity                         │
│  7. Differential Abundance (ALDEx2)              │
│  8. Visualization & Export                       │
└──────────────────────────────────────────────────┘
           │
           ▼
ASV Table + Taxonomy + Diversity Plots + Differential Taxa
```

## Complete R Workflow

```r
library(dada2)
library(phyloseq)
library(ALDEx2)
library(vegan)
library(ggplot2)

# === CONFIGURATION ===
path <- 'raw_reads'
silva_train <- 'silva_nr99_v138.1_train_set.fa.gz'
silva_species <- 'silva_species_assignment_v138.1.fa.gz'
metadata_file <- 'sample_metadata.csv'

# === 1. READ FILES ===
fnFs <- sort(list.files(path, pattern = '_R1_001.fastq.gz', full.names = TRUE))
fnRs <- sort(list.files(path, pattern = '_R2_001.fastq.gz', full.names = TRUE))
sample_names <- sapply(strsplit(basename(fnFs), '_'), `[`, 1)

# Setup filtered files
filtFs <- file.path('filtered', paste0(sample_names, '_F_filt.fastq.gz'))
filtRs <- file.path('filtered', paste0(sample_names, '_R_filt.fastq.gz'))

# === 2. FILTER & TRIM ===
out <- filterAndTrim(fnFs, filtFs, fnRs, filtRs,
                     truncLen = c(240, 160), maxN = 0, maxEE = c(2, 2),
                     truncQ = 2, rm.phix = TRUE, compress = TRUE, multithread = TRUE)

# === 3. LEARN ERRORS & DENOISE ===
errF <- learnErrors(filtFs, multithread = TRUE)
errR <- learnErrors(filtRs, multithread = TRUE)
dadaFs <- dada(filtFs, err = errF, multithread = TRUE)
dadaRs <- dada(filtRs, err = errR, multithread = TRUE)

# === 4. MERGE & CHIMERAS ===
mergers <- mergePairs(dadaFs, filtFs, dadaRs, filtRs, verbose = TRUE)
seqtab <- makeSequenceTable(mergers)
seqtab_nochim <- removeBimeraDenovo(seqtab, method = 'consensus', multithread = TRUE)

# === 5. ASSIGN TAXONOMY ===
taxa <- assignTaxonomy(seqtab_nochim, silva_train, multithread = TRUE)
taxa <- addSpecies(taxa, silva_species)

# === 6. BUILD PHYLOGENETIC TREE (for UniFrac) ===
library(DECIPHER)
library(phangorn)

seqs <- getSequences(seqtab_nochim)
names(seqs) <- paste0('ASV', seq_along(seqs))
alignment <- AlignSeqs(DNAStringSet(seqs), anchor = NA, processors = NULL)
phang_align <- phyDat(as(alignment, 'matrix'), type = 'DNA')
dm <- dist.ml(phang_align)
tree <- NJ(dm)
tree <- midpoint(ladderize(tree))

# === 7. CREATE PHYLOSEQ ===
metadata <- read.csv(metadata_file, row.names = 1)
ps <- phyloseq(otu_table(seqtab_nochim, taxa_are_rows = FALSE),
               tax_table(taxa), sample_data(metadata), phy_tree(tree))
taxa_names(ps) <- paste0('ASV', seq(ntaxa(ps)))

# === 8. DIVERSITY ===
# Alpha diversity (including Faith's PD with tree)
library(picante)
alpha_div <- estimate_richness(ps, measures = c('Observed', 'Shannon', 'Simpson'))
faith_pd <- pd(t(otu_table(ps)), phy_tree(ps), include.root = TRUE)
alpha_div$PD <- faith_pd$PD
alpha_div$Group <- sample_data(ps)$Group

# Beta diversity (Bray-Curtis and UniFrac)
bray_dist <- phyloseq::distance(ps, method = 'bray')
unifrac_dist <- UniFrac(ps, weighted = TRUE)
pcoa_bray <- ordinate(ps, method = 'PCoA', distance = bray_dist)
pcoa_unifrac <- ordinate(ps, method = 'PCoA', distance = unifrac_dist)

# PERMANOVA on both metrics
meta_df <- data.frame(sample_data(ps))
permanova_bray <- adonis2(bray_dist ~ Group, data = meta_df, permutations = 999)
permanova_unifrac <- adonis2(unifrac_dist ~ Group, data = meta_df, permutations = 999)

# === 9. DIFFERENTIAL ABUNDANCE ===
# Filter low-abundance taxa
ps_filt <- filter_taxa(ps, function(x) sum(x > 0) > 0.1 * nsamples(ps), TRUE)

# ALDEx2
otu <- as.data.frame(t(otu_table(ps_filt)))
groups <- as.character(sample_data(ps_filt)$Group)
aldex_results <- aldex(otu, groups, mc.samples = 128, test = 'welch', effect = TRUE)
aldex_results$significant <- aldex_results$we.eBH < 0.05 & abs(aldex_results$effect) > 1

# === 10. OUTPUT ===
cat('Pipeline complete!\n')
cat('  ASVs:', ntaxa(ps), '\n')
cat('  Samples:', nsamples(ps), '\n')
cat('  PERMANOVA R2:', round(permanova$R2[1], 3), 'p =', permanova$`Pr(>F)`[1], '\n')
cat('  Differential taxa:', sum(aldex_results$significant), '\n')
```

## QC Checkpoints

| Stage | Check | Expected | Action if Failed |
|-------|-------|----------|------------------|
| Filter | >70% reads pass | >70% | Adjust truncLen/maxEE |
| Merge | >80% pairs merge | >80% | Check amplicon length |
| Chimera | <25% chimeras | <25% | Check PCR cycles |
| Taxonomy | >80% genus assigned | >80% | Try different database |
| Rarefaction | Curves plateau | Plateau | Increase depth |
| PERMANOVA | p < 0.05 | p < 0.05 | Check experimental design |

## Output Files

```
microbiome_results/
├── phyloseq_object.rds      # Complete phyloseq
├── asv_table.csv            # ASV counts
├── taxonomy.csv             # Taxonomic assignments
├── alpha_diversity.csv      # Per-sample metrics
├── aldex2_results.csv       # Differential taxa
├── read_tracking.csv        # Reads per pipeline stage
├── plots/
│   ├── quality_profiles.pdf
│   ├── alpha_diversity.pdf
│   ├── beta_diversity_pcoa.pdf
│   ├── taxonomic_barplot.pdf
│   └── aldex2_effect_plot.pdf
```

## Workflow Variants

### ITS Fungal Workflow
```r
# Key differences for ITS:
# 1. No truncLen (variable length amplicons)
out <- filterAndTrim(fnFs, filtFs, fnRs, filtRs, maxN = 0, maxEE = c(2, 2),
                     truncQ = 2, minLen = 50, rm.phix = TRUE, multithread = TRUE)

# 2. Use UNITE database
taxa <- assignTaxonomy(seqtab_nochim, 'sh_general_release_dynamic_25.07.2023.fasta',
                       multithread = TRUE)
```

### Different 16S Regions
```r
# V3-V4 (~460bp): truncLen = c(280, 200)
# V4 (~253bp): truncLen = c(240, 160)
# V1-V3 (~500bp): truncLen = c(260, 220)
```

### GTDB Taxonomy
```r
# For environmental samples, GTDB may be more accurate
taxa <- assignTaxonomy(seqtab_nochim, 'GTDB_bac120_arc53_ssu_r214_fullTaxo.fa.gz',
                       multithread = TRUE)
```

## Related Skills

- microbiome/amplicon-processing - DADA2 details
- microbiome/taxonomy-assignment - Database options, IDTAXA
- microbiome/diversity-analysis - Diversity metrics, Faith's PD
- microbiome/differential-abundance - ALDEx2, ANCOM-BC2
- microbiome/functional-prediction - PICRUSt2 functional analysis
