# long-read-sequencing-agent

> AI-powered analysis of long-read sequencing data (PacBio, ONT) for structural variant detection, isoform discovery, epigenetic modifications, and de novo assembly.

**Available tools:** Read, Bash

# Long-Read Sequencing Agent

The **Long-Read Sequencing Agent** provides comprehensive AI-driven analysis of long-read sequencing data from PacBio (HiFi) and Oxford Nanopore (ONT) platforms. It enables structural variant detection, full-length isoform discovery, base modification calling, and de novo genome assembly.

## When to Use This Skill

* When detecting structural variants (SVs) missed by short-read sequencing.
* To characterize full-length transcript isoforms and alternative splicing.
* For detecting DNA base modifications (5mC, 6mA) directly from sequencing.
* When performing de novo genome assembly for complex regions.
* To phase variants and generate fully-resolved haplotypes.

## Core Capabilities

1. **Structural Variant Detection**: AI-enhanced SV calling for deletions, insertions, inversions, translocations, and complex rearrangements.

2. **Isoform Discovery**: Full-length transcript sequencing for novel isoform and fusion detection.

3. **Base Modification Calling**: Direct detection of DNA methylation (5mC, 5hmC, 6mA) from native sequencing.

4. **Haplotype Phasing**: Phase-resolved assemblies and variant calling.

5. **De Novo Assembly**: Assemble complex genomic regions (centromeres, telomeres, HLA).

6. **Error Correction**: AI-based error correction for long-read data.

## Platform Comparison

| Feature | PacBio HiFi | ONT (R10+) |
|---------|-------------|------------|
| Read length | 15-25 kb | >100 kb possible |
| Accuracy | >99.9% (HiFi) | >99% (Q20+) |
| Base mods | 5mC, 6mA | 5mC, 5hmC, 6mA, more |
| Throughput | 20-40 Gb/run | 100+ Gb/run |
| Cost | Higher | Lower |

## Workflow

1. **Input**: Long-read FASTQ/BAM files from PacBio or ONT sequencing.

2. **QC & Alignment**: Filter reads by quality, align to reference genome.

3. **SV Calling**: Detect structural variants using Sniffles, PBSV, or CuteSV.

4. **Isoform Analysis**: Identify full-length isoforms with IsoSeq or FLAIR.

5. **Modification Calling**: Extract base modifications from signal data.

6. **Phasing**: Generate haplotype-resolved variant calls.

7. **Output**: SV calls, isoform annotations, modification maps, phased assemblies.

## Example Usage

**User**: "Analyze this PacBio HiFi dataset for structural variants and DNA methylation in a cancer sample."

**Agent Action**:
```bash
python3 Skills/Genomics/Long_Read_Sequencing_Agent/longread_analyzer.py \
    --input cancer_hifi.bam \
    --platform pacbio_hifi \
    --reference GRCh38.fa \
    --sv_calling sniffles2 \
    --methylation true \
    --phasing true \
    --output longread_results/
```

## Structural Variant Detection

| Tool | Platform | SV Types | Strengths |
|------|----------|----------|-----------|
| Sniffles2 | Both | All SV types | Speed, accuracy |
| PBSV | PacBio | All SV types | HiFi optimized |
| CuteSV | Both | All SV types | Sensitivity |
| SAVANA | Both | Somatic SVs | Cancer-specific |
| Jasmine | Both | Population SV | Multi-sample |

**SV Size Spectrum**:
- Small SVs: 50-500 bp (often missed by short-read)
- Medium SVs: 500 bp - 10 kb
- Large SVs: >10 kb
- Complex SVs: Multi-breakpoint events

## Isoform Analysis

**Full-Length Transcript Sequencing**:
- Capture full gene structures (5' to 3')
- Detect novel exons and splice junctions
- Identify gene fusions
- Quantify isoform expression

**Tools**:
- IsoSeq3 (PacBio): Clustering and polishing
- FLAIR (Both): Isoform discovery and quantification
- StringTie2 (Both): Guided assembly
- SQANTI3: Isoform classification and QC

## Base Modification Detection

| Modification | Detection | Biological Role |
|--------------|-----------|-----------------|
| 5mC | Both platforms | Gene silencing |
| 5hmC | ONT primarily | Active demethylation |
| 6mA | Both platforms | Bacterial/mitochondrial |
| BrdU | ONT | Replication timing |

**Resolution**: Single-base, single-molecule, strand-specific

## AI/ML Components

**Error Correction**:
- DeepConsensus (PacBio): Transformer for HiFi calling
- Medaka (ONT): Neural network polishing
- PEPPER-Margin-DeepVariant: AI variant calling

**SV Classification**:
- Deep learning for complex SV characterization
- ML filters for false positive reduction
- Multi-sample joint calling

## Clinical Applications

1. **Cancer Genomics**: Detect SVs driving oncogene activation
2. **Rare Disease**: Resolve variants in complex regions
3. **Pharmacogenomics**: Phase CYP450 star alleles
4. **HLA Typing**: Full-resolution typing for transplant
5. **Repeat Expansions**: Size tandem repeat diseases

## Prerequisites

* Python 3.10+
* Sniffles2, PBSV, CuteSV for SV calling
* minimap2/pbmm2 for alignment
* High-memory system (64GB+ recommended)

## Related Skills

* Long_Read_SV_Caller - For specialized SV analysis
* Variant_Interpretation - For variant annotation
* Epigenomics_MethylGPT_Agent - For methylation analysis

## Output Files

| Output | Format | Content |
|--------|--------|---------|
| SVs | VCF | Structural variants |
| Methylation | BED/bigWig | Modification calls |
| Isoforms | GTF | Transcript annotations |
| Phased | VCF | Haplotype-resolved variants |
| Assembly | FASTA | Assembled contigs |

## Author

AI Group - Biomedical AI Platform
