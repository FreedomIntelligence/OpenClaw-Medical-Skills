# tooluniverse-clinical-trial-design

> Strategic clinical trial design feasibility assessment using ToolUniverse. Evaluates patient population sizing, biomarker prevalence, endpoint selection, comparator analysis, safety monitoring, and regulatory pathways. Creates comprehensive feasibility reports with evidence grading, enrollment projections, and trial design recommendations. Use when planning Phase 1/2 trials, assessing trial feasibility, or designing biomarker-driven studies.

# Clinical Trial Design Feasibility Assessment

Systematically assess clinical trial feasibility by analyzing 6 research dimensions. Produces comprehensive feasibility reports with quantitative enrollment projections, endpoint recommendations, and regulatory pathway analysis.

**IMPORTANT**: Always use English terms in tool calls (drug names, disease names, biomarker names), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

## Core Principles

### 1. Report-First Approach (MANDATORY)
**DO NOT** show tool outputs to user. Instead:
1. Create `[INDICATION]_trial_feasibility_report.md` FIRST
2. Initialize with all section headers
3. Progressively update as data arrives
4. Present only the final report

### 2. Evidence Grading System

| Grade | Symbol | Criteria | Examples |
|-------|--------|----------|----------|
| **A** | ★★★ | Regulatory acceptance, multiple precedents | FDA-approved endpoint in same indication |
| **B** | ★★☆ | Clinical validation, single precedent | Phase 3 trial in related indication |
| **C** | ★☆☆ | Preclinical or exploratory | Phase 1 use, biomarker validation ongoing |
| **D** | ☆☆☆ | Proposed, no validation | Novel endpoint, no precedent |

### 3. Feasibility Score (0-100)
Weighted composite score:
- **Patient Availability** (30%): Population size × biomarker prevalence × geography
- **Endpoint Precedent** (25%): Historical use, regulatory acceptance
- **Regulatory Clarity** (20%): Pathway defined, precedents exist
- **Comparator Feasibility** (15%): Standard of care availability
- **Safety Monitoring** (10%): Known risks, monitoring established

---

## When to Use This Skill

Apply when users:
- Plan early-phase trials (Phase 1/2 emphasis)
- Need enrollment feasibility assessment
- Design biomarker-selected trials
- Evaluate endpoint strategies
- Assess regulatory pathways
- Compare trial design options
- Need safety monitoring plans

**Trigger phrases**: "clinical trial design", "trial feasibility", "enrollment projections", "endpoint selection", "trial planning", "Phase 1/2 design", "basket trial", "biomarker trial"

---

## Quick Start

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse(use_cache=True)
tu.load_tools()

# Example: EGFR+ NSCLC trial feasibility
indication = "EGFR-mutant non-small cell lung cancer"
biomarker = "EGFR L858R"

# Step 1: Get disease prevalence
disease_info = tu.tools.OpenTargets_get_disease_id_description_by_name(
    diseaseName="non-small cell lung cancer"
)

prevalence = tu.tools.OpenTargets_get_diseases_phenotypes(
    efoId=disease_info['data']['id']
)

# Step 2: Estimate biomarker prevalence
# EGFR mutations: ~15% of NSCLC in US, ~50% in Asia
variants = tu.tools.ClinVar_search_variants(
    gene="EGFR",
    significance="pathogenic"
)

# Step 3: Find precedent trials
trials = tu.tools.search_clinical_trials(
    condition="EGFR positive non-small cell lung cancer",
    status="completed",
    phase="2"
)

# Step 4: Identify standard of care comparator
soc_drugs = tu.tools.FDA_OrangeBook_search_drugs(
    ingredient="osimertinib"  # Current SOC for EGFR+ NSCLC
)

# Compile into feasibility report...
```

---

## Core Strategy: 6 Research Paths

Execute 6 parallel research dimensions:

```
Trial Design Query (e.g., "EGFR+ NSCLC trial, Phase 2, ORR endpoint")
│
├─ PATH 1: Patient Population Sizing
│   ├─ Disease prevalence (OpenTargets_get_diseases_phenotypes)
│   ├─ Biomarker prevalence (ClinVar, gnomAD, literature)
│   ├─ Geographic distribution (clinical trials, epidemiology)
│   ├─ Eligibility criteria impact (age, comorbidities)
│   └─ Patient availability calculator
│
├─ PATH 2: Biomarker Prevalence & Testing
│   ├─ Mutation frequency (ClinVar, COSMIC, gnomAD)
│   ├─ Testing availability (CLIA labs, FDA-approved tests)
│   ├─ Test turnaround time
│   ├─ Cost and reimbursement
│   └─ Alternative biomarkers (correlates, surrogates)
│
├─ PATH 3: Comparator Selection
│   ├─ Standard of care (FDA_OrangeBook, guidelines)
│   ├─ Approved comparators (DrugBank, FDA labels)
│   ├─ Historical controls feasibility
│   ├─ Placebo appropriateness
│   └─ Combination therapy considerations
│
├─ PATH 4: Endpoint Selection
│   ├─ Primary endpoint precedents (search_clinical_trials)
│   ├─ FDA acceptance history (FDA_get_approval_history)
│   ├─ Measurement feasibility (imaging, biomarkers)
│   ├─ Time to event considerations
│   └─ Surrogate vs clinical endpoints
│
├─ PATH 5: Safety Endpoints & Monitoring
│   ├─ Mechanism-based toxicity (drugbank_get_pharmacology)
│   ├─ Class effect toxicities (FAERS_search_reports)
│   ├─ Organ-specific monitoring (liver, cardiac, etc.)
│   ├─ Dose-limiting toxicity history
│   └─ Safety monitoring plan
│
└─ PATH 6: Regulatory Pathway
    ├─ Regulatory precedents (505(b)(1), 505(b)(2))
    ├─ Breakthrough therapy potential
    ├─ Orphan drug designation (if rare)
    ├─ Fast track eligibility
    └─ FDA guidance documents
```

---

## Report Structure (14 Sections)

Create `[INDICATION]_trial_feasibility_report.md` with:

### 1. Executive Summary
```markdown
# Clinical Trial Feasibility Report: [INDICATION]

