# wikipedia-search

> Search and fetch structured content from Wikipedia using the MediaWiki API for reliable, encyclopedic information

# Wikipedia Search Skill

This skill enables Claude to search and fetch content from Wikipedia using the MediaWiki API. It provides more reliable, structured access to Wikipedia than general web search, with support for summaries, full article content, and multi-language access.

## When to Use

Use this skill when you need:

- **Encyclopedic knowledge** — Factual information about people, places, events, concepts
- **Historical information** — Well-documented historical facts, dates, and events
- **Scientific and technical concepts** — Definitions, explanations, and overviews
- **Biographical information** — Details about notable people
- **Geographic information** — Countries, cities, landmarks, and their details
- **Quick fact verification** — Cross-checking encyclopedic facts
- **Structured content** — Need article sections, categories, and links
- **Multi-language content** — Access Wikipedia in languages other than English

## When NOT to Use

Avoid using this skill for:

- **Current events or breaking news** — Wikipedia may not be up-to-date for very recent events (use web-search instead)
- **Controversial or disputed topics** — Wikipedia can have bias or edit wars; use multiple sources
- **Opinions or analysis** — Wikipedia aims for neutral point of view, not opinion
- **How-to guides or tutorials** — Wikipedia is encyclopedic, not instructional (look for specialized resources)
- **Code examples or technical documentation** — Use official docs or specialized sites
- **Personal or local information** — Wikipedia only covers notable topics
- **Real-time data** — Stock prices, weather, sports scores (use web-search instead)

## Usage

The skill is invoked by running the wiki script with a query:

```bash
python ~/.```

### Options

- `--mode [search|summary|full]` — Operation mode (default: summary)
  - `search`: Search for page titles matching the query
  - `summary`: Get a concise summary of a specific page
  - `full`: Get the complete article with sections and structure
- `--sentences N` — Number of sentences for summary mode (default: 5)
- `--lang CODE` — Language code (default: en)

### Common Language Codes

- `en` — English
- `es` — Spanish
- `fr` — French
- `de` — German
- `it` — Italian
- `ja` — Japanese
- `zh` — Chinese
- `ru` — Russian
- `ar` — Arabic
- `pt` — Portuguese

## Examples

### 1. Search for Page Titles

Search for Wikipedia articles matching a term:

```bash
python ~/.```

Output:
```json
{
  "mode": "search",
  "query": "quantum computing",
  "results": [
    {
      "title": "Quantum computing",
      "description": "Study of computers based on quantum phenomena",
      "url": "https://en.wikipedia.org/wiki/Quantum_computing"
    },
    ...
  ],
  "count": 10
}
```

### 2. Get a Summary

Get a concise summary of a Wikipedia page:

```bash
python ~/.```

Or with custom sentence count:

```bash
python ~/.```

Output:
```json
{
  "mode": "summary",
  "title": "Albert Einstein",
  "exists": true,
  "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
  "summary": "Albert Einstein was a German-born theoretical physicist...",
  "categories": ["1879 births", "1955 deaths", "German physicists", ...]
}
```

### 3. Get Full Article Content

Retrieve the complete article with sections:

```bash
python ~/.```

Output:
```json
{
  "mode": "full",
  "title": "Machine learning",
  "exists": true,
  "url": "https://en.wikipedia.org/wiki/Machine_learning",
  "summary": "Machine learning is a field of study in artificial intelligence...",
  "sections": [
    {
      "title": "History and relationships to other fields",
      "level": 0,
      "text": "..."
    },
    ...
  ],
  "categories": [...],
  "links": ["Artificial intelligence", "Neural network", ...]
}
```

### 4. Search in Different Languages

Search or fetch content in other languages:

```bash
python ~/.```

```bash
python ~/.```

## Workflow

When using this skill, follow this workflow:

### For Unknown Topics (Search First)

