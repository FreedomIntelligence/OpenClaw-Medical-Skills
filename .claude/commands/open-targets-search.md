# open-targets-search

> Search Open Targets drug-disease associations with natural language queries. Target validation powered by Valyu semantic search.

# Open Targets Search

Search the complete Open Targets database of drug-disease associations and target validation data using natural language queries powered by Valyu's semantic search API.

## Why This Skill is Powerful

- **No API Parameter Parsing**: Just pass natural language queries directly - no need to construct complex search parameters
- **Semantic Search**: Understands the meaning of your query, not just keyword matching
- **Full-Text Access**: Returns complete target-disease association data with evidence scores
- **Image Links**: Includes data visualizations when available
- **Comprehensive Coverage**: Access to all Open Targets drug-disease association data

## Requirements

1. Node.js 18+ (uses built-in fetch)
2. Valyu API key from https://platform.valyu.ai ($10 free credits)

## CRITICAL: Script Path Resolution

The `scripts/search` commands in this documentation are relative to this skill's installation directory.

Before running any command, locate the script using:

```bash
OPEN_TARGETS_SCRIPT=$(find ~/.claude/plugins/cache -name "search" -path "*/open-targets-search/*/scripts/*" -type f 2>/dev/null | head -1)
```

Then use the full path for all commands:
```bash
$OPEN_TARGETS_SCRIPT "JAK2 inhibitors" 15
```

## API Key Setup Flow

When you run a search and receive `"setup_required": true`, follow this flow:

1. **Ask the user for their API key:**
   "To search Open Targets, I need your Valyu API key. Get one free ($10 credits) at https://platform.valyu.ai"

2. **Once the user provides the key, run:**
   ```bash
   scripts/search setup <api-key>
   ```

3. **Retry the original search.**

## When to Use This Skill

- Target validation for diseases
- Drug-disease associations
- Target prioritization for research
- Genetic evidence for targets
- Target-disease pathway analysis
- Therapeutic hypothesis validation
## Output Format

```json
{
  "success": true,
  "type": "open_targets_search",
  "query": "JAK2 inhibitors",
  "result_count": 10,
  "results": [
    {
      "title": "Target-Disease Association",
      "url": "https://platform.opentargets.org/...",
      "content": "Association data, evidence, scores...",
      "source": "open-targets",
      "relevance_score": 0.95,
      "images": ["https://example.com/pathway.png"]
    }
  ],
  "cost": 0.025
}
```

## Processing Results

### With jq

```bash
# Get association titles
scripts/search "query" 10 | jq -r '.results[].title'

# Get URLs
scripts/search "query" 10 | jq -r '.results[].url'

# Extract full content
scripts/search "query" 10 | jq -r '.results[].content'
```

## Common Use Cases

### Target Validation

```bash
# Find target evidence
scripts/search "kinase targets in inflammatory diseases" 50
```

### Drug Repurposing

```bash
# Search for repurposing opportunities
scripts/search "drugs targeting IL-6 pathway" 20
```

### Genetic Evidence

```bash
# Find genetic associations
scripts/search "loss of function variants protective effects" 15
```

### Disease Mechanism

```bash
# Search for mechanistic insights
scripts/search "immune checkpoint targets in cancer" 25
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

If you're building an AI project and want to integrate Open Targets Search directly into your application, use the Valyu SDK:

### Python Integration

```python
from valyu import Valyu

client = Valyu(api_key="your-api-key")

response = client.search(
    query="your search query here",
    included_sources=["valyu/valyu-open-targets"],
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
  includedSources: ["valyu/valyu-open-targets"],
  maxResults: 20
});

response.results.forEach((result) => {
  console.log(`Title: ${result.title}`);
  console.log(`URL: ${result.url}`);
  console.log(`Content: ${result.content.substring(0, 500)}...`);
});
```

See the [Valyu docs](https://docs.valyu.ai) for full integration examples and SDK reference.
