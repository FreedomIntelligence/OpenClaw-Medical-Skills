# bio-comparative-genomics-ancestral-reconstruction

> Reconstruct ancestral sequences at phylogenetic nodes using PAML and IQ-TREE marginal likelihood methods. Infer ancient protein sequences and trace evolutionary trajectories through sequence history. Use when inferring ancestral states for protein resurrection or tracing evolutionary history.

**Available tools:** Read, Bash

# Ancestral Sequence Reconstruction

## PAML Ancestral Reconstruction

```python
'''Ancestral sequence reconstruction with PAML codeml/baseml'''

import subprocess
import re
from Bio import SeqIO
from Bio.Seq import Seq


def create_asr_control(alignment, tree, output_dir, seq_type='protein'):
    '''Create control file for ancestral reconstruction

    RateAncestor = 1: Enable ancestral reconstruction
    Generates RST file with ancestral sequences

    For codons: Use codeml with seqtype = 1
    For amino acids: Use codeml with seqtype = 2
    For nucleotides: Use baseml
    '''
    if seq_type == 'protein':
        ctl = f'''
      seqfile = {alignment}
     treefile = {tree}
      outfile = {output_dir}/asr.mlc

      seqtype = 2
        model = 3
    aaRatefile = wag.dat

 RateAncestor = 1
    cleandata = 0
        '''
    else:  # codon
        ctl = f'''
      seqfile = {alignment}
     treefile = {tree}
      outfile = {output_dir}/asr.mlc

      seqtype = 1
    CodonFreq = 2
        model = 0
      NSsites = 0

 RateAncestor = 1
    cleandata = 0
        '''

    ctl_file = f'{output_dir}/asr.ctl'
    with open(ctl_file, 'w') as f:
        f.write(ctl)

    return ctl_file


def parse_rst_file(rst_file):
    '''Parse PAML RST file for ancestral sequences

    RST contains:
    - Tree with node numbers
    - Ancestral sequences at each node
    - Posterior probabilities for each site

    Node numbering: Extant sequences first, then internal nodes
    '''
    ancestors = {}
    current_node = None
    current_seq = []

    with open(rst_file) as f:
        content = f.read()

    # Find ancestral sequence section
    if 'Ancestral reconstruction by' in content:
        sections = content.split('Ancestral reconstruction by')
        for section in sections[1:]:
            lines = section.strip().split('\n')
            for line in lines:
                if line.startswith('node #'):
                    if current_node and current_seq:
                        ancestors[current_node] = ''.join(current_seq)
                    match = re.search(r'node #(\d+)', line)
                    if match:
                        current_node = f'Node_{match.group(1)}'
                        current_seq = []
                elif current_node and line.strip() and not line.startswith(' '):
                    # Sequence line
                    seq_part = ''.join(line.split()[1:]) if len(line.split()) > 1 else ''
                    current_seq.append(seq_part)

    if current_node and current_seq:
        ancestors[current_node] = ''.join(current_seq)

    return ancestors


def extract_marginal_probabilities(rst_file):
    '''Extract site-wise posterior probabilities

    High confidence: P > 0.95 (commonly used threshold)
    Moderate confidence: P > 0.80
    Low confidence: P < 0.80 (consider alternatives)

    Report ambiguous sites for experimental validation
    '''
    site_probs = []

    with open(rst_file) as f:
        in_probs = False
        for line in f:
            if 'Prob of best state' in line:
                in_probs = True
                continue
            if in_probs and line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        site = int(parts[0])
                        state = parts[1]
                        prob = float(parts[2])
                        site_probs.append({
                            'site': site,
                            'state': state,
                            'probability': prob,
                            'confidence': 'high' if prob > 0.95 else 'moderate' if prob > 0.8 else 'low'
                        })
                    except ValueError:
                        in_probs = False

    return site_probs
```

## IQ-TREE Ancestral Reconstruction

