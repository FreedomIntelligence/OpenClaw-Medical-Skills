# bio-longitudinal-monitoring

> Tracks ctDNA dynamics over time for treatment response monitoring using serial liquid biopsy samples. Analyzes tumor fraction trends, mutation clearance kinetics, and defines molecular response criteria. Use when monitoring patients during therapy or detecting molecular relapse before clinical progression.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Longitudinal Monitoring

**"Track ctDNA levels over my patient's treatment"** → Monitor tumor fraction and mutation dynamics across serial liquid biopsy timepoints for treatment response assessment and early relapse detection.
- Python: `pandas` + `matplotlib` for trend analysis and molecular response classification

Track ctDNA dynamics over treatment for response assessment and relapse detection.

## Key Metrics

| Metric | Description | Clinical Relevance |
|--------|-------------|-------------------|
| Tumor fraction trend | Change over time | Response/progression |
| Mutation clearance | Time to undetectable | Depth of response |
| Molecular relapse | ctDNA rise | Early relapse detection |
| Lead time | ctDNA vs imaging | Months before clinical |

## Tracking Tumor Fraction

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def analyze_tf_dynamics(patient_data):
    '''
    Analyze tumor fraction dynamics over treatment.

    Args:
        patient_data: DataFrame with columns [sample_id, timepoint, tumor_fraction, treatment_phase]
    '''
    # Sort by timepoint
    patient_data = patient_data.sort_values('timepoint')

    # Calculate log2 fold changes
    baseline_tf = patient_data.iloc[0]['tumor_fraction']
    patient_data['log2_fc'] = np.log2(patient_data['tumor_fraction'] / baseline_tf)

    # Calculate response metrics
    min_tf = patient_data['tumor_fraction'].min()
    min_timepoint = patient_data.loc[patient_data['tumor_fraction'].idxmin(), 'timepoint']

    metrics = {
        'baseline_tf': baseline_tf,
        'nadir_tf': min_tf,
        'nadir_timepoint': min_timepoint,
        'max_reduction': baseline_tf - min_tf,
        'log2_max_reduction': np.log2(baseline_tf / min_tf) if min_tf > 0 else np.inf
    }

    return patient_data, metrics


def define_response(tf_series, baseline, criteria='2log'):
    '''
    Define molecular response based on tumor fraction changes.

    Args:
        tf_series: Series of tumor fractions
        baseline: Baseline tumor fraction
        criteria: Response criteria (e.g., '2log' for 2-log reduction)
    '''
    if criteria == '2log':
        # 2-log (100-fold) reduction
        threshold = baseline / 100
    elif criteria == '1log':
        threshold = baseline / 10
    elif criteria == 'undetectable':
        threshold = 0.001  # Assay-dependent LOD

    response = tf_series < threshold
    return response
```

## Mutation Tracking

```python
def track_mutations(mutation_data):
    '''
    Track specific mutations across timepoints.

    Args:
        mutation_data: DataFrame with [timepoint, mutation, vaf]
    '''
    # Pivot to get VAF per mutation per timepoint
    pivot = mutation_data.pivot_table(
        index='timepoint',
        columns='mutation',
        values='vaf',
        aggfunc='first'
    )

    # Calculate mean VAF trend
    pivot['mean_vaf'] = pivot.mean(axis=1)

    # Identify cleared mutations
    last_timepoint = pivot.index.max()
    cleared = []
    for mut in pivot.columns:
        if mut == 'mean_vaf':
            continue
        if pivot.loc[last_timepoint, mut] < 0.001 or pd.isna(pivot.loc[last_timepoint, mut]):
            cleared.append(mut)

    return pivot, cleared


def calculate_clearance_kinetics(mutation_data, mutation):
    '''
    Calculate mutation clearance half-life.
    '''
    mut_data = mutation_data[mutation_data['mutation'] == mutation].sort_values('timepoint')

    if len(mut_data) < 3:
        return None

    # Log-linear regression for exponential decay
    from scipy import stats

    x = mut_data['timepoint'].values
    y = np.log(mut_data['vaf'].values + 1e-6)  # Add small value to avoid log(0)

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # Half-life = ln(2) / |slope|
    half_life = np.log(2) / abs(slope) if slope < 0 else np.inf

    return {
        'mutation': mutation,
        'half_life': half_life,
        'slope': slope,
        'r_squared': r_value**2
    }
