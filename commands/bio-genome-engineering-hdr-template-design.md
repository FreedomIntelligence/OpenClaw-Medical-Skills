# bio-genome-engineering-hdr-template-design

> Design homology-directed repair donor templates for CRISPR knock-ins using primer3-py. Create ssODN, dsDNA, or plasmid templates with optimized homology arms. Use when designing donor templates for precise insertions, tagging, or allele replacement.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, primer3-py 2.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# HDR Template Design

**"Design a donor template for my CRISPR knock-in"** → Create homology-directed repair templates (ssODN, dsDNA, or plasmid) with optimized homology arm lengths and silent PAM mutations, using primer3 for flanking primer design.
- Python: `primer3.bindings.design_primers()` (primer3-py) for primer/arm design, `Bio.Seq` for template construction

## Template Types

```
ssODN (single-stranded oligodeoxynucleotide):
- Length: 100-200nt total
- Homology arms: 30-60nt each side
- Best for: Small insertions (<50bp), point mutations
- Delivery: Electroporation with RNP

dsDNA (double-stranded DNA):
- Length: 500bp - 5kb total
- Homology arms: 200-800bp each side
- Best for: Larger insertions (tags, reporters)
- Delivery: Plasmid or PCR product

Plasmid donor:
- Homology arms: 500-2000bp
- Best for: Large insertions (>1kb), conditional alleles
- Delivery: Transfection
```

## ssODN Design

```python
from Bio.Seq import Seq

def design_ssodn(target_seq, cut_site, insert_seq='', arm_length=50):
    '''Design single-stranded oligo donor for HDR

    Args:
        target_seq: Genomic sequence around cut site
        cut_site: Position of Cas9 cut (3bp upstream of PAM)
        insert_seq: Sequence to insert (empty for deletion/mutation)
        arm_length: Length of each homology arm (30-60nt optimal)

    ssODN considerations:
    - Total length should be 100-200nt (synthesis limit)
    - Asymmetric arms can improve HDR (PAM-distal shorter)
    - Strand choice: complementary to non-target strand often better
    '''
    # Extract homology arms
    left_arm = target_seq[cut_site - arm_length:cut_site]
    right_arm = target_seq[cut_site:cut_site + arm_length]

    # Assemble ssODN
    ssodn = left_arm + insert_seq + right_arm

    # Also provide reverse complement (may work better)
    ssodn_rc = str(Seq(ssodn).reverse_complement())

    return {
        'sense': ssodn,
        'antisense': ssodn_rc,
        'length': len(ssodn),
        'left_arm_length': len(left_arm),
        'right_arm_length': len(right_arm),
        'insert_length': len(insert_seq)
    }


def design_ssodn_mutation(target_seq, mutation_pos, new_base, arm_length=50):
    '''Design ssODN for a point mutation

    For point mutations, center the mutation in the ssODN.
    Also introduce silent PAM mutation to prevent re-cutting.
    '''
    # Build mutant sequence
    mutant = list(target_seq)
    mutant[mutation_pos] = new_base
    mutant_seq = ''.join(mutant)

    # Extract arms around mutation
    left_start = mutation_pos - arm_length
    right_end = mutation_pos + arm_length + 1

    ssodn = mutant_seq[left_start:right_end]

    return {
        'sequence': ssodn,
        'length': len(ssodn),
        'mutation_position_in_ssodn': arm_length,
        'original_base': target_seq[mutation_pos],
        'new_base': new_base
    }
```

## Asymmetric Arm Design

```python
def design_asymmetric_ssodn(target_seq, cut_site, insert_seq, pam_position):
    '''Design ssODN with asymmetric homology arms

    Asymmetric arms can improve HDR efficiency:
    - PAM-proximal arm: 30-40nt (shorter)
    - PAM-distal arm: 60-90nt (longer)

    The longer arm is on the side that gets resected first.
    '''
    # Determine which side is PAM-proximal
    if pam_position > cut_site:  # PAM is to the right
        left_arm_length = 70   # PAM-distal (longer)
        right_arm_length = 35  # PAM-proximal (shorter)
    else:  # PAM is to the left
        left_arm_length = 35
        right_arm_length = 70

    left_arm = target_seq[cut_site - left_arm_length:cut_site]
    right_arm = target_seq[cut_site:cut_site + right_arm_length]

    ssodn = left_arm + insert_seq + right_arm

    return {
        'sequence': ssodn,
        'length': len(ssodn),
        'left_arm_length': left_arm_length,
        'right_arm_length': right_arm_length,
        'asymmetry': 'PAM-distal longer'
    }
```

## dsDNA Donor Design

