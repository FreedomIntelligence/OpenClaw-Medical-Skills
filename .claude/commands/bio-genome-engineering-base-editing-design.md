# bio-genome-engineering-base-editing-design

> Design guides for cytosine and adenine base editing using editing window optimization and BE-Hive outcome prediction. Select optimal positions for C-to-T or A-to-G conversions without double-strand breaks. Use when designing base editor experiments for precise nucleotide changes.

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Base Editing Design

**"Design a base editor guide for my C-to-T conversion"** → Identify guide sequences that position the target nucleotide within the editing window of cytosine (CBE) or adenine (ABE) base editors, predicting editing outcomes and bystander effects.
- Python: editing window analysis with `Bio.Seq`, BE-Hive outcome prediction

## Base Editor Types

```
Cytosine Base Editors (CBE):
- Convert C to T (or G to A on opposite strand)
- Examples: BE3, BE4, BE4max, AncBE4max
- Editing window: Positions 4-8 (PAM-distal numbering)

Adenine Base Editors (ABE):
- Convert A to G (or T to C on opposite strand)
- Examples: ABE7.10, ABE8e, ABE8.20
- Editing window: Positions 4-7 (narrower than CBE)

Position numbering:
Position 1 = PAM-proximal (next to NGG)
Position 20 = PAM-distal (5' end of spacer)
Editing window is typically positions 4-8 from PAM-distal end
```

## Find Editable Positions

**Goal:** Identify guide sequences that place a target nucleotide within the base editor's editing window while minimizing bystander edits.

**Approach:** Scan for PAM sites in both orientations, calculate where the target base falls within the spacer, filter guides where the target lands in the CBE (positions 4-8) or ABE (positions 4-7) editing window, and rank by fewest bystander bases in the window.

```python
from Bio.Seq import Seq
import re

# Editing window positions (1-indexed from PAM-distal end)
# Position 1 is first nt of spacer, position 20 is adjacent to PAM
CBE_WINDOW = (4, 8)   # BE4max optimal window
ABE_WINDOW = (4, 7)   # ABE8e optimal window

def find_cbe_targets(sequence, target_c_position):
    '''Find guides that place a C in the CBE editing window

    Args:
        sequence: DNA sequence containing the target C
        target_c_position: 0-indexed position of C to edit

    Returns:
        List of guide options with editing predictions
    '''
    sequence = sequence.upper()
    guides = []

    # Search for PAMs that would place target C in window
    for pam_match in re.finditer(r'(?=(.GG))', sequence):
        pam_pos = pam_match.start()

        # Calculate where target C falls in the spacer
        spacer_start = pam_pos - 20
        if spacer_start < 0:
            continue

        c_position_in_spacer = target_c_position - spacer_start + 1  # 1-indexed

        # Check if C is in editing window
        if CBE_WINDOW[0] <= c_position_in_spacer <= CBE_WINDOW[1]:
            spacer = sequence[spacer_start:pam_pos]

            # Find bystander Cs in window (may also be edited)
            bystanders = []
            for i in range(CBE_WINDOW[0] - 1, CBE_WINDOW[1]):
                if i < len(spacer) and spacer[i] == 'C' and (spacer_start + i) != target_c_position:
                    bystanders.append(i + 1)

            guides.append({
                'spacer': spacer,
                'pam_position': pam_pos,
                'target_position_in_spacer': c_position_in_spacer,
                'bystander_cs': bystanders,
                'bystander_count': len(bystanders),
                'strand': '+'
            })

    # Sort by fewest bystanders
    return sorted(guides, key=lambda x: x['bystander_count'])


def find_abe_targets(sequence, target_a_position):
    '''Find guides that place an A in the ABE editing window'''
    sequence = sequence.upper()
    guides = []

    for pam_match in re.finditer(r'(?=(.GG))', sequence):
        pam_pos = pam_match.start()
        spacer_start = pam_pos - 20
        if spacer_start < 0:
            continue

        a_position_in_spacer = target_a_position - spacer_start + 1

        if ABE_WINDOW[0] <= a_position_in_spacer <= ABE_WINDOW[1]:
            spacer = sequence[spacer_start:pam_pos]

            bystanders = []
            for i in range(ABE_WINDOW[0] - 1, ABE_WINDOW[1]):
                if i < len(spacer) and spacer[i] == 'A' and (spacer_start + i) != target_a_position:
                    bystanders.append(i + 1)

            guides.append({
                'spacer': spacer,
                'pam_position': pam_pos,
                'target_position_in_spacer': a_position_in_spacer,
                'bystander_as': bystanders,
                'bystander_count': len(bystanders),
                'strand': '+'
            })

    return sorted(guides, key=lambda x: x['bystander_count'])
```

