# bio-comparative-genomics-hgt-detection

> Detect horizontal gene transfer events using HGTector, compositional analysis, and phylogenetic incongruence methods. Identify foreign genes in bacterial and archaeal genomes from anomalous composition or unexpected phylogenetic placement. Use when searching for horizontally transferred genes or analyzing genome evolution in prokaryotes.

**Available tools:** Read, Bash

# Horizontal Gene Transfer Detection

## HGTector Workflow

```python
'''HGT detection with HGTector and compositional methods'''

import subprocess
import pandas as pd
import numpy as np
from Bio import SeqIO
from collections import Counter


def run_hgtector(proteome, taxonomy_db, output_dir, threads=4):
    '''Run HGTector for HGT detection

    HGTector uses BLAST-based phyletic distribution analysis:
    1. BLAST proteome against reference database
    2. Classify genes by taxonomic distribution
    3. Identify genes with unexpected phyletic patterns

    Requires:
    - NCBI taxonomy database
    - Reference protein database (e.g., RefSeq)
    '''
    # Search against database
    search_cmd = f'''hgtector search \\
        -i {proteome} \\
        -o {output_dir}/search \\
        -m diamond \\
        -t {threads} \\
        -d refseq'''

    subprocess.run(search_cmd, shell=True)

    # Analyze results
    analyze_cmd = f'''hgtector analyze \\
        -i {output_dir}/search \\
        -o {output_dir}/analyze \\
        -t {taxonomy_db}'''

    subprocess.run(analyze_cmd, shell=True)

    return f'{output_dir}/analyze'


def parse_hgtector_results(results_dir):
    '''Parse HGTector output for HGT candidates

    Output columns:
    - gene: Gene identifier
    - close: Score for close taxonomic matches
    - distal: Score for distal taxonomic matches
    - hgt: HGT prediction (1 = putative HGT)
    '''
    results_file = f'{results_dir}/scores.tsv'
    df = pd.read_csv(results_file, sep='\t')

    # Classify HGT candidates
    # distal > close suggests foreign origin
    df['hgt_score'] = df['distal'] - df['close']

    # Threshold: Higher positive score = stronger HGT signal
    # Score > 0.5: Moderate HGT evidence
    # Score > 1.0: Strong HGT evidence
    df['hgt_call'] = df['hgt_score'] > 0.5

    return df
```

## Compositional Analysis

```python
def calculate_gc_content(sequence):
    '''Calculate GC content of a sequence'''
    gc = sum(1 for nt in sequence.upper() if nt in 'GC')
    return gc / len(sequence) if sequence else 0


def calculate_codon_usage(cds_sequence):
    '''Calculate codon usage frequencies

    Foreign genes often have different codon usage
    reflecting their donor genome's bias
    '''
    if len(cds_sequence) % 3 != 0:
        return None

    codons = [cds_sequence[i:i+3] for i in range(0, len(cds_sequence) - 2, 3)]
    counts = Counter(codons)
    total = sum(counts.values())

    return {codon: count / total for codon, count in counts.items()}


def calculate_cai(gene_codons, reference_codons):
    '''Calculate Codon Adaptation Index

    CAI measures how well a gene matches the host codon usage
    Low CAI suggests foreign origin

    CAI < 0.5: Potentially foreign
    CAI 0.5-0.7: Intermediate
    CAI > 0.7: Native-like codon usage
    '''
    import math

    w_values = {}
    for aa_codons in group_synonymous_codons(reference_codons):
        max_freq = max(reference_codons.get(c, 0) for c in aa_codons)
        if max_freq > 0:
            for c in aa_codons:
                w_values[c] = reference_codons.get(c, 0) / max_freq

    cai_sum = 0
    n = 0
    for codon, freq in gene_codons.items():
        if codon in w_values and w_values[codon] > 0:
            cai_sum += math.log(w_values[codon]) * freq
            n += freq

    return math.exp(cai_sum) if n > 0 else 0


def group_synonymous_codons(codon_usage):
    '''Group codons by amino acid'''
    genetic_code = {
        'F': ['TTT', 'TTC'], 'L': ['TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG'],
        'I': ['ATT', 'ATC', 'ATA'], 'M': ['ATG'], 'V': ['GTT', 'GTC', 'GTA', 'GTG'],
        'S': ['TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC'],
        'P': ['CCT', 'CCC', 'CCA', 'CCG'], 'T': ['ACT', 'ACC', 'ACA', 'ACG'],
        'A': ['GCT', 'GCC', 'GCA', 'GCG'], 'Y': ['TAT', 'TAC'],
        'H': ['CAT', 'CAC'], 'Q': ['CAA', 'CAG'], 'N': ['AAT', 'AAC'],
        'K': ['AAA', 'AAG'], 'D': ['GAT', 'GAC'], 'E': ['GAA', 'GAG'],
        'C': ['TGT', 'TGC'], 'W': ['TGG'], 'R': ['CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
        'G': ['GGT', 'GGC', 'GGA', 'GGG']
    }
    return [codons for codons in genetic_code.values()]


def detect_gc_anomalies(genome_fasta, cds_gff, window_size=5000):
    '''Detect regions with anomalous GC content

    Horizontally transferred regions often have
    different GC content than the host genome

    Threshold: >2 standard deviations from genome mean
    '''
    # Load genome
    genome = SeqIO.read(genome_fasta, 'fasta')
    genome_gc = calculate_gc_content(str(genome.seq))

    # Calculate windowed GC
    windows = []
    seq = str(genome.seq)
    for i in range(0, len(seq) - window_size, window_size // 2):
        window_seq = seq[i:i + window_size]
        gc = calculate_gc_content(window_seq)
        windows.append({
            'start': i,
            'end': i + window_size,
            'gc': gc
        })

    df = pd.DataFrame(windows)

    # Identify anomalies
    mean_gc = df['gc'].mean()
    std_gc = df['gc'].std()

    # Z-score threshold: |Z| > 2 suggests anomalous region
    df['z_score'] = (df['gc'] - mean_gc) / std_gc
    df['anomalous'] = abs(df['z_score']) > 2

    return df, genome_gc
```

