# bio-epidemiological-genomics-variant-surveillance

> Assign pathogen lineages and track variants using Nextclade and pangolin for viral surveillance. Monitor variant prevalence and identify emerging variants of concern. Use when classifying viral sequences, tracking lineage dynamics, or monitoring for variants of concern.

## Version Compatibility

Reference examples tested with: Nextclade 3.3+, ggplot2 3.5+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Variant Surveillance

**"Classify my viral sequences into lineages"** → Assign pathogen lineages and track variants of concern using Nextclade or pangolin for real-time genomic surveillance.
- CLI: `nextclade run -d sars-cov-2 -i sequences.fasta`
- CLI: `pangolin sequences.fasta` for SARS-CoV-2 Pango lineage assignment

## Nextclade CLI

```bash
# Install Nextclade
npm install -g @nextstrain/nextclade

# Or download binary
curl -fsSL "https://github.com/nextstrain/nextclade/releases/latest/download/nextclade-x86_64-unknown-linux-gnu" -o nextclade
chmod +x nextclade

# List available datasets
nextclade dataset list

# Download dataset (e.g., SARS-CoV-2)
nextclade dataset get --name sars-cov-2 --output-dir data/sars-cov-2

# Run analysis
nextclade run \
    --input-dataset data/sars-cov-2 \
    --output-tsv results.tsv \
    --output-json results.json \
    sequences.fasta
```

## Pangolin for SARS-CoV-2

```bash
# Install pangolin
pip install pangolin

# Update lineage definitions
pangolin --update

# Run lineage assignment
pangolin sequences.fasta -o pangolin_results.csv

# With specific version
pangolin sequences.fasta --analysis-mode accurate -o results.csv
```

## Parse Nextclade Results

```python
import pandas as pd

def parse_nextclade(results_file):
    '''Parse Nextclade TSV output

    Key columns:
    - seqName: Sequence identifier
    - clade: Nextstrain clade (e.g., 21L for Omicron BA.2)
    - Nextclade_pango: Pangolin lineage
    - qc.overallStatus: Quality control status
    - substitutions: List of mutations
    - aaSubstitutions: Amino acid changes
    '''
    df = pd.read_csv(results_file, sep='\t')

    # Filter by QC status
    df['pass_qc'] = df['qc.overallStatus'].isin(['good', 'mediocre'])

    return df


def summarize_lineages(results_df, lineage_col='Nextclade_pango'):
    '''Summarize lineage distribution'''
    # Filter passed QC
    passed = results_df[results_df['pass_qc']]

    summary = {
        'total_sequences': len(results_df),
        'passed_qc': len(passed),
        'unique_lineages': passed[lineage_col].nunique(),
        'lineage_counts': passed[lineage_col].value_counts().to_dict()
    }

    return summary
```

## Track Variants of Concern

**Goal:** Classify viral sequences into WHO-defined variants of concern and track their prevalence over time.

**Approach:** Map Pango lineages to VOC labels using pattern matching, then group by time period and compute proportional representation of each VOC.

```python
# WHO Variants of Concern/Interest definitions
VOC_DEFINITIONS = {
    'Alpha': {'lineages': ['B.1.1.7', 'Q.*'], 'key_mutations': ['N501Y', 'P681H']},
    'Beta': {'lineages': ['B.1.351'], 'key_mutations': ['K417N', 'E484K', 'N501Y']},
    'Gamma': {'lineages': ['P.1'], 'key_mutations': ['K417T', 'E484K', 'N501Y']},
    'Delta': {'lineages': ['B.1.617.2', 'AY.*'], 'key_mutations': ['L452R', 'P681R']},
    'Omicron': {'lineages': ['B.1.1.529', 'BA.*', 'XBB.*'], 'key_mutations': ['G339D', 'N501Y']}
}

def classify_voc(lineage):
    '''Classify lineage as VOC'''
    for voc, definition in VOC_DEFINITIONS.items():
        for pattern in definition['lineages']:
            if pattern.endswith('*'):
                if lineage.startswith(pattern[:-1]):
                    return voc
            elif lineage == pattern:
                return voc
    return 'Other'


def track_voc_prevalence(results_df, date_col='collection_date'):
    '''Track variant of concern prevalence over time'''
    results_df = results_df.copy()
    results_df['VOC'] = results_df['Nextclade_pango'].apply(classify_voc)

    # Group by week
    results_df['week'] = pd.to_datetime(results_df[date_col]).dt.to_period('W')

    prevalence = results_df.groupby(['week', 'VOC']).size().unstack(fill_value=0)
    prevalence_pct = prevalence.div(prevalence.sum(axis=1), axis=0) * 100

    return prevalence_pct
```

