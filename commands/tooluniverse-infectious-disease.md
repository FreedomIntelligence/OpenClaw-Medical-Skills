# tooluniverse-infectious-disease

> Rapid pathogen characterization and drug repurposing analysis for infectious disease outbreaks. Identifies pathogen taxonomy, essential proteins, predicts structures, and screens existing drugs via docking. Use when facing novel pathogens, emerging infections, or needing rapid therapeutic options during outbreaks.

# Infectious Disease Outbreak Intelligence

Rapid response system for emerging pathogens using taxonomy analysis, target identification, structure prediction, and computational drug repurposing.

**KEY PRINCIPLES**:
1. **Speed is critical** - Optimize for rapid actionable intelligence
2. **Target essential proteins** - Focus on conserved, essential viral/bacterial proteins
3. **Leverage existing drugs** - Prioritize FDA-approved compounds for repurposing
4. **Structure-guided** - Use NvidiaNIM for rapid structure prediction and docking
5. **Evidence-graded** - Grade repurposing candidates by evidence strength
6. **Actionable output** - Prioritized drug candidates with rationale
7. **English-first queries** - Always use English terms in tool calls (pathogen names, protein names, drug names), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## When to Use

Apply when user asks:
- "New pathogen detected - what drugs might work?"
- "Emerging virus [X] - therapeutic options?"
- "Drug repurposing candidates for [pathogen]"
- "What do we know about [novel coronavirus/bacteria]?"
- "Essential targets in [pathogen] for drug development"
- "Can we repurpose [drug] against [pathogen]?"

---

## Critical Workflow Requirements

### 1. Report-First Approach (MANDATORY)

1. **Create the report file FIRST**:
   - File name: `[PATHOGEN]_outbreak_intelligence.md`
   - Initialize with section headers
   - Add placeholder: `[Analyzing...]`

2. **Progressively update** as you gather data

3. **Output separate files**:
   - `[PATHOGEN]_drug_candidates.csv` - Ranked repurposing candidates
   - `[PATHOGEN]_target_proteins.csv` - Druggable targets

### 2. Citation Requirements (MANDATORY)

```markdown
### Target: RNA-dependent RNA polymerase (RdRp)
- **UniProt**: P0DTD1 (NSP12)
- **Essentiality**: Required for replication
- **Conservation**: >95% across variants
- **Drug precedent**: Remdesivir targets RdRp

*Source: UniProt via `UniProt_search`, literature review*
```

---

## Phase 0: Tool Verification

### Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `NCBI_Taxonomy_search` | `name` | `query` |
| `UniProt_search` | `name` | `query` |
| `ChEMBL_search_targets` | `target` | `query` |
| `NvidiaNIM_diffdock` | `protein_file` | `protein` (content) |

---

## Workflow Overview

```
Phase 1: Pathogen Identification
├── Taxonomic classification
├── Closest relatives (for knowledge transfer)
├── Genome/proteome availability
└── OUTPUT: Pathogen profile
    ↓
Phase 2: Target Identification
├── Essential genes/proteins
├── Conserved across strains
├── Druggability assessment
└── OUTPUT: Prioritized target list
    ↓
Phase 3: Structure Prediction (NvidiaNIM)
├── AlphaFold2/ESMFold for targets
├── Binding site identification
├── Quality assessment (pLDDT)
└── OUTPUT: Target structures
    ↓
Phase 4: Drug Repurposing Screen
├── Approved drugs for related pathogens
├── Broad-spectrum antivirals/antibiotics
├── Docking screen (NvidiaNIM_diffdock)
└── OUTPUT: Candidate drugs
    ↓
Phase 4.5: Pathway Analysis (NEW)
├── KEGG: Pathogen metabolism pathways
├── Essential metabolic targets
├── Host-pathogen interaction pathways
└── OUTPUT: Pathway-based drug targets
    ↓
Phase 5: Literature Intelligence (ENHANCED)
├── PubMed: Published outbreak reports
├── BioRxiv/MedRxiv: Recent preprints (CRITICAL for outbreaks)
├── ArXiv: Computational/ML preprints
├── OpenAlex: Citation tracking
└── OUTPUT: Evidence synthesis
    ↓
Phase 6: Report Synthesis
├── Top drug candidates
├── Clinical trial opportunities
├── Recommended immediate actions
└── OUTPUT: Final report
```