**Date**: [YYYY-MM-DD]
**Trial Type**: [Phase 1/2, biomarker-selected, basket, etc.]
**Primary Endpoint**: [ORR, PFS, DLT, etc.]
**Feasibility Score**: [0-100] - [LOW/MODERATE/HIGH]

## Key Findings
- **Patient Availability**: [Est. enrollable patients/year in US]
- **Enrollment Timeline**: [Months to target N]
- **Endpoint Precedent**: [Grade A/B/C/D] - [Description]
- **Regulatory Pathway**: [505(b)(1), breakthrough, orphan, etc.]
- **Critical Risks**: [Top 3 feasibility risks]

## Go/No-Go Recommendation
[RECOMMEND PROCEED / RECOMMEND ADDITIONAL VALIDATION / DO NOT RECOMMEND]

Rationale: [2-3 sentence summary]
```

### 2. Disease Background
- Indication definition
- Prevalence and incidence (with sources)
- Current standard of care
- Unmet medical need
- Disease biology relevant to trial design

### 3. Patient Population Analysis
```markdown
## 3.1 Base Population Size
- **US Incidence**: [X per 100,000] [★★☆: Source]
- **Prevalence**: [Y total patients in US] [★★★: CDC/NCI data]
- **Annual new cases**: [Z patients/year]

## 3.2 Biomarker Selection Impact
- **Biomarker**: [e.g., EGFR L858R mutation]
- **Prevalence in disease**: [%] [★★★: ClinVar/COSMIC]
- **Geographic variation**: [Asian vs. Caucasian, etc.]
- **Testing availability**: [FDA-approved tests, CLIA labs]

## 3.3 Eligibility Criteria Funnel
| Criterion | Remaining Patients | % Retained |
|-----------|-------------------|------------|
| Base disease population | [N] | 100% |
| Biomarker positive | [N × biomarker %] | [%] |
| Age 18-75 | [N × age factor] | [%] |
| No prior therapy | [N × treatment-naive %] | [%] |
| ECOG 0-1 | [N × performance factor] | [%] |
| Adequate organ function | [N × eligibility factor] | [%] |
| **FINAL ELIGIBLE POOL** | **[N]** | **[%]** |

## 3.4 Geographic Distribution
- High-incidence regions: [e.g., Asia 50%, US 15% for EGFR+]
- Trial site implications
- Recruitment strategy recommendations

## 3.5 Enrollment Projections
**Assumptions**:
- Eligible pool: [N patients/year in US]
- Site activation: [M sites]
- Screening success rate: [%]
- Patients per site per month: [X]

**Target Enrollment**: [Total N]
**Projected Timeline**: [Months]
**Sites Required**: [Minimum M sites]
```

### 4. Biomarker Strategy
```markdown
## 4.1 Primary Biomarker
- **Biomarker**: [Gene mutation, protein expression, etc.]
- **Prevalence**: [%] [★★★: ClinVar data]
- **Assay Type**: [NGS, IHC, PCR, etc.]
- **FDA-Approved Tests**: [List CDx tests]
- **Turnaround Time**: [Days]
- **Cost**: [$X per test]

## 4.2 Alternative/Complementary Biomarkers
| Biomarker | Prevalence | Correlation | Testing |
|-----------|------------|-------------|---------|
| [Alt 1] | [%] | [R²] | [Method] |
| [Alt 2] | [%] | [R²] | [Method] |

## 4.3 Biomarker Testing Logistics
- Pre-screening vs. screening approach
- Central lab vs. local testing
- Tissue vs. liquid biopsy (ctDNA)
- Quality control requirements
```

### 5. Endpoint Selection & Justification
```markdown
## 5.1 Primary Endpoint
**Proposed**: [e.g., Objective Response Rate (ORR)]

**Regulatory Precedent** [★★★]:
- [N] FDA approvals in [indication] using ORR (2015-2024)
- Recent example: [Drug] approved [Year] (ORR XX%, n=YY)
- Source: search_clinical_trials, FDA_get_approval_history

**Measurement Feasibility**:
- Assessment method: [RECIST 1.1, irRECIST, etc.]
- Imaging modality: [CT, MRI, PET]
- Assessment frequency: [Every X weeks]
- Independent review: [Yes/No, cost]

**Statistical Considerations**:
- Expected ORR: [%] (based on [source])
- Null hypothesis: [%]
- Sample size: [N] (α=0.05, β=0.20, two-sided)
- Response duration: [Median months]

## 5.2 Secondary Endpoints
| Endpoint | Evidence Grade | Feasibility | Rationale |
|----------|----------------|-------------|-----------|
| Progression-Free Survival (PFS) | ★★★ | High | FDA-accepted, precedent in [trials] |
| Duration of Response (DoR) | ★★☆ | High | Standard in oncology |
| Overall Survival (OS) | ★★★ | Low (early phase) | Follow-up for long-term |
| [Biomarker response] | ★☆☆ | Medium | Exploratory, mechanistic |

## 5.3 Exploratory Endpoints
- Pharmacodynamic biomarkers (proof-of-mechanism)
- ctDNA clearance (liquid biopsy)
- Quality of life (PRO-CTCAE)
- Correlative science (tumor profiling)

## 5.4 Endpoint Risks & Mitigation
- Risk: [Low response rate → sample size inflation]
- Mitigation: [Adaptive design, interim analysis]
```

### 6. Comparator Analysis
```markdown
## 6.1 Standard of Care
**Current SOC**: [Drug name(s)]
- FDA approval: [Year] [★★★: FDA_OrangeBook]
- Efficacy: [ORR/PFS from pivotal trial]
- Limitations: [Resistance, toxicity, access]

**SOC Comparator Feasibility**: [HIGH/MEDIUM/LOW]

## 6.2 Trial Design Options
### Option A: Single-Arm vs. SOC
- **Design**: Phase 2, single-arm, N=[X]
- **Comparator**: Historical SOC data (ORR=[%])
- **Pros**: Faster enrollment, smaller N
- **Cons**: Selection bias, regulatory skepticism
- **Feasibility Score**: [0-100]

