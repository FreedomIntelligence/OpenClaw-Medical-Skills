# bio-comparative-genomics-positive-selection

> Detect positive selection using dN/dS (omega) tests with PAML codeml and HyPhy. Identify sites and branches under adaptive evolution through codon models and branch-site tests. Use when testing for adaptive evolution in gene families or identifying positively selected sites.

**Available tools:** Read, Bash

# Positive Selection Analysis

## dN/dS Overview

```python
'''
dN/dS (omega, ω) interpretation:
- ω < 1: Purifying (negative) selection - deleterious mutations removed
- ω = 1: Neutral evolution - no selective pressure
- ω > 1: Positive (diversifying) selection - advantageous mutations favored

Most genes: ω << 1 (strong purifying selection)
Immune genes, reproduction: Often show ω > 1 at specific sites
'''
```

## PAML Codeml Analysis

```python
'''Run PAML codeml for selection analysis'''

import subprocess
import os
from Bio import SeqIO
from Bio.Seq import Seq


def prepare_codon_alignment(cds_fasta, output_phy):
    '''Prepare codon alignment in PHYLIP format

    Requirements:
    - CDS sequences (in-frame, no stop codons except terminal)
    - Multiple sequence alignment already performed
    - Sequence length divisible by 3
    '''
    records = list(SeqIO.parse(cds_fasta, 'fasta'))

    # Validate codon alignment
    for rec in records:
        if len(rec.seq) % 3 != 0:
            print(f'Warning: {rec.id} length not divisible by 3')

    # Write PHYLIP format
    n_seq = len(records)
    seq_len = len(records[0].seq)

    with open(output_phy, 'w') as f:
        f.write(f' {n_seq} {seq_len}\n')
        for rec in records:
            # PHYLIP names: 10 characters, padded
            name = rec.id[:10].ljust(10)
            f.write(f'{name}{str(rec.seq)}\n')

    return output_phy


def create_codeml_control(alignment_file, tree_file, output_dir, model='M8'):
    '''Create codeml control file

    Site models for detecting positive selection:
    - M0: One ratio (single ω for all sites)
    - M1a: Nearly neutral (ω0 < 1, ω1 = 1)
    - M2a: Positive selection (ω0 < 1, ω1 = 1, ω2 > 1)
    - M7: Beta (ω from beta distribution, 0 < ω < 1)
    - M8: Beta + ω > 1 (allows positive selection)
    - M8a: Beta + ω = 1 (null for M8 comparison)

    Standard comparison: M8 vs M7 or M8 vs M8a
    '''
    model_params = {
        'M0': {'NSsites': 0, 'model': 0},
        'M1a': {'NSsites': 1, 'model': 0},
        'M2a': {'NSsites': 2, 'model': 0},
        'M7': {'NSsites': 7, 'model': 0},
        'M8': {'NSsites': 8, 'model': 0},
        'M8a': {'NSsites': 8, 'model': 0, 'fix_omega': 1, 'omega': 1},
    }

    params = model_params.get(model, model_params['M8'])

    ctl_content = f'''
      seqfile = {alignment_file}
     treefile = {tree_file}
      outfile = {output_dir}/mlc

        noisy = 9
      verbose = 1
      runmode = 0
      seqtype = 1
    CodonFreq = 2
        model = {params.get('model', 0)}
      NSsites = {params.get('NSsites', 8)}
        icode = 0
    fix_kappa = 0
        kappa = 2
    fix_omega = {params.get('fix_omega', 0)}
        omega = {params.get('omega', 1)}
    '''

    ctl_file = f'{output_dir}/codeml_{model}.ctl'
    with open(ctl_file, 'w') as f:
        f.write(ctl_content)

    return ctl_file


def run_codeml(ctl_file):
    '''Run PAML codeml'''
    cmd = f'codeml {ctl_file}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f'Codeml error: {result.stderr}')

    return result


def parse_codeml_output(mlc_file):
    '''Parse codeml output for likelihood and parameters'''
    results = {'lnL': None, 'omega': None, 'kappa': None, 'sites': []}

    with open(mlc_file) as f:
        content = f.read()

    # Extract log-likelihood
    for line in content.split('\n'):
        if 'lnL' in line and 'np' in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p == 'lnL':
                    results['lnL'] = float(parts[i + 2])
                    break

        # Extract omega values
        if 'omega' in line.lower() and '=' in line:
            parts = line.split('=')
            if len(parts) >= 2:
                try:
                    results['omega'] = float(parts[-1].strip().split()[0])
                except ValueError:
                    pass

    # Extract positively selected sites (BEB analysis)
    if 'Bayes Empirical Bayes' in content:
        beb_section = content.split('Bayes Empirical Bayes')[1]
        for line in beb_section.split('\n'):
            parts = line.split()
            if len(parts) >= 5:
                try:
                    site = int(parts[0])
                    aa = parts[1]
                    prob = float(parts[2])
                    # Sites with P > 0.95 considered significant
                    # Sites with P > 0.99 highly significant
                    if prob > 0.95:
                        results['sites'].append({
                            'position': site,
                            'amino_acid': aa,
                            'probability': prob,
                            'significance': '**' if prob > 0.99 else '*'
                        })
                except (ValueError, IndexError):
                    continue

    return results


def likelihood_ratio_test(lnL_null, lnL_alt, df=2):
    '''Perform likelihood ratio test

    For M8 vs M7: df = 2
    For M2a vs M1a: df = 2
    For branch-site test: df = 1

    Significance thresholds (chi-square):
    - df=1: 3.84 (p<0.05), 6.63 (p<0.01)
    - df=2: 5.99 (p<0.05), 9.21 (p<0.01)
    '''
    from scipy import stats

    lrt = 2 * (lnL_alt - lnL_null)
    p_value = 1 - stats.chi2.cdf(lrt, df)

    return {
        'LRT_statistic': lrt,
        'degrees_freedom': df,
        'p_value': p_value,
        'significant': p_value < 0.05
    }
```

