# medical-research-toolkit

> Query 14+ biomedical databases for drug repurposing, target discovery, clinical trials, and literature research. Access ChEMBL, PubMed, ClinicalTrials.gov, OpenTargets, OpenFDA, OMIM, Reactome, KEGG, UniProt, and more through a unified MCP endpoint. Use when researching disease targets, finding approved/investigational drugs, searching clinical evidence, discovering genetic associations, or analyzing compound bioactivity data.

# Medical Research Toolkit

Query 14+ biomedical databases for drug repurposing, target discovery, clinical evidence, and literature research — all via a unified MCP endpoint.

## ⚡ 30-Second Start

```bash
# Find drugs for myasthenia gravis
curl -X POST https://mcp.cloud.curiloo.com/tools/unified/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"chembl_find_drugs_by_indication","arguments":{"indication":"myasthenia gravis","max_results":10}},"id":1}'
```

**That's it!** You now have approved and investigational drugs for the disease.

---

## Quick Recipes

### Find Drugs for a Disease

```bash
curl -X POST https://mcp.cloud.curiloo.com/tools/unified/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"chembl_find_drugs_by_indication","arguments":{"indication":"myasthenia gravis","max_results":20}},"id":1}'
```

Returns: Approved + investigational drugs with max phase reached

### Find Disease Targets

```bash
# First: Find disease ID
curl -X POST https://mcp.cloud.curiloo.com/tools/unified/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"opentargets_search","arguments":{"query":"myasthenia gravis","entity_type":"disease"}},"id":1}'

# Returns: disease ID (e.g., EFO_0004991)
# Then: Get targets
curl -X POST https://mcp.cloud.curiloo.com/tools/unified/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"opentargets_get_associations","arguments":{"disease_id":"EFO_0004991","size":20}},"id":2}'
```

Returns: Top disease targets ranked by evidence strength (0-1 score)

### Search Literature

```bash
curl -X POST https://mcp.cloud.curiloo.com/tools/unified/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"pubmed_search_articles","arguments":{"diseases":["myasthenia gravis"],"keywords":["immunotherapy"],"max_results":20}},"id":1}'
```

Returns: PubMed articles on myasthenia gravis immunotherapy

### Find Active Clinical Trials

```bash
curl -X POST https://mcp.cloud.curiloo.com/tools/unified/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"ctg_search_studies","arguments":{"condition":"myasthenia gravis","recruitment_status":"RECRUITING","max_results":20}},"id":1}'
```

Returns: Actively recruiting trials for the disease

### Check Drug Safety

```bash
curl -X POST https://mcp.cloud.curiloo.com/tools/unified/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"openfda_search_adverse_events","arguments":{"drug_name":"eculizumab","limit":50}},"id":1}'
```

Returns: FDA adverse event reports—check for serious outcomes, death, hospitalization

---

## What You Get

**14+ Integrated Databases**

| Database | What's Inside | Use For |
|----------|---------------|---------|
| **ChEMBL** | 2M drugs, bioactivity data | Finding approved/investigational drugs |
| **OpenTargets** | Disease-target links + evidence | Identifying therapeutic targets |
| **PubMed** | 35M+ articles + preprints | Literature review & validation |
| **ClinicalTrials.gov** | 400K+ active trials | Finding ongoing studies |
| **OpenFDA** | Adverse events, drug labels | Safety assessment |
| **OMIM** | Genetic diseases, genes → phenotypes | Understanding disease genetics |
| **Reactome** | Pathways, protein interactions | Mechanism understanding |
| **UniProt** | Protein sequences, annotations | Protein properties |
| **KEGG** | Metabolic & disease pathways | Systems-level view |
| **GWAS Catalog** | Genetic associations | Variant discovery |
| **Pathway Commons** | Integrated pathway data | Network analysis |
| **MyGene.info** | Gene annotations | ID mapping |
| **MyVariant.info** | Variant effects | Variant interpretation |
| + more | | |

---

## Use Cases

### 🧬 Drug Repurposing
Find non-standard-care drugs for rare/complex diseases:
1. Find disease targets (OpenTargets)
2. Search for drugs targeting those genes (ChEMBL)
3. Check ongoing trials (ClinicalTrials)
4. Verify safety (OpenFDA, PubMed)

### 🔬 Target Discovery
Identify novel therapeutic targets:
1. Find disease associations (OpenTargets, GWAS)
2. Get pathway context (Reactome, KEGG)
3. Review literature (PubMed)
4. Check protein properties (UniProt)

### 📋 Clinical Evidence Review
Compile evidence for a hypothesis:
1. Search trials (ClinicalTrials.gov)
2. Find literature (PubMed)
3. Check FDA data (OpenFDA)

