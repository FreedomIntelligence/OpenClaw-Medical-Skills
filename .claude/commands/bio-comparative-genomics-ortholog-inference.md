# bio-comparative-genomics-ortholog-inference

> Infer orthologous gene groups across species using OrthoFinder and ProteinOrtho. Identify orthologs, paralogs, and co-orthologs for comparative genomics and functional annotation transfer. Use when identifying gene orthologs across species or building orthogroups for evolutionary analysis.

**Available tools:** Read, Bash

# Ortholog Inference

## OrthoFinder Workflow

```python
'''Ortholog inference with OrthoFinder'''

import subprocess
import pandas as pd
import os


def run_orthofinder(proteome_dir, output_dir=None, threads=4):
    '''Run OrthoFinder on directory of proteomes

    Input: Directory with one FASTA file per species
    File naming: Species name derived from filename

    OrthoFinder performs:
    1. All-vs-all DIAMOND/BLAST
    2. Gene tree inference
    3. Species tree inference
    4. Ortholog/paralog classification
    '''
    cmd = f'orthofinder -f {proteome_dir} -t {threads}'

    if output_dir:
        cmd += f' -o {output_dir}'

    # -M msa: Use MSA for gene trees (more accurate but slower)
    # -S diamond: Fast search (default)
    # -S blast: More sensitive search
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Output location
    if output_dir:
        results_dir = output_dir
    else:
        # OrthoFinder creates Results_MonDD in proteome_dir
        results_dir = None
        for d in os.listdir(proteome_dir):
            if d.startswith('OrthoFinder/Results_'):
                results_dir = os.path.join(proteome_dir, d)
                break

    return results_dir


def parse_orthogroups(orthogroups_file):
    '''Parse OrthoFinder Orthogroups.tsv

    Columns: Orthogroup, Species1, Species2, ...
    Values: Gene IDs (comma-separated if multiple)

    Orthogroup types:
    - Single-copy: One gene per species (ideal for phylogenomics)
    - Multi-copy: Duplications in some lineages
    - Species-specific: Genes unique to one species
    '''
    df = pd.read_csv(orthogroups_file, sep='\t')
    df = df.set_index('Orthogroup')

    orthogroups = {}
    for og_id, row in df.iterrows():
        genes = {}
        for species in df.columns:
            cell = row[species]
            if pd.notna(cell) and cell:
                genes[species] = cell.split(', ')
            else:
                genes[species] = []
        orthogroups[og_id] = genes

    return orthogroups


def classify_orthogroups(orthogroups, species_list):
    '''Classify orthogroups by copy number pattern

    Categories:
    - single_copy: Exactly one gene per species (best for phylogenomics)
    - universal: Present in all species (possibly multicopy)
    - partial: Missing from some species
    - species_specific: Only in one species
    '''
    classification = {
        'single_copy': [],
        'universal': [],
        'partial': [],
        'species_specific': []
    }

    for og_id, genes in orthogroups.items():
        present_in = [sp for sp in species_list if genes.get(sp)]
        copy_counts = [len(genes.get(sp, [])) for sp in species_list]

        if len(present_in) == 1:
            classification['species_specific'].append(og_id)
        elif len(present_in) == len(species_list):
            if all(c == 1 for c in copy_counts):
                classification['single_copy'].append(og_id)
            else:
                classification['universal'].append(og_id)
        else:
            classification['partial'].append(og_id)

    return classification


def get_single_copy_orthologs(orthogroups_file):
    '''Extract single-copy orthologs for phylogenomics

    Single-copy orthologs are ideal because:
    - Clear 1:1 relationships
    - No paralogy complications
    - Suitable for concatenated alignments
    '''
    df = pd.read_csv(orthogroups_file, sep='\t')
    df = df.set_index('Orthogroup')

    single_copy = []
    for og_id, row in df.iterrows():
        is_single = True
        for species in df.columns:
            cell = row[species]
            if pd.isna(cell) or cell == '':
                is_single = False
                break
            if ',' in str(cell):
                is_single = False
                break
        if is_single:
            single_copy.append(og_id)

    return df.loc[single_copy]
```