---

## Phase 1: Pathogen Identification

### 1.1 Taxonomic Classification

```python
def identify_pathogen(tu, pathogen_query):
    """Classify pathogen taxonomically."""
    
    # NCBI Taxonomy search
    taxonomy = tu.tools.NCBI_Taxonomy_search(query=pathogen_query)
    
    return {
        'taxid': taxonomy.get('taxid'),
        'scientific_name': taxonomy.get('scientific_name'),
        'rank': taxonomy.get('rank'),
        'lineage': taxonomy.get('lineage'),
        'type': classify_type(taxonomy)  # virus, bacteria, fungus, parasite
    }
```

### 1.2 Related Pathogens (Knowledge Transfer)

```python
def find_related_pathogens(tu, taxid):
    """Find related pathogens for drug knowledge transfer."""
    
    # Get family/genus level relatives
    relatives = tu.tools.NCBI_Taxonomy_get_children(
        taxid=taxid,
        rank="genus"
    )
    
    # Find relatives with approved drugs
    related_with_drugs = []
    for rel in relatives:
        drugs = tu.tools.ChEMBL_search_targets(
            query=rel['scientific_name'],
            organism_contains=True
        )
        if drugs:
            related_with_drugs.append({
                'pathogen': rel,
                'drugs': drugs
            })
    
    return related_with_drugs
```

### 1.3 Output for Report

```markdown
## 1. Pathogen Profile

### 1.1 Taxonomic Classification

| Property | Value |
|----------|-------|
| **Organism** | SARS-CoV-2 |
| **Taxonomy ID** | 2697049 |
| **Type** | RNA virus (positive-sense, single-stranded) |
| **Family** | Coronaviridae |
| **Genus** | Betacoronavirus |
| **Lineage** | Riboviria > Orthornavirae > Pisuviricota > Pisoniviricetes > Nidovirales |

### 1.2 Related Pathogens with Drug Precedent

| Relative | Similarity | Approved Drugs | Relevance |
|----------|------------|----------------|-----------|
| SARS-CoV | 79% genome | Remdesivir (EUA) | High |
| MERS-CoV | 50% genome | None approved | Medium |
| HCoV-229E | 45% genome | None specific | Low |

**Knowledge Transfer Opportunity**: SARS-CoV drug development data highly relevant.

*Source: NCBI Taxonomy, ChEMBL*
```

---

## Phase 2: Target Identification

### 2.1 Essential Protein Identification

```python
def identify_targets(tu, pathogen_name):
    """Identify essential druggable targets."""
    
    # Search UniProt for pathogen proteins
    proteins = tu.tools.UniProt_search(
        query=f"organism:{pathogen_name}",
        reviewed=True
    )
    
    # Prioritize by essentiality and druggability
    targets = []
    for protein in proteins:
        # Check for known drug interactions
        chembl_target = tu.tools.ChEMBL_search_targets(
            query=protein['gene_name']
        )
        
        targets.append({
            'uniprot': protein['accession'],
            'name': protein['protein_name'],
            'function': protein['function'],
            'has_drug_precedent': len(chembl_target) > 0,
            'druggability': assess_druggability(protein)
        })
    
    return rank_targets(targets)
```

### 2.2 Target Prioritization Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Essentiality** | 30% | Required for replication/survival |
| **Conservation** | 25% | Conserved across strains/variants |
| **Druggability** | 25% | Structural features amenable to binding |
| **Drug precedent** | 20% | Existing drugs for homologous targets |

