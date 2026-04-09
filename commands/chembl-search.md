# chembl-search

> Search ChEMBL bioactive molecules database with natural language queries. Find compounds and assay data with Valyu semantic search.

# ChEMBL Search

Search the complete ChEMBL database of bioactive molecules, drug targets, and binding data using natural language queries powered by Valyu's semantic search API.

## Why This Skill is Powerful

- **No API Parameter Parsing**: Just pass natural language queries directly - no need to construct complex search parameters
- **Semantic Search**: Understands the meaning of your query, not just keyword matching
- **Full-Text Access**: Returns complete compound and target information
- **Image Links**: Includes molecular structures and data visualizations
- **Comprehensive Coverage**: Access to all ChEMBL bioactive molecule data for drug discovery

## Requirements

1. Node.js 18+ (uses built-in fetch)
2. Valyu API key from https://platform.valyu.ai ($10 free credits)

## CRITICAL: Script Path Resolution

The `scripts/search` commands in this documentation are relative to this skill's installation directory.

Before running any command, locate the script using:

```bash
CHEMBL_SCRIPT=$(find ~/.claude/plugins/cache -name "search" -path "*/chembl-search/*/scripts/*" -type f 2>/dev/null | head -1)
```

Then use the full path for all commands:
```bash
$CHEMBL_SCRIPT "kinase inhibitors" 15
```

## API Key Setup Flow

When you run a search and receive `"setup_required": true`, follow this flow:

1. **Ask the user for their API key:**
   "To search ChEMBL, I need your Valyu API key. Get one free ($10 credits) at https://platform.valyu.ai"

2. **Once the user provides the key, run:**
   ```bash
   scripts/search setup <api-key>
   ```

3. **Retry the original search.**

## When to Use This Skill

- Finding bioactive compounds for drug discovery
- Target-based compound searching
- Compound property optimization
- Assay data and biological activity research
- Structure-activity relationship studies
- Lead compound identification
## Output Format

```json
{
  "success": true,
  "type": "chembl_search",
  "query": "kinase inhibitors",
  "result_count": 10,
  "results": [
    {
      "title": "Compound/Assay Title",
      "url": "https://chembl.org/...",
      "content": "Compound data, targets, assay results...",
      "source": "chembl",
      "relevance_score": 0.95,
      "images": ["https://example.com/structure.png"]
    }
  ],
  "cost": 0.025
}
```

## Processing Results

### With jq

```bash
# Get compound titles
scripts/search "query" 10 | jq -r '.results[].title'

# Get URLs
scripts/search "query" 10 | jq -r '.results[].url'

# Extract full content
scripts/search "query" 10 | jq -r '.results[].content'
```

## Common Use Cases

### Drug Discovery

```bash
# Find lead compounds
scripts/search "JAK2 selective inhibitors for myelofibrosis" 50
```

### Target Validation

```bash
# Search for target information
scripts/search "protein kinase B binding assays" 20
```

### SAR Analysis

```bash
# Find structure-activity relationships
scripts/search "benzimidazole derivatives anticancer activity" 15
```

### Mechanism Research

```bash
# Search for mechanism data
scripts/search "allosteric modulators of NMDA receptors" 25
```


## Error Handling

All commands return JSON with `success` field:

```json
{
  "success": false,
  "error": "Error message"
}
```

Exit codes:
- `0` - Success
- `1` - Error (check JSON for details)

## API Endpoint

- Base URL: `https://api.valyu.ai/v1`
- Endpoint: `/search`
- Authentication: X-API-Key header

## Architecture

```
scripts/
├── search          # Bash wrapper
└── search.mjs      # Node.js CLI
```

Direct API calls using Node.js built-in `fetch()`, zero external dependencies.

## Adding to Your Project

If you're building an AI project and want to integrate ChEMBL Search directly into your application, use the Valyu SDK:

### Python Integration

```python
from valyu import Valyu

client = Valyu(api_key="your-api-key")

response = client.search(
    query="your search query here",
    included_sources=["valyu/valyu-chembl"],
    max_results=20
)

for result in response["results"]:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Content: {result['content'][:500]}...")
```

### TypeScript Integration

```typescript
import { Valyu } from "valyu-js";

const client = new Valyu("your-api-key");

const response = await client.search({
  query: "your search query here",
  includedSources: ["valyu/valyu-chembl"],
  maxResults: 20
});

response.results.forEach((result) => {
  console.log(`Title: ${result.title}`);
  console.log(`URL: ${result.url}`);
  console.log(`Content: ${result.content.substring(0, 500)}...`);
});
```

See the [Valyu docs](https://docs.valyu.ai) for full integration examples and SDK reference.
