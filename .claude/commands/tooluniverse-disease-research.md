# tooluniverse-disease-research

> Generate comprehensive disease research reports using 100+ ToolUniverse tools. Creates a detailed markdown report file and progressively updates it with findings from 10 research dimensions. All information includes source references. Use when users ask about diseases, syndromes, or need systematic disease analysis.

# ToolUniverse Disease Research

Generate a comprehensive, detailed disease research report with full source citations. The report is created as a markdown file and progressively updated during research.

**IMPORTANT**: Always use English disease names and search terms in tool calls, even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

## When to Use

Apply when the user:
- Asks about any disease, syndrome, or medical condition
- Needs comprehensive disease intelligence
- Wants a detailed research report with citations
- Asks "what do we know about [disease]?"

## Core Workflow: Report-First Approach

**DO NOT** show the search process to the user. Instead:

1. **Create report file first** - Initialize `{disease_name}_research_report.md`
2. **Research each dimension** - Use all relevant tools
3. **Update report progressively** - Write findings to file after each dimension
4. **Include citations** - Every fact must reference its source tool

```
User: "Research Parkinson's disease"

Agent Actions (internal, not shown to user):
1. Create "parkinsons_disease_research_report.md" with template
2. Research DIM 1 → Update Identity section
3. Research DIM 2 → Update Clinical section
4. ... continue for all 10 dimensions
5. Present final report to user
```

## Report Template

Create this file structure at the start:

```markdown
# Disease Research Report: {Disease Name}

**Report Generated**: {date}
**Disease Identifiers**: (to be filled)

---

## Executive Summary

(Brief 3-5 sentence overview - fill after all research complete)

---

## 1. Disease Identity & Classification

### Ontology Identifiers
| System | ID | Source |
|--------|-----|--------|
| EFO | | |
| ICD-10 | | |
| UMLS CUI | | |
| SNOMED CT | | |

### Synonyms & Alternative Names
- (list with source)

### Disease Hierarchy
- Parent: 
- Subtypes:

**Sources**: (list tools used)

---

## 2. Clinical Presentation

### Phenotypes (HPO)
| HPO ID | Phenotype | Description | Source |
|--------|-----------|-------------|--------|

### Symptoms & Signs
- (list with source)

### Diagnostic Criteria
- (from literature/MedlinePlus)

**Sources**: (list tools used)

---

## 3. Genetic & Molecular Basis

### Associated Genes
| Gene | Score | Ensembl ID | Evidence | Source |
|------|-------|------------|----------|--------|

### GWAS Associations
| SNP | P-value | Odds Ratio | Study | Source |
|-----|---------|------------|-------|--------|

### Pathogenic Variants (ClinVar)
| Variant | Clinical Significance | Condition | Source |
|---------|----------------------|-----------|--------|

**Sources**: (list tools used)

---

## 4. Treatment Landscape

### Approved Drugs
| Drug | ChEMBL ID | Mechanism | Phase | Target | Source |
|------|-----------|-----------|-------|--------|--------|

### Clinical Trials
| NCT ID | Title | Phase | Status | Intervention | Source |
|--------|-------|-------|--------|--------------|--------|

### Treatment Guidelines
- (from literature)

**Sources**: (list tools used)

---

## 5. Biological Pathways & Mechanisms

### Key Pathways
| Pathway | Reactome ID | Genes Involved | Source |
|---------|-------------|----------------|--------|

### Protein-Protein Interactions
- (tissue-specific networks)

### Expression Patterns
| Tissue | Expression Level | Source |
|--------|------------------|--------|

**Sources**: (list tools used)

---

## 6. Epidemiology & Risk Factors

### Prevalence & Incidence
- (from literature)

### Risk Factors
| Factor | Evidence | Source |
|--------|----------|--------|

### GWAS Studies
| Study | Sample Size | Findings | Source |
|-------|-------------|----------|--------|

**Sources**: (list tools used)

---

## 7. Literature & Research Activity

### Publication Trends
- Total publications (5 years): 
- Current year: 
- Trend: 

### Key Publications
| PMID | Title | Year | Citations | Source |
|------|-------|------|-----------|--------|

### Research Institutions
- (from OpenAlex)

**Sources**: (list tools used)

---

## 8. Similar Diseases & Comorbidities

### Similar Diseases
| Disease | Similarity Score | Shared Genes | Source |
|---------|-----------------|--------------|--------|

### Comorbidities
- (from literature/clinical data)

**Sources**: (list tools used)

---

## 9. Cancer-Specific Information (if applicable)

### CIViC Variants
| Gene | Variant | Evidence Level | Clinical Significance | Source |
|------|---------|----------------|----------------------|--------|

### Molecular Profiles
- (biomarkers)

### Targeted Therapies
| Therapy | Target | Evidence | Source |
|---------|--------|----------|--------|

**Sources**: (list tools used)

---

## 10. Drug Safety & Adverse Events

### Drug Warnings
| Drug | Warning Type | Description | Source |
|------|--------------|-------------|--------|

### Clinical Trial Adverse Events
| Trial | Drug | Adverse Event | Frequency | Source |
|-------|------|---------------|-----------|--------|

### FAERS Reports
- (FDA adverse event data)

**Sources**: (list tools used)

---

## References

### Data Sources Used
| Tool | Query | Section |
|------|-------|---------|

### Database Versions
- OpenTargets: (version/date)
- ClinVar: (version/date)
- GWAS Catalog: (version/date)
```