### 2.3 Output for Report

```markdown
## 2. Druggable Targets

### 2.1 Prioritized Target List

| Rank | Target | UniProt | Function | Score | Drug Precedent |
|------|--------|---------|----------|-------|----------------|
| 1 | RdRp (NSP12) | P0DTD1 | RNA replication | 92 | Remdesivir |
| 2 | Main protease (Mpro) | P0DTD1 | Polyprotein cleavage | 88 | Nirmatrelvir |
| 3 | Papain-like protease | P0DTD1 | Polyprotein cleavage | 75 | GRL0617 (preclinical) |
| 4 | Spike protein | P0DTC2 | Host cell entry | 70 | Antibodies |
| 5 | Helicase (NSP13) | P0DTD1 | RNA unwinding | 65 | None approved |

### 2.2 Target Details

#### Target 1: RNA-dependent RNA polymerase (RdRp/NSP12)

| Property | Value |
|----------|-------|
| **UniProt** | P0DTD1 (polyprotein position 4393-5324) |
| **Length** | 932 amino acids |
| **Function** | Catalyzes RNA synthesis from RNA template |
| **Essentiality** | Absolute (no replication without RdRp) |
| **Conservation** | >99% across all SARS-CoV-2 variants |
| **Binding site** | Nucleotide binding pocket |
| **Drug precedent** | Remdesivir (FDA approved), Favipiravir |

*Source: UniProt, ChEMBL*
```

---

## Phase 3: Structure Prediction

### 3.1 AlphaFold2 Structure Prediction (NVIDIA NIM)

```python
def predict_target_structure(tu, sequence, target_name):
    """Predict structure for target protein."""
    
    # Use AlphaFold2 for high accuracy
    structure = tu.tools.NvidiaNIM_alphafold2(
        sequence=sequence,
        algorithm="mmseqs2",
        relax_prediction=False
    )
    
    # Parse pLDDT confidence
    plddt_scores = parse_plddt(structure)
    
    return {
        'structure': structure['structure'],
        'mean_plddt': np.mean(plddt_scores),
        'high_confidence_regions': get_high_confidence(plddt_scores),
        'predicted_binding_site': identify_binding_site(structure)
    }
```

### 3.2 Structure Quality Assessment

| pLDDT Range | Confidence | Use for Docking |
|-------------|------------|-----------------|
| >90 | Very High | Excellent |
| 70-90 | High | Good |
| 50-70 | Medium | Use caution |
| <50 | Low | Not recommended |

### 3.3 Output for Report

```markdown
## 3. Target Structures

### 3.1 Structure Prediction Results

| Target | Method | Length | Mean pLDDT | Docking Ready |
|--------|--------|--------|------------|---------------|
| RdRp (NSP12) | AlphaFold2 | 932 aa | 91.2 | ✓ Yes |
| Mpro | AlphaFold2 | 306 aa | 93.5 | ✓ Yes |
| PLpro | AlphaFold2 | 315 aa | 88.7 | ✓ Yes |

### 3.2 RdRp Structure Quality

| Region | Residues | pLDDT | Functional Role |
|--------|----------|-------|-----------------|
| Palm domain | 582-620 | 94.2 | Catalytic site |
| Fingers domain | 397-581 | 91.8 | NTP entry |
| Thumb domain | 621-815 | 89.4 | RNA binding |
| Active site | D760, D761 | 96.1 | Catalysis |

**Docking Recommendation**: Structure suitable for docking; active site highly confident.

*Source: NVIDIA NIM via `NvidiaNIM_alphafold2`*
```

---

## Phase 4: Drug Repurposing Screen

### 4.1 Identify Repurposing Candidates

