# molecule-evolution-agent

> Evolve Molecules

**Available tools:** Read, Bash

# Molecule Evolution Agent

The **Molecule Evolution Agent** acts as an autonomous medicinal chemist. It takes a starting molecule (or uses a default like Aspirin) and iteratively modifies its structure to optimize binding for a specific protein target.

## When to Use This Skill

*   **Lead Optimization**: When you have a hit molecule and want to improve its potency.
*   **De Novo Design**: To explore chemical space around a target protein.
*   **Idea Generation**: To get creative structural modifications suggested by an LLM.

## Core Capabilities

1.  **SMILES Manipulation**: Reads and writes chemical structures in SMILES format.
2.  **LLM Chemist**: Uses an LLM to suggest chemically valid modifications (e.g., "Add a fluorine group to the ring").
3.  **Mock Scoring**: (Currently) Uses a mock scoring function to simulate docking affinity.

## Workflow

1.  **Input**: Target Protein Name (e.g., "GPRC5D").
2.  **Process**: 
    *   Start with a seed molecule.
    *   Loop for *N* generations.
    *   Ask LLM for a modification.
    *   Score the new molecule.
    *   Keep the best candidate.
3.  **Output**: Top candidate SMILES and the evolution history.

## Example Usage

**User**: "Design a better binder for GPRC5D."

**Agent Action**:
```bash
python3 Skills/Drug_Discovery/Molecule_Design/evolution_agent.py
# (Note: The script currently defaults to GPRC5D, but can be extended for arguments)
```
