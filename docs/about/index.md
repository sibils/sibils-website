---
description: >-
  Who develops and runs SIBiLS, how to contact the team, funding and partners,
  licence of the annotations, privacy and source code.
---

# About SIBiLS

SIBiLS (SIB Literature Services, also expanded as Swiss Institute of Bioinformatics Literature Services) is a resource of the SIB Swiss Institute of Bioinformatics. It keeps copies of MEDLINE, PubMed Central and other literature collections, annotates them with concepts from reference vocabularies, and makes them available through web applications, REST APIs and a SPARQL endpoint.
{ .lead }

## Who runs SIBiLS

SIBiLS is developed and run by the [SIB Text Mining group](https://www.sib.swiss/patrick-ruch-group), led by Patrick Ruch. Since 2008 the group has been based at the Haute école de gestion de Genève (HEG Genève, HES-SO University of Applied Sciences and Arts Western Switzerland), where it is the [BiTeM group](https://bitem.hesge.ch/) of the Information Science department. [Expasy](https://www.expasy.org/resources/sibils), the SIB portal of bioinformatics resources, lists SIBiLS as developed by the Text Mining group and as an ELIXIR Switzerland service.

Milestones:

- 2020: SIBiLS is described in the web server issue of *Nucleic Acids Research*, with daily updated copies of MEDLINE and the PubMed Central open-access subset.
- 2021 to 2023: the [e-BioDiv](https://ebiodiv.org/) project, which complements BiCIKL, sets up a production-level import of Plazi taxonomic treatments into SIBiLS.
- 2023: BiodiversityPMC, built within the BiCIKL project, gives one entry point to MEDLINE, PMC, Plazi treatments and Pensoft articles that are not in PMC. Its official launch is announced on 14 February 2024.
- 2024: the [Scientific Advisory Board](../sab.md) meets online on 10 December 2024; its report is on Zenodo.
- 2025 and 2026: papers describe the supplementary data collection and the current annotation pipeline and its evaluation.

## Contact

- Questions about the services: Julien Gobeill, [julien.gobeill@hesge.ch](mailto:julien.gobeill@hesge.ch).
- Bug reports and feature requests for the web applications and APIs: [issues of the sibils/community repository](https://github.com/sibils/community/issues) on GitHub (a GitHub account is needed). The "Bug report" and "Feature request" links in the footer of BiodiversityPMC open these forms.
- Corrections to this documentation: [issues of the sibils/sibils-website repository](https://github.com/sibils/sibils-website/issues).
- To have your publications indexed, see [Add your publications](../collections/how_to_upload.md).

## Funding and partners

The team belongs to the [SIB Swiss Institute of Bioinformatics](https://www.sib.swiss/) and is hosted by [HEG Genève](https://heg.hesge.ch/) and [HES-SO](https://www.hes-so.ch/). Past and current funding:

- **ELIXIR.** ELIXIR-EXCELERATE (European Commission, Horizon 2020, grant 676559) and the ELIXIR Data Platform funded the first SIBiLS services; the ELIXIR Data Platform also supported the supplementary data collection. In 2026, within the ELIXIR project KYBELE, new taxon and trophic-guild vocabularies were added to the annotation of BiodiversityPMC and a question answering demonstrator was built.
- **European Commission, Horizon 2020.** BiodiversityPMC was developed with Plazi and Pensoft within the BiCIKL project (grant 101007492).
- **swissuniversities.** The [e-BioDiv](https://ebiodiv.org/) project (2021 to 2023), run by HES-SO and SIB with Plazi, the Natural History Museum of Bern and the Bern University of Applied Sciences, was funded by swissuniversities. The swissuniversities Open Science programme funded work on BiodiversityPMC presented in 2023.
- **Swiss National Science Foundation.** The FAIRClinical project (CHIST-ERA, SNSF 217525) supported the evaluation of the annotations, and the METAPLANTCODE project (Biodiversa+, SNSF 216811) the addition of biodiversity vocabularies.
- **HES-SO** paid the open-access charges of the 2020 paper in *Nucleic Acids Research*.

A [Scientific Advisory Board](../sab.md) advises the team on the development of the services.

## Licence

The annotations produced by SIBiLS (the tagged entities) are licensed under the [Creative Commons Attribution 3.0 Switzerland](https://creativecommons.org/licenses/by/3.0/ch/) licence (CC BY 3.0 CH). The documents themselves keep the terms set by their publishers and source repositories; for example, each article of the PMC open-access subset has its own licence.

To cite SIBiLS in your work, see [How to cite](../publications.md#how-to-cite).

## Privacy

This website counts page views with [Matomo](https://matomo.org/), an open-source web analytics tool, hosted on the team's own domain (matomo.text-analytics.ch) rather than by a third-party analytics service. Matomo sets no cookies, and only the first two bytes of IPv4 addresses are kept. The tracking code runs only on sibils.org: local copies and previews of this documentation do not load it. The site shows no advertising.

The home page reads the current number of documents in each collection from the SIBiLS API (biodiversitypmc.sibils.org): your browser sends this request without cookies, with only the address of this site as referrer.

Videos are served from candy.text-analytics.ch, except the video on the [Variomes](../variomes/index.md) page, which is embedded from YouTube through youtube-nocookie.com.

The web applications (BiodiversityPMC, Question-Answering, BiotXplorer, Variomes, Triage) have their own privacy pages, linked from their menus.

## Source code

| Repository | Contents |
|------------|----------|
| [sibils/sibils-website](https://github.com/sibils/sibils-website) | This documentation website (MkDocs) |
| [sibils/jats-parser](https://github.com/sibils/jats-parser) | Parser of JATS XML full texts (first published as bitem-heg-geneve/jats-parser) |
| [sibils/sibils2bioc](https://github.com/sibils/sibils2bioc) | Conversion of the SIBiLS internal format to BioC, used to display documents with their annotations |
| [sibils/BioMoQA-RAG](https://github.com/sibils/BioMoQA-RAG) | Question-Answering pipeline behind qa.sibils.org |
| [sibils/GCBR_match](https://github.com/sibils/GCBR_match) | Code of the study of supplementary data files |
| [variomes/sibtm-variomes](https://github.com/variomes/sibtm-variomes) | Code published with the Variomes paper |
