# bio-workflows-crispr-editing-pipeline

> End-to-end CRISPR experiment design from target selection to delivery-ready constructs. Covers guide RNA design, off-target assessment, and specialized editing strategies including knockouts, base editing, and HDR knockins. Use when designing complete CRISPR editing experiments for gene knockout, correction, or tagging.

**Available tools:** Read, Bash

# CRISPR Editing Pipeline

Complete workflow for CRISPR experiment design: from target gene to delivery-ready constructs with branching paths for different editing strategies.

## Workflow Overview

```
Target Gene/Position
        |
        v
[1. Guide RNA Design] --> CRISPRscan / Rule Set 2 / DeepCRISPR
        |
        v
[2. Off-Target Assessment] --> Cas-OFFinder + CFD scoring
        |
        v
    Decision Point: What type of edit?
        |
    +---+-------------------+--------------------+
    |                       |                    |
    v                       v                    v
[3a. Knockout]        [3b. Base Editing]   [3c. Knockin]
 Standard Cas9         CBE/ABE design       HDR template
 Frameshift            C>T or A>G           with homology arms
        |                   |                    |
        v                   v                    v
    Final Constructs with Validation Primers
```

## Prerequisites

```bash
pip install crisprscan biopython pandas numpy matplotlib

conda install -c bioconda primer3-py cas-offinder

# Python packages for scoring
pip install crisprtools  # if available
```

## Primary Path: Gene Knockout

### Step 1: Guide RNA Design

```python
from Bio import SeqIO
from Bio.Seq import Seq
import pandas as pd
import re

def find_guides(sequence, pam='NGG'):
    '''Find all potential gRNA target sites with NGG PAM.'''
    guides = []
    seq_str = str(sequence).upper()

    # Forward strand: 20bp + NGG
    for match in re.finditer(r'(?=([ATCG]{20}[ATCG]GG))', seq_str):
        pos = match.start()
        target = match.group(1)[:20]
        pam_seq = match.group(1)[20:23]
        guides.append({
            'sequence': target,
            'pam': pam_seq,
            'position': pos,
            'strand': '+',
            'full_target': match.group(1)
        })

    # Reverse strand: CCN + 20bp
    for match in re.finditer(r'(?=(CC[ATCG][ATCG]{20}))', seq_str):
        pos = match.start()
        full = match.group(1)
        target = str(Seq(full[3:23]).reverse_complement())
        pam_seq = str(Seq(full[0:3]).reverse_complement())
        guides.append({
            'sequence': target,
            'pam': pam_seq,
            'position': pos,
            'strand': '-',
            'full_target': full
        })

    return pd.DataFrame(guides)


def score_guide(guide_seq):
    '''Score guide using Rule Set 2-like heuristics.'''
    score = 0.5  # Base score

    # GC content (optimal: 40-70%)
    gc = (guide_seq.count('G') + guide_seq.count('C')) / len(guide_seq)
    if 0.4 <= gc <= 0.7:
        score += 0.2
    elif gc < 0.3 or gc > 0.8:
        score -= 0.2

    # No poly-T (>4 T's is Pol III terminator)
    if 'TTTT' in guide_seq:
        score -= 0.3

    # G at position 20 (adjacent to PAM) preferred
    if guide_seq[-1] == 'G':
        score += 0.1

    # Avoid GG at positions 19-20
    if guide_seq[-2:] == 'GG':
        score -= 0.1

    # Seed region (positions 12-20) GC
    seed = guide_seq[11:20]
    seed_gc = (seed.count('G') + seed.count('C')) / len(seed)
    if 0.4 <= seed_gc <= 0.7:
        score += 0.1

    return min(1.0, max(0.0, score))


# Example: Design guides for BRCA1 exon
gene_seq = '''ATGGATTTATCTGCTCTTCGCGTTGAAGAAGTACAAAATGTCATTAATGCTATGCAGAAAATCTTAGAGT
GTCCCATCTGTCTGGAGTTGATCAAGGAACCTGTCTCCACAAAGTGTGACCACATATTTTGCAAATTTTG'''

guides = find_guides(gene_seq.replace('\n', ''))
guides['activity_score'] = guides['sequence'].apply(score_guide)

# Filter high-scoring guides
# Activity score >0.6 is standard threshold for reliable editing
good_guides = guides[guides['activity_score'] > 0.6].sort_values('activity_score', ascending=False)
print(f'Found {len(good_guides)} high-scoring guides')
print(good_guides[['sequence', 'position', 'strand', 'activity_score']].head(10))
```

### Step 2: Off-Target Assessment

