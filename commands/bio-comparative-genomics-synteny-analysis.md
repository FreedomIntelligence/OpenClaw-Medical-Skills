# bio-comparative-genomics-synteny-analysis

> Analyze genome collinearity and syntenic blocks using MCScanX, SyRI, and JCVI for comparative genomics. Detect conserved gene order, chromosomal rearrangements, and whole-genome duplications. Use when comparing genome structure between species or identifying conserved genomic regions.

**Available tools:** Read, Bash

# Synteny Analysis

## MCScanX Workflow

```python
'''Synteny analysis with MCScanX and visualization'''

import subprocess
import pandas as pd
from collections import defaultdict

def prepare_mcscanx_input(gff_file, fasta_file, species_prefix):
    '''Prepare input files for MCScanX

    MCScanX requires:
    1. .gff file: gene positions (sp  gene  chr  start  end)
    2. .blast file: all-vs-all BLASTP results
    '''
    genes = []
    with open(gff_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if parts[2] == 'gene':
                chrom = parts[0]
                start, end = int(parts[3]), int(parts[4])
                gene_id = parts[8].split('ID=')[1].split(';')[0]
                genes.append(f'{species_prefix}\t{gene_id}\t{chrom}\t{start}\t{end}')

    with open(f'{species_prefix}.gff', 'w') as f:
        f.write('\n'.join(genes))

    return f'{species_prefix}.gff'


def run_mcscanx(gff1, gff2, blast_file, output_prefix):
    '''Run MCScanX for synteny detection

    Key parameters:
    -k: Match score for collinear genes (default 50)
    -g: Gap penalty (default -1)
    -s: Minimum syntenic block size (default 5 genes)
    -e: E-value threshold for BLAST (default 1e-5)
    '''
    # Combine GFF files
    subprocess.run(f'cat {gff1} {gff2} > {output_prefix}.gff', shell=True)

    # Copy BLAST file
    subprocess.run(f'cp {blast_file} {output_prefix}.blast', shell=True)

    # Run MCScanX
    # -s 5: Minimum 5 genes per syntenic block (smaller = more noise)
    # -m 25: Maximum gaps allowed (larger = more relaxed blocks)
    cmd = f'MCScanX -s 5 -m 25 {output_prefix}'
    subprocess.run(cmd, shell=True)

    return f'{output_prefix}.collinearity'


def parse_collinearity(collinearity_file):
    '''Parse MCScanX collinearity output

    Output format:
    ## Alignment X: score=N e_value=X N genes
    X-Y: gene1  gene2
    '''
    blocks = []
    current_block = None

    with open(collinearity_file) as f:
        for line in f:
            if line.startswith('## Alignment'):
                if current_block:
                    blocks.append(current_block)
                parts = line.strip().split()
                score = int(parts[3].split('=')[1])
                e_value = float(parts[4].split('=')[1])
                n_genes = int(parts[5])
                current_block = {
                    'score': score,
                    'e_value': e_value,
                    'n_genes': n_genes,
                    'gene_pairs': []
                }
            elif current_block and '-' in line and ':' in line:
                parts = line.strip().split()
                if len(parts) >= 3:
                    gene1, gene2 = parts[1], parts[2]
                    current_block['gene_pairs'].append((gene1, gene2))

    if current_block:
        blocks.append(current_block)

    return blocks


def classify_synteny_type(blocks, species1_chroms, species2_chroms):
    '''Classify syntenic relationships

    Types:
    - 1:1: Direct orthology (conserved)
    - 1:many: Lineage-specific duplication
    - many:many: Ancient WGD or complex rearrangement
    '''
    sp1_coverage = defaultdict(list)
    sp2_coverage = defaultdict(list)

    for block in blocks:
        for gene1, gene2 in block['gene_pairs']:
            chr1 = species1_chroms.get(gene1)
            chr2 = species2_chroms.get(gene2)
            if chr1 and chr2:
                sp1_coverage[chr1].append(chr2)
                sp2_coverage[chr2].append(chr1)

    classifications = []
    for chr1, partners in sp1_coverage.items():
        unique_partners = len(set(partners))
        if unique_partners == 1:
            classifications.append(('1:1', chr1, partners[0]))
        else:
            classifications.append(('1:many', chr1, set(partners)))

    return classifications
```

## SyRI for Structural Variants

