---
description: >-
  The ontologies, thesauri and taxonomies that SIBiLS uses to annotate its collections,
  with the concept_source, type and version of each.
---

# Vocabularies

SIBiLS annotates the documents of all its collections (MEDLINE, PMC, supplementary data, Plazi treatments and Zenodo) with concepts from the vocabularies listed on this page: ontologies, thesauri, taxonomies and lists of names. An annotation links a mention in the text, for example of a species, a gene, a disease or a chemical, to the identifier of a concept in one of these vocabularies.
{ .lead }

Caucheteur et al. [-@caucheteur2026sibils] describe how the annotations are made and measure their precision vocabulary by vocabulary.

The COVoc vocabularies are described by Caucheteur et al. [-@caucheteur2023covoc].

The <!-- sibils:terminology-browser --> is a web application to browse and search these vocabularies. It lists the concepts of each vocabulary, as a tree for some of them, such as MeSH, the Gene Ontology and Uberon. For each concept it shows the preferred term, the synonyms and the number of documents annotated with it in each collection, clinical trials included. Its search finds concepts by name, synonym or identifier. It is updated separately from this page, so its versions can differ from the tables below. <span class="vocab-browse">The "browse concepts" link in each row opens the vocabulary there.</span>

Each annotation names its vocabulary in the `concept_source` field and copies the entity `type` and the `version` of the vocabulary. The tables below give these values for each vocabulary. Documents also carry annotations that do not come from this list: identifiers such as DOIs and PubMed ids (`concept_source` `id_doi` and `id_pubmed`) and research funders (`grant`, identified by their Crossref Funder Registry DOI).

Vocabularies of SIBiLS release <!-- sibils:release -->, as returned by the SIBiLS API on <!-- sibils:date -->. A few names, descriptions and links are corrected on this page where the API has typos or out-of-date text.

<!-- sibils:vocabularies -->
