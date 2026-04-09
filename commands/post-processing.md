# post-processing

> Extract, analyze, and visualize simulation output data. Use for field extraction, time series analysis, line profiles, statistical summaries, derived quantity computation, result comparison to references, and automated report generation from simulation results.

**Available tools:** R, e, a, d, ,,  , B, s, h, W, r, i, t, G, p, l, o, b

# Post-Processing Skill

Analyze and extract meaningful information from simulation output data.

## Goal

Transform raw simulation output into actionable insights through field extraction, statistical analysis, derived quantities, visualizations, and comparison with reference data.

## Inputs to Gather

Before running post-processing scripts, collect:

1. **Output Data Location**
   - Path to simulation output files (JSON, CSV, HDF5, VTK)
   - Time step/snapshot indices of interest
   - Field names to extract

2. **Analysis Type**
   - Field extraction (spatial data at specific times)
   - Time series (temporal evolution of quantities)
   - Line profiles (1D cuts through domain)
   - Statistical summary (mean, std, distributions)
   - Derived quantities (gradients, integrals, fluxes)
   - Comparison to reference data

3. **Output Requirements**
   - Output format (JSON, CSV, tabular)
   - Visualization needs
   - Report format

## Scripts

| Script | Purpose | Key Inputs |
|--------|---------|------------|
| `field_extractor.py` | Extract field data from output files | --input, --field, --timestep |
| `time_series_analyzer.py` | Analyze temporal evolution | --input, --quantity, --window |
| `profile_extractor.py` | Extract line profiles | --input, --field, --start, --end |
| `statistical_analyzer.py` | Compute field statistics | --input, --field, --region |
| `derived_quantities.py` | Calculate derived quantities | --input, --quantity, --params |
| `comparison_tool.py` | Compare to reference data | --simulation, --reference, --metric |
| `report_generator.py` | Generate summary reports | --input, --template, --output |

## Workflow

### 1. Data Inventory

First, understand what data is available:

```bash
# List available fields and timesteps
python scripts/field_extractor.py --input results/ --list --json
```

### 2. Field Extraction

Extract spatial field data at specific timesteps:

```bash
# Extract concentration field at timestep 100
python scripts/field_extractor.py \
    --input results/field_0100.json \
    --field concentration \
    --json

# Extract multiple fields
python scripts/field_extractor.py \
    --input results/field_0100.json \
    --field "phi,concentration,temperature" \
    --json
```

### 3. Time Series Analysis

Analyze temporal evolution of quantities:

```bash
# Extract total energy vs time
python scripts/time_series_analyzer.py \
    --input results/history.json \
    --quantity total_energy \
    --json

# Compute moving average with window
python scripts/time_series_analyzer.py \
    --input results/history.json \
    --quantity mass \
    --window 10 \
    --json

# Detect steady state
python scripts/time_series_analyzer.py \
    --input results/history.json \
    --quantity residual \
    --detect-steady-state \
    --tolerance 1e-6 \
    --json
```

### 4. Line Profile Extraction

Extract 1D profiles through the domain:

```bash
# Extract profile along x-axis at y=0.5
python scripts/profile_extractor.py \
    --input results/field_0100.json \
    --field concentration \
    --start "0,0.5,0" \
    --end "1,0.5,0" \
    --points 100 \
    --json

# Interface profile (through center)
python scripts/profile_extractor.py \
    --input results/field_0100.json \
    --field phi \
    --axis x \
    --slice-position 0.5 \
    --json
```

### 5. Statistical Analysis

Compute statistics over field data:

```bash
# Global statistics
python scripts/statistical_analyzer.py \
    --input results/field_0100.json \
    --field concentration \
    --json

# Statistics in specific region
python scripts/statistical_analyzer.py \
    --input results/field_0100.json \
    --field phi \
    --region "x>0.3 and x<0.7" \
    --json

# Distribution analysis
python scripts/statistical_analyzer.py \
    --input results/field_0100.json \
    --field phi \
    --histogram \
    --bins 50 \
    --json
```

### 6. Derived Quantities

Calculate physical quantities from raw data:

