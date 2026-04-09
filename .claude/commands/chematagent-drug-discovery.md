# chematagent-drug-discovery

> Chemical Lab Agent

**Available tools:** Bash, Read

# CheMatAgent

A two-tiered agent system with access to 137 Python-wrapped chemical tools for drug discovery and materials science.

## When to Use

*   **Molecule Design**: Generating novel structures with specific properties.
*   **Property Prediction**: Estimating solubility, toxicity, and bioactivity.
*   **Synthesis Planning**: Designing retro-synthetic routes.

## Core Capabilities

1.  **Tool Orchestration**: Manages a library of 137 chemical tools.
2.  **Multi-Scale Modeling**: Bridges quantum mechanics and molecular dynamics.
3.  **Lab Automation**: Generates instructions for robotic synthesis platforms.

## Workflow

1.  **Goal**: Define target property (e.g., "LogP < 5").
2.  **Design**: Generate candidates.
3.  **Filter**: Use property prediction tools.
4.  **Plan**: Output synthesis recipe.

## Example Usage

**User**: "Design a molecule similar to Aspirin but with higher solubility."

**Agent Action**:
```bash
python -m chematagent.design --scaffold "Aspirin" --objective "maximize solubility"
```
