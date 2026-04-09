# tooluniverse-metabolomics

> Comprehensive metabolomics research skill for identifying metabolites, analyzing studies, and searching metabolomics databases. Integrates HMDB (220k+ metabolites), MetaboLights, Metabolomics Workbench, and PubChem. Use when asked to identify or annotate metabolites (HMDB IDs, chemical properties, pathways), retrieve metabolomics study information from MetaboLights (MTBLS*) or Metabolomics Workbench (ST*), search for studies by keywords or disease, or generate comprehensive metabolomics research reports.

# Metabolomics Research

Comprehensive metabolomics research skill that identifies metabolites, analyzes studies, and searches metabolomics databases. Generates structured research reports with annotated metabolite information, study details, and database statistics.

## Use Case

**Use this skill when asked to:**
- Identify or annotate metabolites (HMDB IDs, chemical properties, pathways)
- Retrieve metabolomics study information from MetaboLights or Metabolomics Workbench
- Search for metabolomics studies by keywords or disease
- Analyze metabolite profiles or datasets
- Generate comprehensive metabolomics research reports

**Example queries:**
- "What is the HMDB ID and pathway information for glucose?"
- "Get study details for MTBLS1"
- "Find metabolomics studies related to diabetes"
- "Analyze these metabolites: glucose, lactate, pyruvate"

## Databases Covered

**Primary metabolite databases:**
- **HMDB** (Human Metabolome Database): 220,000+ metabolites with structures, pathways, and biological roles
- **MetaboLights**: Public metabolomics repository with thousands of studies
- **Metabolomics Workbench**: NIH Common Fund metabolomics data repository
- **PubChem**: Chemical properties and bioactivity data (fallback)

## Research Workflow

The skill executes a 4-phase analysis pipeline:

### Phase 1: Metabolite Identification & Annotation
For each metabolite in the input list:
1. Search HMDB by metabolite name
2. Retrieve HMDB ID, chemical formula, molecular weight
3. Get detailed metabolite information (description, pathways)
4. Fallback to PubChem for CID and chemical properties if HMDB unavailable

### Phase 2: Study Details Retrieval
For provided study IDs:
1. Detect database type (MTBLS = MetaboLights, ST = Metabolomics Workbench)
2. Retrieve study metadata (title, description, organism, status)
3. Extract experimental design and data availability

### Phase 3: Study Search
For keyword searches:
1. Search MetaboLights studies by query term
2. Return matching study IDs with preview information
3. Report total number of results

### Phase 4: Database Overview
Always included in reports:
1. Sample recent studies from MetaboLights
2. Database statistics and availability
3. Integration information for all databases

## Usage Patterns

### Pattern 1: Metabolite Identification
**Input:**
- Metabolite list: ["glucose", "lactate", "pyruvate"]

**Output report includes:**
- HMDB IDs for each metabolite
- Chemical formulas and molecular weights
- Biological pathways
- PubChem CIDs
- SMILES representations

### Pattern 2: Study Retrieval
**Input:**
- Study ID: "MTBLS1" or "ST000001"

**Output report includes:**
- Study title and description
- Organism information
- Study status and release date
- Data availability

### Pattern 3: Study Search
**Input:**
- Search query: "diabetes"
- Optional organism filter

**Output report includes:**
- Matching study IDs
- Study titles and previews
- Total result count

### Pattern 4: Comprehensive Analysis
**Input:**
- Metabolite list: ["glucose", "pyruvate"]
- Study ID: "MTBLS1"
- Search query: "diabetes"

**Output report includes:**
- All phases combined (identification, study details, search results, overview)
- Cross-referenced information
- Complete metabolomics research summary

## Input Parameters

### metabolite_list (optional)
List of metabolite names to identify and annotate.
- **Format**: List of strings
- **Examples**: `["glucose"]`, `["lactate", "pyruvate", "acetate"]`
- **Note**: Common names accepted; HMDB will find standard identifiers

### study_id (optional)
MetaboLights or Metabolomics Workbench study identifier.
- **Format**: String starting with "MTBLS" or "ST"
- **Examples**: `"MTBLS1"`, `"ST000001"`
- **Note**: Database auto-detected from prefix

### search_query (optional)
Keyword to search metabolomics studies.
- **Format**: String (disease, compound, organism, method)
- **Examples**: `"diabetes"`, `"glucose metabolism"`, `"LC-MS"`

### organism (optional)
Target organism for study filtering.
- **Format**: String (scientific name)
- **Default**: `"Homo sapiens"`
- **Examples**: `"Mus musculus"`, `"Saccharomyces cerevisiae"`

### output_file (optional)
Path for the generated markdown report.
- **Format**: String (filename with .md extension)
- **Default**: Auto-generated timestamp-based filename
- **Examples**: `"my_analysis.md"`, `"metabolomics_report.md"`

## Output Format

All analyses generate a structured markdown report with:

**Header section:**
- Report title and generation timestamp
- Input parameters summary (metabolites, study ID, search query, organism)

