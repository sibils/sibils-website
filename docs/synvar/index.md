---
description: >-
  SynVar generates synonyms and normalized descriptions of a human genetic variant at the
  genome, transcript and protein levels, to find it in the literature.
---

# SynVar

SynVar generates synonyms and normalized descriptions of a human genetic variant, at the genome, transcript and protein levels, to find the variant in the literature.
{ .lead }

[Open SynVar](https://synvar.sibils.org/){ .btn .btn-primary }
[API documentation](../api/synvar/index.md){ .btn }

<div class="facts" markdown>

Web application
:   [synvar.sibils.org](https://synvar.sibils.org/)

API
:   REST API at `https://synvar.sibils.org/api`, see the [SynVar API](../api/synvar/index.md), the [usage guide](https://synvar.sibils.org/resources/info.html) and the [interactive API](https://synvar.sibils.org/docs)

Resources used
:   UniProt, VariantValidator, Mutalyzer, NCBI E-utilities (dbSNP), ClinGen Allele Registry, GA4GH VRS

Output
:   XML or JSON; GA4GH VRS through the API

Citation
:   Mottaz et al. [-@mottaz2022synvar], with the Variomes paper Pasche et al. [-@pasche2022variomes] and the SIBiLS papers Gobeill et al. [-@10_1093_nar_gkaa328] and Caucheteur et al. [-@caucheteur2026sibils]

</div>

## What it does

Genetic variants are studied for their role in diseases, for designing new drugs and for refining treatments through patient stratification, but interpreting them requires time-consuming curation. [Variomes](../variomes/index.md) [@pasche2022variomes] supports this curation by ranking the publications about a variant.

SynVar was developed to help Variomes find more of these publications. It generates the synonyms of a variant and normalizes it, a task with three difficulties:

* Variants can be represented at different levels (genomic, transcript or protein) with a combinatorial (many-to-many) relationship between them.

* Variant descriptions depend on a reference sequence on which the variation is described, to avoid positional ambiguity.

* The majority of variants mentioned in the literature do not follow a standard nomenclature.

While many databases of polymorphisms and somatic variants exist, such as ClinVar, COSMIC or dbSNP, using them as terminologies has several drawbacks:

* Depending on the database, variants are mapped on different levels, hindering a linear relationship between them, and some are position- but not change-specific, reducing specificity.

* Dependency on databases prevents retrieval of newly described variants in the literature.

* Databases do not provide the non-standard expressions found in the literature.

For a given variant, including variants not yet described in any database, SynVar generates its descriptions at the genome, transcript and protein levels, in HGVS format and in the non-standard forms frequently found in the literature. It accepts a variant at any of these levels. In the published evaluation, expansion with SynVar raised the recall of a variant curation-support search service by 133.8% while precision stayed at 93% [@mottaz2022synvar].

SynVar has two modes. Expansion mode (the default) returns the variant descriptions and literature-oriented synonyms described below. Normalization mode (the *Normalisation only* option, `mode=normalize` in the API) returns normalized representations instead: HGVS, SPDI and VCF, the dbSNP and ClinGen identifiers, and GA4GH VRS representations, when available.

## How it works

### Input types

* **Protein variant**: the change is validated on the reference protein sequence, by default that of the canonical isoform; gene, protein, transcript and isoform cross-references come from [UniProt](https://www.uniprot.org/). Substitutions are back-translated into the possible transcript variants with [Mutalyzer](https://mutalyzer.nl/) [@den2016sequence], and insertions and deletions with SynVar's own sequence-based rules. Finally the transcript variants are mapped onto their genomic position (GRCh37 and GRCh38 builds) using [VariantValidator](https://www.variantvalidator.org/) [@freeman2018variantvalidator].

* **Transcript variant**: the variant is validated, mapped onto its genomic position and translated into the protein variant using VariantValidator. Without an explicit transcript, candidate transcripts are resolved from the gene.

* **Genomic variant**: the variant is validated and mapped to the transcript and protein variants using VariantValidator, where transcript mappings are available. For an intergenic variant, only genomic variant synonyms are generated.

* **dbSNP id**: the genomic variants associated with the dbSNP [@smigielski2000dbsnp] id are retrieved through the NCBI E-utilities. The conversion and translation procedure is then the same as for a genomic variant.

* **ClinGen id**: the genomic variant corresponding to a ClinGen allele identifier (CA ID, e.g. CA123643) is retrieved from the [ClinGen Allele Registry](https://reg.clinicalgenome.org/). The procedure is then the same as for a genomic variant.

* **Any**: SynVar recognizes the level of each variant mention. Where no level is explicit, it tries protein, transcript, genome, dbSNP and ClinGen, in that order, until a GRCh38 mapping is found.

COSMIC identifiers are no longer accepted.

### Output

Results are returned as a list of genomic variants (unique position and change), along with their corresponding transcript and protein variants, grouped by genes and isoforms. The output is in XML (default) or JSON format. The main elements are the following:

* **synonym**: Synonyms of gene and protein names.
* **hgvs**: Variant description in the standard HGVS format. The main HGVS description can be used as a unique identifier. Other HGVS descriptions are given for each level of description, using the NCBI reference sequences.
* **syntactic-variation**: Variant expressions as encountered in the literature.
* **rsid, caid**: dbSNP and ClinGen identifiers of the variant, when available.

## Using SynVar

SynVar handles human variants only (Homo sapiens, NCBI Taxonomy 9606).

### Fields

* **Gene/Chromosome**: Gene name or chromosome number/name (e.g. BRAF, JAK2, 9, X). The field can be empty if the gene is given in the *Variation* field, or if a complete HGVS expression, a dbSNP id or a ClinGen id is searched.

* **Variation** (required): Variant in a format such as V600E (amino acid sequence) or 1799T>A (DNA sequence), an HGVS expression with its reference sequence (e.g. NM_004333.6:c.1799T>A), a dbSNP id (e.g. rs113488022) or a ClinGen id (e.g. CA123643). The field also accepts a gene with its variant (e.g. BRAF V600E) or a sentence that mentions several variants.

* **Level**: Level of the provided variant description: *Protein*, *Transcript/cDNA*, *Genome*, *dbSNP*, *ClinGen* or *Any*.

* **Output format**: *XML* or *JSON*.

### Advanced options

* **Include additional isoforms**: also return the other mapped isoforms (MANE Select and UniProt canonical isoforms are included by default, when available).
* **Require genome mapping**: require a successful mapping onto the genome (without this option, unmapped variants can be returned).
* **Normalisation only**: return normalized representations instead of literature synonyms (see [What it does](#what-it-does)).
* **Start Met ±1 shift**: add protein synonyms numbered without the initiator methionine.
* **Include insertion synonyms for duplications**: add insertion-equivalent synonyms for duplications.
* **Additional shifted synonyms**: add shifted deletion and duplication synonyms in repetitive sequence.

The [usage guide](https://synvar.sibils.org/resources/info.html) on the SynVar site describes each option and the supported notations in detail.

## API

See the [SynVar API](../api/synvar/index.md) page and the [usage guide](https://synvar.sibils.org/resources/info.html). For example, [`https://synvar.sibils.org/api?ref=BRAF&variant=V600E&level=protein&mode=normalize&format=json`](https://synvar.sibils.org/api?ref=BRAF&variant=V600E&level=protein&mode=normalize&format=json) returns the normalized descriptions of BRAF V600E.