```python
def get_repurposing_candidates(tu, target_name, pathogen_family):
    """Find approved drugs to repurpose."""
    
    candidates = []
    
    # 1. Drugs approved for related pathogens
    related_drugs = tu.tools.ChEMBL_search_drugs(
        query=pathogen_family,
        max_phase=4
    )
    candidates.extend(related_drugs)
    
    # 2. Broad-spectrum antivirals
    antivirals = tu.tools.ChEMBL_search_drugs(
        query="broad spectrum antiviral",
        max_phase=4
    )
    candidates.extend(antivirals)
    
    # 3. Drugs with known activity against target class
    target_class_drugs = tu.tools.DGIdb_get_drug_gene_interactions(
        genes=[target_name]
    )
    candidates.extend(target_class_drugs)
    
    return deduplicate(candidates)
```

### 4.2 Docking Screen (NVIDIA NIM)

```python
def dock_candidates(tu, target_structure, candidate_smiles_list):
    """Dock candidate drugs against target."""
    
    results = []
    for smiles in candidate_smiles_list:
        docking = tu.tools.NvidiaNIM_diffdock(
            protein=target_structure,
            ligand=smiles,
            num_poses=5
        )
        
        results.append({
            'smiles': smiles,
            'top_score': docking['poses'][0]['confidence'],
            'poses': docking['poses']
        })
    
    return sorted(results, key=lambda x: x['top_score'], reverse=True)
```

### 4.3 Output for Report

```markdown
## 4. Drug Repurposing Screen

### 4.1 Candidate Identification

| Source | Candidates | FDA Approved |
|--------|------------|--------------|
| Related pathogen drugs | 12 | 8 |
| Broad-spectrum antivirals | 15 | 11 |
| Target class drugs | 8 | 5 |
| **Total unique** | **28** | **19** |

### 4.2 Docking Results (RdRp Target)

| Rank | Drug | Indication | Docking Score | Evidence |
|------|------|------------|---------------|----------|
| 1 | **Remdesivir** | COVID-19 | 0.92 | ★★★ FDA approved |
| 2 | **Favipiravir** | Influenza | 0.87 | ★★☆ Phase 3 COVID |
| 3 | **Sofosbuvir** | HCV | 0.84 | ★★☆ In vitro active |
| 4 | Ribavirin | RSV, HCV | 0.78 | ★☆☆ Mixed results |
| 5 | Molnupiravir | COVID-19 | 0.76 | ★★★ FDA approved |

### 4.3 Top Candidate: Remdesivir

| Property | Value |
|----------|-------|
| **Docking score** | 0.92 (excellent) |
| **Mechanism** | RdRp inhibitor (nucleotide analog) |
| **FDA status** | Approved for COVID-19 |
| **Clinical evidence** | ACTT-1: Reduced recovery time |
| **Binding mode** | Active site, chain termination |

*Source: NVIDIA NIM via `NvidiaNIM_diffdock`, ChEMBL*
```

---

## Phase 4.5: Pathway Analysis (NEW)

### 4.5.1 Pathogen Metabolism Pathways

```python
def analyze_pathogen_pathways(tu, pathogen_name, pathogen_type):
    """Identify druggable metabolic pathways in pathogen."""
    
    # KEGG pathogen pathways
    pathways = tu.tools.kegg_search_pathway(
        query=f"{pathogen_name} metabolism"
    )
    
    # Essential metabolic genes
    essential_genes = tu.tools.kegg_get_pathway_genes(
        pathway_id=pathways[0]['pathway_id']
    )
    
    # Host-pathogen interaction pathways
    host_pathogen = tu.tools.kegg_search_pathway(
        query=f"{pathogen_name} host interaction"
    )
    
    return {
        'metabolic_pathways': pathways,
        'essential_genes': essential_genes,
        'host_interaction': host_pathogen
    }
```

### 4.5.2 Output for Report

