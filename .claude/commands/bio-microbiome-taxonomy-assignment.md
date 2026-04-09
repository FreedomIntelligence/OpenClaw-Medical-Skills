# bio-microbiome-taxonomy-assignment

> Taxonomic classification of ASVs using reference databases like SILVA, GTDB, or UNITE. Covers naive Bayes classifiers (DADA2, IDTAXA) and exact matching approaches. Use when assigning taxonomy to ASVs after DADA2 amplicon processing.

## Version Compatibility

Reference examples tested with: DADA2 1.30+, QIIME2 2024.2+, phyloseq 1.46+, scanpy 1.10+, scikit-learn 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Taxonomy Assignment

**"Assign taxonomy to my ASVs"** → Classify amplicon sequence variants against reference databases (SILVA, GTDB, UNITE) using naive Bayes or exact-matching approaches for taxonomic annotation.
- R: `dada2::assignTaxonomy()` with SILVA/GTDB reference
- CLI: `qiime feature-classifier classify-sklearn` for QIIME2 workflows

## DADA2 Naive Bayes Classifier

```r
library(dada2)

seqtab_nochim <- readRDS('seqtab_nochim.rds')

# SILVA for 16S (download from https://zenodo.org/record/4587955)
taxa <- assignTaxonomy(seqtab_nochim, 'silva_nr99_v138.1_train_set.fa.gz',
                       multithread = TRUE)

# Add species-level (exact matching)
taxa <- addSpecies(taxa, 'silva_species_assignment_v138.1.fa.gz')

# Check results
head(taxa)
```

## GTDB for 16S

```r
# GTDB-formatted database (better for environmental samples)
taxa_gtdb <- assignTaxonomy(seqtab_nochim, 'GTDB_bac120_arc53_ssu_r220_fullTaxo.fa.gz',
                            multithread = TRUE)
```

## UNITE for ITS (Fungi)

```r
# UNITE database for fungal ITS
taxa_its <- assignTaxonomy(seqtab_nochim, 'sh_general_release_dynamic_25.07.2023.fasta',
                           multithread = TRUE)
```

## QIIME2 Feature Classifier

```bash
# Train classifier (one-time)
qiime feature-classifier fit-classifier-naive-bayes \
    --i-reference-reads silva-138-99-seqs.qza \
    --i-reference-taxonomy silva-138-99-tax.qza \
    --o-classifier silva-138-99-nb-classifier.qza

# Classify ASVs
qiime feature-classifier classify-sklearn \
    --i-classifier silva-138-99-nb-classifier.qza \
    --i-reads rep-seqs.qza \
    --o-classification taxonomy.qza
```

## VSEARCH Exact Matching

```bash
# Faster but requires exact or near-exact matches
vsearch --usearch_global asv_seqs.fasta \
    --db silva_138_SSURef_NR99.fasta \
    --id 0.97 \
    --blast6out taxonomy_vsearch.tsv \
    --top_hits_only
```

## RDP Classifier

```r
library(dada2)

# RDP training set (less detailed than SILVA)
taxa_rdp <- assignTaxonomy(seqtab_nochim, 'rdp_train_set_18.fa.gz',
                           multithread = TRUE)
```

## IDTAXA (DECIPHER) - Often More Accurate

**Goal:** Classify ASVs using DECIPHER's tree-based IDTAXA classifier, which provides more conservative and often more accurate assignments than naive Bayes.

**Approach:** Convert ASV sequences to DNAStringSet, classify against a pre-trained IDTAXA model, and convert the hierarchical output to a standard taxonomy matrix.

```r
library(DECIPHER)

# Load IDTAXA training set (download from http://www2.decipher.codes/Downloads.html)
load('SILVA_SSU_r138_2019.RData')  # Creates 'trainingSet' object

# Convert ASV sequences to DNAStringSet
dna <- DNAStringSet(getSequences(seqtab_nochim))

# Classify with IDTAXA
ids <- IdTaxa(dna, trainingSet, strand = 'top', processors = NULL, verbose = TRUE)

# Convert to matrix format like assignTaxonomy
ranks <- c('domain', 'phylum', 'class', 'order', 'family', 'genus', 'species')
taxa_idtaxa <- t(sapply(ids, function(x) {
    m <- match(ranks, x$rank)
    taxa <- x$taxon[m]
    taxa[startsWith(taxa, 'unclassified_')] <- NA
    taxa
}))
colnames(taxa_idtaxa) <- ranks
```

## Confidence Filtering

```r
# assignTaxonomy returns bootstrap confidence
# Filter low-confidence assignments
taxa_filtered <- taxa
taxa_filtered[taxa_filtered < 80] <- NA  # If using minBoot output

# Or use confidence threshold during assignment
taxa <- assignTaxonomy(seqtab_nochim, 'silva_nr99_v138.1_train_set.fa.gz',
                       minBoot = 80, multithread = TRUE)
```

## Combine into phyloseq

```r
library(phyloseq)

# Create phyloseq object
ps <- phyloseq(otu_table(seqtab_nochim, taxa_are_rows = FALSE),
               tax_table(taxa))

# Add sample metadata
sample_data(ps) <- read.csv('sample_metadata.csv', row.names = 1)

# Rename ASVs for readability
taxa_names(ps) <- paste0('ASV', seq(ntaxa(ps)))
```

## Database Comparison

| Database | Organisms | Taxonomy | Updated |
|----------|-----------|----------|---------|
| SILVA 138.1 | Bacteria, Archaea, Eukaryotes | 7 ranks | 2024 |
| GTDB R220 | Bacteria, Archaea | 7 ranks (genome-based) | 2024 |
| RDP 18 | Bacteria, Archaea | 6 ranks | 2016 |
| UNITE 10.0 | Fungi | 7 ranks | 2024 |
| PR2 5.0 | Protists | 8 ranks | 2024 |

## Related Skills

- amplicon-processing - Generate ASV table for classification
- diversity-analysis - Analyze classified communities
- metagenomics/kraken-classification - Read-level taxonomic classification
