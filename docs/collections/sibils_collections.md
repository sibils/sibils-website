---
description: >-
  The collections that SIBiLS indexes and annotates: MEDLINE, PMC and PMC+, supplementary
  data, Plazi treatments and Zenodo, with their sizes.
---

# SIBiLS collections

SIBiLS indexes and annotates five collections of publications: MEDLINE, PMC and PMC+, supplementary data, Plazi treatments and Zenodo. Together they form [BiodiversityPMC](../biodiversitypmc/index.md), to which publishers can [add their publications](how_to_upload.md).
{ .lead }

The documents come from the FTP server of the US National Library of Medicine, which SIBiLS harvests, from the SIBiLS FTP server, where Plazi and other publishers upload their documents, and from Zenodo communities. Documents are collected and updated daily. Documents are annotated with concepts from the SIBiLS [vocabularies](../vocabularies.md).

Each collection has an API id, used as the `col` parameter of the [fetch](../api/biodiversitypmc/fetch.md) and [search](../api/biodiversitypmc/search.md) APIs.

## Collection sizes

<!-- sibils:collection-counts -->

## MEDLINE

MEDLINE, the bibliographic database of the US National Library of Medicine, holds citations and abstracts from thousands of biomedical and life-science journals.

API id `medline`. Documents are identified by their PMID, for example [`14691011`](https://biodiversitypmc.sibils.org/api/fetch?ids=14691011&col=medline).

## PMC and PMC+

PubMed Central (PMC) is the free full-text archive of biomedical and life-science journal literature at the US National Library of Medicine.

SIBiLS indexes the PMC open-access subset and the PMC author manuscripts, and adds open-access articles on biodiversity that are not in PMC (such as Pensoft articles); this collection is called PMC+. It has three partitions: the PMC open-access subset, the PMC author manuscripts and the PMC+ subset of articles from outside PMC.

API id `pmc`. Documents are identified by their PMCID, for example [`PMC7319474`](https://biodiversitypmc.sibils.org/api/fetch?ids=PMC7319474&col=pmc), or by their DOI for articles of the PMC+ subset, for example [`10.3389/fevo.2023.1081385`](https://biodiversitypmc.sibils.org/api/fetch?ids=10.3389/fevo.2023.1081385&col=pmc).

## Supplementary data

Supplementary files are published with a PMC article but outside its main text: data tables, spreadsheets, documents, images and videos, often holding raw data, detailed methods or additional analyses. SIBiLS extracts their text, using OCR for images, so that they can be searched like articles. Gobeill et al. (2025) describe the method and what these files add to the literature [@gobeill2025supplementary]. The collection has two partitions: supplementary data files and manuscript figures.

API id `suppdata`. Documents are identified by the PMCID of the article followed by the file name, for example [`PMC10838014_gyad114_suppl_supplementary_data_sd3.xlsx`](https://biodiversitypmc.sibils.org/api/fetch?ids=PMC10838014_gyad114_suppl_supplementary_data_sd3.xlsx&col=suppdata).

## Plazi treatments

A taxonomic treatment is the part of a publication that describes a taxon: its classification, description and identification, synonyms, distribution and ecological notes. [Plazi](https://plazi.org/) extracts treatments from publications as structured records that taxonomists, ecologists and conservationists can reuse. SIBiLS began indexing Plazi treatments, together with Pensoft articles that are not in PMC, within the BiCIKL project [@pasche2023towards]; the [e-BioDiv](https://ebiodiv.org/) project (2021 to 2023), which complements BiCIKL, set up their production-level import.

API id `plazi`. Documents are identified by their Plazi treatment identifier, for example [`8F0287F93576FFAF381A50CBFA9A0B55`](https://biodiversitypmc.sibils.org/api/fetch?ids=8F0287F93576FFAF381A50CBFA9A0B55&col=plazi).

## Zenodo

The Biodiversity Literature Repository (BLR) is a collection hosted on Zenodo as the [Biosyslit community](https://zenodo.org/communities/biosyslit/), which is harvested and indexed into SIBiLS. BLR holds open-access and restricted-access records; restricted records can be read by members of the community. Some records of BLR also belong to the [BHL-BLR](https://zenodo.org/communities/bhl-blr/), [Batlit](https://zenodo.org/communities/batlit/) or [TaxoDros](https://zenodo.org/communities/taxodros/) communities; the collection counts them as partitions. BLR mostly holds PDF files, which are harder to reuse than the JATS XML of PMC+; SIBiLS converts them to text at indexing time.

API id `zenodo`. Documents are identified by the Zenodo record id followed by a chunk number, for example [`15935589_0`](https://biodiversitypmc.sibils.org/api/fetch?ids=15935589_0&col=zenodo).