```markdown
## 4.5 Pathway Analysis

### Pathogen Metabolic Pathways (KEGG)

| Pathway | Essentiality | Drug Targets |
|---------|--------------|--------------|
| Viral replication (ko03030) | Essential | RdRp, Helicase |
| Viral protein processing | Essential | Mpro, PLpro |
| Host membrane interaction | Essential | Spike, ACE2 |

### Druggable Pathway Targets

| Target | Pathway | Known Drugs | Evidence |
|--------|---------|-------------|----------|
| RdRp | Viral replication | Remdesivir | ★★★ |
| 3CLpro | Protein processing | Nirmatrelvir | ★★★ |
| PLpro | Protein processing | GRL-0617 | ★★☆ |

### Host-Pathogen Interaction Points

| Interaction | Host Protein | Pathway | Druggability |
|-------------|--------------|---------|--------------|
| Entry | ACE2 | Cell surface | ★★☆ |
| Fusion | TMPRSS2 | Protease | ★★★ |
| Replication | Host ribosomes | Translation | ★☆☆ |

*Source: KEGG, Reactome*
```

---

## Phase 5: Literature Intelligence (ENHANCED)

### 5.1 Comprehensive Literature Search

```python
def comprehensive_outbreak_literature(tu, pathogen_name):
    """Search all literature sources for outbreak intelligence."""
    
    # PubMed: Peer-reviewed
    pubmed = tu.tools.PubMed_search_articles(
        query=f"{pathogen_name} AND (outbreak OR treatment OR drug)",
        limit=50,
        sort="date"
    )
    
    # BioRxiv: CRITICAL for outbreaks - newest findings
    biorxiv = tu.tools.BioRxiv_search_preprints(
        query=f"{pathogen_name} treatment mechanism",
        limit=20
    )
    
    # MedRxiv: Clinical preprints
    medrxiv = tu.tools.MedRxiv_search_preprints(
        query=f"{pathogen_name} clinical trial",
        limit=20
    )
    
    # ArXiv: Computational/ML papers
    arxiv = tu.tools.ArXiv_search_papers(
        query=f"{pathogen_name} drug discovery",
        category="q-bio",
        limit=10
    )
    
    # Clinical trials
    trials = tu.tools.search_clinical_trials(
        condition=pathogen_name,
        status="Recruiting"
    )
    
    # Citation analysis
    key_papers = pubmed[:10]
    for paper in key_papers:
        citation = tu.tools.openalex_search_works(
            query=paper['title'],
            limit=1
        )
        paper['citations'] = citation[0].get('cited_by_count', 0) if citation else 0
    
    return {
        'pubmed': pubmed,
        'biorxiv': biorxiv,
        'medrxiv': medrxiv,
        'arxiv': arxiv,
        'trials': trials,
        'key_papers': key_papers
    }
```

### 5.2 Output for Report

```markdown
## 5. Literature Intelligence

### 5.1 Published Literature (Peer-Reviewed)

| Topic | Papers | Key Finding |
|-------|--------|-------------|
| Treatment | 234 | Paxlovid remains effective |
| Resistance | 45 | Nirmatrelvir resistance mutations identified |
| Variants | 189 | XBB variants maintain drug sensitivity |
| Vaccines | 312 | Updated boosters protective |

### 5.2 Preprints (CRITICAL for Emerging Outbreaks)

**⚠️ Note**: Preprints are NOT peer-reviewed. Critical for rapid intelligence but use with caution.

| Source | Title | Posted | Key Finding |
|--------|-------|--------|-------------|
| BioRxiv | Novel RdRp inhibitor shows activity... | 2024-02-01 | New candidate |
| MedRxiv | Real-world effectiveness of... | 2024-01-28 | Paxlovid 85% effective |
| BioRxiv | Resistance mutations in... | 2024-01-25 | Monitor L50F mutation |

### 5.3 Computational/ML Preprints (ArXiv)

| Title | Category | Relevance |
|-------|----------|-----------|
| Deep learning for antiviral discovery | q-bio.BM | Drug design |
| Structure prediction for novel... | q-bio.BM | Target modeling |

### 5.4 Active Clinical Trials

| NCT ID | Phase | Drug | Status |
|--------|-------|------|--------|
| NCT05012345 | 3 | Ensitrelvir | Recruiting |
| NCT05023456 | 2 | VV116 | Recruiting |
| NCT05034567 | 2 | S-217622 | Active |

### 5.5 Citation Analysis (High-Impact Papers)

| PMID | Title | Citations | Year |
|------|-------|-----------|------|
| 33123456 | Remdesivir for COVID-19 | 5,234 | 2020 |
| 34234567 | Paxlovid Phase 3 results | 2,876 | 2022 |

*Source: PubMed, BioRxiv, MedRxiv, ArXiv, OpenAlex, ClinicalTrials.gov*
```

