# bio-metagenomics-metaphlan

> Marker gene-based taxonomic profiling using MetaPhlAn 4. Provides accurate species-level relative abundances using clade-specific markers. Use when accurate taxonomic profiling is needed and computational resources are limited, or for comparison with HMP/other MetaPhlAn studies.

## Version Compatibility

Reference examples tested with: Bowtie2 2.5.3+, MetaPhlAn 4.1+, minimap2 2.26+, pandas 2.2+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# MetaPhlAn 4 Profiling

**"Profile the species composition of my metagenome"** → Determine species-level relative abundances from shotgun metagenomic reads using clade-specific marker gene alignment.
- CLI: `metaphlan sample.fastq --input_type fastq -o profile.txt`

MetaPhlAn 4 uses ~5M clade-specific markers from 26,970 species-level genome bins. Supports both short reads (bowtie2) and long reads (minimap2).

## Basic Profiling

```bash
# Profile single sample
metaphlan sample.fastq.gz \
    --input_type fastq \
    --output_file profile.txt
```

## Paired-End Reads

```bash
# MetaPhlAn processes PE as single file or concatenated
metaphlan reads_R1.fastq.gz,reads_R2.fastq.gz \
    --input_type fastq \
    --output_file profile.txt \
    --mapout sample.map.bz2
```

## Save Mapping Output for Reuse

```bash
# First run - save intermediate mapping
metaphlan sample.fastq.gz \
    --input_type fastq \
    --mapout sample.map.bz2 \
    --output_file profile.txt

# Rerun with different settings without realigning
metaphlan sample.map.bz2 \
    --input_type mapout \
    --output_file profile_v2.txt
```

## Long-Read Support (MetaPhlAn 4+)

```bash
# Long reads automatically use minimap2 instead of bowtie2
metaphlan long_reads.fastq.gz \
    --input_type fastq \
    --output_file profile.txt
```

## Common Options

```bash
metaphlan sample.fastq.gz \
    --input_type fastq \
    --nproc 8 \                    # CPU threads
    --tax_lev s \                  # Taxonomic level (k,p,c,o,f,g,s,t)
    --min_cu_len 2000 \            # Min total nucleotide length
    --stat_q 0.2 \                 # Quantile for robust average
    --output_file profile.txt \
    --mapout sample.map.bz2
```

## Install Database

```bash
# Download database (done automatically on first run)
metaphlan --install

# Or specify database location
metaphlan --install --db_dir /path/to/db
```

## Analysis Types

```bash
# Relative abundances (default)
metaphlan sample.fastq.gz --input_type fastq -t rel_ab

# Relative abundances with read counts
metaphlan sample.fastq.gz --input_type fastq -t rel_ab_w_read_stats

# Marker presence/absence
metaphlan sample.fastq.gz --input_type fastq -t marker_pres_table

# Marker abundances
metaphlan sample.fastq.gz --input_type fastq -t marker_ab_table
```

## Multiple Samples

```bash
# Process each sample
for fq in samples/*.fastq.gz; do
    sample=$(basename $fq .fastq.gz)
    metaphlan $fq \
        --input_type fastq \
        --nproc 4 \
        --output_file profiles/${sample}_profile.txt \
        --mapout mapout/${sample}.map.bz2
done

# Merge profiles
merge_metaphlan_tables.py profiles/*_profile.txt > merged_abundance.txt
```

## Filter by Taxonomic Level

```bash
# Species only
metaphlan sample.fastq.gz --input_type fastq --tax_lev s -o species.txt

# Genus only
metaphlan sample.fastq.gz --input_type fastq --tax_lev g -o genus.txt

# All levels (default)
metaphlan sample.fastq.gz --input_type fastq --tax_lev a -o all_levels.txt
```

## Output Format

```
#SampleID	sample
#clade_name	relative_abundance
k__Bacteria	100.0
k__Bacteria|p__Proteobacteria	65.23
k__Bacteria|p__Proteobacteria|c__Gammaproteobacteria	62.15
k__Bacteria|p__Proteobacteria|c__Gammaproteobacteria|o__Enterobacterales	58.42
k__Bacteria|p__Proteobacteria|c__Gammaproteobacteria|o__Enterobacterales|f__Enterobacteriaceae	55.21
k__Bacteria|p__Proteobacteria|c__Gammaproteobacteria|o__Enterobacterales|f__Enterobacteriaceae|g__Escherichia	52.33
k__Bacteria|p__Proteobacteria|c__Gammaproteobacteria|o__Enterobacterales|f__Enterobacteriaceae|g__Escherichia|s__Escherichia_coli	52.33
```

## Parse Output in Python

```python
import pandas as pd

profile = pd.read_csv('profile.txt', sep='\t', comment='#', header=None,
                       names=['clade', 'abundance'])

species = profile[profile['clade'].str.contains('\\|s__')]
species['species'] = species['clade'].str.split('|').str[-1].str.replace('s__', '')
species.sort_values('abundance', ascending=False).head(20)
```

## Extract SGBs (Strain-level)

```bash
# Include strain-level genomic bins
metaphlan sample.fastq.gz \
    --input_type fastq \
    --tax_lev t \                  # Include t__ level (SGBs)
    --output_file profile_with_sgb.txt
```

## Sample Metadata in Output

```bash
# Add sample ID to output
metaphlan sample.fastq.gz \
    --input_type fastq \
    --sample_id sample_name \
    --output_file profile.txt
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| --input_type | fastq | Input format (fastq, mapout) |
| --nproc | 4 | CPU threads |
| --tax_lev | a | Taxonomic level (a=all) |
| --stat_q | 0.2 | Quantile value |
| --min_cu_len | 2000 | Min clade length |
| -t | rel_ab | Analysis type |
| --mapout | none | Save mapping output |
| --db_dir | default | Database directory |

Note: Unknown species estimation is now enabled by default in MetaPhlAn 4.2+

## Analysis Types (-t)

| Type | Description |
|------|-------------|
| rel_ab | Relative abundances (%) |
| rel_ab_w_read_stats | With read statistics |
| marker_pres_table | Marker presence/absence |
| marker_ab_table | Marker abundances |
| clade_specific_strain_tracker | Strain tracking |

## Related Skills

- kraken-classification - Alternative k-mer based classification
- abundance-estimation - Bracken for Kraken2 abundances
- metagenome-visualization - Visualize profiles
