# biomcp-server

> MCP bio bridge

**Available tools:** WebFetch

# BioMCP Server

Deploy and operate the BioMCP server so MCP-compatible clients (Claude Desktop, LobeChat, etc.) can query biomedical databases via a single standardized interface.

## When to Use
- Unified literature search (PubMed/PMC) inside MCP clients.
- Entity normalization via PubTator3 or genomic variant lookups.
- ClinicalTrials.gov queries without bespoke API wrappers.

## Core Capabilities
1. **PubMed/PMC search:** Execute complex literature queries.
2. **PubTator3 annotations:** Map text to genes, diseases, chemicals, species.
3. **ClinicalTrials.gov:** Retrieve trial metadata/protocols.
4. **Genomic variant lookups:** Fetch variant/gene summaries from connected sources.

## Deployment Workflow
1. **Install deps:** `cd repo && uv sync` (preferred) or `pip install .`.
2. **Run server:** `python -m biomcp.server` or `make run`; Docker Compose provided.
3. **Configure client:** Add command/args snippet from `README.md` into MCP client config (Claude Desktop, BioKernel, etc.).
4. **Test tools:** Invoke PubMed + ClinicalTrials + variant endpoints to ensure connectivity.
5. **Monitor:** Capture logs, rate-limit statuses, and data-source versions for audit.

## Guardrails
- Keep API keys/env secrets outside the repo.
- Respect upstream rate limits to avoid throttling or bans.
- Document which data sources are enabled per deployment and update when they change.

## References
- Source repo + configuration examples in `README.md`, `repo/docker-compose.yml`, and `repo/Makefile`.
