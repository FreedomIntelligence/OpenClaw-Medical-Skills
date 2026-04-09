# tooluniverse-chemical-safety

> Comprehensive chemical safety and toxicology assessment integrating ADMET-AI predictions, CTD toxicogenomics, FDA label safety data, DrugBank safety profiles, and STITCH chemical-protein interactions. Performs predictive toxicology (AMES, DILI, LD50, carcinogenicity), organ/system toxicity profiling, chemical-gene-disease relationship mapping, regulatory safety extraction, and environmental hazard assessment. Use when asked about chemical toxicity, drug safety profiling, ADMET properties, environmental health risks, chemical hazard assessment, or toxicogenomic analysis.

# Chemical Safety & Toxicology Assessment

Comprehensive chemical safety and toxicology analysis integrating predictive AI models, curated toxicogenomics databases, regulatory safety data, and chemical-biological interaction networks. Generates structured risk assessment reports with evidence grading.

## When to Use This Skill

**Triggers**:
- "Is this chemical toxic?" / "What are the toxicity endpoints for [compound]?"
- "Assess the safety profile of [drug/chemical]"
- "What are the ADMET properties of [SMILES]?"
- "What genes does [chemical] interact with?"
- "What diseases are linked to [chemical] exposure?"
- "Predict toxicity for these molecules"
- "Drug safety assessment for [drug name]"
- "Environmental health risk of [chemical]"
- "Chemical hazard profiling"
- "Toxicogenomic analysis of [compound]"

**Use Cases**:
1. **Predictive Toxicology**: AI-predicted toxicity endpoints (AMES mutagenicity, DILI, LD50, carcinogenicity, skin reactions) for novel compounds via SMILES
2. **ADMET Profiling**: Full absorption, distribution, metabolism, excretion, toxicity characterization
3. **Toxicogenomics**: Chemical-gene interaction mapping, gene-disease associations from CTD
4. **Regulatory Safety**: FDA label warnings, boxed warnings, contraindications, adverse reactions
5. **Drug Safety Assessment**: Combined DrugBank safety + FDA labels + adverse event data
6. **Chemical-Protein Interactions**: STITCH-based chemical-protein binding and interaction networks
7. **Environmental Toxicology**: Chemical-disease associations for environmental contaminants

---

## KEY PRINCIPLES

1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Tool parameter verification** - Verify params via `get_tool_info` before calling unfamiliar tools
3. **Evidence grading** - Grade all safety claims by evidence strength (T1-T4)
4. **Citation requirements** - Every toxicity finding must have inline source attribution
5. **Mandatory completeness** - All sections must exist with data minimums or explicit "No data" notes
6. **Disambiguation first** - Resolve compound identity (name -> SMILES, CID, ChEMBL ID) before analysis
7. **Negative results documented** - "No toxicity signals found" is data; empty sections are failures
8. **Conservative risk assessment** - When evidence is ambiguous, flag as "requires further investigation"
9. **English-first queries** - Always use English chemical/drug names in tool calls

---

## Evidence Grading System (MANDATORY)

Grade every toxicity claim by evidence strength:

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|----------|
| **T1** | [T1] | Direct human evidence, regulatory finding | FDA boxed warning, clinical trial toxicity, human case reports |
| **T2** | [T2] | Animal studies, validated in vitro | Nonclinical toxicology, AMES positive, animal LD50 |
| **T3** | [T3] | Computational prediction, association data | ADMET-AI prediction, CTD association, QSAR model |
| **T4** | [T4] | Database annotation, text-mined | Literature mention, database entry without validation |

### Required Evidence Grading Locations

Evidence grades MUST appear in:
1. **Executive Summary** - Key toxicity findings graded
2. **Toxicity Predictions** - Every ADMET-AI endpoint with confidence note
3. **Regulatory Safety** - FDA findings marked [T1]
4. **Chemical-Gene Interactions** - CTD data marked by curation status
5. **Risk Assessment** - Final risk classification with supporting evidence tiers

---

## Core Strategy: 8 Research Dimensions

