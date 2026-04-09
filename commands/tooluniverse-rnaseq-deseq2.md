# tooluniverse-rnaseq-deseq2

> Production-ready RNA-seq differential expression analysis using PyDESeq2. Performs DESeq2 normalization, dispersion estimation, Wald testing, LFC shrinkage, and result filtering. Handles multi-factor designs, multiple contrasts, batch effects, and integrates with gene enrichment (gseapy) and ToolUniverse annotation tools (UniProt, Ensembl, OpenTargets). Supports CSV/TSV/H5AD input formats and any organism. Use when analyzing RNA-seq count matrices, identifying DEGs, performing differential expression with statistical rigor, or answering questions about gene expression changes.

# RNA-seq Differential Expression Analysis (DESeq2)

Comprehensive differential expression analysis of RNA-seq count data using PyDESeq2, with integrated enrichment analysis (gseapy) and gene annotation via ToolUniverse.

**BixBench Coverage**: Validated on 53 BixBench questions across 15 computational biology projects covering RNA-seq, miRNA-seq, and differential expression analysis tasks.

---

## Core Principles

1. **Data-first approach** - Load and validate count data and metadata BEFORE any analysis
2. **Statistical rigor** - Always use proper normalization, dispersion estimation, and multiple testing correction
3. **Flexible design** - Support single-factor, multi-factor, and interaction designs
4. **Threshold awareness** - Apply user-specified thresholds exactly (padj, log2FC, baseMean)
5. **Reproducible** - Set random seeds, document all parameters, output complete results
6. **Question-driven** - Parse what the user is actually asking and extract the specific answer
7. **Enrichment integration** - Chain DESeq2 results into pathway/GO enrichment when requested
8. **English-first queries** - Use English gene/pathway names in all tool calls

---

## When to Use This Skill

Apply when users:
- Have RNA-seq count matrices and want differential expression analysis
- Ask about DESeq2, DEGs, differential expression, padj, log2FC
- Need dispersion estimates or diagnostics
- Want enrichment analysis (GO, KEGG, Reactome) on DEGs
- Ask about specific gene expression changes between conditions
- Need to compare multiple strains/conditions/treatments
- Ask about batch effect correction in RNA-seq
- Questions mention "count data", "count matrix", "RNA-seq", "transcriptomics"

---

## Required Packages

```python
# Core (MUST be installed)
import pandas as pd
import numpy as np
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# Enrichment (optional, for GO/KEGG/Reactome)
import gseapy as gp

# ToolUniverse (optional, for gene annotation)
from tooluniverse import ToolUniverse
```

**Installation**:
```bash
pip install pydeseq2 gseapy pandas numpy scipy anndata
```

---

## Analysis Workflow

### Step 1: Question Parsing

**CRITICAL FIRST STEP**: Before writing ANY code, parse the question to identify:

- **Data files**: Look for `*counts*.csv`, `*metadata*.csv`, `*.h5ad`
- **Thresholds**: Extract padj (default 0.05), log2FC (default 0), baseMean (default 0)
- **Design**: Identify factors mentioned ("strain", "condition", "batch")
- **Contrast**: Determine comparison ("A vs B", "mutant vs wildtype")
- **Direction**: Check if "upregulated", "downregulated", or both
- **Enrichment**: Look for "GO", "KEGG", "Reactome", "pathway"
- **Specific genes**: Check if asking about individual genes

See [references/question_parsing.md](references/question_parsing.md) for detailed parsing patterns.

### Step 1.5: Design Formula Decision Tree ⚠️ CRITICAL

**ALWAYS inspect metadata for ALL variables, not just what the question mentions!**

Many experiments have hidden batch effects (media conditions, sequencing batches, time points) that MUST be included as covariates. Failing to account for these reduces statistical power and can lead to incorrect results.

