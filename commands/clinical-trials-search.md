# clinical-trials-search

> Search ClinicalTrials.gov with natural language queries. Find clinical trials, enrollment, and outcomes using Valyu semantic search.

# Clinical Trials Search

Search the complete ClinicalTrials.gov database of clinical studies using natural language queries powered by Valyu's semantic search API.

## Why This Skill is Powerful

- **No API Parameter Parsing**: Just pass natural language queries directly - no need to construct complex search parameters
- **Semantic Search**: Understands the meaning of your query, not just keyword matching
- **Full-Text Access**: Returns complete trial information including phases, conditions, interventions, and outcomes
- **Image Links**: Includes data visualizations when available
- **Comprehensive Coverage**: Access to all ClinicalTrials.gov data

## Requirements

1. Node.js 18+ (uses built-in fetch)
2. Valyu API key from https://platform.valyu.ai ($10 free credits)

## CRITICAL: Script Path Resolution

The `scripts/search` commands in this documentation are relative to this skill's installation directory.

Before running any command, locate the script using:

```bash
CLINICAL_TRIALS_SCRIPT=$(find ~/.claude/plugins/cache -name "search" -path "*/clinical-trials-search/*/scripts/*" -type f 2>/dev/null | head -1)
```

Then use the full path for all commands:
```bash
$CLINICAL_TRIALS_SCRIPT "CAR-T cell therapy trials" 15
```

## API Key Setup Flow

When you run a search and receive `"setup_required": true`, follow this flow:

1. **Ask the user for their API key:**
   "To search ClinicalTrials.gov, I need your Valyu API key. Get one free ($10 credits) at https://platform.valyu.ai"

2. **Once the user provides the key, run:**
   ```bash
   scripts/search setup <api-key>
   ```

3. **Retry the original search.**

## When to Use This Skill

- Finding ongoing and completed clinical trials
- Identifying trial eligibility criteria
- Recruiting status and enrollment information
- Comparing treatment approaches in trials
- Patient recruitment and enrollment research
- Outcomes and safety data from trials
## Output Format

```json
{
  "success": true,
  "type": "clinical_trials_search",
  "query": "CAR-T cell therapy trials",
  "result_count": 10,
  "results": [
    {
      "title": "Trial Title",
      "url": "https://clinicaltrials.gov/...",
      "content": "Trial details, phase, conditions, outcomes...",
      "source": "clinical-trials",
      "relevance_score": 0.95,
      "images": []
    }
  ],
  "cost": 0.025
}
```

## Processing Results

### With jq

```bash
# Get trial titles
scripts/search "query" 10 | jq -r '.results[].title'

# Get URLs
scripts/search "query" 10 | jq -r '.results[].url'

# Extract full content
scripts/search "query" 10 | jq -r '.results[].content'
```

## Common Use Cases

### Drug Development

```bash
# Find drug trials
scripts/search "phase 2 trials for Alzheimer's disease" 50
```

### Treatment Research

```bash
# Search for treatment studies
scripts/search "checkpoint inhibitor combinations in lung cancer" 20
```

### Medical Device Studies

```bash
# Find device trials
scripts/search "continuous glucose monitoring device studies" 15
```

### Intervention Analysis

```bash
# Search for intervention studies
scripts/search "behavioral interventions for obesity" 25
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

If you're building an AI project and want to integrate Clinical Trials Search directly into your application, use the Valyu SDK:

### Python Integration

```python
from valyu import Valyu

client = Valyu(api_key="your-api-key")

response = client.search(
    query="your search query here",
    included_sources=["valyu/valyu-clinical-trials"],
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
  includedSources: ["valyu/valyu-clinical-trials"],
  maxResults: 20
});

response.results.forEach((result) => {
  console.log(`Title: ${result.title}`);
  console.log(`URL: ${result.url}`);
  console.log(`Content: ${result.content.substring(0, 500)}...`);
});
```

See the [Valyu docs](https://docs.valyu.ai) for full integration examples and SDK reference.
