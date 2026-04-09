# tooluniverse-phylogenetics

> Production-ready phylogenetics and sequence analysis skill for alignment processing, tree analysis, and evolutionary metrics. Computes treeness, RCV, treeness/RCV, parsimony informative sites, evolutionary rate, DVMC, tree length, alignment gap statistics, GC content, and bootstrap support using PhyKIT, Biopython, and DendroPy. Performs NJ/UPGMA/parsimony tree construction, Robinson-Foulds distance, Mann-Whitney U tests, and batch analysis across gene families. Integrates with ToolUniverse for sequence retrieval (NCBI, UniProt, Ensembl) and tree annotation. Use when processing FASTA/PHYLIP/Nexus/Newick files, computing phylogenetic metrics, comparing taxa groups, or answering questions about alignments, trees, parsimony, or molecular evolution.

# Phylogenetics and Sequence Analysis

Comprehensive phylogenetics and sequence analysis using PhyKIT, Biopython, and DendroPy. Designed for bioinformatics questions about multiple sequence alignments, phylogenetic trees, parsimony, molecular evolution, and comparative genomics.

**IMPORTANT**: This skill handles complex phylogenetic workflows. Most implementation details have been moved to `references/` for progressive disclosure. This document focuses on high-level decision-making and workflow orchestration.

---

## When to Use This Skill

Apply when users:
- Have FASTA alignment files and ask about parsimony informative sites, gaps, or alignment quality
- Have Newick tree files and ask about treeness, tree length, evolutionary rate, or DVMC
- Ask about treeness/RCV, RCV, or relative composition variability
- Need to compare phylogenetic metrics between groups (fungi vs animals, etc.)
- Ask about PhyKIT functions (treeness, rcv, dvmc, evo_rate, parsimony_informative, tree_length)
- Have gene family data with paired alignments and trees
- Need Mann-Whitney U tests or other statistical comparisons of phylogenetic metrics
- Ask about bootstrap support, branch lengths, or tree topology
- Need to build trees (NJ, UPGMA, parsimony) from alignments
- Ask about Robinson-Foulds distance or tree comparison

**BixBench Coverage**: 33 questions across 8 projects (bix-4, bix-11, bix-12, bix-25, bix-35, bix-38, bix-45, bix-60)

**NOT for** (use other skills instead):
- Multiple sequence alignment generation → Use external tools (MUSCLE, MAFFT, ClustalW)
- Maximum Likelihood tree construction → Use IQ-TREE, RAxML, or PhyML
- Bayesian phylogenetics → Use MrBayes or BEAST
- Ancestral state reconstruction → Use separate tools

---

## Core Principles

1. **Data-first approach** - Discover and validate all input files (alignments, trees) before any analysis
2. **PhyKIT-compatible** - Use PhyKIT functions for treeness, RCV, DVMC, parsimony, evolutionary rate (matches BixBench expected outputs)
3. **Format-flexible** - Support FASTA, PHYLIP, Nexus, Newick, and auto-detect formats
4. **Batch processing** - Process hundreds of gene alignments/trees in a single analysis
5. **Statistical rigor** - Mann-Whitney U, medians, percentiles, standard deviations with scipy.stats
6. **Precision awareness** - Match rounding to 4 decimal places (PhyKIT default) or as requested
7. **Group comparison** - Compare metrics between taxa groups (e.g., fungi vs animals)
8. **Question-driven** - Parse exactly what is asked and return the specific number/statistic

---

## Required Python Packages

```python
# Core (MUST be installed)
import numpy as np
import pandas as pd
from scipy import stats
from Bio import AlignIO, Phylo, SeqIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

# PhyKIT (primary computation engine)
from phykit.services.tree.treeness import Treeness
from phykit.services.tree.total_tree_length import TotalTreeLength
from phykit.services.tree.evolutionary_rate import EvolutionaryRate
from phykit.services.tree.dvmc import DVMC
from phykit.services.tree.treeness_over_rcv import TreenessOverRCV
from phykit.services.alignment.parsimony_informative_sites import ParsimonyInformative
from phykit.services.alignment.rcv import RelativeCompositionVariability

# DendroPy (for advanced tree operations)
import dendropy

# ToolUniverse (for sequence retrieval)
from tooluniverse import ToolUniverse
```

**Installation**:
```bash
pip install phykit dendropy biopython pandas numpy scipy
```

---

## High-Level Workflow Decision Tree