**Decision process**:
1. **List ALL metadata columns** (don't skip any!)
2. **Categorize each column**:
   - **Biological interest**: The factor you're testing (strain, treatment, genotype, condition)
   - **Batch/Block**: Systematic covariates (media, batch, sequencing_run, time, plate)
   - **Irrelevant**: Sample IDs, notes, file names
3. **Design formula**:
   - Single factor: `~condition` (only if no batch variables exist)
   - With covariates: `~batch1 + batch2 + condition` (covariates first!)
   - Interaction: `~batch + factor1 + factor2 + factor1:factor2`

**Example** (critical real-world case):
```
Metadata columns: [Strain, Media, Replicate]
Question asks: "strain effects"

❌ WRONG: design="~Strain" (ignores Media!)
✅ CORRECT: design="~Media + Strain" (accounts for media variation)

Why: Even though question doesn't mention media, it systematically
affects expression. DESeq2 must remove media effects to properly test strain.
```

**Rule of thumb**: If a column has 2+ levels and represents an experimental condition (not sample ID), include it in design.

### Step 2: Data Loading & Validation

Load count matrix and metadata, then validate alignment:

```python
import pandas as pd
from scripts.load_count_matrix import load_count_matrix, validate_inputs

# Load data
counts = load_count_matrix("counts.csv")
metadata = pd.read_csv("metadata.csv", index_col=0)

# Validate and align
counts, metadata, issues = validate_inputs(counts, metadata)
```

**Key considerations**:
- Ensure samples as rows, genes as columns (PyDESeq2 requirement)
- Verify integer counts (round if needed)
- Align sample names between counts and metadata
- Remove zero-count genes

See [references/data_loading.md](references/data_loading.md) for detailed data handling.

### Step 2.5: Inspect Metadata Structure ⚠️ REQUIRED

Before choosing design formula, ALWAYS inspect metadata to identify all experimental factors:

```python
# Print metadata structure
print("Metadata columns and levels:")
for col in metadata.columns:
    unique_vals = metadata[col].unique()
    print(f"  {col}: {len(unique_vals)} levels → {list(unique_vals)[:5]}")

# Example output:
#   Strain: 4 levels → ['1', '97', '98', '99']
#   Media: 3 levels → ['MMGluFeMinus', 'MMGluFePlus', 'Succinate']
#   Replicate: 3 levels → ['A', 'B', 'C']

# Decision:
#   - Strain: Biological factor (testing)
#   - Media: Batch/covariate (MUST include!)
#   - Replicate: Biological replicate (don't include as factor)
# Design: ~Media + Strain
```

This step prevents missing hidden batch effects that could invalidate your analysis.

### Step 3: Run PyDESeq2

Execute differential expression analysis:

```python
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# Setup design (set reference level first)
metadata['condition'] = pd.Categorical(
    metadata['condition'],
    categories=['control', 'treatment']  # First = reference
)

# Run DESeq2
dds = DeseqDataSet(
    counts=counts,
    metadata=metadata,
    design="~condition",
    quiet=True
)
dds.deseq2()

# Extract results
stat_res = DeseqStats(dds, contrast=['condition', 'treatment', 'control'], quiet=True)
stat_res.run_wald_test()
stat_res.summary()

# Apply LFC shrinkage (if needed)
stat_res.lfc_shrink(coeff='condition[T.treatment]')

results = stat_res.results_df
```

#### Multi-Factor Design (Common Real-World Case)

When metadata has multiple experimental variables (e.g., strain + media conditions), ALWAYS include covariates:

```python
# Inspect metadata (from Step 2.5) showed:
#   - Strain: 4 levels (factor of interest)
#   - Media: 3 levels (batch effect - MUST include!)

# Set reference levels for BOTH factors
metadata['media'] = pd.Categorical(
    metadata['media'],
    categories=['MMGluFeMinus', 'MMGluFePlus', 'Succinate']  # First = reference
)
metadata['strain'] = pd.Categorical(
    metadata['strain'],
    categories=['1', '97', '98', '99']  # First = reference (JBX1)
)

# Include covariate in design formula
dds = DeseqDataSet(
    counts=counts,
    metadata=metadata,
    design="~media + strain",  # Covariate first, then factor!
    quiet=True
)
dds.deseq2()

# Extract strain effect (controlling for media)
stat_res = DeseqStats(dds, contrast=['strain', '98', '1'], quiet=True)
stat_res.run_wald_test()
stat_res.summary()
results = stat_res.results_df
```

**Why this matters**: DESeq2 will model media effects separately, removing media-driven variance before testing strain differences. This increases statistical power and prevents false positives/negatives.

**When to use what**:
- **Python (PyDESeq2)**: Use for ALL DESeq2 analysis (normalization, testing, filtering)
- **ToolUniverse**: Use ONLY for gene annotation (ID conversion, pathway context)
- **gseapy**: Use for enrichment analysis (GO/KEGG/Reactome)

See [references/pydeseq2_workflow.md](references/pydeseq2_workflow.md) for complete PyDESeq2 patterns including batch effects, interaction terms, and complex designs.

### Step 4: Filter Results

Apply thresholds from the question:

```python
# Filter DEGs
sig_genes = results[
    (results['padj'] < 0.05) &
    (results['log2FoldChange'].abs() > 0.5) &
    (results['baseMean'] > 10)
]

# Direction-specific filtering
up_genes = sig_genes[sig_genes['log2FoldChange'] > 0]
down_genes = sig_genes[sig_genes['log2FoldChange'] < 0]
```

**Common filtering patterns**:
- Basic DEG count: `len(sig_genes)`
- Specific gene value: `results.loc['GENE_NAME', 'log2FoldChange']`
- Set operations: Use Python sets for "unique", "shared", "overlap"

See [references/result_filtering.md](references/result_filtering.md) for advanced filtering.

### Step 5: Dispersion Analysis (if asked)

Access dispersion estimates:

```python
# Get dispersion data
disp_data = dds.var  # Dispersions stored here

# Common question: "genes below threshold prior to fitting"
genewise = dds.var['genewise_dispersions']
count_below = (genewise < 1e-5).sum()
```

**Dispersion column mapping**:
- "prior to fitting" → `genewise_dispersions`
- "fitted dispersions" → `fitted_dispersions`
- "after shrinkage" / "MAP" → `MAP_dispersions`
- "final" → `dispersions`

See [references/dispersion_analysis.md](references/dispersion_analysis.md) for diagnostics.

### Step 6: Enrichment Analysis (optional)

Run pathway enrichment on DEGs:

```python
import gseapy as gp

# Prepare gene list
gene_list = sig_genes.index.tolist()

# Run enrichment
enr = gp.enrich(
    gene_list=gene_list,
    gene_sets='GO_Biological_Process_2023',  # or KEGG, Reactome
    background=None,  # or specify background
    outdir=None,
    cutoff=0.05,
    no_plot=True,
    verbose=False
)

# Extract results
top_pathways = enr.results.head(10)
```

**Library selection**:
- Human GO: `GO_Biological_Process_2023`
- Mouse KEGG: `KEGG_2019_Mouse`
- Human KEGG: `KEGG_2021_Human`
- Reactome: `Reactome_2022`

See [references/enrichment_analysis.md](references/enrichment_analysis.md) for complete enrichment workflows.

### Step 7: Gene Annotation with ToolUniverse (optional)

Use ToolUniverse ONLY for gene annotation, not analysis:

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Gene ID conversion
result = tu.tools.MyGene_query_genes(query="TP53")

# Gene details
result = tu.tools.ensembl_lookup_gene(
    gene_id="ENSG00000141510",
    species="homo_sapiens"
)
```

**Do NOT use ToolUniverse for**:
- Differential expression (use PyDESeq2)
- Statistical testing (use scipy.stats)
- Enrichment analysis (use gseapy)

---

## Output Formatting

Match the question's requested format:

```python
# Numeric precision
round(value, 2)  # "2 decimal points"
f"{value:.2E}"   # "scientific notation"

# Percentages
f"{value * 100:.1f}%"  # "as percentage"

# Counts (no decimals)
int(len(sig_genes))  # "how many genes"
```

See [references/output_formatting.md](references/output_formatting.md) for all format patterns.

---

## Common BixBench Patterns

### Pattern 1: Basic DEG Count
**Question**: "How many genes show significant DE (padj < 0.05, |log2FC| > 0.5)?"

```python
degs = results[(results['padj'] < 0.05) & (results['log2FoldChange'].abs() > 0.5)]
answer = len(degs)
```

### Pattern 2: Specific Gene Value
**Question**: "What is the log2FC of gene X?"

```python
answer = round(results.loc['GENE_X', 'log2FoldChange'], 2)
```

### Pattern 3: Direction-Specific
**Question**: "How many genes are upregulated?"

```python
up_degs = results[(results['padj'] < 0.05) & (results['log2FoldChange'] > 0)]
answer = len(up_degs)
```

### Pattern 4: Set Operations
**Question**: "How many genes are uniquely DE in condition A?"

```python
degs_A = set(results_A[results_A['padj'] < 0.05].index)
degs_B = set(results_B[results_B['padj'] < 0.05].index)
unique_A = degs_A - degs_B
answer = len(unique_A)
```

### Pattern 5: Dispersion Count
**Question**: "How many genes have dispersion below 1e-5 prior to fitting?"

```python
genewise = dds.var['genewise_dispersions']
answer = (genewise < 1e-5).sum()
```

See [references/bixbench_examples.md](references/bixbench_examples.md) for all 10 patterns with examples.

---

## Error Handling

| Error | Solution |
|-------|----------|
| "No matching samples" | Check if counts need transposing; strip whitespace |
| "Dispersion trend did not converge" | Use `fit_type='mean'` |
| "Contrast not found" | Check `metadata['factor'].unique()` for exact names |
| "Non-integer counts" | Round to integers OR use t-test for normalized data |
| "NaN in padj" | Independent filtering removed genes; exclude from counts |

See [references/troubleshooting.md](references/troubleshooting.md) for complete debugging guide.

---

## Validation Checklist

Every analysis MUST include:

**Data Loading**:
- [ ] Count matrix oriented correctly (samples as rows, genes as columns)
- [ ] Metadata aligned with counts
- [ ] Integer counts validated

**DESeq2 Analysis**:
- [ ] Design formula matches question
- [ ] Reference level set correctly (first in Categorical)
- [ ] Correct contrast extracted

**Results**:
- [ ] Thresholds match question exactly
- [ ] Direction filter applied if specified
- [ ] Answer formatted correctly (decimal places, notation)

**Quality Checks**:
- [ ] DEG count is reasonable
- [ ] P-values between 0 and 1
- [ ] Log2FC values are finite

---

## Known Limitations

### PyDESeq2 vs R DESeq2 Differences

This skill uses **PyDESeq2** (Python implementation) for differential expression analysis. While PyDESeq2 faithfully implements the DESeq2 algorithm, numerical differences exist between Python and R implementations:

**Dispersion Estimation**:
- Dispersion estimates may differ from R DESeq2, especially for very low dispersion genes (< 1e-05)
- This is due to different numerical optimization methods between Python and R statistical libraries
- Results are still statistically valid and biologically meaningful
- If you need exact R DESeq2 dispersions for benchmark reproducibility, consider using R DESeq2 directly via rpy2

**For Most Analyses**: PyDESeq2 provides accurate, publication-quality results. The differences are in numerical precision, not statistical validity.

### GO/KEGG Enrichment (gseapy vs clusterProfiler)

Enrichment analysis uses **Python gseapy** by default. Results may differ from **R clusterProfiler** due to:
- Different enrichment algorithms and statistical tests
- Different GO/KEGG database versions
- Different term simplification/redundancy removal methods

**For R clusterProfiler Compatibility**:
If you need results matching R clusterProfiler exactly (e.g., for benchmark reproducibility):

```python
# Install rpy2 and R packages first:
# pip install rpy2
# In R: install.packages(c("clusterProfiler", "org.Hs.eg.db", "enrichplot"))

from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri, vectors
pandas2ri.activate()

# Load R packages
clusterProfiler = importr('clusterProfiler')
orgdb = importr('org.Hs.eg.db')

# Convert Python gene list to R vector
gene_list = sig_genes.index.tolist()
r_genes = vectors.StrVector(gene_list)

# Run enrichGO (R's clusterProfiler)
enrich_result = clusterProfiler.enrichGO(
    gene=r_genes,
    OrgDb=orgdb.org_Hs_eg_db,
    ont='BP',  # Biological Process
    pAdjustMethod='BH',
    pvalueCutoff=0.05,
    qvalueCutoff=0.2
)

# Apply simplify to remove redundant terms
simplified = clusterProfiler.simplify(enrich_result, cutoff=0.7, by='p.adjust')

# Convert R result back to pandas
results_df = pandas2ri.rpy2py(simplified)
```

**Default behavior**: Uses gseapy (no R dependencies required). This is sufficient for most analyses and provides valid enrichment results.

**When to use R clusterProfiler**:
- When exact reproducibility with R-based benchmarks is required
- When collaborating with R users who need identical results
- When specific clusterProfiler features (GSEA, compareCluster) are needed

---

## References

Detailed documentation for advanced topics:

- [question_parsing.md](references/question_parsing.md) - Extract parameters from questions
- [data_loading.md](references/data_loading.md) - Data loading and validation patterns
- [pydeseq2_workflow.md](references/pydeseq2_workflow.md) - Complete PyDESeq2 code examples
- [result_filtering.md](references/result_filtering.md) - Advanced filtering and extraction
- [dispersion_analysis.md](references/dispersion_analysis.md) - Dispersion diagnostics
- [enrichment_analysis.md](references/enrichment_analysis.md) - GO/KEGG/Reactome workflows
- [output_formatting.md](references/output_formatting.md) - Format answers correctly
- [bixbench_examples.md](references/bixbench_examples.md) - All 10 question patterns
- [troubleshooting.md](references/troubleshooting.md) - Common issues and debugging

## Utility Scripts

Helper scripts for common tasks:

- [format_deseq2_output.py](scripts/format_deseq2_output.py) - Output formatters
- [load_count_matrix.py](scripts/load_count_matrix.py) - Data loading utilities
