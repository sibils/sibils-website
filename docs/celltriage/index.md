---
description: >-
  Triage services (CellTriage, DisTriage, ScaleBioMTriage, IpbesTriage) score new
  publications every week for their relevance to a curation project.
---

# Triage

Triage services score new publications every week for their relevance to a curation project, so that curators can read the most useful ones first.
{ .lead }

[Open the Triage app](https://triage.sibils.org/){ .btn .btn-primary }
[Open CellTriage](https://triage.sibils.org/celltriage){ .btn }
[CellTriage API](../api/celltriage/index.md){ .btn }

<div class="facts" markdown>

Web application
:   [triage.sibils.org](https://triage.sibils.org/): CellTriage, DisTriage, ScaleBioMTriage, IpbesTriage

API
:   CellTriage API, interactive documentation at [celltriage.sibils.org/docs](https://celltriage.sibils.org/docs); see the [CellTriage API](../api/celltriage/index.md) page

Collections
:   MEDLINE and PMC (CellTriage)

Output
:   Ranked lists of publications, updated every week; export as JSON or CSV in the web application

Reference
:   CellTriage: no dedicated publication. DisTriage: Nugnes et al., Nucleic Acids Research 2026 [@nugnes2026disprot]

</div>

## CellTriage

[CellTriage](https://triage.sibils.org/celltriage) helps the curators of [Cellosaurus](https://www.cellosaurus.org/) find, among the articles published every week, those that give information about cell lines, such as their properties and origin.

CellTriage uses large language models pre-trained on biomedical texts and fine-tuned to identify relevant publications. It ranks new abstracts from MEDLINE and full-text articles from PubMed Central on a weekly basis, assigning each publication a score based on the likelihood that it contains useful information for Cellosaurus.

The CellTriage page of the web application lists the weekly updates; each week opens the ranked documents, which can be filtered (for example by Cellosaurus cell line) and exported. The former address `https://celltriage.sibils.org/` redirects to [triage.sibils.org/celltriage](https://triage.sibils.org/celltriage).

## Other triage services

The Triage web application also hosts these services, each with its own weekly updates:

[DisTriage](https://triage.sibils.org/distriage)
:   A literature triage service that helps biocurators identify and prioritize relevant publications for the curation of [DisProt](https://www.disprot.org/), the database of intrinsically disordered proteins [@nugnes2026disprot]. DisProt curators use it to rank new publications every week.

[ScaleBioMTriage](https://triage.sibils.org/scalebiomtriage)
:   An island biodiversity triage system, developed within the ScaleBioM project (Scalable Biodiversity Monitoring by Broadening Article Acquisition, 2025–2026; see the [list of approved projects](https://www.swissuniversities.ch/fileadmin/swissuniversities/Dokumente/Hochschulpolitik/Open_Science/2025/2025_B3.2_Approved_Projects.pdf) of swissuniversities), a joint project of HES-SO, SIB and the University of Neuchâtel.

[IpbesTriage](https://triage.sibils.org/ipbestriage)
:   A triage service designed to support [IPBES](https://www.ipbes.net/) (the Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services) in its global assessments. Unlike the other triage services, it is a multiclass, multilabel classifier.

## API

The [CellTriage API](../api/celltriage/index.md) scores a list of PMIDs submitted by the user; its interactive documentation is at [celltriage.sibils.org/docs](https://celltriage.sibils.org/docs).

!!! cite "How to cite"
    There is no dedicated publication for CellTriage. Please cite SIBiLS:

    - Gobeill J, Caucheteur D, Michel PA, Mottin L, Pasche E, Ruch P (2020). SIB Literature Services: RESTful customizable search engines in biomedical literature, enriched with automatically mapped biomedical concepts. *Nucleic Acids Research* 48(W1):W12–W16. [doi:10.1093/nar/gkaa328](https://doi.org/10.1093/nar/gkaa328) · [PMID 32379317](https://pubmed.ncbi.nlm.nih.gov/32379317/)
    - Caucheteur D, Flament A, Gobeill J, Pasche E, Michel PA, Mottin L, Liyanapathirana J, Mottaz A, Ruch P (2026). Enhancing the SIB Literature Services (SIBiLS) with annotations to support biocuration. *Database* 2026:baag034. [doi:10.1093/database/baag034](https://doi.org/10.1093/database/baag034) · [PMID 42768721](https://pubmed.ncbi.nlm.nih.gov/42768721/)

    DisTriage is described in:

    - Nugnes MV, Bouhraoua KEA, Zoubiri M, Pancsa R, Fichó E, DisProt Consortium, Tompa P, Piovesan D, Tosatto SCE, Aspromonte MC (2026). DisProt in 2026: enhancing intrinsically disordered proteins accessibility, deposition, and annotation. *Nucleic Acids Research* 54(D1):D383–D392. [doi:10.1093/nar/gkaf1175](https://doi.org/10.1093/nar/gkaf1175) · [PMID 41249866](https://pubmed.ncbi.nlm.nih.gov/41249866/)