---

## Research Protocol

### Step 1: Initialize Report

```python
from datetime import datetime

def create_report_file(disease_name):
    """Create initial report file with template"""
    filename = f"{disease_name.lower().replace(' ', '_')}_research_report.md"
    
    template = f"""# Disease Research Report: {disease_name}

**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Disease Identifiers**: Pending research...

---

## Executive Summary

*Research in progress...*

---

## 1. Disease Identity & Classification
*Researching...*

## 2. Clinical Presentation
*Pending...*

[... rest of template ...]
"""
    
    with open(filename, 'w') as f:
        f.write(template)
    
    return filename
```

### Step 2: Research Each Dimension with Citations

For EACH piece of information, track:
- **Tool name** that provided the data
- **Parameters** used in the query
- **Timestamp** of the query

```python
def research_with_citations(tu, disease_name, report_file):
    """Research and update report with full citations"""
    
    references = []  # Track all sources
    
    # === DIMENSION 1: Identity ===
    
    # Get EFO ID
    efo_result = tu.tools.OSL_get_efo_id_by_disease_name(disease=disease_name)
    efo_id = efo_result.get('efo_id')
    references.append({
        'tool': 'OSL_get_efo_id_by_disease_name',
        'params': {'disease': disease_name},
        'section': 'Identity'
    })
    
    # Get ICD codes
    icd_result = tu.tools.icd_search_codes(query=disease_name, version="ICD10CM")
    references.append({
        'tool': 'icd_search_codes',
        'params': {'query': disease_name, 'version': 'ICD10CM'},
        'section': 'Identity'
    })
    
    # Get UMLS
    umls_result = tu.tools.umls_search_concepts(query=disease_name)
    references.append({
        'tool': 'umls_search_concepts',
        'params': {'query': disease_name},
        'section': 'Identity'
    })
    
    # Get synonyms from EFO
    if efo_id:
        efo_term = tu.tools.ols_get_efo_term(obo_id=efo_id.replace('_', ':'))
        references.append({
            'tool': 'ols_get_efo_term',
            'params': {'obo_id': efo_id},
            'section': 'Identity'
        })
        
        # Get subtypes
        children = tu.tools.ols_get_efo_term_children(obo_id=efo_id.replace('_', ':'), size=20)
        references.append({
            'tool': 'ols_get_efo_term_children',
            'params': {'obo_id': efo_id, 'size': 20},
            'section': 'Identity'
        })
    
    # UPDATE REPORT FILE with Identity section
    update_report_section(report_file, 'Identity', {
        'efo_id': efo_id,
        'icd_codes': icd_result,
        'umls': umls_result,
        'synonyms': efo_term.get('synonyms', []) if efo_term else [],
        'subtypes': children
    }, references[-5:])  # Last 5 references for this section
    
    # === DIMENSION 2: Clinical ===
    # ... continue for all dimensions
```

