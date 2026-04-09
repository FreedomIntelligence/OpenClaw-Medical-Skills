# gene-panel-design-agent

> AI-powered design of targeted gene panels for clinical and research applications including cancer diagnostics, pharmacogenomics, and rare disease testing.

**Available tools:** Read, Bash

# Gene Panel Design Agent

The **Gene Panel Design Agent** provides AI-driven design of targeted sequencing panels for clinical diagnostics, cancer profiling, pharmacogenomics, and research applications.

## When to Use This Skill

* When designing custom gene panels for clinical or research use.
* To optimize panel content for specific disease areas.
* For balancing panel size with diagnostic yield.
* When designing probes for hybrid capture or amplicon approaches.
* To validate panel performance computationally.

## Core Capabilities

1. **Gene Selection**: Evidence-based gene prioritization for disease areas.

2. **Target Region Definition**: Specify exons, introns, UTRs, promoters to include.

3. **Probe Design**: In silico probe/primer design for capture or amplicon.

4. **Coverage Prediction**: Estimate uniformity and dropout risk.

5. **Validation Planning**: Design positive controls and performance metrics.

6. **Cost Optimization**: Balance panel size with clinical utility.

## Workflow

1. **Input**: Disease focus, required genes, platform choice, size constraints.

2. **Gene Prioritization**: Rank genes by clinical evidence level.

3. **Region Definition**: Define target coordinates.

4. **Probe Design**: Generate capture probes or primers.

5. **Coverage Simulation**: Predict sequencing performance.

6. **Optimization**: Iterate design for uniformity.

7. **Output**: Panel BED file, probe sequences, validation plan.

## Example Usage

**User**: "Design a comprehensive solid tumor panel covering actionable mutations and resistance markers."

**Agent Action**:
```bash
python3 Skills/Genomics/Gene_Panel_Design_Agent/panel_designer.py \
    --disease solid_tumor \
    --gene_sources nccn,civic,oncokb \
    --platform hybcap \
    --target_size 1.5mb \
    --include_fusions true \
    --include_cnv_backbone true \
    --output panel_design/
```

## Panel Design Considerations

| Factor | Impact | Optimization |
|--------|--------|--------------|
| Panel size | Cost, depth | Prioritize high-evidence genes |
| GC content | Coverage uniformity | Probe design, blockers |
| Repeat regions | Mapping challenges | Avoid or boost coverage |
| Homologous regions | Misalignment | Unique design, blockers |
| Structural variants | Detection | Intronic coverage, breakpoints |
| CNV detection | Require backbone | Tiled probes across genome |

## Gene Prioritization Sources

| Source | Content | Evidence Level |
|--------|---------|----------------|
| OncoKB | Actionable alterations | FDA/guideline levels |
| CIViC | Clinical variants | Community-curated |
| ClinVar | Pathogenic variants | Classification criteria |
| NCCN | Guideline genes | Clinical practice |
| COSMIC | Cancer genes | Census tier 1/2 |

## Panel Types

**Comprehensive Cancer Panel** (300-700 genes):
- All known cancer drivers
- Actionable mutations
- Resistance markers
- MSI/TMB estimation

**Focused Tumor Panel** (50-100 genes):
- Most actionable genes
- Cost-effective
- Higher depth possible

**Pharmacogenomics Panel**:
- CPIC/DPWG genes
- CYP450, HLA, transporters
- Star allele compatible design

**Rare Disease Panel**:
- Disease-specific genes
- Deep intronic variants
- CNV detection

## AI/ML Components

**Gene Ranking**:
- Literature mining for evidence
- Mutation frequency weighting
- Actionability scoring

**Probe Optimization**:
- GC content balancing
- Tm normalization
- Off-target minimization

**Coverage Prediction**:
- ML models from historical data
- GC-coverage relationships
- Dropout prediction

## Validation Planning

**Performance Metrics**:
- Coverage uniformity (CV)
- On-target rate
- Sensitivity by variant type
- Reproducibility

**Reference Materials**:
- Horizon Discovery cell lines
- SeraCare controls
- Well-characterized samples
- In silico spike-ins

## Technical Specifications

| Platform | Typical Size | Depth | CNV Capable |
|----------|--------------|-------|-------------|
| Hybrid capture | 1-3 Mb | 500-1000x | Yes (with backbone) |
| Amplicon | 10-500 kb | 1000-5000x | Limited |
| Anchored multiplex | Variable | Variable | Fusions |

## Prerequisites

* Python 3.10+
* BEDTools for coordinate manipulation
* Probe design algorithms
* Reference genome and annotations

## Related Skills

* CRISPR_Design_Agent - For guide design
* Variant_Interpretation - For variant selection
* Tumor_Mutational_Burden_Agent - For TMB panel requirements

## Output Files

| File | Content | Purpose |
|------|---------|---------|
| panel.bed | Target coordinates | Sequencing design |
| probes.fa | Probe sequences | Manufacturing |
| genes.csv | Gene list with rationale | Documentation |
| validation.pdf | QC plan | Laboratory setup |

## Author

AI Group - Biomedical AI Platform
