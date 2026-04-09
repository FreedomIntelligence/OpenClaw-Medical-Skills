# bio-systems-biology-metabolic-reconstruction

> Build genome-scale metabolic models from genome sequences using CarveMe and gapseq for automated reconstruction. Generate draft models ready for curation and analysis. Use when creating metabolic models for organisms without existing models.

**Available tools:** Read, Bash

# Metabolic Reconstruction

## CarveMe (Recommended)

```bash
# Install CarveMe
pip install carveme

# Basic reconstruction from protein FASTA
carve genome.faa -o model.xml

# Specify output format
carve genome.faa -o model.xml --format sbml
carve genome.faa -o model.json --format json

# Gap-fill for specific media
carve genome.faa -o model.xml --gapfill M9

# Available media: M9, LB, M9[glc], M9[glyc], etc.
```

## CarveMe Options

```bash
# Use diamond instead of blastp (faster)
carve genome.faa -o model.xml --diamond

# Specify organism type
carve genome.faa -o model.xml --grampos  # Gram-positive
carve genome.faa -o model.xml --gramneg  # Gram-negative (default)

# Initialize from template model
carve genome.faa -o model.xml --init M9

# Verbose output for debugging
carve genome.faa -o model.xml -v
```

## gapseq (Alternative)

```bash
# Install gapseq
git clone https://github.com/jotech/gapseq
cd gapseq
./gapseq check  # Check dependencies

# Full reconstruction workflow
./gapseq find -p all genome.fasta  # Find metabolic pathways
./gapseq find -t all genome.fasta  # Find transporters
./gapseq draft -r genome-all-Reactions.tbl \
               -t genome-Transporters.tbl \
               -p genome-all-Pathways.tbl \
               -c genome.fasta
./gapseq fill -m genome-draft.RDS -c genome.fasta -n M9
```

## Python API for CarveMe

```python
import subprocess

def reconstruct_model(fasta_path, output_path, media='M9', grampos=False):
    '''Run CarveMe reconstruction

    Args:
        fasta_path: Path to protein FASTA file
        output_path: Output model file path (.xml or .json)
        media: Gap-filling media (M9, LB, etc.)
        grampos: True for Gram-positive organisms

    Model size expectations:
    - Bacteria: 1000-2500 reactions typical
    - Fungi: 1500-3000 reactions
    - Archaea: 800-1500 reactions
    '''
    cmd = ['carve', fasta_path, '-o', output_path, '--gapfill', media]

    if grampos:
        cmd.append('--grampos')

    subprocess.run(cmd, check=True)
    return output_path
```

## Load and Inspect Draft Model

```python
import cobra

model = cobra.io.read_sbml_model('model.xml')

print(f'Reactions: {len(model.reactions)}')
print(f'Metabolites: {len(model.metabolites)}')
print(f'Genes: {len(model.genes)}')

# Check if model can grow
solution = model.optimize()
print(f'Growth rate: {solution.objective_value:.4f}')

# List exchange reactions (available nutrients)
for rxn in model.exchanges[:10]:
    print(f'{rxn.id}: {rxn.reaction}')
```

## Quality Metrics

```python
def assess_model_quality(model):
    '''Basic quality assessment for draft model

    Returns metrics to evaluate reconstruction quality.
    '''
    metrics = {
        'reactions': len(model.reactions),
        'metabolites': len(model.metabolites),
        'genes': len(model.genes),
        'gene_reaction_ratio': len(model.reactions) / max(1, len(model.genes))
    }

    # Count reaction types
    metrics['exchanges'] = len(model.exchanges)
    metrics['transport'] = len([r for r in model.reactions if 'transport' in r.name.lower()])

    # Test growth
    sol = model.optimize()
    metrics['can_grow'] = sol.status == 'optimal' and sol.objective_value > 0.001

    # Gene-reaction rules
    metrics['orphan_reactions'] = len([r for r in model.reactions if not r.genes])

    return metrics
```

## Multiple Genome Reconstruction

```python
import os
from pathlib import Path

def batch_reconstruction(fasta_dir, output_dir, media='M9'):
    '''Reconstruct models for multiple genomes

    Use for comparative genomics or community modeling.
    '''
    os.makedirs(output_dir, exist_ok=True)

    for fasta in Path(fasta_dir).glob('*.faa'):
        output = Path(output_dir) / f'{fasta.stem}.xml'
        reconstruct_model(str(fasta), str(output), media=media)
        print(f'Completed: {fasta.name}')
```

## Community Model Construction

```python
def merge_models(model_paths, community_name='community'):
    '''Create community model from individual organisms

    For microbiome FBA, need to create a shared compartment
    for metabolite exchange between organisms.
    '''
    import cobra

    models = [cobra.io.read_sbml_model(p) for p in model_paths]

    # Add species prefix to all components
    for i, model in enumerate(models):
        species_id = f'sp{i+1}'
        for rxn in model.reactions:
            rxn.id = f'{species_id}_{rxn.id}'
        for met in model.metabolites:
            met.id = f'{species_id}_{met.id}'
        for gene in model.genes:
            gene.id = f'{species_id}_{gene.id}'

    # Merge into community model
    community = models[0].copy()
    for model in models[1:]:
        community.merge(model)

    return community
```

## Related Skills

- systems-biology/model-curation - Validate and curate draft models
- systems-biology/flux-balance-analysis - Analyze reconstructed models
- database-access/entrez-fetch - Download genome sequences
