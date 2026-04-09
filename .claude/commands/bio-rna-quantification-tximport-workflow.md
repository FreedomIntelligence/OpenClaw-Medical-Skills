# bio-rna-quantification-tximport-workflow

> Import transcript-level quantifications from Salmon/kallisto into R for gene-level analysis with DESeq2/edgeR using tximport or tximeta. Use when importing transcript counts into R for DESeq2/edgeR.

**Available tools:** Read, Bash

# tximport Workflow

Import transcript-level estimates from Salmon, kallisto, or other quantifiers into R for gene-level differential expression analysis.

## Basic tximport

```r
library(tximport)

# Define sample files
files <- c(
    sample1 = 'sample1_quant/quant.sf',
    sample2 = 'sample2_quant/quant.sf',
    sample3 = 'sample3_quant/quant.sf'
)

# Load transcript-to-gene mapping
tx2gene <- read.csv('tx2gene.csv')  # columns: TXNAME, GENEID

# Import at gene level
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)
```

## Creating tx2gene Mapping

### From GTF (using GenomicFeatures)

```r
library(GenomicFeatures)

txdb <- makeTxDbFromGFF('annotation.gtf')
k <- keys(txdb, keytype = 'TXNAME')
tx2gene <- select(txdb, k, 'GENEID', 'TXNAME')
```

### From Ensembl (using biomaRt)

```r
library(biomaRt)

mart <- useMart('ensembl', dataset = 'hsapiens_gene_ensembl')
tx2gene <- getBM(
    attributes = c('ensembl_transcript_id_version', 'ensembl_gene_id_version'),
    mart = mart
)
colnames(tx2gene) <- c('TXNAME', 'GENEID')
```

### From Salmon quant.sf

```r
quant <- read.table('sample1_quant/quant.sf', header = TRUE)
tx2gene <- data.frame(
    TXNAME = quant$Name,
    GENEID = gsub('\\..*', '', quant$Name)  # Remove version
)
```

## Import Types

### Gene-Level Summarization (Default)

```r
# Summarize transcripts to gene level
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)
# Returns: counts, abundance (TPM), length at gene level
```

### Transcript-Level (No Summarization)

```r
# Keep transcript-level estimates
txi <- tximport(files, type = 'salmon', txOut = TRUE)
# Returns: counts, abundance, length at transcript level
```

### Scaled TPM (for visualization)

```r
# Gene-level TPM
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene,
                countsFromAbundance = 'scaledTPM')
```

## Source-Specific Import

### Salmon

```r
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene)
```

### kallisto

```r
txi <- tximport(files, type = 'kallisto', tx2gene = tx2gene)
```

### RSEM

```r
txi <- tximport(files, type = 'rsem', tx2gene = tx2gene)
```

### StringTie

```r
txi <- tximport(files, type = 'stringtie', tx2gene = tx2gene)
```

## Using with DESeq2

```r
library(DESeq2)

# Create sample metadata
coldata <- data.frame(
    condition = factor(c('control', 'control', 'treated', 'treated')),
    row.names = names(files)
)

# Create DESeqDataSet from tximport
dds <- DESeqDataSetFromTximport(txi, colData = coldata, design = ~ condition)

# Filter low counts
dds <- dds[rowSums(counts(dds)) >= 10, ]

# Run DESeq2
dds <- DESeq(dds)
res <- results(dds)
```

## Using with edgeR

```r
library(edgeR)

# Create DGEList with offset
cts <- txi$counts
normMat <- txi$length
normMat <- normMat / exp(rowMeans(log(normMat)))
o <- log(calcNormFactors(cts / normMat)) + log(colSums(cts / normMat))

y <- DGEList(cts)
y$offset <- t(t(log(normMat)) + o)

# Continue with edgeR analysis
y <- estimateDisp(y, design)
```

## tximeta: Metadata-Aware Import

tximeta automatically attaches transcript and gene information from the original annotation.

```r
library(tximeta)

# First time: link transcriptome to annotation
makeLinkedTxome(
    indexDir = 'salmon_index',
    source = 'Ensembl',
    organism = 'Homo sapiens',
    release = '110',
    genome = 'GRCh38',
    fasta = 'transcripts.fa',
    gtf = 'annotation.gtf'
)

# Import with full metadata
coldata <- data.frame(
    files = files,
    names = names(files),
    condition = c('control', 'control', 'treated', 'treated')
)

se <- tximeta(coldata)

# Summarize to gene level
gse <- summarizeToGene(se)

# Convert to DESeqDataSet
dds <- DESeqDataSet(gse, design = ~ condition)
```

## tximport Output Structure

```r
names(txi)
# [1] "abundance"           "counts"              "length"
# [4] "countsFromAbundance"

# abundance: TPM values (genes x samples)
# counts: estimated counts (genes x samples)
# length: effective gene lengths (genes x samples)
```

## Handling Version Numbers

```r
# Remove version from transcript IDs
tx2gene$TXNAME <- gsub('\\.\\d+$', '', tx2gene$TXNAME)

# Or ignore version during import
txi <- tximport(files, type = 'salmon', tx2gene = tx2gene,
                ignoreTxVersion = TRUE, ignoreAfterBar = TRUE)
```

## Related Skills

- rna-quantification/alignment-free-quant - Upstream Salmon/kallisto
- differential-expression/deseq2-basics - DESeq2 analysis
- differential-expression/edger-basics - edgeR analysis
- genome-intervals/gtf-gff-handling - GTF annotation parsing
