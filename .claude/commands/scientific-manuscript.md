# scientific-manuscript

> High-impact scientific manuscript preparation for journals like Nature, Blood, Cell. Use when writing abstracts, introductions, methods, results, discussions, or figure legends. Includes citation management, statistical reporting standards, ICMJE guidelines, and journal-specific formatting for hematology/oncology publications.

# Scientific Manuscript Preparation

## Document Structure for High-Impact Journals

### Title
- Concise (<15 words for Nature, <20 for Blood)
- Include key finding and system/disease
- Avoid jargon and abbreviations

### Abstract (Structured for Blood/Clinical Journals)

```markdown
**Background:** One sentence on knowledge gap.
**Methods:** Key approaches, patient cohort size, techniques.
**Results:** Primary findings with statistics (P values, CIs).
**Conclusions:** Clinical/translational significance.
```

### Introduction (~500-800 words)
1. **Paragraph 1**: Broad context, disease burden, clinical relevance
2. **Paragraph 2**: Current knowledge, key mechanisms
3. **Paragraph 3**: Knowledge gap, unanswered questions
4. **Paragraph 4**: Study aims, hypothesis, approach overview

### Methods (Detailed, Reproducible)

```markdown
**Patient Cohort and Samples**
- IRB approval number, consent process
- Inclusion/exclusion criteria
- Sample processing, storage conditions

**Single-Cell RNA Sequencing**
- Library preparation (10x Genomics Chromium 3' v3.1)
- Sequencing platform, read depth
- Quality metrics (cells/sample, genes/cell, % mitochondrial)

**Computational Analysis**
- Software versions (Scanpy 1.9.x, scvi-tools 0.20.x)
- QC thresholds (min genes, max %MT)
- Integration method (TotalVI, Harmony)
- Clustering parameters (resolution, n_neighbors)
- Differential expression (Wilcoxon, FDR < 0.05, |log2FC| > 1)

**Statistical Analysis**
- Software (R 4.3.x, Python 3.11)
- Tests used with justification
- Multiple testing correction method
- Power analysis if applicable
```

### Results (~2000-3000 words)
- Lead each paragraph with key finding
- Reference figures in order (Figure 1A-C...)
- Report exact P values (P = 0.003, not P < 0.05)
- Include confidence intervals where relevant
- Avoid interpretation; save for Discussion

### Discussion (~1500-2000 words)

```markdown
**Paragraph 1**: Summarize key findings, relate to hypothesis

**Paragraph 2-4**: Compare to existing literature
- "Consistent with [Author et al.], we found..."
- "In contrast to [Study], our analysis revealed..."
- Mechanistic interpretation

**Paragraph 5**: Translational/Clinical implications
- Therapeutic targets
- Biomarkers
- Patient stratification

**Paragraph 6**: Limitations
- Sample size, cohort characteristics
- Technical limitations
- Generalizability

**Paragraph 7**: Future directions and conclusion
```

## Statistical Reporting Standards

### Continuous Variables
- Mean ± SD (normal) or Median [IQR] (non-normal)
- Report normality test used

### Categorical Variables
- N (%) with comparison test

### P Values
- Report exact values (P = 0.023)
- For very small: P < 0.0001
- Always report test used

### Sample Sizes
- "n = X patients" or "n = X cells"
- Report for each comparison group

## Figure Legends Template

```markdown
**Figure 1. Title describes main finding**
(A) Brief description of panel A. Statistical test, P value.
(B) Description including axis labels if not obvious.
(C-D) Can combine similar panels.
Scale bars: X μm. Error bars: mean ± SEM. *P < 0.05, **P < 0.01, ***P < 0.001.
n = X biological replicates from Y independent experiments.
```

## Reference Formatting

### Blood Journal (Vancouver)
```
1. Smith JA, Jones BC. Title of article. Blood. 2024;143(5):567-578.
```

### Nature (Author-Year)
```
Smith, J.A. & Jones, B.C. Title of article. Nature 620, 567–578 (2024).
```

## Journal-Specific Requirements

### Blood (ASH)
- Word limit: 4000 (full article)
- Figures: 7 max
- References: 60 max
- Structured abstract: 250 words

### Nature
- Word limit: ~3000 (Article)
- Main text figures: 6-8
- Methods: no limit, separate section
- Extended Data for supplementary figures

### Cell
- Word limit: 7000 (Article)
- STAR Methods format
- Graphical abstract required

## HIPAA Compliance Reminders

- No patient identifiers in any form
- Use Specimen IDs, not patient names/MRNs
- Aggregate data for small groups (n < 5)
- IRB approval statement required
- Data availability statement (GEO accession for sequencing)

## Writing Style

- Active voice preferred
- Past tense for results ("We found...")
- Present tense for established facts
- Avoid "interesting," "significant" (unless statistical)
- Be specific: "83.9-fold increase" not "marked increase"

See `references/journal_templates.md` for specific formats.
See `references/statistical_tests.md` for test selection guide.