```
Chemical/Drug Query
|
+-- PHASE 0: Compound Disambiguation (ALWAYS FIRST)
|   +-- Resolve name -> SMILES, PubChem CID, ChEMBL ID
|   +-- Get molecular formula, weight, canonical structure
|
+-- PHASE 1: Predictive Toxicology (ADMET-AI)
|   +-- Mutagenicity (AMES)
|   +-- Hepatotoxicity (DILI, ClinTox)
|   +-- Carcinogenicity
|   +-- Acute toxicity (LD50)
|   +-- Skin reactions
|   +-- Stress response pathways
|   +-- Nuclear receptor activity
|
+-- PHASE 2: ADMET Properties
|   +-- Absorption: BBB penetrance, bioavailability
|   +-- Distribution: clearance, volume of distribution
|   +-- Metabolism: CYP interactions (1A2, 2C9, 2C19, 2D6, 3A4)
|   +-- Physicochemical: solubility, lipophilicity, pKa
|
+-- PHASE 3: Toxicogenomics (CTD)
|   +-- Chemical-gene interactions
|   +-- Chemical-disease associations
|   +-- Affected biological pathways
|
+-- PHASE 4: Regulatory Safety (FDA Labels)
|   +-- Boxed warnings (Black Box)
|   +-- Contraindications
|   +-- Adverse reactions
|   +-- Warnings and precautions
|   +-- Nonclinical toxicology
|
+-- PHASE 5: Drug Safety Profile (DrugBank)
|   +-- Toxicity data
|   +-- Contraindications
|   +-- Drug interactions affecting safety
|
+-- PHASE 6: Chemical-Protein Interactions (STITCH)
|   +-- Direct chemical-protein binding
|   +-- Interaction confidence scores
|   +-- Off-target effects
|
+-- PHASE 7: Structural Alerts (ChEMBL)
|   +-- Known toxic substructures (PAINS, Brenk)
|   +-- Structural alert flags
|
+-- SYNTHESIS: Integrated Risk Assessment
    +-- Aggregate all evidence tiers
    +-- Risk classification (Low/Medium/High/Critical)
    +-- Data gaps and recommendations
```

---

## Phase 0: Compound Disambiguation (ALWAYS FIRST)

**CRITICAL**: Resolve compound identity before any analysis.

### Input Types Handled

| Input Format | Resolution Strategy |
|-------------|---------------------|
| Drug name (e.g., "Aspirin") | PubChem_get_CID_by_compound_name -> get SMILES from properties |
| SMILES string | Use directly for ADMET-AI; resolve to CID for other tools |
| PubChem CID | PubChem_get_compound_properties_by_CID -> get SMILES + name |
| ChEMBL ID | ChEMBL_get_molecule -> get SMILES + properties |

### Resolution Steps