## Phylogenetic Incongruence

```python
def detect_phylogenetic_incongruence(gene_tree, species_tree):
    '''Detect HGT via phylogenetic incongruence

    Compare gene tree topology to species tree
    Genes with conflicting placement may be HGT

    Methods:
    - AU test: Approximately Unbiased test
    - SH test: Shimodaira-Hasegawa test
    - Bootstrap: Compare bootstrap support
    '''
    from Bio import Phylo
    from io import StringIO

    # Load trees
    g_tree = Phylo.read(StringIO(gene_tree), 'newick')
    s_tree = Phylo.read(StringIO(species_tree), 'newick')

    # Get taxa
    g_taxa = set(t.name for t in g_tree.get_terminals())
    s_taxa = set(t.name for t in s_tree.get_terminals())

    # Basic topological comparison
    # For full analysis, use IQ-TREE topology tests
    common_taxa = g_taxa & s_taxa

    return {
        'gene_taxa': g_taxa,
        'species_taxa': s_taxa,
        'common_taxa': common_taxa,
        'unique_to_gene': g_taxa - s_taxa
    }


def run_topology_test(alignment, tree1, tree2, output_prefix):
    '''Run AU/SH tests for tree comparison

    Tests if gene significantly favors unexpected topology
    p < 0.05 suggests trees are significantly different
    '''
    cmd = f'''iqtree2 -s {alignment} \\
        -z trees.nwk \\
        -n 0 \\
        -zb 10000 \\
        -au \\
        -pre {output_prefix}'''

    # Prepare tree file
    with open('trees.nwk', 'w') as f:
        f.write(f'{tree1}\n{tree2}\n')

    subprocess.run(cmd, shell=True)

    return f'{output_prefix}.iqtree'
```

## Genomic Island Detection

```python
def identify_genomic_islands(genome_gc, gene_annotations, gc_threshold=2):
    '''Identify putative genomic islands (HGT clusters)

    Genomic islands characteristics:
    - Anomalous GC content
    - Different codon usage
    - Flanked by mobile elements (IS, integrases)
    - Near tRNA genes (common integration sites)

    Islands often contain:
    - Pathogenicity factors
    - Antibiotic resistance genes
    - Metabolic capabilities
    '''
    # Group consecutive anomalous genes
    islands = []
    current_island = []

    sorted_genes = sorted(gene_annotations, key=lambda x: x['start'])

    for gene in sorted_genes:
        if abs(gene.get('gc_zscore', 0)) > gc_threshold:
            if not current_island:
                current_island = [gene]
            elif gene['start'] - current_island[-1]['end'] < 10000:
                current_island.append(gene)
            else:
                if len(current_island) >= 3:  # Minimum 3 genes for island
                    islands.append(current_island)
                current_island = [gene]
        else:
            if current_island and len(current_island) >= 3:
                islands.append(current_island)
            current_island = []

    if current_island and len(current_island) >= 3:
        islands.append(current_island)

    return islands


def annotate_island_features(island_genes, mobile_element_db):
    '''Annotate genomic island features

    Look for:
    - Integrases (island integration)
    - Transposases (IS elements)
    - Phage proteins
    - tRNA genes nearby (integration hotspots)
    '''
    features = {
        'has_integrase': False,
        'has_transposase': False,
        'has_phage': False,
        'near_trna': False
    }

    for gene in island_genes:
        product = gene.get('product', '').lower()
        if 'integrase' in product:
            features['has_integrase'] = True
        if 'transposase' in product:
            features['has_transposase'] = True
        if 'phage' in product or 'prophage' in product:
            features['has_phage'] = True

    return features
```

## Related Skills

- comparative-genomics/ortholog-inference - Identify orthologs for phylogenetic tests
- phylogenetics/modern-tree-inference - Build gene trees for incongruence analysis
- metagenomics/amr-detection - AMR genes often on mobile elements
