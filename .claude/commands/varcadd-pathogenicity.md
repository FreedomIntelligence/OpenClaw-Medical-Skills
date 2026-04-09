# varcadd-pathogenicity

> Variant Scorer

**Available tools:** Bash, Read

# varCADD (Variant Pathogenicity Predictor)

Genome-wide pathogenicity prediction leveraging standing variation data to improve accuracy over traditional CADD scores.

## When to Use

*   **Variant Prioritization**: Ranking candidate variants in rare disease cases.
*   **VUS Interpretation**: Assessing variants of uncertain significance.
*   **Research**: Annotating novel variants in population studies.

## Core Capabilities

1.  **Score Generation**: Calculate C-scores for SNVs and indels.
2.  **Annotation**: Add functional context (conservation, protein domains).
3.  **Filtering**: Identify likely pathogenic variants based on thresholds.

## Workflow

1.  **Input**: VCF file.
2.  **Annotate**: Run varCADD model.
3.  **Filter**: Keep variants with Score > X.
4.  **Output**: Annotated VCF or ranked table.

## Example Usage

**User**: "Score these variants from patient X."

**Agent Action**:
```bash
varcadd score --input patient.vcf --output scored.vcf
```
