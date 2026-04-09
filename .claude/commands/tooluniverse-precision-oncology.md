# tooluniverse-precision-oncology

> Provide actionable treatment recommendations for cancer patients based on molecular profile. Interprets tumor mutations, identifies FDA-approved therapies, finds resistance mechanisms, matches clinical trials. Use when oncologist asks about treatment options for specific mutations (EGFR, KRAS, BRAF, etc.), therapy resistance, or clinical trial eligibility.

# Precision Oncology Treatment Advisor

Provide actionable treatment recommendations for cancer patients based on their molecular profile using CIViC, ClinVar, OpenTargets, ClinicalTrials.gov, and structure-based analysis.

**KEY PRINCIPLES**:
1. **Report-first** - Create report file FIRST, update progressively
2. **Evidence-graded** - Every recommendation has evidence level
3. **Actionable output** - Prioritized treatment options, not data dumps
4. **Clinical focus** - Answer "what should we do?" not "what exists?"
5. **English-first queries** - Always use English terms in tool calls (mutations, drug names, cancer types), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## When to Use

Apply when user asks:
- "Patient has [cancer] with [mutation] - what treatments?"
- "What are options for EGFR-mutant lung cancer?"
- "Patient failed [drug], what's next?"
- "Clinical trials for KRAS G12C?"
- "Why isn't [drug] working anymore?"

---

## Phase 0: Tool Verification

**CRITICAL**: Verify tool parameters before first use.

| Tool | WRONG | CORRECT |
|------|-------|---------|
| `civic_get_variant` | `variant_name` | `id` (numeric) |
| `civic_get_evidence_item` | `variant_id` | `id` |
| `OpenTargets_*` | `ensemblID` | `ensemblId` (camelCase) |
| `search_clinical_trials` | `disease` | `condition` |

---

## Workflow Overview

```
Input: Cancer type + Molecular profile (mutations, fusions, amplifications)

Phase 1: Profile Validation
├── Validate variant nomenclature
├── Resolve gene identifiers
└── Confirm cancer type (EFO/ICD)

Phase 2: Variant Interpretation
├── CIViC → Evidence for each variant
├── ClinVar → Pathogenicity
├── COSMIC → Somatic mutation frequency
├── GDC/TCGA → Real tumor data
├── DepMap → Target essentiality
├── OncoKB → FDA actionability levels (NEW)
├── cBioPortal → Cross-study mutation data (NEW)
├── Human Protein Atlas → Expression validation (NEW)
├── OpenTargets → Target-disease evidence
└── OUTPUT: Variant significance table + target validation + expression

Phase 2.5: Tumor Expression Context (NEW)
├── CELLxGENE → Cell-type specific expression in tumor
├── ChIPAtlas → Regulatory context
├── Cancer-specific expression patterns
└── OUTPUT: Expression validation

Phase 3: Treatment Options
├── Approved therapies (FDA label)
├── NCCN-recommended (literature)
├── Off-label with evidence
└── OUTPUT: Prioritized treatment list

Phase 3.5: Pathway & Network Analysis (NEW)
├── KEGG/Reactome → Pathway context
├── IntAct → Protein interactions
├── Drug combination rationale
└── OUTPUT: Biological context for combinations

Phase 4: Resistance Analysis (if prior therapy)
├── Known resistance mechanisms
├── Structure-based analysis (NvidiaNIM)
├── Network-based bypass pathways (IntAct)
└── OUTPUT: Resistance explanation + strategies

Phase 5: Clinical Trial Matching
├── Active trials for indication + biomarker
├── Eligibility filtering
└── OUTPUT: Matched trials

Phase 5.5: Literature Evidence (NEW)
├── PubMed → Published evidence
├── BioRxiv/MedRxiv → Recent preprints
├── OpenAlex → Citation analysis
└── OUTPUT: Supporting literature

Phase 6: Report Synthesis
├── Executive summary
├── Treatment recommendations (prioritized)
└── Next steps
```

---

## Phase 1: Profile Validation

### 1.1 Resolve Gene Identifiers

```python
def resolve_gene(tu, gene_symbol):
    """Resolve gene to all needed IDs."""
    ids = {}
    
    # Ensembl ID (for OpenTargets)
    gene_info = tu.tools.MyGene_query_genes(q=gene_symbol, species="human")
    ids['ensembl'] = gene_info.get('ensembl', {}).get('gene')
    
    # UniProt (for structure)
    uniprot = tu.tools.UniProt_search(query=gene_symbol, organism="human")
    ids['uniprot'] = uniprot[0].get('primaryAccession') if uniprot else None
    
    # ChEMBL target
    target = tu.tools.ChEMBL_search_targets(query=gene_symbol, organism="Homo sapiens")
    ids['chembl_target'] = target[0].get('target_chembl_id') if target else None
    
    return ids
```

