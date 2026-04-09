# bio-epidemiological-genomics-amr-surveillance

> Detect and track antimicrobial resistance genes using AMRFinderPlus and ResFinder with epidemiological context. Monitor resistance trends and identify emerging resistance patterns. Use when screening genomes for AMR genes or tracking resistance in surveillance programs.

## Version Compatibility

Reference examples tested with: AMRFinderPlus 3.12+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# AMR Surveillance

**"Screen my isolates for resistance genes and track AMR trends"** → Detect antimicrobial resistance determinants in bacterial genomes and monitor resistance patterns over time for surveillance programs.
- CLI: `amrfinder -n assembly.fasta --plus --organism Klebsiella`

## AMRFinderPlus

```bash
# Install AMRFinderPlus
conda install -c bioconda ncbi-amrfinderplus

# Update database
amrfinder -u

# Basic AMR detection from genome
amrfinder -n genome.fasta -o results.tsv

# With protein input (faster, more sensitive)
amrfinder -p proteins.faa -o results.tsv

# Specify organism for point mutations
amrfinder -n genome.fasta --organism Salmonella -o results.tsv

# Available organisms: Acinetobacter_baumannii, Campylobacter,
# Clostridioides_difficile, Enterococcus_faecalis, Enterococcus_faecium,
# Escherichia, Klebsiella, Neisseria, Pseudomonas_aeruginosa,
# Salmonella, Staphylococcus_aureus, Staphylococcus_pseudintermedius,
# Streptococcus_agalactiae, Streptococcus_pneumoniae, Streptococcus_pyogenes,
# Vibrio_cholerae
```

## Parse AMRFinder Results

```python
import pandas as pd

def parse_amrfinder(results_file):
    '''Parse AMRFinderPlus output

    Key columns:
    - Gene symbol: AMR gene name
    - Sequence name: Contig/protein where found
    - Element type: AMR, STRESS, VIRULENCE
    - Element subtype: AMR mechanism
    - Class: Drug class affected
    - Subclass: Specific drug affected
    - % Coverage: Alignment coverage (>90% typical cutoff)
    - % Identity: Sequence identity (>90% typical cutoff)
    '''
    df = pd.read_csv(results_file, sep='\t')

    # Filter high-confidence hits
    df = df[(df['% Coverage of reference sequence'] >= 90) &
            (df['% Identity to reference sequence'] >= 90)]

    return df


def summarize_amr_profile(results_df):
    '''Summarize AMR profile by drug class'''
    amr_only = results_df[results_df['Element type'] == 'AMR']

    summary = {
        'total_genes': len(amr_only),
        'drug_classes': amr_only['Class'].nunique(),
        'by_class': amr_only.groupby('Class')['Gene symbol'].apply(list).to_dict()
    }

    return summary
```

## ResFinder Alternative

```bash
# ResFinder for acquired resistance genes
# Web: https://cge.cbs.dtu.dk/services/ResFinder/

# Command line via KMA
kma -i reads_1.fq reads_2.fq -o output -t_db resfinder_db -1t1

# Or use CGE Docker
docker run --rm -v $(pwd):/data cgetools/resfinder \
    -i /data/genome.fasta -o /data/results -db_res /db/resfinder_db
```

## Track Resistance Trends

**Goal:** Monitor how AMR gene prevalence changes over time across a surveillance cohort.

**Approach:** Group samples by time period, count AMR gene occurrences per period, and normalize to prevalence percentages for trend analysis.

```python
def analyze_amr_trends(samples_df, date_col='collection_date', gene_col='Gene symbol'):
    '''Analyze AMR gene prevalence over time

    For surveillance programs tracking:
    - Emergence of new resistance
    - Increasing prevalence of known resistance
    - Geographic spread patterns
    '''
    # Group by time period
    samples_df['period'] = pd.to_datetime(samples_df[date_col]).dt.to_period('M')

    # Calculate prevalence by period
    prevalence = samples_df.groupby(['period', gene_col]).size().unstack(fill_value=0)

    # Normalize to percentage
    total_per_period = samples_df.groupby('period').size()
    prevalence_pct = prevalence.div(total_per_period, axis=0) * 100

    return prevalence_pct


def detect_emerging_resistance(historical_df, new_samples_df):
    '''Flag novel or increasing resistance patterns

    Alerts for:
    1. New AMR gene not seen before
    2. Significant increase in prevalence
    3. New combinations of resistance
    '''
    historical_genes = set(historical_df['Gene symbol'].unique())
    new_genes = set(new_samples_df['Gene symbol'].unique())

    novel = new_genes - historical_genes

    if novel:
        print(f'ALERT: Novel resistance genes detected: {novel}')

    return novel
```

## Clinical Interpretation

```python
# Drug-gene relationships for interpretation
AMR_INTERPRETATION = {
    'bla_CTX-M': {
        'class': 'Beta-lactam',
        'affects': ['Cephalosporins (3rd gen)', 'Penicillins'],
        'clinical': 'ESBL producer - avoid cephalosporins'
    },
    'bla_KPC': {
        'class': 'Beta-lactam',
        'affects': ['Carbapenems', 'Cephalosporins', 'Penicillins'],
        'clinical': 'Carbapenemase - limited treatment options'
    },
    'mcr-1': {
        'class': 'Polymyxin',
        'affects': ['Colistin'],
        'clinical': 'Plasmid-mediated colistin resistance - critical'
    },
    'vanA': {
        'class': 'Glycopeptide',
        'affects': ['Vancomycin', 'Teicoplanin'],
        'clinical': 'VRE - infection control measures required'
    }
}

def interpret_amr_profile(genes):
    '''Generate clinical interpretation of AMR profile'''
    interpretations = []

    for gene in genes:
        for pattern, info in AMR_INTERPRETATION.items():
            if pattern in gene:
                interpretations.append({
                    'gene': gene,
                    **info
                })
                break

    return interpretations
```

## Surveillance Report

**Goal:** Generate a summary report of AMR prevalence by drug class with alerts for critical resistance types.

**Approach:** Aggregate AMR detections by drug class, calculate per-class prevalence as percentage of total samples, and flag carbapenem, colistin, and vancomycin resistance specifically.

```python
def generate_surveillance_report(samples_df, period='month'):
    '''Generate AMR surveillance summary report

    Standard surveillance metrics:
    - Prevalence by drug class
    - Trends over time
    - Geographic distribution
    - Emerging threats
    '''
    report = {
        'period': period,
        'total_samples': len(samples_df['sample_id'].unique()),
        'total_amr_genes': samples_df['Gene symbol'].nunique()
    }

    # Prevalence by class
    class_counts = samples_df.groupby('Class')['sample_id'].nunique()
    report['prevalence_by_class'] = (class_counts / report['total_samples'] * 100).to_dict()

    # Critical resistance
    critical = ['Carbapenem', 'Colistin', 'Vancomycin']
    for drug in critical:
        matching = samples_df[samples_df['Class'].str.contains(drug, case=False, na=False)]
        report[f'{drug.lower()}_resistance'] = len(matching['sample_id'].unique())

    return report
```

## Related Skills

- metagenomics/amr-detection - AMR from metagenomic samples
- epidemiological-genomics/pathogen-typing - Strain context for AMR
- variant-calling/variant-annotation - Point mutation resistance
