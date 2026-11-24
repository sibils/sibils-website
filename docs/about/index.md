---
description: >-
  Who develops and runs SIBiLS, how to contact the team, funding, use and
  licence of the annotations, source code, history and privacy.
---

# About SIBiLS

SIBiLS (SIB Literature Services) is a resource of the SIB Swiss Institute of Bioinformatics, developed and run by the SIB Text Mining group at HEG-Genève (HES-SO). It keeps daily updated copies of MEDLINE, PubMed Central and other literature collections, annotates them with concepts from reference vocabularies, and gives free access to them through web applications, REST APIs and a SPARQL endpoint.
{ .lead }

## Who runs SIBiLS

SIBiLS is developed and run by the [SIB Text Mining group](https://www.sib.swiss/patrick-ruch-group) of the [SIB Swiss Institute of Bioinformatics](https://www.sib.swiss/), led by Patrick Ruch. Since 2008 the group has been based at the [Haute école de gestion de Genève](https://heg.hesge.ch/) (HEG-Genève, [HES-SO University of Applied Sciences and Arts Western Switzerland](https://www.hes-so.ch/)), where Patrick Ruch also heads the [BiTeM group](https://bitem.hesge.ch/) of the Information Science department. [Expasy](https://www.expasy.org/resources/sibils), the SIB portal of bioinformatics resources, lists SIBiLS as developed by the Text Mining group and as an ELIXIR Switzerland service. The name SIBiLS is also expanded as Swiss Institute of Bioinformatics Literature Services.

A [Scientific Advisory Board](sab.md) advises the team on the development of the services.

## Contact

- **Questions about the services:** Julien Gobeill, [julien.gobeill@hesge.ch](mailto:julien.gobeill@hesge.ch).
- **Bug reports and feature requests** for the web applications and APIs: [issues of the sibils/community repository](https://github.com/sibils/community/issues) on GitHub (a GitHub account is needed; issues are public). The "Bug report" and "Feature request" links in the footers of BiodiversityPMC, Question-Answering, BiotXplorer and Triage open these forms. The same repository takes suggestions of published work that uses SIBiLS.
- **Corrections to this documentation:** [issues of the sibils/sibils-website repository](https://github.com/sibils/sibils-website/issues).
- **To have your publications indexed,** see [Add your publications](../data/add-publications.md).

## Funding

Past and current funding, most recent first:

- **ELIXIR project KYBELE** (2026): new taxon and [trophic-guild vocabularies](../data/vocabularies.md#kybele) for the annotation of BiodiversityPMC, and a [Question-Answering](../services/qa/index.md) demonstrator.
- **ScaleBioM** (swissuniversities, Open Science II programme, 2026; led by HES-SO with the University of Neuchâtel): to add a channel that acquires biodiversity articles from OpenAlex for BiodiversityPMC. [ScaleBioMTriage](../services/triage/index.md#other-triage-services) was developed within it.
- **METAPLANTCODE** (Biodiversa+, Swiss National Science Foundation, grant 216811, 2024 to 2028): the addition of biodiversity vocabularies.
- **FAIRClinical** (CHIST-ERA, Swiss National Science Foundation, grant 217525, 2024 to 2027): part of the evaluation of the annotations.
- **eBioDiv** (swissuniversities, 2021 to 2023; [ebiodiv.org](https://ebiodiv.org/)), a project of HES-SO and SIB with Plazi, the Natural History Museum of Bern and the Bern University of Applied Sciences: the production-level import of Plazi taxonomic treatments into SIBiLS. The swissuniversities Open Science programme funded work on BiodiversityPMC presented in 2023.
- **BiCIKL** (European Commission, Horizon 2020, grant 101007492, 2021 to 2024): BiodiversityPMC, developed with Plazi and Pensoft.
- **HES-SO** (2020): the open-access charges of the SIBiLS paper in *Nucleic Acids Research*.
- **ELIXIR-EXCELERATE** (European Commission, Horizon 2020, grant 676559, 2015 to 2019): the first SIBiLS services.
- **ELIXIR Data Platform:** the first SIBiLS services, the supplementary data collection, the annotation of supplementary data files, and the cross-references between BiodiversityPMC and BioStudies and Europe PMC.

## Use, licence and citation { #licence }

The APIs are free and need no registration or API key; [Using the APIs](../developers/index.md#using-the-apis) gives the limits to respect. The collections are updated daily.

The annotations produced by SIBiLS (the tagged entities) are licensed under the [Creative Commons Attribution 3.0 Switzerland](https://creativecommons.org/licenses/by/3.0/ch/deed.en) licence (CC BY 3.0 CH). The documents themselves keep the terms set by their publishers and source repositories; for example, each article of the PMC open-access subset has its own licence.

To cite SIBiLS in your work, see [How to cite](../publications.md#how-to-cite).

## Source code

Code of SIBiLS and of its services on GitHub (the [sibils organisation](https://github.com/sibils) has more repositories):

- [sibils/sibils-website](https://github.com/sibils/sibils-website): this documentation website (MkDocs).
- [sibils/jats-parser](https://github.com/sibils/jats-parser): parser of JATS XML full texts (first published as bitem-heg-geneve/jats-parser) and the proxy that prepares SIBiLS documents for the publication viewer.
- [sibils/sibils2bioc](https://github.com/sibils/sibils2bioc): conversion of the SIBiLS internal format to BioC, used to display documents with their annotations.
- [sibils/BioMoQA-RAG](https://github.com/sibils/BioMoQA-RAG): Question-Answering pipeline behind qa.sibils.org.
- [sibils/GCBR_match](https://github.com/sibils/GCBR_match): matching of Global Core Biodata Resource names and accession numbers, used in the study of supplementary data files.
- [variomes/sibtm-variomes](https://github.com/variomes/sibtm-variomes): code published with the Variomes paper.
- [bitem-heg-geneve/CellTriage-api](https://github.com/bitem-heg-geneve/CellTriage-api): code of the [CellTriage API](../developers/celltriage/index.md), which scores articles for their relevance to Cellosaurus curation.

## History

- **2020:** SIBiLS is described in the web server issue of *Nucleic Acids Research*, with daily updated copies of MEDLINE and the PubMed Central open-access subset.
- **2021 to 2023:** the eBioDiv project, which complements BiCIKL, sets up a production-level import of Plazi taxonomic treatments into SIBiLS.
- **2023:** [BiodiversityPMC](../services/biodiversitypmc/index.md), built within the BiCIKL project, gives one entry point to MEDLINE, PMC, Plazi treatments and Pensoft articles that are not in PMC. After a soft launch in summer 2023, it is officially announced at the BiCIKL General Assembly on 14 February 2024.
- **2024 and 2025:** the [Scientific Advisory Board](sab.md) meets online on 10 December 2024, then in Geneva on 17 and 18 December 2025; its reports are on Zenodo.
- **2025 and 2026:** papers describe the [supplementary data collection](../data/collections.md#supplementary-data) and the current annotation pipeline and its evaluation.

## Privacy

This website counts page views with [Matomo](https://matomo.org/), an open-source web analytics tool, hosted on the team's own domain (matomo.text-analytics.ch) rather than by a third-party analytics service. Matomo sets no cookies, and only the first two bytes of IPv4 addresses are kept. For each page view it receives the web address and title of the page, the site you came from, your local time, how long the page took to load, your screen size, which plugins your browser supports (such as a PDF viewer), and the browser, operating system and language that your browser announces; it also records clicks on links to other sites and on downloads. The tracking code runs only on sibils.org: local copies and previews of this documentation do not load it. The site shows no advertising.

The home page reads the current number of documents in each collection from the SIBiLS API (biodiversitypmc.sibils.org), and the API reference pages load their descriptions from biodiversitypmc.sibils.org and qa.sibils.org: your browser sends these requests without cookies, with only the address of this site as referrer. On the API reference pages, "Try it out" sends the request you write to that API.

Videos are loaded from candy.text-analytics.ch only when you play them. The video on the [Variomes](../services/variomes/index.md) page is hosted on YouTube: the page shows a play button, and your browser loads the YouTube player from youtube-nocookie.com only when you start the video; the player then contacts YouTube and Google servers, and YouTube's privacy policy applies.

If you change the colour theme or choose a tab in a code example, your browser keeps the choice in its local storage (keys sibils-theme and sibils-tab); it is not sent to any server.

The web applications (BiodiversityPMC, Question-Answering, BiotXplorer, Variomes, Triage) have their own privacy pages, linked from their menus.
