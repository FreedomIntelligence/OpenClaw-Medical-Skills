# mcpmed-bioinformatics-server

> Model Context Protocol (MCP) server for bioinformatics web services like GEO, STRING, and UCSC Cell Browser.

**Available tools:** Bash

# MCPmed Bioinformatics Web Services

Adapts the Model Context Protocol (MCP) to bioinformatics web server backends. This creates a standardized, machine-actionable layer for LLMs to interact with external biological resources, matching the 2026 standard for agentic tools.

## When to Use This Skill

*   "Query STRING database for protein-protein interactions via MCP"
*   "Fetch dataset metadata from GEO using MCPmed"
*   "Access UCSC Cell Browser data through MCP"

## Core Capabilities

1.  **GEO Integration**: Search and retrieve Gene Expression Omnibus metadata autonomously.
2.  **STRING DB Access**: Query protein-protein interaction networks contextually.
3.  **UCSC Cell Browser**: Programmatic access to single-cell datasets.

## Workflow

1.  **Step 1**: Start the MCPmed server to expose the bioinformatics backend tools.
2.  **Step 2**: Connect the LLM client using MCP to query the integrated databases.

## Example Usage

**User**: "Query the STRING database for interactions with TP53."

**Agent Action**:
```bash
python3 -m mcpmed.cli query string --gene TP53
```
