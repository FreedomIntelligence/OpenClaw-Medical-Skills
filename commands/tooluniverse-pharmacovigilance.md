# tooluniverse-pharmacovigilance

> Analyze drug safety signals from FDA adverse event reports, label warnings, and pharmacogenomic data. Calculates disproportionality measures (PRR, ROR), identifies serious adverse events, assesses pharmacogenomic risk variants. Use when asked about drug safety, adverse events, post-market surveillance, or risk-benefit assessment.

# Pharmacovigilance Safety Analyzer

Systematic drug safety analysis using FAERS adverse event data, FDA labeling, PharmGKB pharmacogenomics, and clinical trial safety signals.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, update progressively
2. **Signal quantification** - Use disproportionality measures (PRR, ROR)
3. **Severity stratification** - Prioritize serious/fatal events
4. **Multi-source triangulation** - FAERS, labels, trials, literature
5. **Pharmacogenomic context** - Include genetic risk factors
6. **Actionable output** - Risk-benefit summary with recommendations
7. **English-first queries** - Always use English drug names and search terms in tool calls, even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## When to Use

Apply when user asks:
- "What are the safety concerns for [drug]?"
- "What adverse events are associated with [drug]?"
- "Is [drug] safe? What are the risks?"
- "Should I be concerned about [specific adverse event] with [drug]?"
- "Compare safety profiles of [drug A] vs [drug B]"
- "Pharmacovigilance analysis for [drug]"

---

## Critical Workflow Requirements

### 1. Report-First Approach (MANDATORY)

1. **Create the report file FIRST**:
   - File name: `[DRUG]_safety_report.md`
   - Initialize with all section headers
   - Add placeholder text: `[Researching...]`

2. **Progressively update** as you gather data

3. **Output separate data files**:
   - `[DRUG]_adverse_events.csv` - Ranked AEs with counts/signals
   - `[DRUG]_pharmacogenomics.csv` - PGx variants and recommendations

### 2. Citation Requirements (MANDATORY)

Every safety signal MUST include source:

```markdown
### Signal: Hepatotoxicity
- **PRR**: 3.2 (95% CI: 2.8-3.7)
- **Cases**: 1,247 reports
- **Serious**: 892 (71.5%)
- **Fatal**: 23

*Source: FAERS via `FAERS_count_reactions_by_drug_event` (Q1 2020 - Q4 2025)*
```

---

## Phase 0: Tool Verification

**CRITICAL**: Verify tool parameters before calling.

### Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `FAERS_count_reactions_by_drug_event` | `drug` | `drug_name` |
| `DailyMed_search_spls` | `name` | `drug_name` |
| `PharmGKB_search_drug` | `drug` | `query` |
| `OpenFDA_get_drug_events` | `drug_name` | `search` |

---

## Workflow Overview

```
Phase 1: Drug Disambiguation
├── Resolve drug name (brand → generic)
├── Get identifiers (RxCUI, ChEMBL, DrugBank)
└── Identify drug class and mechanism
    ↓
Phase 2: Adverse Event Profiling (FAERS)
├── Query FAERS for drug-event pairs
├── Calculate disproportionality (PRR, ROR)
├── Stratify by seriousness
└── OUTPUT: Ranked AE table
    ↓
Phase 3: Label Warning Extraction
├── DailyMed boxed warnings
├── Contraindications
├── Warnings and precautions
└── OUTPUT: Label safety summary
    ↓
Phase 4: Pharmacogenomic Risk
├── PharmGKB clinical annotations
├── High-risk genotypes
├── Dosing recommendations
└── OUTPUT: PGx risk table
    ↓
Phase 5: Clinical Trial Safety
├── ClinicalTrials.gov safety data
├── Phase 3/4 discontinuation rates
├── Serious AEs in trials
└── OUTPUT: Trial safety summary
    ↓
Phase 5.5: Pathway & Mechanism Context (NEW)
├── KEGG: Drug metabolism pathways
├── Reactome: Mechanism-linked pathways
├── Target pathway analysis
└── OUTPUT: Mechanistic safety context
    ↓
Phase 5.6: Literature Intelligence (ENHANCED)
├── PubMed: Published safety studies
├── BioRxiv/MedRxiv: Recent preprints
├── OpenAlex: Citation analysis
└── OUTPUT: Literature evidence
    ↓
Phase 6: Signal Prioritization
├── Rank by PRR × severity × frequency
├── Identify actionable signals
├── Risk-benefit assessment
└── OUTPUT: Prioritized signal list
    ↓
Phase 7: Report Synthesis
```