### 1.2 Validate Variant Nomenclature

- **HGVS protein**: p.L858R, p.V600E
- **cDNA**: c.2573T>G
- **Common names**: T790M, G12C

---

## Phase 2: Variant Interpretation

### 2.1 CIViC Evidence Query

```python
def get_civic_evidence(tu, gene_symbol, variant_name):
    """Get CIViC evidence for variant."""
    # Search for variant
    variants = tu.tools.civic_search_variants(query=f"{gene_symbol} {variant_name}")
    
    evidence_items = []
    for var in variants:
        # Get evidence items for this variant
        evi = tu.tools.civic_get_variant(id=var['id'])
        evidence_items.extend(evi.get('evidence_items', []))
    
    # Categorize by evidence type
    return {
        'predictive': [e for e in evidence_items if e['evidence_type'] == 'Predictive'],
        'prognostic': [e for e in evidence_items if e['evidence_type'] == 'Prognostic'],
        'diagnostic': [e for e in evidence_items if e['evidence_type'] == 'Diagnostic']
    }
```

### 2.2 COSMIC Somatic Mutation Analysis (NEW)

```python
def get_cosmic_mutations(tu, gene_symbol, variant_name=None):
    """Get somatic mutation data from COSMIC database."""
    
    # Get all mutations for gene
    gene_mutations = tu.tools.COSMIC_get_mutations_by_gene(
        operation="get_by_gene",
        gene=gene_symbol,
        max_results=100,
        genome_build=38
    )
    
    # If specific variant, search for it
    if variant_name:
        specific = tu.tools.COSMIC_search_mutations(
            operation="search",
            terms=f"{gene_symbol} {variant_name}",
            max_results=20
        )
        return {
            'specific_variant': specific.get('results', []),
            'all_gene_mutations': gene_mutations.get('results', [])
        }
    
    return gene_mutations

def get_cosmic_hotspots(tu, gene_symbol):
    """Identify mutation hotspots in COSMIC."""
    mutations = tu.tools.COSMIC_get_mutations_by_gene(
        operation="get_by_gene",
        gene=gene_symbol,
        max_results=500
    )
    
    # Count by position
    position_counts = Counter(m['MutationAA'] for m in mutations.get('results', []))
    hotspots = position_counts.most_common(10)
    
    return hotspots
```

**Why COSMIC matters**:
- **Gold standard** for somatic cancer mutations
- Provides cancer type distribution (which cancers have this mutation)
- FATHMM pathogenicity prediction for novel variants
- Identifies hotspots vs. rare mutations

### 2.3 GDC/TCGA Pan-Cancer Analysis (NEW)

Access real patient tumor data from The Cancer Genome Atlas:

```python
def get_tcga_mutation_data(tu, gene_symbol, cancer_type=None):
    """
    Get somatic mutations from TCGA via GDC.
    
    Answers: "How often is this mutation seen in real tumors?"
    """
    
    # Get mutation frequency across all TCGA
    frequency = tu.tools.GDC_get_mutation_frequency(
        gene_symbol=gene_symbol
    )
    
    # Get specific mutations
    mutations = tu.tools.GDC_get_ssm_by_gene(
        gene_symbol=gene_symbol,
        project_id=f"TCGA-{cancer_type}" if cancer_type else None,
        size=50
    )
    
    return {
        'frequency': frequency.get('data', {}),
        'mutations': mutations.get('data', {}),
        'note': 'Real patient tumor data from TCGA'
    }

def get_tcga_expression_profile(tu, gene_symbol, cancer_type):
    """Get gene expression data from TCGA."""
    
    # Map cancer type to TCGA project
    project_map = {
        'lung': 'TCGA-LUAD',
        'breast': 'TCGA-BRCA', 
        'colorectal': 'TCGA-COAD',
        'melanoma': 'TCGA-SKCM',
        'glioblastoma': 'TCGA-GBM'
    }
    project_id = project_map.get(cancer_type.lower(), f'TCGA-{cancer_type.upper()}')
    
    expression = tu.tools.GDC_get_gene_expression(
        project_id=project_id,
        size=20
    )
    
    return expression.get('data', {})

def get_tcga_cnv_status(tu, gene_symbol, cancer_type):
    """Get copy number status from TCGA."""
    
    project_map = {
        'lung': 'TCGA-LUAD',
        'breast': 'TCGA-BRCA'
    }
    project_id = project_map.get(cancer_type.lower(), f'TCGA-{cancer_type.upper()}')
    
    cnv = tu.tools.GDC_get_cnv_data(
        project_id=project_id,
        gene_symbol=gene_symbol,
        size=20
    )
    
    return cnv.get('data', {})
```