### Step 3: Update Report File After Each Dimension

```python
def update_report_section(filename, section_name, data, sources):
    """Update a specific section in the report file"""
    
    # Read current file
    with open(filename, 'r') as f:
        content = f.read()
    
    # Format section content with citations
    if section_name == 'Identity':
        section_content = format_identity_section(data, sources)
    elif section_name == 'Clinical':
        section_content = format_clinical_section(data, sources)
    # ... etc
    
    # Replace placeholder with actual content
    placeholder = f"## {section_number}. {section_name}\n*Researching...*"
    content = content.replace(placeholder, section_content)
    
    # Write back
    with open(filename, 'w') as f:
        f.write(content)


def format_identity_section(data, sources):
    """Format Identity section with proper citations"""
    
    source_list = ', '.join([s['tool'] for s in sources])
    
    return f"""## 1. Disease Identity & Classification

### Ontology Identifiers
| System | ID | Source |
|--------|-----|--------|
| EFO | {data['efo_id']} | OSL_get_efo_id_by_disease_name |
| ICD-10 | {data['icd_codes']} | icd_search_codes |
| UMLS CUI | {data['umls']} | umls_search_concepts |

### Synonyms & Alternative Names
{format_list_with_source(data['synonyms'], 'ols_get_efo_term')}

### Disease Subtypes
{format_list_with_source(data['subtypes'], 'ols_get_efo_term_children')}

**Sources**: {source_list}
"""
```

---

## Complete Tool Usage by Section

### Section 1: Identity (use ALL of these)
```python
# Required tools - use all
tu.tools.OSL_get_efo_id_by_disease_name(disease=disease_name)
tu.tools.OpenTargets_get_disease_id_description_by_name(diseaseName=disease_name)
tu.tools.ols_search_efo_terms(query=disease_name)
tu.tools.ols_get_efo_term(obo_id=efo_id)
tu.tools.ols_get_efo_term_children(obo_id=efo_id, size=30)
tu.tools.umls_search_concepts(query=disease_name)
tu.tools.umls_get_concept_details(cui=cui)
tu.tools.icd_search_codes(query=disease_name, version="ICD10CM")
tu.tools.snomed_search_concepts(query=disease_name)
```

### Section 2: Clinical Presentation (use ALL of these)
```python
tu.tools.OpenTargets_get_associated_phenotypes_by_disease_efoId(efoId=efo_id)
tu.tools.get_HPO_ID_by_phenotype(query=symptom)  # for each key symptom
tu.tools.get_phenotype_by_HPO_ID(id=hpo_id)  # for top phenotypes
tu.tools.MedlinePlus_search_topics_by_keyword(term=disease_name, db="healthTopics")
tu.tools.MedlinePlus_get_genetics_condition_by_name(condition=disease_slug)
tu.tools.MedlinePlus_connect_lookup_by_code(cs=icd_oid, c=icd_code)
```

### Section 3: Genetics (use ALL of these)
```python
tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId=efo_id)
tu.tools.OpenTargets_target_disease_evidence(efoId=efo_id, ensemblId=gene_id)  # for top genes
tu.tools.clinvar_search_variants(condition=disease_name, max_results=50)
tu.tools.clinvar_get_variant_details(variant_id=vid)  # for top variants
tu.tools.clinvar_get_clinical_significance(variant_id=vid)
tu.tools.gwas_search_associations(disease_trait=disease_name, size=50)
tu.tools.gwas_get_variants_for_trait(disease_trait=disease_name, size=50)
tu.tools.gwas_get_associations_for_trait(disease_trait=disease_name, size=50)
tu.tools.gwas_get_studies_for_trait(disease_trait=disease_name, size=30)
tu.tools.GWAS_search_associations_by_gene(gene_name=gene)  # for top genes
tu.tools.gnomad_get_variant_frequency(variant=variant)  # for key variants
```