```python
def run_syri(ref_genome, query_genome, alignment_file, output_prefix):
    '''Run SyRI for structural rearrangement identification

    SyRI detects:
    - Syntenic regions (SYN)
    - Inversions (INV)
    - Translocations (TRANS)
    - Duplications (DUP)
    - Insertions/Deletions (INS/DEL)

    Requires whole-genome alignment (minimap2 or MUMmer)
    '''
    # Align genomes with minimap2
    align_cmd = f'minimap2 -ax asm5 {ref_genome} {query_genome} > {output_prefix}.sam'
    subprocess.run(align_cmd, shell=True)

    # Run SyRI
    syri_cmd = f'syri -c {output_prefix}.sam -r {ref_genome} -q {query_genome} -F S --prefix {output_prefix}'
    subprocess.run(syri_cmd, shell=True)

    return f'{output_prefix}syri.out'


def parse_syri_output(syri_file):
    '''Parse SyRI structural variant output'''
    variants = []

    with open(syri_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 10:
                var_type = parts[10]
                ref_chr, ref_start, ref_end = parts[0], int(parts[1]), int(parts[2])
                qry_chr, qry_start, qry_end = parts[5], int(parts[6]), int(parts[7])
                variants.append({
                    'type': var_type,
                    'ref_chr': ref_chr,
                    'ref_start': ref_start,
                    'ref_end': ref_end,
                    'qry_chr': qry_chr,
                    'qry_start': qry_start,
                    'qry_end': qry_end,
                    'size': ref_end - ref_start
                })

    return pd.DataFrame(variants)
```

## JCVI Visualization

```python
def create_synteny_plot(blocks_file, layout_file, output_file):
    '''Create synteny dot plot with JCVI

    JCVI (python-jcvi) provides publication-ready figures
    '''
    from jcvi.graphics.dotplot import dotplot
    from jcvi.graphics.karyotype import karyotype

    # Dotplot shows collinear blocks as diagonal lines
    # Good for detecting WGD (parallel diagonals)
    dotplot_cmd = f'python -m jcvi.graphics.dotplot {blocks_file}'
    subprocess.run(dotplot_cmd, shell=True)

    # Karyotype view for chromosome-level comparison
    karyotype_cmd = f'python -m jcvi.graphics.karyotype {layout_file}'
    subprocess.run(karyotype_cmd, shell=True)


def detect_wgd(blocks, min_parallel_blocks=3):
    '''Detect whole-genome duplication signatures

    WGD indicators:
    - Multiple parallel syntenic blocks
    - 2:1 or 4:1 chromosome ratios
    - Similar Ks peaks across blocks

    min_parallel_blocks: Minimum parallel blocks to call WGD
    A 2:1 ratio suggests one WGD, 4:1 suggests two WGDs
    '''
    chrom_ratios = defaultdict(list)

    for block in blocks:
        if block['n_genes'] >= 10:  # Focus on substantial blocks
            pairs = block['gene_pairs']
            # Extract chromosome info from gene names
            # Implementation depends on naming convention
            pass

    return chrom_ratios
```

## Ks Analysis for Dating

```python
def calculate_ks_for_pairs(cds_file1, cds_file2, gene_pairs):
    '''Calculate synonymous substitution rate (Ks) for gene pairs

    Ks interpretation:
    - Ks < 0.1: Very recent divergence or gene conversion
    - Ks 0.1-0.5: Within-species duplication
    - Ks 0.5-1.5: Between closely related species
    - Ks > 1.5: Saturated, unreliable

    Ks peaks indicate WGD events
    '''
    from Bio import SeqIO
    from Bio.Seq import Seq

    # Load CDS sequences
    cds1 = SeqIO.to_dict(SeqIO.parse(cds_file1, 'fasta'))
    cds2 = SeqIO.to_dict(SeqIO.parse(cds_file2, 'fasta'))

    ks_values = []
    for gene1, gene2 in gene_pairs:
        if gene1 in cds1 and gene2 in cds2:
            # Run yn00 or codeml for Ks calculation
            # Simplified - actual implementation uses PAML
            pass

    return ks_values


def plot_ks_distribution(ks_values, output_file):
    '''Plot Ks distribution to identify WGD peaks'''
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.stats import gaussian_kde

    # Filter saturated values
    # Ks > 2 is typically saturated and unreliable
    ks_filtered = [k for k in ks_values if 0 < k < 2]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Histogram
    ax.hist(ks_filtered, bins=50, density=True, alpha=0.7, label='Ks distribution')

    # KDE for peak detection
    if len(ks_filtered) > 10:
        kde = gaussian_kde(ks_filtered)
        x = np.linspace(0, 2, 200)
        ax.plot(x, kde(x), 'r-', linewidth=2, label='KDE')

    ax.set_xlabel('Ks (synonymous substitution rate)')
    ax.set_ylabel('Density')
    ax.legend()
    plt.savefig(output_file)

    return fig
```

## Related Skills

- comparative-genomics/positive-selection - dN/dS analysis on syntenic genes
- comparative-genomics/ortholog-inference - Identify orthologs for synteny
- phylogenetics/modern-tree-inference - Phylogenetic context for synteny dating
- alignment/pairwise-alignment - Sequence alignment for Ks calculation