**GDC Tools Summary**:
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `GDC_get_mutation_frequency` | Pan-cancer mutation stats | `gene_symbol` |
| `GDC_get_ssm_by_gene` | Specific mutations | `gene_symbol`, `project_id` |
| `GDC_get_gene_expression` | RNA-seq data | `project_id` |
| `GDC_get_cnv_data` | Copy number | `project_id`, `gene_symbol` |
| `GDC_list_projects` | Find TCGA projects | `program="TCGA"` |

**Why TCGA/GDC matters**:
- **Real patient data** - Not cell line or curated, actual tumor sequencing
- **Pan-cancer view** - Same gene across 33 cancer types
- **Multi-omic** - Mutations, expression, CNV together
- **Clinical correlation** - Survival data available

### 2.4 DepMap Target Validation (NEW)

Assess gene essentiality using CRISPR knockout data from cancer cell lines:

```python
def assess_target_essentiality(tu, gene_symbol, cancer_type=None):
    """
    Is this gene essential in cancer cell lines?
    
    Essential genes have negative dependency scores.
    Answers: "If we target this gene, will cancer cells die?"
    """
    
    # Get gene dependency data
    dependencies = tu.tools.DepMap_get_gene_dependencies(
        gene_symbol=gene_symbol
    )
    
    # Get cell lines for specific cancer type
    if cancer_type:
        cell_lines = tu.tools.DepMap_get_cell_lines(
            cancer_type=cancer_type,
            page_size=20
        )
        return {
            'gene': gene_symbol,
            'dependencies': dependencies.get('data', {}),
            'cell_lines': cell_lines.get('data', {}),
            'interpretation': 'Negative scores = gene is essential for cell survival'
        }
    
    return dependencies

def get_depmap_drug_sensitivity(tu, drug_name, cancer_type=None):
    """Get drug sensitivity data from DepMap."""
    
    drugs = tu.tools.DepMap_get_drug_response(
        drug_name=drug_name
    )
    
    return drugs.get('data', {})
```

**DepMap Tools Summary**:
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `DepMap_get_gene_dependencies` | CRISPR essentiality | `gene_symbol` |
| `DepMap_get_cell_lines` | Cell line metadata | `cancer_type`, `tissue` |
| `DepMap_search_cell_lines` | Search by name | `query` |
| `DepMap_get_drug_response` | Drug sensitivity | `drug_name` |

**Why DepMap matters for Precision Oncology**:
- **Target validation** - Proves gene is essential for cancer survival
- **Cancer selectivity** - Essential in cancer but not normal cells?
- **Resistance prediction** - What other genes become essential when you knockout target?
- **Combination rationale** - Identify synthetic lethal partners

**Example Clinical Application**:
```markdown
### Target Essentiality Assessment (DepMap)

**KRAS dependency in pancreatic cancer cell lines**:
| Cell Line | KRAS Effect Score | Interpretation |
|-----------|-------------------|----------------|
| PANC-1 | -0.82 | Strongly essential |
| MIA PaCa-2 | -0.75 | Essential |
| BxPC-3 | -0.21 | Less dependent (KRAS WT) |

*Interpretation: KRAS-mutant pancreatic cancer lines are highly dependent on KRAS - validates targeting strategy.*

*Source: DepMap via `DepMap_get_gene_dependencies`*
```

### 2.5 OncoKB Actionability Assessment (NEW)

OncoKB provides FDA-approved therapeutic actionability annotations:

