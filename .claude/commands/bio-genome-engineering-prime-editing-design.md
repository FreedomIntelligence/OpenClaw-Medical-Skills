# bio-genome-engineering-prime-editing-design

> Design pegRNAs for prime editing using PrimeDesign algorithms. Generate spacer, PBS, and RT template sequences for precise genomic modifications without double-strand breaks. Use when designing prime editing experiments for precise insertions, deletions, or point mutations.

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Prime Editing Design

**"Design a prime editing guide for my point mutation"** → Generate pegRNA sequences (spacer, scaffold, RT template, PBS) for precise genomic modifications without double-strand breaks, optimizing PBS length and RT template for editing efficiency.
- Python: PrimeDesign algorithms with `Bio.Seq` for sequence handling

## pegRNA Structure

```
pegRNA components:
1. Spacer (20nt) - guides Cas9 to target site
2. Scaffold - Cas9 binding sequence
3. RT template - encodes the desired edit
4. PBS (primer binding site) - anneals to nicked strand

        Spacer (20nt)      Scaffold     RT template    PBS
    5'─[NNNNNNNNNNNNNNNNNNNN]─[scaffold]─[edit]─────[PBS]─3'
```

## Design pegRNA for Point Mutation

```python
from Bio.Seq import Seq

def design_pegrna_substitution(target_seq, edit_pos, new_base, pbs_length=13, rt_length=15):
    '''Design pegRNA for a point mutation

    Args:
        target_seq: ~100bp sequence centered on edit site
        edit_pos: Position of nucleotide to change (0-indexed in target_seq)
        new_base: New nucleotide (A, C, G, or T)
        pbs_length: Primer binding site length (13-17nt optimal)
                   Shorter = less stable, Longer = more secondary structure
        rt_length: RT template length including edit (10-20nt for substitutions)

    Returns:
        dict with pegRNA components
    '''
    target_seq = target_seq.upper()

    # Find nick site (3bp upstream of PAM, which is 3bp after edit for +strand)
    # For substitution, nick should be close to edit site
    nick_pos = edit_pos + 3  # Adjust based on PAM location

    # Spacer: 20nt upstream of PAM
    spacer_start = nick_pos - 17  # Nick is 3bp upstream of PAM
    spacer = target_seq[spacer_start:spacer_start + 20]

    # PBS: Reverse complement of sequence just upstream of nick
    pbs_region = target_seq[nick_pos - pbs_length:nick_pos]
    pbs = str(Seq(pbs_region).reverse_complement())

    # RT template: Contains the edit
    # Sequence from nick site, with edit incorporated
    rt_region = list(target_seq[nick_pos:nick_pos + rt_length])

    # Incorporate the edit
    edit_offset = edit_pos - nick_pos
    if 0 <= edit_offset < len(rt_region):
        rt_region[edit_offset] = new_base

    rt_template = str(Seq(''.join(rt_region)).reverse_complement())

    return {
        'spacer': spacer,
        'pbs': pbs,
        'rt_template': rt_template,
        'pbs_length': pbs_length,
        'rt_length': rt_length,
        'edit_type': 'substitution'
    }
```

## PBS Length Optimization

```python
def optimize_pbs_length(nick_region, min_len=10, max_len=17):
    '''Find optimal PBS length

    PBS considerations:
    - Too short (<10nt): Unstable annealing, low editing efficiency
    - Too long (>17nt): Secondary structure, reduced efficiency
    - Optimal: 13-17nt with 40-60% GC content

    Returns list of PBS options with predicted stability
    '''
    options = []

    for length in range(min_len, max_len + 1):
        pbs_region = nick_region[-length:]
        pbs = str(Seq(pbs_region).reverse_complement())

        gc = sum(1 for nt in pbs if nt in 'GC') / length

        # Estimate melting temperature (simplified)
        # Tm = 2*(A+T) + 4*(G+C) for short oligos
        at = sum(1 for nt in pbs if nt in 'AT')
        gc_count = length - at
        tm = 2 * at + 4 * gc_count

        # Score based on optimal parameters
        score = 1.0
        if gc < 0.4 or gc > 0.6:
            score -= 0.2
        if tm < 45 or tm > 65:
            score -= 0.2
        if length < 13:
            score -= 0.1

        options.append({
            'length': length,
            'sequence': pbs,
            'gc_content': gc,
            'melting_temp': tm,
            'score': score
        })

    return sorted(options, key=lambda x: x['score'], reverse=True)
```

## RT Template Design

