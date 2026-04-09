# bio-metagenomics-kraken

> Taxonomic classification of metagenomic reads using Kraken2. Fast k-mer based classification against RefSeq database. Use when performing initial taxonomic classification of shotgun metagenomic reads before abundance estimation with Bracken.

## Version Compatibility

Reference examples tested with: Kraken2 2.1+, MetaPhlAn 4.1+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Kraken2 Classification

**"Classify what organisms are in my metagenomic sample"** → Assign taxonomic labels to sequencing reads using exact k-mer matching against a reference database for fast initial classification.
- CLI: `kraken2 --db db --paired R1.fastq R2.fastq --report report.txt`

## Basic Classification

```bash
# Classify reads against standard database
kraken2 --db /path/to/kraken2_db \
    --output output.kraken \
    --report report.txt \
    reads.fastq.gz
```

## Paired-End Reads

```bash
kraken2 --db /path/to/kraken2_db \
    --paired \
    --output output.kraken \
    --report report.txt \
    reads_R1.fastq.gz reads_R2.fastq.gz
```

## Common Options

```bash
kraken2 --db /path/to/kraken2_db \
    --threads 8 \                  # CPU threads
    --confidence 0.1 \             # Confidence threshold
    --minimum-base-quality 20 \    # Quality filter
    --output output.kraken \
    --report report.txt \
    --use-names \                  # Add taxon names to output
    --gzip-compressed \            # Input is gzipped
    reads.fastq.gz
```

## Memory-Efficient Mode

```bash
# For systems with limited RAM
kraken2 --db /path/to/kraken2_db \
    --memory-mapping \             # Use disk-based database
    --output output.kraken \
    --report report.txt \
    reads.fastq.gz
```

## Report Only (No Per-Read Output)

```bash
# Save space by not writing per-read classifications
kraken2 --db /path/to/kraken2_db \
    --report report.txt \
    --report-zero-counts \         # Include taxa with 0 counts
    reads.fastq.gz
```

## Classified/Unclassified Output

```bash
# Separate classified and unclassified reads
kraken2 --db /path/to/kraken2_db \
    --classified-out classified#.fq \     # # replaced by 1/2 for PE
    --unclassified-out unclassified#.fq \
    --output output.kraken \
    --report report.txt \
    --paired \
    reads_R1.fastq.gz reads_R2.fastq.gz
```

## Build Custom Database

**Goal:** Create a custom Kraken2 database with specific organism libraries for targeted classification.

**Approach:** Download NCBI taxonomy, add desired library sequences (bacteria, archaea, viral), build the k-mer index, and clean up intermediate files.

```bash
# Download taxonomy
kraken2-build --download-taxonomy --db custom_db

# Download specific libraries
kraken2-build --download-library bacteria --db custom_db
kraken2-build --download-library archaea --db custom_db
kraken2-build --download-library viral --db custom_db

# Build database
kraken2-build --build --db custom_db --threads 8

# Clean up intermediate files
kraken2-build --clean --db custom_db
```

## Add Custom Sequences

```bash
# Add FASTA sequences to library
kraken2-build --add-to-library custom_genomes.fasta --db custom_db

# Then build
kraken2-build --build --db custom_db
```

## Inspect Database

```bash
# View database contents
kraken2-inspect --db /path/to/kraken2_db | head -50
```

## Report Format

```
 17.45  1745    1745    U   0       unclassified
 82.55  8255    48      R   1       root
 82.07  8207    2       R1  131567    cellular organisms
 81.99  8199    132     D   2           Bacteria
 76.23  7623    178     P   1224          Proteobacteria
```

Columns:
1. Percentage of reads
2. Number of reads rooted at taxon
3. Number of reads directly assigned
4. Rank code (U, R, D, P, C, O, F, G, S)
5. NCBI taxon ID
6. Scientific name

## Parse Kraken Output in Python

```python
import pandas as pd

report = pd.read_csv('report.txt', sep='\t', header=None,
                      names=['pct', 'reads_clade', 'reads_taxon', 'rank', 'taxid', 'name'])

report['name'] = report['name'].str.strip()

species = report[report['rank'] == 'S']
species_sorted = species.sort_values('pct', ascending=False)
species_sorted.head(20)
```

## Filter Report by Rank

```bash
# Get only species-level classifications
awk '$4 == "S"' report.txt > species_report.txt

# Get genus level
awk '$4 == "G"' report.txt > genus_report.txt
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| --db | required | Database path |
| --threads | 1 | CPU threads |
| --confidence | 0.0 | Confidence threshold (0-1) |
| --minimum-base-quality | 0 | Phred quality threshold |
| --memory-mapping | false | Use disk-based database |
| --paired | false | Paired-end mode |
| --use-names | false | Include taxon names |
| --report-zero-counts | false | Include 0-count taxa |

## Database Libraries

| Library | Content |
|---------|---------|
| bacteria | RefSeq complete bacterial genomes |
| archaea | RefSeq complete archaeal genomes |
| viral | RefSeq complete viral genomes |
| plasmid | RefSeq plasmid nucleotide sequences |
| human | GRCh38 human genome |
| fungi | RefSeq fungi |
| protozoa | RefSeq protozoa |
| UniVec_Core | Common vector sequences |

## Related Skills

- abundance-estimation - Estimate abundances with Bracken
- metaphlan-profiling - Alternative marker-based profiling
- metagenome-visualization - Visualize results
