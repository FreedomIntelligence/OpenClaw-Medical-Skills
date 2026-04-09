# bio-workflows-outbreak-pipeline

> End-to-end outbreak investigation from pathogen isolates to transmission networks. Orchestrates MLST typing, AMR surveillance, phylodynamic dating, and transmission inference with TransPhylo. Use when investigating disease outbreaks or tracking pathogen transmission chains.

**Available tools:** Read, Bash

# Outbreak Pipeline

Complete workflow for genomic epidemiology: from pathogen isolates to transmission networks and outbreak characterization.

## Workflow Overview

```
Pathogen Isolate Genomes (FASTA/FASTQ)
        |
        v
   +---------+---------+
   |                   |
   v                   v
[1a. MLST Typing]   [1b. AMR Detection]  <-- Parallel execution
   |                   |
   +--------+----------+
            |
            v
[2. Core Genome Alignment] --> snippy / ParSNP
            |
            v
[3. Phylodynamics] --> TreeTime / BEAST2
            |
            v
[4. Transmission Inference] --> TransPhylo
            |
            v
Transmission Network + R0 Estimates + Timeline
```

## Prerequisites

```bash
conda install -c bioconda mlst abricate snippy iqtree fasttree

pip install treetime transphylo biopython pandas matplotlib

# R packages for TransPhylo
Rscript -e "install.packages('TransPhylo')"
```

## Primary Path: Bacterial Outbreak Investigation

### Step 1a: MLST Typing (Parallel)

```bash
#!/bin/bash
ISOLATES="isolate1.fasta isolate2.fasta isolate3.fasta"
OUTDIR="outbreak_results"
mkdir -p ${OUTDIR}/{mlst,amr,alignment,phylo,transmission}

# Run MLST on all isolates
echo "=== MLST Typing ==="
for fasta in $ISOLATES; do
    sample=$(basename $fasta .fasta)
    mlst $fasta > ${OUTDIR}/mlst/${sample}.mlst.txt
done

# Combine results
cat ${OUTDIR}/mlst/*.mlst.txt > ${OUTDIR}/mlst/all_mlst.tsv
echo "MLST complete: ${OUTDIR}/mlst/all_mlst.tsv"
```

### Step 1b: AMR Detection (Parallel)

```bash
echo "=== AMR Detection ==="
for fasta in $ISOLATES; do
    sample=$(basename $fasta .fasta)
    abricate --db ncbi $fasta > ${OUTDIR}/amr/${sample}.amr.tsv
done

# Summary matrix
abricate --summary ${OUTDIR}/amr/*.amr.tsv > ${OUTDIR}/amr/amr_summary.tsv
echo "AMR summary: ${OUTDIR}/amr/amr_summary.tsv"
```

### Step 2: Core Genome Alignment

```bash
echo "=== Core Genome Alignment ==="
REFERENCE="reference.gbk"  # Reference genome in GenBank format

# Run snippy for each isolate
for fasta in $ISOLATES; do
    sample=$(basename $fasta .fasta)
    snippy --outdir ${OUTDIR}/alignment/snippy_${sample} \
           --ref $REFERENCE \
           --ctgs $fasta \
           --cpus 8
done

# Core SNP alignment
snippy-core --ref $REFERENCE ${OUTDIR}/alignment/snippy_*

# Clean alignment (remove recombination, optional)
# run_gubbins.py core.full.aln

mv core.* ${OUTDIR}/alignment/
echo "Core alignment: ${OUTDIR}/alignment/core.aln"
```

### Step 3: Phylodynamics with TreeTime

```python
import subprocess
from Bio import Phylo, AlignIO
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

outdir = Path('outbreak_results')

# Build ML tree
subprocess.run([
    'iqtree2', '-s', str(outdir / 'alignment/core.aln'),
    '-m', 'GTR+G', '-bb', '1000', '-nt', 'AUTO',
    '--prefix', str(outdir / 'phylo/outbreak')
], check=True)

# Prepare metadata with dates
# Format: name\tdate (YYYY-MM-DD or decimal year)
metadata = pd.DataFrame({
    'name': ['isolate1', 'isolate2', 'isolate3', 'isolate4', 'isolate5'],
    'date': ['2024-01-15', '2024-01-22', '2024-02-01', '2024-02-10', '2024-02-15']
})
metadata.to_csv(outdir / 'phylo/metadata.tsv', sep='\t', index=False)

# Run TreeTime
subprocess.run([
    'treetime',
    '--tree', str(outdir / 'phylo/outbreak.treefile'),
    '--aln', str(outdir / 'alignment/core.aln'),
    '--dates', str(outdir / 'phylo/metadata.tsv'),
    '--outdir', str(outdir / 'phylo/treetime_output'),
    '--coalescent', 'skyline',
    '--clock-filter', '3'  # Remove outliers >3 IQR from clock
], check=True)

# Check temporal signal
# Good signal: R2 > 0.5, clock rate ~1e-6 to 1e-7 subs/site/year for bacteria
print('TreeTime output:', outdir / 'phylo/treetime_output')
```

### Step 4: Transmission Inference with TransPhylo