---

## Phase 1: Drug Disambiguation

### 1.1 Resolve Drug Identity

```python
def resolve_drug(tu, drug_query):
    """Resolve drug name to standardized identifiers."""
    identifiers = {}
    
    # DailyMed for NDC and SPL
    dailymed = tu.tools.DailyMed_search_spls(drug_name=drug_query)
    if dailymed:
        identifiers['ndc'] = dailymed[0].get('ndc')
        identifiers['setid'] = dailymed[0].get('setid')
        identifiers['generic_name'] = dailymed[0].get('generic_name')
    
    # ChEMBL for molecule data
    chembl = tu.tools.ChEMBL_search_drugs(query=drug_query)
    if chembl:
        identifiers['chembl_id'] = chembl[0].get('molecule_chembl_id')
        identifiers['max_phase'] = chembl[0].get('max_phase')
    
    return identifiers
```

### 1.2 Output for Report

```markdown
## 1. Drug Identification

| Property | Value |
|----------|-------|
| **Generic Name** | Metformin |
| **Brand Names** | Glucophage, Fortamet, Glumetza |
| **Drug Class** | Biguanide antidiabetic |
| **ChEMBL ID** | CHEMBL1431 |
| **Mechanism** | AMPK activator, hepatic gluconeogenesis inhibitor |
| **First Approved** | 1994 (US) |

*Source: DailyMed via `DailyMed_search_spls`, ChEMBL*
```

---

## Phase 2: Adverse Event Profiling

### 2.1 FAERS Query Strategy

```python
def get_faers_events(tu, drug_name, top_n=50):
    """Query FAERS for adverse events."""
    
    # Get event counts
    events = tu.tools.FAERS_count_reactions_by_drug_event(
        drug_name=drug_name,
        limit=top_n
    )
    
    # For each event, get detailed breakdown
    detailed_events = []
    for event in events:
        detail = tu.tools.FAERS_get_event_details(
            drug_name=drug_name,
            reaction=event['reaction']
        )
        detailed_events.append({
            'reaction': event['reaction'],
            'count': event['count'],
            'serious': detail.get('serious_count', 0),
            'fatal': detail.get('death_count', 0),
            'hospitalization': detail.get('hospitalization_count', 0)
        })
    
    return detailed_events
```

### 2.2 Disproportionality Analysis

**Proportional Reporting Ratio (PRR)**:
```
PRR = (A/B) / (C/D)

Where:
A = Reports of drug X with event Y
B = Reports of drug X with any event
C = Reports of event Y with any drug (excluding X)
D = Total reports (excluding drug X)
```

**Signal Thresholds**:
| Measure | Signal Threshold | Strong Signal |
|---------|------------------|---------------|
| PRR | >2.0 | >3.0 |
| Chi-squared | >4.0 | >10.0 |
| N (case count) | ≥3 | ≥10 |

### 2.3 Severity Classification

| Category | Definition | Priority |
|----------|------------|----------|
| **Fatal** | Death outcome | Highest |
| **Life-threatening** | Immediate death risk | Very High |
| **Hospitalization** | Required/prolonged hospitalization | High |
| **Disability** | Persistent impairment | High |
| **Congenital anomaly** | Birth defect | High |
| **Other serious** | Medical intervention required | Medium |
| **Non-serious** | No serious criteria | Low |

### 2.4 Output for Report