## Editing Efficiency by Position

```python
# Position-dependent editing efficiency
# Based on BE-Hive and published data
# Values represent relative editing efficiency (1.0 = maximum)

CBE_POSITION_EFFICIENCY = {
    # Position: efficiency (BE4max)
    1: 0.05, 2: 0.10, 3: 0.20,
    4: 0.70, 5: 0.90, 6: 1.00,  # Peak efficiency
    7: 0.85, 8: 0.50,
    9: 0.20, 10: 0.10
}

ABE_POSITION_EFFICIENCY = {
    # Position: efficiency (ABE8e)
    1: 0.02, 2: 0.05, 3: 0.15,
    4: 0.60, 5: 0.95, 6: 1.00,  # Peak at 5-6
    7: 0.70,
    8: 0.20, 9: 0.05
}

def predict_editing_efficiency(guide, editor='CBE'):
    '''Predict editing efficiency based on position

    Interpretation:
    - >0.7: High efficiency expected (good candidate)
    - 0.4-0.7: Moderate efficiency
    - <0.4: Low efficiency (consider alternatives)
    '''
    pos = guide['target_position_in_spacer']

    if editor == 'CBE':
        efficiency = CBE_POSITION_EFFICIENCY.get(pos, 0.05)
    else:  # ABE
        efficiency = ABE_POSITION_EFFICIENCY.get(pos, 0.05)

    return efficiency
```

## Bystander Edit Prediction

```python
def predict_bystander_edits(spacer, editor='CBE'):
    '''Predict which bases in the window will be edited

    Bystanders are non-target bases in the editing window
    that may also be converted. This is a key consideration
    for base editing design.

    Returns:
        List of predicted edits with efficiency scores
    '''
    edits = []

    if editor == 'CBE':
        window = CBE_WINDOW
        target_base = 'C'
        efficiency_map = CBE_POSITION_EFFICIENCY
    else:
        window = ABE_WINDOW
        target_base = 'A'
        efficiency_map = ABE_POSITION_EFFICIENCY

    for i in range(window[0] - 1, window[1]):
        if i < len(spacer) and spacer[i] == target_base:
            pos = i + 1  # 1-indexed
            edits.append({
                'position': pos,
                'original': target_base,
                'edited': 'T' if editor == 'CBE' else 'G',
                'efficiency': efficiency_map.get(pos, 0.1)
            })

    return edits
```

## Dual Base Editor Design

```python
def design_dual_edit(sequence, c_position, a_position, max_distance=50):
    '''Design for simultaneous C>T and A>G edits

    Some applications require both CBE and ABE edits.
    This finds guides where both targets are accessible.
    '''
    cbe_guides = find_cbe_targets(sequence, c_position)
    abe_guides = find_abe_targets(sequence, a_position)

    # Find compatible pairs (different PAMs, both in window)
    compatible = []
    for cbe in cbe_guides:
        for abe in abe_guides:
            distance = abs(cbe['pam_position'] - abe['pam_position'])
            if distance > 0 and distance <= max_distance:
                compatible.append({
                    'cbe_guide': cbe,
                    'abe_guide': abe,
                    'distance': distance
                })

    return compatible
```

## Sequence Context Effects

```python
def score_sequence_context(spacer, position, editor='CBE'):
    '''Score based on sequence context preferences

    CBE context preferences (5' neighbor of target C):
    - TC: High efficiency (most preferred)
    - CC: Good efficiency
    - AC: Moderate efficiency
    - GC: Lower efficiency

    ABE has less pronounced context preferences.
    '''
    if position < 2 or position > len(spacer):
        return 0.5

    idx = position - 1  # 0-indexed

    if editor == 'CBE':
        if idx > 0:
            context = spacer[idx - 1]
            context_scores = {'T': 1.0, 'C': 0.8, 'A': 0.6, 'G': 0.4}
            return context_scores.get(context, 0.5)
    else:  # ABE
        # ABE is less context-dependent
        return 0.8

    return 0.5
```

## Related Skills

- genome-engineering/grna-design - Standard Cas9 guide design
- genome-engineering/prime-editing-design - Alternative for non-C/A edits
- crispr-screens/base-editing-analysis - Analyze base editing outcomes