### 📊 Literature Mining
Systematically search biomedical research:
1. PubMed: 35M+ articles searchable by gene, disease, drug, chemical
2. Preprints: bioRxiv, medRxiv
3. Filter by keywords, date, study type

---

## API Endpoint

**Production (No setup needed):**
```
https://mcp.cloud.curiloo.com/tools/unified/mcp
```

All 14+ databases unified into one endpoint.

**Running Locally:**
```bash
pip install medical-mcps
medical-mcps
# Available at: http://localhost:8000/tools/unified/mcp
```

---

## Complete References

See detailed guides for each database:

- **[PubMed Guide](./references/pubmed.md)** — Literature search (genes, diseases, keywords)
- **[ClinicalTrials Guide](./references/clinical-trials.md)** — Find active trials
- **[ChEMBL Guide](./references/chembl.md)** — Drug-target data & bioactivity
- **[OpenTargets Guide](./references/opentargets.md)** — Disease-target associations
- **[OpenFDA Guide](./references/openfda.md)** — Drug safety & adverse events
- **[OMIM Guide](./references/omim.md)** — Genetic diseases (requires API key)
- **[Other APIs](./references/other-apis.md)** — Reactome, UniProt, KEGG, GWAS, etc.

---

## Workflow Example

**Complete Drug Repurposing Pipeline:**

See [drug-repurposing-workflow.md](./scripts/drug-repurposing-workflow.md) for step-by-step example with all 8 steps + curl commands.

---

## API Keys

Most APIs are **free, no key required**. Optional keys for higher rate limits:

| Database | Key? | Why | Get Key |
|----------|------|-----|---------|
| ChEMBL | No | Public data | (not needed) |
| OpenTargets | No | Public data | (not needed) |
| PubMed | No | Public data | (not needed) |
| ClinicalTrials | No | Public data | (not needed) |
| **OMIM** | **Yes** | Proprietary data | https://omim.org/api |
| OpenFDA | Optional | Higher rate limits | https://open.fda.gov |
| NCI Clinical Trials | Optional | Higher rate limits | https://clinicaltrialsapi.cancer.gov |

---

## Rate Limits & Caching

- **No authentication** for production endpoint (public)
- **Rate limits**: Generous (~1000+ requests/day per database)
- **Caching**: Automatic 30-day HTTP caching (RFC 9111)
- **Cost**: $0 (all databases public or researcher-accessible)

---

## Common Patterns

### Batch Query Loop

```bash
# Search multiple targets
for gene in CHRNE RAPSN LRP4; do
  curl -X POST https://mcp.cloud.curiloo.com/tools/unified/mcp \
    -H "Content-Type: application/json" -H "Accept: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"chembl_find_drugs_by_target\",\"arguments\":{\"target_name\":\"$gene\",\"max_results\":10}},\"id\":1}"
  sleep 1  # Be nice to the API
done
```

### ID Conversion

Need to convert IDs between databases?

```bash
curl -X POST https://mcp.cloud.curiloo.com/tools/unified/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"nodenorm_get_normalized_nodes","arguments":{"curie":"HGNC:11998"}},"id":1}'
```

Returns: Equivalent IDs in NCBI Gene, Uniprot, Ensembl, MyGene, etc.

---

## Troubleshooting

**No results?**
- Try alternative terms (gene symbol vs protein name)
- Check spelling
- Use standardized IDs (gene symbols, disease names)
- Some APIs use specific ID formats (EFO vs MONDO, etc.)

**Too many results?**
- Add filters (max_results, phase, recruitment status)
- Use `limit` or `size` parameters
- Combine with other databases to narrow focus

**API key errors?**
- OMIM requires API key — get from https://omim.org/api
- Other databases optional — request key if hitting rate limits

---

## Next Steps

1. **Pick a use case** (drug repurposing, target discovery, etc.)
2. **Read the relevant database guide** from References section
3. **Copy a quick recipe** from above
4. **Customize parameters** for your disease/gene/drug
5. **Scale up** — build your full research workflow

---

## Resources

- **Source Code**: https://github.com/pascalwhoop/medical-mcps
- **Author**: Pascal Brockmeyer (@pascalwhoop)
- **Organization**: Every Cure (https://www.everycure.org)
- **License**: MIT

---

## Getting Help

- Database not working? → Check [Troubleshooting](#troubleshooting)
- Want detailed guide? → See [Complete References](#complete-references)
- Need a workflow example? → See [drug-repurposing-workflow.md](./scripts/drug-repurposing-workflow.md)
- Question about
