# bio-workflow-management-wdl-workflows

> Create portable bioinformatics pipelines with Workflow Description Language (WDL) using Cromwell or miniwdl execution engines. Use when running GATK best practices pipelines, working with Terra/AnVIL platforms, or building workflows for cloud execution on Google Cloud or AWS.

**Available tools:** Read, Bash

# WDL Workflows

## Basic Task Definition

```wdl
version 1.0

task fastqc {
    input {
        File fastq
        Int threads = 2
    }

    command <<<
        fastqc -t ~{threads} ~{fastq}
    >>>

    output {
        File html = glob("*_fastqc.html")[0]
        File zip = glob("*_fastqc.zip")[0]
    }

    runtime {
        docker: "biocontainers/fastqc:v0.11.9"
        cpu: threads
        memory: "4 GB"
    }
}
```

## Simple Workflow

```wdl
version 1.0

workflow rnaseq {
    input {
        File fastq_1
        File fastq_2
        File salmon_index
    }

    call fastp {
        input:
            reads_1 = fastq_1,
            reads_2 = fastq_2
    }

    call salmon_quant {
        input:
            reads_1 = fastp.trimmed_1,
            reads_2 = fastp.trimmed_2,
            index = salmon_index
    }

    output {
        File quant_sf = salmon_quant.quant_file
    }
}
```

## Task with All Sections

```wdl
version 1.0

task bwa_mem {
    input {
        File reference
        File reference_index
        File reads_1
        File reads_2
        String sample_id
        Int threads = 8
    }

    Int disk_size = ceil(size(reference, "GB") + size(reads_1, "GB") * 3) + 20

    command <<<
        bwa mem -t ~{threads} -R "@RG\tID:~{sample_id}\tSM:~{sample_id}" \
            ~{reference} ~{reads_1} ~{reads_2} | \
            samtools sort -@ ~{threads} -o ~{sample_id}.sorted.bam
        samtools index ~{sample_id}.sorted.bam
    >>>

    output {
        File bam = "~{sample_id}.sorted.bam"
        File bai = "~{sample_id}.sorted.bam.bai"
    }

    runtime {
        docker: "biocontainers/bwa:v0.7.17"
        cpu: threads
        memory: "16 GB"
        disks: "local-disk " + disk_size + " HDD"
    }
}
```

## Scatter (Parallel Execution)

```wdl
version 1.0

workflow process_samples {
    input {
        Array[File] fastq_files
        File reference
    }

    scatter (fastq in fastq_files) {
        call align {
            input:
                fastq = fastq,
                reference = reference
        }
    }

    output {
        Array[File] bam_files = align.bam
    }
}
```

## Scatter with Paired Files

```wdl
version 1.0

struct SampleFastqs {
    String sample_id
    File fastq_1
    File fastq_2
}

workflow paired_alignment {
    input {
        Array[SampleFastqs] samples
        File reference
    }

    scatter (sample in samples) {
        call align {
            input:
                sample_id = sample.sample_id,
                reads_1 = sample.fastq_1,
                reads_2 = sample.fastq_2,
                reference = reference
        }
    }

    output {
        Array[File] bams = align.bam
    }
}
```

## Conditional Execution

```wdl
version 1.0

workflow conditional_qc {
    input {
        File fastq
        Boolean run_qc = true
    }

    if (run_qc) {
        call fastqc {
            input:
                fastq = fastq
        }
    }

    output {
        File? qc_report = fastqc.html
    }
}
```

## Structs and Complex Types

```wdl
version 1.0

struct ReferenceData {
    File fasta
    File fasta_index
    File dict
    File? known_sites
}

workflow variant_calling {
    input {
        ReferenceData reference
        Array[File] bam_files
    }

    scatter (bam in bam_files) {
        call haplotype_caller {
            input:
                bam = bam,
                ref_fasta = reference.fasta,
                ref_index = reference.fasta_index,
                ref_dict = reference.dict
        }
    }
}
```

## Input JSON

```json
{
    "rnaseq.fastq_1": "data/sample1_R1.fq.gz",
    "rnaseq.fastq_2": "data/sample1_R2.fq.gz",
    "rnaseq.salmon_index": "ref/salmon_index",
    "rnaseq.threads": 8
}
```

## Array Inputs JSON

```json
{
    "process_samples.samples": [
        {
            "sample_id": "sample1",
            "fastq_1": "data/sample1_R1.fq.gz",
            "fastq_2": "data/sample1_R2.fq.gz"
        },
        {
            "sample_id": "sample2",
            "fastq_1": "data/sample2_R1.fq.gz",
            "fastq_2": "data/sample2_R2.fq.gz"
        }
    ],
    "process_samples.reference": "ref/genome.fa"
}
```

## Subworkflows