### Option B: Randomized vs. SOC
- **Design**: Phase 2, 1:1 randomization, N=[X] per arm
- **Comparator**: Active control ([SOC drug])
- **Pros**: Robust comparison, regulatory preferred
- **Cons**: 2x enrollment, comparator sourcing
- **Feasibility Score**: [0-100]

### Option C: Non-Inferiority Design
- **Rationale**: [If aiming for better safety with similar efficacy]
- **Non-inferiority margin**: [Δ = X%]
- **Sample size**: [N] (larger than superiority)

## 6.3 Comparator Drug Sourcing
- Commercial availability: [Yes/No]
- Patent status: [Generic available?]
- Cost: [$X per course]
- Stability and storage: [Requirements]
```

### 7. Safety Endpoints & Monitoring Plan
```markdown
## 7.1 Primary Safety Endpoint
**Dose-Limiting Toxicity (DLT)** [for Phase 1 component]:
- DLT definition: [Grade 3+ non-hematologic, Grade 4+ hematologic]
- DLT assessment period: [Cycle 1, 28 days]
- Dose escalation rule: [3+3, BOIN, mTPI]

## 7.2 Mechanism-Based Toxicities
**Drug Class**: [Kinase inhibitor, checkpoint inhibitor, etc.]

**Expected Toxicities** [★★★: FAERS, label data]:
| Toxicity | Incidence | Grade 3+ | Monitoring |
|----------|-----------|----------|------------|
| Diarrhea | 60% | 10% | Symptom diary, hydration |
| Rash | 40% | 5% | Dermatology consult PRN |
| Hepatotoxicity | 20% | 3% | LFTs weekly (cycle 1), then q3w |
| [Specific AE] | [%] | [%] | [Plan] |

**Data Source**: FAERS_search_reports (similar drugs), drugbank_get_pharmacology

## 7.3 Organ-Specific Monitoring
```markdown
### Hepatic
- Baseline: LFTs, hepatitis panel
- Monitoring: AST/ALT/bili weekly (cycle 1), then q3w
- Stopping rule: ALT >5× ULN or bili >3× ULN

### Cardiac
- Baseline: ECG, ECHO if anthracycline history
- Monitoring: ECG q cycle, ECHO if symptoms
- Stopping rule: QTcF >500 ms, LVEF drop >15%

### Renal
- Baseline: Cr, eGFR, urinalysis
- Monitoring: Cr/eGFR q cycle
- Stopping rule: CrCl <30 mL/min

### [Organ X]
- [Similar structure]
```

## 7.4 Safety Monitoring Committee (SMC)
- Composition: [3 independent experts: oncologist, toxicologist, biostatistician]
- Review frequency: [After every 6 patients, then quarterly]
- Stopping rules: [≥3 DLTs at dose level, ≥2 drug-related deaths]
```

### 8. Study Design Recommendations
```markdown
## 8.1 Recommended Design
**Phase**: [1/2, 1b/2, 2]
**Design Type**: [Single-arm, randomized, basket, umbrella]
**Primary Objective**: [Assess safety and preliminary efficacy]

**Schema**:
```
[Indication + Biomarker]
    ↓ Screening (Biomarker testing)
    ↓ Enrollment
    ├─ [Phase 1 dose escalation: 3+3 design, N=12-18]
    │   Dose Levels: [X mg, Y mg, Z mg QD]
    │   DLT assessment: Cycle 1 (28 days)
    └─ [Phase 2 expansion: Simon 2-stage, N=43]
        Stage 1: N=13 (≥2 responses to proceed)
        Stage 2: N=30 additional
        Target ORR: 30% (H0: 10%, α=0.05, β=0.20)
```

## 8.2 Eligibility Criteria
**Inclusion**:
- Age ≥18 years
- Histologically confirmed [disease]
- [Biomarker] positive (central lab confirmed)
- Measurable disease per RECIST 1.1
- ECOG PS 0-1
- Adequate organ function
- [≤1 prior line for advanced disease]

**Exclusion**:
- Brain metastases (unless treated and stable)
- Prior [drug class] therapy
- Active infection, immunodeficiency
- Pregnancy/nursing
- Significant cardiovascular disease

## 8.3 Treatment Plan
- **Dosing**: [X mg PO QD, 28-day cycles]
- **Dose modifications**: [20% reductions for Grade 2+]
- **Duration**: Until progression, toxicity, or 24 months
- **Concomitant meds**: Supportive care allowed, restrictions on CYP3A4 inhibitors

## 8.4 Assessment Schedule
| Assessment | Screening | Cycle 1 | Cycles 2-6 | Cycles 7+ | EOT |
|------------|-----------|---------|------------|-----------|-----|
| History & PE | X | X | X | X | X |
| ECOG PS | X | X | X | X | X |
| Labs (CBC, CMP, LFT) | X | Weekly | q3w | q3w | X |
| Tumor imaging | X | - | q6w | q9w | X |
| ECG | X | - | q3w (if abnormal) | - | X |
| Biomarker (ctDNA) | X | C1D15 | q6w | - | X |
| AE assessment | - | Continuous | Continuous | Continuous | X |
```

### 9. Enrollment & Site Strategy
```markdown
## 9.1 Site Selection Criteria
**Required Capabilities**:
- [Biomarker] testing (or central lab partnership)
- Phase 1/2 experience
- GCP compliance, IRB approval
- Access to [patient population]
- Investigator publications in [indication]

**Geographic Distribution**:
- US sites: [N] (target regions: [high-incidence areas])
- International: [Consider Asia if biomarker enriched there]

## 9.2 Enrollment Projections
**Assumptions**:
- Screening rate: [X patients/site/month]
- Screen failure rate: [30%] (biomarker negative, eligibility)
- Enrollment rate: [Y patients/site/month]

**Timeline** (N=[total]):
| Milestone | Month | Cumulative Enrolled |
|-----------|-------|---------------------|
| First site activated | 0 | 0 |
| First patient enrolled | 1 | 1 |
| 25% enrollment | [M1] | [0.25N] |
| 50% enrollment | [M2] | [0.5N] |
| 75% enrollment | [M3] | [0.75N] |
| Last patient enrolled | [M4] | [N] |
| Primary analysis | [M4 + follow-up] | - |

