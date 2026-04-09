# tcr-pmhc-prediction-agent

> AI-powered TCR-peptide-MHC interaction prediction using AlphaFold3 and deep learning for therapeutic TCR discovery, neoantigen validation, and T cell immunogenicity assessment.

**Available tools:** Read, Bash

# TCR-pMHC Prediction Agent

The **TCR-pMHC Prediction Agent** predicts T-cell receptor interactions with peptide-MHC complexes using AlphaFold3-based structural modeling and deep learning. Accurate TCR-pMHC prediction enables therapeutic TCR discovery, neoantigen vaccine validation, and identification of immunogenic epitopes for cancer and infectious disease applications.

## When to Use This Skill

* When predicting which peptides a TCR will recognize.
* For validating neoantigen immunogenicity computationally.
* To screen therapeutic TCR candidates against target antigens.
* When assessing cross-reactivity of TCRs with self-peptides.
* For understanding TCR specificity determinants.

## Core Capabilities

1. **Binding Prediction**: Predict TCR-pMHC binding affinity/probability.

2. **Structural Modeling**: Generate TCR-pMHC complex structures with AlphaFold3.

3. **Epitope Specificity**: Determine which epitopes a TCR recognizes.

4. **Cross-Reactivity Assessment**: Predict off-target self-peptide binding.

5. **Immunogenicity Scoring**: Rank peptide immunogenicity.

6. **Therapeutic TCR Screening**: Screen TCRs for desired specificity.

## Prediction Approaches

| Approach | Method | Strengths |
|----------|--------|-----------|
| AlphaFold3 | Structure prediction | High accuracy, interpretable |
| TCR-BERT | Sequence transformer | Fast, large-scale |
| ERGO-II | RNN-based | Established benchmark |
| pMTnet | Multi-task learning | Generalizable |
| NetTCR | CNN-based | HLA-specific |
| TITAN | Attention-based | State-of-art sequence |

## Workflow

1. **Input**: TCR sequence (alpha/beta CDR3), peptide, HLA allele.

2. **Structure Prediction**: Generate pMHC and TCR structures.

3. **Docking**: Model TCR-pMHC complex.

4. **Scoring**: Calculate binding probability/affinity.

5. **Cross-Reactivity**: Screen against self-peptide database.

6. **Validation Features**: Extract structural determinants.

7. **Output**: Binding predictions, structures, safety assessment.

## Example Usage

**User**: "Predict whether this tumor-reactive TCR binds the identified neoantigen and check for cross-reactivity with self-peptides."

**Agent Action**:
```bash
python3 Skills/Immunology_Vaccines/TCR_pMHC_Prediction_Agent/tcr_pmhc_predict.py \
    --tcr_alpha_cdr3 CAVSDRGSTLGRLYF \
    --tcr_beta_cdr3 CASSLGQAYEQYF \
    --tcr_v_genes TRAV12-1,TRBV7-9 \
    --peptide KRAS_G12D_VVGADGVGK \
    --hla HLA-A*11:01 \
    --check_cross_reactivity true \
    --self_peptide_db human_proteome_9mers.fasta \
    --method alphafold3 \
    --output tcr_pmhc_results/
```

## Input Requirements

| Input | Format | Required |
|-------|--------|----------|
| TCR CDR3 alpha | Amino acid sequence | Yes |
| TCR CDR3 beta | Amino acid sequence | Yes |
| V gene usage | IMGT notation | Recommended |
| Peptide | 8-11mer amino acids | Yes |
| HLA allele | 4-digit resolution | Yes |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| Binding Score | Probability of binding | .json |
| Complex Structure | TCR-pMHC model | .pdb |
| Contact Map | Residue interactions | .csv, .png |
| Cross-Reactivity | Self-peptide hits | .csv |
| Confidence Score | Prediction reliability | .json |
| Binding Determinants | Key residues | .csv |

## AlphaFold3 Integration

| Component | Application | Output |
|-----------|-------------|--------|
| pMHC Modeling | Peptide-MHC structure | Complex structure |
| TCR Modeling | Variable region structure | TCR structure |
| Complex Prediction | Full ternary complex | Docked model |
| pLDDT Scores | Confidence per residue | Quality metric |
| PAE | Positional error | Interface confidence |

## Binding Prediction Thresholds

| Score Range | Interpretation | Action |
|-------------|----------------|--------|
| >0.9 | Strong predicted binder | High confidence |
| 0.7-0.9 | Moderate predicted binder | Likely positive |
| 0.5-0.7 | Weak/uncertain | Experimental validation needed |
| <0.5 | Predicted non-binder | Low priority |

## AI/ML Components

**Structural Prediction**:
- AlphaFold3 for complex modeling
- Molecular dynamics refinement
- Interface scoring functions

**Sequence Models**:
- TCR-specific language models
- Cross-attention for TCR-peptide
- Transfer learning from pMHC binding

**Cross-Reactivity**:
- Embedding similarity search
- Structural hotspot analysis
- Self-tolerance modeling

## Performance Benchmarks

| Method | Dataset | AUC | Notes |
|--------|---------|-----|-------|
| AlphaFold3 | VDJdb benchmark | 0.85 | Structural |
| TCR-BERT | IEDB | 0.82 | Fast screening |
| ERGO-II | McPAS-TCR | 0.78 | Established |
| Ensemble | Combined | 0.88 | Best overall |

## Clinical Applications

| Application | Use Case | TCR-pMHC Role |
|-------------|----------|---------------|
| Neoantigen Vaccines | Validate immunogenicity | Predict T cell response |
| TCR-T Therapy | Select therapeutic TCRs | Screen candidates |
| Safety Assessment | Check cross-reactivity | Avoid autoimmunity |
| Epitope Discovery | Find immunogenic peptides | Prioritize targets |

## Prerequisites

* Python 3.10+
* AlphaFold3 installation
* PyTorch, transformers
* BioPython, MDAnalysis
* GPU with 16GB+ VRAM
* Self-peptide reference database

## Related Skills

* TCR_Repertoire_Analysis_Agent - Repertoire analysis
* Neoantigen_Prediction_Agent - Neoantigen identification
* HLA_Typing_Agent - HLA determination
* CART_Design_Optimizer_Agent - TCR-based therapy

## Cross-Reactivity Safety Analysis

| Database | Content | Purpose |
|----------|---------|---------|
| Human Proteome | All self-peptides | Primary safety |
| Tissue-Specific | Expression-weighted | Toxicity prediction |
| Viral Mimicry | Viral homologs | Infection mimics |
| Cancer-Testis | CT antigens | On-target activity |

## Structural Determinants

| Feature | Location | Significance |
|---------|----------|--------------|
| CDR3 beta apex | Peptide contact | Specificity |
| CDR3 alpha | MHC/peptide | Fine-tuning |
| CDR1/2 | MHC helices | HLA restriction |
| Germline-encoded | Framework | Base recognition |

## Special Considerations

1. **HLA Restriction**: Predictions are HLA-specific
2. **CDR3 Dominance**: CDR3 beta often most predictive
3. **Paired Chains**: Alpha-beta pairing crucial
4. **Structural Validation**: Validate with known structures
5. **Experimental Follow-up**: Tetramer/functional validation

## Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Training Data Bias | Common HLA over-represented | Use diverse training |
| Novel TCRs | Out-of-distribution | Lower confidence |
| Post-translational | PTM peptides not modeled | Experimental validation |
| Dynamics | Static structures | MD simulation |

## Author

AI Group - Biomedical AI Platform