```markdown
## 2. Adverse Event Profile (FAERS)

**Data Period**: Q1 2020 - Q4 2025
**Total Reports for Drug**: 45,234

### 2.1 Top Adverse Events by Frequency

| Rank | Adverse Event | Reports | PRR | 95% CI | Serious (%) | Fatal |
|------|---------------|---------|-----|--------|-------------|-------|
| 1 | Diarrhea | 8,234 | 2.3 | 2.1-2.5 | 12% | 3 |
| 2 | Nausea | 6,892 | 1.8 | 1.6-2.0 | 8% | 0 |
| 3 | Lactic acidosis | 1,247 | 15.2 | 12.8-17.9 | 89% ⚠️ | 156 ⚠️ |
| 4 | Hypoglycemia | 2,341 | 2.1 | 1.9-2.4 | 34% | 8 |
| 5 | Vitamin B12 deficiency | 892 | 8.4 | 7.2-9.8 | 23% | 0 |

### 2.2 Serious Adverse Events Only

| Adverse Event | Serious Reports | Fatal | PRR | Signal |
|---------------|-----------------|-------|-----|--------|
| Lactic acidosis | 1,110 | 156 | 15.2 | **STRONG** ⚠️ |
| Acute kidney injury | 678 | 34 | 4.2 | Moderate |
| Hepatotoxicity | 234 | 12 | 3.1 | Moderate |

### 2.3 Signal Interpretation

**Strong Signal: Lactic Acidosis** ⚠️
- PRR of 15.2 indicates 15x higher reporting rate than expected
- 89% classified as serious
- 156 fatalities (12.5% case fatality)
- **Known class effect of biguanides**
- Risk factors: renal impairment, hypoxia, contrast agents

*Source: FAERS via `FAERS_count_reactions_by_drug_event`*
```

---

## Phase 3: Label Warning Extraction

### 3.1 DailyMed Query

```python
def extract_label_warnings(tu, setid):
    """Extract safety sections from FDA label."""
    
    label = tu.tools.DailyMed_get_spl_by_set_id(setid=setid)
    
    warnings = {
        'boxed_warning': label.get('boxed_warning'),
        'contraindications': label.get('contraindications'),
        'warnings_precautions': label.get('warnings_and_precautions'),
        'adverse_reactions': label.get('adverse_reactions'),
        'drug_interactions': label.get('drug_interactions')
    }
    
    return warnings
```

### 3.2 Warning Severity Categories

| Category | Symbol | Description |
|----------|--------|-------------|
| **Boxed Warning** | ⬛ | Most serious, life-threatening |
| **Contraindication** | 🔴 | Must not use |
| **Warning** | 🟠 | Significant risk |
| **Precaution** | 🟡 | Use caution |

### 3.3 Output for Report

```markdown
## 3. FDA Label Safety Information

### 3.1 Boxed Warning ⬛

**LACTIC ACIDOSIS**
> Metformin can cause lactic acidosis, a rare but serious complication. 
> Risk increases with renal impairment, sepsis, dehydration, excessive 
> alcohol intake, hepatic impairment, and acute heart failure.
> 
> **Contraindicated in patients with eGFR <30 mL/min/1.73m²**

### 3.2 Contraindications 🔴

| Contraindication | Rationale |
|------------------|-----------|
| eGFR <30 mL/min/1.73m² | Lactic acidosis risk |
| Acute/chronic metabolic acidosis | May worsen acidosis |
| Hypersensitivity to metformin | Allergic reaction |

### 3.3 Warnings and Precautions 🟠

| Warning | Clinical Action |
|---------|-----------------|
| Vitamin B12 deficiency | Monitor B12 levels annually |
| Hypoglycemia with insulin | Reduce insulin dose |
| Radiologic contrast | Hold 48h around procedure |
| Surgical procedures | Hold day of surgery |

*Source: DailyMed via `DailyMed_get_spl_by_set_id`*
```

---

## Phase 4: Pharmacogenomic Risk

### 4.1 PharmGKB Query

```python
def get_pharmacogenomics(tu, drug_name):
    """Get pharmacogenomic annotations."""
    
    # Search PharmGKB
    pgx = tu.tools.PharmGKB_search_drug(query=drug_name)
    
    annotations = []
    for result in pgx:
        if result.get('clinical_annotation'):
            annotations.append({
                'gene': result['gene'],
                'variant': result['variant'],
                'phenotype': result['phenotype'],
                'recommendation': result['recommendation'],
                'level': result['level_of_evidence']
            })
    
    return annotations
```

### 4.2 PGx Evidence Levels