**Sites Required**: [Minimum M sites to achieve timeline]

## 9.3 Recruitment Strategies
- Physician outreach: Academic consortia, tumor boards
- Patient advocacy groups: [Organization names]
- ClinicalTrials.gov listing (prominent, lay summary)
- Social media: Targeted ads in [indication] communities
- Referral network: Community oncologists
```

### 10. Regulatory Pathway
```markdown
## 10.1 FDA Pathway Selection
**Recommended**: [505(b)(1) / 505(b)(2) / Breakthrough / Orphan]

**Rationale**:
- [505(b)(1)]: New molecular entity, full development program
- [505(b)(2)]: [If relying on published safety data for similar drugs]
- **Breakthrough Therapy**: [If preliminary evidence of substantial improvement on serious outcome]
  - Criteria: [X-fold ORR vs. SOC in early data]
  - Benefits: Rolling review, frequent FDA meetings
- **Orphan Designation**: [If prevalence <200,000 in US]
  - Eligible if: [Biomarker-defined subtype constitutes orphan population]
  - Benefits: 7-year exclusivity, tax credits, fee waivers

## 10.2 Regulatory Precedents
**Similar Approvals** [★★★]:
- [Drug A]: [Indication], [Year], [Endpoint used], [N=X], [ORR=Y%]
- [Drug B]: [Indication], [Year], [Accelerated approval → full]
- Source: FDA_get_approval_history, drug labels

**FDA Guidance Documents**:
- [Relevant guidance title] (Year)
- Key recommendations: [e.g., ORR acceptable for Phase 2, confirmatory trial needed]

## 10.3 Pre-IND Meeting
**Recommended Topics**:
1. Primary endpoint acceptability (ORR vs. PFS)
2. Biomarker test qualification (CDx plan)
3. Comparator arm (single-arm acceptable?)
4. Pediatric study plan waiver
5. Safety monitoring plan

**Timing**: [3-4 months before IND submission]

## 10.4 IND Timeline
| Milestone | Month | Deliverable |
|-----------|-------|-------------|
| Pre-IND meeting request | -4 | Briefing package |
| Pre-IND meeting | -3 | FDA feedback |
| IND submission | 0 | Complete IND package |
| FDA 30-day review | 1 | Clinical hold or proceed |
| First patient dosed | 1-2 | After IND clearance |
```

### 11. Budget & Resource Considerations
```markdown
## 11.1 Cost Drivers
| Item | Cost Estimate | Notes |
|------|---------------|-------|
| Protocol development | $50-100K | CRO or internal |
| IND preparation | $100-200K | CMC, toxicology reports |
| Site activation | $50K/site × [M sites] | IRB, contracts |
| Patient recruitment | $200-500K | Advertising, patient navigation |
| [Biomarker] testing | $[X]/patient | Central lab, CDx |
| Imaging (RECIST) | $3-5K/scan × [N scans] | CT, independent review |
| Drug supply | [Depends on sponsor] | If not sponsor-provided |
| CRO monitoring | $100-300/hour | Site visits, SDV |
| Data management | $150-300K | EDC, database lock |
| Statistical analysis | $50-100K | SAP, CSR |
| **TOTAL (Phase 1/2)** | **$[X-Y]M** | [N patients, M sites] |

## 11.2 Timeline & FTE Requirements
**Duration**: [X months] (enrollment) + [Y months] (follow-up)
**Team**:
- Medical monitor: 0.5 FTE
- Project manager: 0.8 FTE
- Clinical operations: 0.3 FTE
- Data manager: 0.3 FTE
- Biostatistician: 0.2 FTE
```

### 12. Risk Assessment
```markdown
## 12.1 Feasibility Risks (High Priority)
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Slow enrollment (biomarker screen fail) | HIGH | HIGH | - Expand sites to [high-prevalence regions]<br>- Allow alternative biomarkers<br>- Liquid biopsy screening |
| Low response rate (ORR <10%) | MEDIUM | CRITICAL | - Interim futility analysis (Simon stage 1)<br>- Lower null hypothesis if justified<br>- Pivot to combination if single-agent weak |
| Unexpected toxicity (>33% DLT rate) | LOW | CRITICAL | - Conservative starting dose (50% MTD from preclin)<br>- Dose escalation with BOIN (adaptive)<br>- Close SMC oversight |
| Comparator drug supply issues | MEDIUM | MEDIUM | - Secure commercial supply early<br>- Generic sourcing if available |
| Regulatory pushback on single-arm design | MEDIUM | HIGH | - Pre-IND meeting to align<br>- Plan for randomized Phase 2b if needed |

## 12.2 Scientific Risks
- Biomarker hypothesis unvalidated: [Correlative studies to de-risk]
- Patient heterogeneity: [Stratification by [factor]]
- Resistance mechanisms: [Serial biopsies for molecular profiling]
```

### 13. Success Criteria & Go/No-Go Decision
```markdown
## 13.1 Phase 1 Success Criteria (Go to Phase 2)
- [ ] ≤33% DLT rate at RP2D
- [ ] ≥50% patients achieve [PD biomarker response]
- [ ] No unexpected safety signals (Grade 5 AEs, new class effects)
- [ ] PK supports QD dosing

## 13.2 Phase 2 Interim Analysis (Simon Stage 1)
- **Enrollment**: 13 patients
- **Decision Rule**:
  - ≥2 responses (ORR ≥15%) → Proceed to Stage 2
  - <2 responses → Stop for futility

## 13.3 Phase 2 Final Success Criteria (Advance to Phase 3)
- [ ] ORR ≥30% (95% CI lower bound >10%)
- [ ] Median DoR ≥6 months
- [ ] PFS signal (HR <0.7 vs. historical SOC)
- [ ] Safety profile manageable (Grade ≥3 AE <40%)
- [ ] Biomarker correlation with response (enrichment signal)