### Section 4: Treatment (use ALL of these)
```python
tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=efo_id, size=100)
tu.tools.OpenTargets_get_drug_chembId_by_generic_name(drugName=drug)  # for each drug
tu.tools.OpenTargets_get_drug_mechanisms_of_action_by_chemblId(chemblId=chembl_id)
tu.tools.search_clinical_trials(condition=disease_name, pageSize=50)
tu.tools.get_clinical_trial_descriptions(nct_ids=nct_list)
tu.tools.get_clinical_trial_conditions_and_interventions(nct_ids=nct_list)
tu.tools.get_clinical_trial_eligibility_criteria(nct_ids=nct_list)
tu.tools.get_clinical_trial_outcome_measures(nct_ids=nct_list)
tu.tools.extract_clinical_trial_outcomes(nct_ids=nct_list)
tu.tools.GtoPdb_list_diseases(name=disease_name)
tu.tools.GtoPdb_get_disease(disease_id=gtopdb_id)
```

### Section 5: Pathways (use ALL of these)
```python
tu.tools.Reactome_get_diseases()
tu.tools.Reactome_map_uniprot_to_pathways(id=uniprot_id)  # for top genes
tu.tools.Reactome_get_pathway(stId=pathway_id)  # for key pathways
tu.tools.Reactome_get_pathway_reactions(stId=pathway_id)
tu.tools.humanbase_ppi_analysis(gene_list=top_genes, tissue=relevant_tissue)
tu.tools.gtex_get_expression_by_gene(gene=gene)  # for top genes
tu.tools.HPA_get_protein_expression(gene=gene)
tu.tools.geo_search_datasets(query=disease_name)
```

### Section 6: Literature (use ALL of these)
```python
tu.tools.PubMed_search_articles(query=f'"{disease_name}"', limit=100)
tu.tools.PubMed_search_articles(query=f'"{disease_name}" AND epidemiology', limit=50)
tu.tools.PubMed_search_articles(query=f'"{disease_name}" AND mechanism', limit=50)
tu.tools.PubMed_search_articles(query=f'"{disease_name}" AND treatment', limit=50)
tu.tools.PubMed_get_article(pmid=pmid)  # for top 10 articles
tu.tools.PubMed_get_related(pmid=key_pmid)
tu.tools.PubMed_get_cited_by(pmid=key_pmid)
tu.tools.OpenTargets_get_publications_by_disease_efoId(efoId=efo_id)
tu.tools.openalex_search_works(query=disease_name, limit=50)
tu.tools.europe_pmc_search_abstracts(query=disease_name, limit=50)
tu.tools.semantic_scholar_search_papers(query=disease_name, limit=50)
```

### Section 7: Similar Diseases
```python
tu.tools.OpenTargets_get_similar_entities_by_disease_efoId(efoId=efo_id, threshold=0.3, size=30)
```

### Section 8: Cancer-Specific (if cancer)
```python
tu.tools.civic_search_diseases(limit=100)
tu.tools.civic_search_genes(query=gene, limit=20)  # for cancer genes
tu.tools.civic_get_variants_by_gene(gene_id=civic_gene_id, limit=50)
tu.tools.civic_get_variant(variant_id=vid)
tu.tools.civic_get_evidence_item(evidence_id=eid)
tu.tools.civic_search_therapies(limit=100)
tu.tools.civic_search_molecular_profiles(limit=50)
```

### Section 9: Pharmacology
```python
tu.tools.GtoPdb_get_targets(target_type=type, limit=50)  # GPCR, ion channel, etc
tu.tools.GtoPdb_get_target(target_id=tid)  # for disease-relevant targets
tu.tools.GtoPdb_get_target_interactions(target_id=tid)
tu.tools.GtoPdb_search_interactions(approved_only=True)
tu.tools.GtoPdb_list_ligands(ligand_type="Approved")
```