## Gene Trees and Reconciliation

```python
def parse_gene_trees(gene_trees_dir):
    '''Load gene trees from OrthoFinder

    Gene trees show evolutionary history within orthogroups
    Duplication/loss events inferred by species tree reconciliation
    '''
    from Bio import Phylo
    import glob

    trees = {}
    for tree_file in glob.glob(f'{gene_trees_dir}/*.txt'):
        og_id = os.path.basename(tree_file).replace('_tree.txt', '')
        trees[og_id] = Phylo.read(tree_file, 'newick')

    return trees


def identify_paralogs(orthogroup, species):
    '''Identify in-paralogs within an orthogroup

    In-paralogs: Duplications after speciation (within-species)
    Out-paralogs: Duplications before speciation (between-species)

    Multiple genes from same species in an orthogroup are in-paralogs
    '''
    genes = orthogroup.get(species, [])
    if len(genes) > 1:
        return {
            'species': species,
            'paralogs': genes,
            'count': len(genes)
        }
    return None


def find_co_orthologs(orthogroups, gene_id, species):
    '''Find co-orthologs of a gene

    Co-orthologs: Multiple genes in one species that are
    all orthologous to a single gene in another species

    Result of gene duplication after speciation
    '''
    for og_id, genes in orthogroups.items():
        if gene_id in genes.get(species, []):
            co_orthologs = {}
            for sp, sp_genes in genes.items():
                if sp != species and sp_genes:
                    co_orthologs[sp] = sp_genes
            return {'orthogroup': og_id, 'co_orthologs': co_orthologs}

    return None
```

## ProteinOrtho Alternative

```python
def run_proteinortho(proteome_files, output_prefix, threads=4):
    '''Run ProteinOrtho for ortholog detection

    Faster than OrthoFinder for many genomes
    Uses synteny information if available

    -p=blastp+: Use DIAMOND (faster)
    -conn: Connectivity threshold (default 0.1)
    '''
    files_str = ' '.join(proteome_files)
    cmd = f'proteinortho -cpus={threads} -project={output_prefix} {files_str}'

    subprocess.run(cmd, shell=True)

    return f'{output_prefix}.proteinortho.tsv'


def parse_proteinortho(ortho_file):
    '''Parse ProteinOrtho output

    Columns: # Species, Genes, Alg.-Conn., Species1, Species2, ...
    '''
    df = pd.read_csv(ortho_file, sep='\t')

    orthogroups = {}
    for i, row in df.iterrows():
        og_id = f'OG{i:06d}'
        n_species = row['# Species']
        conn = row['Alg.-Conn.']

        genes = {}
        for col in df.columns[3:]:
            val = row[col]
            if pd.notna(val) and val != '*':
                genes[col] = val.split(',')
            else:
                genes[col] = []

        orthogroups[og_id] = {
            'genes': genes,
            'n_species': n_species,
            'connectivity': conn
        }

    return orthogroups
```

## Functional Annotation Transfer

```python
def transfer_annotation(query_gene, orthologs, annotation_db):
    '''Transfer functional annotation via orthology

    Annotation transfer guidelines:
    - Single-copy orthologs: High confidence transfer
    - Co-orthologs: Transfer to all, note potential subfunctionalization
    - In-paralogs: Transfer with caution (may have diverged function)

    Evidence codes:
    - IEA: Inferred from Electronic Annotation
    - ISO: Inferred from Sequence Orthology
    '''
    annotations = []

    for species, genes in orthologs.items():
        for gene in genes:
            if gene in annotation_db:
                ann = annotation_db[gene]
                annotations.append({
                    'source_gene': gene,
                    'source_species': species,
                    'annotation': ann,
                    'evidence': 'ISO'  # Sequence orthology
                })

    return annotations
```

## Related Skills

- comparative-genomics/synteny-analysis - Synteny-based ortholog verification
- comparative-genomics/positive-selection - Selection analysis on orthologs
- phylogenetics/modern-tree-inference - Build trees from single-copy orthologs
- alignment/pairwise-alignment - Align orthogroup sequences