## Branch-Site Models

```python
def create_branch_site_control(alignment, tree, foreground_branch, output_dir):
    '''Create control file for branch-site test

    Branch-site model A tests for positive selection on
    specific branches (foreground) while allowing variation
    across the tree.

    Foreground branch: Mark with #1 in tree file
    Example: ((A,B),(C #1,D));

    Comparison: Model A vs null (fix_omega = 1)
    '''
    ctl_content = f'''
      seqfile = {alignment}
     treefile = {tree}
      outfile = {output_dir}/branch_site.mlc

      runmode = 0
      seqtype = 1
    CodonFreq = 2
        model = 2
      NSsites = 2
    fix_kappa = 0
        kappa = 2
    fix_omega = 0
        omega = 1
    '''

    ctl_file = f'{output_dir}/branch_site.ctl'
    with open(ctl_file, 'w') as f:
        f.write(ctl_content)

    return ctl_file


def mark_foreground_branch(tree_file, foreground_taxa, output_file):
    '''Mark foreground lineage in Newick tree

    For testing selection on specific lineage:
    - Add #1 after the clade of interest
    - Can mark multiple branches with different tags
    '''
    with open(tree_file) as f:
        tree = f.read().strip()

    # Simple marking - for complex trees use ete3
    for taxon in foreground_taxa:
        tree = tree.replace(taxon, f'{taxon} #1')

    with open(output_file, 'w') as f:
        f.write(tree)

    return output_file
```

## HyPhy Alternative

```python
def run_hyphy_busted(alignment_file, tree_file, output_json):
    '''Run HyPhy BUSTED for gene-wide selection

    BUSTED (Branch-site Unrestricted Statistical Test for
    Episodic Diversification) tests whether a gene has
    experienced positive selection at any site on any branch.

    More sensitive than PAML for episodic selection
    '''
    cmd = f'hyphy busted --alignment {alignment_file} --tree {tree_file} --output {output_json}'
    subprocess.run(cmd, shell=True)

    return output_json


def run_hyphy_meme(alignment_file, tree_file, output_json):
    '''Run HyPhy MEME for site-specific selection

    MEME (Mixed Effects Model of Evolution) detects
    episodic diversifying selection at individual sites.

    Better than PAML M8 when selection is episodic
    (not constant across all branches)
    '''
    cmd = f'hyphy meme --alignment {alignment_file} --tree {tree_file} --output {output_json}'
    subprocess.run(cmd, shell=True)

    return output_json


def run_hyphy_fel(alignment_file, tree_file, output_json):
    '''Run HyPhy FEL for pervasive selection

    FEL (Fixed Effects Likelihood) tests for pervasive
    selection at each site across the entire phylogeny.

    Use when selection is expected to be constant
    '''
    cmd = f'hyphy fel --alignment {alignment_file} --tree {tree_file} --output {output_json}'
    subprocess.run(cmd, shell=True)

    return output_json


def parse_hyphy_json(json_file):
    '''Parse HyPhy JSON output'''
    import json

    with open(json_file) as f:
        results = json.load(f)

    # Extract test results
    test_results = results.get('test results', {})

    # Extract sites under selection (MEME/FEL)
    sites = []
    mle = results.get('MLE', {}).get('content', {})
    for site_data in mle.get('0', {}).values():
        if isinstance(site_data, list) and len(site_data) > 5:
            # Structure varies by method
            pass

    return {
        'p_value': test_results.get('p-value'),
        'LRT': test_results.get('LRT'),
        'sites': sites
    }
```

## Related Skills

- comparative-genomics/synteny-analysis - Find syntenic genes for selection tests
- comparative-genomics/ortholog-inference - Identify orthologs for analysis
- alignment/msa-parsing - Parse and manipulate codon alignments
- phylogenetics/modern-tree-inference - Generate trees for codeml