```python
def get_oncokb_annotations(tu, gene_symbol, variant_name, tumor_type=None):
    """
    Get OncoKB actionability annotations.
    
    OncoKB Level of Evidence:
    - Level 1: FDA-approved
    - Level 2: Standard care
    - Level 3A: Compelling clinical evidence
    - Level 3B: Standard care in different tumor type
    - Level 4: Biological evidence
    - R1/R2: Resistance evidence
    """
    
    # Annotate the specific variant
    annotation = tu.tools.OncoKB_annotate_variant(
        operation="annotate_variant",
        gene=gene_symbol,
        variant=variant_name,  # e.g., "V600E"
        tumor_type=tumor_type  # OncoTree code e.g., "MEL", "LUAD"
    )
    
    result = {
        'oncogenic': annotation.get('data', {}).get('oncogenic'),
        'mutation_effect': annotation.get('data', {}).get('mutationEffect'),
        'highest_sensitive_level': annotation.get('data', {}).get('highestSensitiveLevel'),
        'treatments': annotation.get('data', {}).get('treatments', [])
    }
    
    # Get gene-level info
    gene_info = tu.tools.OncoKB_get_gene_info(
        operation="get_gene_info",
        gene=gene_symbol
    )
    
    result['is_oncogene'] = gene_info.get('data', {}).get('oncogene', False)
    result['is_tumor_suppressor'] = gene_info.get('data', {}).get('tsg', False)
    
    return result

def get_oncokb_cnv_annotation(tu, gene_symbol, alteration_type, tumor_type=None):
    """Get OncoKB annotation for copy number alterations."""
    
    annotation = tu.tools.OncoKB_annotate_copy_number(
        operation="annotate_copy_number",
        gene=gene_symbol,
        copy_number_type=alteration_type,  # "AMPLIFICATION" or "DELETION"
        tumor_type=tumor_type
    )
    
    return {
        'oncogenic': annotation.get('data', {}).get('oncogenic'),
        'treatments': annotation.get('data', {}).get('treatments', [])
    }
```

**OncoKB Level Mapping**:
| OncoKB Level | Our Tier | Description |
|--------------|----------|-------------|
| LEVEL_1 | ★★★ | FDA-recognized biomarker |
| LEVEL_2 | ★★★ | Standard care |
| LEVEL_3A | ★★☆ | Compelling clinical evidence |
| LEVEL_3B | ★★☆ | Different tumor type |
| LEVEL_4 | ★☆☆ | Biological evidence |
| LEVEL_R1 | Resistance | FDA-approved resistance marker |
| LEVEL_R2 | Resistance | Compelling resistance evidence |

### 2.6 cBioPortal Cross-Study Analysis (NEW)

Aggregate mutation data across multiple cancer studies:

```python
def get_cbioportal_mutations(tu, gene_symbols, study_id="brca_tcga"):
    """
    Get mutation data from cBioPortal across cancer studies.
    
    Provides: Mutation types, protein changes, co-mutations.
    """
    
    # Get mutations for genes in study
    mutations = tu.tools.cBioPortal_get_mutations(
        study_id=study_id,
        gene_list=",".join(gene_symbols)  # e.g., "EGFR,KRAS"
    )
    
    # Parse results
    results = []
    for mut in mutations or []:
        results.append({
            'gene': mut.get('gene', {}).get('hugoGeneSymbol'),
            'protein_change': mut.get('proteinChange'),
            'mutation_type': mut.get('mutationType'),
            'sample_id': mut.get('sampleId'),
            'validation_status': mut.get('validationStatus')
        })
    
    return results

def get_cbioportal_cancer_studies(tu, cancer_type=None):
    """Get available cancer studies from cBioPortal."""
    
    studies = tu.tools.cBioPortal_get_cancer_studies(limit=50)
    
    if cancer_type:
        studies = [s for s in studies if cancer_type.lower() in s.get('cancerTypeId', '').lower()]
    
    return studies

def analyze_co_mutations(tu, gene_symbol, study_id):
    """Find frequently co-mutated genes."""
    
    # Get molecular profiles
    profiles = tu.tools.cBioPortal_get_molecular_profiles(study_id=study_id)
    
    # Get mutation data
    mutations = tu.tools.cBioPortal_get_mutations(
        study_id=study_id,
        gene_list=gene_symbol
    )
    
    return {
        'profiles': profiles,
        'mutations': mutations,
        'study_id': study_id
    }
```

**cBioPortal Use Cases**:
| Use Case | Tool | Parameters |
|----------|------|------------|
| Find mutation frequency | `cBioPortal_get_mutations` | `study_id`, `gene_list` |
| List available studies | `cBioPortal_get_cancer_studies` | `limit` |
| Get molecular profiles | `cBioPortal_get_molecular_profiles` | `study_id` |
| Analyze co-mutations | Multiple tools | Combined analysis |

### 2.7 Human Protein Atlas Expression (NEW)

Validate target expression in tumor vs normal tissues:

