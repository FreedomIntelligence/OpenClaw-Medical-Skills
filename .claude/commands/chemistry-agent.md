# chemistry-agent

> Autonomous chemical synthesis & analysis

**Available tools:** Bash, Read, Write

# Chemistry Agent

The Chemistry Agent is a specialized module for autonomous chemical reasoning, synthesis planning, and property prediction. It integrates with computational chemistry tools and potentially lab automation hardware.

## When to Use This Skill

*   When you need to design a synthesis route for a molecule.
*   When predicting chemical properties (solubility, toxicity).
*   When analyzing reaction mechanisms.

## Core Capabilities

1.  **Retrosynthesis**: Planning backward from target to starting materials.
2.  **Property Prediction**: Estimating physicochemical properties.
3.  **Reaction Optimization**: Suggesting optimal conditions.

## Example Usage

**User**: "Plan a synthesis route for Aspirin."

**Agent Action**:
```bash
python3 src/chemistry/main.py --target "Aspirin" --task "retrosynthesis"
```