```
START: User question about phylogenetic data
│
├─ Q1: What type of analysis is needed?
│  │
│  ├─ ALIGNMENT ANALYSIS (FASTA/PHYLIP files)
│  │  ├─ Parsimony informative sites → phykit_parsimony_informative()
│  │  ├─ RCV score → phykit_rcv()
│  │  ├─ Gap percentage → alignment_gap_percentage()
│  │  ├─ GC content → alignment_statistics()
│  │  └─ See: references/sequence_alignment.md
│  │
│  ├─ TREE ANALYSIS (Newick files)
│  │  ├─ Treeness → phykit_treeness()
│  │  ├─ Tree length → phykit_tree_length()
│  │  ├─ Evolutionary rate → phykit_evolutionary_rate()
│  │  ├─ DVMC → phykit_dvmc()
│  │  ├─ Bootstrap support → extract_bootstrap_support()
│  │  └─ See: references/tree_building.md
│  │
│  ├─ COMBINED ANALYSIS (alignment + tree)
│  │  └─ Treeness/RCV → phykit_treeness_over_rcv()
│  │
│  ├─ TREE CONSTRUCTION (build from alignment)
│  │  ├─ Neighbor-Joining → build_nj_tree()
│  │  ├─ UPGMA → build_upgma_tree()
│  │  ├─ Parsimony → build_parsimony_tree()
│  │  └─ See: references/tree_building.md
│  │
│  ├─ GROUP COMPARISON (fungi vs animals, etc.)
│  │  ├─ Batch compute metrics per group
│  │  ├─ Mann-Whitney U test
│  │  ├─ Summary statistics (median, mean, percentiles)
│  │  └─ See: references/parsimony_analysis.md
│  │
│  └─ TREE COMPARISON
│     ├─ Robinson-Foulds distance → robinson_foulds_distance()
│     └─ Bootstrap consensus → bootstrap_analysis()
│
├─ Q2: What data format is available?
│  ├─ FASTA (.fa, .fasta, .faa, .fna)
│  ├─ PHYLIP (.phy, .phylip) - Use phylip-relaxed for long names
│  ├─ Nexus (.nex, .nexus)
│  ├─ Newick (.nwk, .newick, .tre, .tree)
│  └─ Auto-detect with load_alignment() or load_tree()
│
└─ Q3: Is this a batch analysis?
   ├─ Single gene → Run metric function once
   ├─ Multiple genes → Use batch_compute_metric()
   └─ Group comparison → Use discover_gene_files() + compare_groups()
```

---

## Quick Reference: Common Metrics

| Metric | Function | Input | Description |
|--------|----------|-------|-------------|
| **Treeness** | `phykit_treeness(tree_file)` | Newick | Internal branch length / Total branch length |
| **RCV** | `phykit_rcv(aln_file)` | FASTA/PHYLIP | Relative Composition Variability |
| **Treeness/RCV** | `phykit_treeness_over_rcv(tree, aln)` | Both | Treeness divided by RCV |
| **Tree Length** | `phykit_tree_length(tree_file)` | Newick | Sum of all branch lengths |
| **Evolutionary Rate** | `phykit_evolutionary_rate(tree_file)` | Newick | Total branch length / num terminals |
| **DVMC** | `phykit_dvmc(tree_file)` | Newick | Degree of Violation of Molecular Clock |
| **Parsimony Sites** | `phykit_parsimony_informative(aln_file)` | FASTA/PHYLIP | Sites with ≥2 chars appearing ≥2 times |
| **Gap Percentage** | `alignment_gap_percentage(aln_file)` | FASTA/PHYLIP | Percentage of gap characters |

See `scripts/tree_statistics.py` for implementation.

---

## Common Analysis Patterns (BixBench)

### Pattern 1: Single Metric Across Groups

**Question**: "What is the median DVMC for fungi vs animals?"

**Workflow**:
```python
# 1. Discover files
fungi_genes = discover_gene_files("data/fungi")
animal_genes = discover_gene_files("data/animals")

# 2. Compute metric
fungi_dvmc = batch_dvmc(fungi_genes)
animal_dvmc = batch_dvmc(animal_genes)

# 3. Compare
fungi_values = list(fungi_dvmc.values())
animal_values = list(animal_dvmc.values())

print(f"Fungi median DVMC: {np.median(fungi_values):.4f}")
print(f"Animal median DVMC: {np.median(animal_values):.4f}")
```

**See**: `references/parsimony_analysis.md` for full implementation

### Pattern 2: Statistical Comparison

**Question**: "What is the Mann-Whitney U statistic comparing treeness between groups?"

