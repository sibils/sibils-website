---
description: >-
  The papers, abstracts, reports and datasets that describe SIBiLS and its
  services, published work that uses them, and how to cite them.
---

# Publications

The papers, abstracts, reports and datasets that describe SIBiLS and its services, published work that uses them, and how to cite them.
{ .lead }

## How to cite

!!! cite ""

    If you use SIBiLS, its APIs or one of its web applications, please cite both papers:

    <!-- sibils:cite 10_1093_nar_gkaa328 caucheteur2026sibils -->

Some services, collections and vocabularies have their own publication, to cite together with the two SIBiLS papers:

| Service or data | Publication |
|-----------------|-------------|
| [BiodiversityPMC](biodiversitypmc/index.md) | <!-- sibils:cite-short pasche2023sibils --> and <!-- sibils:cite-short pasche2023towards --> |
| [Question-Answering](qa/index.md) | No dedicated publication: cite the two SIBiLS papers. The current pipeline is described in a project milestone report of the ELIXIR project KYBELE, <!-- sibils:cite-short flament2026qademonstrator --> |
| [BiotXplorer](biotxplorer/index.md) | <!-- sibils:cite-short ruch2024biotxplorer --> |
| [Variomes](variomes/index.md) | <!-- sibils:cite-short pasche2022variomes --> |
| [SynVar](synvar/index.md) | <!-- sibils:cite-short mottaz2022synvar -->, with the Variomes paper |
| [Triage](celltriage/index.md) | DisTriage: <!-- sibils:cite-short nugnes2026disprot -->. CellTriage, ScaleBioMTriage and IpbesTriage: no dedicated publication |
| [SPARQL endpoint](sparql/index.md) | No dedicated publication |
| [Supplementary data](collections/sibils_collections.md#supplementary-data) collection | <!-- sibils:cite-short gobeill2025supplementary --> |
| [COVoc](vocabularies.md#covoc) vocabularies | <!-- sibils:cite-short caucheteur2023covoc --> |

When you report results obtained with SIBiLS, also give the date of your queries: the collections are updated daily. The release of the software is given by the `sibils_version` field of the [/count](https://biodiversitypmc.sibils.org/api/count) endpoint.

??? note "BibTeX for the papers to cite"

    <!-- sibils:bibtex 10_1093_nar_gkaa328 caucheteur2026sibils pasche2023towards pasche2023sibils ruch2024biotxplorer pasche2022variomes mottaz2022synvar nugnes2026disprot gobeill2025supplementary caucheteur2023covoc -->

## Publications about SIBiLS

Papers, conference abstracts, posters, project reports and datasets that describe SIBiLS or one of its services, newest first. The two SIBiLS papers are under [How to cite](#how-to-cite). Presentations, news items and preprints of published papers are not listed.

### Papers, conference abstracts and posters

<!-- sibils:bibliography about-papers -->

### Reports and datasets

Deposited on Zenodo.

<!-- sibils:bibliography about-reports -->

## Work using SIBiLS

Published work that uses SIBiLS or one of its services, newest first: studies by other groups or with members of the SIBiLS team, and the team's runs in evaluation campaigns. The note after each reference says how the work uses or describes SIBiLS.

<!-- sibils:bibliography work-using -->

See also [the works that Europe PMC lists as citing the 2020 SIBiLS paper](https://europepmc.org/search?query=CITES%3A32379317_MED). To suggest published work that uses SIBiLS, open an issue in the [sibils/community](https://github.com/sibils/community/issues) repository on GitHub.

Entries were checked against Crossref, DataCite and PubMed in November 2026.
