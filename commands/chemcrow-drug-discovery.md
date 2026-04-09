# chemcrow-drug-discovery

> An LLM chemistry agent with expert-designed tools for organic synthesis, drug discovery, and materials design.

**Available tools:** Read, Bash

# ChemCrow

ChemCrow is an open-source package for the accurate integration of Large Language Models (LLMs) with chemistry tools. It is designed to autonomously plan and execute chemical syntheses, research materials, and discover new drugs.

## When to Use This Skill

*   **Synthesis Planning**: "How do I synthesize Ibuprofen?"
*   **Property Prediction**: "What is the logP of this molecule?"
*   **Safety Checks**: "Is this reaction explosive?"
*   **Literature Search**: "Find patents related to this substructure."

## Core Capabilities

1.  **Synthesis Planning**: Uses tools like RXN4Chemistry or local retrosynthesis models to plan routes.
2.  **Molecule Manipulation**: Add/remove functional groups, generate SMILES (RDKit).
3.  **Safety Assessment**: Checks reagents against safety databases (PubChem, GHS).
4.  **Web Search**: Google/Patent search for chemical literature.

## Tools (Expanded List - v2.0)

*   **RDKit**: Cheminformatics (MolToSmiles, SmilesToMol, descriptors).
*   **PubChem**: Search for properties and safety data.
*   **LiteratureSearch**: Search arXiv, patents.
*   **Synthesis**: IBM RXN, OPLS.
*   **Name2SMILES**: Convert chemical names to structures.

## Example Usage

**User**: "Plan a synthesis for a derivative of Aspirin that might have better solubility."

**Agent Action**:
1.  Retrieves Aspirin structure (SMILES).
2.  Modifies structure (e.g., adds a polar group) using RDKit.
3.  Checks solubility prediction.
4.  Plans synthesis route for the new molecule.
5.  Checks safety of reagents.
