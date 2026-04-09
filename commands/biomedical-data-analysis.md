# biomedical-data-analysis

> Omics data forge

**Available tools:** Bash, Read, python_repl

# Biomedical Data Analysis

Run the cross-language data analysis workflows (Python, R, SQL, Tableau/Power BI) described in this module to clean, analyze, and visualize biomedical datasets end-to-end.

## Workflow
1. **Scope request:** Identify analysis_type (`exploratory`, `statistical`, `predictive`, `visualization`) and required language/tooling.
2. **Acquire data:** Load from CSV/Parquet/SQL using pandas, tidyverse, or connectors described in `README.md`.
3. **Process:** Apply wrangling, descriptive stats, modeling, or SQL aggregations as listed in the capability tables.
4. **Visualize:** Choose Matplotlib/Seaborn/Plotly for inline plots or emit Tableau/Power BI specs per need.
5. **Document:** Provide code snippets + outputs, noting package versions and any assumptions.

## Guardrails
- Use reproducible scripts or notebooks—avoid manual spreadsheet edits.
- Keep PHI secure; when touching EHR-level SQL list filters minimizing data exposure.
- Clearly separate exploratory findings from validated statistical conclusions.

## References
- Capability tables, code samples, and parameter definitions live in `README.md` (plus `tutorials/README.md` for step-by-step lessons).