---

## Report Template

```markdown
# Outbreak Intelligence Report: [PATHOGEN]

**Generated**: [Date] | **Query**: [Original query] | **Status**: In Progress

---

## Executive Summary
[Analyzing...]

---

## 1. Pathogen Profile
### 1.1 Classification
[Analyzing...]
### 1.2 Related Pathogens
[Analyzing...]

---

## 2. Druggable Targets
### 2.1 Prioritized Targets
[Analyzing...]
### 2.2 Target Details
[Analyzing...]

---

## 3. Target Structures
### 3.1 Prediction Results
[Analyzing...]
### 3.2 Binding Sites
[Analyzing...]

---

## 4. Drug Repurposing Screen
### 4.1 Candidate Drugs
[Analyzing...]
### 4.2 Docking Results
[Analyzing...]
### 4.3 Top Candidates
[Analyzing...]

---

## 5. Literature Intelligence
### 5.1 Recent Findings
[Analyzing...]
### 5.2 Clinical Trials
[Analyzing...]

---

## 6. Recommendations
### 6.1 Immediate Actions
[Analyzing...]
### 6.2 Clinical Trial Opportunities
[Analyzing...]
### 6.3 Research Priorities
[Analyzing...]

---

## 7. Data Gaps & Limitations
[Analyzing...]

---

## 8. Data Sources
[Will be populated...]
```

---

## Evidence Grading

| Tier | Symbol | Criteria | Example |
|------|--------|----------|---------|
| **T1** | ★★★ | FDA approved for this pathogen | Remdesivir for COVID |
| **T2** | ★★☆ | Clinical trial evidence OR approved for related pathogen | Favipiravir |
| **T3** | ★☆☆ | In vitro activity OR strong docking + mechanism | Sofosbuvir |
| **T4** | ☆☆☆ | Computational prediction only | Novel docking hits |

---

## Completeness Checklist

### Phase 1: Pathogen ID
- [ ] Taxonomic classification complete
- [ ] Related pathogens identified
- [ ] Genome/proteome availability noted

### Phase 2: Targets
- [ ] ≥5 targets identified
- [ ] Essentiality documented
- [ ] Conservation assessed
- [ ] Drug precedent checked

### Phase 3: Structures
- [ ] Structures predicted for top 3 targets
- [ ] pLDDT confidence reported
- [ ] Binding sites identified

### Phase 4: Drug Screen
- [ ] ≥20 candidates screened
- [ ] FDA-approved drugs prioritized
- [ ] Docking scores reported
- [ ] Top 5 candidates detailed

### Phase 5: Literature
- [ ] Recent papers summarized
- [ ] Active trials listed
- [ ] Resistance data noted

### Phase 6: Recommendations
- [ ] ≥3 immediate actions
- [ ] Clinical trial opportunities
- [ ] Research priorities

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `NvidiaNIM_alphafold2` | `alphafold_get_prediction` | `NvidiaNIM_esmfold` |
| `NvidiaNIM_diffdock` | `NvidiaNIM_boltz2` | Manual docking |
| `NCBI_Taxonomy_search` | `UniProt_taxonomy` | Manual classification |
| `ChEMBL_search_drugs` | `DrugBank_search` | PubChem bioassays |

---

## Tool Reference

See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) for complete tool documentation.
