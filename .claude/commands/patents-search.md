# patents-search

> Search global patents with natural language queries. Prior art, patent landscapes, and innovation tracking via Valyu.

# Patents Search

Search the complete global patent database using natural language queries powered by Valyu's semantic search API.

## Why This Skill is Powerful

- **No API Parameter Parsing**: Just pass natural language queries directly - no need to construct complex search parameters
- **Semantic Search**: Understands the meaning of your query, not just keyword matching
- **Full-Text Access**: Returns complete patent information including claims, descriptions, and technical details
- **Image Links**: Includes patent diagrams and figures when available
- **Comprehensive Coverage**: Access to global patent data across jurisdictions

## Requirements

1. Node.js 18+ (uses built-in fetch)
2. Valyu API key from https://platform.valyu.ai ($10 free credits)

## CRITICAL: Script Path Resolution

The `scripts/search` commands in this documentation are relative to this skill's installation directory.

Before running any command, locate the script using:

```bash
PATENTS_SCRIPT=$(find ~/.claude/plugins/cache -name "search" -path "*/patents-search/*/scripts/*" -type f 2>/dev/null | head -1)
```

Then use the full path for all commands:
```bash
$PATENTS_SCRIPT "CRISPR gene editing methods" 15
```

## API Key Setup Flow

When you run a search and receive `"setup_required": true`, follow this flow:

1. **Ask the user for their API key:**
   "To search patents, I need your Valyu API key. Get one free ($10 credits) at https://platform.valyu.ai"

2. **Once the user provides the key, run:**
   ```bash
   scripts/search setup <api-key>
   ```

3. **Retry the original search.**

## When to Use This Skill

- Prior art searching and patent landscaping
- Technology trend analysis
- Competitor innovation tracking
- Patent freedom-to-operate analysis
- Patent claim analysis and interpretation
- Patent filing strategy research
## Output Format

```json
{
  "success": true,
  "type": "patents_search",
  "query": "CRISPR gene editing methods",
  "result_count": 10,
  "results": [
    {
      "title": "Patent Title",
      "url": "https://patents.google.com/...",
      "content": "Patent claims, description, technical details...",
      "source": "patents",
      "relevance_score": 0.95,
      "images": ["https://example.com/diagram.png"]
    }
  ],
  "cost": 0.025
}
```

## Processing Results

### With jq

```bash
# Get patent titles
scripts/search "query" 10 | jq -r '.results[].title'

# Get URLs
scripts/search "query" 10 | jq -r '.results[].url'

# Extract full content
scripts/search "query" 10 | jq -r '.results[].content'
```

## Common Use Cases

### Prior Art Search

```bash
# Find prior art
scripts/search "lithium ion battery electrode materials" 50
```

### Competitive Intelligence

```bash
# Search competitor patents
scripts/search "CAR-T cell therapy manufacturing methods" 20
```

### Technology Landscape

```bash
# Find technology trends
scripts/search "quantum computing error correction patents" 15
```

### Freedom to Operate

```bash
# Search for blocking patents
scripts/search "mRNA vaccine delivery systems" 25
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

If you're building an AI project and want to integrate Patents Search directly into your application, use the Valyu SDK:

### Python Integration

```python
from valyu import Valyu

client = Valyu(api_key="your-api-key")

response = client.search(
    query="your search query here",
    included_sources=["valyu/valyu-patents"],
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
  includedSources: ["valyu/valyu-patents"],
  maxResults: 20
});

response.results.forEach((result) => {
  console.log(`Title: ${result.title}`);
  console.log(`URL: ${result.url}`);
  console.log(`Content: ${result.content.substring(0, 500)}...`);
});
```

See the [Valyu docs](https://docs.valyu.ai) for full integration examples and SDK reference.
