# bio-workflow-management-nextflow-pipelines

> Create scalable, containerized bioinformatics pipelines with Nextflow DSL2 supporting Docker, Singularity, and cloud execution. Use when building portable pipelines with container support, running workflows on cloud platforms (AWS, Google Cloud), or leveraging nf-core community pipelines.

**Available tools:** Read, Bash

# Nextflow Pipelines

## Basic Pipeline Structure

```groovy
// main.nf
nextflow.enable.dsl=2

params.reads = "data/*_{1,2}.fq.gz"
params.outdir = "results"

process FASTQC {
    input:
    tuple val(sample_id), path(reads)

    output:
    path("*.html"), emit: html
    path("*.zip"), emit: zip

    script:
    """
    fastqc ${reads}
    """
}

workflow {
    Channel.fromFilePairs(params.reads)
        | FASTQC
}
```

## DSL2 Modules

```groovy
// modules/fastqc.nf
process FASTQC {
    tag "${sample_id}"
    publishDir "${params.outdir}/qc", mode: 'copy'

    input:
    tuple val(sample_id), path(reads)

    output:
    tuple val(sample_id), path("*.html"), emit: html
    tuple val(sample_id), path("*.zip"), emit: zip

    script:
    """
    fastqc -t ${task.cpus} ${reads}
    """
}
```

```groovy
// main.nf
include { FASTQC } from './modules/fastqc'
include { ALIGN } from './modules/align'

workflow {
    reads_ch = Channel.fromFilePairs(params.reads)
    FASTQC(reads_ch)
    ALIGN(reads_ch)
}
```

## Config File

```groovy
// nextflow.config
params {
    reads = "data/*_{1,2}.fq.gz"
    outdir = "results"
    genome = "ref/genome.fa"
}

process {
    cpus = 4
    memory = '8 GB'
    time = '2h'

    withName: 'ALIGN' {
        cpus = 16
        memory = '32 GB'
    }
}

profiles {
    docker {
        docker.enabled = true
    }
    singularity {
        singularity.enabled = true
    }
    slurm {
        process.executor = 'slurm'
    }
}
```

## Container Support

```groovy
process SALMON_QUANT {
    container 'quay.io/biocontainers/salmon:1.10.0--h7e5ed60_0'

    input:
    tuple val(sample_id), path(reads)
    path(index)

    output:
    tuple val(sample_id), path("${sample_id}"), emit: quant

    script:
    """
    salmon quant -i ${index} -l A -1 ${reads[0]} -2 ${reads[1]} \
        -o ${sample_id} --threads ${task.cpus}
    """
}
```

## Channel Operations

```groovy
// From file pairs
Channel.fromFilePairs("data/*_{1,2}.fq.gz")
    .set { reads_ch }

// From path
Channel.fromPath("data/*.bam")
    .map { file -> tuple(file.baseName, file) }
    .set { bam_ch }

// From samplesheet
Channel.fromPath(params.samplesheet)
    .splitCsv(header: true)
    .map { row -> tuple(row.sample, file(row.fastq_1), file(row.fastq_2)) }
    .set { samples_ch }

// Combine channels
reads_ch.combine(reference_ch)
```

## Subworkflows

```groovy
// subworkflows/qc.nf
include { FASTQC } from '../modules/fastqc'
include { MULTIQC } from '../modules/multiqc'

workflow QC {
    take:
    reads

    main:
    FASTQC(reads)
    MULTIQC(FASTQC.out.zip.collect())

    emit:
    qc_report = MULTIQC.out.report
}
```

```groovy
// main.nf
include { QC } from './subworkflows/qc'
include { ALIGN } from './subworkflows/align'

workflow {
    reads = Channel.fromFilePairs(params.reads)
    QC(reads)
    ALIGN(reads)
}
```

## Cluster Execution

```groovy
// nextflow.config for SLURM
process {
    executor = 'slurm'
    queue = 'normal'
    clusterOptions = '--account=myproject'

    withLabel: 'high_memory' {
        memory = '128 GB'
        queue = 'highmem'
    }
}

executor {
    name = 'slurm'
    queueSize = 100
    submitRateLimit = '10 sec'
}
```

## AWS/Cloud Execution

```groovy
// nextflow.config for AWS Batch
process {
    executor = 'awsbatch'
    queue = 'my-batch-queue'
}

aws {
    region = 'us-east-1'
    batch {
        cliPath = '/usr/local/bin/aws'
    }
}
```

```bash
# Run on AWS
nextflow run main.nf -profile awsbatch -bucket-dir s3://my-bucket/work
```

## Resource Labels

```groovy
process {
    withLabel: 'process_low' {
        cpus = 2
        memory = '4 GB'
        time = '1h'
    }
    withLabel: 'process_medium' {
        cpus = 8
        memory = '16 GB'
        time = '4h'
    }
    withLabel: 'process_high' {
        cpus = 16
        memory = '64 GB'
        time = '12h'
    }
}
```

```groovy
process ALIGN {
    label 'process_high'
    // ...
}
```

## Error Handling

```groovy
process RISKY_PROCESS {
    errorStrategy 'retry'
    maxRetries 3
    memory { 8.GB * task.attempt }

    script:
    """
    memory_intensive_command
    """
}

process OPTIONAL_PROCESS {
    errorStrategy 'ignore'
    // ...
}
```

## Caching and Resume

```bash
# Resume from last run
nextflow run main.nf -resume

# Clean work directory
nextflow clean -f

# Show execution trace
nextflow log
```

## Complete RNA-seq Pipeline

```groovy
nextflow.enable.dsl=2

params.reads = "data/*_{1,2}.fq.gz"
params.salmon_index = "ref/salmon_index"
params.outdir = "results"

process FASTP {
    tag "${sample_id}"
    publishDir "${params.outdir}/trimmed", mode: 'copy'

    input:
    tuple val(sample_id), path(reads)

    output:
    tuple val(sample_id), path("${sample_id}_{1,2}.trimmed.fq.gz"), emit: reads
    path("${sample_id}.json"), emit: json

    script:
    """
    fastp -i ${reads[0]} -I ${reads[1]} \
        -o ${sample_id}_1.trimmed.fq.gz -O ${sample_id}_2.trimmed.fq.gz \
        --json ${sample_id}.json --thread ${task.cpus}
    """
}

process SALMON_QUANT {
    tag "${sample_id}"
    publishDir "${params.outdir}/salmon", mode: 'copy'

    input:
    tuple val(sample_id), path(reads)
    path(index)

    output:
    tuple val(sample_id), path("${sample_id}"), emit: quant

    script:
    """
    salmon quant -i ${index} -l A -1 ${reads[0]} -2 ${reads[1]} \
        -o ${sample_id} --threads ${task.cpus}
    """
}

process MULTIQC {
    publishDir "${params.outdir}", mode: 'copy'

    input:
    path('*')

    output:
    path("multiqc_report.html")

    script:
    """
    multiqc .
    """
}

workflow {
    reads_ch = Channel.fromFilePairs(params.reads)
    index_ch = Channel.fromPath(params.salmon_index)

    FASTP(reads_ch)
    SALMON_QUANT(FASTP.out.reads, index_ch.first())

    qc_files = FASTP.out.json.collect()
        .mix(SALMON_QUANT.out.quant.collect())
    MULTIQC(qc_files.collect())
}
```

## Related Skills

- workflow-management/snakemake-workflows - Snakemake alternative
- workflows/rnaseq-to-de - End-to-end RNA-seq
- read-qc/fastp-workflow - QC processes
