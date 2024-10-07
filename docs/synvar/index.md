---
hide:
  - navigation
  - toc
---

# SynVar

<p style="text-align: center" markdown>
  [SynVar](https://synvar.sibils.org/){ .md-button .md-button--primary .sibils-service }
</p>

## Background

Genetic variants are drawing increasing interest regarding their role in pathologies, for designing new drugs or refining treatment efficacy through stratification. However, variant interpretation depends on time-consuming curation tasks. To support variant interpretation efforts and decisions based on the latest evidences, we propose [Variomes](../variomes/index.md) [@pasche2021variomes], a service performing variant-specific triage of publications.

To increase the comprehensiveness of Variomes, we developed SynVar. This tool enables the generation of synonyms and normalization of variants. This task faces different challenges: 

* Variants can be represented at different levels - genomic, transcript or protein - with a combinatorial (many-to-many) relationship between them.

* Variant descriptions depend on a reference sequence on which the variation is described, to avoid positional ambiguity.

* The majority of variants mentioned in the literature do not follow a standard nomenclature.

While many databases of polymorphisms and somatic variants exist, such as ClinVar, COSMIC or dbSNP, using them as terminologies has several drawbacks: 

* Depending on the database, variants are mapped on different levels, hindering a linear relationship between them, and some are position- but not change-specific, reducing specificity.

* Dependency to databases prevents retrieval of newly described variants in literature.

* It doesn't provide non-standard expressions as found in the literature.

## Description

To enable a smooth and effective retrieval of variants in the literature, we developed a synonym generation tool that enables to generate for a given SNP – including variants not described in existing databases – its corresponding description at the genome, transcript and protein level, in the HGVS format as well as in many non standard – yet frequently used – descriptions found in the literature. It is adapted for variant expansion and normalization from any description level. 

## Workflow

### Use-cases

* **Protein variant**: the change is   validated on the reference sequence of the canonical isoform, by default, as retrieved by the [NextProt API tool](https://api.nextprot.org/) [@zahn2020nextprot]. The valid variant is then backtranslated into the possible transcript variants, using the back-translator tool from [Mutalyzer](https://mutalyzer.nl/) [@den2016sequence]. Finally the transcript variant is mapped onto its genomic position (GRCh37 and GRCh38 builds) using [VariantValidator](https://rest.variantvalidator.org/) [@freeman2018variantvalidator].

* **Transcript variant**: the variant is validated and mapped onto genome position using VariantValidator. It is translated into protein variant using Mutalyzer.

* **Genomic variant**: the variant is validated and converted to the transcript variants using VariantValidator, if not intergenic. Transcript variants are translated into protein variants using Mutalyzer. If intergenic, only genomic variant synonyms are generated.

* **dbSNP id**: The different genomic variants associated to the dbSNP [@smigielski2000dbsnp] id are retrieved through the NCBI eutils services. The conversion and translation procedure from genomic variant is similar to the one described above.

* **COSMIC id**: The transcript variant corresponding to the COSMIC id is retrieved through the downloadable COSMIC data [@tate2019cosmic]. The genomic mapping and translation of transcript variant is similar to the one described above.

### Output

Results are returned as a list of genomic variants (unique position and change), along with their corresponding transcript and protein variants, grouped by genes and isoforms. The output is in XML format. The main elements are the following:

* **synonym**: Synonyms of gene and protein names.
* **hgvs**: Variant description in the standard HGVS format. The main HGVS description can be used as a unique identifier. Other HGVS are given for each level of description using the NCBI reference sequences.
* **syntactic-variation**: Variant expressions as encountered in the literature.

## Search interface

### Fields

* **Gene/Chromosome**: Gene name or chromosome number/name (e.g. JAK2, BRAF, 9, X, MT). The field can be empty if a dbSNP or COSMIC id is searched.

* **Variant**: Variant in the following format: V600E (for amino acid sequence) or 1799T>A (for DNA sequence) or a dbSNP id (e.g. rs113488022) or COSMIC id (e.g. COSM476).

* **Level**: Level of the provided variant description (*protein, transcript, genome, dbsnp or cosmic*).

## API

See [the dedicated page](../api/synvar/index.md)
