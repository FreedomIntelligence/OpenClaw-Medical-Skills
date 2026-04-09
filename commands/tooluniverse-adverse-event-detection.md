# tooluniverse-adverse-event-detection

> Detect and analyze adverse drug event signals using FDA FAERS data, drug labels, disproportionality analysis (PRR, ROR, IC), and biomedical evidence. Generates quantitative safety signal scores (0-100) with evidence grading. Use for post-market surveillance, pharmacovigilance, drug safety assessment, adverse event investigation, and regulatory decision support.

# Adverse Drug Event Signal Detection & Analysis

Automated pipeline for detecting, quantifying, and contextualizing adverse drug event signals using FAERS disproportionality analysis, FDA label mining, mechanism-based prediction, and literature evidence. Produces a quantitative Safety Signal Score (0-100) for regulatory and clinical decision-making.

**KEY PRINCIPLES**:
1. **Signal quantification first** - Every adverse event must have PRR/ROR/IC with confidence intervals
2. **Serious events priority** - Deaths, hospitalizations, life-threatening events always analyzed first
3. **Multi-source triangulation** - FAERS + FDA labels + OpenTargets + DrugBank + literature
4. **Context-aware assessment** - Distinguish drug-specific vs class-wide vs confounding signals
5. **Report-first approach** - Create report file FIRST, update progressively
6. **Evidence grading mandatory** - T1 (regulatory/boxed warning) through T4 (computational)
7. **English-first queries** - Always use English drug names in tool calls, respond in user's language

---

## When to Use

Apply when user asks:
- "What are the safety signals for [drug]?"
- "Detect adverse events for [drug]"
- "Is [drug] associated with [adverse event]?"
- "What are the FAERS signals for [drug]?"
- "Compare safety of [drug A] vs [drug B] for [adverse event]"
- "What are the serious adverse events for [drug]?"
- "Are there emerging safety signals for [drug]?"
- "Post-market surveillance report for [drug]"
- "Pharmacovigilance signal detection for [drug]"
- "What is the disproportionality analysis for [drug] and [event]?"

**Differentiation from tooluniverse-pharmacovigilance**: This skill focuses specifically on **signal detection and quantification** using disproportionality analysis (PRR, ROR, IC) with statistical rigor, produces a quantitative **Safety Signal Score (0-100)**, and performs **comparative safety analysis** across drug classes. The pharmacovigilance skill provides broader safety profiling without the same depth of signal detection metrics.

---

## Workflow Overview

```
Phase 0: Input Parsing & Drug Disambiguation
  Parse drug name, resolve to ChEMBL ID, DrugBank ID
  Identify drug class, mechanism, and approved indications
    |
Phase 1: FAERS Adverse Event Profiling
  Top adverse events by frequency
  Seriousness and outcome distributions
  Demographics (age, sex, country)
    |
Phase 2: Disproportionality Analysis (Signal Detection)
  Calculate PRR, ROR, IC with 95% CI for each AE
  Apply signal detection criteria
  Classify signal strength (Strong/Moderate/Weak/None)
    |
Phase 3: FDA Label Safety Information
  Boxed warnings, contraindications
  Warnings and precautions, adverse reactions
  Drug interactions, special populations
    |
Phase 4: Mechanism-Based Adverse Event Context
  Target-based AE prediction (OpenTargets safety)
  Off-target effects, ADMET predictions
  Drug class effects comparison
    |
Phase 5: Comparative Safety Analysis
  Compare to drugs in same class
  Identify unique vs class-wide signals
  Head-to-head disproportionality comparison
    |
Phase 6: Drug-Drug Interactions & Risk Factors
  Known DDIs causing AEs
  Pharmacogenomic risk factors (PharmGKB)
  FDA PGx biomarkers
    |
Phase 7: Literature Evidence
  PubMed safety studies, case reports
  OpenAlex citation analysis
  Preprint emerging signals (EuropePMC)
    |
Phase 8: Risk Assessment & Safety Signal Score
  Calculate Safety Signal Score (0-100)
  Evidence grading (T1-T4) for each signal
  Clinical significance assessment
    |
Phase 9: Report Synthesis & Recommendations
  Monitoring recommendations
  Risk mitigation strategies
  Completeness checklist
```

---

## Phase 0: Input Parsing & Drug Disambiguation

### 0.1 Resolve Drug Identity

```python
# Step 1: Get ChEMBL ID from drug name
chembl_result = tu.tools.OpenTargets_get_drug_chembId_by_generic_name(drugName="atorvastatin")
# Response: {data: {search: {hits: [{id: "CHEMBL1487", name: "ATORVASTATIN", description: "..."}]}}}
chembl_id = chembl_result['data']['search']['hits'][0]['id']  # "CHEMBL1487"

# Step 2: Get drug mechanism of action
moa = tu.tools.OpenTargets_get_drug_mechanisms_of_action_by_chemblId(chemblId=chembl_id)
# Response: {data: {drug: {mechanismsOfAction: {rows: [{mechanismOfAction: "HMG-CoA reductase inhibitor", actionType: "INHIBITOR", targetName: "...", targets: [{id: "ENSG00000113161", approvedSymbol: "HMGCR"}]}]}}}}

# Step 3: Get blackbox warning status
blackbox = tu.tools.OpenTargets_get_drug_blackbox_status_by_chembl_ID(chemblId=chembl_id)
# Response: {data: {drug: {name: "ATORVASTATIN", hasBeenWithdrawn: false, blackBoxWarning: false}}}

# Step 4: Get DrugBank info (safety, toxicity)
drugbank = tu.tools.drugbank_get_safety_by_drug_name_or_drugbank_id(
    query="atorvastatin", case_sensitive=False, exact_match=False, limit=3
)
# Response: {results: [{drug_name: "Atorvastatin", drugbank_id: "DB01076", toxicity: "...", food_interactions: "..."}]}

# Step 5: Get DrugBank targets
targets = tu.tools.drugbank_get_targets_by_drug_name_or_drugbank_id(
    query="atorvastatin", case_sensitive=False, exact_match=False, limit=3
)
# Response: {results: [{drug_name: "...", targets: [{name: "HMG-CoA reductase", ...}]}]}

# Step 6: Get approved indications
indications = tu.tools.OpenTargets_get_drug_indications_by_chemblId(chemblId=chembl_id)
# Response: {data: {drug: {indications: {rows: [{disease: {name: "hypercholesterolemia"}, maxPhaseForIndication: 4}]}}}}
```

