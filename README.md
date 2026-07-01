# OpenClaw Medical Skills

<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/FreedomIntelligence/OpenClaw-Medical-Skills?style=for-the-badge&logo=github&color=gold)](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/FreedomIntelligence/OpenClaw-Medical-Skills?style=for-the-badge&logo=github&color=blue)](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/FreedomIntelligence/OpenClaw-Medical-Skills?style=for-the-badge&logo=github)](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills/issues)
[![Skills Count](https://img.shields.io/badge/Skills-869-brightgreen?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==)](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills/tree/main/skills)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-OpenClaw%20%7C%20NanoClaw-orange?style=for-the-badge)](https://github.com/openclaw/openclaw)

**The largest open-source medical AI skill library for OpenClaw.**

*869 curated skills · Clinical · Genomics · Drug Discovery · Bioinformatics · Medical Devices*

[English](#) | [中文](README_zh.md)

</div>

---

## What Is This?

**OpenClaw Medical Skills** is a curated collection of **869 AI agent skills** covering the full spectrum of biomedical and clinical research. These skills are designed for [OpenClaw](https://github.com/openclaw/openclaw) / [NanoClaw](https://github.com/qwibitai/nanoclaw) — Claude-based personal AI assistant frameworks — and transform a general-purpose AI agent into a powerful medical and scientific research companion.

Each skill is a self-contained module (a `SKILL.md` file) that:
- Teaches the agent specialized domain knowledge and workflows
- Connects to real databases, APIs, and computational tools
- Produces structured, clinically or scientifically relevant outputs

> We benefit from the open-source community. The full collection of resources can be found here: [Awesome LLM Resources](https://github.com/WangRongsheng/awesome-LLM-resources?tab=readme-ov-file#%E6%8A%80%E8%83%BD-Skills)

### Why This Collection Matters

| Without Skills | With OpenClaw Medical Skills |
|---|---|
| Generic AI responses about medicine | Real PubMed / ClinicalTrials.gov / FDA queries |
| No bioinformatics capability | RNA-seq, scRNA-seq, GWAS, variant calling pipelines |
| No drug intelligence | ChEMBL, DrugBank, DDI prediction, pharmacovigilance |
| No clinical documentation | SOAP notes, discharge summaries, prior auth decisions |
| No genomics support | VCF annotation, ACMG classification, PRS calculation |
| No regulatory guidance | FDA, CE mark, IEC 62304, ISO 14971 compliance |

This collection aggregates skills from **12+ open-source skill repositories** spanning academic research tools, clinical workflows, regulatory frameworks, and cutting-edge AI-driven protein design — giving your AI agent capabilities comparable to a team of specialized research scientists.

---

## Installation

### Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) installed and running, **or** [NanoClaw](https://github.com/qwibitai/nanoclaw) as an alternative
- Git (for cloning this repo)

---

### For OpenClaw Users

OpenClaw loads skills from two locations:

| Priority | Path | Scope |
|---|---|---|
| High | `<workspace>/skills/` | Per-workspace (recommended) |
| Low | `~/.openclaw/skills/` | Global, shared across all agents |

#### Method 1 — Clone and Copy (Recommended)

```bash
# Clone this repository (skills only — skips large data files)
git clone --depth=1 --no-checkout https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills.git
cd OpenClaw-Medical-Skills
git sparse-checkout init --cone
git sparse-checkout set skills
git checkout main

# Install to your workspace skills directory
cp -r skills/* <your-workspace>/skills/

# Or install globally (available to all agents)
cp -r skills/* ~/.openclaw/skills/
```

> **Note:** Some skills bundle large data files (databases, datasets). The
> sparse-checkout method above avoids downloading them. If you need the full
> repo including all data, install [Git LFS](https://git-lfs.com) first, then
> run `git clone https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills.git`.

Skills are picked up automatically on the next session. No restart needed.

#### Method 2 — OpenClaw CLI

If you use the [OpenClaw plugin registry](https://clawhub.com), you can search and install individual skills from there. For bulk install from this collection, Method 1 is faster.

```bash
openclaw plugins install <skill-slug>    # install a single skill
openclaw plugins update                  # update all installed skills
```

#### Method 3 — Configure Extra Directories

To point OpenClaw at a cloned copy of this repo permanently, add it to `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "local": ["/path/to/OpenClaw-Medical-Skills"]
  }
}
```

This mounts the entire collection without copying files.

#### Method 4 — Install Selected Skills Only

Pick skills relevant to your domain:

```bash
# Example: clinical + drug discovery stack
SKILLS=(
  "clinical-reports"
  "tooluniverse-drug-research"
  "tooluniverse-pharmacovigilance"
  "clinicaltrials-database"
  "biomedical-search"
  "tooluniverse-drug-drug-interaction"
)

for skill in "${SKILLS[@]}"; do
  cp -r OpenClaw-Medical-Skills/skills/$skill ~/.openclaw/skills/
done
```

---

### For NanoClaw Users

NanoClaw loads skills into agent containers at startup from `container/skills/`.

```bash
# Clone and copy into NanoClaw container skills directory
git clone https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills.git
cp -r OpenClaw-Medical-Skills/skills/* /path/to/nanoclaw/container/skills/

# Rebuild the container to apply
cd /path/to/nanoclaw
./container/build.sh
```

---

### Verification

After installation, ask your agent:

```
What medical and clinical skills do you have available?
```

Your agent should list the installed skills with their capabilities.

---

## Skills Overview

| Category | Count | Highlights |
|---|---|---|
| General & Core | 10 | Browser/search, document tools, and developer workflow utilities |
| Medical & Clinical | 119 | Clinical reports, CDS, oncology, imaging, and healthcare AI |
| Scientific Databases | 43 | Genomics/protein/drug databases and biomedical knowledge retrieval |
| Bioinformatics (gptomics) | 239 | Variant analysis, sequencing QC, DE, pathways, single-cell, and epigenomics |
| Omics & Computational Biology | 59 | Single-cell/spatial, proteomics, cheminformatics, and protein design tools |
| ClawBio Pipelines | 21 | Orchestration pipelines for scRNA, GWAS, ancestry, and structural workflows |
| BioOS Extended Suite | 285 | Extended agent suite for oncology, immunology, clinical AI, and infrastructure |
| Data Science & Tools | 93 | Statistics, visualization, automation, simulation, and scientific tooling |
| **Total** | **869** | |

---

## Table of Contents

### General & Core
- [General Tools](#general-tools)

### Medical & Clinical
- [Medical Tools](#medical-tools)
- [Drug Safety & Chemical Biology](#drug-safety--chemical-biology)
- [Medical Imaging & Pathology](#medical-imaging--pathology)
- [Healthcare ML & Clinical AI](#healthcare-ml--clinical-ai)
- [Mental Health & Crisis Intervention](#mental-health--crisis-intervention)
- [Health & Wellness Analytics](#health--wellness-analytics)
- [Medical Device & Regulatory](#medical-device--regulatory)
- [Medical Device Software (meddev-agent-skills)](#medical-device--regulatory)

### Scientific Databases
- [Scientific Databases (Genomics & Variants)](#scientific-databases-genomics--variants)
- [Scientific Databases (Proteins, Pathways & Drugs)](#scientific-databases-proteins-pathways--drugs)
- [Cancer Genomics Databases](#cancer-genomics-databases)
- [Genomic & Molecular Databases](#genomic--molecular-databases)
- [Structural Biology & Drug Discovery](#structural-biology--drug-discovery)

### Bioinformatics (gptomics bio-* suite)
- [Bioinformatics Tools & Pipelines](#bioinformatics-tools--pipelines)
- [Bioinformatics — Clinical Databases & Variant Analysis](#bioinformatics--clinical-databases--variant-analysis)
- [Bioinformatics — Sequencing & Read QC](#bioinformatics--sequencing--read-qc)
- [Bioinformatics — Differential Expression & Transcriptomics](#bioinformatics--differential-expression--transcriptomics)
- [Bioinformatics — Pathway & Network Analysis](#bioinformatics--pathway--network-analysis)
- [Bioinformatics — Single-Cell & Spatial Omics](#bioinformatics--single-cell--spatial-omics)
- [Bioinformatics — Epigenomics & Chromatin](#bioinformatics--epigenomics--chromatin)
- [Bioinformatics — Metagenomics & Microbiome](#bioinformatics--metagenomics--microbiome)
- [Bioinformatics — Immunoinformatics & Flow Cytometry](#bioinformatics--immunoinformatics--flow-cytometry)
- [Bioinformatics — Multi-Omics Integration](#bioinformatics--multi-omics-integration)
- [Bioinformatics — Proteomics & Metabolomics](#bioinformatics--proteomics--metabolomics)
- [Bioinformatics — Structural Biology & Cheminformatics](#bioinformatics--structural-biology--cheminformatics)
- [Bioinformatics — Epidemiological & Causal Genomics](#bioinformatics--epidemiological--causal-genomics)

### Omics & Computational Biology
- [Single-Cell & Spatial Omics](#single-cell--spatial-omics)
- [Single-Cell & Trajectory Analysis](#single-cell--trajectory-analysis)
- [Proteomics & Mass Spectrometry](#proteomics--mass-spectrometry)
- [Cheminformatics & Drug Discovery](#cheminformatics--drug-discovery)
- [Protein Structure & Design](#protein-structure--design)
- [Phylogenetics & Network Analysis](#phylogenetics--network-analysis)

### ClawBio Pipelines
- [Bioinformatics Orchestration & Pipelines (ClawBio)](#bioinformatics-orchestration--pipelines-clawbio)
- [Genomics, Ancestry & Pharmacogenomics (ClawBio)](#genomics-ancestry--pharmacogenomics-clawbio)
- [Structural Biology & Literature (ClawBio)](#structural-biology--literature-clawbio)

### BioOS Extended Suite
- [BioOS Extended Bioinformatics Suite](#bioos-extended-bioinformatics-suite-mdbabumiamssmllms-universal-life-science-and-clinical-skills-)
- [Oncology & Precision Medicine Agents (BioOS)](#oncology--precision-medicine-agents-bioos)
- [Hematology & Blood Disorders (BioOS)](#hematology--blood-disorders-bioos)
- [Immunology & Cell Therapy (BioOS)](#immunology--cell-therapy-bioos)
- [Single-Cell & Spatial Agents (BioOS)](#single-cell--spatial-agents-bioos)
- [Drug Discovery & Design (BioOS)](#drug-discovery--design-bioos)
- [Clinical AI & Healthcare (BioOS)](#clinical-ai--healthcare-bioos)
- [Research Infrastructure & Agents (BioOS)](#research-infrastructure--agents-bioos)

### Data Science & Tools
- [Statistics & Data Analysis](#statistics--data-analysis)
- [Data Processing & Scientific Computing](#data-processing--scientific-computing)
- [Scientific Visualization & Communication](#scientific-visualization--communication)
- [Public Health & Time Series](#public-health--time-series)
- [Computational Simulation & Ontology](#computational-simulation--ontology-heshamfsmaterials-simulation-skills)
- [Analyst Personas](#analyst-personas)
- [Lab Automation & Integration](#lab-automation--integration)
- [Scientific Research & Writing](#scientific-research--writing)
- [Scientific Literature & Reference Management](#scientific-literature--reference-management)
- [Additional Scientific Tools](#additional-scientific-tools)
- [Developer Workflow Skills](#developer-workflow-skills-obrasuperpowers)

---

## Skills List

- [Skill Hub](https://skill.442595.xyz/) — 5800+ curated AI Agent Skills for Claude Code, Codex, Cursor, Hermes & more across 22 categories.
## 🧰 General & Core

<details open>
<summary>Expand/Collapse this category</summary>

### General Tools

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [agent-browser](skills/agent-browser/) | Browse the web for any task — research topics, read articles, interact with web apps, fill forms, take screenshots, extract data, and test web pages. Use whenever a browser would be useful. |
| [find-skills](skills/find-skills/) | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. |
| [multi-search-engine](skills/multi-search-engine/) | Multi search engine integration with 17 engines (8 CN + 9 Global). Supports Baidu, Bing, 360, Sogou, WeChat, Google, DuckDuckGo, WolframAlpha and more. Supports advanced operators, time filters, site search. No API keys required. |
| [wikipedia-search](skills/wikipedia-search/) | Search and fetch structured content from Wikipedia using the MediaWiki API for reliable, encyclopedic information. Supports multi-language queries. |
| [deep-research](skills/deep-research/) | Execute autonomous multi-step deep research on any topic. Searches multiple sources, reads full content, synthesizes findings, and produces a structured report. Use for comprehensive research, literature reviews, competitive analysis, or topic deep-dives. |
| [pdf](skills/pdf/) | Comprehensive PDF toolkit — extract text and tables, create new PDFs, merge/split documents, handle forms, OCR scanned PDFs. Use when working with any .pdf file. |
| [docx](skills/docx/) | Create, edit, and analyze Word documents (.docx). Supports tracked changes, comments, formatting preservation, and text extraction. Use for drafting, redlining, or extracting content from Word files. |
| [xlsx](skills/xlsx/) | Spreadsheet creation, editing, and analysis. Supports formulas, formatting, data analysis, and visualization. Use for any .xlsx, .xlsm, .csv, or .tsv task. |
| [pptx](skills/pptx/) | Presentation creation, editing, and analysis. Supports layouts, speaker notes, templates, and design. Use for any .pptx file. |
| [doc-coauthoring](skills/doc-coauthoring/) | Guide users through a structured workflow for co-authoring documentation. Use when writing documentation, proposals, technical specs, decision docs, or similar structured content. |

</details>

</details>

## 🏥 Medical & Clinical

<details open>
<summary>Expand/Collapse this category</summary>

### Medical Tools

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [pubmed-search](skills/pubmed-search/) | Search PubMed for scientific literature. Use when the user asks to find papers, search literature, look up research, find publications, or asks about recent studies. |
| [medical-research-toolkit](skills/medical-research-toolkit/) | Query 14+ biomedical databases for drug repurposing, target discovery, clinical trials, and literature research. Access ChEMBL, PubMed, ClinicalTrials.gov, OpenTargets, OpenFDA, OMIM, Reactome, KEGG, UniProt, and more through a unified MCP endpoint. |
| [medical-specialty-briefs](skills/medical-specialty-briefs/) | Generate daily or on-demand medical research briefs for any medical specialty. Searches latest research from top-tier journals (NEJM, Lancet, JAMA, BMJ, Nature Medicine), delivers concise summaries with 1-sentence takeaways and direct links. Use when user asks for medical news, research updates, or specialty-specific updates (endocrinology, cardiology, oncology, neurology, etc.). |
| [usmle](skills/usmle/) | Prepare for US medical licensing exams with progress tracking, weak area analysis, question bank management, and residency match planning. Covers Step 1/2 CK/Step 3, IMG-specific guidance, score prediction, and wellbeing support. |
| [medical-entity-extractor](skills/medical-entity-extractor/) | Extract medical entities (symptoms, medications, lab values, diagnoses) from patient messages. |
| [patiently-ai](skills/patiently-ai/) | Simplifies medical documents for patients. Takes doctor's letters, test results, prescriptions, discharge summaries, and clinical notes and explains them in clear, personalised language. |
| [biomedical-search](skills/biomedical-search/) | Complete biomedical information search combining PubMed, preprints, clinical trials, and FDA drug labels. Powered by Valyu semantic search. |
| [medical-imaging-review](skills/medical-imaging-review/) | Write comprehensive literature reviews for medical imaging AI research. Use when writing survey papers, systematic reviews, or literature analyses on imaging topics. |
| [fhir-developer-skill](skills/fhir-developer-skill/) | FHIR API development guide for building healthcare endpoints (Patient, Observation, Encounter, Condition, MedicationRequest). Use when developing or integrating FHIR REST APIs. |
| [clinical-trial-protocol-skill](skills/clinical-trial-protocol-skill/) | Generate clinical trial protocols for medical devices or drugs. Use when designing clinical studies, creating FDA submission documentation, or developing protocols for investigational products. |
| [prior-auth-review-skill](skills/prior-auth-review-skill/) | Automate payer review of prior authorization (PA) requests. Assesses medical necessity, validates against coverage policies, and generates PA decisions. |
| [clinical-reports](skills/clinical-reports/) | Write comprehensive clinical reports — case reports (CARE guidelines), diagnostic reports (radiology/pathology/lab), clinical trial reports (ICH-E3, CSR), and patient documentation (SOAP, H&P, discharge summaries). HIPAA/FDA/ICH-GCP compliant. |
| [clinicaltrials-database](skills/clinicaltrials-database/) | Query ClinicalTrials.gov via API v2. Search trials by condition, drug, location, status, or phase. Retrieve trial details by NCT ID, export data for clinical research and patient matching. |
| [clinical-decision-support](skills/clinical-decision-support/) | Generate clinical decision support (CDS) documents for pharmaceutical and clinical research — patient cohort analyses, treatment recommendation reports with GRADE evidence grading, biomarker integration, and statistical outputs (hazard ratios, survival curves). |
| [tooluniverse-clinical-trial-design](skills/tooluniverse-clinical-trial-design/) | Strategic clinical trial design feasibility assessment. Evaluates patient population sizing, biomarker prevalence, endpoint selection, comparator analysis, safety monitoring, and regulatory pathways. Use when planning Phase 1/2 trials or assessing trial feasibility. |
| [tooluniverse-disease-research](skills/tooluniverse-disease-research/) | Generate comprehensive disease research reports covering epidemiology, mechanisms, diagnostics, treatments, and ongoing trials. Use when asking about diseases, syndromes, or needing systematic disease analysis. |
| [tooluniverse-literature-deep-research](skills/tooluniverse-literature-deep-research/) | Deep literature research with target disambiguation, evidence grading, and structured theme extraction. Resolves gene/protein IDs, identifies synonyms, synthesizes biological models, and generates testable hypotheses. Use for thorough literature reviews or target profiles. |
| [tooluniverse-clinical-guidelines](skills/tooluniverse-clinical-guidelines/) | Search and retrieve clinical practice guidelines from 12+ sources (NICE, WHO, ADA, AHA/ACC, NCCN, SIGN, CPIC, etc.). Covers cardiology, oncology, diabetes, pharmacogenomics, and more. Use when asking about treatment recommendations or standard of care. |
| [tooluniverse-drug-research](skills/tooluniverse-drug-research/) | Comprehensive drug research reports covering identity, pharmacology, targets, clinical trials, safety, pharmacogenomics, and ADMET. Use for drug profiling, safety assessment, or clinical development research. |
| [tooluniverse-drug-repurposing](skills/tooluniverse-drug-repurposing/) | Identify drug repurposing candidates using target-based, compound-based, and disease-driven strategies. Finds new indications for approved drugs by analyzing targets, bioactivity, and safety profiles. |
| [tooluniverse-drug-drug-interaction](skills/tooluniverse-drug-drug-interaction/) | Drug-drug interaction prediction and risk assessment. Analyzes CYP450/transporter mechanisms, severity classification, and provides management strategies. Supports polypharmacy analysis (3+ drugs) and alternative drug recommendations. |
| [tooluniverse-rare-disease-diagnosis](skills/tooluniverse-rare-disease-diagnosis/) | Differential diagnosis for rare diseases based on phenotype and genetic data. Matches symptoms to HPO terms, identifies candidate diseases from Orphanet/OMIM, and interprets variants of uncertain significance. |
| [tooluniverse-pharmacovigilance](skills/tooluniverse-pharmacovigilance/) | Analyze drug safety signals from FDA adverse event reports, label warnings, and pharmacogenomic data. Calculates PRR/ROR, identifies serious adverse events, and assesses pharmacogenomic risk. |
| [tooluniverse-clinical-trial-matching](skills/tooluniverse-clinical-trial-matching/) | Patient-to-trial matching for precision medicine and oncology. Ranks trials from ClinicalTrials.gov by molecular eligibility, clinical criteria, biomarker alignment, and geographic feasibility with a quantitative Trial Match Score (0-100). |
| [literature-review](skills/literature-review/) | Systematic literature reviews across multiple databases (PubMed, arXiv, bioRxiv, Semantic Scholar). Produces professionally formatted reports with verified citations in APA, Nature, Vancouver styles. |
| [tooluniverse-precision-oncology](skills/tooluniverse-precision-oncology/) | Actionable treatment recommendations for cancer patients based on molecular profile. Interprets tumor mutations, identifies FDA-approved therapies, clinical trials, and resistance mechanisms. |
| [tooluniverse-cancer-variant-interpretation](skills/tooluniverse-cancer-variant-interpretation/) | Clinical interpretation of somatic mutations in cancer. Given gene+variant (e.g., EGFR L858R, BRAF V600E), assesses oncogenicity, therapeutic implications, and trial eligibility. |
| [tooluniverse-variant-analysis](skills/tooluniverse-variant-analysis/) | Production-ready VCF processing, variant annotation, and mutation analysis. Parses VCF files, annotates with ClinVar/gnomAD/COSMIC, and interprets clinical significance. |
| [tooluniverse-variant-interpretation](skills/tooluniverse-variant-interpretation/) | Systematic clinical variant interpretation from raw calls to ACMG-classified recommendations. Aggregates evidence from ClinVar, gnomAD, literature, and population databases. |
| [tooluniverse-structural-variant-analysis](skills/tooluniverse-structural-variant-analysis/) | Comprehensive structural variant (SV/CNV) analysis for clinical genomics. Classifies SVs, assesses pathogenicity, and interprets copy number alterations. |
| [tooluniverse-polygenic-risk-score](skills/tooluniverse-polygenic-risk-score/) | Build and interpret polygenic risk scores (PRS) for complex diseases using GWAS summary statistics. Calculates genetic risk profiles and interprets PRS percentiles. |
| [tooluniverse-precision-medicine-stratification](skills/tooluniverse-precision-medicine-stratification/) | Patient stratification for precision medicine by integrating genomic, clinical, and therapeutic data. Identifies treatment-relevant subgroups and biomarker-driven therapy options. |
| [tooluniverse-gwas-trait-to-gene](skills/tooluniverse-gwas-trait-to-gene/) | Discover genes associated with diseases and traits using GWAS Catalog (500k+ associations) and Open Targets Genetics locus-to-gene predictions. |
| [tooluniverse-gwas-drug-discovery](skills/tooluniverse-gwas-drug-discovery/) | Transform GWAS signals into drug targets and repurposing opportunities. Performs locus-to-gene mapping, druggability assessment, and existing drug identification. |
| [tooluniverse-gwas-study-explorer](skills/tooluniverse-gwas-study-explorer/) | Compare GWAS studies and assess replication across cohorts. Integrates NHGRI-EBI GWAS Catalog and Open Targets Genetics for cross-study meta-analysis. |
| [tooluniverse-gwas-finemapping](skills/tooluniverse-gwas-finemapping/) | Identify and prioritize causal variants at GWAS loci using statistical fine-mapping. Computes posterior probabilities and credible sets for causal variant identification. |
| [tooluniverse-gwas-snp-interpretation](skills/tooluniverse-gwas-snp-interpretation/) | Interpret SNPs from GWAS studies by aggregating evidence from GWAS Catalog, Open Targets Genetics, and ClinVar. Retrieves variant-trait associations and functional annotations. |
| [tooluniverse-phylogenetics](skills/tooluniverse-phylogenetics/) | Phylogenetics and sequence analysis — alignment processing, evolutionary tree construction, and evolutionary metrics for pathogens or species. |
| [tooluniverse-epigenomics](skills/tooluniverse-epigenomics/) | Epigenomics data processing — methylation array analysis (CpG filtering, differential methylation), chromatin accessibility, and histone modification analysis. |
| [tooluniverse-rnaseq-deseq2](skills/tooluniverse-rnaseq-deseq2/) | RNA-seq differential expression analysis using PyDESeq2. Performs normalization, dispersion estimation, Wald testing, LFC shrinkage, and pathway enrichment. |
| [tooluniverse-single-cell](skills/tooluniverse-single-cell/) | Single-cell RNA-seq analysis using scanpy. Performs QC, normalization, PCA, UMAP, Leiden clustering, trajectory analysis, and cell type annotation. |
| [tooluniverse-spatial-transcriptomics](skills/tooluniverse-spatial-transcriptomics/) | Spatial transcriptomics data analysis — maps gene expression in tissue architecture. Supports 10x Visium, MERFISH, seqFISH, and Slide-seq platforms. |
| [tooluniverse-spatial-omics-analysis](skills/tooluniverse-spatial-omics-analysis/) | Computational analysis for spatial multi-omics data integration — spatially variable genes, domain annotation, and tissue-resolved omics. |
| [tooluniverse-proteomics-analysis](skills/tooluniverse-proteomics-analysis/) | Mass spectrometry proteomics analysis — protein quantification, differential expression, PTMs, and protein-protein interaction network construction. |
| [tooluniverse-metabolomics](skills/tooluniverse-metabolomics/) | Metabolomics research — identifies metabolites and searches databases (HMDB 220k+ metabolites, MetaboLights, Metabolomics Workbench). |
| [tooluniverse-metabolomics-analysis](skills/tooluniverse-metabolomics-analysis/) | Metabolomics data analysis — metabolite identification, quantification, pathway analysis, and metabolic flux from LC-MS, GC-MS, or NMR data. |
| [tooluniverse-multi-omics-integration](skills/tooluniverse-multi-omics-integration/) | Integrate transcriptomics, proteomics, epigenomics, genomics, and metabolomics for systems biology and precision medicine. |
| [tooluniverse-multiomic-disease-characterization](skills/tooluniverse-multiomic-disease-characterization/) | Systems-level disease characterization integrating genomics, transcriptomics, proteomics, pathway, and therapeutic layers. |
| [tooluniverse-expression-data-retrieval](skills/tooluniverse-expression-data-retrieval/) | Retrieve gene expression and omics datasets from ArrayExpress and BioStudies with quality assessment and structured reports. |
| [tooluniverse-gene-enrichment](skills/tooluniverse-gene-enrichment/) | Gene enrichment and pathway analysis using gseapy, PANTHER, STRING, Reactome. Supports GO enrichment, KEGG pathways, and 40+ ToolUniverse tools. |
| [tooluniverse-systems-biology](skills/tooluniverse-systems-biology/) | Systems biology and pathway analysis using Reactome, KEGG, WikiPathways, Pathway Commons, and BioModels. Network modeling and pathway simulation. |
| [tooluniverse-protein-interactions](skills/tooluniverse-protein-interactions/) | Protein-protein interaction network analysis using STRING, BioGRID, and SASBDB. Maps interaction networks with confidence scores and functional modules. |
| [tooluniverse-protein-structure-retrieval](skills/tooluniverse-protein-structure-retrieval/) | Retrieve protein structure data from RCSB PDB, PDBe, and AlphaFold with quality assessment and comprehensive structural profiles. |
| [tooluniverse-protein-therapeutic-design](skills/tooluniverse-protein-therapeutic-design/) | Design novel protein therapeutics (binders, enzymes, scaffolds) using AI-guided de novo design — RFdiffusion, ProteinMPNN, and ESM. |
| [tooluniverse-antibody-engineering](skills/tooluniverse-antibody-engineering/) | Antibody engineering and optimization for therapeutics — humanization, affinity maturation, developability assessment, and immunogenicity prediction. |
| [tooluniverse-immune-repertoire-analysis](skills/tooluniverse-immune-repertoire-analysis/) | TCR/BCR repertoire analysis from sequencing data — clonality, diversity, V(D)J gene usage, clonal expansion, and antigen specificity prediction. |
| [tooluniverse-immunotherapy-response-prediction](skills/tooluniverse-immunotherapy-response-prediction/) | Predict patient response to immune checkpoint inhibitors using multi-biomarker integration — TMB, MSI, PD-L1, TIL signatures, and HLA typing. |
| [tooluniverse-infectious-disease](skills/tooluniverse-infectious-disease/) | Pathogen characterization and drug repurposing for infectious disease outbreaks. Identifies taxonomy, essential proteins, structural targets, and treatment options. |
| [tooluniverse-crispr-screen-analysis](skills/tooluniverse-crispr-screen-analysis/) | CRISPR screen analysis for functional genomics — pooled or arrayed screens (knockout/activation/interference) to identify essential genes and hits. |
| [tooluniverse-target-research](skills/tooluniverse-target-research/) | Comprehensive biological target intelligence — protein info, structure, interactions, pathways, expression, variant landscape, and drug pipeline. |
| [tooluniverse-network-pharmacology](skills/tooluniverse-network-pharmacology/) | Compound-target-disease network analysis for drug repurposing, polypharmacology discovery, and systems pharmacology. |
| [tooluniverse-statistical-modeling](skills/tooluniverse-statistical-modeling/) | Statistical modeling on biomedical datasets — linear/logistic regression, mixed-effects models, survival analysis, and Bayesian methods. |
| [tooluniverse-image-analysis](skills/tooluniverse-image-analysis/) | Biomedical microscopy image analysis — colony morphometry, cell counting, fluorescence quantification, and statistical comparison of imaging data. |
| [literature-search](skills/literature-search/) | Comprehensive scientific literature search across PubMed, arXiv, bioRxiv, medRxiv using natural language queries powered by Valyu semantic search. |
| [medrxiv-search](skills/medrxiv-search/) | Search medRxiv medical preprints with natural language queries powered by Valyu semantic search. |
| [clinical-trials-search](skills/clinical-trials-search/) | Search ClinicalTrials.gov with natural language queries — find trials by condition, enrollment status, and outcomes via Valyu. |
| [drug-discovery-search](skills/drug-discovery-search/) | End-to-end drug discovery platform combining ChEMBL, DrugBank, targets, and FDA labels via natural language Valyu search. |
| [drug-labels-search](skills/drug-labels-search/) | Search FDA drug labels with natural language queries — indications, dosing, and safety data via Valyu. |
| [chembl-search](skills/chembl-search/) | Search ChEMBL bioactive molecules database — compounds, assay data, and bioactivity via Valyu semantic search. |
| [open-targets-search](skills/open-targets-search/) | Search Open Targets drug-disease associations and target validation via Valyu semantic search. |
| [patents-search](skills/patents-search/) | Search global patents with natural language queries — prior art, patent landscapes, and innovation tracking via Valyu. |
| [drugbank-search](skills/drugbank-search/) | Search DrugBank comprehensive drug database — mechanisms, interactions, and safety data via Valyu semantic search. |
| [arxiv-search](skills/arxiv-search/) | Search arXiv preprints (biology, medicine, AI) using natural language queries powered by Valyu semantic search. |
| [gwas-database](skills/gwas-database/) | Query NHGRI-EBI GWAS Catalog for SNP-trait associations by rs ID, disease/trait, or gene. Retrieve p-values and summary statistics for genetic epidemiology. |
| [scikit-survival](skills/scikit-survival/) | Survival analysis and time-to-event modeling in Python — Kaplan-Meier, Cox regression, log-rank tests, and censored data handling using scikit-survival. |

</details>

### Drug Safety & Chemical Biology

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [tooluniverse-adverse-event-detection](skills/tooluniverse-adverse-event-detection/) | Detect and analyze adverse drug event signals using FDA FAERS data, drug labels, disproportionality analysis (PRR, ROR, IC), and biomedical evidence. Generates quantitative safety signal scores (0-100). |
| [tooluniverse-binder-discovery](skills/tooluniverse-binder-discovery/) | Discover novel small molecule binders for protein targets using structure-based and ligand-based approaches. Creates actionable reports with candidate compounds, ADMET profiles, and synthesis feasibility. |
| [tooluniverse-chemical-compound-retrieval](skills/tooluniverse-chemical-compound-retrieval/) | Retrieves chemical compound information from PubChem and ChEMBL with disambiguation, cross-referencing, and quality assessment. Comprehensive compound profiles with identifiers, properties, bioactivity. |
| [tooluniverse-chemical-safety](skills/tooluniverse-chemical-safety/) | Comprehensive chemical safety and toxicology assessment integrating ADMET-AI predictions, CTD toxicogenomics, FDA label safety data, DrugBank safety profiles, and STITCH chemical-protein interactions. |
| [tooluniverse-drug-target-validation](skills/tooluniverse-drug-target-validation/) | Computational validation of drug targets across 10 dimensions: disambiguation, disease association, druggability, chemical matter, clinical precedent, safety, and expression evidence. |
| [tooluniverse-sequence-retrieval](skills/tooluniverse-sequence-retrieval/) | Retrieve biological sequences (DNA, RNA, protein) from NCBI and ENA with gene disambiguation, accession type handling, and comprehensive sequence profiles. |

</details>

### Medical Imaging & Pathology

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [pydicom](skills/pydicom/) | Python library for working with DICOM medical imaging files. Reading, writing, modifying DICOM data, extracting pixel data, handling metadata and multi-frame files. |
| [histolab](skills/histolab/) | Digital pathology image processing toolkit for whole slide images (WSI). Process H&E or IHC stained tissue images, extract tiles from gigapixel slides. |
| [pathml](skills/pathml/) | Computational pathology toolkit for analyzing WSI and multiparametric imaging data. H&E stained images, multiplex immunofluorescence, spatial omics integration. |
| [omero-integration](skills/omero-integration/) | Microscopy data management platform. Access images via Python, retrieve datasets, analyze pixels, manage ROIs/annotations, for high-content screening workflows. |
| [neurokit2](skills/neurokit2/) | Comprehensive biosignal processing: ECG, EEG, EDA, RSP, PPG, EMG, EOG signals. Cardiovascular signal analysis, neurophysiology, and physiological data processing. |
| [neuropixels-analysis](skills/neuropixels-analysis/) | Neuropixels neural recording analysis. Load SpikeGLX/OpenEphys data, Kilosort4 spike sorting, quality metrics, Allen/IBL curation, for neuroscience research. |

</details>

### Healthcare ML & Clinical AI

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [pyhealth](skills/pyhealth/) | Comprehensive healthcare AI toolkit for developing ML models with clinical data (EHR, claims). Task definition API, model training, evaluation for clinical NLP and prediction. |
| [scikit-learn](skills/scikit-learn/) | Machine learning in Python: supervised learning (classification, regression), unsupervised learning (clustering, dimensionality reduction), model evaluation, hyperparameter tuning. |
| [transformers](skills/transformers/) | Pre-trained transformer models for NLP, computer vision, audio, and multimodal tasks. Text generation, classification, question answering, and biomedical NLP (BioBERT, ClinicalBERT). |
| [shap](skills/shap/) | Model interpretability using SHAP (SHapley Additive exPlanations). Explain ML model predictions, compute feature importance, generate SHAP plots for biomedical models. |
| [umap-learn](skills/umap-learn/) | UMAP dimensionality reduction. Fast nonlinear manifold learning for 2D/3D visualization, clustering preprocessing (HDBSCAN), for high-dimensional omics data. |

</details>

### Health & Wellness Analytics

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [nutrition-analyzer](skills/nutrition-analyzer/) | Comprehensive nutrition analysis: macro/micronutrient tracking, dietary assessment, meal planning, food data lookup, and nutritional recommendations. |
| [mental-health-analyzer](skills/mental-health-analyzer/) | Mental health data analysis: mood tracking, symptom patterns, PHQ/GAD scoring, behavioral insights, and wellness recommendations. |
| [sleep-analyzer](skills/sleep-analyzer/) | Sleep quality analysis: sleep stages, duration, efficiency metrics, circadian rhythm assessment, and sleep hygiene recommendations. |
| [rehabilitation-analyzer](skills/rehabilitation-analyzer/) | Rehabilitation progress tracking: functional assessments, exercise programs, recovery milestones, and outcome measurement for physical/occupational therapy. |
| [fitness-analyzer](skills/fitness-analyzer/) | Fitness performance analysis: exercise tracking, strength/cardio metrics, training load, VO2max estimation, and periodization planning. |
| [health-trend-analyzer](skills/health-trend-analyzer/) | Longitudinal health trend analysis: vital sign tracking, biomarker trends, risk factor monitoring, and predictive health insights. |
| [weightloss-analyzer](skills/weightloss-analyzer/) | Weight management analytics: caloric balance, body composition tracking, progress monitoring, and evidence-based weight loss strategies. |
| [goal-analyzer](skills/goal-analyzer/) | Health goal tracking and analysis: SMART goal setting, progress metrics, habit formation, and motivational insights for wellness objectives. |
| [occupational-health-analyzer](skills/occupational-health-analyzer/) | Occupational health assessment: workplace ergonomics, exposure risk, work-related illness surveillance, and return-to-work planning. |
| [travel-health-analyzer](skills/travel-health-analyzer/) | Travel medicine: destination health risks, vaccination requirements, malaria prophylaxis, altitude sickness, and traveler health preparation. |
| [family-health-analyzer](skills/family-health-analyzer/) | Family health management: pediatric milestones, family medical history, preventive screening schedules, and multigenerational health tracking. |
| [tcm-constitution-analyzer](skills/tcm-constitution-analyzer/) | Traditional Chinese Medicine constitution analysis: TCM body type assessment, pattern differentiation, herbal recommendations, and lifestyle guidance. |
| [emergency-card](skills/emergency-card/) | Generate emergency medical information cards with critical health data, medications, allergies, and emergency contacts for patient safety. |
| [ai-analyzer](skills/ai-analyzer/) | AI-powered comprehensive health data interpretation combining multiple biomarkers and health metrics for holistic wellness assessment. |
| [wellally-tech](skills/wellally-tech/) | Technical framework for WellAlly health analytics platform: integration patterns, data pipelines, and health AI infrastructure. |

</details>

### Mental Health & Crisis Intervention

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [crisis-detection-intervention-ai](skills/crisis-detection-intervention-ai/) | Detect crisis signals using NLP and mental health sentiment analysis. Implements suicide ideation detection, automated escalation, and crisis resource integration for mental health apps and recovery platforms. |
| [crisis-response-protocol](skills/crisis-response-protocol/) | Handle mental health crisis situations safely: crisis detection, safety protocols, emergency escalation, suicide prevention, and hotline integration for AI coaching applications. |
| [hipaa-compliance](skills/hipaa-compliance/) | Ensure HIPAA compliance when handling PHI. Audit logging, data access controls, security event tracking, and compliance verification for health data applications. |
| [clinical-diagnostic-reasoning](skills/clinical-diagnostic-reasoning/) | Identify and counteract cognitive biases in medical decision-making through systematic error analysis, differential diagnosis frameworks, and clinical judgment improvement. |
| [speech-pathology-ai](skills/speech-pathology-ai/) | AI-powered speech-language pathology: phoneme analysis, articulation visualization, voice disorder assessment, fluency intervention, AAC, and stuttering treatment support. |
| [hrv-alexithymia-expert](skills/hrv-alexithymia-expert/) | Heart rate variability biometrics and emotional awareness training. HRV analysis, interoception training, biofeedback, vagal tone assessment, and autonomic nervous system evaluation. |
| [adhd-daily-planner](skills/adhd-daily-planner/) | ADHD-optimized daily planning: time-blind friendly scheduling, executive function support, dopamine-aware task design, and neurodivergent-friendly productivity systems. |
| [grief-companion](skills/grief-companion/) | Compassionate bereavement support, memorial creation, grief education, and healing journey guidance through the non-linear path of loss. |
| [jungian-psychologist](skills/jungian-psychologist/) | Jungian analytical psychology: shadow work, archetypal analysis, dream interpretation, active imagination, addiction/recovery through depth psychology lens, and individuation process. |
| [modern-drug-rehab-computer](skills/modern-drug-rehab-computer/) | Comprehensive addiction recovery knowledge system: evidence-based treatment (CBT, DBT, MI, EMDR, MAT), recovery resources, crisis intervention, and family systems for rehab environments. |
| [recovery-community-moderator](skills/recovery-community-moderator/) | Trauma-informed AI moderation for addiction recovery communities: harm reduction, 12-step traditions, conflict detection, and crisis post identification. |

</details>

### Medical Device & Regulatory

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [iso-13485-certification](skills/iso-13485-certification/) | Comprehensive toolkit for ISO 13485 QMS documentation for medical devices: gap analysis, Quality Manuals, procedures, Medical Device Files. Covers FDA QMSR, EU MDR compliance. |

</details>

</details>

## 🗂️ Scientific Databases

<details open>
<summary>Expand/Collapse this category</summary>

### Scientific Databases (Genomics & Variants)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [clinvar-database](skills/clinvar-database/) | Query NCBI ClinVar for variant clinical significance. Search by gene/position, interpret pathogenicity classifications, access via E-utilities API or FTP, annotate VCFs, for genomic medicine. |
| [clinpgx-database](skills/clinpgx-database/) | Access ClinPGx pharmacogenomics data (successor to PharmGKB). Query gene-drug interactions, CPIC guidelines, allele functions, for precision medicine and genotype-guided dosing decisions. |
| [cosmic-database](skills/cosmic-database/) | Access COSMIC cancer mutation database. Query somatic mutations, Cancer Gene Census, mutational signatures, gene fusions, for cancer research and precision oncology. Requires authentication. |
| [ensembl-database](skills/ensembl-database/) | Query Ensembl genome database REST API for 250+ species. Gene lookups, sequence retrieval, variant analysis, comparative genomics, orthologs, VEP predictions, for genomic research. |
| [gene-database](skills/gene-database/) | Query NCBI Gene via E-utilities/Datasets API. Search by symbol/ID, retrieve gene info (RefSeqs, GO, locations, phenotypes), batch lookups, for gene annotation and functional analysis. |
| [geo-database](skills/geo-database/) | Access NCBI GEO for gene expression/genomics data. Search/download microarray and RNA-seq datasets (GSE, GSM, GPL), retrieve SOFT/Matrix files, for transcriptomics and expression analysis. |
| [ena-database](skills/ena-database/) | Access European Nucleotide Archive via API/FTP. Retrieve DNA/RNA sequences, raw reads (FASTQ), genome assemblies by accession, for genomics and bioinformatics pipelines. |
| [gget](skills/gget/) | CLI/Python toolkit for rapid bioinformatics queries with access to 20+ databases: Ensembl, UniProt, AlphaFold, ARCHS4, Enrichr, OpenTargets, COSMIC, BLAST, and more. |
| [pysam](skills/pysam/) | Genomic file toolkit. Read/write SAM/BAM/CRAM alignments, VCF/BCF variants, FASTA/FASTQ sequences, extract regions, calculate coverage, for NGS data processing pipelines. |

</details>

### Scientific Databases (Proteins, Pathways & Drugs)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [alphafold-database](skills/alphafold-database/) | Access AlphaFold's 200M+ AI-predicted protein structures. Retrieve structures by UniProt ID, download PDB/mmCIF files, analyze confidence metrics (pLDDT, PAE), for drug discovery and structural biology. |
| [pdb-database](skills/pdb-database/) | Access RCSB PDB for 3D protein/nucleic acid structures. Search by text/sequence/structure, download coordinates (PDB/mmCIF), retrieve metadata, for structural biology and drug discovery. |
| [uniprot-database](skills/uniprot-database/) | Direct REST API access to UniProt. Protein searches, FASTA retrieval, ID mapping, Swiss-Prot/TrEMBL. For multi-database workflows, prefer bioservices (unified interface to 40+ services). |
| [string-database](skills/string-database/) | Query STRING API for protein-protein interactions (59M proteins, 20B interactions). Network analysis, GO/KEGG enrichment, interaction discovery, 5000+ species, for systems biology. |
| [kegg-database](skills/kegg-database/) | Direct REST API access to KEGG (academic use). Pathway analysis, gene-pathway mapping, metabolic pathways, drug interactions, ID conversion. |
| [reactome-database](skills/reactome-database/) | Query Reactome REST API for pathway analysis, enrichment, gene-pathway mapping, disease pathways, molecular interactions, expression analysis, for systems biology. |
| [brenda-database](skills/brenda-database/) | Access BRENDA enzyme database via SOAP API. Retrieve kinetic parameters (Km, kcat), reaction equations, organism data, substrate-specific enzyme info for biochemical research. |
| [hmdb-database](skills/hmdb-database/) | Access Human Metabolome Database (220K+ metabolites). Search by name/ID/structure, retrieve chemical properties, biomarker data, NMR/MS spectra, pathways, for metabolomics. |
| [metabolomics-workbench-database](skills/metabolomics-workbench-database/) | Access NIH Metabolomics Workbench via REST API (4,200+ studies). Query metabolites, RefMet nomenclature, MS/NMR data, m/z searches, for metabolomics and biomarker discovery. |
| [pubchem-database](skills/pubchem-database/) | Query PubChem via PUG-REST API (110M+ compounds). Search by name/CID/SMILES, retrieve properties, similarity/substructure searches, bioactivity, for cheminformatics. |
| [chembl-database](skills/chembl-database/) | Query ChEMBL's bioactive molecules and drug discovery data. Search compounds by structure/properties, retrieve bioactivity data (IC50, Ki), find inhibitors, for medicinal chemistry. |
| [drugbank-database](skills/drugbank-database/) | Access comprehensive drug information from DrugBank including drug properties, interactions, targets, pathways, chemical structures, and pharmacology data. |
| [zinc-database](skills/zinc-database/) | Access ZINC (230M+ purchasable compounds). Search by ZINC ID/SMILES, similarity searches, 3D-ready structures for docking, analog discovery, for virtual screening. |
| [opentargets-database](skills/opentargets-database/) | Query Open Targets Platform for target-disease associations, drug target discovery, tractability/safety data, genetics/omics evidence, known drugs, for therapeutic target identification. |
| [fda-database](skills/fda-database/) | Query openFDA API for drugs, devices, adverse events, recalls, regulatory submissions (510k, PMA), substance identification (UNII), for FDA regulatory data analysis. |
| [pubmed-database](skills/pubmed-database/) | Direct REST API access to PubMed. Advanced Boolean/MeSH queries, E-utilities API, batch processing, citation management. |
| [openalex-database](skills/openalex-database/) | Query and analyze scholarly literature using the OpenAlex database. Search for academic papers, analyze research trends, find works by authors or institutions. |
| [biorxiv-database](skills/biorxiv-database/) | Search bioRxiv preprint server by keywords, authors, date ranges, or categories, retrieving paper metadata for life sciences preprint discovery. |
| [bioservices](skills/bioservices/) | Primary Python tool for 40+ bioinformatics services. Unified API for UniProt, KEGG, ChEMBL, PubChem, Reactome, QuickGO — preferred for multi-database workflows. |
| [uspto-database](skills/uspto-database/) | Access USPTO APIs for patent/trademark searches, examination history (PEDS), assignments, citations, office actions, for IP analysis and prior art searches. |

</details>

### Cancer Genomics Databases

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [cbioportal-database](skills/cbioportal-database/) | Query cBioPortal for cancer genomics: somatic mutations, copy number, gene expression, and survival data across hundreds of cancer studies. Cancer target validation, oncogene analysis, and patient-level genomic profiling. |
| [depmap](skills/depmap/) | Query the Cancer Dependency Map (DepMap) for cancer cell line gene dependency scores (CRISPR Chronos), drug sensitivity, and gene effect profiles. Identify cancer-specific vulnerabilities and synthetic lethal interactions. |
| [imaging-data-commons](skills/imaging-data-commons/) | Query and download public cancer imaging data from NCI Imaging Data Commons. Access radiology (CT, MR, PET) and pathology datasets for AI training or research. No authentication required. |

</details>

### Genomic & Molecular Databases

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bindingdb-database](skills/bindingdb-database/) | Query BindingDB for measured drug-target binding affinities (Ki, Kd, IC50, EC50). Drug discovery, lead optimization, polypharmacology, and SAR studies. |
| [gnomad-database](skills/gnomad-database/) | Query gnomAD for population allele frequencies, variant constraint scores (pLI, LOEUF), and loss-of-function intolerance. Variant pathogenicity interpretation and rare disease genetics. |
| [gtex-database](skills/gtex-database/) | Query GTEx for tissue-specific gene expression, eQTLs, and sQTLs. Link GWAS variants to gene regulation and interpret non-coding variant effects. |
| [interpro-database](skills/interpro-database/) | Query InterPro for protein family, domain, and functional site annotations. Integrates Pfam, PANTHER, PRINTS, SMART, and 11+ databases for protein function prediction. |
| [jaspar-database](skills/jaspar-database/) | Query JASPAR for transcription factor binding site profiles (PWMs/PFMs). Regulatory genomics, motif analysis, and GWAS regulatory variant interpretation. |
| [monarch-database](skills/monarch-database/) | Query the Monarch Initiative knowledge graph for disease-gene-phenotype associations. Integrates OMIM, ORPHANET, HPO, ClinVar for rare disease gene discovery. |
| [tiledbvcf](skills/tiledbvcf/) | Scalable VCF/BCF ingestion, storage, and parallel queries using TileDB for population genomics at scale. |

</details>

### Structural Biology & Drug Discovery

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [molecular-dynamics](skills/molecular-dynamics/) | Run and analyze molecular dynamics simulations with OpenMM and MDAnalysis. Protein/small molecule systems, force fields, energy minimization, RMSD/RMSF analysis, free energy surfaces. |
| [glycoengineering](skills/glycoengineering/) | Analyze and engineer protein glycosylation. Predict N/O-glycosylation sites, access glycoengineering tools (NetOGlyc, GlycoShield). Therapeutic antibody optimization and vaccine design. |
| [adaptyv](skills/adaptyv/) | Cloud laboratory platform for automated protein testing: binding assays, expression testing, thermostability, enzyme activity. Protein sequence optimization with NetSolP, SoluProt, ESM. |
| [ginkgo-cloud-lab](skills/ginkgo-cloud-lab/) | Submit and manage protocols on Ginkgo Bioworks Cloud Lab for autonomous lab execution. Cell-free protein expression, protocol workflows, and biotech automation. |

</details>

</details>

## 🧬 Bioinformatics (gptomics bio-* suite)

<details open>
<summary>Expand/Collapse this category</summary>

### Bioinformatics Tools & Pipelines

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [biopython](skills/biopython/) | Primary Python toolkit for molecular biology: PubMed/NCBI queries (Bio.Entrez), sequence manipulation, file parsing (FASTA, GenBank, FASTQ, PDB), BLAST workflows. |
| [scikit-bio](skills/scikit-bio/) | Biological data toolkit. Sequence analysis, alignments, phylogenetic trees, diversity metrics (alpha/beta, UniFrac), ordination (PCoA), PERMANOVA, for microbiome analysis. |
| [etetoolkit](skills/etetoolkit/) | Phylogenetic tree toolkit (ETE). Tree manipulation (Newick/NHX), evolutionary event detection, orthology/paralogy, NCBI taxonomy, visualization (PDF/SVG), for phylogenomics. |
| [deeptools](skills/deeptools/) | NGS analysis toolkit. BAM to bigWig conversion, QC (correlation, PCA, fingerprints), heatmaps/profiles (TSS, peaks), for ChIP-seq, RNA-seq, ATAC-seq visualization. |
| [nextflow-development](skills/nextflow-development/) | Run nf-core bioinformatics pipelines (rnaseq, sarek, atacseq) on sequencing data. Use for RNA-seq, WGS/WES, or ATAC-seq from local FASTQs or public datasets (GEO/SRA). |
| [fastq-analysis](skills/fastq-analysis/) | SRA downloading, FASTQ quality control, STAR alignment, gene quantification, and single-cell kallisto/bustools pipelines for bulk and single-cell sequencing data. |
| [geniml](skills/geniml/) | Genomic interval data (BED files) for machine learning tasks. Train region embeddings (Region2Vec, BEDspace), single-cell ATAC-seq analysis. |
| [gtars](skills/gtars/) | High-performance genomic interval analysis in Rust with Python bindings. Genomic regions, BED files, coverage tracks, overlap detection, tokenization for ML models. |
| [arboreto](skills/arboreto/) | Infer gene regulatory networks (GRNs) from gene expression data using GRNBoost2 and GENIE3 algorithms. For bulk RNA-seq and single-cell RNA-seq regulatory network inference. |
| [lamindb](skills/lamindb/) | Open-source biological data framework for queryable, traceable, reproducible, and FAIR datasets (scRNA-seq, genomics, imaging). |
| [dnanexus-integration](skills/dnanexus-integration/) | DNAnexus cloud genomics platform. Build apps/applets, manage data, dxpy Python SDK, run workflows, FASTQ/BAM/VCF, for genomics pipeline development. |
| [latchbio-integration](skills/latchbio-integration/) | Latch platform for bioinformatics workflows. Build pipelines with Latch SDK, @workflow/@task decorators, deploy serverless workflows, Nextflow/Snakemake integration. |

</details>

### Bioinformatics — Clinical Databases & Variant Analysis

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-clinical-databases-clinvar-lookup](skills/bio-clinical-databases-clinvar-lookup/) | Query ClinVar for clinical variant classifications, pathogenicity assertions, and review status. |
| [bio-clinical-databases-dbsnp-queries](skills/bio-clinical-databases-dbsnp-queries/) | Query dbSNP for SNP frequency, allele, and functional annotation data. |
| [bio-clinical-databases-gnomad-frequencies](skills/bio-clinical-databases-gnomad-frequencies/) | Retrieve population allele frequencies from gnomAD for rare variant interpretation. |
| [bio-clinical-databases-hla-typing](skills/bio-clinical-databases-hla-typing/) | HLA typing from sequencing data using standard typing tools and databases. |
| [bio-clinical-databases-myvariant-queries](skills/bio-clinical-databases-myvariant-queries/) | Batch query MyVariant.info for aggregated variant annotations from multiple databases. |
| [bio-clinical-databases-pharmacogenomics](skills/bio-clinical-databases-pharmacogenomics/) | PharmGKB/CPIC pharmacogenomics variant lookup for drug-gene interactions. |
| [bio-clinical-databases-polygenic-risk](skills/bio-clinical-databases-polygenic-risk/) | Calculate polygenic risk scores from GWAS summary statistics and genotype data. |
| [bio-clinical-databases-somatic-signatures](skills/bio-clinical-databases-somatic-signatures/) | Extract and classify mutational signatures from somatic variant catalogs (COSMIC). |
| [bio-clinical-databases-tumor-mutational-burden](skills/bio-clinical-databases-tumor-mutational-burden/) | Compute tumor mutational burden (TMB) from somatic variant calls. |
| [bio-clinical-databases-variant-prioritization](skills/bio-clinical-databases-variant-prioritization/) | Rank and filter candidate variants by pathogenicity scores, inheritance, and phenotype match. |
| [bio-variant-calling](skills/bio-variant-calling/) | GATK-based germline variant calling pipeline from aligned BAM/CRAM files. |
| [bio-variant-calling-clinical-interpretation](skills/bio-variant-calling-clinical-interpretation/) | Interpret variant calls in clinical context with ACMG guidelines. |
| [bio-variant-calling-deepvariant](skills/bio-variant-calling-deepvariant/) | DeepVariant deep-learning variant caller for short-read WGS/WES data. |
| [bio-variant-calling-filtering-best-practices](skills/bio-variant-calling-filtering-best-practices/) | Apply VQSR and hard-filtering best practices to variant call sets. |
| [bio-variant-calling-joint-calling](skills/bio-variant-calling-joint-calling/) | Joint genotyping across multiple samples for improved variant discovery. |
| [bio-variant-calling-structural-variant-calling](skills/bio-variant-calling-structural-variant-calling/) | Call structural variants (SVs) from long-read or paired-end sequencing. |
| [bio-variant-annotation](skills/bio-variant-annotation/) | Annotate VCF files with functional, population, and clinical consequence data. |
| [bio-variant-normalization](skills/bio-variant-normalization/) | Normalize variant representations (left-alignment, decomposition) for consistent comparison. |
| [bio-vcf-basics](skills/bio-vcf-basics/) | Read, write, and parse VCF files; filter by quality, region, and sample. |
| [bio-vcf-manipulation](skills/bio-vcf-manipulation/) | Advanced VCF manipulation: merging, splitting, reformatting, subset extraction. |
| [bio-vcf-statistics](skills/bio-vcf-statistics/) | Compute variant statistics: ts/tv ratio, heterozygosity, depth distributions. |
| [bio-gatk-variant-calling](skills/bio-gatk-variant-calling/) | End-to-end GATK HaplotypeCaller variant calling with BQSR and joint genotyping. |
| [bio-copy-number-cnv-annotation](skills/bio-copy-number-cnv-annotation/) | Annotate CNV calls with gene content, database overlap, and clinical significance. |
| [bio-copy-number-cnv-visualization](skills/bio-copy-number-cnv-visualization/) | Visualize copy number profiles and segment plots from WGS/WES data. |
| [bio-copy-number-cnvkit-analysis](skills/bio-copy-number-cnvkit-analysis/) | CNVKit copy number analysis for targeted sequencing and WES data. |
| [bio-copy-number-gatk-cnv](skills/bio-copy-number-gatk-cnv/) | GATK4 somatic copy number alteration calling pipeline. |
| [bio-tumor-fraction-estimation](skills/bio-tumor-fraction-estimation/) | Estimate tumor purity and ploidy from allele frequencies and copy number data. |
| [bio-ctdna-mutation-detection](skills/bio-ctdna-mutation-detection/) | Detect circulating tumor DNA mutations from liquid biopsy ultra-deep sequencing. |
| [bio-cfdna-preprocessing](skills/bio-cfdna-preprocessing/) | Process cell-free DNA sequencing data: adapter trimming, deduplication, QC. |
| [bio-methylation-based-detection](skills/bio-methylation-based-detection/) | Detect methylation-based cancer signals from cfDNA methylation data. |
| [bio-longitudinal-monitoring](skills/bio-longitudinal-monitoring/) | Track somatic variant evolution and clonal dynamics across serial samples. |

</details>

### Bioinformatics — Sequencing & Read QC

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-fastq-quality](skills/bio-fastq-quality/) | Assess FASTQ read quality with FastQC/MultiQC; generate per-sample QC reports. |
| [bio-read-qc-adapter-trimming](skills/bio-read-qc-adapter-trimming/) | Trim sequencing adapters with Trimmomatic, Cutadapt, or fastp. |
| [bio-read-qc-contamination-screening](skills/bio-read-qc-contamination-screening/) | Screen reads for human/microbial contamination using FastQ Screen or Kraken. |
| [bio-read-qc-fastp-workflow](skills/bio-read-qc-fastp-workflow/) | End-to-end read QC and preprocessing with fastp including UMI handling. |
| [bio-read-qc-quality-filtering](skills/bio-read-qc-quality-filtering/) | Apply quality-score and length filters to remove low-quality reads. |
| [bio-read-qc-quality-reports](skills/bio-read-qc-quality-reports/) | Aggregate multi-sample QC reports with MultiQC. |
| [bio-read-qc-umi-processing](skills/bio-read-qc-umi-processing/) | Deduplicate PCR duplicates using UMI-tools for accurate quantification. |
| [bio-paired-end-fastq](skills/bio-paired-end-fastq/) | Handle paired-end FASTQ files: validation, interleaving, splitting. |
| [bio-alignment-io](skills/bio-alignment-io/) | Read/write SAM/BAM/CRAM alignment files with pysam and samtools. |
| [bio-alignment-msa-parsing](skills/bio-alignment-msa-parsing/) | Parse and analyze multiple sequence alignments (FASTA, ClustalW, Stockholm). |
| [bio-alignment-msa-statistics](skills/bio-alignment-msa-statistics/) | Compute MSA statistics: conservation, gap content, entropy. |
| [bio-alignment-pairwise](skills/bio-alignment-pairwise/) | Pairwise sequence alignment using Smith-Waterman, Needleman-Wunsch, BLAST. |
| [bio-longread-alignment](skills/bio-longread-alignment/) | Align long reads (ONT/PacBio) with minimap2; sort and index BAM files. |
| [bio-longread-qc](skills/bio-longread-qc/) | Quality control for long-read sequencing: read length, N50, error rate. |
| [bio-longread-medaka](skills/bio-longread-medaka/) | Consensus polishing and variant calling with Oxford Nanopore Medaka. |
| [bio-longread-structural-variants](skills/bio-longread-structural-variants/) | Call large structural variants from long-read data with Sniffles/PBSV. |
| [bio-basecalling](skills/bio-basecalling/) | Base-call raw ONT signals with Dorado/Guppy; convert FAST5 to FASTQ. |
| [bio-compressed-files](skills/bio-compressed-files/) | Handle compressed bioinformatics files: bgzip, tabix, zstd, htslib. |
| [bio-format-conversion](skills/bio-format-conversion/) | Convert between bioinformatics formats: FASTQ↔FASTA, BAM↔CRAM, BED↔GTF. |
| [bio-sequence-statistics](skills/bio-sequence-statistics/) | Compute sequence statistics: GC content, length distributions, complexity. |
| [bio-read-sequences](skills/bio-read-sequences/) | Read and iterate over biological sequences from FASTA/FASTQ files. |
| [bio-write-sequences](skills/bio-write-sequences/) | Write biological sequences to FASTA/FASTQ with metadata preservation. |
| [bio-filter-sequences](skills/bio-filter-sequences/) | Filter sequences by length, quality, pattern, or taxonomy label. |
| [bio-batch-processing](skills/bio-batch-processing/) | Batch-process large bioinformatics datasets across samples and cohorts. |
| [bio-rnaseq-qc](skills/bio-rnaseq-qc/) | RNA-seq specific QC: strandedness, rRNA contamination, gene body coverage. |
| [bio-long-read-sequencing-clair3-variants](skills/bio-long-read-sequencing-clair3-variants/) | Call variants from long-read sequencing with Clair3 deep-learning model. |
| [bio-long-read-sequencing-isoseq-analysis](skills/bio-long-read-sequencing-isoseq-analysis/) | Iso-Seq full-length transcript analysis for isoform discovery. |
| [bio-long-read-sequencing-nanopore-methylation](skills/bio-long-read-sequencing-nanopore-methylation/) | Call CpG methylation from Oxford Nanopore sequencing with Modbam2bed. |
| [bio-splicing-qc](skills/bio-splicing-qc/) | RNA splicing quality assessment: junction read coverage, novel splice sites. |
| [bio-splicing-quantification](skills/bio-splicing-quantification/) | Quantify alternative splicing events: PSI/inclusion levels per isoform. |
| [bio-sashimi-plots](skills/bio-sashimi-plots/) | Generate sashimi plots for visualizing RNA-seq splicing at specific loci. |
| [bio-consensus-sequences](skills/bio-consensus-sequences/) | Generate consensus FASTA sequences by applying VCF variants to a reference using `bcftools consensus`; useful for sample-specific references and haplotype reconstruction. |

</details>

### Bioinformatics — Differential Expression & Transcriptomics

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-de-deseq2-basics](skills/bio-de-deseq2-basics/) | DESeq2 differential expression analysis: design matrix, size factors, dispersion. |
| [bio-de-edger-basics](skills/bio-de-edger-basics/) | EdgeR differential expression for count data with empirical Bayes dispersion. |
| [bio-de-results](skills/bio-de-results/) | Extract, filter, and annotate DESeq2/EdgeR results tables. |
| [bio-de-visualization](skills/bio-de-visualization/) | Volcano plots, MA plots, and heatmaps for differential expression results. |
| [bio-differential-expression-batch-correction](skills/bio-differential-expression-batch-correction/) | Remove batch effects with ComBat/limma for multi-cohort DE analysis. |
| [bio-differential-expression-timeseries-de](skills/bio-differential-expression-timeseries-de/) | Time-series differential expression with splines and mixed models. |
| [bio-differential-splicing](skills/bio-differential-splicing/) | Detect differential alternative splicing events with rMATS or MAJIQ. |
| [bio-isoform-switching](skills/bio-isoform-switching/) | Identify isoform switching events with DRIMSeq and IsoformSwitchAnalyzeR. |
| [bio-ribo-seq-orf-detection](skills/bio-ribo-seq-orf-detection/) | Detect translated ORFs from ribosome profiling data with RiboTaper/Ribo-TISH. |
| [bio-ribo-seq-riboseq-preprocessing](skills/bio-ribo-seq-riboseq-preprocessing/) | Preprocess ribosome profiling reads: adapter trimming, rRNA removal, alignment. |
| [bio-ribo-seq-ribosome-periodicity](skills/bio-ribo-seq-ribosome-periodicity/) | Assess triplet periodicity and ribosome footprint quality in Ribo-seq data. |
| [bio-ribo-seq-ribosome-stalling](skills/bio-ribo-seq-ribosome-stalling/) | Identify ribosome stalling sites and pausing from Ribo-seq profiles. |
| [bio-ribo-seq-translation-efficiency](skills/bio-ribo-seq-translation-efficiency/) | Compute translation efficiency ratios from matched RNA-seq and Ribo-seq. |

</details>

### Bioinformatics — Pathway & Network Analysis

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-pathway-go-enrichment](skills/bio-pathway-go-enrichment/) | Gene Ontology enrichment analysis with clusterProfiler or g:Profiler. |
| [bio-pathway-gsea](skills/bio-pathway-gsea/) | Gene Set Enrichment Analysis (GSEA) with pre-ranked or count-based statistics. |
| [bio-pathway-kegg-pathways](skills/bio-pathway-kegg-pathways/) | KEGG pathway enrichment and visualization for metabolic/signaling pathways. |
| [bio-pathway-reactome](skills/bio-pathway-reactome/) | Reactome pathway analysis with hierarchical enrichment and visualization. |
| [bio-pathway-wikipathways](skills/bio-pathway-wikipathways/) | WikiPathways enrichment and network visualization. |
| [bio-pathway-enrichment-visualization](skills/bio-pathway-enrichment-visualization/) | Dot plots, enrichment maps, and network visualizations for pathway results. |

</details>

### Bioinformatics — Single-Cell & Spatial Omics

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-single-cell-batch-integration](skills/bio-single-cell-batch-integration/) | Integrate scRNA-seq datasets across batches with Harmony, BBKNN, scVI. |
| [bio-single-cell-cell-annotation](skills/bio-single-cell-cell-annotation/) | Annotate single-cell clusters using marker genes and reference atlases. |
| [bio-single-cell-cell-communication](skills/bio-single-cell-cell-communication/) | Infer ligand-receptor cell-cell communication with CellChat or NicheNet. |
| [bio-single-cell-clustering](skills/bio-single-cell-clustering/) | Cluster single cells with Leiden/Louvain algorithms in Scanpy/Seurat. |
| [bio-single-cell-data-io](skills/bio-single-cell-data-io/) | Read/write AnnData, Seurat, and 10x Genomics h5ad/h5 formats. |
| [bio-single-cell-doublet-detection](skills/bio-single-cell-doublet-detection/) | Remove doublets from scRNA-seq with Scrublet or DoubletFinder. |
| [bio-single-cell-lineage-tracing](skills/bio-single-cell-lineage-tracing/) | Reconstruct cell lineage trees from scRNA-seq with clonal barcodes. |
| [bio-single-cell-markers-annotation](skills/bio-single-cell-markers-annotation/) | Identify cluster marker genes and auto-annotate cell types. |
| [bio-single-cell-metabolite-communication](skills/bio-single-cell-metabolite-communication/) | Infer metabolite-mediated intercellular communication from scRNA-seq. |
| [bio-single-cell-multimodal-integration](skills/bio-single-cell-multimodal-integration/) | Integrate scRNA-seq with ATAC, CITE-seq, or spatial using WNN/MultiVI. |
| [bio-single-cell-perturb-seq](skills/bio-single-cell-perturb-seq/) | Analyze genetic perturbation screens from Perturb-seq / CROP-seq data. |
| [bio-single-cell-preprocessing](skills/bio-single-cell-preprocessing/) | Single-cell preprocessing: count filtering, normalization, HVG selection. |
| [bio-single-cell-scatac-analysis](skills/bio-single-cell-scatac-analysis/) | scATAC-seq peak calling, TF motif enrichment, and chromatin accessibility. |
| [bio-single-cell-splicing](skills/bio-single-cell-splicing/) | RNA velocity and splicing dynamics with scVelo or Alevin. |
| [bio-single-cell-trajectory-inference](skills/bio-single-cell-trajectory-inference/) | Infer pseudotime trajectories with Monocle3, PAGA, or Slingshot. |
| [bio-spatial-transcriptomics-image-analysis](skills/bio-spatial-transcriptomics-image-analysis/) | Analyze histology images co-registered with spatial transcriptomics data. |
| [bio-spatial-transcriptomics-spatial-communication](skills/bio-spatial-transcriptomics-spatial-communication/) | Ligand-receptor communication analysis with spatial context (COMMOT, SpatialDE). |
| [bio-spatial-transcriptomics-spatial-data-io](skills/bio-spatial-transcriptomics-spatial-data-io/) | Load and process Visium, Slide-seq, MERFISH, and STARmap datasets. |
| [bio-spatial-transcriptomics-spatial-deconvolution](skills/bio-spatial-transcriptomics-spatial-deconvolution/) | Deconvolve cell type proportions in spatial spots with RCTD, SPOTlight. |
| [bio-spatial-transcriptomics-spatial-domains](skills/bio-spatial-transcriptomics-spatial-domains/) | Identify spatially variable genes and tissue domains with SpatialDE/BANKSY. |
| [bio-spatial-transcriptomics-spatial-multiomics](skills/bio-spatial-transcriptomics-spatial-multiomics/) | Integrate spatial transcriptomics with proteomics, metabolomics, or imaging. |
| [bio-spatial-transcriptomics-spatial-neighbors](skills/bio-spatial-transcriptomics-spatial-neighbors/) | Build spatial neighbor graphs and perform neighborhood enrichment analysis. |
| [bio-spatial-transcriptomics-spatial-preprocessing](skills/bio-spatial-transcriptomics-spatial-preprocessing/) | Preprocess spatial transcriptomics: QC, normalization, spot filtering. |
| [bio-spatial-transcriptomics-spatial-proteomics](skills/bio-spatial-transcriptomics-spatial-proteomics/) | Analyze spatial proteomics data from CODEX, IMC, or MIBI platforms. |
| [bio-spatial-transcriptomics-spatial-statistics](skills/bio-spatial-transcriptomics-spatial-statistics/) | Spatial statistics: Moran's I, spatial autocorrelation, co-localization. |
| [bio-spatial-transcriptomics-spatial-visualization](skills/bio-spatial-transcriptomics-spatial-visualization/) | Visualize spatial gene expression maps and tissue section overlays. |

</details>

### Bioinformatics — Epigenomics & Chromatin

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-atac-seq-atac-peak-calling](skills/bio-atac-seq-atac-peak-calling/) | Call ATAC-seq chromatin accessibility peaks with MACS2/MACS3. |
| [bio-atac-seq-atac-qc](skills/bio-atac-seq-atac-qc/) | ATAC-seq quality control: TSS enrichment, fragment size, FRiP score. |
| [bio-atac-seq-differential-accessibility](skills/bio-atac-seq-differential-accessibility/) | Differential chromatin accessibility between conditions with DESeq2/DiffBind. |
| [bio-atac-seq-footprinting](skills/bio-atac-seq-footprinting/) | Transcription factor footprinting from ATAC-seq with TOBIAS or HINT-ATAC. |
| [bio-atac-seq-motif-deviation](skills/bio-atac-seq-motif-deviation/) | TF motif deviation scoring with chromVAR for single-cell ATAC data. |
| [bio-atac-seq-nucleosome-positioning](skills/bio-atac-seq-nucleosome-positioning/) | Infer nucleosome positioning from ATAC-seq fragment length distributions. |
| [bio-chipseq-differential-binding](skills/bio-chipseq-differential-binding/) | Differential ChIP-seq binding analysis with DiffBind. |
| [bio-chipseq-motif-analysis](skills/bio-chipseq-motif-analysis/) | De novo and known motif discovery from ChIP-seq peaks with HOMER/MEME. |
| [bio-chipseq-peak-annotation](skills/bio-chipseq-peak-annotation/) | Annotate ChIP-seq peaks with genomic features and nearest genes. |
| [bio-chipseq-peak-calling](skills/bio-chipseq-peak-calling/) | Call ChIP-seq peaks with MACS2 for TF binding and histone marks. |
| [bio-chipseq-qc](skills/bio-chipseq-qc/) | ChIP-seq quality metrics: FRiP, SCC, phantompeakqualtools. |
| [bio-chipseq-super-enhancers](skills/bio-chipseq-super-enhancers/) | Identify super enhancers from H3K27ac ChIP-seq with ROSE. |
| [bio-chipseq-visualization](skills/bio-chipseq-visualization/) | Heatmaps and aggregate profiles at peak regions with deepTools. |
| [bio-hi-c-analysis-compartment-analysis](skills/bio-hi-c-analysis-compartment-analysis/) | Call A/B compartments from Hi-C contact matrices. |
| [bio-hi-c-analysis-contact-pairs](skills/bio-hi-c-analysis-contact-pairs/) | Process Hi-C contact pairs: filtering, deduplication, binning. |
| [bio-hi-c-analysis-hic-data-io](skills/bio-hi-c-analysis-hic-data-io/) | Read and write Hi-C data formats: .hic, cool, mcool with cooler/hicstuff. |
| [bio-hi-c-analysis-hic-differential](skills/bio-hi-c-analysis-hic-differential/) | Differential Hi-C interaction analysis between conditions. |
| [bio-hi-c-analysis-hic-visualization](skills/bio-hi-c-analysis-hic-visualization/) | Visualize Hi-C contact maps, TADs, and loops with pyGenomeTracks. |
| [bio-hi-c-analysis-loop-calling](skills/bio-hi-c-analysis-loop-calling/) | Detect chromatin loops from Hi-C data with Mustache or HICCUPS. |
| [bio-hi-c-analysis-matrix-operations](skills/bio-hi-c-analysis-matrix-operations/) | Normalize Hi-C matrices: ICE, KR, VC; compute observed/expected. |
| [bio-hi-c-analysis-tad-detection](skills/bio-hi-c-analysis-tad-detection/) | Identify topologically associating domains (TADs) from Hi-C data. |
| [bio-methylation-bismark-alignment](skills/bio-methylation-bismark-alignment/) | Align bisulfite sequencing reads and extract CpG methylation with Bismark. |
| [bio-methylation-calling](skills/bio-methylation-calling/) | Call CpG methylation from WGBS/RRBS alignments. |
| [bio-methylation-dmr-detection](skills/bio-methylation-dmr-detection/) | Identify differentially methylated regions (DMRs) with DSS or MethylKit. |
| [bio-methylation-methylkit](skills/bio-methylation-methylkit/) | Methylation analysis with MethylKit: CpG tiles, DMR calling, annotation. |

</details>

### Bioinformatics — Metagenomics & Microbiome

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-metagenomics-abundance](skills/bio-metagenomics-abundance/) | Estimate microbial taxon abundances from shotgun metagenomics. |
| [bio-metagenomics-amr-detection](skills/bio-metagenomics-amr-detection/) | Detect antimicrobial resistance genes with AMRFinder or RGI/CARD. |
| [bio-metagenomics-functional-profiling](skills/bio-metagenomics-functional-profiling/) | Functional profiling of metagenomes with HUMAnN3 for pathway/gene families. |
| [bio-metagenomics-kraken](skills/bio-metagenomics-kraken/) | Taxonomic classification of metagenomic reads with Kraken2/Bracken. |
| [bio-metagenomics-metaphlan](skills/bio-metagenomics-metaphlan/) | Clade-specific marker-based profiling of microbial communities with MetaPhlAn4. |
| [bio-metagenomics-strain-tracking](skills/bio-metagenomics-strain-tracking/) | Track microbial strains across samples with StrainPhlan or inStrain. |
| [bio-metagenomics-visualization](skills/bio-metagenomics-visualization/) | Visualize microbiome composition with Krona charts and stacked bar plots. |
| [bio-microbiome-amplicon-processing](skills/bio-microbiome-amplicon-processing/) | Process 16S/ITS amplicon sequencing with QIIME2 or DADA2. |
| [bio-microbiome-differential-abundance](skills/bio-microbiome-differential-abundance/) | Test differential microbial abundance with ANCOM-BC, MaAsLin2, or ALDEx2. |
| [bio-microbiome-diversity-analysis](skills/bio-microbiome-diversity-analysis/) | Alpha/beta diversity analysis: Shannon, PD, UniFrac, PCoA. |
| [bio-microbiome-functional-prediction](skills/bio-microbiome-functional-prediction/) | Predict functional capacity from 16S data with PICRUSt2 or Tax4Fun. |
| [bio-microbiome-qiime2-workflow](skills/bio-microbiome-qiime2-workflow/) | End-to-end QIIME2 workflow: denoising, diversity, differential abundance. |
| [bio-microbiome-taxonomy-assignment](skills/bio-microbiome-taxonomy-assignment/) | Assign taxonomy to ASVs/OTUs using SILVA, GTDB, or Greengenes2. |

</details>

### Bioinformatics — Immunoinformatics & Flow Cytometry

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-immunoinformatics-epitope-prediction](skills/bio-immunoinformatics-epitope-prediction/) | Predict MHC-I/II epitopes from protein sequences with NetMHCpan/MHCflurry. |
| [bio-immunoinformatics-immunogenicity-scoring](skills/bio-immunoinformatics-immunogenicity-scoring/) | Score peptide immunogenicity for vaccine and neoantigen prioritization. |
| [bio-immunoinformatics-mhc-binding-prediction](skills/bio-immunoinformatics-mhc-binding-prediction/) | Predict peptide-MHC binding affinities for multiple alleles. |
| [bio-immunoinformatics-neoantigen-prediction](skills/bio-immunoinformatics-neoantigen-prediction/) | Predict neoantigens from somatic mutations for personalized cancer vaccines. |
| [bio-immunoinformatics-tcr-epitope-binding](skills/bio-immunoinformatics-tcr-epitope-binding/) | Predict TCR-epitope binding with ERGO, pMTnet, or NetTCR. |
| [bio-tcr-bcr-analysis-immcantation-analysis](skills/bio-tcr-bcr-analysis-immcantation-analysis/) | Analyze B/T cell receptor repertoires with the Immcantation suite. |
| [bio-tcr-bcr-analysis-mixcr-analysis](skills/bio-tcr-bcr-analysis-mixcr-analysis/) | MiXCR V(D)J alignment and clonotype assembly for immune repertoires. |
| [bio-tcr-bcr-analysis-repertoire-visualization](skills/bio-tcr-bcr-analysis-repertoire-visualization/) | Visualize repertoire diversity, clonal expansion, and V-gene usage. |
| [bio-tcr-bcr-analysis-scirpy-analysis](skills/bio-tcr-bcr-analysis-scirpy-analysis/) | Single-cell TCR/BCR analysis integrated with scRNA-seq using Scirpy. |
| [bio-tcr-bcr-analysis-vdjtools-analysis](skills/bio-tcr-bcr-analysis-vdjtools-analysis/) | Immune repertoire statistics and overlap analysis with VDJtools. |
| [bio-flow-cytometry-bead-normalization](skills/bio-flow-cytometry-bead-normalization/) | Normalize flow cytometry data using calibration beads. |
| [bio-flow-cytometry-clustering-phenotyping](skills/bio-flow-cytometry-clustering-phenotyping/) | Cluster and phenotype cell populations with FlowSOM, PhenoGraph, or UMAP. |
| [bio-flow-cytometry-compensation-transformation](skills/bio-flow-cytometry-compensation-transformation/) | Apply compensation matrices and biexponential/arcsinh transformations. |
| [bio-flow-cytometry-cytometry-qc](skills/bio-flow-cytometry-cytometry-qc/) | Quality control for flow/mass cytometry: signal drift, spillover, outlier detection. |
| [bio-flow-cytometry-differential-analysis](skills/bio-flow-cytometry-differential-analysis/) | Statistical comparison of cell populations between conditions. |
| [bio-flow-cytometry-doublet-detection](skills/bio-flow-cytometry-doublet-detection/) | Detect and remove doublets from flow cytometry data. |
| [bio-flow-cytometry-fcs-handling](skills/bio-flow-cytometry-fcs-handling/) | Read, write, and manipulate FCS files with FlowCore/FlowKit. |
| [bio-flow-cytometry-gating-analysis](skills/bio-flow-cytometry-gating-analysis/) | Manual and algorithmic gating strategies for cell population identification. |
| [bio-imaging-mass-cytometry-cell-segmentation](skills/bio-imaging-mass-cytometry-cell-segmentation/) | Segment cells in IMC images with Mesmer or CellProfiler. |
| [bio-imaging-mass-cytometry-data-preprocessing](skills/bio-imaging-mass-cytometry-data-preprocessing/) | Preprocess imaging mass cytometry data: hot pixel removal, normalization. |
| [bio-imaging-mass-cytometry-interactive-annotation](skills/bio-imaging-mass-cytometry-interactive-annotation/) | Interactively annotate cell types in IMC spatial datasets. |
| [bio-imaging-mass-cytometry-phenotyping](skills/bio-imaging-mass-cytometry-phenotyping/) | Phenotype immune and tumor cells from multi-marker IMC panels. |
| [bio-imaging-mass-cytometry-quality-metrics](skills/bio-imaging-mass-cytometry-quality-metrics/) | Quality metrics for IMC acquisitions: signal-to-noise, tissue coverage. |
| [bio-imaging-mass-cytometry-spatial-analysis](skills/bio-imaging-mass-cytometry-spatial-analysis/) | Spatial cell neighborhood analysis from imaging mass cytometry data. |

</details>

### Bioinformatics — Multi-Omics Integration

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-multi-omics-data-harmonization](skills/bio-multi-omics-data-harmonization/) | Harmonize multi-omics datasets: sample matching, batch correction, feature alignment. |
| [bio-multi-omics-mixomics-analysis](skills/bio-multi-omics-mixomics-analysis/) | Multi-omics factor analysis with mixOmics (DIABLO, MOFA, sPLS-DA). |
| [bio-multi-omics-mofa-integration](skills/bio-multi-omics-mofa-integration/) | Multi-Omics Factor Analysis (MOFA+) for latent factor discovery across modalities. |
| [bio-multi-omics-similarity-network](skills/bio-multi-omics-similarity-network/) | Similarity Network Fusion (SNF) for patient stratification from multi-omics. |

</details>

### Bioinformatics — Proteomics & Metabolomics

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-proteomics-data-import](skills/bio-proteomics-data-import/) | Import DDA/DIA proteomics data from MaxQuant, Proteome Discoverer, FragPipe. |
| [bio-proteomics-dia-analysis](skills/bio-proteomics-dia-analysis/) | DIA proteomics analysis with DIA-NN or Spectronaut. |
| [bio-proteomics-differential-abundance](skills/bio-proteomics-differential-abundance/) | Differential protein abundance with limma, MSstats, or DEqMS. |
| [bio-proteomics-peptide-identification](skills/bio-proteomics-peptide-identification/) | Peptide spectrum matching and database search result parsing. |
| [bio-proteomics-protein-inference](skills/bio-proteomics-protein-inference/) | Protein grouping, parsimony, and FDR control for proteomics experiments. |
| [bio-proteomics-proteomics-qc](skills/bio-proteomics-proteomics-qc/) | Proteomics QC: peptide counts, coverage, missing values, CV. |
| [bio-proteomics-ptm-analysis](skills/bio-proteomics-ptm-analysis/) | Post-translational modification analysis: phospho, ubiquitin, glycan enrichment. |
| [bio-proteomics-quantification](skills/bio-proteomics-quantification/) | Label-free, TMT/iTRAQ, and SILAC quantification workflows. |
| [bio-proteomics-spectral-libraries](skills/bio-proteomics-spectral-libraries/) | Build and use spectral libraries for DIA data analysis. |
| [bio-metabolomics-lipidomics](skills/bio-metabolomics-lipidomics/) | Lipidomics data analysis: lipid class annotation, fatty acid composition. |
| [bio-metabolomics-metabolite-annotation](skills/bio-metabolomics-metabolite-annotation/) | Annotate mass spec features with HMDB, MZmine, SIRIUS, or MetFrag. |
| [bio-metabolomics-msdial-preprocessing](skills/bio-metabolomics-msdial-preprocessing/) | MS-DIAL-based LC-MS/GC-MS data preprocessing and peak detection. |
| [bio-metabolomics-normalization-qc](skills/bio-metabolomics-normalization-qc/) | Metabolomics normalization: PQN, LOESS, median, batch correction. |
| [bio-metabolomics-pathway-mapping](skills/bio-metabolomics-pathway-mapping/) | Map identified metabolites to KEGG, MetaCyc, or Reactome pathways. |
| [bio-metabolomics-statistical-analysis](skills/bio-metabolomics-statistical-analysis/) | Univariate/multivariate stats for metabolomics: PCA, PLS-DA, ANOVA. |
| [bio-metabolomics-targeted-analysis](skills/bio-metabolomics-targeted-analysis/) | Targeted metabolomics with MRM/SRM: calibration curves, quantification. |
| [bio-metabolomics-xcms-preprocessing](skills/bio-metabolomics-xcms-preprocessing/) | XCMS-based LC-MS peak detection, alignment, and grouping. |

</details>

### Bioinformatics — Structural Biology & Cheminformatics

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-structural-biology-alphafold-predictions](skills/bio-structural-biology-alphafold-predictions/) | Use AlphaFold2/3 predictions: model quality assessment, confidence scores. |
| [bio-structural-biology-modern-structure-prediction](skills/bio-structural-biology-modern-structure-prediction/) | Modern structure prediction with ESMFold, RoseTTAFold, and OpenFold. |
| [bio-pdb-geometric-analysis](skills/bio-pdb-geometric-analysis/) | Geometric analysis of protein structures: distances, angles, contacts, RMSD. |
| [bio-pdb-structure-io](skills/bio-pdb-structure-io/) | Read and write PDB/mmCIF structure files with BioPython or Gemmi. |
| [bio-pdb-structure-modification](skills/bio-pdb-structure-modification/) | Modify protein structures: add hydrogens, mutate residues, energy minimize. |
| [bio-pdb-structure-navigation](skills/bio-pdb-structure-navigation/) | Navigate and inspect PDB structures: chain, residue, atom selection. |
| [bio-molecular-descriptors](skills/bio-molecular-descriptors/) | Calculate molecular descriptors (RDKit): MW, LogP, TPSA, fingerprints. |
| [bio-molecular-io](skills/bio-molecular-io/) | Read/write chemical structure formats: SDF, SMILES, MOL2, PDB with RDKit. |
| [bio-reaction-enumeration](skills/bio-reaction-enumeration/) | Enumerate reactions and products from SMARTS reaction templates. |
| [bio-similarity-searching](skills/bio-similarity-searching/) | Molecular similarity search: Tanimoto, fingerprint-based, scaffold hopping. |
| [bio-substructure-search](skills/bio-substructure-search/) | Substructure searching in chemical databases using SMARTS patterns. |
| [bio-virtual-screening](skills/bio-virtual-screening/) | Virtual screening workflows: docking, scoring, pose filtering with AutoDock/Vina. |
| [bio-admet-prediction](skills/bio-admet-prediction/) | Predict ADMET properties: absorption, distribution, metabolism, excretion, toxicity. |

</details>

### Bioinformatics — Epidemiological & Causal Genomics

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-epidemiological-genomics-amr-surveillance](skills/bio-epidemiological-genomics-amr-surveillance/) | Antimicrobial resistance surveillance from genomic epidemiology data. |
| [bio-epidemiological-genomics-pathogen-typing](skills/bio-epidemiological-genomics-pathogen-typing/) | Pathogen molecular typing: MLST, wgMLST, cgMLST for outbreak analysis. |
| [bio-epidemiological-genomics-phylodynamics](skills/bio-epidemiological-genomics-phylodynamics/) | Phylodynamics: molecular clock, population dynamics, BEAST2/TreeTime. |
| [bio-epidemiological-genomics-transmission-inference](skills/bio-epidemiological-genomics-transmission-inference/) | Infer transmission networks from pathogen genomics with TransPhylo/outbreaker2. |
| [bio-epidemiological-genomics-variant-surveillance](skills/bio-epidemiological-genomics-variant-surveillance/) | Track pathogen variant emergence and spread from genomic surveillance. |
| [bio-causal-genomics-colocalization-analysis](skills/bio-causal-genomics-colocalization-analysis/) | Colocalization analysis of GWAS and eQTL signals with coloc or eCAVIAR. |
| [bio-causal-genomics-fine-mapping](skills/bio-causal-genomics-fine-mapping/) | Fine-map causal variants at GWAS loci with SuSiE or FINEMAP. |
| [bio-causal-genomics-mediation-analysis](skills/bio-causal-genomics-mediation-analysis/) | Causal mediation analysis for gene expression intermediaries. |
| [bio-causal-genomics-mendelian-randomization](skills/bio-causal-genomics-mendelian-randomization/) | Two-sample Mendelian randomization with MR-Base/TwoSampleMR. |
| [bio-causal-genomics-pleiotropy-detection](skills/bio-causal-genomics-pleiotropy-detection/) | Detect horizontal pleiotropy and heterogeneity in MR analyses. |
| [bio-genome-engineering-base-editing-design](skills/bio-genome-engineering-base-editing-design/) | Design base editors (CBE/ABE) for precise single-base correction. |
| [bio-genome-engineering-grna-design](skills/bio-genome-engineering-grna-design/) | Design and score CRISPR guide RNAs with Cas-OFFinder and CRISPOR. |
| [bio-genome-engineering-hdr-template-design](skills/bio-genome-engineering-hdr-template-design/) | Design HDR templates for precise knock-in via homology-directed repair. |
| [bio-genome-engineering-off-target-prediction](skills/bio-genome-engineering-off-target-prediction/) | Predict CRISPR off-target sites genome-wide for safety assessment. |
| [bio-genome-engineering-prime-editing-design](skills/bio-genome-engineering-prime-editing-design/) | Design pegRNAs and nickase gRNAs for prime editing experiments. |
| [bio-crispr-screens-base-editing-analysis](skills/bio-crispr-screens-base-editing-analysis/) | Analyze base editing screens: guide efficiency, editing outcomes. |
| [bio-crispr-screens-batch-correction](skills/bio-crispr-screens-batch-correction/) | Correct batch effects in CRISPR screen data across replicates. |
| [bio-crispr-screens-crispresso-editing](skills/bio-crispr-screens-crispresso-editing/) | Quantify editing outcomes with CRISPResso2 from amplicon sequencing. |
| [bio-crispr-screens-hit-calling](skills/bio-crispr-screens-hit-calling/) | Call hits from CRISPR screens using MAGeCK, BAGEL2, or casTLE. |
| [bio-crispr-screens-jacks-analysis](skills/bio-crispr-screens-jacks-analysis/) | CRISPR screen analysis with JACKS hierarchical Bayesian model. |
| [bio-crispr-screens-library-design](skills/bio-crispr-screens-library-design/) | Design CRISPR screen libraries: guide selection, controls, coverage. |
| [bio-crispr-screens-mageck-analysis](skills/bio-crispr-screens-mageck-analysis/) | MAGeCK MLE/RRA analysis for CRISPR pooled screens. |
| [bio-crispr-screens-screen-qc](skills/bio-crispr-screens-screen-qc/) | Quality control for CRISPR screens: Gini index, read distribution. |

</details>

</details>

## 🔬 Omics & Computational Biology

<details open>
<summary>Expand/Collapse this category</summary>

### Single-Cell & Spatial Omics

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [anndata](skills/anndata/) | Working with annotated data matrices in Python for single-cell genomics analysis, managing experimental measurements with metadata and large-scale omics data. |
| [scanpy](skills/scanpy/) | Single-cell RNA-seq analysis. Load .h5ad/10X data, QC, normalization, PCA/UMAP/t-SNE, Leiden clustering, marker genes, cell type annotation, trajectory. |
| [scvi-tools](skills/scvi-tools/) | Deep learning for single-cell analysis: data integration/batch correction (scVI/scANVI), ATAC-seq (PeakVI), CITE-seq (totalVI), multiome (MultiVI), spatial deconvolution (DestVI). |
| [single-cell-rna-qc](skills/single-cell-rna-qc/) | Quality control on single-cell RNA-seq data (.h5ad or .h5 files) using scverse best practices with MAD-based filtering and comprehensive visualizations. |
| [cellxgene-census](skills/cellxgene-census/) | Query CZ CELLxGENE Census (61M+ cells). Filter by cell type/tissue/disease, retrieve expression data, integrate with scanpy/PyTorch, for population-scale single-cell analysis. |
| [pydeseq2](skills/pydeseq2/) | Differential gene expression analysis (Python DESeq2). Identify DE genes from bulk RNA-seq counts, Wald tests, FDR correction, volcano/MA plots. |
| [bulk-combat-correction](skills/bulk-combat-correction/) | Remove batch effects from merged bulk RNA-seq or microarray cohorts using pyComBat, with corrected matrix export and pre/post correction visualizations. |
| [bulk-deg-analysis](skills/bulk-deg-analysis/) | Bulk RNA-seq DEG pipeline: gene ID mapping, DESeq2 normalization, statistical testing, visualization, and pathway enrichment via OmicVerse. |
| [bulk-deseq2-analysis](skills/bulk-deseq2-analysis/) | PyDESeq2-based differential expression analysis with ID mapping, DE testing, fold-change thresholding, and enrichment visualization. |
| [bulk-stringdb-ppi](skills/bulk-stringdb-ppi/) | Query STRING for protein interactions, build PPI graphs with pyPPI, and render network figures for bulk gene lists. |
| [bulk-to-single-deconvolution](skills/bulk-to-single-deconvolution/) | Convert bulk RNA-seq cohorts to synthetic single-cell datasets using Bulk2Single workflow for cell fraction estimation and beta-VAE generation. |
| [bulk-trajblend-interpolation](skills/bulk-trajblend-interpolation/) | Extend scRNA-seq developmental trajectories with BulkTrajBlend by generating intermediate cells from bulk RNA-seq using beta-VAE and GNN models. |
| [bulk-wgcna-analysis](skills/bulk-wgcna-analysis/) | Run PyWGCNA through OmicVerse — co-expression module construction, eigengene visualization, and hub gene extraction. |
| [single-annotation](skills/single-annotation/) | Single-cell annotation workflows: SCSA, MetaTiME, CellVote, CellMatch, GPTAnno, and weighted KNN transfer for annotating cell types across modalities. |
| [single-cellphone-db](skills/single-cellphone-db/) | Run CellPhoneDB v5 on annotated single-cell data to infer ligand-receptor networks and produce CellChat-style visualizations. |
| [single-clustering](skills/single-clustering/) | Single-cell clustering workflow: QC, multimethod clustering, topic modeling, cNMF, and cross-batch integration in OmicVerse. |
| [single-downstream-analysis](skills/single-downstream-analysis/) | OmicVerse downstream tutorials covering AUCell scoring, metacell DEG, and related exports for single-cell data. |
| [single-multiomics](skills/single-multiomics/) | OmicVerse multi-omics tutorials: MOFA, GLUE pairing, SIMBA integration, TOSICA transfer, and StaVIA cartography. |
| [single-preprocessing](skills/single-preprocessing/) | Single-cell preprocessing in OmicVerse: QC, normalization, HVG detection, PCA/embedding pipelines (CPU/GPU). |
| [single-to-spatial-mapping](skills/single-to-spatial-mapping/) | Map scRNA-seq atlases onto spatial transcriptomics slides using Single2Spatial workflow for deep-forest training and marker visualization. |
| [single-trajectory](skills/single-trajectory/) | OmicVerse trajectory workflows: PAGA, Palantir, VIA, velocity coupling, and fate scoring. |
| [spatial-tutorials](skills/spatial-tutorials/) | Spatial transcriptomics tutorials: preprocessing, deconvolution, and downstream modeling across Visium, Visium HD, Stereo-seq, and Slide-seq. |
| [tcga-preprocessing](skills/tcga-preprocessing/) | Ingest TCGA sample sheets, expression archives, and clinical carts into OmicVerse, with survival metadata initialization and AnnData export. |
| [gsea-enrichment](skills/gsea-enrichment/) | Gene set enrichment analysis in OmicVerse with correct geneset format handling for loading pathway databases and running GSEA. |

</details>

### Cheminformatics & Drug Discovery

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [rdkit](skills/rdkit/) | Cheminformatics toolkit for fine-grained molecular control. SMILES/SDF parsing, descriptors (MW, LogP, TPSA), fingerprints, substructure search, 2D/3D generation, similarity. |
| [datamol](skills/datamol/) | Pythonic RDKit wrapper with simplified interface for standard drug discovery: SMILES parsing, standardization, descriptors, fingerprints, clustering, 3D conformer generation. |
| [medchem](skills/medchem/) | Medicinal chemistry filters. Apply drug-likeness rules (Lipinski, Veber), PAINS filters, structural alerts, complexity metrics, for compound prioritization and library filtering. |
| [diffdock](skills/diffdock/) | Diffusion-based molecular docking. Predict protein-ligand binding poses from PDB/SMILES, confidence scores, virtual screening, for structure-based drug design. |
| [molfeat](skills/molfeat/) | Molecular featurization for ML (100+ featurizers). ECFP, MACCS, descriptors, pretrained models (ChemBERTa), convert SMILES to features, for QSAR and molecular ML. |
| [deepchem](skills/deepchem/) | Molecular machine learning toolkit. Property prediction (ADMET, toxicity), GNNs (GCN, MPNN), MoleculeNet benchmarks, pretrained models, for drug discovery ML. |
| [torchdrug](skills/torchdrug/) | Graph-based drug discovery toolkit. Molecular property prediction (ADMET), protein modeling, knowledge graph reasoning, molecular generation, retrosynthesis, GNNs. |
| [torch_geometric](skills/torch_geometric/) | Graph Neural Networks (PyG). Node/graph classification, link prediction, GCN, GAT, GraphSAGE, molecular property prediction, for geometric deep learning in drug discovery. |
| [pytdc](skills/pytdc/) | Therapeutics Data Commons. AI-ready drug discovery datasets (ADME, toxicity, DTI), benchmarks, scaffold splits, molecular oracles, for therapeutic ML. |
| [cobrapy](skills/cobrapy/) | Constraint-based metabolic modeling (COBRA). FBA, FVA, gene knockouts, flux sampling, SBML models, for systems biology and metabolic engineering. |

</details>

### Proteomics & Mass Spectrometry

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [matchms](skills/matchms/) | Mass spectrometry spectral analysis. Process mzML/MGF/MSP files, spectral similarity (cosine, modified cosine), metadata harmonization, compound identification. |
| [pyopenms](skills/pyopenms/) | Python interface to OpenMS for LC-MS/MS proteomics and metabolomics workflows. File handling (mzML, mzXML, mzTab, pepXML, mzIdentML) and quantification. |
| [flowio](skills/flowio/) | Parse FCS (Flow Cytometry Standard) files v2.0-3.1. Extract events as NumPy arrays, read metadata/channels, convert to CSV/DataFrame, for flow cytometry data preprocessing. |

</details>

### Protein Structure & Design

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [esm](skills/esm/) | ESM3 generative multimodal protein design (sequence, structure, function) and ESM C efficient protein embeddings. Protein language models for sequence scoring and embedding. |
| [alphafold](skills/alphafold/) | Validate protein designs using AlphaFold2 structure prediction. Validates designed sequences, predicts binder-target complex structures, calculates pLDDT/PAE metrics. |
| [boltz](skills/boltz/) | Structure prediction using Boltz-1/Boltz-2, an open biomolecular structure predictor for protein complexes, binder validation, and open-source AlphaFold alternative. |
| [boltzgen](skills/boltzgen/) | All-atom protein design using BoltzGen diffusion model. Side-chain aware design from the start, designing around small molecules or ligands. |
| [chai](skills/chai/) | Structure prediction using Chai-1 foundation model for protein-protein complexes, binder validation, and protein-small molecule interaction prediction. |
| [rfdiffusion](skills/rfdiffusion/) | Generate protein backbones using RFdiffusion diffusion model for de novo protein structure generation and binder scaffold design. |
| [bindcraft](skills/bindcraft/) | End-to-end binder design using BindCraft hallucination with built-in AF2 validation for production-quality binder campaigns. |
| [binder-design](skills/binder-design/) | Guidance for choosing the right protein binder design tool (BoltzGen, BindCraft, or RFdiffusion) and planning binder design campaigns. |
| [proteinmpnn](skills/proteinmpnn/) | Design protein sequences using ProteinMPNN inverse folding for RFdiffusion backbones, sequence redesign, and partial fixed-position design. |
| [ligandmpnn](skills/ligandmpnn/) | Ligand-aware protein sequence design using LigandMPNN for sequences around small molecules, enzyme active site design, and binding pocket optimization. |
| [solublempnn](skills/solublempnn/) | Solubility-optimized protein sequence design using SolubleMPNN for E. coli expression, reducing aggregation, and solubility optimization. |
| [foldseek](skills/foldseek/) | Structure similarity search with Foldseek for finding similar structures in PDB/AFDB databases, structural homology search, and evolutionary relationship discovery. |
| [ipsae](skills/ipsae/) | Binder design ranking using ipSAE (interprotein Score from Aligned Errors) for ranking binder designs and filtering BindCraft or RFdiffusion outputs. |
| [pdb](skills/pdb/) | Fetch and analyze protein structures from RCSB PDB by PDB ID, search for similar structures, prepare targets for binder design. |
| [protein-design-workflow](skills/protein-design-workflow/) | End-to-end guidance for protein design pipelines from project initiation to experimental validation. |
| [protein-qc](skills/protein-qc/) | Quality control metrics and filtering thresholds for protein design: pLDDT, PAE, ipTM for binding, expression, and structure evaluation. |
| [cell-free-expression](skills/cell-free-expression/) | Guidance for cell-free protein synthesis (CFPS) optimization, troubleshooting low yield/aggregation, and optimizing DNA template design. |
| [binding-characterization](skills/binding-characterization/) | Guidance for SPR and BLI binding characterization experiments, kinetics interpretation, and troubleshooting poor binding signal. |

</details>

### Single-Cell & Trajectory Analysis

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [scvelo](skills/scvelo/) | RNA velocity analysis. Estimate cell state transitions from unspliced/spliced mRNA dynamics, infer trajectory directions, compute latent time, and identify driver genes in scRNA-seq data. |

</details>

### Phylogenetics & Network Analysis

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [phylogenetics](skills/phylogenetics/) | Build and analyze phylogenetic trees using MAFFT, IQ-TREE 2, and FastTree. Evolutionary analysis, microbial genomics, viral phylodynamics, and molecular clock studies. |
| [networkx](skills/networkx/) | Network and graph analysis in Python. Biological network analysis, protein interaction networks, pathway graphs, community detection, and centrality measures. |
| [torch-geometric](skills/torch-geometric/) | Graph Neural Networks (PyG) for molecular property prediction, drug-target interaction modeling, and geometric deep learning on biological graphs. |

</details>

</details>

## ⚙️ ClawBio Pipelines

<details open>
<summary>Expand/Collapse this category</summary>

### Bioinformatics Orchestration & Pipelines (ClawBio)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-orchestrator](skills/bio-orchestrator/) | Meta-agent routing bioinformatics requests to specialized sub-skills. Handles file type detection (VCF, FASTQ, BAM, PDB, h5ad), analysis planning, report generation, and reproducibility export. |
| [scrna-orchestrator](skills/scrna-orchestrator/) | Local Scanpy pipeline for single-cell RNA-seq QC, clustering, marker discovery, and two-group differential expression from raw-count .h5ad files. |
| [seq-wrangler](skills/seq-wrangler/) | Sequence QC, alignment, and BAM processing. Wraps FastQC, BWA/Bowtie2, SAMtools for automated read-to-BAM pipelines. |
| [vcf-annotator](skills/vcf-annotator/) | Annotate VCF variants with VEP, ClinVar, gnomAD frequencies, and ancestry-aware context. Generates prioritized variant reports. |
| [repro-enforcer](skills/repro-enforcer/) | Export bioinformatics analyses as reproducible bundles with Conda environment, Singularity container definition, and Nextflow pipeline. |
| [galaxy-bridge](skills/galaxy-bridge/) | Galaxy tool discovery, recommendation, and execution — 8,000+ bioinformatics tools from usegalaxy.org with multi-signal scoring and workflow suggestions. |

</details>

### Genomics, Ancestry & Pharmacogenomics (ClawBio)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [gwas-lookup](skills/gwas-lookup/) | Federated variant lookup across 9 genomic databases: GWAS Catalog, Open Targets, PheWeb (UKB, FinnGen, BBJ), GTEx, eQTL Catalogue, and more. |
| [gwas-prs](skills/gwas-prs/) | Calculate polygenic risk scores from DTC genetic data (23andMe/AncestryDNA) using the PGS Catalog. |
| [pharmgx-reporter](skills/pharmgx-reporter/) | Pharmacogenomic report from DTC genetic data — 12 genes, 31 SNPs, 51 drugs with CPIC guidelines and personalized dosage cards. |
| [clinpgx](skills/clinpgx/) | Query the ClinPGx API for pharmacogenomic gene-drug data, clinical annotations, CPIC guidelines, and FDA drug labels. |
| [drug-photo](skills/drug-photo/) | Identify a medication from a packaging photo via Claude vision, then retrieve genotype-informed dosage guidance. |
| [claw-ancestry-pca](skills/claw-ancestry-pca/) | Ancestry decomposition PCA against the Simons Genome Diversity Project (345 samples, 164 global populations). |
| [genome-compare](skills/genome-compare/) | Compare genome to reference individuals and estimate ancestry composition via IBS and EM admixture. |
| [equity-scorer](skills/equity-scorer/) | Compute HEIM diversity and equity metrics from VCF or ancestry data. Generates heterozygosity, FST, PCA plots, and HEIM Equity Score with markdown reports. |
| [claw-metagenomics](skills/claw-metagenomics/) | Shotgun metagenomics profiling: taxonomy (Kraken2/Bracken), resistome (CARD/RGI), and functional pathways (HUMAnN3) from paired-end FASTQ. |
| [ukb-navigator](skills/ukb-navigator/) | Semantic search across UK Biobank's 12,000+ data fields and publications — find the right variables for your research question. |

</details>

### Structural Biology & Literature (ClawBio)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [struct-predictor](skills/struct-predictor/) | Local protein structure prediction with AlphaFold, Boltz, or Chai. Compare structures, compute RMSD, visualize 3D models. |
| [lit-synthesizer](skills/lit-synthesizer/) | Search PubMed and bioRxiv, summarize papers with LLM, build citation graphs, and generate literature review sections. |
| [claw-semantic-sim](skills/claw-semantic-sim/) | Semantic Similarity Index for disease research literature using PubMedBERT embeddings. Compute research equity metrics (HEIM). |
| [labstep](skills/labstep/) | Interact with the Labstep electronic lab notebook API. Query experiments, protocols, resources, and inventory. |
| [profile-report](skills/profile-report/) | Generate structured bioinformatics analysis profile reports. |

</details>

</details>

## 🧠 BioOS Extended Suite

<details open>
<summary>Expand/Collapse this category</summary>

### BioOS Extended Bioinformatics Suite (mdbabumiamssm/LLMs-Universal-Life-Science-and-Clinical-Skills-)

#### Sequence & Alignment Tools

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-alignment-sorting](skills/bio-alignment-sorting/) | Sort SAM/BAM files by coordinate or name with samtools sort. |
| [bio-alignment-filtering](skills/bio-alignment-filtering/) | Filter alignments by flag, quality, region, or paired status. |
| [bio-alignment-indexing](skills/bio-alignment-indexing/) | Index BAM/CRAM files with samtools index for random access. |
| [bio-alignment-validation](skills/bio-alignment-validation/) | Validate alignment file integrity and detect truncated/corrupt files. |
| [bio-alignment-files-bam-statistics](skills/bio-alignment-files-bam-statistics/) | Compute alignment statistics: flagstat, idxstats, coverage depth. |
| [bio-sam-bam-basics](skills/bio-sam-bam-basics/) | Read, inspect, and manipulate SAM/BAM files with samtools/pysam. |
| [bio-duplicate-handling](skills/bio-duplicate-handling/) | Mark and remove PCR duplicates with Picard or samtools markdup. |
| [bio-pileup-generation](skills/bio-pileup-generation/) | Generate base-level pileup from BAM for variant calling and coverage. |
| [bio-reference-operations](skills/bio-reference-operations/) | Download, index, and manage reference genome FASTA files. |
| [bio-blast-searches](skills/bio-blast-searches/) | Run BLAST searches against local or remote databases for sequence homology. |
| [bio-local-blast](skills/bio-local-blast/) | Set up and run BLAST+ locally with custom databases. |
| [bio-entrez-search](skills/bio-entrez-search/) | Search NCBI Entrez databases (PubMed, gene, nucleotide, protein, SRA). |
| [bio-entrez-fetch](skills/bio-entrez-fetch/) | Fetch records from NCBI Entrez by accession or UID. |
| [bio-entrez-link](skills/bio-entrez-link/) | Retrieve linked records across NCBI Entrez databases. |
| [bio-uniprot-access](skills/bio-uniprot-access/) | Query UniProt for protein sequences, annotations, and cross-references. |
| [bio-geo-data](skills/bio-geo-data/) | Download and parse GEO datasets and series matrices. |
| [bio-sra-data](skills/bio-sra-data/) | Download raw sequencing data from NCBI SRA with fasterq-dump. |
| [bio-batch-downloads](skills/bio-batch-downloads/) | Batch download bioinformatics data from NCBI, EBI, Ensembl. |

</details>

#### Sequence Analysis

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-seq-objects](skills/bio-seq-objects/) | Work with BioPython sequence objects: SeqRecord, features, annotations. |
| [bio-sequence-properties](skills/bio-sequence-properties/) | Compute sequence properties: MW, pI, hydrophobicity, extinction coefficient. |
| [bio-sequence-similarity](skills/bio-sequence-similarity/) | Compute sequence similarity with pairwise alignment and percent identity. |
| [bio-sequence-slicing](skills/bio-sequence-slicing/) | Slice, extract, and manipulate subsequences from FASTA/FASTQ. |
| [bio-motif-search](skills/bio-motif-search/) | Search sequences for regulatory motifs using FIMO, MAST, or regex. |
| [bio-codon-usage](skills/bio-codon-usage/) | Analyze codon usage bias and optimize sequences for expression. |
| [bio-transcription-translation](skills/bio-transcription-translation/) | Transcribe and translate DNA sequences; handle genetic code variations. |
| [bio-reverse-complement](skills/bio-reverse-complement/) | Compute reverse complement and strand-aware sequence operations. |
| [bio-primer-design-primer-basics](skills/bio-primer-design-primer-basics/) | Design PCR primers with Primer3 for standard amplification. |
| [bio-primer-design-primer-validation](skills/bio-primer-design-primer-validation/) | Validate primer specificity by BLAST and thermodynamic analysis. |
| [bio-primer-design-qpcr-primers](skills/bio-primer-design-qpcr-primers/) | Design qPCR/RT-PCR primers with efficiency and specificity optimization. |
| [bio-restriction-sites](skills/bio-restriction-sites/) | Find restriction enzyme recognition sites in DNA sequences. |
| [bio-restriction-mapping](skills/bio-restriction-mapping/) | Create restriction maps and in silico digestion patterns. |
| [bio-restriction-fragment-analysis](skills/bio-restriction-fragment-analysis/) | Analyze restriction fragment patterns for cloning and gel prediction. |
| [bio-restriction-enzyme-selection](skills/bio-restriction-enzyme-selection/) | Select restriction enzymes for cloning based on cut sites and compatibility. |

</details>

#### Read Alignment

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-read-alignment-bwa-alignment](skills/bio-read-alignment-bwa-alignment/) | Align short reads to reference genome with BWA-MEM. |
| [bio-read-alignment-bowtie2-alignment](skills/bio-read-alignment-bowtie2-alignment/) | Align short reads with Bowtie2; local and end-to-end modes. |
| [bio-read-alignment-hisat2-alignment](skills/bio-read-alignment-hisat2-alignment/) | Splice-aware RNA-seq alignment with HISAT2. |
| [bio-read-alignment-star-alignment](skills/bio-read-alignment-star-alignment/) | High-speed STAR aligner for RNA-seq with junction detection. |

</details>

#### Genome Assembly

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-genome-assembly-long-read-assembly](skills/bio-genome-assembly-long-read-assembly/) | De novo assembly from ONT/PacBio long reads with Flye or Canu. |
| [bio-genome-assembly-hifi-assembly](skills/bio-genome-assembly-hifi-assembly/) | HiFi (CCS) read assembly with Hifiasm for high-accuracy genomes. |
| [bio-genome-assembly-short-read-assembly](skills/bio-genome-assembly-short-read-assembly/) | Illumina de novo assembly with SPAdes for metagenomes/bacteria/transcriptomes. |
| [bio-genome-assembly-metagenome-assembly](skills/bio-genome-assembly-metagenome-assembly/) | Metagenomic assembly: co-assembly, binning, MAG recovery. |
| [bio-genome-assembly-assembly-qc](skills/bio-genome-assembly-assembly-qc/) | Assess assembly quality with QUAST, BUSCO, and NGA50 metrics. |
| [bio-genome-assembly-assembly-polishing](skills/bio-genome-assembly-assembly-polishing/) | Polish assemblies with Medaka (ONT) or NextPolish (Illumina). |
| [bio-genome-assembly-scaffolding](skills/bio-genome-assembly-scaffolding/) | Scaffold contigs with Hi-C, optical mapping, or long reads. |
| [bio-genome-assembly-contamination-detection](skills/bio-genome-assembly-contamination-detection/) | Detect and remove contamination in assembled genomes. |

</details>

#### Genome Intervals & Annotation

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-genome-intervals-bed-file-basics](skills/bio-genome-intervals-bed-file-basics/) | Read, write, and filter BED files with pybedtools/bedtools. |
| [bio-genome-intervals-interval-arithmetic](skills/bio-genome-intervals-interval-arithmetic/) | Intersect, subtract, merge, and complement genomic intervals. |
| [bio-genome-intervals-proximity-operations](skills/bio-genome-intervals-proximity-operations/) | Find nearest features and compute distances between intervals. |
| [bio-genome-intervals-coverage-analysis](skills/bio-genome-intervals-coverage-analysis/) | Compute read depth coverage across genomic regions. |
| [bio-genome-intervals-bigwig-tracks](skills/bio-genome-intervals-bigwig-tracks/) | Create and query BigWig signal tracks from BAM/bedGraph. |
| [bio-genome-intervals-gtf-gff-handling](skills/bio-genome-intervals-gtf-gff-handling/) | Parse and manipulate GTF/GFF annotation files. |
| [bio-bedgraph-handling](skills/bio-bedgraph-handling/) | Process bedGraph coverage files: arithmetic, normalization, conversion. |

</details>

#### RNA Quantification

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-rna-quantification-featurecounts-counting](skills/bio-rna-quantification-featurecounts-counting/) | Count reads per gene with featureCounts from subread package. |
| [bio-rna-quantification-alignment-free-quant](skills/bio-rna-quantification-alignment-free-quant/) | Pseudo-alignment quantification with Salmon or Kallisto. |
| [bio-rna-quantification-tximport-workflow](skills/bio-rna-quantification-tximport-workflow/) | Import Salmon/Kallisto quantification into R/DESeq2 with tximport. |
| [bio-rna-quantification-count-matrix-qc](skills/bio-rna-quantification-count-matrix-qc/) | QC count matrices: library size, zero inflation, gene detection rates. |
| [bio-expression-matrix-counts-ingest](skills/bio-expression-matrix-counts-ingest/) | Load and validate count matrices from multiple quantification tools. |
| [bio-expression-matrix-gene-id-mapping](skills/bio-expression-matrix-gene-id-mapping/) | Map between Ensembl, Entrez, HGNC, and gene symbol identifiers. |
| [bio-expression-matrix-metadata-joins](skills/bio-expression-matrix-metadata-joins/) | Join sample metadata to expression matrices for downstream analysis. |
| [bio-expression-matrix-sparse-handling](skills/bio-expression-matrix-sparse-handling/) | Handle sparse count matrices efficiently with scipy sparse formats. |

</details>

#### Epitranscriptomics & CLIP-seq

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-epitranscriptomics-merip-preprocessing](skills/bio-epitranscriptomics-merip-preprocessing/) | Preprocess MeRIP-seq data for m6A methylation analysis. |
| [bio-epitranscriptomics-m6a-peak-calling](skills/bio-epitranscriptomics-m6a-peak-calling/) | Call m6A peaks from MeRIP-seq with exomePeak2 or MACS2. |
| [bio-epitranscriptomics-m6anet-analysis](skills/bio-epitranscriptomics-m6anet-analysis/) | Nanopore direct RNA m6A detection with m6Anet deep learning. |
| [bio-epitranscriptomics-m6a-differential](skills/bio-epitranscriptomics-m6a-differential/) | Differential m6A methylation analysis between conditions. |
| [bio-epitranscriptomics-modification-visualization](skills/bio-epitranscriptomics-modification-visualization/) | Visualize RNA modification profiles and metagene plots. |
| [bio-clip-seq-clip-preprocessing](skills/bio-clip-seq-clip-preprocessing/) | Preprocess CLIP-seq/eCLIP data: adapter trimming, demultiplexing. |
| [bio-clip-seq-clip-alignment](skills/bio-clip-seq-clip-alignment/) | Align CLIP-seq reads with STAR; handle unique mappers. |
| [bio-clip-seq-clip-peak-calling](skills/bio-clip-seq-clip-peak-calling/) | Call RBP binding peaks from CLIP-seq with PureCLIP or MACS2. |
| [bio-clip-seq-binding-site-annotation](skills/bio-clip-seq-binding-site-annotation/) | Annotate CLIP-seq peaks with genomic features and RNA regions. |
| [bio-clip-seq-clip-motif-analysis](skills/bio-clip-seq-clip-motif-analysis/) | Discover RBP binding motifs from CLIP-seq peak sequences. |

</details>

#### Small RNA-seq

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-small-rna-seq-smrna-preprocessing](skills/bio-small-rna-seq-smrna-preprocessing/) | Preprocess small RNA-seq: adapter trimming, size selection. |
| [bio-small-rna-seq-mirdeep2-analysis](skills/bio-small-rna-seq-mirdeep2-analysis/) | Identify and quantify known/novel miRNAs with miRDeep2. |
| [bio-small-rna-seq-mirge3-analysis](skills/bio-small-rna-seq-mirge3-analysis/) | miRNA annotation and quantification with miRge3.0. |
| [bio-small-rna-seq-target-prediction](skills/bio-small-rna-seq-target-prediction/) | Predict miRNA target genes with TargetScan or miRDB. |
| [bio-small-rna-seq-differential-mirna](skills/bio-small-rna-seq-differential-mirna/) | Differential miRNA expression analysis with DESeq2/edgeR. |

</details>

#### Population Genetics & Phasing

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-population-genetics-plink-basics](skills/bio-population-genetics-plink-basics/) | PLINK2 for GWAS QC, LD pruning, and basic population genetics. |
| [bio-population-genetics-population-structure](skills/bio-population-genetics-population-structure/) | Population stratification with PCA, ADMIXTURE, and STRUCTURE. |
| [bio-population-genetics-linkage-disequilibrium](skills/bio-population-genetics-linkage-disequilibrium/) | Compute LD metrics (r², D') and LD decay analysis. |
| [bio-population-genetics-association-testing](skills/bio-population-genetics-association-testing/) | GWAS association testing with PLINK, BOLT-LMM, or SAIGE. |
| [bio-population-genetics-scikit-allel-analysis](skills/bio-population-genetics-scikit-allel-analysis/) | Population genetics analysis with scikit-allel: diversity, Fst, haplotypes. |
| [bio-population-genetics-selection-statistics](skills/bio-population-genetics-selection-statistics/) | Detect natural selection signatures: iHS, XP-EHH, Tajima's D. |
| [bio-phasing-imputation-haplotype-phasing](skills/bio-phasing-imputation-haplotype-phasing/) | Phase variants with SHAPEIT4 or BEAGLE. |
| [bio-phasing-imputation-genotype-imputation](skills/bio-phasing-imputation-genotype-imputation/) | Impute missing genotypes using Michigan/TOPMed imputation servers. |
| [bio-phasing-imputation-reference-panels](skills/bio-phasing-imputation-reference-panels/) | Select and prepare reference panels (1KGP, HRC, TOPMed) for imputation. |
| [bio-phasing-imputation-imputation-qc](skills/bio-phasing-imputation-imputation-qc/) | QC imputed data: R² filter, INFO score, allele concordance. |

</details>

#### Comparative Genomics & Phylogenetics

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-comparative-genomics-ortholog-inference](skills/bio-comparative-genomics-ortholog-inference/) | Infer orthologs and paralogs with OrthoFinder or OMA. |
| [bio-comparative-genomics-synteny-analysis](skills/bio-comparative-genomics-synteny-analysis/) | Detect syntenic blocks between genomes with MCScan or SyRI. |
| [bio-comparative-genomics-positive-selection](skills/bio-comparative-genomics-positive-selection/) | Test for positive selection with PAML, HyPhy, or dN/dS ratios. |
| [bio-comparative-genomics-hgt-detection](skills/bio-comparative-genomics-hgt-detection/) | Detect horizontal gene transfer events in microbial genomes. |
| [bio-comparative-genomics-ancestral-reconstruction](skills/bio-comparative-genomics-ancestral-reconstruction/) | Reconstruct ancestral sequences and traits with ASR methods. |
| [bio-phylo-tree-io](skills/bio-phylo-tree-io/) | Read/write phylogenetic trees in Newick, Nexus, PhyloXML formats. |
| [bio-phylo-modern-tree-inference](skills/bio-phylo-modern-tree-inference/) | Maximum likelihood tree inference with IQ-TREE 2 or FastTree. |
| [bio-phylo-tree-manipulation](skills/bio-phylo-tree-manipulation/) | Root, prune, reorder, and annotate phylogenetic trees. |
| [bio-phylo-tree-visualization](skills/bio-phylo-tree-visualization/) | Visualize trees with iTOL, ETE3, or ggtree. |
| [bio-phylo-distance-calculations](skills/bio-phylo-distance-calculations/) | Compute pairwise phylogenetic distances and diversity metrics. |

</details>

#### Systems Biology & Metabolic Modeling

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-systems-biology-flux-balance-analysis](skills/bio-systems-biology-flux-balance-analysis/) | Flux balance analysis (FBA) with COBRApy for metabolic network modeling. |
| [bio-systems-biology-metabolic-reconstruction](skills/bio-systems-biology-metabolic-reconstruction/) | Reconstruct genome-scale metabolic models from genome annotations. |
| [bio-systems-biology-gene-essentiality](skills/bio-systems-biology-gene-essentiality/) | Predict essential genes by single gene knockouts in metabolic models. |
| [bio-systems-biology-context-specific-models](skills/bio-systems-biology-context-specific-models/) | Build context-specific metabolic models from expression data (GIMME, iMAT). |
| [bio-systems-biology-model-curation](skills/bio-systems-biology-model-curation/) | Curate SBML metabolic models: mass/charge balance, gap filling. |

</details>

#### Experimental Design & Reporting

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-experimental-design-sample-size](skills/bio-experimental-design-sample-size/) | Power analysis and sample size calculation for omics experiments. |
| [bio-experimental-design-power-analysis](skills/bio-experimental-design-power-analysis/) | Statistical power analysis for detecting differential signals. |
| [bio-experimental-design-batch-design](skills/bio-experimental-design-batch-design/) | Optimize sample batching to minimize confounding with ComBat design. |
| [bio-experimental-design-multiple-testing](skills/bio-experimental-design-multiple-testing/) | Multiple testing correction: Bonferroni, BH/FDR, q-values. |
| [bio-machine-learning-omics-classifiers](skills/bio-machine-learning-omics-classifiers/) | Train classifiers on omics data: random forest, SVM, XGBoost. |
| [bio-machine-learning-biomarker-discovery](skills/bio-machine-learning-biomarker-discovery/) | Identify biomarkers from omics data with LASSO, elastic net, SHAP. |
| [bio-machine-learning-model-validation](skills/bio-machine-learning-model-validation/) | Cross-validation, AUC-ROC, calibration, and permutation testing. |
| [bio-machine-learning-survival-analysis](skills/bio-machine-learning-survival-analysis/) | Survival ML: RSF, DeepSurv, CoxBoost from omics features. |
| [bio-machine-learning-atlas-mapping](skills/bio-machine-learning-atlas-mapping/) | Map query cells to reference atlases with scANVI or Symphony. |
| [bio-machine-learning-prediction-explanation](skills/bio-machine-learning-prediction-explanation/) | Explain omics ML predictions with SHAP and feature importance. |
| [bio-reporting-automated-qc-reports](skills/bio-reporting-automated-qc-reports/) | Generate automated MultiQC-style reports for omics pipelines. |
| [bio-reporting-jupyter-reports](skills/bio-reporting-jupyter-reports/) | Create Jupyter notebook reports with reproducible analysis code. |
| [bio-reporting-rmarkdown-reports](skills/bio-reporting-rmarkdown-reports/) | Render Rmarkdown reports with integrated plots and statistics. |
| [bio-reporting-quarto-reports](skills/bio-reporting-quarto-reports/) | Build Quarto multi-format reports (HTML/PDF) from analysis code. |
| [bio-reporting-figure-export](skills/bio-reporting-figure-export/) | Export publication-quality figures in PDF/SVG/TIFF at specified DPI. |
| [bio-research-tools-biomarker-signature-studio](skills/bio-research-tools-biomarker-signature-studio/) | Build, validate, and visualize multi-omic biomarker signatures. |

</details>

#### End-to-End Workflow Pipelines

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-workflows-fastq-to-variants](skills/bio-workflows-fastq-to-variants/) | Complete FASTQ → alignment → variant calling pipeline. |
| [bio-workflows-rnaseq-to-de](skills/bio-workflows-rnaseq-to-de/) | RNA-seq → alignment → counts → DESeq2 differential expression. |
| [bio-workflows-scrnaseq-pipeline](skills/bio-workflows-scrnaseq-pipeline/) | Single-cell RNA-seq end-to-end: Cell Ranger → Scanpy → clustering. |
| [bio-workflows-atacseq-pipeline](skills/bio-workflows-atacseq-pipeline/) | ATAC-seq: trimming → alignment → peak calling → differential. |
| [bio-workflows-chipseq-pipeline](skills/bio-workflows-chipseq-pipeline/) | ChIP-seq: alignment → peak calling → motif analysis → annotation. |
| [bio-workflows-methylation-pipeline](skills/bio-workflows-methylation-pipeline/) | WGBS/RRBS: bismark alignment → methylation calling → DMR detection. |
| [bio-workflows-metagenomics-pipeline](skills/bio-workflows-metagenomics-pipeline/) | Metagenomics: QC → classification → functional profiling → AMR. |
| [bio-workflows-metabolomics-pipeline](skills/bio-workflows-metabolomics-pipeline/) | LC-MS/GC-MS: preprocessing → annotation → statistical analysis. |
| [bio-workflows-proteomics-pipeline](skills/bio-workflows-proteomics-pipeline/) | DDA/DIA proteomics: search → quantification → differential abundance. |
| [bio-workflows-gwas-pipeline](skills/bio-workflows-gwas-pipeline/) | GWAS: QC → imputation → association → fine-mapping → annotation. |
| [bio-workflows-somatic-variant-pipeline](skills/bio-workflows-somatic-variant-pipeline/) | Tumor-normal somatic variant calling with GATK Mutect2/Strelka2. |
| [bio-workflows-cnv-pipeline](skills/bio-workflows-cnv-pipeline/) | Copy number variant detection: WGS/WES CNV calling and annotation. |
| [bio-workflows-spatial-pipeline](skills/bio-workflows-spatial-pipeline/) | Spatial transcriptomics: alignment → deconvolution → domain detection. |
| [bio-workflows-multi-omics-pipeline](skills/bio-workflows-multi-omics-pipeline/) | Multi-omics integration pipeline: MOFA, SNF, similarity network fusion. |
| [bio-workflows-multiome-pipeline](skills/bio-workflows-multiome-pipeline/) | 10x Multiome: joint scRNA-seq + scATAC-seq processing and integration. |
| [bio-workflows-hic-pipeline](skills/bio-workflows-hic-pipeline/) | Hi-C contact map generation, normalization, TAD/loop calling. |
| [bio-workflows-neoantigen-pipeline](skills/bio-workflows-neoantigen-pipeline/) | Neoantigen prediction: somatic variants → MHC binding → immunogenicity. |
| [bio-workflows-microbiome-pipeline](skills/bio-workflows-microbiome-pipeline/) | Microbiome: 16S/ITS amplicon or shotgun → diversity → differential. |
| [bio-workflows-crispr-screen-pipeline](skills/bio-workflows-crispr-screen-pipeline/) | CRISPR screen: guide counting → MAGeCK → hit calling → visualization. |
| [bio-workflows-crispr-editing-pipeline](skills/bio-workflows-crispr-editing-pipeline/) | CRISPR editing: amplicon sequencing → CRISPResso2 → outcome analysis. |
| [bio-workflows-tcr-pipeline](skills/bio-workflows-tcr-pipeline/) | TCR/BCR: V(D)J alignment → clonotype → repertoire analysis. |
| [bio-workflows-riboseq-pipeline](skills/bio-workflows-riboseq-pipeline/) | Ribo-seq: footprint alignment → periodicity → ORF detection. |
| [bio-workflows-smrna-pipeline](skills/bio-workflows-smrna-pipeline/) | Small RNA-seq: miRNA identification → quantification → DE analysis. |
| [bio-workflows-merip-pipeline](skills/bio-workflows-merip-pipeline/) | MeRIP-seq: m6A peak calling → differential → motif analysis. |
| [bio-workflows-clip-pipeline](skills/bio-workflows-clip-pipeline/) | CLIP-seq: peak calling → binding site annotation → motif discovery. |
| [bio-workflows-imc-pipeline](skills/bio-workflows-imc-pipeline/) | Imaging mass cytometry: segmentation → phenotyping → spatial analysis. |
| [bio-workflows-cytometry-pipeline](skills/bio-workflows-cytometry-pipeline/) | Flow/mass cytometry: QC → gating → clustering → differential. |
| [bio-workflows-longread-sv-pipeline](skills/bio-workflows-longread-sv-pipeline/) | Long-read structural variant calling and annotation pipeline. |
| [bio-workflows-genome-assembly-pipeline](skills/bio-workflows-genome-assembly-pipeline/) | De novo genome assembly: raw reads → assembly → QC → annotation. |
| [bio-workflows-outbreak-pipeline](skills/bio-workflows-outbreak-pipeline/) | Pathogen genomics: assembly → typing → phylodynamics → transmission. |
| [bio-workflows-biomarker-pipeline](skills/bio-workflows-biomarker-pipeline/) | Biomarker discovery: omics → feature selection → validation → report. |
| [bio-workflows-metabolic-modeling-pipeline](skills/bio-workflows-metabolic-modeling-pipeline/) | Metabolic model reconstruction → FBA → simulation → visualization. |
| [bio-splicing-pipeline](skills/bio-splicing-pipeline/) | Alternative splicing analysis: rMATS → PSI → differential → sashimi. |
| [bio-liquid-biopsy-pipeline](skills/bio-liquid-biopsy-pipeline/) | Liquid biopsy: cfDNA/ctDNA QC → mutation detection → TMB → MRD. |
| [bio-workflow-management-snakemake-workflows](skills/bio-workflow-management-snakemake-workflows/) | Create and manage Snakemake reproducible bioinformatics workflows. |
| [bio-workflow-management-nextflow-pipelines](skills/bio-workflow-management-nextflow-pipelines/) | Build and run Nextflow (DSL2) bioinformatics pipelines. |
| [bio-workflow-management-cwl-workflows](skills/bio-workflow-management-cwl-workflows/) | Write Common Workflow Language (CWL) portable workflow definitions. |
| [bio-workflow-management-wdl-workflows](skills/bio-workflow-management-wdl-workflows/) | Create WDL workflows for Terra/Cromwell bioinformatics execution. |
| [bio-workflows-expression-to-pathways](skills/bio-workflows-expression-to-pathways/) | End-to-end workflow from differential expression to GO/KEGG/Reactome enrichment and pathway visualization. |

</details>

#### Data Visualization (Bioinformatics)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bio-data-visualization-heatmaps-clustering](skills/bio-data-visualization-heatmaps-clustering/) | Hierarchical clustering heatmaps with ComplexHeatmap or seaborn. |
| [bio-data-visualization-volcano-customization](skills/bio-data-visualization-volcano-customization/) | Customized volcano plots with ggplot2 or matplotlib for DE results. |
| [bio-data-visualization-circos-plots](skills/bio-data-visualization-circos-plots/) | Circular genome visualization with Circos or pycirclize. |
| [bio-data-visualization-genome-browser-tracks](skills/bio-data-visualization-genome-browser-tracks/) | Generate genome browser tracks and IGV sessions from BAM/BigWig. |
| [bio-data-visualization-genome-tracks](skills/bio-data-visualization-genome-tracks/) | Multi-panel genome track plots with pyGenomeTracks. |
| [bio-data-visualization-ggplot2-fundamentals](skills/bio-data-visualization-ggplot2-fundamentals/) | R ggplot2 for publication-quality genomics and omics figures. |
| [bio-data-visualization-interactive-visualization](skills/bio-data-visualization-interactive-visualization/) | Interactive omics visualizations with Plotly, Bokeh, or shiny. |
| [bio-data-visualization-upset-plots](skills/bio-data-visualization-upset-plots/) | UpSet plots for multi-set intersection visualization. |
| [bio-data-visualization-multipanel-figures](skills/bio-data-visualization-multipanel-figures/) | Compose multipanel publication figures with cowplot or patchwork. |
| [bio-data-visualization-color-palettes](skills/bio-data-visualization-color-palettes/) | Scientific color palettes: colorblind-safe, perceptually uniform, diverging. |
| [bio-data-visualization-specialized-omics-plots](skills/bio-data-visualization-specialized-omics-plots/) | Specialized plots: lollipop (mutations), circomap, oncoprint. |

</details>

### Oncology & Precision Medicine Agents (BioOS)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [autonomous-oncology-agent](skills/autonomous-oncology-agent/) | Autonomous oncology research agent: literature mining, trial matching, biomarker analysis, and treatment hypothesis generation. |
| [precision-oncology-agent](skills/precision-oncology-agent/) | Precision oncology: tumor molecular profiling → actionable alterations → treatment recommendations. |
| [pan-cancer-multiomics-agent](skills/pan-cancer-multiomics-agent/) | Pan-cancer multi-omics integration for cross-cancer pattern discovery and driver identification. |
| [tumor-clonal-evolution-agent](skills/tumor-clonal-evolution-agent/) | Model tumor clonal evolution: phylogenetic trees, clonal dynamics, branching patterns from somatic variants. |
| [tumor-heterogeneity-agent](skills/tumor-heterogeneity-agent/) | Analyze intratumoral heterogeneity from bulk and single-cell sequencing data. |
| [tumor-mutational-burden-agent](skills/tumor-mutational-burden-agent/) | Compute TMB and assess its predictive value for immunotherapy response. |
| [chromosomal-instability-agent](skills/chromosomal-instability-agent/) | Quantify chromosomal instability (CIN) from copy number and SV data. |
| [cancer-metabolism-agent](skills/cancer-metabolism-agent/) | Analyze tumor metabolic reprogramming from transcriptomic and metabolomic data. |
| [liquid-biopsy-analytics-agent](skills/liquid-biopsy-analytics-agent/) | Comprehensive liquid biopsy analytics: ctDNA detection, MRD monitoring, treatment response. |
| [ctdna-dynamics-mrd-agent](skills/ctdna-dynamics-mrd-agent/) | Track ctDNA dynamics for minimal residual disease detection and treatment monitoring. |
| [mrd-edge-detection-agent](skills/mrd-edge-detection-agent/) | Ultra-sensitive MRD detection from deep sequencing with error suppression. |
| [hrd-analysis-agent](skills/hrd-analysis-agent/) | Homologous recombination deficiency (HRD) analysis for PARP inhibitor response prediction. |
| [computational-pathology-agent](skills/computational-pathology-agent/) | Computational pathology: WSI analysis, tissue segmentation, histological feature extraction. |
| [multimodal-radpath-fusion-agent](skills/multimodal-radpath-fusion-agent/) | Fuse radiology and pathology imaging for integrated cancer phenotyping. |
| [radiomics-pathomics-fusion-agent](skills/radiomics-pathomics-fusion-agent/) | Extract radiomic and pathomic features and integrate for predictive modeling. |
| [radgpt-radiology-reporter](skills/radgpt-radiology-reporter/) | AI-assisted radiology report generation from imaging findings. |
| [organoid-drug-response-agent](skills/organoid-drug-response-agent/) | Analyze drug response in patient-derived organoids for personalized therapy prediction. |
| [pdx-model-analysis-agent](skills/pdx-model-analysis-agent/) | Patient-derived xenograft model analysis for drug efficacy and biomarker discovery. |
| [deep-visual-proteomics-agent](skills/deep-visual-proteomics-agent/) | Deep visual proteomics: spatial proteomic analysis from laser-capture microdissection MS data. |
| [exosome-ev-analysis-agent](skills/exosome-ev-analysis-agent/) | Extracellular vesicle and exosome analysis: cargo profiling and biomarker discovery. |
| [microbiome-cancer-agent](skills/microbiome-cancer-agent/) | Tumor microbiome analysis and its role in cancer progression and immunotherapy response. |
| [bio-fragment-analysis](skills/bio-fragment-analysis/) | Analyze cfDNA fragment size distributions and fragmentomics features (FinaleToolkit/Griffin) for cancer detection and tissue-of-origin assessment. |

</details>

### Hematology & Blood Disorders (BioOS)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [myeloma-mrd-agent](skills/myeloma-mrd-agent/) | Multiple myeloma MRD assessment from flow cytometry and NGS data. |
| [mpn-progression-monitor-agent](skills/mpn-progression-monitor-agent/) | Myeloproliferative neoplasm progression monitoring from serial molecular data. |
| [mpn-research-assistant](skills/mpn-research-assistant/) | Research assistant for myeloproliferative neoplasms: literature, mutation analysis, treatment. |
| [bone-marrow-ai-agent](skills/bone-marrow-ai-agent/) | Bone marrow analysis: blast counting, immunophenotyping, disease classification. |
| [hemoglobinopathy-analysis-agent](skills/hemoglobinopathy-analysis-agent/) | Hemoglobin variant analysis, sickle cell, and thalassemia genotype-phenotype assessment. |
| [chip-clonal-hematopoiesis-agent](skills/chip-clonal-hematopoiesis-agent/) | Clonal hematopoiesis of indeterminate potential (CHIP) variant detection and risk assessment. |
| [coagulation-thrombosis-agent](skills/coagulation-thrombosis-agent/) | Coagulation pathway analysis, thrombophilia assessment, anticoagulation guidance. |

</details>

### Immunology & Cell Therapy (BioOS)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [cart-design-optimizer-agent](skills/cart-design-optimizer-agent/) | Optimize CAR-T cell construct design: scFv selection, linker, co-stimulatory domain. |
| [armored-cart-design-agent](skills/armored-cart-design-agent/) | Design armored CAR-T cells with cytokine payloads and resistance mechanisms. |
| [tcell-exhaustion-analysis-agent](skills/tcell-exhaustion-analysis-agent/) | Analyze T cell exhaustion from scRNA-seq and ATAC-seq data. |
| [nk-cell-therapy-agent](skills/nk-cell-therapy-agent/) | NK cell therapy design: receptor engineering, expansion protocols, persistence. |
| [tcr-pmhc-prediction-agent](skills/tcr-pmhc-prediction-agent/) | Predict TCR-pMHC binding affinity and selectivity for TCR therapy design. |
| [tcr-repertoire-analysis-agent](skills/tcr-repertoire-analysis-agent/) | TCR repertoire analysis: V(D)J usage, clonotype dynamics, antigen specificity. |
| [immune-checkpoint-combination-agent](skills/immune-checkpoint-combination-agent/) | Predict optimal immune checkpoint combination strategies from tumor immune microenvironment. |
| [tme-immune-profiling-agent](skills/tme-immune-profiling-agent/) | Tumor microenvironment immune profiling: cell type deconvolution and spatial mapping. |
| [cytokine-storm-analysis-agent](skills/cytokine-storm-analysis-agent/) | Cytokine storm detection, severity scoring, and intervention modeling. |

</details>

### Single-Cell & Spatial Agents (BioOS)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [cellagent-annotation](skills/cellagent-annotation/) | AI-driven single-cell cluster annotation using marker gene databases. |
| [universal-single-cell-annotator](skills/universal-single-cell-annotator/) | Universal scRNA-seq annotator using foundation models and multi-reference integration. |
| [scfoundation-model-agent](skills/scfoundation-model-agent/) | Single-cell foundation model inference (scFoundation/scGPT) for zero-shot annotation. |
| [rna-velocity-agent](skills/rna-velocity-agent/) | RNA velocity analysis with scVelo for trajectory and fate decision inference. |
| [spatial-transcriptomics-agent](skills/spatial-transcriptomics-agent/) | End-to-end spatial transcriptomics analysis: QC, deconvolution, domain detection. |
| [spatial-transcriptomics-analysis](skills/spatial-transcriptomics-analysis/) | Spatial transcriptomics analysis with Squidpy and SpatialDE. |
| [spatial-agent](skills/spatial-agent/) | Spatial omics agent: integrate spatial data with imaging, protein, and genomic layers. |
| [nicheformer-spatial-agent](skills/nicheformer-spatial-agent/) | Spatial niche analysis with Nicheformer foundation model for tissue microenvironment. |
| [spatial-epigenomics-agent](skills/spatial-epigenomics-agent/) | Spatial epigenomics analysis: spatially resolved chromatin accessibility and gene regulation. |
| [bioinformatics-singlecell](skills/bioinformatics-singlecell/) | General single-cell bioinformatics: clustering, trajectory, cell communication. |
| [scrna-qc](skills/scrna-qc/) | Single-cell RNA-seq quality control: doublet removal, ambient RNA, filtering thresholds. |
| [compbioagent-explorer](skills/compbioagent-explorer/) | Computational biology exploration agent for multi-omics dataset analysis. |
| [simo-multiomics-integration-agent](skills/simo-multiomics-integration-agent/) | Single-cell multi-omics integration with SIMO/MOFA+ for joint embedding. |
| [epigenomics-methylgpt-agent](skills/epigenomics-methylgpt-agent/) | Epigenomics and DNA methylation analysis with MethylGPT-inspired approaches. |
| [biomaster-workflows](skills/biomaster-workflows/) | BioMaster workflow orchestration for end-to-end bioinformatics analyses. |

</details>

### Drug Discovery & Design (BioOS)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [agentd-drug-discovery](skills/agentd-drug-discovery/) | AgentD autonomous drug discovery: target identification, hit finding, ADMET optimization. |
| [chematagent-drug-discovery](skills/chematagent-drug-discovery/) | CheMatAgent: chemistry-aware drug design with retrosynthesis and property optimization. |
| [chemcrow-drug-discovery](skills/chemcrow-drug-discovery/) | ChemCrow drug discovery toolkit: web search, Python, chemical tools integration. |
| [medea-therapeutic-discovery](skills/medea-therapeutic-discovery/) | MEDEA therapeutic discovery: multimodal evidence aggregation for target-disease validation. |
| [molecule-evolution-agent](skills/molecule-evolution-agent/) | Directed molecular evolution: generative models for compound optimization and library design. |
| [molecular-glue-discovery-agent](skills/molecular-glue-discovery-agent/) | Molecular glue discovery: induced proximity degraders and ternary complex stabilizers. |
| [protac-design-agent](skills/protac-design-agent/) | PROTAC design: E3 ligase ligand selection, linker optimization, ternary complex modeling. |
| [tpd-ternary-complex-agent](skills/tpd-ternary-complex-agent/) | Targeted protein degradation ternary complex modeling and cooperativity prediction. |
| [mage-antibody-generator](skills/mage-antibody-generator/) | MAGE antibody generator: sequence design, humanization, affinity maturation. |
| [antibody-design-agent](skills/antibody-design-agent/) | Antibody design: epitope mapping, CDR engineering, bispecific construction. |
| [aav-vector-design-agent](skills/aav-vector-design-agent/) | AAV vector design: capsid selection, promoter optimization, payload capacity. |
| [protein-structure-prediction](skills/protein-structure-prediction/) | Protein structure prediction with AlphaFold3, ESMFold, or Boltz with comparison. |
| [crispr-guide-design](skills/crispr-guide-design/) | CRISPR guide RNA design with on-target scoring and off-target minimization. |
| [crispr-offtarget-predictor](skills/crispr-offtarget-predictor/) | Predict CRISPR Cas9/Cas12 off-target sites genome-wide with CRISPOR/Cas-OFFinder. |
| [chemical-property-lookup](skills/chemical-property-lookup/) | Look up chemical properties from PubChem, ChEMBL, DrugBank by name/SMILES. |
| [chemistry-agent](skills/chemistry-agent/) | General chemistry agent for synthesis planning, reaction prediction, and property calculation. |
| [cryoem-ai-drug-design-agent](skills/cryoem-ai-drug-design-agent/) | AI-guided drug design from cryo-EM structures: binding site analysis and docking. |
| [time-resolved-cryoem-agent](skills/time-resolved-cryoem-agent/) | Time-resolved cryo-EM analysis for dynamic structural biology. |
| [cnv-caller-agent](skills/cnv-caller-agent/) | Specialized CNV detection agent integrating multiple callers with ensemble scoring. |
| [popeve-variant-predictor-agent](skills/popeve-variant-predictor-agent/) | Variant pathogenicity prediction using EVE population-based evolutionary models. |
| [varcadd-pathogenicity](skills/varcadd-pathogenicity/) | VARCADD pathogenicity scoring for coding variants from structure and evolution. |
| [variant-interpretation-acmg](skills/variant-interpretation-acmg/) | ACMG/AMP variant interpretation with evidence-based classification framework. |
| [gene-panel-design-agent](skills/gene-panel-design-agent/) | Design targeted gene panels for clinical or research sequencing applications. |
| [pharmacogenomics-agent](skills/pharmacogenomics-agent/) | Pharmacogenomics analysis: variant-drug interaction prediction and dosing recommendations. |
| [multi-ancestry-prs-agent](skills/multi-ancestry-prs-agent/) | Multi-ancestry polygenic risk score computation with ancestry-specific weighting. |
| [prs-net-deep-learning-agent](skills/prs-net-deep-learning-agent/) | Deep learning PRS prediction with PRSnet for complex traits. |
| [cellfree-rna-agent](skills/cellfree-rna-agent/) | Cell-free RNA analysis: plasma cfRNA profiling for liquid biopsy diagnostics. |
| [long-read-sequencing-agent](skills/long-read-sequencing-agent/) | Long-read sequencing analysis: SV calling, methylation, isoform discovery, assembly. |
| [bayesian-optimizer](skills/bayesian-optimizer/) | Bayesian optimization for experimental design and hyperparameter tuning in biomedical research. |

</details>

### Clinical AI & Healthcare (BioOS)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [chatehr-clinician-assistant](skills/chatehr-clinician-assistant/) | EHR clinical assistant: note summarization, structured data extraction, clinical decision support. |
| [clinical-note-summarization](skills/clinical-note-summarization/) | Summarize clinical notes into structured SOAP format with key findings. |
| [clinical-nlp-extractor](skills/clinical-nlp-extractor/) | Extract clinical entities (diagnoses, medications, procedures) from unstructured text. |
| [ehr-fhir-integration](skills/ehr-fhir-integration/) | EHR-FHIR integration: HL7 FHIR resource creation, querying, and workflow automation. |
| [fhir-development](skills/fhir-development/) | FHIR API development: build SMART on FHIR apps and FHIR resource endpoints. |
| [digital-twin-clinical-agent](skills/digital-twin-clinical-agent/) | Create patient digital twins for treatment simulation and outcome prediction. |
| [trial-eligibility-agent](skills/trial-eligibility-agent/) | Assess patient eligibility for clinical trials from EHR data and trial criteria. |
| [trialgpt-matching](skills/trialgpt-matching/) | TrialGPT patient-to-trial matching with eligibility assessment from clinical notes. |
| [wearable-analysis-agent](skills/wearable-analysis-agent/) | Analyze wearable sensor data: activity, sleep, HRV, ECG for health monitoring. |
| [multimodal-medical-imaging](skills/multimodal-medical-imaging/) | Multimodal medical imaging analysis: CT, MRI, PET fusion and segmentation. |
| [prior-auth-coworker](skills/prior-auth-coworker/) | Prior authorization workflow assistant for insurance approval processes. |
| [care-coordination](skills/care-coordination/) | Care coordination agent: multi-disciplinary team communication and care plan management. |
| [claims-appeals](skills/claims-appeals/) | Insurance claims appeals: documentation preparation and denial reasoning analysis. |
| [lab-results](skills/lab-results/) | Lab result interpretation: reference ranges, trend analysis, critical value alerts. |
| [drug-interaction-checker](skills/drug-interaction-checker/) | Check drug-drug interactions from patient medication lists with severity scoring. |
| [regulatory-drafter](skills/regulatory-drafter/) | Draft regulatory submissions: FDA, EMA, ICH document preparation. |
| [regulatory-drafting](skills/regulatory-drafting/) | Regulatory writing and document structuring for medical device/drug submissions. |
| [biomedical-data-analysis](skills/biomedical-data-analysis/) | Comprehensive biomedical data analysis: statistics, visualization, and interpretation. |
| [data-visualization-biomedical](skills/data-visualization-biomedical/) | Biomedical-specific data visualization: clinical trial plots, survival curves, forest plots. |

</details>

### Research Infrastructure & Agents (BioOS)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [biomni-general-agent](skills/biomni-general-agent/) | BioMni general biomedical agent for flexible multi-step research tasks. |
| [biomni-research-agent](skills/biomni-research-agent/) | BioMni research-focused agent with literature, database, and analysis integration. |
| [biokernel](skills/biokernel/) | BioKernel: unified computational kernel for bioinformatics tool orchestration. |
| [biomcp-server](skills/biomcp-server/) | BioMCP: Model Context Protocol server for bioinformatics tool access. |
| [mcpmed-bioinformatics-server](skills/mcpmed-bioinformatics-server/) | MCP server providing medical bioinformatics tool access to agents. |
| [kragen-knowledge-graph](skills/kragen-knowledge-graph/) | KRAGEN knowledge graph for biomedical entity relationships and reasoning. |
| [leads-literature-mining](skills/leads-literature-mining/) | LEADS literature mining: automated extraction of biological findings from papers. |
| [knowledge-synthesis](skills/knowledge-synthesis/) | Synthesize knowledge from multiple biomedical sources into structured summaries. |
| [deep-research-swarm](skills/deep-research-swarm/) | Multi-agent swarm for deep scientific research with parallel literature synthesis. |
| [research-literature](skills/research-literature/) | Research literature management: search, organize, and synthesize scientific papers. |
| [search-strategy](skills/search-strategy/) | Design systematic search strategies for scientific literature and databases. |
| [scientific-manuscript](skills/scientific-manuscript/) | Scientific manuscript writing and revision with journal-specific formatting. |
| [cellular-senescence-agent](skills/cellular-senescence-agent/) | Cellular senescence analysis: marker scoring, SASP profiling, tissue aging assessment. |
| [ngs-analysis](skills/ngs-analysis/) | Next-generation sequencing data analysis orchestration and QC. |
| [opentrons-protocol-agent](skills/opentrons-protocol-agent/) | Opentrons liquid handler protocol design for automated lab workflows. |
| [virtual-lab-agent](skills/virtual-lab-agent/) | Virtual lab agent for in silico experiment simulation and protocol optimization. |
| [data-visualization-expert](skills/data-visualization-expert/) | Expert data visualization for complex scientific and clinical datasets. |
| [lobster-bioinformatics](skills/lobster-bioinformatics/) | Run bioinformatics analyses via Lobster AI: scRNA-seq, bulk RNA-seq, literature mining, dataset discovery, QC, and visualization. |

</details>

</details>

## 📊 Data Science & Tools

<details open>
<summary>Expand/Collapse this category</summary>

### Statistics & Data Analysis

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [statistical-analysis](skills/statistical-analysis/) | Statistical analysis toolkit. Hypothesis tests (t-test, ANOVA, chi-square), regression, correlation, Bayesian stats, power analysis, assumption checks, APA reporting. |
| [statsmodels](skills/statsmodels/) | Statistical modeling: OLS, GLM, logistic, ARIMA, time series, hypothesis tests, diagnostics, AIC/BIC, for rigorous statistical inference. |
| [pymc](skills/pymc/) | Bayesian modeling with PyMC. Build hierarchical models, MCMC (NUTS), variational inference, LOO/WAIC comparison, posterior checks, for probabilistic programming. |
| [simpy](skills/simpy/) | Process-based discrete-event simulation for clinical systems: queues, resources, time-based events. Useful for modeling hospital workflows and patient flow. |
| [exploratory-data-analysis](skills/exploratory-data-analysis/) | Comprehensive exploratory data analysis on scientific data files across 200+ file formats — structure, content, quality assessment, and visualization. |
| [data-stats-analysis](skills/data-stats-analysis/) | Statistical tests, hypothesis testing, correlation analysis, and multiple testing corrections using scipy and statsmodels (OmicVerse). |
| [data-transform](skills/data-transform/) | Transform, clean, reshape, and preprocess biological data using pandas and numpy (OmicVerse). |
| [data-viz-plots](skills/data-viz-plots/) | Create publication-quality plots and visualizations using matplotlib and seaborn (OmicVerse). |
| [scientific-visualization](skills/scientific-visualization/) | Create publication figures with matplotlib/seaborn/plotly. Multi-panel layouts, error bars, significance markers, colorblind-safe, PDF/EPS/TIFF export. |

</details>

### Lab Automation & Integration

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [opentrons-integration](skills/opentrons-integration/) | Lab automation platform for Flex/OT-2 robots. Write Protocol API v2 protocols, liquid handling, hardware modules (heater-shaker, thermocycler), labware management. |
| [pylabrobot](skills/pylabrobot/) | Laboratory automation toolkit for controlling liquid handlers, plate readers, pumps, heater shakers, incubators, centrifuges, and analytical equipment. |
| [benchling-integration](skills/benchling-integration/) | Benchling R&D platform integration. Access registry (DNA, proteins), inventory, ELN entries, workflows via API, build Benchling Apps, for lab data management automation. |
| [labarchive-integration](skills/labarchive-integration/) | Electronic lab notebook API integration. Access notebooks, manage entries/attachments, backup notebooks, integrate with Protocols.io/Jupyter/REDCap. |
| [protocolsio-integration](skills/protocolsio-integration/) | Integration with protocols.io API for managing scientific protocols — search, create, update, publish protocols, and manage protocol steps and reagents. |
| [instrument-data-to-allotrope](skills/instrument-data-to-allotrope/) | Convert laboratory instrument output files (PDF, CSV, Excel, TXT) to Allotrope Simple Model (ASM) JSON format for LIMS systems, data lakes, and downstream analysis. |

</details>

### Scientific Research & Writing

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [scientific-writing](skills/scientific-writing/) | Write scientific manuscripts in full paragraphs using a two-stage process: section outlines then full text. Covers all sections of research papers. |
| [scientific-critical-thinking](skills/scientific-critical-thinking/) | Evaluate research rigor. Assess methodology, experimental design, statistical validity, biases, confounding, evidence quality (GRADE, Cochrane ROB). |
| [scientific-brainstorming](skills/scientific-brainstorming/) | Research ideation partner. Generate hypotheses, explore interdisciplinary connections, challenge assumptions, develop methodologies, identify research gaps. |
| [hypothesis-generation](skills/hypothesis-generation/) | Generate testable hypotheses. Formulate from observations, design experiments, explore competing explanations, develop predictions, propose mechanisms. |
| [scientific-problem-selection](skills/scientific-problem-selection/) | Help scientists with research problem selection, project ideation, troubleshooting stuck projects, and strategic scientific decisions. |
| [peer-review](skills/peer-review/) | Systematic peer review toolkit. Evaluate methodology, statistics, design, reproducibility, ethics, figure integrity, reporting standards, for manuscript and grant review. |
| [citation-management](skills/citation-management/) | Comprehensive citation management. Search Google Scholar and PubMed for papers, extract accurate metadata, validate citations, generate BibTeX entries. |
| [research-grants](skills/research-grants/) | Write competitive research proposals for NSF, NIH, DOE, and DARPA. Agency-specific formatting, review criteria, budget preparation, broader impacts. |
| [research-lookup](skills/research-lookup/) | Look up current research using Perplexity's Sonar Pro Search or Sonar Reasoning Pro via OpenRouter. Automatically selects best model for the query complexity. |
| [biomni](skills/biomni/) | Autonomous biomedical AI agent framework for executing complex research tasks across genomics, drug discovery, molecular biology, and clinical analysis. |
| [treatment-plans](skills/treatment-plans/) | Generate concise (3-4 page) medical treatment plans in LaTeX/PDF format for all clinical specialties including general medicine, rehabilitation, mental health, and chronic disease. |

</details>

### Analyst Personas

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [biologist-analyst](skills/biologist-analyst/) | Expert biologist analyst persona for interpreting biological experiments, sequencing data, cell biology assays, and molecular biology research. |
| [chemist-analyst](skills/chemist-analyst/) | Expert chemist analyst persona for interpreting chemical data, synthesis routes, spectroscopic results, reaction mechanisms, and laboratory analyses. |
| [epidemiologist-analyst](skills/epidemiologist-analyst/) | Expert epidemiologist analyst persona for study design, cohort analysis, risk factor assessment, public health surveillance, and causal inference. |
| [psychologist-analyst](skills/psychologist-analyst/) | Expert psychologist analyst persona for behavioral data analysis, psychological assessment interpretation, clinical case formulation, and mental health research. |

</details>

### Public Health & Time Series

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [datacommons-client](skills/datacommons-client/) | Access public health statistics from Google Data Commons: disease prevalence, demographic data, health indicators across global sources. |
| [timesfm-forecasting](skills/timesfm-forecasting/) | Zero-shot time series forecasting with Google's TimesFM. For vital sign trends, health sensor data, and longitudinal health monitoring without custom model training. |
| [aeon](skills/aeon/) | Time series ML: classification, regression, clustering, anomaly detection, segmentation for temporal health data and sequential clinical measurements. |

</details>

### Scientific Literature & Reference Management

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [bgpt-paper-search](skills/bgpt-paper-search/) | Search scientific papers with BGPT MCP server. Returns 25+ structured fields per paper: methods, results, sample sizes, quality scores. For literature reviews and evidence synthesis. |
| [pyzotero](skills/pyzotero/) | Interact with Zotero reference libraries programmatically via Zotero Web API v3. Retrieve, create, update items, export citations, upload PDFs, and build research automation workflows. |
| [open-notebook](skills/open-notebook/) | Self-hosted NotebookLM alternative. Ingest PDFs, videos, web pages, documents; generate AI-powered notes; chat with research materials; supports 16+ AI providers. |

</details>

### Data Processing & Scientific Computing

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [dask](skills/dask/) | Distributed computing for larger-than-RAM genomics/omics datasets. Scale pandas/NumPy beyond memory, parallel file processing, distributed ML. |
| [polars](skills/polars/) | Fast in-memory DataFrame library (1-100GB). Faster pandas replacement for biomedical data ETL and analysis pipelines. |
| [vaex](skills/vaex/) | Out-of-core DataFrame operations for billions of rows. Fast statistics and visualization for large genomic and clinical datasets. |
| [zarr-python](skills/zarr-python/) | Chunked N-D arrays for cloud storage. Compressed arrays, parallel I/O, S3/GCS integration for large-scale omics data. |
| [pytorch-lightning](skills/pytorch-lightning/) | Organized PyTorch deep learning for biomedical AI: multi-GPU training, callbacks, logging, distributed training for clinical/genomic models. |

</details>

### Scientific Visualization & Communication

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [matplotlib](skills/matplotlib/) | Low-level plotting library for full customization. Publication-quality figures for scientific manuscripts and journals. |
| [seaborn](skills/seaborn/) | Statistical visualization with pandas integration. Box plots, violin plots, heatmaps, pair plots for biomedical data exploration. |
| [plotly](skills/plotly/) | Interactive visualization. Hover info, zoom, dashboards for exploratory biomedical analysis and presentations. |
| [infographics](skills/infographics/) | Create professional scientific infographics with iterative AI refinement. Supports 10 infographic types and 8 industry styles. |
| [scientific-schematics](skills/scientific-schematics/) | Publication-quality scientific diagrams: neural network architectures, biological pathways, system diagrams, flowcharts. |
| [scientific-slides](skills/scientific-slides/) | Build research presentation slide decks for conferences, seminars, thesis defenses. PowerPoint and LaTeX Beamer support. |
| [latex-posters](skills/latex-posters/) | Create professional research posters in LaTeX (beamerposter, tikzposter). Conference posters with multi-column layouts. |
| [pptx-posters](skills/pptx-posters/) | HTML/CSS research posters exportable to PDF or PPTX. Modern web-based poster design. |
| [markdown-mermaid-writing](skills/markdown-mermaid-writing/) | Scientific documentation with Markdown and 24 Mermaid diagram types. 9 document templates for scientific reports. |
| [paper-2-web](skills/paper-2-web/) | Convert academic papers to interactive websites, presentation videos, and conference posters (Paper2Web, Paper2Video, Paper2Poster). |

</details>

### Additional Scientific Tools

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [pymoo](skills/pymoo/) | Multi-objective optimization with PYMOO. Drug design parameter optimization, Pareto front analysis, evolutionary algorithms. |
| [markitdown](skills/markitdown/) | Convert documents (PDF, DOCX, PPTX, HTML, images) to Markdown for processing and analysis. |
| [perplexity-search](skills/perplexity-search/) | AI-powered search via Perplexity for real-time scientific information retrieval. |
| [geopandas](skills/geopandas/) | Geospatial data analysis with GeoPandas. Epidemiology mapping, disease distribution, spatial health analytics. |
| [hypogenic](skills/hypogenic/) | Automated hypothesis generation and testing on tabular datasets. Combine literature insights with data-driven hypothesis validation. |
| [pdf-processing](skills/pdf-processing/) | Advanced PDF processing: text extraction, table parsing, annotation, form filling. |
| [pdf-processing-pro](skills/pdf-processing-pro/) | Professional PDF processing with enhanced OCR, multi-column layout handling, and batch processing. |
| [pdf-anthropic](skills/pdf-anthropic/) | Anthropic-optimized PDF analysis for scientific and medical document comprehension. |
| [xlsx-official](skills/xlsx-official/) | Official Excel/XLSX skill for spreadsheet creation, analysis, and data management. |
| [docx-official](skills/docx-official/) | Official Word/DOCX skill for document creation, editing, and formatting. |
| [pptx-official](skills/pptx-official/) | Official PowerPoint/PPTX skill for presentation creation and editing. |

</details>

### Computational Simulation & Ontology (HeshamFS/materials-simulation-skills)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [ontology-validator](skills/ontology-validator/) | Validate biomedical ontology structures and term relationships (HPO, GO, MeSH, SNOMED, OBO). |
| [ontology-explorer](skills/ontology-explorer/) | Navigate and query biomedical ontologies: term hierarchies, annotations, cross-references. |
| [ontology-mapper](skills/ontology-mapper/) | Map between biomedical ontologies: HPO↔OMIM, GO↔UniProt, disease↔phenotype cross-ontology. |
| [slurm-job-script-generator](skills/slurm-job-script-generator/) | Generate SLURM sbatch scripts for HPC genomics/bioinformatics pipeline jobs with optimized resource requests. |
| [numerical-integration](skills/numerical-integration/) | Select and configure ODE/PDE time integration for biological model simulation (stiff systems, IMEX). |
| [nonlinear-solvers](skills/nonlinear-solvers/) | Configure nonlinear solvers for biological network optimization, parameter fitting, FBA. |
| [parameter-optimization](skills/parameter-optimization/) | Design of experiments, sensitivity analysis, Bayesian optimization for biological model calibration. |
| [linear-solvers](skills/linear-solvers/) | Select linear solvers for large-scale biological network and metabolic model computations. |
| [numerical-stability](skills/numerical-stability/) | Analyze numerical stability for time-dependent biological simulations (CFL criteria, stiffness). |
| [simulation-orchestrator](skills/simulation-orchestrator/) | Orchestrate multi-simulation campaigns: parameter sweeps, batch jobs, result aggregation. |
| [simulation-validator](skills/simulation-validator/) | Validate simulations: pre-flight checks, runtime monitoring, convergence, NaN/Inf detection. |
| [convergence-study](skills/convergence-study/) | Spatial/temporal convergence analysis with Richardson extrapolation for simulation verification. |
| [post-processing](skills/post-processing/) | Extract, analyze, and visualize simulation output data: time series, field profiles, statistics. |
| [performance-profiling](skills/performance-profiling/) | Identify computational bottlenecks, analyze scaling behavior, optimize HPC simulation jobs. |
| [differentiation-schemes](skills/differentiation-schemes/) | Select finite difference/volume/spectral schemes for PDE discretization in biological models. |
| [time-stepping](skills/time-stepping/) | Adaptive time-step control for biological dynamics: CFL constraints, checkpoint scheduling. |
| [mesh-generation](skills/mesh-generation/) | Mesh generation for numerical simulations: resolution, quality metrics, adaptive refinement. |

</details>

### Developer Workflow Skills (obra/superpowers)

<details>
<summary>Click to expand skill list</summary>

| Skill | Description |
|-------|-------------|
| [test-driven-development](skills/test-driven-development/) | TDD workflow: write tests before implementation, red-green-refactor cycle for reliable code. |
| [systematic-debugging](skills/systematic-debugging/) | Structured debugging approach: hypothesis formation, evidence gathering, root cause analysis. |
| [dispatching-parallel-agents](skills/dispatching-parallel-agents/) | Orchestrate parallel subagents for independent tasks to maximize throughput. |
| [writing-plans](skills/writing-plans/) | Write structured implementation plans before touching code for complex multi-step tasks. |
| [executing-plans](skills/executing-plans/) | Execute written implementation plans with review checkpoints in isolated sessions. |
| [brainstorming](skills/brainstorming/) | Structured creative exploration of requirements and design before implementation. |
| [writing-skills](skills/writing-skills/) | Create and verify new SKILL.md skills with proper format and deployment validation. |
| [verification-before-completion](skills/verification-before-completion/) | Run verification commands and confirm outputs before claiming work is complete. |
| [requesting-code-review](skills/requesting-code-review/) | Structure code review requests with context, changes summary, and specific questions. |
| [receiving-code-review](skills/receiving-code-review/) | Process code review feedback with technical rigor rather than blind acceptance. |
| [subagent-driven-development](skills/subagent-driven-development/) | Break development tasks into subtasks for parallel subagent execution. |
| [using-git-worktrees](skills/using-git-worktrees/) | Create isolated git worktrees for feature work and plan execution. |
| [finishing-a-development-branch](skills/finishing-a-development-branch/) | Complete development branches: merge, PR, or cleanup with structured decision options. |
| [using-superpowers](skills/using-superpowers/) | Meta-skill: discover and use available skills for any task at conversation start. |

</details>

</details>

## Acknowledgements

We have benefited from the following excellent projects. If you’re interested, please check them out.

1. [awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
2. [Anthropics Skills](https://github.com/anthropics/skills)
3. [Skillsmp](https://skillsmp.com/)
4. [awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills)
5. [ClawHub](https://clawhub.ai/)
6. [水产市场](https://openclawmp.cc/)
7. [Skills.Sh](https://skills.sh/)
8. [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
9. [llmbase](https://llmbase.ai/openclaw/)
10. [OpenClaw](https://docs.openclaw.ai/zh-CN)
11. [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)
12. [claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills)
13. [LLMs-Universal-Life-Science-and-Clinical-Skills-](https://github.com/mdbabumiamssm/LLMs-Universal-Life-Science-and-Clinical-Skills-)
14. [BioClaw](https://github.com/Runchuan-BU/BioClaw)
15. [ClawBio](https://github.com/ClawBio/ClawBio)


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=FreedomIntelligence/OpenClaw-Medical-Skills&type=Date)](https://star-history.com/#FreedomIntelligence/OpenClaw-Medical-Skills&Date)
