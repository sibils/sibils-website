---
description: >-
  BiodiversityPMC searches MEDLINE, PMC+, supplementary data, Plazi treatments and
  Zenodo, for life and health scientists and biodiversity researchers.
---

# BiodiversityPMC

BiodiversityPMC is a search engine over the SIBiLS literature collections, built for life and health scientists and for researchers in biodiversity and related sciences.
{ .lead }

[Open BiodiversityPMC](https://biodiversitypmc.sibils.org/){ .btn .btn-primary }
[API documentation](../../developers/biodiversitypmc/index.md){ .btn }

<div class="facts" markdown>

Web application
:   [biodiversitypmc.sibils.org](https://biodiversitypmc.sibils.org/)

API
:   REST API at `https://biodiversitypmc.sibils.org/api`, see the [BiodiversityPMC API](../../developers/biodiversitypmc/index.md)

Collections
:   MEDLINE, PMC+, supplementary data, Plazi treatments, Zenodo (BLR and other communities); sizes on the [Collections](../../data/collections.md) page

Output
:   Ranked lists of documents; export as JSON or CSV in the web application, JSON or BioC through the API

Citation
:   Pasche et al. [-@pasche2023towards] [-@pasche2023sibils], with the SIBiLS papers Gobeill et al. [-@10_1093_nar_gkaa328] and Caucheteur et al. [-@caucheteur2026sibils]

</div>

## What it does

BiodiversityPMC builds on the [SIBiLS](../../index.md) copies of MEDLINE citations and PubMed Central (PMC) full-text articles (the PMC open-access subset and the author manuscripts) from the US National Library of Medicine. It adds articles that are not in PMC, from publishers such as Pensoft; more than a million taxonomic treatments from [Plazi](https://plazi.org/); the text extracted from PMC supplementary files; and documents harvested from Zenodo communities such as the [Biodiversity Literature Repository](https://zenodo.org/communities/biosyslit/) (BLR). The [Collections](../../data/collections.md) page describes each collection and gives its current size.

With these additions it covers more disciplines than PMC, such as ecology, environmental sciences and taxonomy, and serves taxonomists, ecologists and anyone who studies or monitors biodiversity. Its authors present it as a step towards a One Health library [@pasche2023sibils].

BiodiversityPMC was soft-launched in summer 2023 and officially announced at the BiCIKL General Assembly in Cambridge (UK) on 14 February 2024 [@eurekalert2024biodiversitypmc].

## Using BiodiversityPMC

The [Documentation](https://biodiversitypmc.sibils.org/docs) page of the web application describes the query syntax and the fields that can be searched in each collection.
