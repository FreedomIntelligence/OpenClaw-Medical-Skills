# bio-primer-design-primer-validation

> Validate PCR primers for specificity, dimers, hairpins, and secondary structures using primer3-py thermodynamic calculations. Check self-complementarity, heterodimer formation, and 3' stability. Use when validating primer specificity and properties.

**Available tools:** Read, Bash

# Primer Validation

Check primers for secondary structures, dimers, and other issues using primer3-py.

## Required Imports

```python
import primer3
```

## Check Hairpin Formation

```python
primer = 'ATGCGATCGATCGATCGATC'

hairpin = primer3.calc_hairpin(primer)
print(f'Hairpin Tm: {hairpin.tm:.1f}C')
print(f'Hairpin dG: {hairpin.dg:.1f} cal/mol')
print(f'Hairpin dH: {hairpin.dh:.1f} cal/mol')
print(f'Hairpin dS: {hairpin.ds:.1f} cal/mol/K')

# Hairpin is problematic if Tm > annealing temp - 10
annealing_temp = 60.0
if hairpin.tm > annealing_temp - 10:
    print(f'WARNING: Hairpin Tm too high for annealing at {annealing_temp}C')
```

## Check Self-Dimer (Homodimer)

```python
primer = 'ATGCGATCGATCGATCGATC'

homodimer = primer3.calc_homodimer(primer)
print(f'Homodimer Tm: {homodimer.tm:.1f}C')
print(f'Homodimer dG: {homodimer.dg:.1f} cal/mol')

# Self-dimer is problematic if Tm is close to annealing temp
if homodimer.tm > 40:
    print('WARNING: Significant self-dimer potential')
```

## Check Primer-Primer Dimer (Heterodimer)

```python
forward = 'ATGCGATCGATCGATCGATC'
reverse = 'GCTAGCTAGCTAGCTAGCTA'

heterodimer = primer3.calc_heterodimer(forward, reverse)
print(f'Heterodimer Tm: {heterodimer.tm:.1f}C')
print(f'Heterodimer dG: {heterodimer.dg:.1f} cal/mol')

if heterodimer.tm > 40:
    print('WARNING: Significant primer dimer potential between forward and reverse')
```

## Complete Primer Validation

```python
def validate_primer(primer_seq, name='Primer', annealing_temp=60.0):
    '''Comprehensive primer validation'''
    print(f'\n=== Validating {name}: {primer_seq} ===')

    # Basic properties
    tm = primer3.calc_tm(primer_seq)
    gc = (primer_seq.count('G') + primer_seq.count('C')) / len(primer_seq) * 100
    print(f'Length: {len(primer_seq)}bp')
    print(f'Tm: {tm:.1f}C')
    print(f'GC: {gc:.1f}%')

    # Hairpin
    hairpin = primer3.calc_hairpin(primer_seq)
    print(f'Hairpin Tm: {hairpin.tm:.1f}C, dG: {hairpin.dg:.1f}')
    if hairpin.tm > annealing_temp - 10:
        print('  WARNING: Hairpin may interfere with annealing')

    # Homodimer
    homodimer = primer3.calc_homodimer(primer_seq)
    print(f'Homodimer Tm: {homodimer.tm:.1f}C, dG: {homodimer.dg:.1f}')
    if homodimer.tm > 40:
        print('  WARNING: Self-dimer potential')

    # 3' end stability (last 5 bases)
    end_3 = primer_seq[-5:]
    end_gc = (end_3.count('G') + end_3.count('C'))
    print(f"3' end (last 5bp): {end_3}, {end_gc} G/C bases")
    if end_gc > 3:
        print("  WARNING: 3' end may be too GC-rich")
    if end_gc == 0:
        print("  WARNING: 3' end lacks GC clamp")

    # Poly-X runs
    for base in 'ATGC':
        for run_len in range(5, len(primer_seq)):
            if base * run_len in primer_seq:
                print(f'  WARNING: Contains {base}x{run_len} run')
                break

    return {'tm': tm, 'gc': gc, 'hairpin_tm': hairpin.tm, 'homodimer_tm': homodimer.tm}

validate_primer('ATGCGATCGATCGATCGATC', 'Forward')
```

## Validate Primer Pair