1. **Input detection**: Determine if input is name, SMILES, CID, or ChEMBL ID
   - SMILES: contains typical SMILES characters (=, #, [, ], (, ), c, n, o and no spaces in middle)
   - CID: numeric only
   - ChEMBL: starts with "CHEMBL"
   - Otherwise: treat as compound name
2. **Name to CID**: `PubChem_get_CID_by_compound_name(name=<compound_name>)`
3. **CID to properties**: `PubChem_get_compound_properties_by_CID(cid=<cid>)`
4. **Extract SMILES**: Get SMILES from PubChem properties (field: `ConnectivitySMILES`, `CanonicalSMILES`, or `IsomericSMILES` depending on response format)
5. **Store resolved IDs**: Maintain dict with `name`, `smiles`, `cid`, `formula`, `weight`, `inchi`

### Disambiguation Output

```markdown
## Compound Identity

| Property | Value |
|----------|-------|
| **Name** | Acetaminophen |
| **PubChem CID** | 1983 |
| **SMILES** | CC(=O)Nc1ccc(O)cc1 |
| **Formula** | C8H9NO2 |
| **Molecular Weight** | 151.16 |
| **InChI** | InChI=1S/C8H9NO2/... |
```

---

## Phase 1: Predictive Toxicology (ADMET-AI)

**When**: SMILES is available (from Phase 0 or provided directly)

**Objective**: Run comprehensive AI-predicted toxicity endpoints

### Tools Used

All ADMET-AI tools take the same parameter format:

| Tool | Predicted Endpoints | Parameter |
|------|---------------------|-----------|
| `ADMETAI_predict_toxicity` | AMES, Carcinogens_Lagunin, ClinTox, DILI, LD50_Zhu, Skin_Reaction, hERG | `smiles`: list[str] |
| `ADMETAI_predict_stress_response` | Stress response pathway activation (ARE, ATAD5, HSE, MMP, p53) | `smiles`: list[str] |
| `ADMETAI_predict_nuclear_receptor_activity` | AhR, AR, ER, PPARg, Aromatase nuclear receptor activity | `smiles`: list[str] |

### Workflow

1. Call `ADMETAI_predict_toxicity(smiles=[resolved_smiles])`
2. Call `ADMETAI_predict_stress_response(smiles=[resolved_smiles])`
3. Call `ADMETAI_predict_nuclear_receptor_activity(smiles=[resolved_smiles])`
4. For each endpoint, interpret prediction:
   - Classification endpoints: Active (1) = toxic signal, Inactive (0) = no signal
   - Regression endpoints (LD50): Report numerical value with context
   - All predictions graded [T3] (computational prediction)

### Decision Logic

- **Multiple SMILES**: Can batch up to ~10 SMILES in single call
- **Failed prediction**: If ADMET-AI fails, note "prediction unavailable" (don't fail entire report)
- **Confidence**: Note that AI predictions are [T3] evidence, not definitive
- **hERG flag**: If hERG = Active, flag prominently (cardiac safety risk)
- **AMES flag**: If AMES = Active, flag prominently (mutagenicity concern)
- **DILI flag**: If DILI = Active, flag prominently (liver toxicity concern)

### Output Table

```markdown
### Toxicity Predictions [T3]

| Endpoint | Prediction | Interpretation | Concern Level |
|----------|-----------|---------------|---------------|
| AMES Mutagenicity | Inactive | No mutagenic signal | Low |
| Carcinogenicity | Inactive | No carcinogenic signal | Low |
| ClinTox | Active | Clinical toxicity signal | HIGH |
| DILI | Active | Drug-induced liver injury risk | HIGH |
| LD50 (Zhu) | 2.45 log(mg/kg) | ~282 mg/kg (moderate) | Medium |
| Skin Reaction | Inactive | No skin sensitization signal | Low |
| hERG Inhibition | Active | Cardiac arrhythmia risk | HIGH |

*All predictions from ADMET-AI. Evidence tier: [T3] (computational prediction)*
```

---

## Phase 2: ADMET Properties

**When**: SMILES is available

**Objective**: Full ADMET characterization beyond toxicity

### Tools Used

| Tool | Properties Predicted | Parameter |
|------|---------------------|-----------|
| `ADMETAI_predict_BBB_penetrance` | Blood-brain barrier crossing probability | `smiles`: list[str] |
| `ADMETAI_predict_bioavailability` | Oral bioavailability (F20%, F30%) | `smiles`: list[str] |
| `ADMETAI_predict_clearance_distribution` | Clearance, VDss, half-life, PPB | `smiles`: list[str] |
| `ADMETAI_predict_CYP_interactions` | CYP1A2, 2C9, 2C19, 2D6, 3A4 inhibition/substrate | `smiles`: list[str] |
| `ADMETAI_predict_physicochemical_properties` | LogP, LogD, LogS, MW, pKa | `smiles`: list[str] |
| `ADMETAI_predict_solubility_lipophilicity_hydration` | Aqueous solubility, lipophilicity, hydration free energy | `smiles`: list[str] |

### Workflow

1. Call all 6 ADMET tools in parallel (independent calls)
2. Compile results into Absorption / Distribution / Metabolism / Excretion sections
3. Assess Lipinski Rule of 5 compliance from physicochemical properties
4. Flag drug-drug interaction risks from CYP inhibition profiles

### Decision Logic

- **BBB penetrant + toxicity**: If BBB = Yes and any CNS toxicity endpoint active, flag as neurotoxicity risk
- **Low bioavailability**: If F20% = Low, note absorption concerns
- **CYP inhibitor**: If CYP3A4 inhibitor = Yes, flag high DDI risk
- **Lipinski violations**: Count violations and report drug-likeness assessment

### Output Format

```markdown
### ADMET Profile [T3]

#### Absorption
| Property | Value | Interpretation |
|----------|-------|----------------|
| BBB Penetrance | Yes | Crosses blood-brain barrier |
| Bioavailability (F20%) | 85% | Good oral absorption |

#### Distribution
| Property | Value | Interpretation |
|----------|-------|----------------|
| VDss | 1.2 L/kg | Moderate tissue distribution |
| PPB | 92% | Highly protein bound |

#### Metabolism
| CYP Enzyme | Substrate | Inhibitor |
|------------|-----------|-----------|
| CYP1A2 | No | No |
| CYP2C9 | Yes | No |
| CYP2C19 | No | No |
| CYP2D6 | No | No |
| CYP3A4 | Yes | Yes (DDI risk) |

#### Excretion
| Property | Value | Interpretation |
|----------|-------|----------------|
| Clearance | 8.5 mL/min/kg | Moderate clearance |
| Half-life | 6.2 h | Moderate half-life |
```

---

## Phase 3: Toxicogenomics (CTD)

**When**: Compound name is resolved

**Objective**: Map chemical-gene-disease relationships from curated CTD data

### Tools Used

| Tool | Function | Parameter |
|------|----------|-----------|
| `CTD_get_chemical_gene_interactions` | Genes affected by chemical | `input_terms`: str (chemical name) |
| `CTD_get_chemical_diseases` | Diseases linked to chemical exposure | `input_terms`: str (chemical name) |

### Workflow

1. Call `CTD_get_chemical_gene_interactions(input_terms=compound_name)`
2. Call `CTD_get_chemical_diseases(input_terms=compound_name)`
3. Parse gene interactions: extract gene symbols, interaction types (increases/decreases expression, binding, etc.)
4. Parse disease associations: extract disease names, evidence types (marker/mechanism/therapeutic)
5. Identify most affected biological processes from gene list

### Decision Logic

- **Direct evidence vs inferred**: CTD separates curated direct evidence from inferred associations
- **Therapeutic vs toxic**: Disease associations can be therapeutic (drug treats disease) or adverse (chemical causes disease)
- **Gene interaction types**: Distinguish between expression changes, binding, and activity modulation
- **Prioritize marker/mechanism**: These indicate stronger causal evidence than simple associations
- **Grade curated as [T2]**: Direct curated CTD evidence from literature
- **Grade inferred as [T3]**: Computationally inferred associations

### Output Format

```markdown
### Toxicogenomics (CTD) [T2/T3]

#### Chemical-Gene Interactions (Top 20)
| Gene | Interaction | Type | Evidence |
|------|------------|------|----------|
| CYP1A2 | increases expression | mRNA | [T2] curated |
| TP53 | affects activity | protein | [T2] curated |
| ...  | ... | ... | ... |

**Total interactions found**: 156
**Top affected pathways**: Xenobiotic metabolism, Apoptosis, DNA damage response

#### Chemical-Disease Associations (Top 10)
| Disease | Association Type | Evidence |
|---------|-----------------|----------|
| Liver Neoplasms | marker/mechanism | [T2] curated |
| Contact Dermatitis | therapeutic | [T2] curated |
| ... | ... | ... |
```

---

## Phase 4: Regulatory Safety (FDA Labels)

**When**: Compound has an approved drug name

**Objective**: Extract regulatory safety information from FDA drug labels

### Tools Used

| Tool | Information Retrieved | Parameter |
|------|---------------------|-----------|
| `FDA_get_boxed_warning_info_by_drug_name` | Black box warnings (most serious) | `drug_name`: str |
| `FDA_get_contraindications_by_drug_name` | Absolute contraindications | `drug_name`: str |
| `FDA_get_adverse_reactions_by_drug_name` | Known adverse reactions | `drug_name`: str |
| `FDA_get_warnings_by_drug_name` | Warnings and precautions | `drug_name`: str |
| `FDA_get_nonclinical_toxicology_info_by_drug_name` | Animal toxicology data | `drug_name`: str |
| `FDA_get_carcinogenic_mutagenic_fertility_by_drug_name` | Carcinogenicity/mutagenicity/fertility data | `drug_name`: str |

### Workflow

1. Call all 6 FDA tools in parallel (independent queries by drug name)
2. Parse and structure each response
3. Prioritize: Boxed Warnings > Contraindications > Warnings > Adverse Reactions
4. All FDA label data is [T1] evidence (regulatory finding based on human/animal data)

### Decision Logic

- **Boxed warning present**: Flag as CRITICAL safety concern in executive summary
- **No FDA data**: Chemical may not be an approved drug; note "Not an FDA-approved drug" and continue with other phases
- **Multiple warnings**: Categorize by organ system (hepatic, cardiac, renal, CNS, etc.)
- **Nonclinical toxicology**: Grade as [T2] (animal data supporting human risk)

### Output Format

```markdown
### Regulatory Safety (FDA) [T1]

#### Boxed Warning
**PRESENT** - Hepatotoxicity risk with doses >4g/day. Liver failure reported. [T1]

#### Contraindications
- Severe hepatic impairment [T1]
- Known hypersensitivity [T1]

#### Adverse Reactions (by frequency)
| Reaction | Frequency | Severity |
|----------|-----------|----------|
| Nausea | Common (>1%) | Mild |
| Hepatotoxicity | Rare (<0.1%) | Severe |
| ... | ... | ... |

#### Nonclinical Toxicology [T2]
- **Carcinogenicity**: No carcinogenic potential in 2-year rat/mouse studies
- **Mutagenicity**: Negative in Ames assay and in vivo micronucleus test
- **Fertility**: No effects on fertility at doses up to 10x human dose
```

---

## Phase 5: Drug Safety Profile (DrugBank)

**When**: Compound is a known drug

**Objective**: Retrieve curated drug safety data from DrugBank

### Tools Used

| Tool | Information | Parameters |
|------|------------|------------|
| `drugbank_get_safety_by_drug_name_or_drugbank_id` | Toxicity, contraindications | `query`: str, `case_sensitive`: bool, `exact_match`: bool, `limit`: int |

### Workflow

1. Call `drugbank_get_safety_by_drug_name_or_drugbank_id(query=drug_name, case_sensitive=False, exact_match=False, limit=5)`
2. Parse toxicity information, overdose data, contraindications
3. Cross-reference with FDA data from Phase 4

### Decision Logic

- **Toxicity field**: Contains LD50 values, overdose symptoms, organ toxicity data
- **DrugBank ID**: Note if found for cross-referencing
- **Conflict with FDA**: If DrugBank and FDA disagree, note discrepancy and defer to FDA [T1]
- **Not found**: Chemical may not be in DrugBank; continue with other phases

---

## Phase 6: Chemical-Protein Interactions (STITCH)

**When**: Compound can be identified by name or SMILES

**Objective**: Map chemical-protein interaction network for off-target assessment

### Tools Used

| Tool | Function | Parameters |
|------|----------|------------|
| `STITCH_resolve_identifier` | Resolve chemical name to STITCH ID | `identifier`: str, `species`: int (9606=human) |
| `STITCH_get_chemical_protein_interactions` | Get chemical-protein interactions | `identifiers`: list[str], `species`: int, `required_score`: int |
| `STITCH_get_interaction_partners` | Get interaction network | `identifiers`: list[str], `species`: int, `limit`: int |

### Workflow

1. Resolve compound: `STITCH_resolve_identifier(identifier=compound_name, species=9606)`
2. Get interactions: `STITCH_get_chemical_protein_interactions(identifiers=[stitch_id], species=9606, required_score=700)`
3. Identify off-target proteins (not the intended drug target)
4. Flag safety-relevant targets: hERG (cardiac), CYP enzymes (metabolism), nuclear receptors (endocrine)

### Decision Logic

- **High confidence (>900)**: Well-established interaction [T2]
- **Medium confidence (700-900)**: Probable interaction [T3]
- **Low confidence (400-700)**: Possible interaction, needs validation [T4]
- **Safety-relevant targets**: Flag interactions with known safety targets
- **No STITCH data**: Chemical may be too novel; note and continue

---

## Phase 7: Structural Alerts (ChEMBL)

**When**: ChEMBL molecule ID is available (from Phase 0)

**Objective**: Check for known toxic substructures

### Tools Used

| Tool | Function | Parameters |
|------|----------|------------|
| `ChEMBL_search_compound_structural_alerts` | Find structural alert matches | `molecule_chembl_id`: str, `limit`: int |

### Workflow

1. If ChEMBL ID available: `ChEMBL_search_compound_structural_alerts(molecule_chembl_id=chembl_id, limit=20)`
2. Parse alert types: PAINS (pan-assay interference), Brenk (medicinal chemistry), Glaxo (GSK structural alerts)
3. Categorize severity: Some alerts are informational, others indicate likely toxicity

### Decision Logic

- **PAINS alerts**: May cause false positives in screening; note for medicinal chemistry
- **Brenk alerts**: Known problematic substructures; flag if present
- **No alerts**: Good sign but not definitive proof of safety
- **No ChEMBL ID**: Skip this phase gracefully; note "structural alert analysis not available"

---

## Synthesis: Integrated Risk Assessment (MANDATORY)

**Always the final section**. Integrates all evidence into actionable risk classification.

### Risk Classification Matrix

| Risk Level | Criteria |
|-----------|----------|
| **CRITICAL** | FDA boxed warning present OR multiple [T1] toxicity findings OR active DILI + active hERG |
| **HIGH** | FDA warnings present OR [T2] animal toxicity OR multiple active ADMET endpoints |
| **MEDIUM** | Some [T3] predictions positive OR CTD disease associations OR structural alerts |
| **LOW** | All ADMET endpoints negative AND no FDA/DrugBank safety flags AND no CTD concerns |
| **INSUFFICIENT DATA** | Fewer than 3 phases returned data; cannot make confident assessment |

### Synthesis Template

```markdown
## Integrated Risk Assessment

### Overall Risk Classification: [HIGH]

### Evidence Summary
| Dimension | Finding | Evidence Tier | Concern |
|-----------|---------|--------------|---------|
| ADMET Toxicity | DILI active, hERG active | [T3] | HIGH |
| FDA Label | Boxed warning for hepatotoxicity | [T1] | CRITICAL |
| CTD Toxicogenomics | 156 gene interactions, liver neoplasms | [T2] | HIGH |
| DrugBank | Known hepatotoxicity at high doses | [T2] | HIGH |
| STITCH | Binds CYP3A4, hERG | [T3] | MEDIUM |
| Structural Alerts | 2 Brenk alerts | [T3] | MEDIUM |

### Key Safety Concerns
1. **Hepatotoxicity** [T1]: FDA boxed warning + ADMET-AI DILI prediction + CTD liver disease associations
2. **Cardiac Risk** [T3]: ADMET-AI hERG prediction + STITCH hERG interaction
3. **Drug Interactions** [T3]: CYP3A4 substrate/inhibitor, potential DDI risk

### Data Gaps
- [ ] No in vivo genotoxicity data available
- [ ] STITCH interaction scores moderate (700-900)
- [ ] No environmental exposure data

### Recommendations
1. Avoid doses >4g/day (hepatotoxicity threshold) [T1]
2. Monitor liver function in chronic use [T1]
3. Screen for CYP3A4 interactions before co-administration [T3]
4. Consider cardiac monitoring for at-risk patients [T3]
```

---

## Mandatory Completeness Checklist

Before finalizing any report, verify:

- [ ] **Phase 0**: Compound fully disambiguated (SMILES + CID at minimum)
- [ ] **Phase 1**: At least 5 toxicity endpoints reported or "prediction unavailable" noted
- [ ] **Phase 2**: ADMET profile with A/D/M/E sections or "not available" noted
- [ ] **Phase 3**: CTD queried; gene interactions and disease associations reported or "no data in CTD"
- [ ] **Phase 4**: FDA labels queried; results or "not an FDA-approved drug" noted
- [ ] **Phase 5**: DrugBank queried; results or "not found in DrugBank" noted
- [ ] **Phase 6**: STITCH queried; results or "no STITCH data available" noted
- [ ] **Phase 7**: Structural alerts checked or "ChEMBL ID not available" noted
- [ ] **Synthesis**: Risk classification provided with evidence summary
- [ ] **Evidence Grading**: All findings have [T1]-[T4] annotations
- [ ] **Data Gaps**: Explicitly listed in synthesis section

---

## Tool Parameter Reference

**Critical Parameter Notes** (verified from source code):

| Tool | Parameter Name | Type | Notes |
|------|---------------|------|-------|
| All ADMETAI tools | `smiles` | `list[str]` | Always a list, even for single compound |
| All CTD tools | `input_terms` | `str` | Chemical name, MeSH name, CAS RN, or MeSH ID |
| All FDA tools | `drug_name` | `str` | Brand or generic drug name |
| drugbank_get_safety_* | `query`, `case_sensitive`, `exact_match`, `limit` | str, bool, bool, int | All 4 required |
| STITCH_resolve_identifier | `identifier`, `species` | str, int | species=9606 for human |
| STITCH_get_chemical_protein_interactions | `identifiers`, `species`, `required_score` | list[str], int, int | required_score=400 default |
| PubChem_get_CID_by_compound_name | `name` | `str` | Compound name (not SMILES) |
| PubChem_get_compound_properties_by_CID | `cid` | `int` | Numeric CID |
| ChEMBL_search_compound_structural_alerts | `molecule_chembl_id` | `str` | ChEMBL ID (e.g., "CHEMBL112") |

### Response Format Notes

- **ADMET-AI**: Returns `{status: "success", data: {...}}` with prediction values
- **CTD**: Returns list of interaction/association objects
- **FDA**: Returns `{status, data}` with label text
- **DrugBank**: Returns `{data: [...]}` with drug records
- **STITCH**: Returns list of interaction objects with scores
- **PubChem CID lookup**: Returns `{IdentifierList: {CID: [...]}}` (may or may not have `data` wrapper)
- **PubChem properties**: Returns dict with `CID`, `MolecularWeight`, `ConnectivitySMILES`, `IUPACName`

---

## Fallback Strategies

### Compound Resolution
- **Primary**: PubChem by name -> CID -> properties -> SMILES
- **Fallback 1**: ChEMBL search by name -> molecule -> SMILES
- **Fallback 2**: If SMILES provided directly, skip name resolution

### Toxicity Prediction
- **Primary**: All 9 ADMET-AI endpoints
- **Fallback**: If ADMET-AI fails for a compound, note "prediction failed" and continue with database evidence
- **Note**: ADMET-AI may fail for very large or unusual SMILES

### Regulatory Data
- **Primary**: FDA labels by drug name
- **Fallback**: If FDA returns no data, try alternative drug names (brand vs generic)
- **Note**: Non-drug chemicals (pesticides, industrial) will not have FDA labels

### CTD Data
- **Primary**: Search by common chemical name
- **Fallback**: Try MeSH name if common name fails
- **Note**: Novel compounds may not be in CTD

---

## Common Use Patterns

### Pattern 1: Novel Compound Assessment
```
Input: SMILES string for new molecule
Workflow: Phase 0 (SMILES->CID) -> Phase 1 (toxicity) -> Phase 2 (ADMET) -> Phase 7 (structural alerts) -> Synthesis
Output: Predictive safety profile for novel compound
```

### Pattern 2: Approved Drug Safety Review
```
Input: Drug name (e.g., "Acetaminophen")
Workflow: All phases (0-7 + Synthesis)
Output: Complete safety dossier with regulatory + predictive + database evidence
```

### Pattern 3: Environmental Chemical Risk
```
Input: Chemical name (e.g., "Bisphenol A")
Workflow: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 (CTD, key for env chemicals) -> Phase 6 -> Synthesis
Output: Environmental health risk assessment focused on gene-disease associations
```

### Pattern 4: Batch Toxicity Screening
```
Input: Multiple SMILES strings
Workflow: Phase 0 -> Phase 1 (batch) -> Phase 2 (batch) -> Comparative table -> Synthesis
Output: Comparative toxicity table ranking compounds by safety
```

### Pattern 5: Toxicogenomic Deep-Dive
```
Input: Chemical name + specific gene or disease interest
Workflow: Phase 0 -> Phase 3 (CTD expanded) -> Literature search -> Synthesis
Output: Detailed chemical-gene-disease mechanistic analysis
```

---

## Output Report Structure

All analyses generate a structured markdown report with progressive sections:

```markdown
# Chemical Safety & Toxicology Report: [Compound Name]

**Generated**: YYYY-MM-DD HH:MM
**Compound**: [Name] | SMILES: [SMILES] | CID: [CID]

## Executive Summary
[2-3 sentence overview with risk classification and key findings, all graded]

## 1. Compound Identity
[Phase 0 results - disambiguation table]

## 2. Predictive Toxicology
[Phase 1 results - ADMET-AI toxicity endpoints]

## 3. ADMET Profile
[Phase 2 results - absorption, distribution, metabolism, excretion]

## 4. Toxicogenomics
[Phase 3 results - CTD chemical-gene-disease relationships]

## 5. Regulatory Safety
[Phase 4 results - FDA label information]

## 6. Drug Safety Profile
[Phase 5 results - DrugBank data]

## 7. Chemical-Protein Interactions
[Phase 6 results - STITCH network]

## 8. Structural Alerts
[Phase 7 results - ChEMBL alerts]

## 9. Integrated Risk Assessment
[Synthesis - risk classification, evidence summary, data gaps, recommendations]

## Appendix: Methods and Data Sources
[Tool versions, databases queried, date of access]
```

---

## Limitations & Known Issues

### Tool-Specific
- **ADMET-AI**: Predictions are computational [T3]; should not replace experimental testing
- **CTD**: Curated but may lag behind latest literature by 6-12 months
- **FDA**: Only covers FDA-approved drugs; not applicable to environmental chemicals or supplements
- **DrugBank**: Primarily drugs; limited coverage of industrial chemicals
- **STITCH**: Score thresholds affect sensitivity; lower scores increase false positives
- **ChEMBL**: Structural alerts require ChEMBL ID; not all compounds have one

### Analysis
- **Novel compounds**: May only have ADMET-AI predictions (no database evidence)
- **Environmental chemicals**: FDA/DrugBank phases will be empty; rely on CTD and ADMET-AI
- **Batch mode**: ADMET-AI can handle batches; other tools require individual queries
- **Species specificity**: Most data is human-centric; animal data noted where applicable

### Technical
- **SMILES validity**: Invalid SMILES will cause ADMET-AI failures
- **Name ambiguity**: Chemical names can be ambiguous; always verify with CID
- **Rate limits**: Some FDA endpoints may rate-limit for rapid queries

---

## Summary

**Chemical Safety & Toxicology Assessment Skill** provides comprehensive safety evaluation by integrating:

1. **Predictive toxicology** (ADMET-AI) - 9 tools covering toxicity, ADMET, physicochemical properties
2. **Toxicogenomics** (CTD) - Chemical-gene-disease relationship mapping
3. **Regulatory safety** (FDA) - 6 tools for label-based safety extraction
4. **Drug safety** (DrugBank) - Curated toxicity and contraindication data
5. **Chemical interactions** (STITCH) - Chemical-protein interaction networks
6. **Structural alerts** (ChEMBL) - Known toxic substructure detection

**Outputs**: Structured markdown report with risk classification, evidence grading, and actionable recommendations

**Best for**: Drug safety assessment, chemical hazard profiling, environmental toxicology, ADMET characterization, toxicogenomic analysis

**Total tools integrated**: 25+ tools across 6 databases
