# tcga-bulk-data-preprocessing-with-omicverse

> Guide Claude through ingesting TCGA sample sheets, expression archives, and clinical carts into omicverse, initialising survival metadata, and exporting annotated AnnData files.

# TCGA bulk data preprocessing with omicverse

## Overview
Follow this skill to recreate the preprocessing routine from [`t_tcga.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_tcga.ipynb). It automates loading TCGA downloads, generating raw/normalised matrices, initialising metadata, and running survival analyses through `ov.bulk.pyTCGA`.

## Instructions
1. **Gather required downloads**
   - Confirm the user has:
     - `gdc_sample_sheet.<date>.tsv` from the TCGA Sample Sheet export.
     - The decompressed `gdc_download_xxxxx` directory containing expression archives.
     - The `clinical.cart.<date>` directory with clinical XML/JSON files.
   - Mention that sample data are available under [`omicverse_guide/docs/Tutorials-bulk/data/TCGA_OV/`](../../omicverse_guide/docs/Tutorials-bulk/data/TCGA_OV/).
2. **Initialise the TCGA helper**
   - Import `omicverse as ov` (and `scanpy as sc` if plotting) then call `ov.plot_set()`.
   - Instantiate `aml_tcga = ov.bulk.pyTCGA(sample_sheet_path, download_dir, clinical_dir)`.
   - Run `aml_tcga.adata_init()` to build the AnnData object with raw counts, FPKM, and TPM layers.
3. **Persist the dataset**
   - Encourage saving the initial AnnData: `aml_tcga.adata.write_h5ad('data/TCGA_OV/ov_tcga_raw.h5ad', compression='gzip')`.
   - When reloading, reconstruct the class with the same paths and call `aml_tcga.adata_read(<path>)`.
4. **Initialise metadata and clinical information**
   - Populate sample metadata using `aml_tcga.adata_meta_init()` to convert gene IDs to symbols and attach patient info.
   - Add survival attributes via `aml_tcga.survial_init()` (note the intentional spelling in the API).
5. **Perform survival analyses**
   - Plot gene-level survival curves with `aml_tcga.survival_analysis('GENE', layer='deseq_normalize', plot=True)`.
   - To process all genes, call `aml_tcga.survial_analysis_all()`; warn that it may take time.
6. **Export results**
   - Save enriched metadata to a new AnnData file (`aml_tcga.adata.write_h5ad('.../ov_tcga_survial_all.h5ad', compression='gzip')`).
   - Suggest exporting summary tables (e.g., survival statistics) if users need to share outputs outside Python.
7. **Troubleshooting tips**
   - Ensure TCGA archives are fully extracted; missing XML/TSV files trigger parsing errors.
   - The helper expects matching case IDs between the sample sheet and expression files—direct users to re-download if IDs do not
 align.
   - Survival plots require clinical dates; if absent, instruct users to check the `clinical_cart` contents.

## Examples
- "Read my TCGA OV download, initialise metadata, and plot MYC survival curves using DESeq-normalised counts."
- "Reload a saved AnnData file, attach survival annotations, and export the updated `.h5ad`."
- "Run survival analysis for all genes and store the enriched dataset."

## References
- Tutorial notebook: [`t_tcga.ipynb`](../../omicverse_guide/docs/Tutorials-bulk/t_tcga.ipynb)
- Sample dataset: [`data/TCGA_OV/`](../../omicverse_guide/docs/Tutorials-bulk/data/TCGA_OV/)
- Quick copy/paste commands: [`reference.md`](reference.md)