```wdl
version 1.0

import "qc.wdl" as qc
import "align.wdl" as align

workflow main_pipeline {
    input {
        File fastq_1
        File fastq_2
        File reference
    }

    call qc.quality_control {
        input:
            reads_1 = fastq_1,
            reads_2 = fastq_2
    }

    call align.alignment {
        input:
            reads_1 = quality_control.trimmed_1,
            reads_2 = quality_control.trimmed_2,
            reference = reference
    }
}
```

## Runtime Options

```wdl
runtime {
    docker: "ubuntu:20.04"
    cpu: 4
    memory: "8 GB"
    disks: "local-disk 100 HDD"
    preemptible: 3
    maxRetries: 2
    zones: "us-central1-a us-central1-b"
    bootDiskSizeGb: 15
}
```

## String Interpolation and Expressions

```wdl
version 1.0

task process {
    input {
        String sample_id
        Int memory_gb = 8
        Array[File] input_files
    }

    Int memory_mb = memory_gb * 1000
    String output_name = sample_id + ".processed.bam"

    command <<<
        # Access array elements
        process_tool \
            --memory ~{memory_mb} \
            --inputs ~{sep=' ' input_files} \
            --output ~{output_name}
    >>>

    output {
        File result = output_name
    }
}
```

## File Size and Disk Calculation

```wdl
version 1.0

task align {
    input {
        File reads_1
        File reads_2
        File reference
    }

    # Calculate disk: input files + 3x for outputs + buffer
    Int disk_gb = ceil(size(reads_1, "GB") + size(reads_2, "GB") +
                       size(reference, "GB") * 2) + 50

    command <<<
        bwa mem ~{reference} ~{reads_1} ~{reads_2} > aligned.sam
    >>>

    runtime {
        disks: "local-disk " + disk_gb + " SSD"
    }
}
```

## Complete RNA-seq Workflow

```wdl
version 1.0

workflow rnaseq_pipeline {
    input {
        Array[String] sample_ids
        Array[File] fastq_1_files
        Array[File] fastq_2_files
        File salmon_index
        Int threads = 8
    }

    scatter (idx in range(length(sample_ids))) {
        call fastp {
            input:
                sample_id = sample_ids[idx],
                reads_1 = fastq_1_files[idx],
                reads_2 = fastq_2_files[idx],
                threads = threads
        }

        call salmon_quant {
            input:
                sample_id = sample_ids[idx],
                reads_1 = fastp.trimmed_1,
                reads_2 = fastp.trimmed_2,
                index = salmon_index,
                threads = threads
        }
    }

    output {
        Array[File] quant_files = salmon_quant.quant_sf
        Array[File] fastp_reports = fastp.json_report
    }
}

task fastp {
    input {
        String sample_id
        File reads_1
        File reads_2
        Int threads = 4
    }

    command <<<
        fastp -i ~{reads_1} -I ~{reads_2} \
            -o ~{sample_id}_trimmed_R1.fq.gz \
            -O ~{sample_id}_trimmed_R2.fq.gz \
            --json ~{sample_id}_fastp.json \
            --thread ~{threads}
    >>>

    output {
        File trimmed_1 = "~{sample_id}_trimmed_R1.fq.gz"
        File trimmed_2 = "~{sample_id}_trimmed_R2.fq.gz"
        File json_report = "~{sample_id}_fastp.json"
    }

    runtime {
        docker: "quay.io/biocontainers/fastp:0.23.4--hadf994f_2"
        cpu: threads
        memory: "4 GB"
    }
}

task salmon_quant {
    input {
        String sample_id
        File reads_1
        File reads_2
        File index
        Int threads = 8
    }

    command <<<
        salmon quant -i ~{index} -l A \
            -1 ~{reads_1} -2 ~{reads_2} \
            -o ~{sample_id}_salmon \
            --threads ~{threads} --validateMappings
    >>>

    output {
        File quant_sf = "~{sample_id}_salmon/quant.sf"
        File quant_dir = "~{sample_id}_salmon"
    }

    runtime {
        docker: "quay.io/biocontainers/salmon:1.10.0--h7e5ed60_0"
        cpu: threads
        memory: "16 GB"
    }
}
```

## Run Commands

```bash
# Validate WDL syntax
womtool validate workflow.wdl

# Generate inputs template
womtool inputs workflow.wdl > inputs.json

# Run with Cromwell (local)
java -jar cromwell.jar run workflow.wdl -i inputs.json

# Run with miniwdl (simpler local runner)
miniwdl run workflow.wdl -i inputs.json

# Run on Terra
# Upload WDL and inputs.json to Terra workspace
```

## Execution Engines

| Engine | Use Case |
|--------|----------|
| Cromwell | Full-featured, Google Cloud, AWS, HPC |
| miniwdl | Lightweight local execution |
| Terra | Cloud platform with Cromwell backend |
| AnVIL | NIH cloud platform (Terra-based) |
| dxWDL | DNAnexus platform |

## Related Skills

- workflow-management/cwl-workflows - CWL alternative
- workflow-management/snakemake-workflows - Python-based alternative
- workflow-management/nextflow-pipelines - Groovy-based alternative
