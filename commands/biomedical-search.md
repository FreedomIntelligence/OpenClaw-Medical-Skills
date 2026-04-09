# biomedical-search

> Complete biomedical information search combining PubMed, preprints, clinical trials, and FDA drug labels. Powered by Valyu semantic search.

# Biomedical Search

Search across all major biomedical databases (PubMed, bioRxiv, medRxiv, ClinicalTrials.gov, FDA drug labels) simultaneously using natural language queries powered by Valyu's semantic search API.

## Why This Skill is Powerful

- **No API Parameter Parsing**: Just pass natural language queries directly - no need to construct complex search parameters
- **Semantic Search**: Understands the meaning of your query, not just keyword matching
- **Full-Text Access**: Returns complete content from literature, trials, and drug labels
- **Image Links**: Includes figures and images when available
- **Comprehensive Coverage**: Search across PubMed, bioRxiv, medRxiv, clinical trials, and drug labels simultaneously
- **Unified Results**: Get results from all biomedical sources in a single query

## Requirements

1. Node.js 18+ (uses built-in fetch)
2. Valyu API key from https://platform.valyu.ai ($10 free credits)

## CRITICAL: Script Path Resolution

The `scripts/search` commands in this documentation are relative to this skill's installation directory.

Before running any command, locate the script using:

```bash
BIOMEDICAL_SCRIPT=$(find ~/.claude/plugins/cache -name "search" -path "*/biomedical-search/*/scripts/*" -type f 2>/dev/null | head -1)
```

Then use the full path for all commands:
```bash
$BIOMEDICAL_SCRIPT "CAR-T cell therapy" 20
```

## API Key Setup Flow

When you run a search and receive `"setup_required": true`, follow this flow:

1. **Ask the user for their API key:**
   "To search biomedical databases, I need your Valyu API key. Get one free ($10 credits) at https://platform.valyu.ai"

2. **Once the user provides the key, run:**
   ```bash
   scripts/search setup <api-key>
   ```

3. **Retry the original search.**

## When to Use This Skill

- Complete biomedical information gathering
- Clinical research combined with basic science
- Finding trials, literature, and official drug info together
- Evidence-based medicine research
- Disease understanding from multiple angles
## Output Format

```json
{
  "success": true,
  "type": "biomedical_search",
  "query": "CAR-T cell therapy",
  "result_count": 20,
  "results": [
    {
      "title": "Title",
      "url": "https://...",
      "content": "Full content...",
      "source": "pubmed|biorxiv|medrxiv|clinical-trials|drug-labels",
      "relevance_score": 0.95,
      "images": ["https://example.com/figure1.jpg"]
    }
  ],
  "cost": 0.035
}
```

## Processing Results

### With jq

```bash
# Get titles
scripts/search "query" 20 | jq -r '.results[].title'

# Get URLs
scripts/search "query" 20 | jq -r '.results[].url'

# Extract full content
scripts/search "query" 20 | jq -r '.results[].content'

# Filter by source type
scripts/search "query" 20 | jq -r '.results[] | select(.source == "clinical-trials") | .title'
```

## Common Use Cases

### Clinical Research Planning

```bash
# Gather evidence for clinical study design
scripts/search "phase 2 trials checkpoint inhibitors melanoma" 50
```

### Drug Safety Assessment

```bash
# Search literature, labels, and trials for safety data
scripts/search "SGLT2 inhibitors cardiovascular safety" 40
```

### Treatment Protocol Development

```bash
# Find current practice and emerging approaches
scripts/search "pembrolizumab dosing regimens NSCLC" 30
```

### Medical Writing

```bash
# Comprehensive research for medical communications
scripts/search "JAK inhibitors rheumatoid arthritis efficacy" 60
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

If you're building an AI project and want to integrate Biomedical Search directly into your application, use the Valyu SDK:

### Python Integration

```python
from valyu import Valyu

client = Valyu(api_key="your-api-key")

response = client.search(
    query="your search query here",
    included_sources=["valyu/valyu-pubmed", "valyu/valyu-biorxiv", "valyu/valyu-medrxiv", "valyu/valyu-clinical-trials", "valyu/valyu-drug-labels"],
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
  includedSources: ["valyu/valyu-pubmed", "valyu/valyu-biorxiv", "valyu/valyu-medrxiv", "valyu/valyu-clinical-trials", "valyu/valyu-drug-labels"],
  maxResults: 20
});

response.results.forEach((result) => {
  console.log(`Title: ${result.title}`);
  console.log(`URL: ${result.url}`);
  console.log(`Content: ${result.content.substring(0, 500)}...`);
});
```

See the [Valyu docs](https://docs.valyu.ai) for full integration examples and SDK reference.