```python
def run_iqtree_asr(alignment, tree=None, model='LG+G4', output_prefix='asr'):
    '''Run IQ-TREE for ancestral sequence reconstruction

    IQ-TREE provides:
    - Marginal reconstruction (default)
    - Joint reconstruction (-asr-joint)
    - State file (.state) with probabilities

    Advantages over PAML:
    - Automatic model selection
    - Better handling of gaps
    - Faster for large datasets
    '''
    cmd = f'iqtree2 -s {alignment} -m {model} --ancestral -pre {output_prefix}'

    if tree:
        cmd += f' -te {tree}'

    subprocess.run(cmd, shell=True)

    return f'{output_prefix}.state'


def parse_iqtree_state(state_file):
    '''Parse IQ-TREE .state file

    Format: Node  Site  State  Probability  [other states and probs]
    '''
    ancestors = {}

    with open(state_file) as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                node = parts[0]
                site = int(parts[1])
                state = parts[2]
                prob = float(parts[3])

                if node not in ancestors:
                    ancestors[node] = {'sequence': [], 'probabilities': []}
                ancestors[node]['sequence'].append(state)
                ancestors[node]['probabilities'].append(prob)

    # Convert to sequences
    for node in ancestors:
        ancestors[node]['sequence'] = ''.join(ancestors[node]['sequence'])

    return ancestors
```

## Alternative State Analysis

```python
def get_alternative_states(site_probs, threshold=0.1):
    '''Identify sites with plausible alternative ancestral states

    Alternative states with P > 0.1 should be considered
    for experimental validation (ancestral protein resurrection)

    These sites may:
    - Affect function differently
    - Represent true ancestral ambiguity
    - Be targets for directed evolution
    '''
    ambiguous_sites = []

    for site_data in site_probs:
        if 'alternatives' in site_data:
            significant_alts = [
                alt for alt in site_data['alternatives']
                if alt['probability'] > threshold
            ]
            if significant_alts:
                ambiguous_sites.append({
                    'site': site_data['site'],
                    'best_state': site_data['state'],
                    'best_prob': site_data['probability'],
                    'alternatives': significant_alts
                })

    return ambiguous_sites


def calculate_sequence_confidence(site_probs):
    '''Calculate overall confidence in ancestral sequence

    Metrics:
    - Mean posterior probability
    - Fraction of high-confidence sites (P > 0.95)
    - Number of ambiguous positions
    '''
    if not site_probs:
        return None

    probs = [s['probability'] for s in site_probs]
    high_conf = sum(1 for p in probs if p > 0.95) / len(probs)
    low_conf = sum(1 for p in probs if p < 0.8)

    return {
        'mean_probability': sum(probs) / len(probs),
        'high_confidence_fraction': high_conf,
        'low_confidence_sites': low_conf,
        'total_sites': len(probs),
        'overall_quality': 'high' if high_conf > 0.9 else 'moderate' if high_conf > 0.7 else 'low'
    }
```

## Ancestral Protein Resurrection

```python
def design_asr_construct(ancestral_seq, extant_reference, ambiguous_sites):
    '''Design constructs for ancestral protein resurrection

    Strategy:
    1. Use most probable state at each position
    2. Create alternative constructs at ambiguous sites
    3. Consider codon optimization for expression host

    Validation:
    - Test activity of resurrected proteins
    - Compare to extant proteins
    - Test alternative constructs at ambiguous positions
    '''
    constructs = [{'name': 'ASR_ML', 'sequence': ancestral_seq, 'description': 'Maximum likelihood ancestral'}]

    # Create alternative constructs for ambiguous sites
    for site in ambiguous_sites[:5]:  # Limit to top 5 ambiguous
        alt_seq = list(ancestral_seq)
        best_alt = site['alternatives'][0]
        alt_seq[site['site'] - 1] = best_alt['state']
        constructs.append({
            'name': f"ASR_alt_{site['site']}",
            'sequence': ''.join(alt_seq),
            'description': f"Alternative at position {site['site']}: {best_alt['state']}"
        })

    return constructs
```

## Related Skills

- comparative-genomics/positive-selection - Selection analysis on ancestral branches
- comparative-genomics/ortholog-inference - Identify orthologs for reconstruction
- phylogenetics/modern-tree-inference - Generate trees for ASR
- alignment/pairwise-alignment - Prepare MSA for reconstruction
