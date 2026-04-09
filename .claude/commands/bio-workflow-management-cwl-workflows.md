# bio-workflow-management-cwl-workflows

> Create portable, standards-based bioinformatics pipelines with Common Workflow Language (CWL). Use when building workflows that need maximum portability across execution platforms, sharing pipelines with collaborators using different systems, or contributing to community workflow registries.

**Available tools:** Read, Bash

# CWL Workflows

## Basic Tool Definition

```yaml
# fastqc.cwl
cwlVersion: v1.2
class: CommandLineTool
baseCommand: fastqc

inputs:
  fastq:
    type: File
    inputBinding:
      position: 1

outputs:
  html:
    type: File
    outputBinding:
      glob: "*_fastqc.html"
  zip:
    type: File
    outputBinding:
      glob: "*_fastqc.zip"
```

## Tool with Parameters

```yaml
# bwa_mem.cwl
cwlVersion: v1.2
class: CommandLineTool
baseCommand: [bwa, mem]

requirements:
  DockerRequirement:
    dockerPull: biocontainers/bwa:v0.7.17
  ResourceRequirement:
    coresMin: 8
    ramMin: 16000

inputs:
  threads:
    type: int
    default: 8
    inputBinding:
      prefix: -t
      position: 1
  reference:
    type: File
    secondaryFiles:
      - .amb
      - .ann
      - .bwt
      - .pac
      - .sa
    inputBinding:
      position: 2
  reads_1:
    type: File
    inputBinding:
      position: 3
  reads_2:
    type: File?
    inputBinding:
      position: 4

stdout: aligned.sam

outputs:
  sam:
    type: stdout
```

## Basic Workflow

```yaml
# rnaseq.cwl
cwlVersion: v1.2
class: Workflow

inputs:
  fastq_1: File
  fastq_2: File
  salmon_index: Directory

outputs:
  quant_results:
    type: Directory
    outputSource: salmon/quant_dir

steps:
  fastp:
    run: fastp.cwl
    in:
      reads_1: fastq_1
      reads_2: fastq_2
    out: [trimmed_1, trimmed_2, json_report]

  salmon:
    run: salmon_quant.cwl
    in:
      index: salmon_index
      reads_1: fastp/trimmed_1
      reads_2: fastp/trimmed_2
    out: [quant_dir]
```

## Scatter (Parallel Execution)

```yaml
cwlVersion: v1.2
class: Workflow

requirements:
  ScatterFeatureRequirement: {}

inputs:
  fastq_files:
    type: File[]
  reference: File

outputs:
  bam_files:
    type: File[]
    outputSource: align/bam

steps:
  align:
    run: bwa_mem.cwl
    scatter: fastq
    in:
      fastq: fastq_files
      reference: reference
    out: [bam]
```

## Multi-Scatter

```yaml
requirements:
  ScatterFeatureRequirement: {}
  MultipleInputFeatureRequirement: {}

steps:
  align:
    run: bwa_mem.cwl
    scatter: [reads_1, reads_2]
    scatterMethod: dotproduct
    in:
      reads_1: fastq_1_array
      reads_2: fastq_2_array
      reference: reference
    out: [bam]
```

## Input File (Job)

```yaml
# job.yaml
fastq_1:
  class: File
  path: data/sample1_R1.fq.gz
fastq_2:
  class: File
  path: data/sample1_R2.fq.gz
salmon_index:
  class: Directory
  path: ref/salmon_index
threads: 8
```

## Secondary Files

```yaml
inputs:
  bam:
    type: File
    secondaryFiles:
      - .bai
  reference:
    type: File
    secondaryFiles:
      - pattern: .fai
        required: true
      - pattern: .dict
        required: false
```

## Docker and Singularity

```yaml
requirements:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/salmon:1.10.0--h7e5ed60_0

hints:
  SoftwareRequirement:
    packages:
      salmon:
        version: ["1.10.0"]
```