## 13.4 Feasibility Scorecard
| Dimension | Weight | Score (0-10) | Weighted | Grade |
|-----------|--------|--------------|----------|-------|
| **Patient Availability** | 30% | [X] | [0.30×X] | [★★☆] |
| - Base population size | - | [X] | - | [Source] |
| - Biomarker prevalence | - | [X] | - | [ClinVar data] |
| - Site access | - | [X] | - | [N sites feasible] |
| **Endpoint Precedent** | 25% | [X] | [0.25×X] | [★★★] |
| - Regulatory acceptance | - | [X] | - | [FDA approvals using ORR] |
| - Measurement feasibility | - | [X] | - | [RECIST standard] |
| **Regulatory Clarity** | 20% | [X] | [0.20×X] | [★★☆] |
| - Pathway defined | - | [X] | - | [Breakthrough potential] |
| - Precedent approvals | - | [X] | - | [Similar indications] |
| **Comparator Feasibility** | 15% | [X] | [0.15×X] | [★★★] |
| - SOC availability | - | [X] | - | [FDA-approved, generic] |
| - Historical data | - | [X] | - | [Published ORR: X%] |
| **Safety Monitoring** | 10% | [X] | [0.10×X] | [★★☆] |
| - Known toxicities | - | [X] | - | [FAERS, class effects] |
| - Monitoring plan | - | [X] | - | [Defined, feasible] |
| **TOTAL FEASIBILITY SCORE** | **100%** | - | **[XX/100]** | - |

**Interpretation**:
- **≥75**: HIGH feasibility - Recommend proceed to protocol development
- **50-74**: MODERATE feasibility - Additional validation recommended
- **<50**: LOW feasibility - Significant de-risking required
```

### 14. Recommendations & Next Steps
```markdown
## 14.1 Final Recommendation
**GO / CONDITIONAL GO / NO-GO**: [Decision]

**Rationale**:
[2-3 paragraphs synthesizing feasibility analysis. Example:]

This trial demonstrates HIGH feasibility (score: 82/100) for the following reasons:
1. **Patient availability is strong** (★★★): EGFR+ NSCLC affects ~18,000 US patients/year,
   with L858R representing 45% (8,100 patients). With 20 sites, enrollment of N=43 is
   achievable in 8-10 months.
2. **Endpoint precedent is robust** (★★★): ORR is FDA-accepted for accelerated approval
   in NSCLC (18 precedents since 2015). RECIST 1.1 is standard, feasible.
3. **Regulatory pathway is clear** (★★☆): 505(b)(1) with breakthrough therapy potential
   given 2x ORR improvement vs. SOC. Pre-IND meeting advised to confirm single-arm design.

**Key Risk**: Enrollment may slow if sites lack rapid EGFR testing. Mitigation: Central
liquid biopsy with 7-day turnaround.

## 14.2 Critical Path to IND
**Immediate Next Steps** (Months 0-3):
- [ ] Request pre-IND meeting with FDA (target Month 1)
- [ ] Initiate CDx partnership for [biomarker] test (FDA clearance path)
- [ ] Secure drug supply (GMP manufacturing, stability)
- [ ] Draft protocol (v1.0) and ICF
- [ ] Site feasibility surveys (target [M] sites)

**IND Preparation** (Months 3-6):
- [ ] Complete CMC section (drug substance/product, manufacturing)
- [ ] Finalize preclinical package (toxicology, pharmacology)
- [ ] Prepare clinical protocol (incorporate FDA feedback)
- [ ] Develop CRFs and EDC database
- [ ] IND submission (Month 6)

**Post-IND** (Months 6-9):
- [ ] IRB submissions (central IRB for multi-site)
- [ ] Site contracts and budgets
- [ ] Investigator meeting
- [ ] First patient enrolled (Month 7-8)

## 14.3 Alternative Designs (If Current Design Infeasible)
**Plan B**: [If enrollment too slow]
- Broaden biomarker criteria (e.g., all EGFR mutations, not just L858R)
- Add international sites (Asia, EU)
- Basket design (multiple cancers with EGFR mutations)

**Plan C**: [If single-arm rejected by FDA]
- Randomized Phase 2 (1:1 vs. SOC)
- Increase sample size to N=86 (43/arm)
- Requires 2x sites and budget

## 14.4 Long-Term Development Strategy
**If Phase 2 Successful**:
- Phase 3 design: Randomized, OS primary endpoint, N=300-500
- Companion diagnostic (CDx): Parallel FDA submission
- Commercial readiness: Manufacturing scale-up
- Patent strategy: File composition-of-matter or method-of-use

