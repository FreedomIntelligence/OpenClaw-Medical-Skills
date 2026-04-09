# bayesian-optimizer

> Bayesian Optimize

**Available tools:** Read, Bash

# Bayesian Optimization (Self-Driving Lab)

The **Bayesian Optimizer** allows agents to efficiently explore a parameter space to maximize a target metric (yield, purity, binding affinity) with minimal experiments. It uses Gaussian Processes to model uncertainty and the Upper Confidence Bound (UCB) acquisition function.

## When to Use This Skill

*   When experiments are expensive or time-consuming.
*   To autonomously tune hyperparameters for a machine learning model.
*   To optimize reaction conditions (temperature, pH, concentration).

## Core Capabilities

1.  **Next Step Proposal**: Suggests the next best experiment parameters.
2.  **Surrogate Modeling**: Predicts outcomes for untested parameters.
3.  **Exploration/Exploitation**: Balances trying new things vs. refining known good results.

## Workflow

1.  **Input**: History of past experiments (params -> results) and bounds.
2.  **Process**: Fits a Gaussian Process to the data.
3.  **Output**: Returns the parameters for the next experiment.

## Example Usage

**User**: "Given these past results, what temperature and pH should I try next?"

**Agent Action**:
```bash
python3 Skills/Mathematics/Probability_Statistics/bayesian_optimization.py \
    --history "[[20, 7.0, 0.5], [25, 6.5, 0.6]]" \
    --bounds "[[10, 40], [5, 9]]" \
    --output next_experiment.json
```
