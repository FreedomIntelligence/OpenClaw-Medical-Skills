# tooluniverse-drug-repurposing

> Identify drug repurposing candidates using ToolUniverse for target-based, compound-based, and disease-driven strategies. Searches existing drugs for new therapeutic indications by analyzing targets, bioactivity, safety profiles, and literature evidence. Use when exploring drug repurposing opportunities, finding new indications for approved drugs, or when users mention drug repositioning, off-label uses, or therapeutic alternatives.

# Drug Repurposing with ToolUniverse

Systematically identify and evaluate drug repurposing candidates using multiple computational strategies.

**IMPORTANT**: Always use English terms in tool calls (drug names, disease names, target names), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

## Core Strategies

### 1. Target-Based Repurposing
Start with disease targets → Find drugs that modulate those targets

### 2. Compound-Based Repurposing  
Start with approved drugs → Find new disease indications

### 3. Disease-Driven Repurposing
Start with disease → Find targets → Match to existing drugs

## Quick Start

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse(use_cache=True)
tu.load_tools()

# Example: Find repurposing candidates for a disease
disease_name = "rheumatoid arthritis"

# Step 1: Get disease information
disease_info = tu.tools.OpenTargets_get_disease_id_description_by_name(
    diseaseName=disease_name
)

# Step 2: Get associated targets
disease_id = disease_info['data']['id']
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(
    efoId=disease_id,
    limit=10
)

# Step 3: Find drugs for each target
for target in targets['data'][:5]:
    drugs = tu.tools.DGIdb_get_drug_gene_interactions(
        gene_name=target['gene_symbol']
    )
    # Evaluate each drug candidate...
```

## Complete Workflow

### Phase 1: Disease & Target Analysis

```python
# 1.1 Get disease information
disease_info = tu.tools.OpenTargets_get_disease_id_description_by_name(
    diseaseName="[disease_name]"
)

# 1.2 Find associated targets
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(
    efoId=disease_info['data']['id'],
    limit=20
)

# 1.3 Get target details for top candidates
target_details = []
for target in targets['data'][:10]:
    details = tu.tools.UniProt_get_entry_by_accession(
        accession=target['uniprot_id']
    )
    target_details.append(details)
```

### Phase 2: Drug Discovery

```python
# 2.1 Find drugs targeting disease-associated targets
drug_candidates = []

for target in targets['data'][:10]:
    # Search DrugBank
    drugbank_results = tu.tools.drugbank_get_drug_name_and_description_by_target_name(
        target_name=target['gene_symbol']
    )
    
    # Search DGIdb
    dgidb_results = tu.tools.DGIdb_get_drug_gene_interactions(
        gene_name=target['gene_symbol']
    )
    
    # Search ChEMBL
    chembl_results = tu.tools.ChEMBL_search_drugs(
        query=target['gene_symbol'],
        limit=10
    )
    
    drug_candidates.extend([drugbank_results, dgidb_results, chembl_results])

# 2.2 Get drug details
for drug_name in unique_drugs:
    # Get DrugBank info
    drug_info = tu.tools.drugbank_get_drug_basic_info_by_drug_name_or_id(
        drug_name_or_drugbank_id=drug_name
    )
    
    # Get current indications
    indications = tu.tools.drugbank_get_indications_by_drug_name_or_drugbank_id(
        drug_name_or_drugbank_id=drug_name
    )
    
    # Get pharmacology
    pharmacology = tu.tools.drugbank_get_pharmacology_by_drug_name_or_drugbank_id(
        drug_name_or_drugbank_id=drug_name
    )
```

### Phase 3: Safety & Feasibility Assessment

```python
# 3.1 Check FDA safety data
for drug in top_candidates:
    # Get warnings and precautions
    warnings = tu.tools.FDA_get_warnings_and_cautions_by_drug_name(
        drug_name=drug['name']
    )
    
    # Get adverse event reports
    adverse_events = tu.tools.FAERS_search_reports_by_drug_and_reaction(
        drug_name=drug['name'],
        limit=100
    )
    
    # Get drug interactions
    interactions = tu.tools.drugbank_get_drug_interactions_by_drug_name_or_id(
        drug_name_or_id=drug['name']
    )

# 3.2 Assess ADMET properties (for novel formulations)
for drug in top_candidates:
    if 'smiles' in drug:
        admet = tu.tools.ADMETAI_predict_admet(
            smiles=drug['smiles'],
            use_cache=True
        )
