---
description: >-
  BiotXplorer searches the literature for pairs of taxa that could have a biotic
  relationship, with the passages that support each interaction.
---

# BiotXplorer

BiotXplorer, the biotic interactions browser, searches the literature for pairs of taxa that could have a biotic relationship, with the passages that support each interaction.
{ .lead }

[Open BiotXplorer](https://biotxplorer.sibils.org/){ .btn .btn-primary }
[API documentation](https://biotxplorer.sibils.org/api/){ .btn }

<div class="facts" markdown>

Web application
:   [biotxplorer.sibils.org](https://biotxplorer.sibils.org/)

API
:   REST API at `https://biotxplorer.sibils.org/api`, interactive documentation at [biotxplorer.sibils.org/api/](https://biotxplorer.sibils.org/api/)

Collections
:   MEDLINE, PMC+, supplementary data, Plazi treatments, Zenodo

Output
:   Pairs of taxa with an interaction type from the Relation Ontology, each with its supporting passages and documents; export as JSON or CSV in the web application

Citation
:   Ruch et al. [-@ruch2024biotxplorer], with the SIBiLS papers Gobeill et al. [-@10_1093_nar_gkaa328] and Caucheteur et al. [-@caucheteur2026sibils]

</div>

## How it works

A search takes up to three terms: a first taxon, a second taxon and an interaction (for example pangolins, cats and host). Pairs of taxa are extracted when they appear in the same sentence as a biotic-interaction term from the Relation Ontology; they are then aggregated over the documents, and queries are expanded through the taxonomic hierarchy [@ruch2024biotxplorer]. The web application shows, for each collection, how many interactions were extracted. Taxa are normalized with Open Tree of Life (OTT) and NCBI Taxonomy identifiers (see [Vocabularies](../vocabularies.md)).

## Video

A presentation of BiotXplorer (3 min 41 s, MP4, 60.5 MB).

<div class="video"><video controls preload="none" poster="../assets/posters/biotxplorer.jpg" aria-label="BiotXplorer video"><source src="https://candy.text-analytics.ch/biotxplorer.mp4" type="video/mp4"><a href="https://candy.text-analytics.ch/biotxplorer.mp4">Download the BiotXplorer video</a> (MP4, 60.5 MB).</video></div>