| Level | Description | Clinical Action |
|-------|-------------|-----------------|
| **1A** | CPIC/DPWG guideline, implementable | Follow guideline |
| **1B** | CPIC/DPWG guideline, annotation | Consider testing |
| **2A** | VIP annotation, moderate evidence | May inform |
| **2B** | VIP annotation, weaker evidence | Research |
| **3** | Low-level annotation | Not actionable |

### 4.3 Output for Report

```markdown
## 4. Pharmacogenomic Risk Factors

### 4.1 Clinically Actionable Variants

| Gene | Variant | Phenotype | Recommendation | Level |
|------|---------|-----------|----------------|-------|
| SLC22A1 | rs628031 | Reduced OCT1 | Reduced metformin response | 2A |
| SLC22A1 | rs36056065 | Loss of function | Consider alternative | 2A |
| ATM | rs11212617 | Increased response | Standard dosing | 3 |

### 4.2 Clinical Implications

**OCT1 (SLC22A1) Poor Metabolizers**:
- ~9% of Caucasians carry two loss-of-function alleles
- Reduced hepatic uptake of metformin
- May have decreased efficacy
- Consider higher doses or alternative agent

**No CPIC/DPWG guidelines currently exist for metformin**

*Source: PharmGKB via `PharmGKB_search_drug`*
```

---

## Phase 5: Clinical Trial Safety

### 5.1 ClinicalTrials.gov Query

```python
def get_trial_safety(tu, drug_name):
    """Get safety data from clinical trials."""
    
    # Search completed phase 3/4 trials
    trials = tu.tools.search_clinical_trials(
        intervention=drug_name,
        phase="Phase 3",
        status="Completed",
        pageSize=20
    )
    
    safety_data = []
    for trial in trials:
        if trial.get('results_posted'):
            results = tu.tools.get_clinical_trial_results(
                nct_id=trial['nct_id']
            )
            safety_data.append(results.get('adverse_events'))
    
    return safety_data
```

### 5.2 Output for Report

```markdown
## 5. Clinical Trial Safety Data

### 5.1 Phase 3 Trial Summary

| Trial | N | Duration | Serious AEs (Drug) | Serious AEs (Placebo) | Deaths |
|-------|---|----------|-------------------|----------------------|--------|
| UKPDS | 1,704 | 10 yr | 12.3% | 14.1% | 8.2% vs 9.1% |
| DPP | 1,073 | 3 yr | 4.2% | 3.8% | 0.1% |
| SPREAD | 884 | 2 yr | 5.1% | 4.9% | 0.2% |

### 5.2 Common Adverse Events in Trials

| Adverse Event | Drug (%) | Placebo (%) | Difference |
|---------------|----------|-------------|------------|
| Diarrhea | 53% | 12% | +41% ⚠️ |
| Nausea | 26% | 8% | +18% |
| Flatulence | 12% | 6% | +6% |
| Asthenia | 9% | 6% | +3% |

*Source: ClinicalTrials.gov via `search_clinical_trials`*
```

---

## Phase 5.5: Pathway & Mechanism Context (NEW)

### 5.5.1 Drug Metabolism Pathways (KEGG)

```python
def get_drug_pathway_context(tu, drug_name, drug_targets):
    """Get pathway context for mechanistic safety understanding."""
    
    # KEGG drug metabolism
    metabolism = tu.tools.kegg_search_pathway(
        query=f"{drug_name} metabolism"
    )
    
    # Target pathways
    target_pathways = {}
    for target in drug_targets:
        pathways = tu.tools.kegg_get_gene_info(gene_id=f"hsa:{target}")
        target_pathways[target] = pathways.get('pathways', [])
    
    return {
        'metabolism_pathways': metabolism,
        'target_pathways': target_pathways
    }
```

### 5.5.2 Output for Report

