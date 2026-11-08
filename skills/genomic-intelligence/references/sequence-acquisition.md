# Sequence Acquisition (Ensembl)

Turn a **gene symbol** or a **genomic region** into reference sequence so users
don't have to bring a FASTA. Ensembl REST (`rest.ensembl.org`) is **public — no
key**; only the *prediction* step needs a key (and only over REST).

On MCP, the acquisition tools (`fetch_ensembl_sequence`, `fetch_region`,
`fetch_gene_for_expression`, `find_genes`) do this for you and return a handle.
Over REST, query Ensembl yourself, then feed the sequence to `/v1/tasks/...`.

## Modes

- **Full gene body** (any task except expression) — resolve the gene, fetch its
  sequence.
- **Coordinate range** — fetch `/sequence/region/{species}/{region}`.
- **TSS-centred, gene-sense sequence sized from the model list, plus
  `tss_index`** (expression only) — see below.

## TSS-centring (why expression is special)

Expression reads the sequence around the **transcription start site (TSS)**,
and how far it reads depends on the model. Every expression model accepts at
least 9,198 bp with the TSS at least 4,599 bp from each end, plus `tss_index`
(the 0-based TSS offset into the whitespace-stripped sequence); that is a
floor, not a target. A long-context model reads much further, and scored on
the floor alone it sees less than it was trained on. The server cuts the
selected model's slice around `tss_index` and ignores the rest. You must know
where the TSS is; the endpoint never discovers it, never pads, and never
reverse-complements. You cannot reliably build this from gene-body coordinates:
the annotated gene start/end can sit far from the real TSS (HBB's gene end is
2,324 bp from its canonical TSS; ACTB's is 33,301 bp). Mis-centring tanks the
prediction.

The correct construction, with nothing hard-coded:

1. **Size the flank from the model list.** `GET /v1/tasks/expression/models`
   (public, no key). F = the largest `bio_spec.recommended_flank_bp` among the
   listed models, never below 4,599, and with 2F within `request_max_bp`. One
   fetch then serves every listed model. Do not pin F or a model id: defaults
   change and longer-context models arrive. Use the model the user named, else
   `default_model`, and send the same one on every call of a run.
2. **Find the TSS.** Resolve the gene's **canonical transcript** (Ensembl
   `GET /lookup/symbol/{species}/{symbol}?expand=1`, the transcript with
   `is_canonical`); the TSS is the transcript start on the + strand and its end
   on the − strand.
3. **Fetch gene-sense, TSS at offset F.** F bp before the TSS and F bp from the
   TSS onward = 2F bp. In Ensembl's 1-based inclusive coordinates: + strand
   `{chr}:{tss-F}..{tss+F-1}:1`; − strand `{chr}:{tss-F+1}..{tss+F}:-1`
   (Ensembl reverse-complements for `-1`). Using the + strand interval for a −
   strand gene puts the TSS at F − 1: still in range, so it scores a window
   shifted by one base with no error. Check the length is exactly 2F.
4. **Send `tss_index = F`**, and the model from step 1.

Near a chromosome end, use the largest symmetric F that fits, down to 4,599,
and say the flank was shortened. On MCP, `fetch_gene_for_expression(gene=...)`
does all of this and the handle records the offset, so `predict_expression`
needs no `tss_index`. Because it needs a transcript, it works from a **gene**,
not a bare region.

If you submit some other locus with `tss_index`, the offset must be counted
on the **stripped nucleotide string** (no newlines, no FASTA header) and satisfy
`4599 ≤ tss_index ≤ len(sequence) − 4599`. An offset that is out of range 422s;
one that is merely *wrong* but in range silently scores the wrong window, so
check `meta.task_specific_counts.scored_window` on the response.

## Species & assembly

- **Default: human, GRCh38.**
- Non-human: use the Ensembl **production name** — lowercase, underscored:
  `mus_musculus`, `drosophila_melanogaster`, `saccharomyces_cerevisiae`. `mouse`
  / `Drosophila` will be rejected.
- The **enhancer** default (DeepSTARR) is *Drosophila* — match species to model
  (see `tasks.md`).

## When to skip acquisition

Supply sequence directly when it is **not** reference genome — variant-bearing,
edited, synthetic, or from a non-Ensembl assembly. Acquisition only returns
reference sequence for the requested coordinates.

## Limits

Bounded by the task's own cap (500,000 bp for every task) and its **floor**:
promoter 300, splice 100, enhancer 50, chromatin 200, annotation 1,000,
expression 9,198 bp. Clearing the floor only gets the request accepted — fetch at
least the model's `context_window_bp` (promoter 2,000, splice 15,000, enhancer
249, chromatin 1,000) if you want the score to reflect real sequence rather than
padding, and for expression `recommended_flank_bp` on each side of the TSS. Ensembl enforces its own per-request size limits; fetch very large
ranges in pieces.