### 0.2 Output for Report

```markdown
## 1. Drug Identification

| Property | Value |
|----------|-------|
| **Generic Name** | Atorvastatin |
| **ChEMBL ID** | CHEMBL1487 |
| **DrugBank ID** | DB01076 |
| **Drug Class** | HMG-CoA reductase inhibitor (Statin) |
| **Mechanism** | HMG-CoA reductase inhibitor (target: HMGCR) |
| **Primary Target** | HMGCR (ENSG00000113161) |
| **Black Box Warning** | No |
| **Withdrawn** | No |

*Source: OpenTargets, DrugBank*
```

---

## Phase 1: FAERS Adverse Event Profiling

### 1.1 Query FAERS for Adverse Events

```python
# Get top adverse event reactions (returns list of {term, count})
reactions = tu.tools.FAERS_count_reactions_by_drug_event(medicinalproduct="ATORVASTATIN")
# Response: [{term: "FATIGUE", count: 19171}, {term: "DIARRHOEA", count: 17127}, ...]

# Get seriousness classification
seriousness = tu.tools.FAERS_count_seriousness_by_drug_event(medicinalproduct="ATORVASTATIN")
# Response: [{term: "Serious", count: 242757}, {term: "Non-serious", count: 83504}]

# Get outcome distribution
outcomes = tu.tools.FAERS_count_outcomes_by_drug_event(medicinalproduct="ATORVASTATIN")
# Response: [{term: "Unknown", count: 162310}, {term: "Fatal", count: 22128}, ...]

# Get age distribution
age_dist = tu.tools.FAERS_count_patient_age_distribution(medicinalproduct="ATORVASTATIN")
# Response: [{term: "Elderly", count: 38510}, {term: "Adult", count: 24302}, ...]

# Get death-related events
deaths = tu.tools.FAERS_count_death_related_by_drug(medicinalproduct="ATORVASTATIN")
# Response: [{term: "alive", count: 113157}, {term: "death", count: 26909}]

# Get reporter country distribution
countries = tu.tools.FAERS_count_reportercountry_by_drug_event(medicinalproduct="ATORVASTATIN")
# Response: [{term: "US", count: 170963}, {term: "GB", count: 40079}, ...]
```

### 1.2 Get Serious Events Breakdown

```python
# Filter serious events - all types
serious_all = tu.tools.FAERS_filter_serious_events(
    operation="filter_serious_events",
    drug_name="ATORVASTATIN",
    seriousness_type="all"
)
# Response: {status: "success", drug_name: "ATORVASTATIN", seriousness_type: "all",
#   total_serious_events: N, top_serious_reactions: [{reaction: "...", count: N}, ...]}

# Death-related serious events
serious_death = tu.tools.FAERS_filter_serious_events(
    operation="filter_serious_events",
    drug_name="ATORVASTATIN",
    seriousness_type="death"
)
# Response: {status: "success", total_serious_events: 18720,
#   top_serious_reactions: [{reaction: "DEATH", count: 7541}, {reaction: "MYOCARDIAL INFARCTION", count: 1286}, ...]}

# Hospitalization-related
serious_hosp = tu.tools.FAERS_filter_serious_events(
    operation="filter_serious_events",
    drug_name="ATORVASTATIN",
    seriousness_type="hospitalization"
)

# Life-threatening
serious_lt = tu.tools.FAERS_filter_serious_events(
    operation="filter_serious_events",
    drug_name="ATORVASTATIN",
    seriousness_type="life_threatening"
)
```

### 1.3 MedDRA Hierarchy Rollup

```python
# Get MedDRA preferred term rollup (top 50)
meddra = tu.tools.FAERS_rollup_meddra_hierarchy(
    operation="rollup_meddra_hierarchy",
    drug_name="ATORVASTATIN"
)
# Response: {status: "success", drug_name: "ATORVASTATIN",
#   meddra_hierarchy: {PT_level: [{preferred_term: "FATIGUE", count: 13957}, ...]}}
```

### 1.4 Output for Report

```markdown
## 2. FAERS Adverse Event Profile

### 2.1 Overview
- **Total reports**: 326,261 (Serious: 242,757 | Non-serious: 83,504)
- **Fatal outcomes**: 22,128
- **Primary reporter countries**: US (170,963), GB (40,079), CA (16,492)

### 2.2 Top 10 Adverse Events by Frequency

| Rank | Adverse Event | Reports | % of Total |
|------|---------------|---------|------------|
| 1 | Fatigue | 19,171 | 5.9% |
| 2 | Diarrhoea | 17,127 | 5.2% |
| 3 | Dyspnoea | 15,992 | 4.9% |
| ... | ... | ... | ... |

### 2.3 Outcome Distribution

| Outcome | Count | Percentage |
|---------|-------|------------|
| Unknown | 162,310 | 39.6% |
| Recovered/resolved | 94,737 | 23.1% |
| Not recovered | 77,721 | 18.9% |
| Recovering | 49,367 | 12.0% |
| Fatal | 22,128 | 5.4% |
| Recovered with sequelae | 4,930 | 1.2% |

### 2.4 Age Distribution

| Age Group | Reports | Percentage |
|-----------|---------|------------|
| Elderly | 38,510 | 61.3% |
| Adult | 24,302 | 38.7% |
| Other | 152 | <1% |

*Source: FAERS via FAERS_count_reactions_by_drug_event, FAERS_count_seriousness_by_drug_event*
```

---

## Phase 2: Disproportionality Analysis (Signal Detection)

### 2.1 Calculate Signal Metrics

**CRITICAL**: This is the core of the skill. For each top adverse event (at least top 15-20), calculate PRR, ROR, and IC with 95% confidence intervals.