```r
library(TransPhylo)
library(ape)

# Load dated tree from TreeTime
tree <- read.nexus("outbreak_results/phylo/treetime_output/timetree.nexus")

# Set parameters
# dateT: date when sampling stopped
# w.shape, w.scale: generation time distribution (Gamma)
# For many bacteria: mean ~14 days, shape=2, scale=7
dateT <- 2024.2  # Decimal year when sampling ended
w_shape <- 2     # Generation time shape (Gamma)
w_scale <- 7/365 # Generation time scale in years (~7 days mean)

# Run TransPhylo
res <- inferTTree(tree, dateT = dateT,
                   w.shape = w_shape, w.scale = w_scale,
                   mcmcIterations = 10000,
                   startNeg = 1, startPi = 0.5)

# Extract results
ttree <- extractTTree(res)

# Transmission network
medTTree <- medTTree(res)

# Plot transmission tree
pdf("outbreak_results/transmission/transmission_tree.pdf", width=10, height=8)
plotTTree(medTTree)
dev.off()

# Who infected whom matrix
wiw <- computeMatWIW(res)
write.csv(wiw, "outbreak_results/transmission/who_infected_whom.csv")

# R0 estimate
R0 <- getOffspringMulti(res)
cat("R0 estimate:", mean(R0), "(95% CI:", quantile(R0, 0.025), "-", quantile(R0, 0.975), ")\n")
```

### Python Alternative: TransPhylo via rpy2

```python
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import pandas as pd
from pathlib import Path

pandas2ri.activate()

transphylo = importr('TransPhylo')
ape = importr('ape')

outdir = Path('outbreak_results')

tree = ape.read_nexus(str(outdir / 'phylo/treetime_output/timetree.nexus'))

date_t = 2024.2
w_shape = 2
w_scale = 7/365

res = transphylo.inferTTree(tree, dateT=date_t, w_shape=w_shape, w_scale=w_scale,
                             mcmcIterations=10000, startNeg=1, startPi=0.5)

# Extract transmission pairs
med_tree = transphylo.medTTree(res)

ro.r(f'''
pdf("{outdir}/transmission/transmission_tree.pdf", width=10, height=8)
plotTTree(medTTree({res}))
dev.off()
''')

print(f'Transmission tree saved to {outdir}/transmission/')
```

## Visualization: Outbreak Timeline

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

metadata = pd.read_csv('outbreak_results/phylo/metadata.tsv', sep='\t')
metadata['date'] = pd.to_datetime(metadata['date'])

mlst = pd.read_csv('outbreak_results/mlst/all_mlst.tsv', sep='\t', header=None,
                    names=['file', 'scheme', 'ST'] + [f'locus{i}' for i in range(7)])
mlst['sample'] = mlst['file'].apply(lambda x: x.split('/')[-1].replace('.fasta', ''))

amr = pd.read_csv('outbreak_results/amr/amr_summary.tsv', sep='\t')

# Merge data
combined = metadata.merge(mlst[['sample', 'ST']], left_on='name', right_on='sample')

fig, ax = plt.subplots(figsize=(12, 6))

colors = {'ST11': 'red', 'ST258': 'blue', 'ST307': 'green'}
for st in combined['ST'].unique():
    subset = combined[combined['ST'] == st]
    ax.scatter(subset['date'], [1]*len(subset), label=f'ST{st}',
               s=100, c=colors.get(f'ST{st}', 'gray'), alpha=0.7)

ax.set_xlabel('Date')
ax.set_ylabel('')
ax.set_title('Outbreak Timeline by Sequence Type')
ax.legend()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('outbreak_results/outbreak_timeline.pdf')
```

## Parameter Recommendations

| Step | Parameter | Value | Rationale |
|------|-----------|-------|-----------|
| snippy | --mincov | 10 | Minimum coverage for variant call |
| IQ-TREE | -m | GTR+G | General time-reversible model |
| TreeTime | --clock-filter | 3 | Remove temporal outliers >3 IQR |
| TransPhylo | w.shape, w.scale | 2, 7/365 | Generation time ~7 days for many bacteria |
| TransPhylo | mcmcIterations | 10000+ | Ensure convergence |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| No MLST match | Novel ST or poor assembly | Check assembly quality, submit novel ST |
| Poor temporal signal | Insufficient sampling, recombination | Remove recombination with Gubbins, check dates |
| TreeTime clock-filter removes many | Wrong root, contamination | Re-root tree, check sample quality |
| TransPhylo non-convergence | Wrong generation time | Adjust w.shape/w.scale, increase iterations |
| Missing AMR genes | Database mismatch | Try multiple databases (ncbi, card, resfinder) |

## Output Files

| File | Description |
|------|-------------|
| `mlst/all_mlst.tsv` | Sequence types for all isolates |
| `amr/amr_summary.tsv` | AMR gene presence/absence matrix |
| `alignment/core.aln` | Core genome SNP alignment |
| `phylo/outbreak.treefile` | ML phylogenetic tree |
| `phylo/treetime_output/` | Dated tree and molecular clock |
| `transmission/transmission_tree.pdf` | Inferred transmission network |
| `transmission/who_infected_whom.csv` | Transmission probability matrix |

## Related Skills

- epidemiological-genomics/pathogen-typing - MLST and cgMLST details
- epidemiological-genomics/amr-surveillance - AMRFinderPlus, ResFinder
- epidemiological-genomics/phylodynamics - TreeTime, BEAST2 parameters
- epidemiological-genomics/transmission-inference - TransPhylo configuration
- epidemiological-genomics/variant-surveillance - Nextclade for viral outbreaks
- phylogenetics/modern-tree-inference - IQ-TREE2 model selection
