# biokernel

> Biomedical OS Core & MCP Server

**Available tools:** Bash, Read

# BioKernel

The BioKernel is the central orchestration layer of the Biomedical OS, managing context, routing tasks to specialized agents via MCP (Model Context Protocol), and handling system resources.

## When to Use This Skill

*   **System Internal**: This is primarily a background skill for routing.
*   When initializing the Biomedical OS environment.
*   When managing state across multiple agent interactions.

## Core Capabilities

1.  **Task Routing**: Dispatches user queries to the correct specialist agent.
2.  **Context Management**: Maintains long-term memory and session state.
3.  **MCP Server**: Exposes tools and resources via standard protocol.

## Example Usage

**User**: "Start the BioKernel server."

**Agent Action**:
```bash
python3 platform/biokernel/server.py --port 8000
```
