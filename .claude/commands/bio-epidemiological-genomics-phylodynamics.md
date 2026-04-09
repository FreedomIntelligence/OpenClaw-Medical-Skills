# bio-epidemiological-genomics-phylodynamics

> Construct time-scaled phylogenies and infer evolutionary dynamics using TreeTime and BEAST2 for outbreak analysis. Estimate divergence times, molecular clock rates, and ancestral states. Use when dating outbreak origins, estimating transmission rates, or building time-calibrated trees.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, TreeTime 0.11+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Phylodynamics

**"Build a time-scaled tree for my outbreak"** → Estimate divergence times and molecular clock rates from dated sequences to reconstruct outbreak timing and evolutionary dynamics.
- Python: `treetime.TreeTime()` for maximum likelihood time-scaled trees
- CLI: `treetime --tree tree.nwk --aln aln.fasta --dates dates.tsv`

## TreeTime Basic Usage

```python
from treetime import TreeTime
from Bio import Phylo

# Load tree and alignment
tree = Phylo.read('tree.nwk', 'newick')

# Create TreeTime object with dates
# dates_file: tab-separated with columns 'name' and 'date'
# Date formats: 2020.5, 2020-06-15, numeric (decimal year)
tt = TreeTime(
    tree=tree,
    aln='alignment.fasta',
    dates='dates.tsv',
    gtr='JC69'  # Nucleotide model: JC69, HKY85, GTR
)

# Run molecular clock analysis
tt.run(
    root='best',           # Root optimization: 'best', 'least-squares', or clade name
    Tc='skyline',          # Coalescent prior: None, 'skyline', 'opt', or numeric
    time_marginal='assign_ml'  # Date estimation method
)

# Access results
print(f'Root date: {tt.tree.root.numdate:.2f}')
print(f'Clock rate: {tt.clock_rate:.2e} subs/site/year')
```

## TreeTime CLI

```bash
# Install treetime
pip install phylo-treetime

# Basic time tree
treetime --tree tree.nwk --aln alignment.fasta --dates dates.tsv --outdir results/

# With coalescent prior (for population dynamics)
treetime --tree tree.nwk --aln alignment.fasta --dates dates.tsv \
    --coalescent skyline --outdir results/

# Ancestral sequence reconstruction
treetime ancestral --tree tree.nwk --aln alignment.fasta --outdir results/

# Mugration (discrete trait analysis, e.g., geographic spread)
treetime mugration --tree tree.nwk --states locations.tsv \
    --attribute location --outdir results/
```

## Date File Format

**Goal:** Prepare a correctly formatted date file mapping sample names to decimal-year collection dates for TreeTime input.

**Approach:** Extract name and date columns from metadata, convert dates to decimal year format, and write as a tab-separated file with 'name' and 'date' headers.

```python
def prepare_date_file(metadata, name_col, date_col, output_path):
    '''Prepare dates file for TreeTime

    Date formats accepted:
    - Decimal year: 2020.5 (July 2020)
    - ISO format: 2020-06-15
    - Year only: 2020 (treated as midpoint)

    For incomplete dates, use ranges:
    - [2020.0:2020.5] for first half of 2020
    '''
    dates = metadata[[name_col, date_col]].copy()
    dates.columns = ['name', 'date']

    # Convert to decimal year if needed
    dates['date'] = dates['date'].apply(convert_to_decimal_year)

    dates.to_csv(output_path, sep='\t', index=False)
    return output_path


def convert_to_decimal_year(date_str):
    '''Convert date string to decimal year'''
    from datetime import datetime

    if isinstance(date_str, (int, float)):
        return float(date_str)

    try:
        dt = datetime.strptime(str(date_str), '%Y-%m-%d')
        year = dt.year
        day_of_year = dt.timetuple().tm_yday
        days_in_year = 366 if (year % 4 == 0) else 365
        return year + (day_of_year - 1) / days_in_year
    except:
        return float(date_str)  # Assume already decimal
```

## Interpret Clock Results

```python
def interpret_clock_rate(rate, genome_length):
    '''Interpret molecular clock rate

    Args:
        rate: Substitutions per site per year
        genome_length: Genome size in bp

    Returns:
        Estimated substitutions per year (genome-wide)

    Typical rates:
    - RNA viruses: 10^-3 to 10^-4 subs/site/year
    - SARS-CoV-2: ~8×10^-4 (24 subs/year for 30kb genome)
    - Bacteria: 10^-6 to 10^-7 subs/site/year
    - E. coli: ~10^-7 (5 SNPs/genome/year)
    '''
    subs_per_year = rate * genome_length

    print(f'Clock rate: {rate:.2e} subs/site/year')
    print(f'Genome-wide: ~{subs_per_year:.1f} substitutions/year')

    # Estimate time to MRCA from SNP distance
    example_snps = 10
    time_estimate = example_snps / (2 * subs_per_year)
    print(f'{example_snps} SNPs = ~{time_estimate:.1f} years since MRCA')
```

## Skyline Plot (Population Dynamics)

**Goal:** Extract effective population size trajectory over time from a TreeTime coalescent skyline analysis.

**Approach:** Parse the skyline JSON output from TreeTime to retrieve time points and corresponding Ne estimates for plotting population dynamics.

```python
def extract_skyline(treetime_results_dir):
    '''Extract coalescent skyline from TreeTime output

    Skyline shows effective population size over time.
    Useful for:
    - Detecting population expansions (outbreak growth)
    - Identifying bottlenecks
    - Estimating R0 from growth rate
    '''
    import json

    with open(f'{treetime_results_dir}/skyline.json') as f:
        skyline = json.load(f)

    times = skyline['times']
    Ne = skyline['Ne']  # Effective population size

    return times, Ne
```

## BEAST2 Integration

```python
def prepare_beast_xml(alignment, dates, template='strict_clock'):
    '''Prepare BEAST2 XML configuration

    BEAST2 templates:
    - strict_clock: Single clock rate (simple outbreaks)
    - relaxed_clock: Rate variation (diverse sampling)
    - bdsky: Birth-death skyline (epidemic dynamics)

    Note: BEAST2 requires more setup than TreeTime but provides
    full Bayesian uncertainty estimates.
    '''
    # BEAST2 typically configured via BEAUti GUI
    # For automation, use templates from beast2.org

    print('BEAST2 setup:')
    print('1. Install BEAST2: https://beast2.org')
    print('2. Run BEAUti to configure analysis')
    print('3. Execute: beast -threads 4 analysis.xml')
    print('4. Summarize: treeannotator -burnin 10 trees.trees output.tree')
```

## Related Skills

- epidemiological-genomics/transmission-inference - Infer who-infected-whom
- phylogenetics/modern-tree-inference - Build input phylogeny
- epidemiological-genomics/variant-surveillance - Track lineage dynamics