1. **Search for titles** — Use `--mode search` to find relevant articles
2. **Choose the right article** — Pick the most relevant title from results
3. **Get summary or full content** — Fetch the article with `--mode summary` or `--mode full`
4. **Parse JSON output** — Extract relevant information from structured data
5. **Cite the source** — Include Wikipedia URL when presenting information

### For Known Topics (Direct Fetch)

1. **Use exact or close title** — Wikipedia is good at matching similar titles
2. **Fetch summary** — Use `--mode summary` for quick facts
3. **Get full content if needed** — Use `--mode full` for comprehensive information
4. **Extract sections** — Parse specific sections for focused information

### JSON Output Structure

#### Search Mode
```json
{
  "mode": "search",
  "query": "original query",
  "results": [
    {
      "title": "Page Title",
      "description": "Brief description",
      "url": "https://en.wikipedia.org/wiki/Page_Title"
    }
  ],
  "count": 10
}
```

#### Summary Mode
```json
{
  "mode": "summary",
  "title": "Article Title",
  "exists": true,
  "url": "https://en.wikipedia.org/wiki/Article_Title",
  "summary": "Summary text...",
  "categories": ["Category1", "Category2"]
}
```

#### Full Mode
```json
{
  "mode": "full",
  "title": "Article Title",
  "exists": true,
  "url": "https://en.wikipedia.org/wiki/Article_Title",
  "summary": "Summary text...",
  "sections": [
    {
      "title": "Section Name",
      "level": 0,
      "text": "Section content..."
    }
  ],
  "categories": ["Category1", "Category2"],
  "links": ["Related Page 1", "Related Page 2"]
}
```

#### Error Response
```json
{
  "mode": "summary",
  "title": "Nonexistent Page",
  "exists": false,
  "error": "Page not found"
}
```

## Best Practices

### Query Formulation

- **Use specific titles** — "Python (programming language)" not just "Python"
- **Try exact names** — Wikipedia handles disambiguation well
- **Use search mode for exploration** — When unsure of exact title, search first
- **Check for disambiguation pages** — Some terms have multiple meanings

### Mode Selection

- **search** — When you don't know the exact page title or want to explore topics
- **summary** — For quick facts, definitions, or overviews (most common use case)
- **full** — When you need detailed information, specific sections, or comprehensive coverage

### Multi-Language Usage

- **Start with English** — English Wikipedia is often most comprehensive
- **Use native language for local topics** — Local events, culture, geography may be better in native language
- **Cross-reference languages** — Different language versions may have different information
- **Match query language** — If searching in French, use --lang fr

### Information Extraction

- **Use sections strategically** — In full mode, target specific sections for focused information
- **Check categories** — Categories help understand topic classification
- **Follow links** — Related links can lead to more detailed subtopics
- **Verify with summary** — Always present in page summary for quick fact-checking

## Attribution Guidelines

When presenting Wikipedia content to users:

- **Always cite Wikipedia** — Include the page URL: `[Article Title](URL)`
- **Note it's from Wikipedia** — Be transparent: "According to Wikipedia..."
- **Include publication status** — Wikipedia is continuously edited; information may change
- **Cross-reference for important facts** — For critical information, verify with additional sources

Example:

```
According to Wikipedia, Python is a high-level, general-purpose programming
language that emphasizes code readability with the use of significant indentation.

Source:
- [Python (programming language) - Wikipedia](https://en.wikipedia.org/wiki/Python_(programming_language))
```

## Error Handling

The script handles common errors gracefully:

### Page Not Found

If a page doesn't exist:
- JSON will include `"exists": false` and `"error": "Page not found"`
- Try using search mode first to find the correct title
- Check spelling and try variations
- Consider disambiguation pages

### Network Failures

If the API request fails:
- Error message printed to stderr
- Exit code will be non-zero
- Retry after a moment or check internet connection

### Import Errors

If `Wikipedia-API` library is missing:
- Script automatically attempts to install it
- Requires `pip` to be available
- May require `--break-system-packages` flag in some environments
- If auto-install fails, manually install: `pip install Wikipedia-API`

### Rate Limiting