```bash
# Run with Docker
cwltool --docker workflow.cwl job.yaml

# Run with Singularity
cwltool --singularity workflow.cwl job.yaml
```

## Resource Requirements

```yaml
requirements:
  ResourceRequirement:
    coresMin: 4
    coresMax: 16
    ramMin: 8000
    ramMax: 32000
    outdirMin: 10000
    tmpdirMin: 10000
```

## Conditional Steps

```yaml
cwlVersion: v1.2
class: Workflow

requirements:
  InlineJavascriptRequirement: {}

inputs:
  run_qc: boolean
  fastq: File

steps:
  fastqc:
    run: fastqc.cwl
    when: $(inputs.run_qc)
    in:
      run_qc: run_qc
      fastq: fastq
    out: [html]
```

## Subworkflows

```yaml
# main.cwl
steps:
  qc_workflow:
    run: subworkflows/qc.cwl
    in:
      reads_1: fastq_1
      reads_2: fastq_2
    out: [qc_report, trimmed_1, trimmed_2]

  alignment_workflow:
    run: subworkflows/align.cwl
    in:
      reads_1: qc_workflow/trimmed_1
      reads_2: qc_workflow/trimmed_2
    out: [bam]
```

## File Arrays and Directories

```yaml
inputs:
  bam_files:
    type: File[]
  output_dir:
    type: string
    default: "results"

outputs:
  results:
    type: Directory
    outputBinding:
      glob: $(inputs.output_dir)
```

## JavaScript Expressions

```yaml
requirements:
  InlineJavascriptRequirement: {}

inputs:
  sample_name: string

outputs:
  output_bam:
    type: File
    outputBinding:
      glob: $(inputs.sample_name + ".sorted.bam")

arguments:
  - prefix: -o
    valueFrom: $(inputs.sample_name).sorted.bam
```

## InitialWorkDirRequirement

```yaml
requirements:
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.reference)
        writable: false
      - entryname: config.txt
        entry: |
          threads=$(inputs.threads)
          memory=$(inputs.memory)
```

## Complete RNA-seq Tool

```yaml
# salmon_quant.cwl
cwlVersion: v1.2
class: CommandLineTool
baseCommand: [salmon, quant]

requirements:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/salmon:1.10.0--h7e5ed60_0
  ResourceRequirement:
    coresMin: 8
    ramMin: 16000

inputs:
  index:
    type: Directory
    inputBinding:
      prefix: -i
  reads_1:
    type: File
    inputBinding:
      prefix: "-1"
  reads_2:
    type: File
    inputBinding:
      prefix: "-2"
  lib_type:
    type: string
    default: A
    inputBinding:
      prefix: -l
  threads:
    type: int
    default: 8
    inputBinding:
      prefix: --threads
  output_dir:
    type: string
    default: quant_output
    inputBinding:
      prefix: -o

outputs:
  quant_dir:
    type: Directory
    outputBinding:
      glob: $(inputs.output_dir)
```

## Run Commands

```bash
# Validate CWL file
cwltool --validate workflow.cwl

# Run workflow
cwltool workflow.cwl job.yaml

# Run with Docker
cwltool --docker workflow.cwl job.yaml

# Run with Singularity
cwltool --singularity workflow.cwl job.yaml

# Run with caching
cwltool --cachedir ./cache workflow.cwl job.yaml

# Run on Toil
toil-cwl-runner workflow.cwl job.yaml
```

## Execution Engines

| Engine | Use Case |
|--------|----------|
| cwltool | Reference implementation, local execution |
| Toil | HPC clusters, cloud (AWS, Google, Azure) |
| Arvados | Enterprise workflow management |
| CWL-Airflow | Airflow integration |

## Related Skills

- workflow-management/wdl-workflows - WDL alternative
- workflow-management/snakemake-workflows - Python-based alternative
- workflow-management/nextflow-pipelines - Groovy-based alternative