```bash
# Compute interface area
python scripts/derived_quantities.py \
    --input results/field_0100.json \
    --quantity interface_area \
    --threshold 0.5 \
    --json

# Compute gradient magnitude
python scripts/derived_quantities.py \
    --input results/field_0100.json \
    --quantity gradient_magnitude \
    --field phi \
    --json

# Compute volume fractions
python scripts/derived_quantities.py \
    --input results/field_0100.json \
    --quantity volume_fraction \
    --field phi \
    --threshold 0.5 \
    --json

# Compute flux through boundary
python scripts/derived_quantities.py \
    --input results/field_0100.json \
    --quantity boundary_flux \
    --field concentration \
    --boundary "x=0" \
    --json
```

### 7. Comparison with Reference

Compare simulation results to reference data:

```bash
# Compare to analytical solution
python scripts/comparison_tool.py \
    --simulation results/profile.json \
    --reference reference/analytical.json \
    --metric l2_error \
    --json

# Compare to experimental data
python scripts/comparison_tool.py \
    --simulation results/history.json \
    --reference experimental_data.csv \
    --metric rmse \
    --interpolate \
    --json

# Compare two simulations
python scripts/comparison_tool.py \
    --simulation results_fine/field.json \
    --reference results_coarse/field.json \
    --metric max_difference \
    --json
```

### 8. Report Generation

Generate automated reports:

```bash
# Generate summary report
python scripts/report_generator.py \
    --input results/ \
    --output report.json \
    --json

# Generate with specific sections
python scripts/report_generator.py \
    --input results/ \
    --sections "summary,statistics,convergence" \
    --output report.json \
    --json
```

## Typical Post-Processing Pipeline

For a complete simulation analysis:

```bash
# Step 1: Inventory available data
python scripts/field_extractor.py --input results/ --list --json

# Step 2: Extract final state statistics
python scripts/statistical_analyzer.py \
    --input results/field_final.json \
    --field phi \
    --json

# Step 3: Analyze convergence history
python scripts/time_series_analyzer.py \
    --input results/history.json \
    --quantity residual \
    --detect-steady-state \
    --json

# Step 4: Compute derived quantities
python scripts/derived_quantities.py \
    --input results/field_final.json \
    --quantity volume_fraction \
    --field phi \
    --json

# Step 5: Compare to reference (if available)
python scripts/comparison_tool.py \
    --simulation results/profile.json \
    --reference benchmark/expected.json \
    --metric l2_error \
    --json

# Step 6: Generate summary report
python scripts/report_generator.py \
    --input results/ \
    --output analysis_report.json \
    --json
```

## Interpretation Guidelines

### Time Series Analysis
- **Monotonic decrease** in energy: System approaching equilibrium
- **Oscillations** in residual: May indicate time step too large
- **Plateau** in quantities: Steady state reached
- **Sudden jumps**: Possible numerical instability

### Statistical Analysis
- **Bimodal distribution** of order parameter: Two-phase mixture
- **High variance**: Heterogeneous microstructure
- **Skewed distribution**: Asymmetric phase fractions

### Comparison Metrics
| Metric | Interpretation |
|--------|----------------|
| L2 error < 1% | Excellent agreement |
| L2 error 1-5% | Good agreement |
| L2 error 5-10% | Moderate agreement |
| L2 error > 10% | Poor agreement, investigate |

## Output Format

All scripts support `--json` flag for machine-readable output:

```json
{
    "script": "field_extractor",
    "version": "1.0.0",
    "input_file": "results/field_0100.json",
    "field": "concentration",
    "data": {
        "shape": [100, 100],
        "min": 0.1,
        "max": 0.9,
        "mean": 0.5
    },
    "values": [[...], [...]]
}
```

## References

For detailed information, see:

- `references/data_formats.md` - Supported input/output formats
- `references/statistical_methods.md` - Statistical analysis methods
- `references/derived_quantities_guide.md` - Physical quantity calculations
- `references/comparison_metrics.md` - Error metrics and interpretation

## Requirements

- Python 3.8+
- NumPy (for numerical operations)
- No other external dependencies for core functionality

## Version History

- v1.0.0 (2024-12-24): Initial release
