# bio-copy-number-cnv-annotation

> Annotate CNVs with genes, pathways, and clinical significance. Use when interpreting CNV calls or identifying affected genes from copy number analysis.

## Version Compatibility

Reference examples tested with: bedtools 2.31+, pandas 2.2+, pybedtools 0.9+, pysam 0.22+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# CNV Annotation

**"Annotate my CNV calls with gene names"** → Overlap CNV segments with gene annotations, clinical databases, and pathway information to identify affected genes and assess clinical significance.
- CLI: `bedtools intersect -a cnvs.bed -b genes.bed`
- Python: `pybedtools.BedTool().intersect()`

## Annotate with Gene Names (bedtools)

```bash
# Convert CNV segments to BED
awk 'NR>1 {print $1"\t"$2"\t"$3"\t"$5"\t"$6}' sample.cns > sample.cnv.bed

# Intersect with gene annotations
bedtools intersect -a sample.cnv.bed -b genes.bed -wa -wb > cnv_genes.txt

# Get genes overlapping CNVs
bedtools intersect -a genes.bed -b sample.cnv.bed -u > affected_genes.bed
```

## CNVkit Gene Annotation

```bash
# Annotate during analysis
cnvkit.py batch tumor.bam --normal normal.bam \
    --targets targets.bed \
    --annotate refFlat.txt \
    --fasta reference.fa \
    -o results/

# Genes are included in output CNS file
```

## Python: Comprehensive Annotation

**Goal:** Annotate CNV segments with all overlapping genes using interval intersection.

**Approach:** Convert CNV segments and gene annotations to BedTool objects, intersect to find overlapping genes, and aggregate gene names per CNV segment.

```python
import pandas as pd
import pybedtools as pbt

def annotate_cnvs(cns_file, gene_bed, output=None):
    '''Annotate CNV segments with overlapping genes.'''
    cns = pd.read_csv(cns_file, sep='\t')

    # Create BED from segments
    cns_bed = pbt.BedTool.from_dataframe(
        cns[['chromosome', 'start', 'end', 'log2']].rename(
            columns={'chromosome': 'chrom'}))

    genes = pbt.BedTool(gene_bed)

    # Intersect
    intersect = cns_bed.intersect(genes, wa=True, wb=True)

    # Parse results
    results = []
    for interval in intersect:
        results.append({
            'chrom': interval[0],
            'start': int(interval[1]),
            'end': int(interval[2]),
            'log2': float(interval[3]),
            'gene_chrom': interval[4],
            'gene_start': int(interval[5]),
            'gene_end': int(interval[6]),
            'gene_name': interval[7] if len(interval) > 7 else 'NA'
        })

    df = pd.DataFrame(results)

    # Aggregate genes per CNV
    cnv_genes = df.groupby(['chrom', 'start', 'end', 'log2'])['gene_name'].apply(
        lambda x: ','.join(sorted(set(x)))).reset_index()

    if output:
        cnv_genes.to_csv(output, sep='\t', index=False)

    return cnv_genes
```

## Annotate with Cancer Gene Census

**Goal:** Flag known cancer-associated genes within CNV regions.

**Approach:** Load the COSMIC Cancer Gene Census, cross-reference with genes overlapping CNVs, and tag matching genes.

```python
import pandas as pd

def annotate_cancer_genes(cnv_genes, cgc_file):
    '''Flag cancer-associated genes in CNVs.'''
    cgc = pd.read_csv(cgc_file, sep='\t')
    cancer_genes = set(cgc['Gene Symbol'].tolist())

    def check_cancer_genes(genes):
        if pd.isna(genes):
            return ''
        gene_list = genes.split(',')
        cancer = [g for g in gene_list if g in cancer_genes]
        return ','.join(cancer)

    cnv_genes['cancer_genes'] = cnv_genes['gene_name'].apply(check_cancer_genes)
    cnv_genes['n_cancer_genes'] = cnv_genes['cancer_genes'].apply(
        lambda x: len(x.split(',')) if x else 0)

    return cnv_genes
```

## Annotate with ACMG/ClinVar

**Goal:** Identify pathogenic ClinVar variants within CNV regions for clinical interpretation.

**Approach:** Query the ClinVar VCF for each CNV region using pysam, collect pathogenic variants and their associated genes.

```python
def annotate_clinvar_cnvs(cnv_bed, clinvar_vcf):
    '''Annotate CNVs with ClinVar variants.'''
    import pysam

    cnv = pd.read_csv(cnv_bed, sep='\t', header=None,
        names=['chrom', 'start', 'end', 'log2'])

    vcf = pysam.VariantFile(clinvar_vcf)

    results = []
    for _, row in cnv.iterrows():
        chrom = row['chrom'].replace('chr', '')
        pathogenic = []

        for rec in vcf.fetch(chrom, row['start'], row['end']):
            clnsig = rec.info.get('CLNSIG', [''])[0]
            if 'pathogenic' in clnsig.lower():
                gene = rec.info.get('GENEINFO', 'NA').split(':')[0]
                pathogenic.append(gene)

        results.append({
            'chrom': row['chrom'],
            'start': row['start'],
            'end': row['end'],
            'log2': row['log2'],
            'clinvar_pathogenic': ','.join(set(pathogenic))
        })

    return pd.DataFrame(results)
```