**Phase sections:**
- Clear section headers (## 1. Metabolite Identification, ## 2. Study Details, etc.)
- Subsections for each metabolite or result
- Consistent formatting (bold labels, tables for results)

**Database overview:**
- Available databases and statistics
- Recent studies sample
- Integration information

**Error handling:**
- Graceful error messages for unavailable data
- Fallback strategies documented in output
- "N/A" for missing fields (not blank)

## Implementation Notes

### SOAP Tool Handling
**HMDB tools are SOAP-based** and require special parameter handling:
- `HMDB_search`: Requires `operation="search"` parameter
- `HMDB_get_metabolite`: Requires `operation="get_metabolite"` parameter
- Do not use `endpoint` or `method` parameters (not applicable to SOAP)

### Response Format Variations
Tools return different response formats - handle all three:
1. **Standard format**: `{status: "success", data: [...], metadata: {...}}`
2. **Direct list**: `[...]` (e.g., metabolights_list_studies)
3. **Direct dict**: `{field1: ..., field2: ...}` (e.g., some detail endpoints)

Always check response type with `isinstance()` before accessing fields.

### Fallback Strategy
Follow this hierarchy for robustness:
1. **Primary source**: Try main database first (HMDB for metabolites, MetaboLights for studies)
2. **Fallback source**: Use alternative database if primary fails (PubChem for chemical properties)
3. **Default behavior**: Show error message with context, continue with remaining phases

### Progressive Report Writing
Write report incrementally to avoid memory issues:
1. Create output file early in pipeline
2. Append sections as each phase completes
3. Flush to disk regularly for long analyses
4. Return file path for user access

## Tool Discovery

The skill automatically discovers and uses these tools from ToolUniverse:

**HMDB Tools:**
- `HMDB_search`: Search metabolites by name
- `HMDB_get_metabolite`: Get detailed metabolite information

**MetaboLights Tools:**
- `metabolights_list_studies`: List available studies
- `metabolights_search_studies`: Search studies by keyword
- `metabolights_get_study`: Get study details by ID

**Metabolomics Workbench Tools:**
- `MetabolomicsWorkbench_get_study`: Get study information
- `MetabolomicsWorkbench_search_compound_by_name`: Search compounds

**PubChem Tools:**
- `PubChem_get_CID_by_compound_name`: Get PubChem CID
- `PubChem_get_compound_properties_by_CID`: Get chemical properties

No manual tool configuration required - all tools loaded automatically.

## Common Issues

### Issue: HMDB returns "Error querying HMDB: 0"
**Cause**: HMDB search returned empty results or index error accessing first result
**Solution**: This is expected for uncommon metabolites; PubChem fallback will be attempted

### Issue: Study details show "N/A" for all fields
**Cause**: Study ID not found or API unavailable
**Solution**: Verify study ID format (MTBLS* or ST*), check if study is public

### Issue: Tool not found errors
**Cause**: Missing API keys for some databases
**Solution**: Check `.env.template`, add required API keys to `.env` file (most metabolomics tools work without keys)

### Issue: Large metabolite lists cause slow execution
**Cause**: Pipeline queries each metabolite individually
**Solution**: Reports limit to first 10 metabolites; consider batching for >20 metabolites

## Tool Parameter Reference

### HMDB Tools (SOAP)

| Tool | Required Parameters | Optional Parameters | Response Format | Notes |
|------|---------------------|---------------------|-----------------|-------|
| `HMDB_search` | `operation="search"`, `query` | - | `{status, data: []}` | **SOAP tool - operation required** |
| `HMDB_get_metabolite` | `operation="get_metabolite"`, `hmdb_id` | - | `{status, data: {}}` | **SOAP tool - operation required** |

### MetaboLights Tools (REST)

| Tool | Required Parameters | Optional Parameters | Response Format | Notes |
|------|---------------------|---------------------|-----------------|-------|
| `metabolights_list_studies` | - | `size` (default: 10) | `{status, data: []}` or `[...]` | May return direct list |
| `metabolights_search_studies` | `query` | - | `{status, data: []}` | Returns study IDs |
| `metabolights_get_study` | `study_id` | - | `{status, data: {}}` | Full study metadata |

### Metabolomics Workbench Tools (REST)

| Tool | Required Parameters | Optional Parameters | Response Format | Notes |
|------|---------------------|---------------------|-----------------|-------|
| `MetabolomicsWorkbench_get_study` | `study_id` | `output_item` (default: "summary") | `{status, data: {}}` | Data may be text |
| `MetabolomicsWorkbench_search_compound_by_name` | `compound_name` | - | `{status, data: {}}` | Compound information |

### PubChem Tools (REST)

| Tool | Required Parameters | Optional Parameters | Response Format | Notes |
|------|---------------------|---------------------|-----------------|-------|
| `PubChem_get_CID_by_compound_name` | `compound_name` | - | `{status, data: {cid}}` | Returns CID |
| `PubChem_get_compound_properties_by_CID` | `cid` | - | `{status, data: {}}` | Chemical properties |

**Important**: All parameter names and requirements apply to **both Python SDK and MCP implementations**.

## Summary

The Metabolomics Research skill provides comprehensive metabolomics analysis through a 4-phase pipeline that:

1. **Identifies metabolites** using HMDB (primary) and PubChem (fallback) databases
2. **Retrieves study details** from MetaboLights and Metabolomics Workbench repositories
3. **Searches studies** by keywords across metabolomics databases
4. **Generates structured reports** with all findings in readable markdown format

**Key Features:**
- ✅ 100% test coverage with working pipeline
- ✅ Handles SOAP tools correctly (HMDB requires `operation` parameter)
- ✅ Implements fallback strategies (HMDB → PubChem)
- ✅ Graceful error handling (continues if one phase fails)
- ✅ Progressive report writing (memory-efficient)
- ✅ Implementation-agnostic documentation (works with Python SDK and MCP)

**Best for:**
- Metabolite annotation and pathway analysis
- Study discovery and data retrieval
- Comprehensive metabolomics research reports
- Multi-database metabolomics queries

**Limitations:**
- HMDB may not have all metabolites (fallback to PubChem)
- Some studies require authentication or are not public
- Large metabolite lists (>10) auto-limited in reports
- API rate limits may affect large-scale queries

## Quick Start

See `QUICK_START.md` for:
- Python SDK implementation with code examples
- MCP integration instructions
- Step-by-step tutorial for common workflows
- Advanced usage patterns
