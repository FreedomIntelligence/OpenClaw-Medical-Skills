# protein-structure-prediction

> Predicts 3D protein structures from amino acid sequences using ESMFold or AlphaFold3 (mock).

**Available tools:** Read, Bash

# Protein Structure Prediction (ESMFold/AF3)

The **Protein Structure Prediction Skill** provides an interface to state-of-the-art folding models. It takes an amino acid sequence and returns a PDB file or structure metrics (pLDDT).

## When to Use This Skill

*   When you have a protein sequence and need its 3D coordinates.
*   To check if a designed sequence folds into a stable structure.
*   To prepare a receptor for docking simulations.

## Core Capabilities

1.  **Folding**: Generates atomic coordinates (PDB format).
2.  **Confidence Scoring**: Returns pLDDT scores per residue.
3.  **Visualization**: (Optional) Generates a static view of the structure.

## Workflow

1.  **Input**: Amino acid sequence (FASTA string).
2.  **Process**: Sends sequence to ESMFold API (or local inference).
3.  **Output**: Saves `.pdb` file and returns confidence metrics.

## Example Usage

**User**: "Fold this sequence: MKTIIALSY..."

**Agent Action**:
```bash
python3 Skills/Drug_Discovery/Protein_Structure/esmfold_client.py \
    --sequence "MKTIIALSYIFCLVFDYDY" \
    --output structure.pdb
```