```markdown
## 5.5 Pathway & Mechanism Context

### Drug Metabolism Pathways (KEGG)

| Pathway | Relevance | Safety Implication |
|---------|-----------|-------------------|
| Drug metabolism - cytochrome P450 | Primary metabolism | CYP2C9 interactions |
| Gluconeogenesis inhibition | MOA | Lactic acidosis mechanism |
| Mitochondrial complex I | Off-target | Lactic acid accumulation |

### Target Pathway Analysis

**Primary Target: AMPK**
- Pathway: AMPK signaling (hsa04152)
- Downstream: mTOR inhibition, autophagy
- Safety relevance: Explains metabolic effects

**Mechanistic Basis for Key AEs**:
| Adverse Event | Pathway Mechanism |
|---------------|-------------------|
| Lactic acidosis | Mitochondrial complex I inhibition |
| GI intolerance | Serotonin release in gut |
| B12 deficiency | Intrinsic factor interference |

*Source: KEGG, Reactome*
```

---

## Phase 5.6: Literature Intelligence (ENHANCED)

### 5.6.1 Published Safety Studies

```python
def comprehensive_safety_literature(tu, drug_name, key_aes):
    """Search all literature sources for safety evidence."""
    
    # PubMed: Peer-reviewed
    pubmed = tu.tools.PubMed_search_articles(
        query=f'"{drug_name}" AND (safety OR adverse OR toxicity)',
        limit=30
    )
    
    # BioRxiv: Preprints
    biorxiv = tu.tools.BioRxiv_search_preprints(
        query=f"{drug_name} mechanism toxicity",
        limit=10
    )
    
    # MedRxiv: Clinical preprints
    medrxiv = tu.tools.MedRxiv_search_preprints(
        query=f"{drug_name} safety",
        limit=10
    )
    
    # Citation analysis for key papers
    key_papers = pubmed[:10]
    for paper in key_papers:
        citation = tu.tools.openalex_search_works(
            query=paper['title'],
            limit=1
        )
        paper['citations'] = citation[0].get('cited_by_count', 0) if citation else 0
    
    return {
        'pubmed': pubmed,
        'preprints': biorxiv + medrxiv,
        'key_papers': key_papers
    }
```

### 5.6.2 Output for Report

```markdown
## 5.6 Literature Evidence

### Key Safety Studies

| PMID | Title | Year | Citations | Finding |
|------|-------|------|-----------|---------|
| 29234567 | Metformin and lactic acidosis: meta-analysis | 2020 | 245 | Risk 4.3/100,000 |
| 28765432 | Long-term cardiovascular outcomes... | 2019 | 567 | CV benefit confirmed |
| 30123456 | B12 deficiency prevalence study | 2021 | 123 | 30% after 4 years |

### Recent Preprints (Not Peer-Reviewed)

| Source | Title | Posted | Relevance |
|--------|-------|--------|-----------|
| MedRxiv | Novel metformin safety signal in elderly | 2024-01 | Age-related risk |
| BioRxiv | Gut microbiome and metformin GI effects | 2024-02 | Mechanistic |

**⚠️ Note**: Preprints have NOT undergone peer review.

### Evidence Summary

| Evidence Type | Count | High-Impact |
|---------------|-------|-------------|
| Systematic reviews | 12 | 5 |
| RCTs with safety data | 28 | 8 |
| Mechanistic studies | 15 | 3 |
| Case reports | 45 | - |

*Source: PubMed, BioRxiv, MedRxiv, OpenAlex*
```

---

## Phase 6: Signal Prioritization

### 6.1 Signal Scoring Formula

```
Signal Score = PRR × Severity_Weight × log10(Case_Count + 1)

Severity Weights:
- Fatal: 10
- Life-threatening: 8
- Hospitalization: 5
- Disability: 5
- Other serious: 3
- Non-serious: 1
```

### 6.2 Output for Report

```markdown
## 6. Prioritized Safety Signals

### 6.1 Critical Signals (Immediate Attention)

| Signal | PRR | Fatal | Score | Action |
|--------|-----|-------|-------|--------|
| Lactic acidosis | 15.2 | 156 | 482 | Boxed warning exists |
| Acute kidney injury | 4.2 | 34 | 89 | Monitor renal function |

### 6.2 Moderate Signals (Monitor)

| Signal | PRR | Serious | Score | Action |
|--------|-----|---------|-------|--------|
| Hepatotoxicity | 3.1 | 234 | 52 | Check LFTs if symptoms |
| Pancreatitis | 2.8 | 178 | 41 | Monitor lipase |

### 6.3 Known/Expected (Manage Clinically)

| Signal | PRR | Frequency | Management |
|--------|-----|-----------|------------|
| Diarrhea | 2.3 | 18% | Start low, titrate slow |
| Nausea | 1.8 | 12% | Take with food |
| B12 deficiency | 8.4 | 2% | Annual monitoring |
```