**Market Considerations**:
- Addressable market: [8,100 EGFR L858R NSCLC patients/year in US]
- Competitive landscape: [Osimertinib, other EGFR TKIs]
- Differentiation: [e.g., Activity against T790M resistance]
- Pricing: [$10-15K/month based on comparators]
```

---

## Complete Example Workflow

### Example: EGFR L858R+ NSCLC Phase 1/2 Trial

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse(use_cache=True)
tu.load_tools()

# ============================================================================
# PATH 1: PATIENT POPULATION SIZING
# ============================================================================

# Step 1.1: Get disease prevalence
disease_info = tu.tools.OpenTargets_get_disease_id_description_by_name(
    diseaseName="non-small cell lung cancer"
)
efo_id = disease_info['data']['id']

# Get phenotype data (includes prevalence if available)
phenotypes = tu.tools.OpenTargets_get_diseases_phenotypes(
    efoId=efo_id
)
# Note: May need to supplement with literature (PubMed) for specific prevalence

# Step 1.2: Estimate EGFR mutation prevalence
egfr_variants = tu.tools.ClinVar_search_variants(
    gene="EGFR",
    significance="pathogenic,likely_pathogenic"
)

# Filter to L858R specifically
l858r_variants = [v for v in egfr_variants['data']
                  if 'L858R' in v.get('name', '')]

# Also check population databases for allele frequency
gnomad_egfr = tu.tools.gnomAD_search_gene_variants(
    gene="EGFR"
)
# Filter to L858R and sum allele frequencies

# Step 1.3: Search literature for epidemiology
epi_papers = tu.tools.PubMed_search_articles(
    query="EGFR L858R prevalence non-small cell lung cancer epidemiology",
    max_results=20
)
# Extract prevalence estimates from recent papers

# ============================================================================
# PATH 2: BIOMARKER PREVALENCE & TESTING
# ============================================================================

# Step 2.1: Find FDA-approved CDx tests
# Search FDA device database (via PubMed or manual lookup)
cdx_search = tu.tools.PubMed_search_articles(
    query="FDA approved companion diagnostic EGFR L858R",
    max_results=10
)

# Step 2.2: Literature on EGFR testing in clinical practice
testing_papers = tu.tools.PubMed_search_articles(
    query="EGFR mutation testing guidelines NCCN turnaround time",
    max_results=15
)

# ============================================================================
# PATH 3: COMPARATOR SELECTION
# ============================================================================

# Step 3.1: Find current standard of care (osimertinib)
soc_drug = "osimertinib"

soc_info = tu.tools.drugbank_get_drug_basic_info_by_drug_name_or_id(
    drug_name_or_drugbank_id=soc_drug
)

soc_indications = tu.tools.drugbank_get_indications_by_drug_name_or_drugbank_id(
    drug_name_or_drugbank_id=soc_drug
)

soc_pharmacology = tu.tools.drugbank_get_pharmacology_by_drug_name_or_drugbank_id(
    drug_name_or_drugbank_id=soc_drug
)

# Step 3.2: Check FDA Orange Book for approved generics
orange_book = tu.tools.FDA_OrangeBook_search_drugs(
    ingredient=soc_drug
)

# Step 3.3: Find FDA approval details
fda_approval = tu.tools.FDA_get_drug_approval_history(
    drug_name=soc_drug
)

# ============================================================================
# PATH 4: ENDPOINT SELECTION
# ============================================================================

# Step 4.1: Search for precedent Phase 2 trials in EGFR+ NSCLC
precedent_trials = tu.tools.search_clinical_trials(
    condition="EGFR positive non-small cell lung cancer",
    phase="2",
    status="completed"
)

# Analyze which primary endpoints were used (ORR, PFS, etc.)
orr_trials = [t for t in precedent_trials['data']
              if 'response rate' in t.get('primary_outcome', '').lower()]

# Step 4.2: Find FDA approvals using ORR as primary endpoint
orr_approvals = tu.tools.PubMed_search_articles(
    query="FDA approval objective response rate NSCLC accelerated approval",
    max_results=30
)

# Step 4.3: Get detailed trial results for sample size justification
# Use ClinicalTrials.gov NCT number from precedent_trials
for trial in precedent_trials['data'][:5]:
    nct_id = trial.get('nct_number')
    trial_details = tu.tools.search_clinical_trials(
        nct_id=nct_id
    )
    # Extract: ORR, n, confidence intervals

# ============================================================================
# PATH 5: SAFETY ENDPOINTS & MONITORING
# ============================================================================

# Step 5.1: Get mechanism-based toxicity from drug class
# If testing an EGFR inhibitor, search for class effects
class_drug = "erlotinib"  # Example EGFR TKI for class effect reference

class_safety = tu.tools.drugbank_get_pharmacology_by_drug_name_or_drugbank_id(
    drug_name_or_drugbank_id=class_drug
)

class_warnings = tu.tools.FDA_get_warnings_and_cautions_by_drug_name(
    drug_name=class_drug
)

# Step 5.2: FAERS data for real-world adverse events
faers_egfr_tki = tu.tools.FAERS_search_reports_by_drug_and_reaction(
    drug_name="erlotinib",
    limit=500
)

# Summarize top adverse events
ae_summary = tu.tools.FAERS_count_reactions_by_drug_event(
    medicinalproduct="ERLOTINIB"
)

# Step 5.3: Search for DLT definitions in similar trials
dlt_papers = tu.tools.PubMed_search_articles(
    query="dose limiting toxicity Phase 1 EGFR inhibitor definition",
    max_results=20
)

# ============================================================================
# PATH 6: REGULATORY PATHWAY
# ============================================================================

# Step 6.1: Search for breakthrough therapy designations in NSCLC
breakthrough_search = tu.tools.PubMed_search_articles(
    query="FDA breakthrough therapy designation NSCLC EGFR mutation",
    max_results=20
)

# Step 6.2: Check if indication qualifies for orphan drug status
# L858R is subset of NSCLC; estimate US prevalence
us_nsclc_annual = 200000  # From epidemiology data
l858r_prevalence = 0.45 * 0.15  # 45% of EGFR+ (15% of NSCLC)
l858r_annual_us = us_nsclc_annual * l858r_prevalence  # ~13,500/year
# Note: Orphan requires <200,000 total prevalence; may not qualify if prevalent

# Step 6.3: Find relevant FDA guidance documents
fda_guidance_search = tu.tools.PubMed_search_articles(
    query="FDA guidance clinical trial endpoints oncology non-small cell lung cancer",
    max_results=15
)

# ============================================================================
# COMPILE FEASIBILITY REPORT
# ============================================================================

# Now compile all data into the 14-section report structure
# Calculate feasibility score based on findings

feasibility_scores = {
    'patient_availability': 8,  # 8/10 based on 13,500 patients/year, good access
    'endpoint_precedent': 9,    # 9/10 ORR widely accepted
    'regulatory_clarity': 7,    # 7/10 breakthrough possible, single-arm needs FDA input
    'comparator_feasibility': 9, # 9/10 osimertinib available, efficacy data clear
    'safety_monitoring': 8      # 8/10 EGFR TKI class effects well-characterized
}

weights = {
    'patient_availability': 0.30,
    'endpoint_precedent': 0.25,
    'regulatory_clarity': 0.20,
    'comparator_feasibility': 0.15,
    'safety_monitoring': 0.10
}

overall_score = sum(feasibility_scores[k] * weights[k] * 10 for k in weights.keys())
# overall_score = 81/100 → HIGH feasibility

print(f"Feasibility Score: {overall_score}/100 - HIGH")
print("Recommendation: RECOMMEND PROCEED to protocol development")
```

---

## Tool Reference by Research Path

### PATH 1: Patient Population Sizing
- `OpenTargets_get_disease_id_description_by_name` - Disease lookup
- `OpenTargets_get_diseases_phenotypes` - Prevalence data
- `ClinVar_search_variants` - Biomarker mutation frequency
- `gnomAD_search_gene_variants` - Population allele frequencies
- `PubMed_search_articles` - Epidemiology literature
- `search_clinical_trials` - Enrollment feasibility from past trials

