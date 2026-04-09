# microbiome-cancer-agent

> AI-powered analysis of microbiome-cancer interactions including tumor microbiome profiling, immunotherapy response prediction, and microbiome-targeted therapeutic opportunities.

**Available tools:** Read, Bash

# Microbiome-Cancer Interaction Agent

The **Microbiome-Cancer Interaction Agent** analyzes relationships between the microbiome and cancer, including tumor-associated bacteria, gut microbiome effects on immunotherapy, and microbiome-targeted therapeutic strategies.

## When to Use This Skill

* When analyzing tumor microbiome composition from sequencing data.
* To predict immunotherapy response based on gut microbiome profiles.
* For identifying microbiome-based biomarkers in cancer.
* When assessing antibiotic impact on cancer treatment efficacy.
* To design microbiome-modulating therapeutic interventions.

## Core Capabilities

1. **Tumor Microbiome Analysis**: Profile intratumoral bacteria from tumor sequencing data.

2. **Gut-Cancer Axis**: Analyze fecal microbiome associations with cancer outcomes.

3. **ICI Response Prediction**: Predict checkpoint inhibitor response from microbiome.

4. **Metabolite Profiling**: Link microbial metabolites to cancer phenotypes.

5. **Antibiotic Impact**: Model antibiotic effects on treatment efficacy.

6. **FMT/Probiotic Design**: Support microbiome-modulating interventions.

## Microbiome-Cancer Associations

| Cancer Type | Key Bacteria | Association |
|-------------|--------------|-------------|
| Colorectal | Fusobacterium nucleatum | Promotion, poor prognosis |
| Colorectal | Bacteroides fragilis (ETBF) | Carcinogenesis |
| Gastric | Helicobacter pylori | Established carcinogen |
| Pancreatic | Gammaproteobacteria | Drug metabolism |
| Breast | Fusobacterium | Metastasis |
| Oral | Porphyromonas gingivalis | Oral SCC |

## Workflow

1. **Input**: 16S/shotgun metagenomics, tumor sequencing, clinical data.

2. **Taxonomy Profiling**: Identify bacterial composition at genus/species level.

3. **Diversity Analysis**: Calculate alpha and beta diversity metrics.

4. **Association Testing**: Correlate microbiome with outcomes.

5. **Functional Prediction**: Infer metabolic potential (PICRUSt2, HUMAnN).

6. **Prediction Modeling**: Build response prediction models.

7. **Output**: Microbiome profile, associations, predictions, interventions.

## Example Usage

**User**: "Analyze gut microbiome from melanoma patients and predict anti-PD-1 response."

**Agent Action**:
```bash
python3 Skills/Microbiome/Microbiome_Cancer_Agent/microbiome_cancer.py \
    --metagenomics fecal_shotgun.fastq.gz \
    --tumor_data melanoma_rnaseq.tsv \
    --clinical treatment_outcomes.csv \
    --analysis ici_response \
    --reference metaphlan_db \
    --output microbiome_report/
```

## ICI Response and Microbiome

**Favorable Microbiome**:
- Akkermansia muciniphila
- Faecalibacterium prausnitzii
- Bifidobacterium spp.
- Ruminococcaceae family
- High diversity

**Unfavorable Microbiome**:
- Bacteroidales (in some studies)
- Low diversity
- Post-antibiotic dysbiosis

## Microbial Metabolites in Cancer

| Metabolite | Source | Effect |
|------------|--------|--------|
| Butyrate | Clostridia | Anti-inflammatory, anti-tumor |
| Inosine | Akkermansia | Enhanced ICI response |
| TMAO | Various | Pro-tumorigenic |
| Secondary bile acids | Various | Variable, context-dependent |
| LPS | Gram-negative | Inflammation, mixed effects |

## AI/ML Components

**Response Prediction**:
- Random forest on microbiome features
- Neural networks for metagenomic profiles
- Integration with host factors

**Microbiome-Metabolite Linking**:
- Genome-scale metabolic models
- Correlation networks
- Causal inference methods

**Intervention Design**:
- FMT donor selection
- Probiotic consortium optimization
- Antibiotic avoidance recommendations

## Tumor Microbiome Analysis

**Challenges**:
- Low bacterial biomass in tumors
- Contamination from reagents/environment
- Batch effects
- Need for stringent controls

**Best Practices**:
- Negative controls (extraction, PCR)
- Decontamination algorithms (decontam, SCRuB)
- Multiple validation methods
- Orthogonal confirmation (FISH, culture)

## Clinical Implications

1. **Biomarker Development**: Microbiome-based response prediction
2. **Intervention Timing**: Avoid antibiotics pre-ICI
3. **FMT Trials**: Responder microbiome transfer
4. **Probiotics**: Rationally designed consortia
5. **Prebiotics**: Fiber to support beneficial bacteria

## Prerequisites

* Python 3.10+
* QIIME2, Metaphlan, HUMAnN
* R (phyloseq, vegan)
* ML frameworks

## Related Skills

* Metagenomics - For general microbiome analysis
* Immune_Checkpoint_Combination_Agent - For ICI optimization
* Metabolomics - For metabolite analysis

## Research Frontiers

1. **Intratumoral bacteria**: Direct tumor effects
2. **Phage therapy**: Targeting pathobionts
3. **Engineered probiotics**: Drug-producing bacteria
4. **Diet interventions**: Modulating microbiome for therapy

## Author

AI Group - Biomedical AI Platform