```

### Phase 4: Literature Evidence

```python
# 4.1 Search for existing evidence
for drug in top_candidates:
    # PubMed search
    query = f"{drug['name']} AND {disease_name}"
    pubmed_results = tu.tools.PubMed_search_articles(
        query=query,
        max_results=50
    )
    
    # Europe PMC search
    pmc_results = tu.tools.EuropePMC_search_articles(
        query=query,
        limit=50
    )
    
    # Clinical trials
    trials = tu.tools.ClinicalTrials_search(
        condition=disease_name,
        intervention=drug['name']
    )
```

### Phase 5: Scoring & Ranking

Create a scoring function to rank candidates:

```python
def score_repurposing_candidate(drug, target_score, safety_data, literature_count):
    """Score drug repurposing candidate (0-100)."""
    score = 0
    
    # Target association strength (0-40 points)
    score += min(target_score * 40, 40)
    
    # Safety profile (0-30 points)
    if drug['approval_status'] == 'approved':
        score += 20
    elif drug['approval_status'] == 'clinical':
        score += 10
    
    if not safety_data.get('black_box_warning'):
        score += 10
    
    # Literature evidence (0-20 points)
    score += min(literature_count / 5 * 20, 20)
    
    # Drug-likeness (0-10 points)
    if drug.get('bioavailability') == 'high':
        score += 10
    
    return score

# Score all candidates
scored_candidates = []
for drug in drug_candidates:
    score = score_repurposing_candidate(
        drug=drug,
        target_score=drug['target_association_score'],
        safety_data=drug['safety_profile'],
        literature_count=drug['supporting_papers']
    )
    drug['repurposing_score'] = score
    scored_candidates.append(drug)

# Sort by score
ranked_candidates = sorted(
    scored_candidates,
    key=lambda x: x['repurposing_score'],
    reverse=True
)
```

## Alternative Strategies

### Strategy A: Mechanism-Based Repurposing

```python
# Find drugs with similar mechanism of action
known_drug = "metformin"

# Get mechanism
moa = tu.tools.drugbank_get_drug_desc_pharmacology_by_moa(
    mechanism_of_action="[moa_term]"
)

# Get similar drugs
similar = tu.tools.ChEMBL_search_similar_molecules(
    query=known_drug,
    similarity_threshold=70
)
```

### Strategy B: Network-Based Repurposing

```python
# Use pathway analysis
pathways = tu.tools.drugbank_get_pathways_reactions_by_drug_or_id(
    drug_name_or_drugbank_id="[drug_name]"
)

# Find drugs affecting same pathways
pathway_drugs = tu.tools.drugbank_get_drug_name_and_description_by_pathway_name(
    pathway_name=pathways['data'][0]['pathway_name']
)
```

### Strategy C: Phenotype-Based Repurposing

```python
# Search by indication/phenotype
indication_drugs = tu.tools.drugbank_get_drug_name_and_description_by_indication(
    indication="[related_indication]"
)

# Analyze adverse events as therapeutic effects
# Example: minoxidil (hypertension) → hair growth
adverse_as_therapeutic = tu.tools.FAERS_search_reports_by_drug_and_reaction(
    drug_name="[drug_name]",
    limit=1000
)
```

## Key ToolUniverse Tools

**Disease & Target Tools**:
- `OpenTargets_get_disease_id_description_by_name` - Disease lookup
- `OpenTargets_get_associated_targets_by_disease_efoId` - Disease targets
- `UniProt_get_entry_by_accession` - Protein details

**Drug Discovery Tools**:
- `drugbank_get_drug_name_and_description_by_target_name` - Drugs by target
- `drugbank_get_drug_name_and_description_by_indication` - Drugs by indication
- `DGIdb_get_drug_gene_interactions` - Drug-gene interactions
- `ChEMBL_search_drugs` - Drug search
- `ChEMBL_get_drug_mechanisms` - Mechanism of action

**Drug Information Tools**:
- `drugbank_get_drug_basic_info_by_drug_name_or_id` - Basic drug info
- `drugbank_get_indications_by_drug_name_or_drugbank_id` - Approved indications
- `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` - Pharmacology
- `drugbank_get_targets_by_drug_name_or_drugbank_id` - Drug targets

**Safety Assessment Tools**:
- `FDA_get_warnings_and_cautions_by_drug_name` - FDA warnings
- `FAERS_search_reports_by_drug_and_reaction` - Adverse events
- `FAERS_count_death_related_by_drug` - Serious outcomes
- `drugbank_get_drug_interactions_by_drug_name_or_id` - Interactions

**Property Prediction Tools**:
- `ADMETAI_predict_admet` - ADMET properties
- `ADMETAI_predict_toxicity` - Toxicity prediction

**Literature Tools**:
- `PubMed_search_articles` - PubMed search
- `EuropePMC_search_articles` - Europe PMC search
- `ClinicalTrials_search` - Clinical trials

## Output Format

Present results as ranked candidates:

```markdown
## Drug Repurposing Analysis: [Disease Name]

