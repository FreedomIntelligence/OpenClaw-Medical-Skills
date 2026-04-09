# bio-epidemiological-genomics-transmission-inference

> Infer pathogen transmission networks and identify likely transmission pairs using TransPhylo and outbreak reconstruction algorithms. Estimate who-infected-whom from genomic and epidemiological data. Use when investigating outbreak transmission chains or identifying superspreaders.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, TreeTime 0.11+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Transmission Inference

**"Infer who infected whom in my outbreak"** → Reconstruct transmission networks from genomic and epidemiological data to identify transmission pairs, superspreaders, and unsampled cases.
- R: `TransPhylo::inferTTree()` for Bayesian transmission tree inference

## TransPhylo in R

```r
library(TransPhylo)
library(ape)

# Load dated phylogeny (from BEAST/TreeTime)
tree <- read.nexus('dated_tree.nexus')

# Convert to TransPhylo format
ptree <- ptreeFromPhylo(tree, dateLastSample = 2020.5)

# Estimate transmission tree
# Uses MCMC to sample from posterior distribution
res <- inferTTree(
    ptree,
    mcmcIterations = 100000,
    startNeg = 0.1,      # Initial within-host effective population
    startOff.r = 2,      # Initial R0 estimate
    startOff.p = 0.5,    # Initial sampling probability
    startPi = 0.9,       # Initial probability of being sampled
    dateT = 2020.6       # End of outbreak observation
)

# Extract consensus transmission tree
ttree <- extractTTree(res)

# Get transmission pairs
pairs <- ttree$ttree[, c('infector', 'infectee', 'time')]
```

## Prepare Data

```python
def prepare_for_transphylo(dated_tree_file, sample_dates, output_prefix):
    '''Prepare inputs for TransPhylo analysis

    Requirements:
    - Time-scaled phylogeny (from TreeTime or BEAST)
    - Sample collection dates
    - Tips must have matching names

    TransPhylo estimates:
    - Who infected whom
    - Unsampled cases in the transmission chain
    - R0 and generation time
    '''
    from Bio import Phylo
    import pandas as pd

    tree = Phylo.read(dated_tree_file, 'nexus')

    # Verify all tips have dates
    dates_df = pd.read_csv(sample_dates, sep='\t')
    tip_names = {clade.name for clade in tree.get_terminals()}
    dated_names = set(dates_df['name'])

    missing = tip_names - dated_names
    if missing:
        print(f'Warning: {len(missing)} tips without dates: {missing}')

    return {'tree': dated_tree_file, 'dates': sample_dates}
```

## Interpret Results

```r
# Analyze TransPhylo output

# Get median transmission tree
med_tree <- medTTree(res)

# Plot transmission tree
plot(med_tree)

# Get R0 estimate
r0_samples <- res$record[, 'off.r']
cat('R0 estimate:', median(r0_samples), '\n')
cat('95% CI:', quantile(r0_samples, c(0.025, 0.975)), '\n')

# Identify superspreaders
# Count number infected by each case
infections_per_case <- table(med_tree$ttree[, 'infector'])
superspreaders <- names(infections_per_case[infections_per_case > 3])
```

## Python Alternative: outbreaker2 Wrapper

**Goal:** Infer likely transmission pairs from genomic distance and collection dates without requiring a dated phylogeny.

**Approach:** For each pair of samples, check that the potential infector was sampled earlier, that the time interval is compatible with the generation time, and that the SNP distance is consistent with direct transmission.

```python
def infer_transmission_simple(distance_matrix, dates, generation_time=5):
    '''Simplified transmission inference

    Uses genomic distance and collection dates to infer likely
    transmission pairs. Less sophisticated than TransPhylo but
    doesn't require dated phylogeny.

    Criteria for transmission pair (A -> B):
    1. A collected before B
    2. Genomic distance consistent with direct transmission
    3. Time difference compatible with generation time
    '''
    import pandas as pd
    import numpy as np

    n = len(dates)
    transmission_pairs = []

    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            time_diff = dates[j] - dates[i]  # Days between collection

            # Potential infector must be sampled first
            if time_diff <= 0:
                continue

            # Check if time difference is compatible
            # Generation time: time between infection of case and infection of secondary
            # Serial interval: time between symptom onset (often used as proxy)
            if time_diff > generation_time * 3:  # Too much time
                continue

            # Check genomic distance
            snp_diff = distance_matrix[i, j]

            # Expected SNPs = rate * time
            # For most pathogens, direct transmission = 0-5 SNP difference
            expected_snps = (time_diff / 365) * 10  # Rough estimate

            if snp_diff <= max(5, expected_snps * 2):
                transmission_pairs.append({
                    'infector': i,
                    'infectee': j,
                    'snp_distance': snp_diff,
                    'days_between': time_diff,
                    'confidence': 'high' if snp_diff <= 2 else 'moderate'
                })

    return pd.DataFrame(transmission_pairs)
```

## Network Visualization

**Goal:** Visualize the inferred transmission chain as a directed network graph showing who infected whom.

**Approach:** Build a directed NetworkX graph from transmission pairs and render it with spring layout, directional arrows, and labeled nodes.

```python
def plot_transmission_network(pairs_df, metadata=None):
    '''Visualize transmission network

    Uses networkx to create directed graph of transmissions.
    '''
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()

    for _, row in pairs_df.iterrows():
        G.add_edge(row['infector'], row['infectee'],
                   weight=row.get('confidence', 1))

    # Layout
    pos = nx.spring_layout(G)

    # Draw
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=500, arrows=True, arrowsize=20)

    plt.title('Transmission Network')
    return plt.gcf()
```

## Superspreader Analysis

```python
def identify_superspreaders(transmission_pairs, threshold=3):
    '''Identify superspreading events

    Superspreader: Individual who infected many others
    Threshold typically 80/20 rule: 20% of cases cause 80% of transmission

    Common threshold: >3 secondary cases
    '''
    from collections import Counter

    infector_counts = Counter(transmission_pairs['infector'])

    superspreaders = {k: v for k, v in infector_counts.items() if v >= threshold}

    total_transmissions = sum(infector_counts.values())
    ss_transmissions = sum(superspreaders.values())

    print(f'Superspreaders (>{threshold} secondary cases):')
    for ss, count in sorted(superspreaders.items(), key=lambda x: -x[1]):
        print(f'  Case {ss}: {count} secondary infections')

    print(f'\nSuperspreading contribution: {ss_transmissions/total_transmissions:.1%}')

    return superspreaders
```

## Related Skills

- epidemiological-genomics/phylodynamics - Generate dated trees
- epidemiological-genomics/pathogen-typing - Identify outbreak clones
- data-visualization/interactive-visualization - Visualize transmission