### PATH 2: Biomarker Prevalence & Testing
- `ClinVar_get_variant_details` - Variant pathogenicity
- `COSMIC_search_mutations` - Cancer-specific mutation frequencies
- `gnomAD_get_variant_details` - Population genetics
- `PubMed_search_articles` - CDx test performance, guidelines

### PATH 3: Comparator Selection
- `drugbank_get_drug_basic_info_by_drug_name_or_id` - Drug info
- `drugbank_get_indications_by_drug_name_or_drugbank_id` - Approved indications
- `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` - Mechanism
- `FDA_OrangeBook_search_drugs` - Generic availability
- `FDA_get_drug_approval_history` - Approval details
- `search_clinical_trials` - Historical control data

### PATH 4: Endpoint Selection
- `search_clinical_trials` - Precedent trials, endpoints used
- `PubMed_search_articles` - FDA acceptance history, endpoint validation
- `FDA_get_drug_approval_history` - Approved endpoints by indication

### PATH 5: Safety Endpoints & Monitoring
- `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` - Mechanism toxicity
- `FDA_get_warnings_and_cautions_by_drug_name` - FDA black box warnings
- `FAERS_search_reports_by_drug_and_reaction` - Real-world adverse events
- `FAERS_count_reactions_by_drug_event` - AE frequency
- `FAERS_count_death_related_by_drug` - Serious outcomes
- `PubMed_search_articles` - DLT definitions, monitoring strategies

### PATH 6: Regulatory Pathway
- `FDA_get_drug_approval_history` - Precedent approvals
- `PubMed_search_articles` - Breakthrough designations, FDA guidance
- `search_clinical_trials` - Regulatory precedents (accelerated approval)

---

## Best Practices

### 1. Start with Report Template
Create full report structure FIRST, then populate:
```markdown
# Clinical Trial Feasibility Report: [INDICATION]
## 1. Executive Summary
[Researching...]
## 2. Disease Background
[Researching...]
[...all 14 sections...]
```

### 2. Use English for All Tool Calls
Even if user asks in another language:
- "EGFR+ NSCLC" not "EGFR+ 非小细胞肺癌"
- "breast cancer" not "cancer du sein"
- Translate results back to user's language

### 3. Validate Biomarker Prevalence Across Sources
Cross-check ClinVar, gnomAD, COSMIC, and literature:
- ClinVar: Clinical significance
- gnomAD: Population frequency (for germline)
- COSMIC: Somatic mutation frequency in cancers
- Literature: Geographic/ethnic variation

### 4. Calculate Enrollment Funnel Explicitly
Show math for patient availability:
```
US NSCLC incidence: 200,000/year
× EGFR+ prevalence: 15% = 30,000
× L858R within EGFR+: 45% = 13,500
× Eligible (age, PS, prior Tx): 60% = 8,100
÷ Competing trials: 3 = 2,700 available/year

For N=43, need 43/2,700 = 1.6% capture rate → Achievable
```

### 5. Evidence Grade Every Key Claim
```markdown
EGFR L858R prevalence is 45% of EGFR+ NSCLC [★★★: PMID:12345, large
sequencing study n=1,500]. *Source: ClinVar, COSMIC*
```

### 6. Provide Regulatory Precedent Details
Not just "ORR is accepted" but:
```markdown
ORR is FDA-accepted for accelerated approval in NSCLC [★★★: FDA approvals]:
- Osimertinib (2015): ORR 57%, n=411, Tx-resistant EGFR+ (NCT01802632)
- Dacomitinib (2018): ORR 45%, n=452, 1L EGFR+ (NCT01774721)
- [3 more examples]
```

### 7. Address Feasibility Risks Proactively
For each HIGH risk, provide mitigation:
```markdown
Risk: Biomarker screen failure rate >70%
→ Mitigation: Liquid biopsy pre-screening (ctDNA EGFR, 7-day turnaround)
```

### 8. Separate Phase 1 and Phase 2 Components
If combined Phase 1/2:
- Phase 1: Safety, DLT, RP2D (N=12-18, 3+3 or BOIN)
- Phase 2: Efficacy, ORR (N=43, Simon 2-stage)
- Distinct success criteria for each phase

---

## Common Pitfalls to Avoid

### ❌ Don't: Show Tool Outputs to User
```markdown
# BAD
OpenTargets returned:
{
  "data": {
    "id": "EFO_0003060",
    "name": "non-small cell lung carcinoma"
  }
}
```

### ✅ Do: Present Synthesized Report
```markdown
# GOOD
## Disease Background
Non-small cell lung cancer (NSCLC) represents 85% of lung cancers, with
~200,000 new cases annually in the US [★★★: CDC WONDER]. EGFR mutations
occur in 15% of Caucasian and 50% of Asian patients [★★★: PMID:23816960].
*Source: OpenTargets, ClinVar*
```

### ❌ Don't: Make Unsupported Claims
```markdown
# BAD
ORR of 60% is expected based on preclinical data.
```

### ✅ Do: Ground in Evidence
```markdown
# GOOD
ORR of 30-40% is projected [★★☆] based on:
- Similar EGFR TKI (erlotinib): 32% ORR in EGFR+ NSCLC (NCT00949650)
- Our drug's 2× IC50 potency vs. erlotinib (preclinical)
*Source: ClinicalTrials.gov, internal data*
```

### ❌ Don't: Ignore Geographic Variation
```markdown
# BAD
EGFR L858R prevalence: 7% of NSCLC
```

### ✅ Do: Specify Geography
```markdown
# GOOD
EGFR L858R prevalence [★★★: COSMIC, ClinVar]:
- Caucasian (US/EU): 6-7% of NSCLC
- East Asian: 20-25% of NSCLC
→ Trial site strategy: Include Asian sites for 2× enrollment
```

---

## Output Format Requirements

### Report File Naming
- `[INDICATION]_trial_feasibility_report.md`
- Example: `EGFR_L858R_NSCLC_trial_feasibility_report.md`