## GISTIC2 for Recurrent CNVs

```bash
# Export segments for GISTIC
cnvkit.py export seg *.cns -o cohort.seg

# Run GISTIC2
gistic2 \
    -b results/ \
    -seg cohort.seg \
    -refgene hg38.refgene.mat \
    -genegistic 1 \
    -smallmem 1 \
    -broad 1 \
    -brlen 0.5 \
    -conf 0.90 \
    -armpeel 1 \
    -savegene 1

# Output: significant regions with genes
```

## AnnotSV for Comprehensive Annotation

```bash
# Export CNVs to VCF
cnvkit.py export vcf sample.cns -o sample.cnv.vcf

# Run AnnotSV
AnnotSV \
    -SVinputFile sample.cnv.vcf \
    -genomeBuild GRCh38 \
    -outputFile sample_annotated \
    -SVminSize 1000

# Output includes: genes, DGV, gnomAD-SV, ClinVar, OMIM
```

## R: Gene Enrichment of CNV Regions

**Goal:** Determine whether amplified or deleted genes are enriched for specific biological pathways.

**Approach:** Extract genes from amplified CNV regions, convert to Entrez IDs, and run GO and KEGG enrichment with clusterProfiler.

```r
library(clusterProfiler)
library(org.Hs.eg.db)

# Get genes in amplified regions
amp_genes <- unique(cnv_annotation$gene_name[cnv_annotation$log2 > 0.5])

# Convert to Entrez IDs
entrez_ids <- mapIds(org.Hs.eg.db, keys=amp_genes, keytype='SYMBOL', column='ENTREZID')
entrez_ids <- na.omit(entrez_ids)

# GO enrichment
go_results <- enrichGO(
    gene=entrez_ids,
    OrgDb=org.Hs.eg.db,
    ont='BP',
    pAdjustMethod='BH',
    qvalueCutoff=0.05
)

# KEGG enrichment
kegg_results <- enrichKEGG(
    gene=entrez_ids,
    organism='hsa',
    pAdjustMethod='BH'
)
```

## Interpret CNV States

```python
def interpret_cnv(log2, purity=1.0, ploidy=2):
    '''Interpret CNV log2 ratio as copy number state.'''
    # Adjusted for purity
    cn = 2 * (2 ** log2)

    if cn < 0.5:
        return 'homozygous_deletion'
    elif cn < 1.5:
        return 'heterozygous_deletion'
    elif cn < 2.5:
        return 'diploid'
    elif cn < 3.5:
        return 'single_copy_gain'
    else:
        return 'amplification'

def summarize_cnvs(cns_annotated):
    '''Summarize CNV calls.'''
    cns_annotated['cnv_type'] = cns_annotated['log2'].apply(interpret_cnv)

    summary = {
        'total_cnvs': len(cns_annotated),
        'amplifications': (cns_annotated['cnv_type'] == 'amplification').sum(),
        'deletions': (cns_annotated['cnv_type'].str.contains('deletion')).sum(),
        'total_genes': cns_annotated['gene_name'].str.split(',').explode().nunique(),
        'cancer_genes': cns_annotated['cancer_genes'].str.split(',').explode().nunique()
    }

    return summary
```

## Output Report

```python
def generate_cnv_report(cns_annotated, output_prefix):
    '''Generate CNV annotation report.'''
    # Full annotation table
    cns_annotated.to_csv(f'{output_prefix}_full.tsv', sep='\t', index=False)

    # High-impact CNVs
    high_impact = cns_annotated[
        (cns_annotated['n_cancer_genes'] > 0) |
        (abs(cns_annotated['log2']) > 1)
    ]
    high_impact.to_csv(f'{output_prefix}_high_impact.tsv', sep='\t', index=False)

    # Gene-level summary
    genes = cns_annotated.explode('gene_name')
    gene_summary = genes.groupby('gene_name').agg({
        'log2': 'mean',
        'chrom': 'first',
        'start': 'min',
        'end': 'max'
    }).reset_index()
    gene_summary.to_csv(f'{output_prefix}_genes.tsv', sep='\t', index=False)

    return high_impact
```

## Related Skills

- copy-number/cnvkit-analysis - Generate CNV calls
- copy-number/cnv-visualization - Visualize annotated CNVs
- pathway-analysis/go-enrichment - Enrichment of CNV genes
- genome-intervals/bed-file-basics - BED file operations