```python
# For each significant adverse event, calculate disproportionality
top_events = ["Rhabdomyolysis", "Myalgia", "Hepatotoxicity", "Diabetes mellitus",
              "Acute kidney injury", "Myopathy", "Pancreatitis"]

for event in top_events:
    result = tu.tools.FAERS_calculate_disproportionality(
        operation="calculate_disproportionality",
        drug_name="ATORVASTATIN",
        adverse_event=event
    )
    # Response structure:
    # {
    #   status: "success",
    #   drug_name: "ATORVASTATIN",
    #   adverse_event: "Rhabdomyolysis",
    #   contingency_table: {
    #     a_drug_and_event: 2226,
    #     b_drug_no_event: 241655,
    #     c_no_drug_event: 37658,
    #     d_no_drug_no_event: 19725450
    #   },
    #   metrics: {
    #     ROR: {value: 4.825, ci_95_lower: 4.622, ci_95_upper: 5.037},
    #     PRR: {value: 4.79, ci_95_lower: 4.59, ci_95_upper: 4.998},
    #     IC: {value: 2.194, ci_95_lower: 2.136, ci_95_upper: 2.252}
    #   },
    #   signal_detection: {
    #     signal_detected: true,
    #     signal_strength: "Strong signal",
    #     criteria: "ROR lower CI > 1.0 and case count >= 3"
    #   }
    # }
```

### 2.2 Signal Detection Criteria

**Proportional Reporting Ratio (PRR)**:
- PRR = (a/(a+b)) / (c/(c+d))
- Signal: PRR >= 2.0 AND lower 95% CI > 1.0 AND case count >= 3

**Reporting Odds Ratio (ROR)**:
- ROR = (a*d) / (b*c)
- Signal: Lower 95% CI > 1.0

**Information Component (IC)**:
- IC = log2(observed/expected)
- Signal: Lower 95% CI > 0

### 2.3 Signal Strength Classification

| Strength | PRR | ROR Lower CI | IC Lower CI | Clinical Action |
|----------|-----|-------------|-------------|-----------------|
| **Strong** | >= 5.0 | >= 3.0 | >= 2.0 | Immediate investigation required |
| **Moderate** | 3.0-4.9 | 2.0-2.9 | 1.0-1.9 | Active monitoring recommended |
| **Weak** | 2.0-2.9 | 1.0-1.9 | 0-0.9 | Routine monitoring, watch for trends |
| **No signal** | < 2.0 | < 1.0 | < 0 | Standard pharmacovigilance |

### 2.4 Demographic Stratification of Key Signals

```python
# For strong/moderate signals, stratify by demographics
result = tu.tools.FAERS_stratify_by_demographics(
    operation="stratify_by_demographics",
    drug_name="ATORVASTATIN",
    adverse_event="Rhabdomyolysis",
    stratify_by="sex"  # Options: sex, age, country
)
# Response: {status: "success", total_reports: 1996,
#   stratification: [{group: 1, count: 1190, percentage: 59.62},  # 1=Male
#                    {group: 2, count: 781, percentage: 39.13}]}    # 2=Female
```

**Note on sex codes**: group 0 = Unknown, group 1 = Male, group 2 = Female.

### 2.5 Output for Report

```markdown
## 3. Disproportionality Analysis (Signal Detection)

### 3.1 Signal Detection Summary

| Adverse Event | Cases (a) | PRR | PRR 95% CI | ROR | ROR 95% CI | IC | Signal |
|---------------|-----------|-----|------------|-----|------------|-----|--------|
| Rhabdomyolysis | 2,226 | 4.79 | 4.59-5.00 | 4.83 | 4.62-5.04 | 2.19 | **STRONG** |
| Myopathy | 1,234 | 6.12 | 5.72-6.55 | 6.18 | 5.77-6.62 | 2.54 | **STRONG** |
| Myalgia | 9,189 | 2.31 | 2.26-2.37 | 2.33 | 2.28-2.39 | 1.18 | Moderate |
| Hepatotoxicity | 456 | 3.45 | 3.10-3.84 | 3.48 | 3.13-3.87 | 1.72 | Moderate |
| Diabetes mellitus | 3,021 | 1.89 | 1.82-1.96 | 1.90 | 1.83-1.97 | 0.91 | Weak |
| Pancreatitis | 678 | 2.15 | 1.97-2.34 | 2.16 | 1.98-2.35 | 1.08 | Weak |

### 3.2 Demographics of Key Signals

**Rhabdomyolysis** (n=1,996):
- Male: 59.6%, Female: 39.1%, Unknown: 1.3%
- Predominantly elderly (>65 years)

*Source: FAERS via FAERS_calculate_disproportionality, FAERS_stratify_by_demographics*
```

---

## Phase 3: FDA Label Safety Information

### 3.1 Extract Label Sections

```python
# Boxed warnings
boxed = tu.tools.FDA_get_boxed_warning_info_by_drug_name(drug_name="atorvastatin")
# Response: {meta: {total: N}, results: [{boxed_warning: ["...text..."]}]}
# NOTE: Returns {error: {code: "NOT_FOUND"}} if no boxed warning exists

# Contraindications
contras = tu.tools.FDA_get_contraindications_by_drug_name(drug_name="atorvastatin")
# Response: {meta: {total: N}, results: [{openfda.generic_name: [...], contraindications: ["...text..."]}]}

# Warnings and precautions
warnings = tu.tools.FDA_get_warnings_by_drug_name(drug_name="atorvastatin")
# Response: {meta: {total: N}, results: [{warnings: ["...text..."], boxed_warning: [...]}]}

# Adverse reactions from label
adverse_rxns = tu.tools.FDA_get_adverse_reactions_by_drug_name(drug_name="atorvastatin")
# Response: {meta: {total: N}, results: [{adverse_reactions: ["...text..."]}]}

# Drug interactions from label
interactions = tu.tools.FDA_get_drug_interactions_by_drug_name(drug_name="atorvastatin")
# Response: {meta: {total: N}, results: [{drug_interactions: ["...text..."]}]}

# Pregnancy/breastfeeding
pregnancy = tu.tools.FDA_get_pregnancy_or_breastfeeding_info_by_drug_name(drug_name="atorvastatin")

# Geriatric use
geriatric = tu.tools.FDA_get_geriatric_use_info_by_drug_name(drug_name="atorvastatin")

# Pediatric use
pediatric = tu.tools.FDA_get_pediatric_use_info_by_drug_name(drug_name="atorvastatin")

# Pharmacogenomics from label
pgx_label = tu.tools.FDA_get_pharmacogenomics_info_by_drug_name(drug_name="atorvastatin")
```