## Mutation Analysis

```python
def parse_mutations(mutation_string):
    '''Parse Nextclade mutation string

    Format: 'A123T,C456G' (nucleotide) or 'S:N501Y,S:D614G' (amino acid)
    '''
    if pd.isna(mutation_string) or mutation_string == '':
        return []
    return mutation_string.split(',')


def find_mutation_prevalence(results_df, mutation_col='aaSubstitutions'):
    '''Calculate prevalence of each mutation'''
    all_mutations = []
    for muts in results_df[mutation_col].dropna():
        all_mutations.extend(parse_mutations(muts))

    mutation_counts = pd.Series(all_mutations).value_counts()
    mutation_prevalence = mutation_counts / len(results_df) * 100

    return mutation_prevalence


def detect_emerging_mutations(results_df, date_col='collection_date', threshold=5):
    '''Detect mutations increasing in frequency'''
    # Goal: Flag mutations showing rapid prevalence increase between
    # early and recent time periods (>2-fold increase above threshold).
    # Approach: Split data at median date, compute per-mutation prevalence
    # in each half, and report mutations with significant frequency gains.
    results_df = results_df.copy()
    results_df['date'] = pd.to_datetime(results_df[date_col])

    # Split into early and recent
    midpoint = results_df['date'].median()
    early = results_df[results_df['date'] < midpoint]
    recent = results_df[results_df['date'] >= midpoint]

    early_prev = find_mutation_prevalence(early)
    recent_prev = find_mutation_prevalence(recent)

    # Find emerging (low->high)
    emerging = []
    for mut in recent_prev.index:
        early_freq = early_prev.get(mut, 0)
        recent_freq = recent_prev[mut]

        if recent_freq > threshold and recent_freq > early_freq * 2:
            emerging.append({
                'mutation': mut,
                'early_prevalence': early_freq,
                'recent_prevalence': recent_freq,
                'fold_change': recent_freq / max(early_freq, 0.1)
            })

    return sorted(emerging, key=lambda x: -x['fold_change'])
```

## Surveillance Report

```python
def generate_surveillance_report(results_df, period='week'):
    '''Generate variant surveillance report'''
    passed = results_df[results_df['pass_qc']]

    report = {
        'period': period,
        'total_sequences': len(results_df),
        'passed_qc': len(passed),
        'qc_pass_rate': f"{len(passed)/len(results_df)*100:.1f}%"
    }

    # Lineage distribution
    lineage_counts = passed['Nextclade_pango'].value_counts()
    report['dominant_lineage'] = lineage_counts.index[0]
    report['dominant_lineage_pct'] = f"{lineage_counts.iloc[0]/len(passed)*100:.1f}%"
    report['top_5_lineages'] = lineage_counts.head(5).to_dict()

    # VOC tracking
    passed['VOC'] = passed['Nextclade_pango'].apply(classify_voc)
    voc_counts = passed['VOC'].value_counts()
    report['voc_distribution'] = voc_counts.to_dict()

    return report
```

## Related Skills

- epidemiological-genomics/phylodynamics - Time-scaled analysis of variants
- variant-calling/variant-annotation - Mutation annotation
- data-visualization/ggplot2-fundamentals - Visualize variant dynamics
