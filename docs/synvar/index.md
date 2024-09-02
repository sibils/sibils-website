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

Genetic variants are drawing increasing interest regarding their role in pathologies, for designing new drugs or refining treatment efficacy through stratification. However, variant interpretation depends on time-consuming curation tasks. To support variant interpretation efforts and decisions based on the latest evidences, we propose [Variomes](../variomes/index.md) [1], a service performing variant-specific triage of publications. 

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

**Protein variant**: the change is validated on the reference sequence of the canonical isoform, by default, as retrieved by the NextProt API tool [2]. The valid variant is then backtranslated into the possible transcript variants, using the back-translator tool from Mutalyzer [3]. Finally the transcript variant is mapped onto its genomic position (GRCh37 and GRCh38 builds) using VariantValidator [4].

**Transcript variant**: the variant is validated and mapped onto genome position using VariantValidator. It is translated into protein variant using Mutalyzer.

**Genomic variant**: the variant is validated and converted to the transcript variants using VariantValidator, if not intergenic. Transcript variants are translated into protein variants using Mutalyzer. If intergenic, only genomic variant synonyms are generated.

**dbSNP id**: The different genomic variants associated to the dbSNP [5] id are retrieved through the NCBI eutils services. The conversion and translation procedure from genomic variant is similar to the one described above.

**COSMIC id**: The transcript variant corresponding to the COSMIC id is retrieved through the downloadable COSMIC data [6]. The genomic mapping and translation of transcript variant is similar to the one described above.

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

## References

1. Pasche, E., Mottaz, A., Caucheteur, D., Gobeill, J., Michel, P.A., Ruch. P. (2021). Variomes: a high recall search engine to support the curation of genomic variants. bioRxiv : the preprint server for biology, 2021.05.29.446224. <https://doi.org/10.1101/2021.05.29.446224>
1. Zahn-Zabal, M., Michel, P. A., Gateau, A., Nikitin, F., Schaeffer, M., Audot, E., Gaudet, P., Duek, P. D., Teixeira, D., Rech de Laval, V., Samarasinghe, K., Bairoch, A., & Lane, L. (2020). The neXtProt knowledgebase in 2020: data, tools and usability improvements. Nucleic acids research, 48(D1), D328–D334. <https://doi.org/10.1093/nar/gkz995>
1. den Dunnen J. T. (2016). Sequence Variant Descriptions: HGVS Nomenclature and Mutalyzer. Current protocols in human genetics, 90, 7.13.1–7.13.19. <https://doi.org/10.1002/cphg.2>
1. Freeman, P. J., Hart, R. K., Gretton, L. J., Brookes, A. J., & Dalgleish, R. (2018). VariantValidator: Accurate validation, mapping, and formatting of sequence variation descriptions. Human mutation, 39(1), 61–68. <https://doi.org/10.1002/humu.23348>
1. Smigielski, E. M., Sirotkin, K., Ward, M., & Sherry, S. T. (2000). dbSNP: a database of single nucleotide polymorphisms. Nucleic acids research, 28(1), 352–355. <https://doi.org/10.1093/nar/28.1.352>
1. Tate, J. G., Bamford, S., Jubb, H. C., Sondka, Z., Beare, D. M., Bindal, N., Boutselakis, H., Cole, C. G., Creatore, C., Dawson, E., Fish, P., Harsha, B., Hathaway, C., Jupe, S. C., Kok, C. Y., Noble, K., Ponting, L., Ramshaw, C. C., Rye, C. E., Speedy, H. E., … Forbes, S. A. (2019). COSMIC: the Catalogue Of Somatic Mutations In Cancer. Nucleic acids research, 47(D1), D941–D947. <https://doi.org/10.1093/nar/gky1015>