```python
def get_hpa_expression(tu, gene_symbol):
    """
    Get protein expression data from Human Protein Atlas.
    
    Critical for validating:
    - Target is expressed in tumor tissue
    - Target has differential tumor vs normal expression
    """
    
    # Search for gene
    gene_info = tu.tools.HPA_search_genes_by_query(search_query=gene_symbol)
    
    if not gene_info:
        return None
    
    # Get tissue expression data
    ensembl_id = gene_info[0].get('Ensembl') if gene_info else None
    
    # Comparative expression in cancer cell lines
    cell_line_data = tu.tools.HPA_get_comparative_expression_by_gene_and_cellline(
        gene_name=gene_symbol,
        cell_line="a549"  # Lung cancer cell line
    )
    
    return {
        'gene_info': gene_info,
        'cell_line_expression': cell_line_data
    }

def check_tumor_specific_expression(tu, gene_symbol, cancer_type):
    """Check if target has tumor-specific expression pattern."""
    
    # Map cancer type to cell line
    cancer_to_cellline = {
        'lung': 'a549',
        'breast': 'mcf7',
        'liver': 'hepg2',
        'cervical': 'hela',
        'prostate': 'pc3'
    }
    
    cell_line = cancer_to_cellline.get(cancer_type.lower(), 'a549')
    
    expression = tu.tools.HPA_get_comparative_expression_by_gene_and_cellline(
        gene_name=gene_symbol,
        cell_line=cell_line
    )
    
    return expression
```

**HPA Expression Validation Output**:
```markdown
### Expression Validation (Human Protein Atlas)

| Gene | Tumor Cell Line | Expression | Normal Tissue | Differential |
|------|-----------------|------------|---------------|--------------|
| EGFR | A549 (lung) | High | Low-Medium | Tumor-elevated |
| ALK | H3122 (lung) | High | Not detected | Tumor-specific |
| HER2 | MCF7 (breast) | Medium | Low | Elevated |

*Source: Human Protein Atlas via `HPA_get_comparative_expression_by_gene_and_cellline`*
```

### 2.8 Evidence Level Mapping

| CIViC Level | Our Tier | Meaning |
|-------------|----------|---------|
| A | ★★★ | FDA-approved, guideline |
| B | ★★☆ | Clinical evidence |
| C | ★★☆ | Case study |
| D | ★☆☆ | Preclinical |
| E | ☆☆☆ | Inferential |

### 2.4 Output Table

```markdown
## Variant Interpretation

| Variant | Gene | Significance | Evidence Level | Clinical Implication |
|---------|------|--------------|----------------|---------------------|
| L858R | EGFR | Oncogenic driver | ★★★ (Level A) | Sensitive to EGFR TKIs |
| T790M | EGFR | Resistance | ★★★ (Level A) | Resistant to 1st/2nd gen TKIs |

### COSMIC Mutation Frequency

| Gene | Mutation | COSMIC Count | Primary Cancer Types | FATHMM Prediction |
|------|----------|--------------|---------------------|-------------------|
| EGFR | L858R | 15,234 | Lung (85%), Colorectal (5%) | Pathogenic |
| EGFR | T790M | 8,567 | Lung (95%) | Pathogenic |
| BRAF | V600E | 45,678 | Melanoma (50%), Colorectal (15%) | Pathogenic |

### TCGA/GDC Patient Tumor Data (NEW)

| Gene | TCGA Project | SSM Cases | CNV Amp | CNV Del | % Samples |
|------|-------------|-----------|---------|---------|-----------|
| EGFR | TCGA-LUAD | 156 | 89 | 5 | 28% |
| EGFR | TCGA-GBM | 45 | 312 | 2 | 57% |
| KRAS | TCGA-PAAD | 134 | 8 | 1 | 92% |

*Source: GDC via `GDC_get_mutation_frequency`, `GDC_get_cnv_data`*

### DepMap Target Essentiality (NEW)

| Gene | Mean Effect (All) | Mean Effect (Cancer Type) | Selectivity | Interpretation |
|------|-------------------|---------------------------|-------------|----------------|
| EGFR | -0.15 | -0.45 (lung) | Cancer-selective | Good target |
| KRAS | -0.82 | -0.91 (pancreatic) | Essential | Hard to target |
| MYC | -0.95 | -0.93 | Pan-essential | Challenging target |

*Effect score <-0.5 = strongly essential for cell survival*
*Source: DepMap via `DepMap_get_gene_dependencies`*

*Combined Sources: CIViC, ClinVar, COSMIC, GDC/TCGA, DepMap*
```

---

## Phase 2.5: Tumor Expression Context (NEW)

### 2.5.1 Cell-Type Expression in Tumor (CELLxGENE)

