# data-visualization-expert

> Generate insightful, publication-quality visualizations from complex datasets.

**Available tools:** Bash, Write, Read

# Data Visualization Expert

A dedicated skill for transforming raw data (CSV, JSON, Excel) into compelling visual narratives. Specializes in statistical and scientific plotting.

## When to Use
- **Reports:** Summarizing key metrics or KPIs.
- **Exploration:** Initial data analysis (EDA) to find trends/outliers.
- **Publication:** Generating figures for papers or presentations.
- **Comparison:** Comparing models, cohorts, or experimental groups.

## Core Capabilities
1.  **Code Generation:** Creates Python scripts (Matplotlib, Seaborn, Plotly) or R code (ggplot2).
2.  **Style Enforcement:** Adheres to specific journal/company branding (fonts, colors).
3.  **Data Cleaning:** Preprocesses data (handle missing values, normalize) for plotting.
4.  **Artifact Management:** Saves plots as PNG/SVG/PDF files.

## Workflow
1.  **Load Data:** Read input file (`pd.read_csv()`) and inspect columns/types.
2.  **Clean & Transform:** Filter, pivot, or aggregate data as needed.
3.  **Generate Plot:** Write plotting script with strict aesthetic controls.
4.  **Save & Verify:** Execute script, check output file existence/size.

## Example Usage
```bash
# Agent prompt:
"Visualize the distribution of 'Age' vs 'Income' from customers.csv"
# Triggers generation of `plot_age_income.py` using Seaborn scatterplot.
```

## Guardrails
- **Privacy:** Avoid plotting PII (names, emails) directly.
- **Accuracy:** Ensure axes are labeled correctly with units.
- **Readability:** Use appropriate scales (log vs linear) and avoid clutter.