### 3.2 Handling No Results

**IMPORTANT**: FDA label tools return `{error: {code: "NOT_FOUND"}}` when a section does not exist. This is NORMAL for many drugs - for example, most drugs do NOT have boxed warnings. Always check for this pattern:

```python
# Check if boxed warning exists
if isinstance(boxed, dict) and 'error' in boxed:
    boxed_warning_text = "None (no boxed warning for this drug)"
else:
    boxed_warning_text = boxed['results'][0].get('boxed_warning', ['None'])[0]
```

### 3.3 Output for Report

```markdown
## 4. FDA Label Safety Information

### 4.1 Boxed Warning
None

### 4.2 Contraindications
- Acute liver failure or decompensated cirrhosis
- Hypersensitivity to atorvastatin (includes anaphylaxis, angioedema, SJS, TEN)

### 4.3 Warnings and Precautions
| Warning | Clinical Relevance |
|---------|-------------------|
| Myopathy/Rhabdomyolysis | Risk with CYP3A4 inhibitors, high doses |
| Immune-Mediated Necrotizing Myopathy | Rare autoimmune myopathy |
| Hepatic Dysfunction | Monitor LFTs |
| Increased HbA1c/Glucose | Diabetes risk |

### 4.4 Drug Interactions (from label)
| Interacting Drug | Mechanism | Clinical Action |
|-----------------|-----------|-----------------|
| Cyclosporine | Increased exposure | Avoid combination |
| CYP3A4 inhibitors | Increased atorvastatin levels | Use lowest dose |
| Gemfibrozil | Increased myopathy risk | Avoid |

### 4.5 Special Populations
- **Pregnancy**: Contraindicated
- **Geriatric**: No dose adjustment needed
- **Pediatric**: Approved for heterozygous FH ages 10+

*Source: FDA drug labels via FDA_get_contraindications_by_drug_name, FDA_get_warnings_by_drug_name*
```

---

## Phase 4: Mechanism-Based Adverse Event Context

### 4.1 Target Safety Profile

```python
# Get target safety data from OpenTargets
# First get target ensembl ID from MOA result
target_id = "ENSG00000113161"  # HMGCR from Phase 0

safety = tu.tools.OpenTargets_get_target_safety_profile_by_ensemblID(ensemblId=target_id)
# Response: {data: {target: {id: "...", approvedSymbol: "HMGCR",
#   safetyLiabilities: [{event: "Decrease, Fertility", eventId: "...",
#     effects: [{direction: "Inhibition/Decrease/Downregulation"}],
#     studies: [{type: "cell-based"}], datasource: "AOP-Wiki"}]}}}

# Get OpenTargets adverse events (uses FAERS data)
ot_aes = tu.tools.OpenTargets_get_drug_adverse_events_by_chemblId(chemblId="CHEMBL1487")
# Response: {data: {drug: {adverseEvents: {count: 13, criticalValue: 513.67,
#   rows: [{name: "myalgia", meddraCode: "10028411", count: 4126, logLR: 6067.33}, ...]}}}}
```

### 4.2 ADMET Predictions (if SMILES available)

```python
# Get SMILES from DrugBank/PharmGKB
smiles = "CC(C)C1=C(C(=C(N1CC[C@H](C[C@H](CC(=O)O)O)O)C2=CC=C(C=C2)F)C3=CC=CC=C3)C(=O)NC4=CC=CC=C4"

# Toxicity predictions
toxicity = tu.tools.ADMETAI_predict_toxicity(smiles=[smiles])
# Response: predictions for hepatotoxicity, cardiotoxicity, etc.

# CYP interaction predictions
cyp = tu.tools.ADMETAI_predict_CYP_interactions(smiles=[smiles])
# Response: CYP inhibition/substrate predictions
```

### 4.3 Drug Warnings from OpenTargets

```python
# Drug warnings (withdrawals, safety warnings)
warnings = tu.tools.OpenTargets_get_drug_warnings_by_chemblId(chemblId="CHEMBL1487")
# Response: {data: {drug: {id: "CHEMBL1487", name: "ATORVASTATIN"}}}
# Note: Empty if no warnings exist
```

### 4.4 Output for Report

```markdown
## 5. Mechanism-Based Adverse Event Context

### 5.1 Target Safety Profile (HMGCR)
| Safety Liability | Direction | Evidence | Source |
|-----------------|-----------|----------|--------|
| Decreased fertility | Inhibition | Cell-based | AOP-Wiki |

### 5.2 OpenTargets Significant Adverse Events
| Adverse Event | FAERS Count | log(LR) | MedDRA Code |
|---------------|-------------|---------|-------------|
| Myalgia | 4,126 | 6,067 | 10028411 |
| Rhabdomyolysis | 2,546 | 4,788 | 10039020 |
| CPK increased | 1,709 | 2,909 | 10005470 |

### 5.3 ADMET Predictions
| Property | Prediction | Confidence |
|----------|-----------|------------|
| Hepatotoxicity | Moderate risk | 0.65 |
| Cardiotoxicity (hERG) | Low risk | 0.23 |
| CYP3A4 substrate | Yes | 0.92 |

*Source: OpenTargets, ADMETAI*
```

---

## Phase 5: Comparative Safety Analysis

### 5.1 Compare to Drug Class

```python
# Head-to-head comparison with class member
comparison = tu.tools.FAERS_compare_drugs(
    operation="compare_drugs",
    drug1="ATORVASTATIN",
    drug2="SIMVASTATIN",
    adverse_event="Rhabdomyolysis"
)
# Response: {status: "success", adverse_event: "Rhabdomyolysis",
#   drug1: {name: "ATORVASTATIN", metrics: {PRR: {value: 4.79, ...}, ROR: {...}, IC: {...}},
#           signal_detection: {signal_detected: true, signal_strength: "Strong signal"}},
#   drug2: {name: "SIMVASTATIN", metrics: {PRR: {value: 12.78, ...}, ...}},
#   comparison: "SIMVASTATIN shows stronger signal than ATORVASTATIN"}

# Compare multiple events across class members
class_drugs = ["ATORVASTATIN", "SIMVASTATIN", "ROSUVASTATIN", "PRAVASTATIN"]
key_events = ["Rhabdomyolysis", "Myalgia", "Hepatotoxicity", "Diabetes mellitus"]
# Run FAERS_compare_drugs for each pair and event combination

# Aggregate adverse events across drug class
class_aes = tu.tools.FAERS_count_additive_adverse_reactions(
    medicinalproducts=class_drugs
)
# Response: [{term: "FATIGUE", count: N}, ...]

# Aggregate seriousness across class
class_serious = tu.tools.FAERS_count_additive_seriousness_classification(
    medicinalproducts=class_drugs
)
# Response: [{term: "Serious", count: N}, {term: "Non-serious", count: N}]
```