```python
import subprocess
from pathlib import Path

def run_cas_offinder(guides_df, genome_fasta, output_dir, max_mismatches=4):
    '''Run Cas-OFFinder for off-target detection.'''
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write input file
    input_file = output_dir / 'cas_offinder_input.txt'
    with open(input_file, 'w') as f:
        f.write(f'{genome_fasta}\n')
        f.write('NNNNNNNNNNNNNNNNNNNNNGG\n')  # 20bp + NGG pattern
        for _, row in guides_df.iterrows():
            f.write(f"{row['sequence']}NNN {max_mismatches}\n")

    # Run Cas-OFFinder
    output_file = output_dir / 'offtargets.txt'
    subprocess.run([
        'cas-offinder', str(input_file), 'C', str(output_file)  # C for CPU
    ], check=True)

    # Parse results
    offtargets = pd.read_csv(output_file, sep='\t', header=None,
                              names=['pattern', 'chromosome', 'position', 'target',
                                    'strand', 'mismatches'])
    return offtargets


def calculate_specificity_score(guide_seq, offtargets_df):
    '''Calculate CFD-based specificity score.'''
    # Simplified: penalize based on mismatch count and position
    guide_offtargets = offtargets_df[offtargets_df['pattern'].str.contains(guide_seq[:10])]

    if len(guide_offtargets) == 0:
        return 1.0

    # Weight by mismatch count (more mismatches = lower penalty)
    penalty = 0
    for _, ot in guide_offtargets.iterrows():
        mm = ot['mismatches']
        if mm == 0:  # Perfect match elsewhere (bad!)
            penalty += 1.0
        elif mm == 1:
            penalty += 0.5
        elif mm == 2:
            penalty += 0.2
        elif mm == 3:
            penalty += 0.1
        else:
            penalty += 0.05

    # Specificity score: higher is better
    # Score >0.7 is generally acceptable
    return max(0, 1 - penalty / 10)


# Filter by off-target profile
good_guides['specificity_score'] = good_guides['sequence'].apply(
    lambda x: calculate_specificity_score(x, pd.DataFrame())  # placeholder
)

# Combined score
good_guides['combined_score'] = (good_guides['activity_score'] * 0.5 +
                                  good_guides['specificity_score'] * 0.5)
final_guides = good_guides.sort_values('combined_score', ascending=False).head(5)
```

### Step 3a: Knockout Design (Frameshift)

```python
def design_knockout(guide_row, target_sequence):
    '''Design knockout experiment with validation primers.'''
    guide_seq = guide_row['sequence']
    position = guide_row['position']

    # Cas9 cuts 3bp upstream of PAM
    cut_site = position + 17 if guide_row['strand'] == '+' else position + 6

    # Validation primers flanking cut site (~200bp amplicon)
    # 200bp amplicon is optimal for detecting indels by gel or Sanger
    left_start = max(0, cut_site - 100)
    right_end = min(len(target_sequence), cut_site + 100)

    return {
        'guide_sequence': guide_seq,
        'pam': guide_row['pam'],
        'cut_site': cut_site,
        'expected_outcome': 'Frameshift indel',
        'validation_amplicon_start': left_start,
        'validation_amplicon_end': right_end
    }

ko_design = design_knockout(final_guides.iloc[0], gene_seq.replace('\n', ''))
print('Knockout Design:')
for k, v in ko_design.items():
    print(f'  {k}: {v}')
```

### Step 3b: Base Editing Design (CBE/ABE)

```python
def design_base_edit(target_position, target_sequence, edit_type='CBE'):
    '''Design base editing experiment.
    CBE: C>T conversion (or G>A on opposite strand)
    ABE: A>G conversion (or T>C on opposite strand)

    Editing window: positions 4-8 in the protospacer (counting from PAM-distal)
    '''
    guides = find_guides(target_sequence)

    suitable_guides = []
    for _, guide in guides.iterrows():
        guide_start = guide['position']
        guide_end = guide_start + 20

        # Check if target position falls in editing window (positions 4-8)
        # Window position 4-8 is optimal for BE3/BE4 (CBE) and ABE7.10/ABE8
        if guide['strand'] == '+':
            window_start = guide_start + 3  # Position 4
            window_end = guide_start + 8    # Position 8
        else:
            window_start = guide_end - 8
            window_end = guide_end - 3

        if window_start <= target_position <= window_end:
            # Check if target base is appropriate
            target_base = target_sequence[target_position].upper()
            if edit_type == 'CBE' and target_base in ['C', 'G']:
                suitable_guides.append(guide)
            elif edit_type == 'ABE' and target_base in ['A', 'T']:
                suitable_guides.append(guide)

    return pd.DataFrame(suitable_guides)


# Example: Design CBE to introduce stop codon
# C>T at specific position can create TAG/TAA/TGA stop
target_pos = 45  # Example position with C
cbe_guides = design_base_edit(target_pos, gene_seq.replace('\n', ''), 'CBE')
print(f'Found {len(cbe_guides)} CBE-compatible guides')
```

### Step 3c: Knockin Design (HDR Template)