```python
def get_tumor_expression_context(tu, gene_symbol, cancer_type):
    """Get cell-type specific expression in tumor microenvironment."""
    
    # Get expression in tumor and normal cells
    expression = tu.tools.CELLxGENE_get_expression_data(
        gene=gene_symbol,
        tissue=cancer_type  # e.g., "lung", "breast"
    )
    
    # Cell metadata for context
    cell_metadata = tu.tools.CELLxGENE_get_cell_metadata(
        gene=gene_symbol
    )
    
    # Identify tumor vs normal expression
    tumor_expression = [c for c in expression if 'tumor' in c.get('cell_type', '').lower()]
    normal_expression = [c for c in expression if 'normal' in c.get('cell_type', '').lower()]
    
    return {
        'tumor_expression': tumor_expression,
        'normal_expression': normal_expression,
        'ratio': calculate_tumor_normal_ratio(tumor_expression, normal_expression)
    }
```

**Why it matters**: 
- Confirms target is expressed in tumor cells (not just stroma)
- Identifies potential resistance from tumor heterogeneity
- Supports drug selection based on expression patterns

### 2.5.2 Output for Report

```markdown
## 2.5 Tumor Expression Context

### Target Expression in Tumor Microenvironment (CELLxGENE)

| Gene | Tumor Cells | Normal Cells | Tumor/Normal Ratio | Interpretation |
|------|-------------|--------------|-------------------|----------------|
| EGFR | High (TPM=85) | Medium (TPM=25) | 3.4x | Good target |
| MET | Medium (TPM=35) | Low (TPM=8) | 4.4x | Potential bypass |
| AXL | High (TPM=120) | Low (TPM=15) | 8.0x | Resistance marker |

### Cell Type Distribution

- **EGFR-high cells**: Tumor epithelial (85%), CAFs (10%), immune (5%)
- **MET-high cells**: Tumor epithelial (70%), endothelial (20%), immune (10%)

**Clinical Relevance**: EGFR highly expressed in tumor epithelial cells. AXL overexpression in tumor suggests potential resistance mechanism.

*Source: CELLxGENE Census*
```

---

## Phase 3: Treatment Options

### 3.1 Approved Therapies

Query order:
1. `OpenTargets_get_associated_drugs_by_target_ensemblId` → Approved drugs
2. `DailyMed_search_spls` → FDA label details
3. `ChEMBL_get_drug_mechanisms_of_action_by_chemblId` → Mechanism

### 3.2 Treatment Prioritization

| Priority | Criteria |
|----------|----------|
| **1st Line** | FDA-approved for indication + biomarker (★★★) |
| **2nd Line** | Clinical trial evidence, guideline-recommended (★★☆) |
| **3rd Line** | Off-label with mechanistic rationale (★☆☆) |

### 3.3 Output Format

```markdown
## Treatment Recommendations

### First-Line Options
**1. Osimertinib (Tagrisso)** ★★★
- FDA-approved for EGFR T790M+ NSCLC
- Evidence: AURA3 trial (ORR 71%, mPFS 10.1 mo)
- Source: FDA label, PMID:27959700

### Second-Line Options
**2. Combination: Osimertinib + [Agent]** ★★☆
- Evidence: Phase 2 data
- Source: NCT04487080
```

---

## Phase 3.5: Pathway & Network Analysis (NEW)

### 3.5.1 Pathway Context (KEGG/Reactome)

```python
def get_pathway_context(tu, gene_symbols, cancer_type):
    """Get pathway context for drug combinations and resistance."""
    
    pathway_map = {}
    for gene in gene_symbols:
        # KEGG pathways
        kegg_gene = tu.tools.kegg_find_genes(query=f"hsa:{gene}")
        if kegg_gene:
            pathways = tu.tools.kegg_get_gene_info(gene_id=kegg_gene[0]['id'])
            pathway_map[gene] = pathways.get('pathways', [])
        
        # Reactome disease score
        reactome = tu.tools.reactome_disease_target_score(
            disease=cancer_type,
            target=gene
        )
        pathway_map[f"{gene}_reactome"] = reactome
    
    return pathway_map
```

### 3.5.2 Protein Interaction Network (IntAct)

```python
def get_resistance_network(tu, drug_target, bypass_candidates):
    """Find protein interactions that may mediate resistance."""
    
    # Get interaction network for drug target
    network = tu.tools.intact_get_interaction_network(
        gene=drug_target,
        depth=2  # Include 2nd degree connections
    )
    
    # Find bypass pathway candidates in network
    bypass_in_network = [
        node for node in network['nodes']
        if node['gene'] in bypass_candidates
    ]
    
    return {
        'network': network,
        'bypass_connections': bypass_in_network,
        'total_interactors': len(network['nodes'])
    }
```

### 3.5.3 Output for Report