**Workflow**:
```python
from scipy import stats

# Compute treeness for both groups
group1_treeness = batch_treeness(group1_genes)
group2_treeness = batch_treeness(group2_genes)

# Mann-Whitney U test (two-sided)
u_stat, p_value = stats.mannwhitneyu(
    list(group1_treeness.values()),
    list(group2_treeness.values()),
    alternative='two-sided'
)

print(f"U statistic: {u_stat:.0f}")
print(f"P-value: {p_value:.4e}")
```

### Pattern 3: Filtering + Metric

**Question**: "What is the treeness/RCV for alignments with <5% gaps?"

**Workflow**:
```python
# 1. Filter by gap percentage
valid_genes = []
for entry in gene_files:
    if 'aln_file' in entry:
        gap_pct = alignment_gap_percentage(entry['aln_file'])
        if gap_pct < 5.0:
            valid_genes.append(entry)

# 2. Compute metric on filtered set
results = batch_treeness_over_rcv(valid_genes)

# 3. Report
values = [r[0] for r in results.values()]  # treeness/rcv ratio
print(f"Median treeness/RCV: {np.median(values):.4f}")
```

### Pattern 4: Specific Gene Lookup

**Question**: "What is the evolutionary rate for gene X?"

**Workflow**:
```python
# Find gene file
gene_files = discover_gene_files("data/")
gene_entry = [g for g in gene_files if g['gene_id'] == 'X'][0]

# Compute metric
evo_rate = phykit_evolutionary_rate(gene_entry['tree_file'])

print(f"Evolutionary rate for gene X: {evo_rate:.4f}")
```

---

## Choosing Methods: When to Use What

### Alignment Methods

**When building alignments** (use external tools, not this skill):

| Method | Speed | Accuracy | Use Case |
|--------|-------|----------|----------|
| **ClustalW** | Slow | Medium | Small datasets (<100 sequences), educational |
| **MUSCLE** | Fast | High | Medium datasets (100-1000 sequences) |
| **MAFFT** | Very Fast | Very High | **Recommended** - Large datasets (>1000 sequences) |

**For this skill**: Work with pre-aligned sequences. Use `load_alignment()` to read any format.

### Tree Building Methods

**When to use which tree method:**

| Method | Speed | Accuracy | Use Case |
|--------|-------|----------|----------|
| **Neighbor-Joining** | Fast | Medium | Quick trees, large datasets, exploratory |
| **UPGMA** | Fast | Low | Assumes molecular clock, special cases only |
| **Maximum Parsimony** | Medium | Medium | Small datasets, discrete characters |
| **Maximum Likelihood** | Slow | High | **Use external tools** (IQ-TREE, RAxML) for production |

**Implementation in this skill**:
```python
# Fast distance-based trees
tree = build_nj_tree("alignment.fa")  # Neighbor-Joining
tree = build_upgma_tree("alignment.fa")  # UPGMA

# Parsimony (for small alignments)
tree = build_parsimony_tree("alignment.fa")
```

**For production ML trees**: Use IQ-TREE or RAxML externally, then analyze with this skill.

See `references/tree_building.md` for detailed implementations.

---

## Batch Processing

### Discovering Gene Files

```python
# Auto-discover paired alignment + tree files
gene_files = discover_gene_files("data/")

# Result: list of dicts with 'gene_id', 'aln_file', 'tree_file'
# [
#   {'gene_id': 'gene1', 'aln_file': 'gene1.fa', 'tree_file': 'gene1.nwk'},
#   {'gene_id': 'gene2', 'aln_file': 'gene2.fa', 'tree_file': 'gene2.nwk'},
#   ...
# ]
```

### Computing Metrics in Batch

```python
# Tree metrics
treeness_results = batch_treeness(gene_files)
tree_length_results = batch_tree_length(gene_files)
dvmc_results = batch_dvmc(gene_files)
evo_rate_results = batch_evolutionary_rate(gene_files)

# Alignment metrics
rcv_results = batch_rcv(gene_files)
pi_results = batch_parsimony_informative(gene_files)
gap_results = batch_gap_percentage(gene_files)

# Combined metrics
treeness_rcv_results = batch_treeness_over_rcv(gene_files)

# All return dict: {gene_id: value}
```

### Statistical Analysis

```python
# Summary statistics
stats = summary_stats(list(treeness_results.values()))
# Returns: {'mean': ..., 'median': ..., 'std': ..., 'min': ..., 'max': ...}

# Group comparison
comparison = compare_groups(
    list(fungi_treeness.values()),
    list(animal_treeness.values()),
    group1_name="Fungi",
    group2_name="Animals"
)
# Returns: {'u_statistic': ..., 'p_value': ..., 'Fungi': {...}, 'Animals': {...}}
```

