# tooluniverse-clinical-guidelines

> Search and retrieve clinical practice guidelines across 12+ authoritative sources including NICE, WHO, ADA, AHA/ACC, NCCN, SIGN, CPIC, CMA, CTFPHC, GIN, MAGICapp, PubMed, EuropePMC, TRIP, and OpenAlex. Covers disease management, cardiology, oncology, diabetes, pharmacogenomics, and more. Use when users ask about clinical guidelines, treatment recommendations, standard of care, evidence-based medicine, or drug-gene dosing recommendations.

# Clinical Guidelines Search & Retrieval

Search and retrieve evidence-based clinical practice guidelines from 12+ authoritative sources spanning 41 tools. Covers disease management guidelines, society recommendations, pharmacogenomics guidance, and patient resources.

**KEY PRINCIPLES**:
1. **Multi-source search** — Search ≥3 databases in parallel for comprehensive coverage
2. **Source-appropriate queries** — Match query style to each database's strengths
3. **Condition + society specific** — When user names a disease or society, use targeted tools
4. **English queries first** — Use English medical terms in all tool calls; respond in user's language
5. **Cite sources** — Every guideline result must include source organization and URL

---

## When to Use

Apply when user asks:
- "What are the guidelines for [condition]?"
- "What does [ADA/AHA/NCCN/NICE/WHO] say about [topic]?"
- "Standard of care for [disease]?"
- "Drug-gene interactions for [drug/gene]?" (pharmacogenomics)
- "Screening recommendations for [condition]?"
- "Is there a guideline for [clinical question]?"
- "What do guidelines say about [treatment/drug]?"
- "Clinical recommendations for [oncology topic]?"

---

## Phase 0: Tool Verification (MANDATORY FIRST STEP)

Before searching, verify tools load:

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()
assert hasattr(tu.tools, 'NICE_Clinical_Guidelines_Search')
```

**Correct call pattern** (use either approach):
```python
# Option A: direct attribute access
result = tu.tools.NICE_Clinical_Guidelines_Search(query='diabetes', limit=5)