---

## Report Template

**File**: `[DRUG]_safety_report.md`

```markdown
# Pharmacovigilance Safety Report: [DRUG]

**Generated**: [Date] | **Query**: [Original query] | **Status**: In Progress

---

## Executive Summary
[Researching...]

---

## 1. Drug Identification
### 1.1 Drug Information
[Researching...]

---

## 2. Adverse Event Profile (FAERS)
### 2.1 Top Adverse Events
[Researching...]
### 2.2 Serious Adverse Events
[Researching...]
### 2.3 Signal Analysis
[Researching...]

---

## 3. FDA Label Safety Information
### 3.1 Boxed Warnings
[Researching...]
### 3.2 Contraindications
[Researching...]
### 3.3 Warnings and Precautions
[Researching...]

---

## 4. Pharmacogenomic Risk Factors
### 4.1 Actionable Variants
[Researching...]
### 4.2 Testing Recommendations
[Researching...]

---

## 5. Clinical Trial Safety
### 5.1 Trial Summary
[Researching...]
### 5.2 Adverse Events in Trials
[Researching...]

---

## 6. Prioritized Safety Signals
### 6.1 Critical Signals
[Researching...]
### 6.2 Moderate Signals
[Researching...]

---

## 7. Risk-Benefit Assessment
[Researching...]

---

## 8. Clinical Recommendations
### 8.1 Monitoring Recommendations
[Researching...]
### 8.2 Patient Counseling Points
[Researching...]
### 8.3 Contraindication Checklist
[Researching...]

---

## 9. Data Gaps & Limitations
[Researching...]

---

## 10. Data Sources
[Will be populated as research progresses...]
```

---

## Evidence Grading

| Tier | Symbol | Criteria | Example |
|------|--------|----------|---------|
| **T1** | ⚠️⚠️⚠️ | PRR >10, fatal outcomes, boxed warning | Lactic acidosis |
| **T2** | ⚠️⚠️ | PRR 3-10, serious outcomes | Hepatotoxicity |
| **T3** | ⚠️ | PRR 2-3, moderate concern | Hypoglycemia |
| **T4** | ℹ️ | PRR <2, known/expected | GI side effects |

---

## Completeness Checklist

### Phase 1: Drug Identification
- [ ] Generic name resolved
- [ ] Brand names listed
- [ ] Drug class identified
- [ ] ChEMBL/DrugBank ID obtained
- [ ] Mechanism of action stated

### Phase 2: FAERS Analysis
- [ ] ≥20 adverse events queried
- [ ] PRR calculated for top events
- [ ] Serious/fatal counts included
- [ ] Signal thresholds applied
- [ ] Time period stated

### Phase 3: Label Warnings
- [ ] Boxed warnings extracted (or "None")
- [ ] Contraindications listed
- [ ] Key warnings summarized
- [ ] Drug interactions noted

### Phase 4: Pharmacogenomics
- [ ] PharmGKB queried
- [ ] Actionable variants listed (or "None")
- [ ] Evidence levels provided
- [ ] Testing recommendations stated

### Phase 5: Clinical Trials
- [ ] Phase 3/4 trials searched
- [ ] Serious AE rates compared
- [ ] Discontinuation rates noted

### Phase 6: Signal Prioritization
- [ ] Signals ranked by score
- [ ] Critical signals flagged
- [ ] Actions recommended

### Phase 7-8: Synthesis
- [ ] Risk-benefit assessment provided
- [ ] Monitoring recommendations listed
- [ ] Patient counseling points included

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `FAERS_count_reactions_by_drug_event` | `OpenFDA_get_drug_events` | Literature search |
| `DailyMed_get_spl_by_set_id` | `FDA_drug_label_search` | DailyMed website |
| `PharmGKB_search_drug` | `CPIC_get_guidelines` | Literature search |
| `search_clinical_trials` | `ClinicalTrials.gov` API | PubMed for trial results |

---

## Tool Reference

See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) for complete tool documentation.