### Top 10 Repurposing Candidates

#### 1. [Drug Name] (Score: 87/100)

**Current Indications**: [list approved uses]
**Proposed Indication**: [new disease/condition]
**Repurposing Rationale**: Targets [gene/protein] with high association to disease

**Evidence Summary**:
- Target association score: 0.85
- Approval status: FDA approved (safer profile)
- Literature support: 23 papers, 4 clinical trials
- Safety profile: No black box warnings

**Mechanism**: [Brief mechanism description]

**Next Steps**: 
- Phase II trial feasibility assessment
- Patient population identification
- Dosing optimization study

**Key Papers**:
1. Smith et al. 2024 - Clinical efficacy in similar condition
2. Jones et al. 2023 - Mechanism validation

---

#### 2. [Drug Name] (Score: 79/100)
[Similar structure...]

### Supporting Analysis

**Target Network**: [visualization or description]
**Pathway Overlap**: [affected pathways]
**Safety Considerations**: [major concerns]
**Development Timeline**: [estimated phases]
```

## Scoring Criteria

**Target Association (0-40 points)**:
- Strong genetic evidence: 40
- Moderate association: 25
- Pathway-level evidence: 15
- Weak/predicted: 5

**Safety Profile (0-30 points)**:
- FDA approved: 20
- Phase III: 15
- Phase II: 10
- Phase I: 5
- No black box warning: +10
- Known serious AE: -10

**Literature Evidence (0-20 points)**:
- Clinical trials: 5 points each (max 15)
- Preclinical studies: 1 point each (max 10)
- Case reports: 0.5 points each (max 5)

**Drug Properties (0-10 points)**:
- High bioavailability: 5
- Good BBB penetration (if CNS): 5
- Low toxicity predictions: 5

## Best Practices

1. **Start Broad**: Query multiple databases (DrugBank, ChEMBL, DGIdb)
2. **Validate Targets**: Confirm target-disease associations in OpenTargets
3. **Check Safety First**: Prioritize approved drugs with known safety profiles
4. **Literature Mining**: Always search for existing clinical/preclinical evidence
5. **Use Caching**: Enable `use_cache=True` for expensive predictions
6. **Batch Operations**: Use `tu.run_batch()` for parallel queries
7. **Consider Mechanism**: Evaluate biological plausibility
8. **Patent Landscape**: Check if indication is already protected
9. **Market Analysis**: Consider unmet medical need and commercial viability
10. **Regulatory Path**: FDA approved drugs have faster repurposing path

## Common Patterns

### Pattern 1: Rapid Screening
```python
# Quick screening of 100+ drugs against disease targets
targets = get_disease_targets(disease_id)[:10]
all_drugs = []

for target in targets:
    drugs = tu.tools.DGIdb_get_drug_gene_interactions(
        gene_name=target['gene_symbol']
    )
    all_drugs.extend(drugs)

# Filter to FDA approved only
approved_drugs = [d for d in all_drugs if d.get('approved')]
```

### Pattern 2: Deep Dive Single Drug
```python
# Comprehensive analysis of one drug candidate
drug_name = "metformin"

# Get everything
info = tu.tools.drugbank_get_drug_basic_info_by_drug_name_or_id(drug_name_or_drugbank_id=drug_name)
targets = tu.tools.drugbank_get_targets_by_drug_name_or_drugbank_id(drug_name_or_drugbank_id=drug_name)
indications = tu.tools.drugbank_get_indications_by_drug_name_or_drugbank_id(drug_name_or_drugbank_id=drug_name)
pharmacology = tu.tools.drugbank_get_pharmacology_by_drug_name_or_drugbank_id(drug_name_or_drugbank_id=drug_name)
interactions = tu.tools.drugbank_get_drug_interactions_by_drug_name_or_id(drug_name_or_id=drug_name)
warnings = tu.tools.FDA_get_warnings_and_cautions_by_drug_name(drug_name=drug_name)
papers = tu.tools.PubMed_search_articles(query=f"{drug_name} AND [new_disease]", max_results=100)
```

### Pattern 3: Comparative Analysis
```python
# Compare multiple candidates side-by-side
candidates = ["drug_a", "drug_b", "drug_c"]