```python
def validate_primer_pair(forward, reverse, annealing_temp=60.0):
    '''Validate a primer pair'''
    print(f'\n=== Primer Pair Validation ===')
    print(f'Forward: {forward}')
    print(f'Reverse: {reverse}')

    # Individual primer checks
    fwd_tm = primer3.calc_tm(forward)
    rev_tm = primer3.calc_tm(reverse)
    print(f'\nTm Forward: {fwd_tm:.1f}C')
    print(f'Tm Reverse: {rev_tm:.1f}C')
    print(f'Tm Difference: {abs(fwd_tm - rev_tm):.1f}C')

    if abs(fwd_tm - rev_tm) > 2:
        print('  WARNING: Tm difference > 2C')

    # Heterodimer check
    heterodimer = primer3.calc_heterodimer(forward, reverse)
    print(f'\nHeterodimer Tm: {heterodimer.tm:.1f}C')
    print(f'Heterodimer dG: {heterodimer.dg:.1f} cal/mol')

    if heterodimer.tm > 40:
        print('  WARNING: Significant primer dimer potential')

    # Check 3' complementarity specifically
    end_heterodimer = primer3.calc_heterodimer(forward[-6:], reverse[-6:])
    print(f"3' end heterodimer Tm: {end_heterodimer.tm:.1f}C")
    if end_heterodimer.tm > 20:
        print("  WARNING: 3' ends may form stable dimer")

    # Individual hairpins and homodimers
    fwd_hairpin = primer3.calc_hairpin(forward)
    rev_hairpin = primer3.calc_hairpin(reverse)
    fwd_homodimer = primer3.calc_homodimer(forward)
    rev_homodimer = primer3.calc_homodimer(reverse)

    print(f'\nForward hairpin Tm: {fwd_hairpin.tm:.1f}C')
    print(f'Reverse hairpin Tm: {rev_hairpin.tm:.1f}C')
    print(f'Forward homodimer Tm: {fwd_homodimer.tm:.1f}C')
    print(f'Reverse homodimer Tm: {rev_homodimer.tm:.1f}C')

    return {
        'fwd_tm': fwd_tm,
        'rev_tm': rev_tm,
        'heterodimer_tm': heterodimer.tm,
        'fwd_hairpin_tm': fwd_hairpin.tm,
        'rev_hairpin_tm': rev_hairpin.tm,
    }

validate_primer_pair('ATGCGATCGATCGATCGATC', 'GCTAGCTAGCTAGCTAGCTA')
```

## Calculate End Stability (Native Function)

```python
# Use native calc_end_stability for 3' end thermodynamics
primer = 'ATGCGATCGATCGATCGATC'

# Calculate stability of last 5 bases (default)
end_stability = primer3.calc_end_stability(primer)
print(f"3' end stability: dG = {end_stability.dg:.1f} cal/mol")

# More negative dG = more stable 3' end = better extension but higher mispriming risk
if end_stability.dg < -9000:
    print('  Note: Very stable 3\' end - good extension but watch for mispriming')
```

## Quick Tm-Only Checks (Lightweight)

```python
# For high-throughput screening, use Tm-only functions (return float, not ThermoResult)
primer = 'ATGCGATCGATCGATCGATC'

# Quick hairpin Tm check
hairpin_tm = primer3.calc_hairpin_tm(primer)
print(f'Hairpin Tm: {hairpin_tm:.1f}C')

# Quick homodimer Tm check
homodimer_tm = primer3.calc_homodimer_tm(primer)
print(f'Homodimer Tm: {homodimer_tm:.1f}C')

# Quick heterodimer Tm check
forward = 'ATGCGATCGATCGATCGATC'
reverse = 'GCTAGCTAGCTAGCTAGCTA'
heterodimer_tm = primer3.calc_heterodimer_tm(forward, reverse)
print(f'Heterodimer Tm: {heterodimer_tm:.1f}C')
```

## Fast Batch Screening with Tm-Only Functions