```

## Relapse Detection

```python
def detect_molecular_relapse(tf_series, baseline, threshold_increase=2):
    '''
    Detect molecular relapse from tumor fraction series.

    Args:
        tf_series: DataFrame with [timepoint, tumor_fraction]
        baseline: Post-treatment nadir
        threshold_increase: Fold-increase to call relapse
    '''
    tf_series = tf_series.sort_values('timepoint')

    # Find nadir
    nadir_idx = tf_series['tumor_fraction'].idxmin()
    nadir_tf = tf_series.loc[nadir_idx, 'tumor_fraction']
    nadir_time = tf_series.loc[nadir_idx, 'timepoint']

    # Check for increase after nadir
    post_nadir = tf_series[tf_series['timepoint'] > nadir_time]

    relapse_detected = False
    relapse_timepoint = None

    for idx, row in post_nadir.iterrows():
        if row['tumor_fraction'] > nadir_tf * threshold_increase:
            relapse_detected = True
            relapse_timepoint = row['timepoint']
            break

    return {
        'nadir_tf': nadir_tf,
        'nadir_timepoint': nadir_time,
        'relapse_detected': relapse_detected,
        'relapse_timepoint': relapse_timepoint
    }
```

## Visualization

```python
def plot_ctdna_dynamics(patient_data, treatment_lines=None, output_file=None):
    '''
    Plot ctDNA dynamics over treatment.
    '''
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot tumor fraction on log scale
    ax.semilogy(patient_data['timepoint'], patient_data['tumor_fraction'],
                'o-', linewidth=2, markersize=8)

    # Add treatment lines
    if treatment_lines:
        for time, label in treatment_lines:
            ax.axvline(x=time, color='gray', linestyle='--', alpha=0.5)
            ax.text(time, ax.get_ylim()[1], label, rotation=90, va='top')

    ax.set_xlabel('Time (days)')
    ax.set_ylabel('Tumor Fraction')
    ax.set_title('ctDNA Dynamics During Treatment')

    # Add LOD line
    ax.axhline(y=0.01, color='red', linestyle=':', alpha=0.5, label='LOD')

    ax.legend()

    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')

    return fig, ax
```

## Clinical Integration

**Goal:** Generate a structured monitoring report combining tumor fraction dynamics, mutation clearance status, and molecular response classification for clinical decision support.

**Approach:** Aggregate tumor fraction trend analysis, mutation tracking pivot tables, and response criteria into a single report dictionary with standardized molecular response categories.

```python
def generate_monitoring_report(patient_id, tf_data, mutation_data, imaging_data=None):
    '''
    Generate clinical monitoring report.
    '''
    report = {
        'patient_id': patient_id,
        'analysis_date': pd.Timestamp.now()
    }

    # Tumor fraction analysis
    tf_data, tf_metrics = analyze_tf_dynamics(tf_data)
    report['tumor_fraction'] = tf_metrics

    # Mutation analysis
    mutation_pivot, cleared = track_mutations(mutation_data)
    report['mutations_tracked'] = len(mutation_pivot.columns) - 1
    report['mutations_cleared'] = len(cleared)

    # Response assessment
    current_tf = tf_data.iloc[-1]['tumor_fraction']
    baseline_tf = tf_data.iloc[0]['tumor_fraction']

    if current_tf < 0.001:
        report['response'] = 'Complete molecular response'
    elif current_tf < baseline_tf * 0.01:
        report['response'] = 'Major molecular response (>2 log)'
    elif current_tf < baseline_tf * 0.5:
        report['response'] = 'Partial molecular response'
    else:
        report['response'] = 'Stable/Progressive'

    return report
```

## Related Skills

- ctdna-mutation-detection - Detect mutations to track
- tumor-fraction-estimation - Estimate tumor fraction per timepoint
- fragment-analysis - Complement with fragmentomics trends