```markdown
## 3.5 Pathway & Network Analysis

### Signaling Pathway Context (KEGG)

| Pathway | Genes Involved | Relevance | Drug Targets |
|---------|---------------|-----------|--------------|
| EGFR signaling (hsa04012) | EGFR, MET, ERBB3 | Primary pathway | Osimertinib, Capmatinib |
| PI3K-AKT (hsa04151) | PIK3CA, AKT1 | Downstream | Alpelisib |
| RAS-MAPK (hsa04010) | KRAS, BRAF, MEK | Bypass potential | Sotorasib, Trametinib |

### Drug Combination Rationale

**Biological basis for combinations**:
- EGFR inhibition → compensatory MET activation (60% of cases)
- **Rationale for EGFR + MET inhibition**: Block primary and bypass pathways
- Network shows direct EGFR-MET interaction (IntAct: MI-score 0.75)

### Protein Interaction Network (IntAct)

| Target | Direct Interactors | Key Partners | Relevance |
|--------|-------------------|--------------|-----------|
| EGFR | 156 | MET, ERBB2, ERBB3, GRB2 | Bypass pathways |
| MET | 89 | EGFR, HGF, GAB1 | Resistance mediator |

*Source: KEGG, Reactome, IntAct*
```

---

## Phase 4: Resistance Analysis

### 4.1 Known Mechanisms (Literature + CIViC)

```python
def analyze_resistance(tu, drug_name, gene_symbol):
    """Find known resistance mechanisms."""
    # CIViC resistance evidence
    resistance = tu.tools.civic_search_evidence_items(
        drug=drug_name,
        evidence_type="Predictive",
        clinical_significance="Resistance"
    )
    
    # Literature search
    papers = tu.tools.PubMed_search_articles(
        query=f'"{drug_name}" AND "{gene_symbol}" AND resistance',
        limit=20
    )
    
    return {'civic': resistance, 'literature': papers}
```

### 4.2 Structure-Based Analysis (NvidiaNIM)

When mutation affects drug binding:

```python
def model_resistance_mechanism(tu, gene_ids, mutation, drug_smiles):
    """Model structural impact of resistance mutation."""
    # Get/predict structure
    structure = tu.tools.NvidiaNIM_alphafold2(sequence=wild_type_sequence)
    
    # Dock drug to wild-type
    wt_docking = tu.tools.NvidiaNIM_diffdock(
        protein=structure['structure'],
        ligand=drug_smiles,
        num_poses=5
    )
    
    # Compare binding site changes
    # Report: "T790M introduces bulky methionine, steric clash with erlotinib"
```

---

## Phase 5: Clinical Trial Matching

### 5.1 Search Strategy

```python
def find_trials(tu, condition, biomarker, location=None):
    """Find matching clinical trials."""
    # Search with biomarker
    trials = tu.tools.search_clinical_trials(
        condition=condition,
        intervention=biomarker,  # e.g., "EGFR"
        status="Recruiting",
        pageSize=50
    )
    
    # Get eligibility for top matches
    nct_ids = [t['nct_id'] for t in trials[:20]]
    eligibility = tu.tools.get_clinical_trial_eligibility_criteria(nct_ids=nct_ids)
    
    return trials, eligibility
```

### 5.2 Output Format

```markdown
## Clinical Trial Options

| NCT ID | Phase | Agent | Biomarker Required | Status | Location |
|--------|-------|-------|-------------------|--------|----------|
| NCT04487080 | 2 | Amivantamab + lazertinib | EGFR T790M | Recruiting | US, EU |
| NCT05388669 | 3 | Patritumab deruxtecan | Prior osimertinib | Recruiting | US |

*Source: ClinicalTrials.gov*
```

---

## Phase 5.5: Literature Evidence (NEW)

### 5.5.1 Published Literature (PubMed)

```python
def search_treatment_literature(tu, cancer_type, biomarker, drug_name):
    """Search for treatment evidence in literature."""
    
    # Drug + biomarker combination
    drug_papers = tu.tools.PubMed_search_articles(
        query=f'"{drug_name}" AND "{biomarker}" AND "{cancer_type}"',
        limit=20
    )
    
    # Resistance mechanisms
    resistance_papers = tu.tools.PubMed_search_articles(
        query=f'"{drug_name}" AND resistance AND mechanism',
        limit=15
    )
    
    return {
        'treatment_evidence': drug_papers,
        'resistance_literature': resistance_papers
    }
```

### 5.5.2 Preprints (BioRxiv/MedRxiv)

```python
def search_preprints(tu, cancer_type, biomarker):
    """Search preprints for cutting-edge findings."""
    
    # BioRxiv cancer research
    biorxiv = tu.tools.BioRxiv_search_preprints(
        query=f"{cancer_type} {biomarker} treatment",
        limit=10
    )
    
    # MedRxiv clinical studies
    medrxiv = tu.tools.MedRxiv_search_preprints(
        query=f"{cancer_type} {biomarker}",
        limit=10
    )
    
    return {
        'biorxiv': biorxiv,
        'medrxiv': medrxiv
    }
```