**Goal:** Design a double-stranded DNA donor template with long homology arms for larger CRISPR knock-in insertions, along with PCR primers for amplification.

**Approach:** Extract left and right homology arms of specified length flanking the cut site, concatenate with the insert sequence, then design PCR primers for the arms and Gibson assembly overlap primers that span the arm-insert junctions.

```python
def design_dsdna_donor(target_seq, cut_site, insert_seq, arm_length=500):
    '''Design double-stranded DNA donor for larger insertions

    Args:
        target_seq: Extended genomic sequence (need ~2kb around cut)
        cut_site: Position of Cas9 cut
        insert_seq: Sequence to insert (tag, reporter, etc.)
        arm_length: Homology arm length (200-800bp recommended)

    For PCR amplification, returns primer sequences for arms.
    '''
    left_arm = target_seq[cut_site - arm_length:cut_site]
    right_arm = target_seq[cut_site:cut_site + arm_length]

    donor = left_arm + insert_seq + right_arm

    return {
        'sequence': donor,
        'length': len(donor),
        'left_arm': left_arm,
        'right_arm': right_arm,
        'insert': insert_seq
    }


def design_pcr_primers_for_donor(left_arm, right_arm, insert_seq, tm_target=60):
    '''Design PCR primers to amplify HDR donor

    Creates primers for Gibson assembly or overlap PCR.
    '''
    # Forward primer: 5' end of left arm
    fwd_primer = left_arm[:20]

    # Reverse primer: 3' end of right arm (reverse complement)
    rev_primer = str(Seq(right_arm[-20:]).reverse_complement())

    # Overlap primers for Gibson assembly
    # Left arm reverse with insert overhang
    left_overlap = str(Seq(left_arm[-20:]).reverse_complement()) + insert_seq[:15]

    # Right arm forward with insert overhang
    right_overlap = insert_seq[-15:] + right_arm[:20]

    return {
        'left_arm_fwd': fwd_primer,
        'left_arm_rev': left_overlap,
        'right_arm_fwd': right_overlap,
        'right_arm_rev': rev_primer
    }
```

## Common Insertions

```python
# Common tag sequences for knock-ins
TAGS = {
    'FLAG': 'GATTACAAGGATGACGATGACAAG',
    '3xFLAG': 'GATTACAAGGATGACGATGACAAGGATTACAAGGATGACGATGACAAGGATTACAAGGATGACGATGACAAG',
    'HA': 'TACCCATACGATGTTCCAGATTACGCT',
    'V5': 'GGTAAGCCTATCCCTAACCCTCTCCTCGGTCTCGATTCTACG',
    'MYC': 'GAACAAAAACTCATCTCAGAAGAGGATCTG',
    '6xHIS': 'CATCACCATCACCATCAC',
    'GFP_LINKER': 'GGCGGAGGCGGAAGC',  # Flexible linker before GFP
}

def design_tag_insertion(target_seq, cut_site, tag_name, position='C-term'):
    '''Design HDR donor for protein tagging

    Args:
        position: 'N-term' or 'C-term' relative to target gene

    For C-terminal tagging, insert before stop codon.
    For N-terminal tagging, insert after start codon.
    '''
    tag_seq = TAGS.get(tag_name, tag_name)  # Use custom if not in dict

    # Add linker if needed
    if position == 'C-term':
        insert = TAGS['GFP_LINKER'] + tag_seq  # Linker before tag
    else:
        insert = tag_seq + TAGS['GFP_LINKER']  # Tag then linker

    return design_ssodn(target_seq, cut_site, insert)
```

## PAM Mutation to Prevent Re-cutting

```python
def add_silent_pam_mutation(donor_seq, pam_position, codon_table='standard'):
    '''Add silent mutation to disrupt PAM in donor

    After HDR, the PAM should be disrupted to prevent Cas9
    from cutting the edited allele.

    Strategy:
    - If PAM (NGG) is in coding region, make synonymous change
    - Change GG to GA, GC, or GT (no longer recognized)
    - Ensure the mutation is synonymous (silent)
    '''
    donor = list(donor_seq)

    # NGG PAM - mutate second G to A (most common silent option)
    if pam_position + 2 < len(donor):
        if donor[pam_position + 1:pam_position + 3] == ['G', 'G']:
            # Try GG -> GA (often silent in 3rd codon position)
            donor[pam_position + 2] = 'A'

    return ''.join(donor)
```

## Related Skills

- genome-engineering/grna-design - Design guide to create cut site
- primer-design/primer-basics - PCR primer design for cloning
- sequence-io/read-sequences - Read and parse GenBank features