```python
def design_rt_template(edit_type, target_seq, nick_pos, **edit_params):
    '''Design RT template for different edit types

    Edit types and typical RT lengths:
    - Substitution: 10-20nt (edit near 5' end of RT)
    - Small insertion (<20bp): RT length = 10 + insertion length
    - Small deletion (<20bp): RT length = 15-25nt flanking deletion
    - Large insertion: May require multiple pegRNAs (twinPE)
    '''
    if edit_type == 'substitution':
        new_base = edit_params['new_base']
        edit_offset = edit_params['edit_pos'] - nick_pos
        rt_len = max(15, edit_offset + 5)

        rt_region = list(target_seq[nick_pos:nick_pos + rt_len])
        if 0 <= edit_offset < len(rt_region):
            rt_region[edit_offset] = new_base

        return str(Seq(''.join(rt_region)).reverse_complement())

    elif edit_type == 'insertion':
        insert_seq = edit_params['insert_seq']
        insert_pos = edit_params['insert_pos'] - nick_pos

        # Build RT with insertion
        rt_5prime = target_seq[nick_pos:nick_pos + insert_pos]
        rt_3prime = target_seq[nick_pos + insert_pos:nick_pos + insert_pos + 10]

        rt_region = rt_5prime + insert_seq + rt_3prime
        return str(Seq(rt_region).reverse_complement())

    elif edit_type == 'deletion':
        del_start = edit_params['del_start'] - nick_pos
        del_end = edit_params['del_end'] - nick_pos

        # Skip deleted region in RT
        rt_5prime = target_seq[nick_pos:nick_pos + del_start]
        rt_3prime = target_seq[nick_pos + del_end:nick_pos + del_end + 15]

        rt_region = rt_5prime + rt_3prime
        return str(Seq(rt_region).reverse_complement())
```

## PE3 Nicking Guide Design

**Goal:** Design a second nicking guide for the PE3 prime editing strategy to improve editing efficiency by nicking the non-edited strand.

**Approach:** Search for PAM sites 40-100bp from the pegRNA nick site on the opposite strand, score candidates by proximity to the optimal 50-80bp distance, and return ranked options.

```python
def design_pe3_nick_guide(target_seq, pegrna_nick_pos, edit_pos):
    '''Design second nicking guide for PE3 strategy

    PE3 uses a second nick on the non-edited strand to improve efficiency.
    Nick distance considerations:
    - Too close (<40bp): Increases indel frequency
    - Optimal (40-100bp): Balances efficiency and precision
    - Too far (>100bp): Reduced benefit

    The second nick should be on the opposite strand.
    '''
    # Search for PAM sites 40-100bp from pegRNA nick
    candidates = []

    for offset in range(40, 101):
        # Check downstream
        pos = pegrna_nick_pos + offset
        if pos + 23 <= len(target_seq):
            if target_seq[pos + 21:pos + 23] == 'GG':
                spacer = target_seq[pos:pos + 20]
                candidates.append({
                    'spacer': spacer,
                    'position': pos,
                    'distance': offset,
                    'strand': '+',
                    'relative': 'downstream'
                })

        # Check upstream (reverse complement)
        pos = pegrna_nick_pos - offset
        if pos >= 20:
            rc_check = str(Seq(target_seq[pos - 3:pos + 20]).reverse_complement())
            if rc_check[:2] == 'CC':  # GG on reverse strand
                spacer = str(Seq(target_seq[pos:pos + 20]).reverse_complement())
                candidates.append({
                    'spacer': spacer,
                    'position': pos,
                    'distance': offset,
                    'strand': '-',
                    'relative': 'upstream'
                })

    # Prefer nicks 50-80bp away
    for c in candidates:
        c['score'] = 1.0 - abs(c['distance'] - 65) / 100

    return sorted(candidates, key=lambda x: x['score'], reverse=True)
```

## Complete pegRNA Assembly

```python
# Standard scaffold sequence for SpCas9
CAS9_SCAFFOLD = 'GTTTTAGAGCTAGAAATAGCAAGTTAAAATAAGGCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC'

def assemble_pegrna(spacer, scaffold, rt_template, pbs):
    '''Assemble full pegRNA sequence for ordering

    Components in 5' to 3' order:
    1. Spacer (20nt)
    2. Scaffold (~76nt for SpCas9)
    3. RT template (variable)
    4. PBS (13-17nt)

    For U6 promoter expression, add G at 5' end if spacer doesn't start with G
    '''
    # Add 5' G if needed for U6 transcription
    if not spacer.startswith('G'):
        spacer = 'G' + spacer[1:]  # Replace first nt or add G

    pegrna = spacer + scaffold + rt_template + pbs

    return {
        'full_sequence': pegrna,
        'length': len(pegrna),
        'spacer': spacer,
        'rt_template': rt_template,
        'pbs': pbs
    }
```

## Related Skills

- genome-engineering/grna-design - Standard guide design for comparison
- genome-engineering/base-editing-design - Alternative for C/G to T/A changes
- variant-calling/variant-annotation - Identify pathogenic variants to correct