# Option B: run_one_function
result = tu.run_one_function({'name': 'NICE_Clinical_Guidelines_Search', 'arguments': {'query': 'diabetes', 'limit': 5}})
```

---

## Phase 1: Identify Query Strategy

Determine which tools to use based on the user's question:

| Query type | Primary tools | Secondary tools |
|-----------|---------------|-----------------|
| General disease guideline | NICE, TRIP, GIN | PubMed, EuropePMC, CMA |
| Cardiology | AHA_ACC_search_guidelines, AHA_list_guidelines | NICE, TRIP |
| Oncology | NCCN_search_guidelines, NCCN_list_patient_guidelines | NICE, GIN |
| Diabetes / endocrinology | ADA_search_standards, ADA_list_standards_sections | NICE, SIGN |
| Pharmacogenomics | CPIC_get_gene_drug_pairs, CPIC_list_guidelines | CPIC_get_gene_info |
| Canadian guidelines | CMA_Guidelines_Search, CTFPHC_search_guidelines | — |
| Scottish/UK guidelines | SIGN_search_guidelines, NICE | CMA |
| International guidelines | GIN_Guidelines_Search | OpenAlex, EuropePMC |
| Living guidelines | MAGICapp_list_guidelines | GIN |
| Full-text retrieval | NICE_Guideline_Full_Text, WHO_Guideline_Full_Text, AHA_ACC_get_guideline | — |

---

## Phase 2: Multi-Source Search

### 2.1 General Search (Use ≥3 databases)

**NICE_Clinical_Guidelines_Search** ⭐ (Best general source)
- Parameters: `query` (string, required), `limit` (integer, required)
- Returns: **list** directly (NOT wrapped in dict) — `[{title, url, summary, content, date}, ...]`
- Handle: `result = tu.tools.NICE_Clinical_Guidelines_Search(...); isinstance(result, list)`
- Example: `NICE_Clinical_Guidelines_Search(query='type 2 diabetes management', limit=5)`

**GIN_Guidelines_Search** ⭐ (Best multi-society aggregator)
- Parameters: `query` (string, required), `limit` (integer, required)
- Returns: **list** directly — `[{title, url, description, source, organization}, ...]`
- Example: `GIN_Guidelines_Search(query='colorectal cancer screening', limit=5)`

**TRIP_Database_Guidelines_Search**
- Parameters: `query` (string, required), `limit` (integer, required), `search_type` (string, required — **must be `'guidelines'`**)
- Returns: **list** directly — `[{title, url, description, content, publication}, ...]`
- Example: `TRIP_Database_Guidelines_Search(query='diabetes', limit=5, search_type='guidelines')`

**WHO_Guidelines_Search** ⚠️ (Limited relevance)
- Parameters: `query` (string, required), `limit` (integer, required)
- Returns: **list** directly — `[{title, url, description, content, source}, ...]`
- **LIMITATION**: Does not reliably filter by topic. May return unrelated recent WHO publications.
- Use for broad international queries; do not rely on for specific disease searches.
- Example: `WHO_Guidelines_Search(query='diabetes', limit=5)`

**CMA_Guidelines_Search** (Canadian)
- Parameters: `query` (string, required), `limit` (integer, required)
- Returns: **list** directly — `[{title, url, description, content, date}, ...]`
- Example: `CMA_Guidelines_Search(query='diabetes', limit=5)`

**SIGN_search_guidelines** (Scottish/UK)
- Parameters: `query` (string, required — NOT `q`), `limit` (integer, optional)
- Returns: **list** directly — `[{number, title, topic, published, url}, ...]`
- Example: `SIGN_search_guidelines(query='diabetes', limit=5)`

**CTFPHC_search_guidelines** (Canadian prevention)
- Parameters: `query` (string, required — NOT `q`), `limit` (integer, optional)
- Returns: **list** directly — `[{title, url, year}, ...]`
- Example: `CTFPHC_search_guidelines(query='colorectal cancer', limit=5)`

**OpenAlex_Guidelines_Search**
- Parameters: `query` (string, required), `limit` (integer, required), `year_from` (integer, **optional**), `year_to` (integer, **optional**)
- Returns: **list** directly — `[{title, authors, institutions, year, doi}, ...]`
- Example: `OpenAlex_Guidelines_Search(query='diabetes management', limit=5)` (year params optional)
- With years: `OpenAlex_Guidelines_Search(query='diabetes management', limit=5, year_from=2020, year_to=2024)`

**EuropePMC_Guidelines_Search**
- Parameters: `query` (string, required), `limit` (integer, required)
- Returns: **list** directly — `[{title, pmid, pmcid, doi, authors}, ...]`
- Note: May return loosely relevant results; use for literature discovery not definitive guidelines
- Example: `EuropePMC_Guidelines_Search(query='diabetes guideline', limit=5)`

**PubMed_Guidelines_Search**
- Parameters: `query` (string, required), `limit` (integer, required), `api_key` (string, **optional** — use `''` for anonymous)
- Returns: **list** directly — `[{title, pmid, pmcid, doi}, ...]`
- Example: `PubMed_Guidelines_Search(query='diabetes guideline', limit=5)` (api_key optional)

### 2.2 Society-Specific Search

**ADA Standards of Care (Diabetes)**

`ADA_list_standards_sections()` — No parameters. Lists all 19 sections of ADA Standards of Care (2026).
- Returns list of section titles with PMIDs

`ADA_search_standards(query, limit)` — Search within ADA Standards.
- Returns: list — `[{title, ...}]`
- **Note**: Uses PubMed corporate author filter. Use broad medical terms, not specific phrases.
- ✅ Works: `'glycemic targets'`, `'pharmacologic approaches'`, `'cardiovascular risk'`
- ❌ May fail: very specific phrases like `'first-line medication metformin'`

`ADA_get_standards_section(section_number)` — Get metadata for a specific section.
- Returns dict with section abstract (not full PMC text)

**AHA/ACC Cardiology**

`AHA_ACC_search_guidelines(query, limit)` — Search AHA/ACC guidelines.
- Returns: **list** directly — `[{title, ...}]`
- Example: `AHA_ACC_search_guidelines(query='heart failure management', limit=5)`

`AHA_list_guidelines(limit)` / `ACC_list_guidelines(limit)` — List recent guidelines.

`AHA_ACC_get_guideline(pmid)` — Get full text of AHA/ACC guideline by PMID (via PMC).
- Returns dict with full text
- Example: `AHA_ACC_get_guideline(pmid='37952199')`

**NCCN Oncology**

`NCCN_list_patient_guidelines(limit)` — List all NCCN patient guideline resources (up to 74).
- Returns: **list** directly — `[{cancer_type, url, category}, ...]`
- ⚠️ Field is `cancer_type`, NOT `title`
- Use `r[i]['cancer_type']` to get the cancer name, `r[i]['url']` for URL

`NCCN_search_guidelines(query, limit)` — Search NCCN publications.
- Returns: **list** directly — `[{title, ...}]`
- Note: Returns PubMed abstracts of NCCN articles (JNCCN), not proprietary guideline text

`NCCN_get_patient_guideline(url)` — Get full text of a patient guideline.
- Parameter: `url` (string) — the full URL from NCCN_list_patient_guidelines
- Example: `NCCN_get_patient_guideline(url='https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients/guidelines-for-patients-details?patientGuidelineId=61')`
- ⚠️ Do NOT pass an integer ID — pass the full URL string

**MAGICapp Living Guidelines**

`MAGICapp_list_guidelines(limit)` — List living guidelines.
- Returns: **dict wrapped** — `r.get('data', [])` gives the list
- ⚠️ Field is `name`, NOT `title`; use `item['name']` for guideline title
- Use `item['guidelineId']` for follow-up calls

`MAGICapp_get_guideline(guideline_id)` — Get full guideline details.
`MAGICapp_get_recommendations(guideline_id)` — Get recommendations for a guideline.
`MAGICapp_get_sections(guideline_id)` — Get sections.

**NCI Resources** ⚠️ (Research tools catalog, NOT clinical guidelines)

`NCI_search_cancer_resources(q, size)` — Search NCI Research Resources for Researchers (R4R).
- ⚠️ **This is a catalog of bioinformatics tools, datasets, and lab instruments — NOT a clinical guidelines database**
- Parameters: `q` (NOT `query`), `size` (NOT `limit` — use `size` for result count)
- Returns: dict — `r.get('data', {}).get('results', [])` gives the list
- Useful for: finding analysis tools, datasets, bioinformatics resources related to a cancer type
- Example: `NCI_search_cancer_resources(q='colorectal cancer screening', size=5)`

### 2.3 Pharmacogenomics Search (CPIC)

**Recommended workflow for gene-drug queries:**

```
Step 1: CPIC_get_gene_info(genesymbol='GENE')          → gene overview
Step 2: CPIC_get_gene_drug_pairs(genesymbol='GENE')    → all drug pairs + CPIC levels
Step 3: CPIC_list_guidelines(limit=50)                 → find guideline_id for gene+drug
Step 4: CPIC_get_recommendations(guideline_id=N)       → specific dosing recommendations
Step 5: CPIC_get_alleles(genesymbol='GENE')            → allele definitions
```

All CPIC tools return **dict-wrapped**: use `r.get('data', [])` to access results.

`CPIC_get_gene_info(genesymbol)` — Gene overview.
- Example: `CPIC_get_gene_info(genesymbol='CYP2D6')`

`CPIC_get_gene_drug_pairs(genesymbol, limit)` — All gene-drug interactions with CPIC levels.
- Returns: `data` = list of `{genesymbol, drugid, cpiclevel, pgkbcalevel, usedforrecommendation, ...}`
- `cpiclevel` A/B/C/D: A = strongest evidence

`CPIC_list_guidelines(limit)` — All CPIC guidelines.
- Returns: `data` = list of `{name: 'GENE and Drug', guidelineId, url, ...}`
- Use to find the `guidelineId` for a specific gene+drug pair

`CPIC_get_recommendations(guideline_id, limit)` — Get dosing recommendations.
- ⚠️ **Parameter is `guideline_id` (integer), NOT `genesymbol`**
- Workflow: first find guideline_id from `CPIC_list_guidelines`, then call this
- Example: `CPIC_get_recommendations(guideline_id=100416, limit=20)`
- Returns duplicate records per allele combination — deduplicate by phenotype before presenting

`CPIC_get_alleles(genesymbol, limit)` — Allele definitions.
- Use `clinicalfunctionalstatus` field (NOT `functionalstatus` which is always null)
- Example: `CPIC_get_alleles(genesymbol='CYP2D6', limit=10)`

`CPIC_get_drug_info(drugname)` — Drug details.
- Example: `CPIC_get_drug_info(drugname='codeine')`

`CPIC_search_gene_drug_pairs(genesymbol, limit)` — Search gene-drug pairs.
- ⚠️ **Requires PostgREST filter syntax**: `genesymbol='eq.CYP2D6'` (not just `'CYP2D6'`)
- Example: `CPIC_search_gene_drug_pairs(genesymbol='eq.CYP2D6', limit=5)`

### 2.4 Full-Text Retrieval

`NICE_Guideline_Full_Text(url)` — Get NICE guideline text.
- Use URL from NICE_Clinical_Guidelines_Search results
- Returns dict (may have empty data for some guidelines; try chapter URLs like `.../chapter/Recommendations`)

`WHO_Guideline_Full_Text(url)` — Get WHO guideline text.
- Note: Most WHO T2D content is in PDFs; tool may return PDF link not full text

`AHA_ACC_get_guideline(pmid)` — Get AHA/ACC guideline text via PMC.

---

## Phase 3: Synthesize Results

### 3.1 Report Structure

```
# Clinical Guidelines: [Topic]

