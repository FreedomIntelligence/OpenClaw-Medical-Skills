# bio-reporting-jupyter-reports

> Creates reproducible Jupyter notebooks for bioinformatics analysis with parameterization using papermill. Use when generating automated analysis reports, running notebook-based pipelines, or creating shareable computational notebooks.

**Available tools:** Read, Bash

# Jupyter Reports with Papermill

## Parameterized Notebooks

```python
import papermill as pm

# Execute notebook with parameters
pm.execute_notebook(
    'analysis_template.ipynb',
    'output_report.ipynb',
    parameters={
        'input_file': 'data/counts.csv',
        'condition_col': 'treatment',
        'fdr_threshold': 0.05
    }
)
```

## Creating Parameterized Templates

Mark a cell with the `parameters` tag in Jupyter:

```python
# Parameters (tag this cell as "parameters")
input_file = 'default.csv'
output_dir = 'results/'
fdr_threshold = 0.05
```

## Batch Processing

```python
import papermill as pm
from pathlib import Path

samples = ['sample1', 'sample2', 'sample3']

for sample in samples:
    pm.execute_notebook(
        'qc_template.ipynb',
        f'reports/{sample}_qc.ipynb',
        parameters={'sample_id': sample}
    )
```

## Converting to HTML/PDF

```bash
# Single notebook
jupyter nbconvert --to html report.ipynb

# With execution
jupyter nbconvert --execute --to html report.ipynb

# PDF (requires pandoc + LaTeX)
jupyter nbconvert --to pdf report.ipynb
```

## Best Practices

- Keep analysis code in cells, explanatory text in markdown
- Use parameters for all configurable values
- Include version information and timestamps
- Clear outputs before committing to version control

## Related Skills

- reporting/quarto-reports - Alternative report format
- reporting/rmarkdown-reports - R-based reports
- workflows/rnaseq-to-de - Embed in workflows