### Section 10: Safety (use ALL of these)
```python
tu.tools.OpenTargets_get_drug_warnings_by_chemblId(chemblId=cid)  # for each drug
tu.tools.OpenTargets_get_drug_blackbox_status_by_chembl_ID(chemblId=cid)
tu.tools.extract_clinical_trial_adverse_events(nct_ids=nct_list)
tu.tools.FAERS_count_reactions_by_drug_event(drug=drug_name, event=event)
tu.tools.AdverseEventPredictionQuestionGenerator(disease_name=disease, drug_name=drug)
```

---

## Citation Format

Every piece of data MUST include its source. Use this format:

### In Tables
```markdown
| Gene | Score | Source |
|------|-------|--------|
| APOE | 0.92 | OpenTargets_get_associated_targets_by_disease_efoId |
| APP | 0.88 | OpenTargets_get_associated_targets_by_disease_efoId |
```

### In Lists
```markdown
- Memory loss [Source: OpenTargets_get_associated_phenotypes_by_disease_efoId]
- Cognitive decline [Source: MedlinePlus_get_genetics_condition_by_name]
```

### In Prose
```markdown
The disease affects approximately 6.5 million Americans (Source: PubMed_search_articles, 
query: "Alzheimer disease epidemiology").
```

### References Section
At the end of the report, include complete tool usage log:

```markdown
## References

### Tools Used
| # | Tool | Parameters | Section | Items Retrieved |
|---|------|------------|---------|-----------------|
| 1 | OSL_get_efo_id_by_disease_name | disease="Alzheimer disease" | Identity | 1 |
| 2 | ols_get_efo_term | obo_id="EFO:0000249" | Identity | 1 |
| 3 | OpenTargets_get_associated_targets_by_disease_efoId | efoId="EFO_0000249" | Genetics | 245 |
| ... | ... | ... | ... | ... |

### Data Retrieved Summary
- Total tools used: 45
- Total API calls: 78
- Sections completed: 10/10
```

---

## Progressive Update Pattern

After researching EACH dimension, immediately update the report file:

```python
# After each dimension's research completes:

# 1. Read current report
with open(report_file, 'r') as f:
    report = f.read()

# 2. Replace placeholder with formatted content
report = report.replace(
    "## 3. Genetic & Molecular Basis\n*Pending...*",
    formatted_genetics_section
)

# 3. Write back immediately
with open(report_file, 'w') as f:
    f.write(report)

# 4. Continue to next dimension
```

---

## Final Report Quality Checklist

Before presenting to user, verify:

- [ ] All 10 sections have content (or marked as "No data available")
- [ ] Every data point has a source citation
- [ ] Executive summary reflects key findings
- [ ] References section lists all tools used
- [ ] Tables are properly formatted
- [ ] No placeholder text remains

---

## Example Output Structure

For "Alzheimer's Disease" research, the final report should be 2000+ lines with:

- **Section 1**: 5+ ontology IDs, 10+ synonyms, disease hierarchy
- **Section 2**: 20+ phenotypes with HPO IDs, symptoms list
- **Section 3**: 50+ genes with scores, 30+ GWAS associations, 100+ ClinVar variants
- **Section 4**: 20+ drugs, 50+ clinical trials with details
- **Section 5**: 10+ pathways, PPI network, expression data
- **Section 6**: 100+ publications, citation analysis, institution list
- **Section 7**: 15+ similar diseases with similarity scores
- **Section 8**: (if cancer) variants, evidence items
- **Section 9**: Pharmacological targets and interactions
- **Section 10**: Drug warnings, adverse events

Total: Detailed report with 500+ individual data points, each with source citation.

---

## Tool Reference

See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) for complete tool documentation.
See [EXAMPLES.md](EXAMPLES.md) for sample reports.