### 5.2 Output for Report

```markdown
## 6. Comparative Safety Analysis (Statin Class)

### 6.1 Head-to-Head: Rhabdomyolysis

| Drug | PRR | PRR 95% CI | ROR | Cases | Signal |
|------|-----|------------|-----|-------|--------|
| Simvastatin | 12.78 | 12.43-13.14 | 13.05 | 5,234 | **STRONG** |
| Atorvastatin | 4.79 | 4.59-5.00 | 4.83 | 2,226 | **STRONG** |
| Rosuvastatin | 3.45 | 3.21-3.71 | 3.47 | 1,102 | Moderate |
| Pravastatin | 5.67 | 5.28-6.09 | 5.72 | 1,876 | **STRONG** |

### 6.2 Class-Wide vs Drug-Specific Signals

| Signal Type | Events |
|-------------|--------|
| **Class-wide** (all statins) | Myalgia, Rhabdomyolysis, CPK elevation, Hepatotoxicity |
| **Drug-specific** (atorvastatin) | [None identified - all signals are class-wide] |

*Source: FAERS via FAERS_compare_drugs*
```

---

## Phase 6: Drug-Drug Interactions & Risk Factors

### 6.1 Drug-Drug Interactions

```python
# FDA label DDIs
ddi_label = tu.tools.FDA_get_drug_interactions_by_drug_name(drug_name="atorvastatin")
# Response: {results: [{drug_interactions: ["...text..."]}]}

# DrugBank interactions
ddi_db = tu.tools.drugbank_get_drug_interactions_by_drug_name_or_id(
    query="atorvastatin", case_sensitive=False, exact_match=False, limit=3
)

# DailyMed DDIs
ddi_dailymed = tu.tools.DailyMed_parse_drug_interactions(drug_name="atorvastatin")
```

### 6.2 Pharmacogenomic Risk Factors

```python
# PharmGKB drug search
pgx_search = tu.tools.PharmGKB_search_drugs(query="atorvastatin")
# Response: {status: "success", data: [{id: "PA448500", name: "atorvastatin", smiles: "..."}]}

# Get detailed PGx info
pgx_details = tu.tools.PharmGKB_get_drug_details(drug_id="PA448500")

# PharmGKB dosing guidelines
dosing = tu.tools.PharmGKB_get_dosing_guidelines(gene="SLCO1B1")
# SLCO1B1 is key pharmacogene for statins

# FDA PGx biomarkers
fda_pgx = tu.tools.fda_pharmacogenomic_biomarkers(drug_name="atorvastatin", limit=10)
# Response: {count: N, results: [{drug_name: "...", biomarker: "...", ...}]}
# Note: May return empty results for some drugs
```

### 6.3 Output for Report

```markdown
## 7. Drug-Drug Interactions & Pharmacogenomic Risk

### 7.1 Key Drug-Drug Interactions
| Interacting Drug | Mechanism | Risk | Management |
|-----------------|-----------|------|------------|
| Cyclosporine | CYP3A4 inhibition | Rhabdomyolysis | Avoid combination |
| Clarithromycin | CYP3A4 inhibition | Myopathy | Limit to 20mg/day |
| Gemfibrozil | Glucuronidation inhibition | Myopathy | Avoid combination |
| Niacin (>1g/day) | Additive myotoxicity | Myopathy | Monitor closely |

### 7.2 Pharmacogenomic Risk Factors
| Gene | Variant | Phenotype | Recommendation | Evidence |
|------|---------|-----------|----------------|----------|
| SLCO1B1 | rs4149056 (*5) | Reduced transport | Consider lower dose | Level 1A |
| CYP3A4 | *22 (rs35599367) | Poor metabolizer | Increased exposure | Level 3 |

*Source: FDA label, PharmGKB, fda_pharmacogenomic_biomarkers*
```

---

## Phase 7: Literature Evidence

### 7.1 Search Published Literature

```python
# PubMed safety studies
pubmed = tu.tools.PubMed_search_articles(
    query='atorvastatin adverse events safety rhabdomyolysis',
    limit=20
)
# Response: [{pmid: "...", title: "...", authors: [...], journal: "...",
#   pub_date: "...", pub_year: "...", doi: "..."}]

# Citation analysis via OpenAlex
openalex = tu.tools.openalex_search_works(
    query="atorvastatin safety adverse events",
    limit=15
)

# Preprints via EuropePMC
preprints = tu.tools.EuropePMC_search_articles(
    query="atorvastatin safety signal",
    source="PPR",
    pageSize=10
)
```

### 7.2 Output for Report

```markdown
## 8. Literature Evidence

### 8.1 Key Safety Publications
| PMID | Title | Year | Journal |
|------|-------|------|---------|
| 41657777 | Differential musculoskeletal outcome reporting... | 2026 | Front Pharmacol |
| ... | ... | ... | ... |

### 8.2 Evidence Summary
| Evidence Type | Count | Key Findings |
|---------------|-------|--------------|
| Meta-analyses | 5 | Statin myopathy 5-10%, rhabdomyolysis rare |
| RCTs | 12 | CV benefit outweighs muscle risk |
| Case reports | 23 | Severe rhabdomyolysis with CYP3A4 inhibitors |

*Source: PubMed, OpenAlex*
```

---

## Phase 8: Risk Assessment & Safety Signal Score

### 8.1 Safety Signal Score Calculation (0-100)

The Safety Signal Score quantifies overall drug safety concern on a 0-100 scale (higher = more concern).

**Component 1: FAERS Signal Strength (0-35 points)**
```
If any signal has PRR >= 5 AND ROR lower CI >= 3: 35 points
If any signal has PRR 3-5 AND ROR lower CI 2-3: 20 points
If any signal has PRR 2-3 AND ROR lower CI 1-2: 10 points
If no signals detected: 0 points
```

