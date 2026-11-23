---
description: >-
  BiodiversityPMC searches MEDLINE, PMC+, supplementary data, Plazi treatments and
  Zenodo, for life and health scientists and biodiversity researchers.
---

# BiodiversityPMC

BiodiversityPMC is a search engine over the SIBiLS literature collections, built for life and health scientists and for researchers in biodiversity and related sciences.
{ .lead }

[Open BiodiversityPMC](https://biodiversitypmc.sibils.org/){ .btn .btn-primary }
[API documentation](../api/biodiversitypmc/index.md){ .btn }

<div class="facts" markdown>

Web application
:   [biodiversitypmc.sibils.org](https://biodiversitypmc.sibils.org/)

API
:   REST API at `https://biodiversitypmc.sibils.org/api`, see the [BiodiversityPMC API](../api/biodiversitypmc/index.md)

Collections
:   MEDLINE, PMC+, supplementary data, Plazi treatments, Zenodo (BLR and other communities); sizes on the [Collections](../collections/sibils_collections.md) page

Output
:   Ranked lists of documents; export as JSON or CSV in the web application, JSON or BioC through the API

Reference
:   Pasche et al., TDWG [-@pasche2023towards] [-@pasche2023sibils]

</div>

## What it does

BiodiversityPMC builds on the [SIBiLS](../index.md) copies of MEDLINE citations and PubMed Central (PMC) full-text articles (the PMC open-access subset and the author manuscripts) from the US National Library of Medicine. It adds articles that are not in PMC, from publishers such as Pensoft; more than a million taxonomic treatments from [Plazi](https://plazi.org/); the text extracted from PMC supplementary files; and documents harvested from Zenodo communities such as the [Biodiversity Literature Repository](https://zenodo.org/communities/biosyslit/) (BLR). The [Collections](../collections/sibils_collections.md) page describes each collection and gives its current size.

With these additions it covers more disciplines than PMC, such as ecology, environmental sciences and taxonomy, and serves taxonomists, ecologists and anyone who studies or monitors biodiversity. Its authors present it as a step towards a One Health library [@pasche2023sibils].

BiodiversityPMC was soft-launched in summer 2023 and officially announced at the BiCIKL General Assembly in Cambridge (UK) on 14 February 2024 [@eurekalert2024biodiversitypmc].

## Using BiodiversityPMC

The [Documentation](https://biodiversitypmc.sibils.org/docs) page of the web application describes the query syntax and the fields that can be searched in each collection.

## API

The [BiodiversityPMC API](../api/biodiversitypmc/index.md) fetches, searches and counts the same documents.

!!! cite "How to cite"
    If you use BiodiversityPMC, please cite:

    <!-- sibils:cite pasche2023towards pasche2023sibils -->

    Please also cite the SIBiLS papers listed under [How to cite](../publications.md#how-to-cite) on the Publications page.
