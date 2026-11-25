---
description: >-
  CellTriage, DisTriage (a prototype), ScaleBioMTriage and IpbesTriage rank new MEDLINE
  publications each week for Cellosaurus, DisProt, island biodiversity and IPBES.
---

# Triage

Four triage services rank the new MEDLINE publications of each week by their relevance to one topic, so that the most relevant ones can be read first: cell lines for Cellosaurus (CellTriage), DisProt curation (DisTriage, a prototype), island biodiversity (ScaleBioMTriage) and the IPBES assessments (IpbesTriage).
{ .lead }

[Open the Triage app](https://triage.sibils.org/){ .btn .btn-primary }
[CellTriage API](../../developers/celltriage/index.md){ .btn }

<div class="facts" markdown>

Web application
:   [triage.sibils.org](https://triage.sibils.org/), one page per service: [CellTriage](https://triage.sibils.org/celltriage), [DisTriage](https://triage.sibils.org/distriage), [ScaleBioMTriage](https://triage.sibils.org/scalebiomtriage), [IpbesTriage](https://triage.sibils.org/ipbestriage)

API
:   CellTriage only: the [CellTriage API](../../developers/celltriage/index.md) scores a list of PMIDs on request; interactive documentation at [celltriage.sibils.org/docs](https://celltriage.sibils.org/docs)

Collections
:   MEDLINE, for the four services; the CellTriage API scores the abstract or, on request, the PMC full text when there is one

Output
:   One list of publications ranked by score per week and per service, in the web application, exportable as JSON or CSV; a score for each given PMID through the CellTriage API

Citation
:   The SIBiLS papers Gobeill et al. [-@10_1093_nar_gkaa328] and Caucheteur et al. [-@caucheteur2026sibils]; for DisTriage, also Nugnes et al. [-@nugnes2026disprot]

</div>

## Triage services

Each service has a page in the Triage app, linked from its name below. It shows the weekly lists, newest first. A list covers the publications that entered PubMed from Monday to Sunday (by their Entrez date) and is usually added on the following Wednesday; it ranks them by score, with their abstracts and identifiers. They can be filtered by publication type and by annotated concepts, starting with the vocabularies that the service shows by default, and each publication can be marked yes, no or maybe; the marks are kept in the browser.

[CellTriage](https://triage.sibils.org/celltriage) { #celltriage }
:   Helps the curators of [Cellosaurus](https://www.cellosaurus.org/) find the publications that give information about cell lines, such as their properties and origin. A language model, pre-trained on biomedical texts and fine-tuned for this task, scores each publication by the likelihood that it holds useful information for Cellosaurus. Its weekly lists start in September 2023; its page shows a filter on [Cellosaurus](../../data/vocabularies.md#cellosaurus) cell lines by default.

[DisTriage](https://triage.sibils.org/distriage) { #distriage }
:   Helps biocurators identify and prioritize the publications relevant to the curation of [DisProt](https://www.disprot.org/), the database of intrinsically disordered proteins. The DisProt 2026 paper describes its model, PubMedBERT fine-tuned to tell relevant from non-relevant publications [@nugnes2026disprot]. It is a prototype under development; its delivery is planned for 2027. Its page shows filters on [DisProt](../../data/vocabularies.md#disprot_type4) terms and [ECO](../../data/vocabularies.md#eco) evidence types by default.

[ScaleBioMTriage](https://triage.sibils.org/scalebiomtriage) { #scalebiomtriage }
:   Ranks publications by their relevance to island biodiversity. It was developed within ScaleBioM (Scalable Biodiversity Monitoring by Broadening Article Acquisition), a swissuniversities project led by HES-SO with the University of Neuchâtel [@swissuniversities2025b32]. The project plans to evaluate how its services can help ecologists, in particular at the University of Neuchâtel, monitor biodiversity on islands. Its weekly lists start in December 2025; its page shows filters on [AGROVOC](../../data/vocabularies.md#agrovoc), [ENVO](../../data/vocabularies.md#envo) and [FLOPO](../../data/vocabularies.md#flopo) by default.

[IpbesTriage](https://triage.sibils.org/ipbestriage) { #ipbestriage }
:   Designed to support [IPBES](https://www.ipbes.net/) (the Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services) in its global assessments. Unlike the other triage services it is a multiclass, multilabel classifier, but the app shows a single score for each publication. Its weekly lists start in January 2026; its page shows the same filters as ScaleBioMTriage by default.

The former address of CellTriage, `https://celltriage.sibils.org/`, leads to its page in the app; the [CellTriage API](../../developers/celltriage/index.md) is still on that host.