**Component 2: Serious Adverse Events (0-30 points)**
```
Deaths reported with high count (>100): 30 points
Deaths reported with low count (1-100): 25 points
Life-threatening events: 20 points
Hospitalizations only: 15 points
Non-serious only: 0 points
```

**Component 3: FDA Label Warnings (0-25 points)**
```
Boxed warning present: 25 points
Drug withdrawn or restricted: 25 points
Contraindications present: 15 points
Warnings and precautions: 10 points
Adverse reactions only: 5 points
No label warnings: 0 points
```

**Component 4: Literature Evidence (0-10 points)**
```
Meta-analyses confirming safety signals: 10 points
Multiple RCTs with safety concerns: 7 points
Case reports/case series: 4 points
No published safety concerns: 0 points
```

**Total Score Interpretation:**
| Score Range | Interpretation | Action |
|-------------|---------------|--------|
| **75-100** | High concern | Serious safety signals; requires immediate regulatory attention |
| **50-74** | Moderate concern | Significant monitoring needed; consider risk mitigation |
| **25-49** | Low-moderate concern | Routine enhanced monitoring; standard risk management |
| **0-24** | Low concern | Standard safety profile; routine pharmacovigilance |

### 8.2 Evidence Grading

| Tier | Criteria | Example |
|------|----------|---------|
| **T1** | Boxed warning, confirmed by RCTs, PRR > 10 | Metformin: Lactic acidosis |
| **T2** | Label warning + FAERS signal (PRR 3-10) + published studies | Atorvastatin: Rhabdomyolysis |
| **T3** | FAERS signal (PRR 2-3) + case reports | Atorvastatin: Pancreatitis |
| **T4** | Computational prediction only (ADMET) or weak signal | ADMETAI hepatotoxicity prediction |

### 8.3 Output for Report

```markdown
## 9. Risk Assessment

### 9.1 Safety Signal Score: 62/100 (MODERATE CONCERN)

| Component | Score | Max | Rationale |
|-----------|-------|-----|-----------|
| FAERS Signal Strength | 35 | 35 | Strong signals (PRR >= 5 for rhabdomyolysis) |
| Serious Adverse Events | 15 | 30 | Hospitalizations; deaths uncommon for drug itself |
| FDA Label Warnings | 10 | 25 | Warnings/precautions but no boxed warning |
| Literature Evidence | 7 | 10 | Multiple RCTs confirm muscle-related risks |
| **TOTAL** | **62** | **100** | **MODERATE CONCERN** |

### 9.2 Evidence-Graded Signals

| Signal | Grade | PRR | Serious | Label | Literature | Overall |
|--------|-------|-----|---------|-------|------------|---------|
| Rhabdomyolysis | T2 | 4.79 | Yes | Warning | Confirmed | Moderate |
| Myopathy | T2 | 6.12 | Yes | Warning | Confirmed | Moderate |
| Hepatotoxicity | T3 | 3.45 | Rare | Warning | Case reports | Low-Moderate |
| Diabetes risk | T3 | 1.89 | No | Warning | RCT data | Low |
```

---

## Phase 9: Report Synthesis & Recommendations

### 9.1 Report Template

**File**: `[DRUG]_adverse_event_report.md`

```markdown
# Adverse Drug Event Signal Detection Report: [DRUG]

**Generated**: [Date] | **Drug**: [Generic Name] | **ChEMBL ID**: [ID]
**Safety Signal Score**: [XX/100] ([INTERPRETATION])

---

## Executive Summary

[2-3 paragraph summary of key findings]

**Key Safety Signals**:
1. [Strongest signal with PRR/ROR]
2. [Second signal]
3. [Third signal]

**Regulatory Status**: [Boxed warning Y/N] | [Withdrawn Y/N] | [Restrictions]

---

## 1. Drug Identification
[Phase 0 output]

## 2. FAERS Adverse Event Profile
[Phase 1 output]

## 3. Disproportionality Analysis
[Phase 2 output]

## 4. FDA Label Safety Information
[Phase 3 output]

## 5. Mechanism-Based Context
[Phase 4 output]

## 6. Comparative Safety Analysis
[Phase 5 output]

## 7. Drug-Drug Interactions & PGx Risk
[Phase 6 output]

## 8. Literature Evidence
[Phase 7 output]

## 9. Risk Assessment
[Phase 8 output]

## 10. Clinical Recommendations

### 10.1 Monitoring Recommendations
| Parameter | Frequency | Rationale |
|-----------|-----------|-----------|
| [Lab test] | [Frequency] | [Why] |

### 10.2 Risk Mitigation Strategies
| Risk | Mitigation | Evidence |
|------|-----------|----------|
| [Risk] | [Strategy] | [Source] |

### 10.3 Patient Counseling Points
- [Point 1]
- [Point 2]

### 10.4 Populations at Higher Risk
| Population | Risk Factor | Recommendation |
|-----------|-------------|----------------|
| [Group] | [Factor] | [Action] |

---

## 11. Completeness Checklist
[See below]

## 12. Data Sources
[All tools and databases used with timestamps]
```

---

## Completeness Checklist

### Phase 0: Drug Disambiguation
- [ ] Generic name resolved
- [ ] ChEMBL ID obtained
- [ ] DrugBank ID obtained
- [ ] Drug class identified
- [ ] Mechanism of action stated
- [ ] Primary target identified
- [ ] Blackbox/withdrawal status checked

### Phase 1: FAERS Profiling
- [ ] Top adverse events queried (>=15 events)
- [ ] Seriousness distribution obtained
- [ ] Outcome distribution obtained
- [ ] Age distribution obtained
- [ ] Death-related events counted
- [ ] Reporter country distribution obtained

### Phase 2: Disproportionality Analysis
- [ ] PRR calculated for >= 10 adverse events
- [ ] ROR with 95% CI for each event
- [ ] IC with 95% CI for each event
- [ ] Signal strength classified for each
- [ ] Demographics stratified for strong signals

### Phase 3: FDA Label
- [ ] Boxed warnings checked (or confirmed none)
- [ ] Contraindications extracted
- [ ] Warnings and precautions extracted
- [ ] Adverse reactions from label
- [ ] Drug interactions from label
- [ ] Special populations (pregnancy, geriatric, pediatric)