See `references/parsimony_analysis.md` for full workflow.

---

## Answer Extraction for BixBench

| Question Pattern | Extraction Method |
|-----------------|-------------------|
| "What is the median X?" | `np.median(values)` |
| "What is the maximum X?" | `np.max(values)` |
| "What is the difference between median X for A vs B?" | `abs(np.median(a) - np.median(b))` |
| "What percentage of X have Y above Z?" | `sum(v > Z for v in values) / len(values) * 100` |
| "What is the Mann-Whitney U statistic?" | `stats.mannwhitneyu(a, b)[0]` |
| "What is the p-value?" | `stats.mannwhitneyu(a, b)[1]` |
| "What is the X value for gene Y?" | `results[gene_id]` |
| "What is the fold-change in median X?" | `np.median(a) / np.median(b)` |
| "multiplied by 1000" | `round(value * 1000)` |

### Rounding Rules

- **PhyKIT default**: 4 decimal places
- **Percentages**: Match question format (e.g., "35%" → integer, "3.5%" → 1 decimal)
- **P-values**: Scientific notation for very small values
- **U statistics**: Integer (no decimals)
- **Always check question wording**: "rounded to 3 decimal places" overrides defaults

---

## BixBench Question Coverage

| Project | Questions | Metrics |
|---------|-----------|---------|
| **bix-4** | 7 | DVMC analysis (fungi vs animals) |
| **bix-11** | 6 | Treeness analysis (median, percentages, Mann-Whitney U) |
| **bix-12** | 5 | Parsimony informative sites (counts, percentages, ratios) |
| **bix-25** | 2 | Treeness/RCV with gap filtering |
| **bix-35** | 4 | Evolutionary rate (specific genes, comparisons) |
| **bix-38** | 5 | Tree length (fold-change, variance, paired ratios) |
| **bix-45** | 4 | RCV (Mann-Whitney U, medians, paired differences) |
| **bix-60** | 1 | Average treeness across multiple trees |

---

## ToolUniverse Integration

### Sequence Retrieval

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Get sequences from NCBI
result = tu.tools.NCBI_get_sequence(accession="NP_000546")

# Get gene tree from Ensembl
tree_result = tu.tools.EnsemblCompara_get_gene_tree(gene="ENSG00000141510")

# Get species tree from OpenTree
tree_result = tu.tools.OpenTree_get_induced_subtree(ott_ids="770315,770319")
```

---

## File Structure

```
tooluniverse-phylogenetics/
├── SKILL.md                           # This file (workflow orchestration)
├── QUICK_START.md                     # Quick reference
├── test_phylogenetics.py             # Comprehensive test suite
├── references/
│   ├── sequence_alignment.md         # Alignment analysis details
│   ├── tree_building.md              # Tree construction methods
│   ├── parsimony_analysis.md         # Statistical comparison workflows
│   └── troubleshooting.md            # Common issues and solutions
└── scripts/
    ├── format_alignment.py           # Alignment format conversion
    └── tree_statistics.py            # Core metric implementations
```

---

## Completeness Checklist

Before returning your answer, verify:

- [ ] Identified all input files (alignments and/or trees)
- [ ] Detected group structure (fungi/animals/etc.) if applicable
- [ ] Used correct PhyKIT function for the requested metric
- [ ] Processed ALL genes in each group (not just a sample)
- [ ] Applied correct statistical test if comparison requested
- [ ] Used correct rounding (4 decimals default, or as specified)
- [ ] Returned the specific statistic asked for (median, max, U stat, p-value, etc.)
- [ ] For percentage questions, confirmed whether answer is integer or decimal
- [ ] For "difference" questions, confirmed direction (A - B vs abs difference)
- [ ] For Mann-Whitney U, used `alternative='two-sided'` (default in scipy)

---

## Next Steps

- For detailed alignment analysis workflows → See `references/sequence_alignment.md`
- For tree construction methods → See `references/tree_building.md`
- For statistical comparison examples → See `references/parsimony_analysis.md`
- For common errors and solutions → See `references/troubleshooting.md`
- For script implementations → See `scripts/tree_statistics.py`

---

## Support

For issues with:
- **PhyKIT functions**: Check PhyKIT documentation at https://jlsteenwyk.com/PhyKIT/
- **Biopython tree/alignment parsing**: See https://biopython.org/wiki/Phylo
- **DendroPy operations**: See https://dendropy.org/
- **ToolUniverse integration**: Check ToolUniverse documentation

## License

Same as ToolUniverse framework license.