### Section Completeness
All 14 sections MUST be present:
1. Executive Summary
2. Disease Background
3. Patient Population Analysis (with funnel)
4. Biomarker Strategy
5. Endpoint Selection & Justification
6. Comparator Analysis
7. Safety Endpoints & Monitoring Plan
8. Study Design Recommendations
9. Enrollment & Site Strategy
10. Regulatory Pathway
11. Budget & Resource Considerations
12. Risk Assessment
13. Success Criteria & Go/No-Go Decision (with scorecard)
14. Recommendations & Next Steps

### Evidence Grading Required In
- Section 1 (Executive Summary): Key findings
- Section 4 (Biomarker): Prevalence claims
- Section 5 (Endpoints): Regulatory precedents
- Section 6 (Comparator): SOC efficacy data
- Section 7 (Safety): Toxicity frequencies
- Section 10 (Regulatory): Approval precedents
- Section 13 (Scorecard): All dimensions

### Feasibility Score Transparency
Show calculation:
```markdown
| Dimension | Weight | Raw Score | Weighted | Evidence |
|-----------|--------|-----------|----------|----------|
| Patient Availability | 30% | 8/10 | 24 | ★★★: Epi data |
| Endpoint Precedent | 25% | 9/10 | 22.5 | ★★★: FDA approvals |
| Regulatory Clarity | 20% | 7/10 | 14 | ★★☆: Pre-IND advised |
| Comparator Feasibility | 15% | 9/10 | 13.5 | ★★★: Generic avail |
| Safety Monitoring | 10% | 8/10 | 8 | ★★☆: Class effects |
| **TOTAL** | **100%** | - | **82/100** | **HIGH** |
```

---

## Example Use Cases

### Use Case 1: Biomarker-Selected Oncology Trial
**Query**: "Assess feasibility of Phase 2 trial for EGFR L858R+ NSCLC, ORR primary endpoint"

**Workflow**:
1. Disease prevalence: 200K NSCLC/year × 15% EGFR+ = 30K
2. Biomarker: L858R is 45% of EGFR+ → 13.5K/year
3. Eligible: 60% → 8K/year
4. Endpoint: ORR accepted (osimertinib precedent)
5. Comparator: Osimertinib (ORR 57%, generic available)
6. Feasibility: HIGH (82/100) → RECOMMEND PROCEED

### Use Case 2: Rare Disease Trial
**Query**: "Feasibility of trial in Niemann-Pick Type C (prevalence 1:120,000)"

**Workflow**:
1. US prevalence: ~2,750 patients total, ~25 new cases/year
2. Endpoint challenge: No validated clinical outcome
3. Orphan drug: QUALIFIED (7-year exclusivity)
4. Comparator: No approved drugs → single-arm feasible
5. Enrollment: Multi-year, need ALL US centers
6. Feasibility: MODERATE (58/100) → CONDITIONAL GO (requires patient registry partnership)

### Use Case 3: Superiority Trial vs. Standard of Care
**Query**: "Phase 2b design for new checkpoint inhibitor vs. pembrolizumab in PD-L1 high NSCLC"

**Workflow**:
1. Patient availability: 40K PD-L1 high NSCLC/year (HIGH)
2. Endpoint: ORR for Phase 2b, plan OS for Phase 3
3. Comparator: Pembrolizumab (ORR 45%, PFS 10mo) - readily available
4. Design: Randomized 1:1, N=120 (60/arm) for 20% ORR improvement
5. Feasibility: HIGH (78/100) → RECOMMEND PROCEED

### Use Case 4: Non-Inferiority Trial
**Query**: "Non-inferiority trial for oral anticoagulant vs. warfarin"

**Workflow**:
1. Patient availability: 2M AFib patients, 600K on warfarin (HIGH)
2. Endpoint: Stroke/SE (FDA-accepted, but requires large N)
3. Non-inferiority margin: HR <1.5 (FDA guidance)
4. Sample size: N=5,000+ for 90% power → LARGE trial
5. Comparator: Warfarin generic, INR monitoring standard
6. Feasibility: MODERATE (65/100) - large N drives cost and timeline

### Use Case 5: Basket Trial (Multiple Cancers, One Biomarker)
**Query**: "Basket trial for NTRK fusion+ solid tumors (15 histologies)"

**Workflow**:
1. Patient availability: NTRK fusions rare (<1% across cancers) → Broad screening
2. Biomarker testing: NGS required (FDA-approved FoundationOne CDx)
3. Endpoint: ORR (precedent: larotrectinib approval, ORR 75%, n=55)
4. Design: Single-arm, N=15-20 per histology × 5-10 histologies
5. Regulatory: Tissue-agnostic approval precedent (★★★: pembrolizumab MSI-H)
6. Feasibility: MODERATE (62/100) - enrollment slow but feasible with broad screening

---

## Integration with Other Skills

### Works Well With
- **tooluniverse-drug-research**: Investigate mechanism, preclinical data
- **tooluniverse-disease-research**: Deep dive on disease biology
- **tooluniverse-target-research**: Validate drug target, essentiality
- **tooluniverse-pharmacovigilance**: Post-market safety for comparator drugs
- **tooluniverse-precision-oncology**: Biomarker biology, resistance mechanisms

### Complementary Analyses
After feasibility report, consider:
1. **Budget model**: Use cost estimates to build financial model
2. **Site feasibility surveys**: Validate enrollment projections with sites
3. **Regulatory strategy document**: Detailed FDA interaction plan
4. **Statistical analysis plan (SAP)**: Translate design into statistical methods

---

## Version Information

- **Version**: 1.0.0
- **Last Updated**: February 2026
- **Compatible with**: ToolUniverse 0.5+
- **Focus**: Phase 1/2 early clinical development

---

## Support & Resources

- **ToolUniverse Docs**: https://zitniklab.hms.harvard.edu/ToolUniverse/
- **FDA Guidance Documents**: https://www.fda.gov/regulatory-information/search-fda-guidance-documents
- **ClinicalTrials.gov**: https://clinicaltrials.gov/
- **Slack Community**: https://join.slack.com/t/tooluniversehq/shared_invite/zt-3dic3eoio-5xxoJch7TLNibNQn5_AREQ