### Phase 4: Mechanism Context
- [ ] Target safety profile (OpenTargets)
- [ ] OpenTargets adverse events queried
- [ ] ADMET predictions (if SMILES available)

### Phase 5: Comparative Analysis
- [ ] At least 1 class comparison performed
- [ ] Class-wide vs drug-specific signals identified
- [ ] Aggregate class AEs computed (if applicable)

### Phase 6: DDIs & PGx
- [ ] DDIs from FDA label extracted
- [ ] PharmGKB queried
- [ ] Dosing guidelines checked
- [ ] FDA PGx biomarkers checked

### Phase 7: Literature
- [ ] PubMed searched (>=10 articles)
- [ ] OpenAlex citation analysis (if time permits)
- [ ] Key safety publications cited

### Phase 8: Risk Assessment
- [ ] Safety Signal Score calculated (0-100)
- [ ] Each signal evidence-graded (T1-T4)
- [ ] Score interpretation provided

### Phase 9: Report
- [ ] Report file created and saved
- [ ] Executive summary written
- [ ] Monitoring recommendations provided
- [ ] Risk mitigation strategies listed
- [ ] Patient counseling points included
- [ ] All sources cited

---

## Tool Parameter Reference (Verified)

### FAERS Tools (OpenFDA-based)

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `FAERS_count_reactions_by_drug_event` | `medicinalproduct` (REQUIRED), `patientsex`, `patientagegroup`, `occurcountry` | Returns [{term, count}] |
| `FAERS_count_seriousness_by_drug_event` | `medicinalproduct` (REQUIRED), `patientsex`, `patientagegroup`, `occurcountry` | Returns [{term: "Serious"/"Non-serious", count}] |
| `FAERS_count_outcomes_by_drug_event` | `medicinalproduct` (REQUIRED), `patientsex`, `patientagegroup`, `occurcountry` | Returns [{term: "Fatal"/"Recovered"/..., count}] |
| `FAERS_count_patient_age_distribution` | `medicinalproduct` (REQUIRED) | Returns [{term: "Elderly"/"Adult"/..., count}] |
| `FAERS_count_death_related_by_drug` | `medicinalproduct` (REQUIRED) | Returns [{term: "alive"/"death", count}] |
| `FAERS_count_reportercountry_by_drug_event` | `medicinalproduct` (REQUIRED), `patientsex`, `patientagegroup`, `serious` | Returns [{term: "US"/"GB"/..., count}] |
| `FAERS_search_adverse_event_reports` | `medicinalproduct`, `limit` (max 100), `skip` | Returns individual case reports with patient/drug/reaction data |
| `FAERS_search_reports_by_drug_and_reaction` | `medicinalproduct` (REQUIRED), `reactionmeddrapt` (REQUIRED), `limit`, `skip`, `patientsex`, `serious` | Returns individual reports filtered by specific reaction |
| `FAERS_search_serious_reports_by_drug` | `medicinalproduct` (REQUIRED), `seriousnessdeath`, `seriousnesshospitalization`, `seriousnesslifethreatening`, `seriousnessdisabling`, `limit` | Returns serious event reports |

### FAERS Analytics Tools (operation-based)

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `FAERS_calculate_disproportionality` | `operation`="calculate_disproportionality", `drug_name` (REQUIRED), `adverse_event` (REQUIRED) | Returns PRR, ROR, IC with 95% CI and signal detection |
| `FAERS_analyze_temporal_trends` | `operation`="analyze_temporal_trends", `drug_name` (REQUIRED), `adverse_event` (optional) | Returns yearly counts and trend direction |
| `FAERS_compare_drugs` | `operation`="compare_drugs", `drug1` (REQUIRED), `drug2` (REQUIRED), `adverse_event` (REQUIRED) | Returns PRR/ROR/IC for both drugs side-by-side |
| `FAERS_filter_serious_events` | `operation`="filter_serious_events", `drug_name` (REQUIRED), `seriousness_type` (death/hospitalization/disability/life_threatening/all) | Returns top serious reactions with counts |
| `FAERS_stratify_by_demographics` | `operation`="stratify_by_demographics", `drug_name` (REQUIRED), `adverse_event` (REQUIRED), `stratify_by` (sex/age/country) | Returns stratified counts and percentages. Sex codes: 0=Unknown, 1=Male, 2=Female |
| `FAERS_rollup_meddra_hierarchy` | `operation`="rollup_meddra_hierarchy", `drug_name` (REQUIRED) | Returns top 50 preferred terms with counts |

### FAERS Aggregate Tools (multi-drug)

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `FAERS_count_additive_adverse_reactions` | `medicinalproducts` (REQUIRED, array), `patientsex`, `patientagegroup`, `occurcountry`, `serious`, `seriousnessdeath` | Aggregates AE counts across multiple drugs |
| `FAERS_count_additive_seriousness_classification` | `medicinalproducts` (REQUIRED, array), `patientsex`, `patientagegroup`, `occurcountry` | Aggregates seriousness across multiple drugs |
| `FAERS_count_additive_reaction_outcomes` | `medicinalproducts` (REQUIRED, array) | Aggregates outcomes across multiple drugs |

### FDA Label Tools

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `FDA_get_boxed_warning_info_by_drug_name` | `drug_name` | Returns `{error: {code: "NOT_FOUND"}}` if no boxed warning |
| `FDA_get_contraindications_by_drug_name` | `drug_name` | Returns `{meta: {total: N}, results: [{contraindications: [...]}]}` |
| `FDA_get_adverse_reactions_by_drug_name` | `drug_name` | Returns `{meta: {total: N}, results: [{adverse_reactions: [...]}]}` |
| `FDA_get_warnings_by_drug_name` | `drug_name` | Returns `{meta: {total: N}, results: [{warnings: [...]}]}` |
| `FDA_get_drug_interactions_by_drug_name` | `drug_name` | Returns `{meta: {total: N}, results: [{drug_interactions: [...]}]}` |
| `FDA_get_pharmacogenomics_info_by_drug_name` | `drug_name` | Returns PGx info from label |
| `FDA_get_pregnancy_or_breastfeeding_info_by_drug_name` | `drug_name` | Returns pregnancy info |
| `FDA_get_geriatric_use_info_by_drug_name` | `drug_name` | Returns geriatric use info |
| `FDA_get_pediatric_use_info_by_drug_name` | `drug_name` | Returns pediatric info |