```python
def design_hdr_template(guide_row, target_sequence, insert_sequence,
                         homology_arm_length=800):
    '''Design HDR donor template with homology arms.

    Homology arm length: 800bp is standard for plasmid donors.
    For ssODN, use 30-60bp arms.
    '''
    cut_site = guide_row['position'] + 17 if guide_row['strand'] == '+' else guide_row['position'] + 6

    # Extract homology arms
    # Arms flank the cut site
    left_arm_start = max(0, cut_site - homology_arm_length)
    left_arm = target_sequence[left_arm_start:cut_site]

    right_arm_end = min(len(target_sequence), cut_site + homology_arm_length)
    right_arm = target_sequence[cut_site:right_arm_end]

    # Mutate PAM in donor to prevent re-cutting
    # Change NGG to NGA or NAG (silent if possible)
    guide_seq = guide_row['sequence']
    pam_position_in_arms = cut_site - left_arm_start + 3

    # Full donor: left_arm + insert + right_arm
    donor = left_arm + insert_sequence + right_arm

    return {
        'guide_sequence': guide_seq,
        'cut_site': cut_site,
        'left_arm': left_arm,
        'right_arm': right_arm,
        'insert': insert_sequence,
        'donor_template': donor,
        'donor_length': len(donor),
        'note': 'Remember to mutate PAM in donor to prevent re-cutting'
    }


# Example: Insert GFP tag
gfp_sequence = 'ATGGTGAGCAAGGGCGAGGAG...'  # Truncated for example
hdr_design = design_hdr_template(final_guides.iloc[0], gene_seq.replace('\n', ''), 'FLAG_TAG', 50)
print('HDR Design:')
print(f"  Left arm length: {len(hdr_design['left_arm'])}")
print(f"  Right arm length: {len(hdr_design['right_arm'])}")
print(f"  Total donor length: {hdr_design['donor_length']}")
```

## Visualization

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def plot_guide_landscape(guides_df, gene_length, exon_coords=None):
    '''Visualize guide positions and scores along gene.'''
    fig, axes = plt.subplots(2, 1, figsize=(14, 6), gridspec_kw={'height_ratios': [1, 2]})

    # Top: Gene structure
    ax1 = axes[0]
    ax1.axhline(y=0.5, color='gray', linewidth=10, solid_capstyle='butt')

    if exon_coords:
        for start, end in exon_coords:
            ax1.axhline(y=0.5, xmin=start/gene_length, xmax=end/gene_length,
                       color='steelblue', linewidth=20, solid_capstyle='butt')

    ax1.set_xlim(0, gene_length)
    ax1.set_ylim(0, 1)
    ax1.set_ylabel('Gene')
    ax1.set_xticks([])
    ax1.set_yticks([])

    # Bottom: Guide scores
    ax2 = axes[1]
    colors = ['green' if s > 0.6 else 'orange' if s > 0.4 else 'red'
              for s in guides_df['activity_score']]

    ax2.scatter(guides_df['position'], guides_df['activity_score'],
                c=colors, s=50, alpha=0.7)
    ax2.axhline(y=0.6, color='green', linestyle='--', alpha=0.5, label='Threshold')
    ax2.set_xlim(0, gene_length)
    ax2.set_ylim(0, 1)
    ax2.set_xlabel('Position (bp)')
    ax2.set_ylabel('Activity Score')
    ax2.legend()

    plt.tight_layout()
    plt.savefig('guide_landscape.pdf')
    return fig


# Plot
plot_guide_landscape(guides, len(gene_seq.replace('\n', '')),
                     exon_coords=[(0, 50), (70, 130)])
```

## Parameter Recommendations

| Step | Parameter | Value | Rationale |
|------|-----------|-------|-----------|
| Guide design | Activity score | >0.6 | Standard threshold for reliable editing |
| Guide design | GC content | 40-70% | Optimal for binding and Cas9 activity |
| Off-target | Max mismatches | 4 | Catches most relevant off-targets |
| Off-target | Specificity score | >0.7 | Acceptable off-target profile |
| Base editing | Window | positions 4-8 | Optimal for BE3/BE4, ABE7.10 |
| HDR | Homology arms | 800bp | Standard for plasmid donors |
| HDR (ssODN) | Homology arms | 30-60bp | For single-strand oligo donors |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| No high-scoring guides | GC-poor region | Expand search region, consider Cas12a |
| Many off-targets | Repetitive sequence | Use high-fidelity Cas9 (eSpCas9, HiFi) |
| Low HDR efficiency | NHEJ dominant | Add NHEJ inhibitors, use ssODN |
| Base editing outside window | Guide position | Redesign with target in positions 4-8 |
| Bystander edits | Multiple C/A in window | Design guides with single target base |

## Output Files

| File | Description |
|------|-------------|
| `guides_ranked.tsv` | All guides with activity and specificity scores |
| `offtargets.txt` | Cas-OFFinder results |
| `knockout_design.json` | KO guide and validation primers |
| `base_edit_design.json` | CBE/ABE design with editing window |
| `hdr_template.fasta` | Donor template sequence |
| `guide_landscape.pdf` | Visualization of guide positions |

## Related Skills

- genome-engineering/grna-design - Detailed scoring algorithms
- genome-engineering/off-target-prediction - Cas-OFFinder and CFD
- genome-engineering/base-editing-design - CBE/ABE specifics
- genome-engineering/prime-editing-design - pegRNA design
- genome-engineering/hdr-template-design - Donor optimization
- primer-design/primer-basics - Validation primer design