```python
def quick_screen_primers(primer_list, max_hairpin_tm=45, max_homodimer_tm=45):
    '''Fast screening using Tm-only functions'''
    passed = []
    failed = []
    for seq in primer_list:
        hairpin_tm = primer3.calc_hairpin_tm(seq)
        homodimer_tm = primer3.calc_homodimer_tm(seq)
        if hairpin_tm < max_hairpin_tm and homodimer_tm < max_homodimer_tm:
            passed.append(seq)
        else:
            failed.append((seq, hairpin_tm, homodimer_tm))
    return passed, failed

primers = ['ATGCGATCGATCGATCGATC', 'GCGCGCGCGCGCGCGCGCGC', 'ATATATATATATATATATAT']
passed, failed = quick_screen_primers(primers)
print(f'Passed: {len(passed)}, Failed: {len(failed)}')
```

## Check Specificity (3' End)

```python
def check_3prime_specificity(primer_seq):
    '''Check if 3' end is suitable for specific priming'''
    end_5bp = primer_seq[-5:]
    end_3bp = primer_seq[-3:]

    # Count G/C in last 5 bases
    gc_5 = end_5bp.count('G') + end_5bp.count('C')

    # Check last base
    last_base = primer_seq[-1]

    print(f"3' sequence: ...{end_5bp}")
    print(f"G/C in last 5bp: {gc_5}")
    print(f"Last base: {last_base}")

    # Ideal: 1-2 G/C in last 5, ending in G or C
    if gc_5 == 0:
        print('  Consider: No GC clamp at 3\' end')
    elif gc_5 > 3:
        print('  Consider: 3\' end may be too stable (mispriming risk)')

    if last_base in 'AT':
        print('  Consider: Ending in A/T may reduce specificity')

    return {'gc_5': gc_5, 'last_base': last_base}

check_3prime_specificity('ATGCGATCGATCGATCGATC')
```

## Batch Validation

```python
import pandas as pd

def batch_validate_primers(primers):
    '''Validate multiple primers'''
    results = []
    for name, seq in primers.items():
        tm = primer3.calc_tm(seq)
        gc = (seq.count('G') + seq.count('C')) / len(seq) * 100
        hairpin = primer3.calc_hairpin(seq)
        homodimer = primer3.calc_homodimer(seq)

        results.append({
            'name': name,
            'sequence': seq,
            'length': len(seq),
            'tm': round(tm, 1),
            'gc_pct': round(gc, 1),
            'hairpin_tm': round(hairpin.tm, 1),
            'homodimer_tm': round(homodimer.tm, 1),
        })

    return pd.DataFrame(results)

primers = {
    'GAPDH_F': 'GTCTCCTCTGACTTCAACAGCG',
    'GAPDH_R': 'ACCACCCTGTTGCTGTAGCCAA',
    'ACTB_F': 'CATGTACGTTGCTATCCAGGC',
    'ACTB_R': 'CTCCTTAATGTCACGCACGAT',
}

df = batch_validate_primers(primers)
print(df.to_string(index=False))
```

## Thermodynamic Parameters Under Different Conditions

```python
primer = 'ATGCGATCGATCGATCGATC'

# Standard conditions
tm_standard = primer3.calc_tm(primer)
hairpin_standard = primer3.calc_hairpin(primer)

# Custom salt conditions
tm_custom = primer3.calc_tm(primer, mv_conc=100.0, dv_conc=2.0, dntp_conc=0.4, dna_conc=200.0)
hairpin_custom = primer3.calc_hairpin(primer, mv_conc=100.0, dv_conc=2.0)

print(f'Standard conditions: Tm={tm_standard:.1f}C, Hairpin Tm={hairpin_standard.tm:.1f}C')
print(f'Custom conditions:   Tm={tm_custom:.1f}C, Hairpin Tm={hairpin_custom.tm:.1f}C')
```

## Validation Thresholds

| Property | Acceptable | Optimal |
|----------|------------|---------|
| Length | 18-30 bp | 20-25 bp |
| Tm | 55-65C | 58-62C |
| GC% | 35-65% | 45-55% |
| Hairpin Tm | <45C | <35C |
| Homodimer Tm | <45C | <35C |
| Heterodimer Tm | <45C | <35C |
| 3' GC (last 5bp) | 1-3 | 2 |

## Related Skills

- primer-basics - Design new primers with primer3
- qpcr-primers - Design and validate qPCR assays
- database-access/local-blast - BLAST primers against genome for specificity