Wikipedia's API is generally permissive:
- No authentication required for reading
- Reasonable use limits (shouldn't hit them in normal usage)
- If rate limited, wait a few seconds before retrying

## Technical Details

### Dependencies

- **Python 3.x** — Required (python3 command must be available)
- **Wikipedia-API** — Auto-installed if missing
- **pip** — Required for dependency installation

### Auto-Installation

The script automatically installs missing dependencies:

```python
subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "Wikipedia-API", "--break-system-packages", "--quiet"
])
```

The `--break-system-packages` flag is needed for externally-managed Python environments (common on modern Linux distributions and macOS with Homebrew Python).

### API Details

- Uses the **MediaWiki API** via the Wikipedia-API Python library
- OpenSearch API for title search functionality
- User agent: `- No API key required
- Free and open access

### Exit Codes

- `0` — Success
- `1` — General error (page not found, network failure, invalid query, etc.)
- `2` — Import error (dependency installation failed)

## Limitations

### Wikipedia Constraints

- **Not always current** — Wikipedia can lag behind breaking news by hours or days
- **Coverage varies** — Obscure topics may have minimal or no articles
- **Neutral POV** — Wikipedia strives for neutrality, which may omit certain perspectives
- **No original research** — Wikipedia doesn't contain new analysis or unpublished information
- **Notability requirements** — Many topics aren't notable enough for Wikipedia inclusion

### Technical Limitations

- **Section text truncated** — In full mode, sections limited to 5000 characters each to prevent huge responses
- **Limited links** — Only first 50 links returned in full mode
- **Limited categories** — Only first 10 categories returned
- **No images** — Script returns text only, not images or media
- **No infobox data** — Structured infobox data not easily accessible via this API

### Language Support

- **Quality varies by language** — English Wikipedia is most comprehensive
- **Translation issues** — Titles don't always translate directly between languages
- **Script mixing** — Some languages use different scripts (Arabic, Chinese, etc.)

## Troubleshooting

### Script Not Executable

If you get "Permission denied" error:

```bash
chmod +x ~/.```

### Python Not Found

If `python3` command doesn't exist, create an alias or use full path to Python interpreter.

### Installation Fails in Virtual Environment

If auto-install fails due to venv restrictions, manually install globally:

```bash
python3 -m pip install Wikipedia-API --user
```

### Page Not Found for Valid Topic

- Try search mode first: `--mode search` to find exact title
- Check for spelling variations
- Try disambiguation: add context in parentheses (e.g., "Mercury (planet)" vs "Mercury (element)")
- Verify the page exists by visiting Wikipedia directly

### Non-English Characters Not Displaying

- Ensure your terminal supports UTF-8 encoding
- JSON output uses `ensure_ascii=False` for proper Unicode support
- May need to set `LANG=en_US.UTF-8` or similar environment variable

## Use Cases and Examples

### Research Starting Point

```bash
# Start with search
python ~/.
# Get summary of main article
python ~/.
# Get full content for deep dive
python ~/.```

### Quick Facts

```bash
# Who is someone?
python ~/.
# What is something?
python ~/.
# Where is something?
python ~/.```

### Historical Information

```bash
# Historical events
python ~/.
# Historical figures
python ~/.```

### Scientific Concepts

```bash
# Physics
python ~/.
# Biology
python ~/.
# Chemistry
python ~/.```

## See Also

- [Wikipedia API Documentation](https://www.mediawiki.org/wiki/API:Main_page) — Official MediaWiki API docs
- [Wikipedia-API Python Library](https://github.com/martin-majlis/Wikipedia-API) — Upstream library documentation
- `../web-search/` — Complementary skill for current events and real-time information

## Notes

- This skill complements the **web-search** skill: use Wikipedia for encyclopedic knowledge and web-search for current events
- Wikipedia content is licensed under CC BY-SA, always attribute properly
- For critical information, cross-reference with other authoritative sources
- Wikipedia's strength is breadth of coverage and structured information, not real-time updates