### 5.5.3 Citation Analysis (OpenAlex)

```python
def analyze_key_papers(tu, key_papers):
    """Get citation metrics for key evidence papers."""
    
    analyzed = []
    for paper in key_papers[:10]:
        work = tu.tools.openalex_search_works(
            query=paper['title'],
            limit=1
        )
        if work:
            analyzed.append({
                'title': paper['title'],
                'citations': work[0].get('cited_by_count', 0),
                'year': work[0].get('publication_year'),
                'open_access': work[0].get('is_oa', False)
            })
    
    return analyzed
```

### 5.5.4 Output for Report

```markdown
## 5.5 Literature Evidence

### Key Clinical Studies

| PMID | Title | Year | Citations | Evidence Type |
|------|-------|------|-----------|---------------|
| 27959700 | AURA3: Osimertinib vs chemotherapy... | 2017 | 2,450 | Phase 3 trial |
| 30867819 | Mechanisms of osimertinib resistance... | 2019 | 680 | Review |
| 34125020 | Amivantamab + lazertinib Phase 1... | 2021 | 320 | Phase 1 trial |

### Recent Preprints (Not Peer-Reviewed)

| Source | Title | Posted | Key Finding |
|--------|-------|--------|-------------|
| MedRxiv | Novel C797S resistance strategy... | 2024-01 | Fourth-gen TKI |
| BioRxiv | scRNA-seq reveals resistance... | 2024-02 | Cell state switch |

**⚠️ Note**: Preprints have NOT undergone peer review. Interpret with caution.

### Evidence Summary

| Category | Papers Found | High-Impact (>100 citations) |
|----------|--------------|------------------------------|
| Treatment efficacy | 25 | 8 |
| Resistance mechanisms | 18 | 5 |
| Combinations | 12 | 3 |

*Source: PubMed, BioRxiv, MedRxiv, OpenAlex*
```

---

## Report Template

**File**: `[PATIENT_ID]_oncology_report.md`

```markdown
# Precision Oncology Report

**Patient ID**: [ID] | **Date**: [Date]

## Patient Profile
- **Diagnosis**: [Cancer type, stage]
- **Molecular Profile**: [Mutations, fusions]
- **Prior Therapy**: [Previous treatments]

---

## Executive Summary
[2-3 sentence summary of key findings and recommendation]

---

## 1. Variant Interpretation
[Table with variants, significance, evidence levels]

## 2. Treatment Recommendations
### First-Line Options
[Prioritized list with evidence]

### Second-Line Options
[Alternative approaches]

## 3. Resistance Analysis (if applicable)
[Mechanism explanation, strategies to overcome]

## 4. Clinical Trial Options
[Matched trials with eligibility]

## 5. Next Steps
1. [Specific actionable recommendation]
2. [Follow-up testing if needed]
3. [Referral if appropriate]

---

## Data Sources
| Source | Query | Data Retrieved |
|--------|-------|----------------|
| CIViC | [gene] [variant] | Evidence items |
| ClinicalTrials.gov | [condition] | Active trials |
```

---

## Completeness Checklist

Before finalizing report:

- [ ] All variants interpreted with evidence levels
- [ ] ≥1 first-line recommendation with ★★★ evidence (or explain why none)
- [ ] Resistance mechanism addressed (if prior therapy failed)
- [ ] ≥3 clinical trials listed (or "no matching trials")
- [ ] Executive summary is actionable (says what to DO)
- [ ] All recommendations have source citations

---

## Fallback Chains

| Primary | Fallback | Use When |
|---------|----------|----------|
| CIViC variant | OncoKB (literature) | Variant not in CIViC |
| OpenTargets drugs | ChEMBL activities | No approved drugs found |
| ClinicalTrials.gov | WHO ICTRP | US trials insufficient |
| NvidiaNIM_alphafold2 | AlphaFold DB | API unavailable |

---

## Evidence Grading

| Tier | Symbol | Criteria | Example |
|------|--------|----------|---------|
| T1 | ★★★ | FDA-approved, Level A evidence | Osimertinib for T790M |
| T2 | ★★☆ | Phase 2/3 data, Level B | Combination trials |
| T3 | ★☆☆ | Preclinical, Level D | Novel mechanisms |
| T4 | ☆☆☆ | Computational only | Docking predictions |

---

## Tool Reference

See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) for complete tool documentation.