## Summary
[2-3 sentence overview of what guidelines say]

## Key Recommendations

### [Source 1: NICE/ADA/NCCN/etc.]
[Key recommendations with evidence grade, URL]

### [Source 2]
[Key recommendations]

## Pharmacogenomics (if applicable)
[CPIC phenotype-to-recommendation table]

## References
[All URLs cited]
```

### 3.2 Evidence Grading

- **Grade A** (ADA) / **Class I** (AHA) / **Strong** (SIGN) = high confidence
- **Grade B/C** = moderate confidence; **Grade D** / **Consensus** = expert opinion
- **CPIC Level A** = strongest PGx evidence; **B** = moderate; **C/D** = limited
- Note recommendation year — guidelines vary in currency (SIGN 2025, ADA 2026, NICE Feb 2026)

### 3.3 CPIC Recommendation Deduplication

CPIC returns multiple records for the same phenotype (one per allele combination). Before presenting:
```python
seen_phenotypes = set()
unique_recs = []
for rec in recs:
    phenotype = rec.get('phenotype') or rec.get('lookupkey', '')
    if phenotype not in seen_phenotypes:
        seen_phenotypes.add(phenotype)
        unique_recs.append(rec)
```

---

## Phase 4: Decision Logic

### General disease guideline:
1. NICE (`query`, `limit`) — UK, high quality
2. GIN (`query`, `limit`) — multi-society aggregator ⭐ best for breadth
3. TRIP (`query`, `limit`, `search_type='guidelines'`)
4. If cardiac → add AHA_ACC_search_guidelines
5. If cancer → add NCCN_search_guidelines + NCCN_list_patient_guidelines
6. If diabetes → add ADA_list_standards_sections + ADA_search_standards

### Pharmacogenomics:
1. `CPIC_get_gene_info(genesymbol)` → overview
2. `CPIC_get_gene_drug_pairs(genesymbol)` → all drugs with CPIC levels
3. `CPIC_list_guidelines(limit=50)` → find guideline_id for target gene+drug
4. `CPIC_get_recommendations(guideline_id=N)` → specific recs (deduplicate by phenotype)

### Full text retrieval:
1. Find guideline URL/PMID from search results
2. NICE URL → NICE_Guideline_Full_Text
3. AHA/ACC PMID → AHA_ACC_get_guideline
4. WHO URL → WHO_Guideline_Full_Text
5. NCCN patient guideline URL → NCCN_get_patient_guideline

### Fallback strategy:
- If NICE returns empty → try TRIP or GIN
- If ADA returns 0 results → broaden query terms (e.g., `'pharmacologic approaches'` instead of `'metformin first-line'`)
- If WHO returns irrelevant results → skip WHO, use GIN or EuropePMC instead
- If CPIC returns no recommendations → list gene-drug pairs with CPIC levels as a proxy

---

## Critical Parameter Notes (Verified by Testing)

| Tool | CORRECT | WRONG |
|------|---------|-------|
| NICE_Clinical_Guidelines_Search | `query='...'`, `limit=N` (both required) | ❌ `q='...'` |
| TRIP_Database_Guidelines_Search | `search_type='guidelines'` required | ❌ omitting search_type |
| OpenAlex_Guidelines_Search | `year_from`/`year_to` are **optional** | ❌ treating as required |
| PubMed_Guidelines_Search | `api_key` is **optional** (omit or use `''`) | ❌ treating api_key as required |
| GIN_Guidelines_Search | `limit=N` required | ❌ omitting limit |
| CMA_Guidelines_Search | `limit=N` required | ❌ omitting limit |
| SIGN_search_guidelines | `query='...'` (NOT `q`) | ❌ `q='...'` |
| CTFPHC_search_guidelines | `query='...'` (NOT `q`) | ❌ `q='...'` |
| NCI_search_cancer_resources | `q='...'`, `size=N` (NOT `limit`) | ❌ `query=...` or `limit=N` |
| NCCN_list_patient_guidelines | field `cancer_type` (not `title`) | ❌ `.get('title')` |
| NCCN_get_patient_guideline | `url='https://...'` (full URL string) | ❌ integer patientGuidelineId |
| MAGICapp_list_guidelines | `r.get('data', [])` for list | ❌ accessing `r` directly as list |
| MAGICapp_* items | field `name` (not `title`) | ❌ `.get('title')` |
| CPIC_* tools | `r.get('data', [])` for list | ❌ accessing `r` directly |
| CPIC_get_recommendations | `guideline_id=N` (integer) | ❌ `genesymbol='CYP2D6'` |
| CPIC_search_gene_drug_pairs | `genesymbol='eq.CYP2D6'` (PostgREST) | ❌ `genesymbol='CYP2D6'` |
| CPIC_get_alleles | use `clinicalfunctionalstatus` field | ❌ `functionalstatus` (always null) |
| NCI_search_cancer_resources | `r.get('data',{}).get('results',[])` | ❌ `r.get('data', [])` |

---

## Response Format Reference

| Tool | Return type | Access pattern |
|------|-------------|----------------|
| NICE_Clinical_Guidelines_Search | **list** (raw) | `result[0]['title']` |
| GIN_Guidelines_Search | **list** (raw) | `result[0]['title']` |
| TRIP_Database_Guidelines_Search | **list** (raw) | `result[0]['title']` |
| WHO_Guidelines_Search | **list** (raw) | `result[0]['title']` |
| EuropePMC_Guidelines_Search | **list** (raw) | `result[0]['title']` |
| PubMed_Guidelines_Search | **list** (raw) | `result[0]['title']` |
| CMA_Guidelines_Search | **list** (raw) | `result[0]['title']` |
| SIGN_search_guidelines | **list** (raw) | `result[0]['title']` |
| CTFPHC_search_guidelines | **list** (raw) | `result[0]['title']` |
| ADA_search_standards | **list** (raw) | `result[0]['title']` |
| AHA_ACC_search_guidelines | **list** (raw) | `result[0]['title']` |
| NCCN_search_guidelines | **list** (raw) | `result[0]['title']` |
| NCCN_list_patient_guidelines | **list** (raw) | `result[0]['cancer_type']` |
| OpenAlex_Guidelines_Search | **list** (raw) | `result[0]['title']` |
| CPIC_list_guidelines | **dict** → `data` | `r.get('data', [])[0]['name']` |
| CPIC_get_gene_drug_pairs | **dict** → `data` | `r.get('data', [])[0]['genesymbol']` |
| CPIC_get_recommendations | **dict** → `data` | `r.get('data', [])[0]` |
| CPIC_get_gene_info | **dict** → `data` | `r.get('data', {})` |
| MAGICapp_list_guidelines | **dict** → `data` | `r.get('data', [])[0]['name']` |
| NCI_search_cancer_resources | **dict** nested | `r.get('data',{}).get('results',[])[0]['title']` |

---

## Known Limitations

- **WHO_Guidelines_Search**: Returns recently-published WHO docs regardless of query topic — results may be irrelevant for specific diseases. Supplement with GIN for international guidelines.
- **NCI_search_cancer_resources**: Catalogs research tools/datasets, NOT clinical practice guidelines.
- **NICE_Guideline_Full_Text**: Retrieves overview page only; recommendation sub-pages (`.../chapter/Recommendations`) may need direct URL
- **SIGN**: No full-text tool; guideline text only available as PDFs
- **ADA_get_standards_section**: Returns abstract only, not full PMC text
- **CPIC_get_recommendations**: Returns many duplicate records per allele combination; deduplicate by phenotype
- **NCCN_search_guidelines**: Returns PubMed/JNCCN abstracts, not proprietary NCCN guideline text
- **TRIP content**: Some TRIP results link to PDF-gated URLs; content extraction may fail with 403

## Missing Sources (Potential Future Tools)

- **USPSTF** (US Preventive Services Task Force) — primary US screening recommendations
- **ACG** (American College of Gastroenterology) — gastroenterology guidelines
- **AGA** (American Gastroenterological Association)
- **Cochrane Reviews** — systematic reviews on clinical interventions
- **AHRQ** — Agency for Healthcare Research and Quality