comparison = []
for drug in candidates:
    data = {
        'name': drug,
        'info': tu.tools.drugbank_get_drug_basic_info_by_drug_name_or_id(drug_name_or_drugbank_id=drug),
        'safety': tu.tools.FDA_get_warnings_and_cautions_by_drug_name(drug_name=drug),
        'evidence': tu.tools.PubMed_search_articles(query=drug, max_results=10)
    }
    comparison.append(data)
```

## Troubleshooting

**"Disease not found"**: 
- Try disease synonyms or EFO ID lookup
- Use broader disease categories

**"No drugs found for target"**:
- Check target name/symbol (HUGO nomenclature)
- Expand to pathway-level drugs
- Consider similar targets (protein family)

**"Insufficient literature evidence"**:
- Search for drug class rather than specific drug
- Check preclinical/animal studies
- Look for mechanism papers

**"Safety data unavailable"**:
- Drug may not be FDA approved in US
- Check EMA or other regulatory databases
- Review clinical trial safety data

## Example Use Cases

**Use Case 1: Find repurposing candidates for rare disease**
```python
# Rare disease often lack approved drugs
# Strategy: Find drugs targeting same pathways as related common diseases

rare_disease = "Niemann-Pick disease"
related_disease = "Alzheimer's disease"  # Similar pathology

# Get pathways affected in related disease
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(
    efoId=related_disease_id
)

# Find drugs for those targets
# Evaluate for rare disease applicability
```

**Use Case 2: Repurpose based on adverse effects**
```python
# Adverse effect in one context = therapeutic in another
# Example: Thalidomide (teratogenic) → cancer treatment

drug = "drug_name"
adverse_events = tu.tools.FAERS_search_reports_by_drug_and_reaction(
    drug_name=drug,
    limit=1000
)

# Analyze if adverse effects beneficial in other contexts
# Example: weight loss AE → obesity treatment potential
```

**Use Case 3: Combination therapy discovery**
```python
# Find drugs that complement existing therapy
primary_drug = "existing_therapy"
disease = "disease_name"

# Get targets not covered by primary drug
disease_targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(
    efoId=disease_id
)

primary_targets = tu.tools.drugbank_get_targets_by_drug_name_or_drugbank_id(
    drug_name_or_drugbank_id=primary_drug
)

# Find drugs for uncovered targets
uncovered_targets = [t for t in disease_targets if t not in primary_targets]
```

## Advanced Techniques

### Technique 1: Polypharmacology-Based Repurposing
```python
# Find drugs with multi-target activity matching disease network

# Get disease network
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(
    efoId=disease_id,
    limit=50
)

# For each drug, count how many disease targets it hits
for drug in candidate_drugs:
    drug_targets = tu.tools.drugbank_get_targets_by_drug_name_or_drugbank_id(
        drug_name_or_drugbank_id=drug
    )
    
    overlap = len(set(drug_targets) & set(disease_targets))
    if overlap >= 3:  # Multi-target match
        print(f"{drug}: hits {overlap} disease targets")
```

### Technique 2: Structure-Based Repurposing
```python
# Find structurally similar approved drugs

known_active = "known_active_compound"

# Get structure
cid = tu.tools.PubChem_get_CID_by_compound_name(
    compound_name=known_active
)

# Find similar
similar = tu.tools.PubChem_search_compounds_by_similarity(
    cid=cid['data']['cid'],
    threshold=85
)

# Check which are approved drugs
for compound in similar['data']:
    drug_info = tu.tools.PubChem_get_drug_label_info_by_CID(
        cid=compound['cid']
    )
```

### Technique 3: AI-Powered Candidate Selection
```python
# Use ML predictions to filter candidates

candidates_with_smiles = get_candidates_with_structures()

# Predict ADMET for all
admet_results = []
for drug in candidates_with_smiles:
    admet = tu.tools.ADMETAI_predict_admet(
        smiles=drug['smiles'],
        use_cache=True
    )
    admet_results.append({
        'drug': drug['name'],
        'admet': admet,
        'pass': evaluate_admet_criteria(admet)
    })

# Keep only drugs passing ADMET criteria
viable_candidates = [r for r in admet_results if r['pass']]
```

## Resources

For comprehensive disease analysis, see [disease-intelligence-gatherer skill](../disease-intelligence-gatherer/SKILL.md).

For compound property analysis, see [chemical-compound-retrieval skill](../chemical-compound-retrieval/SKILL.md).

For detailed ToolUniverse SDK usage, see [tooluniverse-sdk skill](../tooluniverse-sdk/SKILL.md).