### OpenTargets Tools

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `OpenTargets_get_drug_chembId_by_generic_name` | `drugName` | Returns `{data: {search: {hits: [{id, name, description}]}}}` |
| `OpenTargets_get_drug_adverse_events_by_chemblId` | `chemblId` | Returns `{data: {drug: {adverseEvents: {count, rows: [{name, meddraCode, count, logLR}]}}}}` |
| `OpenTargets_get_drug_blackbox_status_by_chembl_ID` | `chemblId` | Returns `{data: {drug: {hasBeenWithdrawn, blackBoxWarning}}}` |
| `OpenTargets_get_drug_warnings_by_chemblId` | `chemblId` | Returns drug warnings (may be empty) |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | `chemblId` | Returns `{data: {drug: {mechanismsOfAction: {rows: [{mechanismOfAction, actionType, targetName, targets}]}}}}` |
| `OpenTargets_get_drug_indications_by_chemblId` | `chemblId` | Returns approved and investigational indications |
| `OpenTargets_get_target_safety_profile_by_ensemblID` | `ensemblId` | Returns `{data: {target: {safetyLiabilities: [{event, effects, studies, datasource}]}}}` |

### DrugBank Tools

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `drugbank_get_safety_by_drug_name_or_drugbank_id` | `query`, `case_sensitive` (bool), `exact_match` (bool), `limit` | Returns toxicity, food interactions |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Returns drug targets |
| `drugbank_get_drug_interactions_by_drug_name_or_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Returns DDIs |
| `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Returns pharmacology |

### PharmGKB Tools

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `PharmGKB_search_drugs` | `query` | Returns `{data: [{id, name, smiles}]}` |
| `PharmGKB_get_drug_details` | `drug_id` (e.g., "PA448500") | Returns detailed drug info |
| `PharmGKB_get_dosing_guidelines` | `guideline_id`, `gene` (both optional) | Returns dosing guidelines |
| `PharmGKB_get_clinical_annotations` | `annotation_id`, `gene_id` (both optional) | Returns clinical annotations |
| `fda_pharmacogenomic_biomarkers` | `drug_name`, `biomarker`, `limit` | Returns `{count, results: [...]}` |

### ADMETAI Tools

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `ADMETAI_predict_toxicity` | `smiles` (REQUIRED, array of strings) | Predicts hepatotoxicity, cardiotoxicity, etc. |
| `ADMETAI_predict_CYP_interactions` | `smiles` (REQUIRED, array) | Predicts CYP inhibition/substrate |

### Literature Tools

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `PubMed_search_articles` | `query`, `limit` | Returns list of article dicts |
| `openalex_search_works` | `query`, `limit` | Returns works with citation counts |
| `EuropePMC_search_articles` | `query`, `source` ("PPR" for preprints), `pageSize` | Returns articles including preprints |
| `search_clinical_trials` | `query_term` (REQUIRED), `condition`, `intervention`, `pageSize` | Returns clinical trials |

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `FAERS_calculate_disproportionality` | Manual calculation from `FAERS_count_*` data | Literature PRR values |
| `FAERS_count_reactions_by_drug_event` | `FAERS_rollup_meddra_hierarchy` | OpenTargets adverse events |
| `FDA_get_boxed_warning_info_by_drug_name` | `OpenTargets_get_drug_blackbox_status_by_chembl_ID` | DrugBank safety |
| `FDA_get_contraindications_by_drug_name` | `FDA_get_warnings_by_drug_name` | DrugBank safety |
| `OpenTargets_get_drug_chembId_by_generic_name` | `ChEMBL_search_drugs` | Manual search |
| `PharmGKB_search_drugs` | `fda_pharmacogenomic_biomarkers` | FDA label PGx section |
| `PubMed_search_articles` | `openalex_search_works` | `EuropePMC_search_articles` |

---

## Common Patterns

### Pattern 1: Full Safety Signal Profile for a Single Drug
Use all phases (0-9) for comprehensive report. Best for regulatory submissions, safety reviews.

### Pattern 2: Specific Adverse Event Investigation
Focus on Phases 0, 2, 3, 7. User asks "Does [drug] cause [event]?" - calculate disproportionality for that specific event, check label, search literature.

### Pattern 3: Drug Class Comparison
Focus on Phases 0, 2, 5. Compare 3-5 drugs in same class for a specific adverse event using `FAERS_compare_drugs`.

### Pattern 4: Emerging Signal Detection
Focus on Phases 1, 2, 7. Screen top 20+ FAERS events for signals, identify any not in FDA label (Phase 3), search recent literature for confirmation.

### Pattern 5: Pharmacogenomic Risk Assessment
Focus on Phases 0, 6. Identify genetic risk factors for adverse events using PharmGKB and FDA PGx biomarkers.

### Pattern 6: Pre-Approval Safety Assessment
Focus on Phases 4, 7. Use ADMET predictions and target safety profiles when FAERS data is limited (new drugs).

---

## Edge Cases

### Drug with No FAERS Reports
- Skip Phases 1-2
- Rely on FDA label (Phase 3), mechanism predictions (Phase 4), and literature (Phase 7)
- Safety Signal Score will be lower due to lack of signal detection data

### Generic vs Brand Name
- Always try both names in FAERS queries (FAERS uses brand names sometimes)
- Use `OpenTargets_get_drug_chembId_by_generic_name` to resolve to standard identifier
- Use `FDA_get_brand_name_generic_name` for name cross-reference

### Drug Combinations
- Use `FAERS_search_reports_by_drug_combination` for polypharmacy analysis
- Distinguish combination AEs from individual drug AEs
- Use `FAERS_count_additive_adverse_reactions` for aggregate class analysis

### Confounding by Indication
- Compare AE profile to the disease being treated
- Example: "Death" reports for chemotherapy drugs may reflect disease progression
- Always note this limitation in the report

### Drugs with Boxed Warnings
- Score component automatically 25/25 for label warnings
- Prioritize boxed warning events in disproportionality analysis
- Cross-reference boxed warning with FAERS signal strength
