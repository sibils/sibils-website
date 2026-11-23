---
description: >-
  The ontologies, thesauri and taxonomies that SIBiLS uses to annotate its collections,
  with the concept_source, type and version of each.
---

# Vocabularies

SIBiLS annotates the documents of all its collections (MEDLINE, PMC, supplementary data, Plazi treatments and Zenodo) with concepts from the vocabularies listed on this page: ontologies, thesauri, taxonomies and lists of names. An annotation links a mention in the text, for example of a species, a gene, a disease or a chemical, to the identifier of a concept in one of these vocabularies.
{ .lead }

The [annotation and vocabularies API](api/annotation/index.md) annotates any text with the same vocabularies and returns the preferred term and synonyms of their concepts. Caucheteur et al. [-@caucheteur2026sibils] describe how the annotations are made and measure their precision vocabulary by vocabulary.

Each annotation names its vocabulary in the `concept_source` field and copies the entity `type` and the `version` of the vocabulary. The tables below give these values for each vocabulary. Documents also carry annotations that do not come from this list: identifiers such as DOIs and PubMed ids (`concept_source` `id_doi` and `id_pubmed`) and research funders (`grant`, identified by their Crossref Funder Registry DOI).

Vocabularies of SIBiLS release <!-- sibils:release -->, as returned by the [terminologies endpoint](https://biodiversitypmc.sibils.org/api/otf/terminologies) on <!-- sibils:date -->. A few names, descriptions and links are corrected on this page where the endpoint has typos or out-of-date text.

<!-- sibils:vocabularies -->
