---
template: home.html
title: SIB Literature Services
description: >-
  SIBiLS (SIB Literature Services) annotates MEDLINE, PubMed Central,
  supplementary data, Plazi treatments and Zenodo records with concepts from
  reference vocabularies, and gives free access to them through web
  applications, REST APIs and a SPARQL endpoint.
hero_lead: >-
  SIBiLS gives free access to biomedical and biodiversity literature, annotated
  with concepts from reference vocabularies, through web applications, REST APIs
  and a SPARQL endpoint.
hero_actions:
  - {label: Search BiodiversityPMC, url: "https://biodiversitypmc.sibils.org/", primary: true}
  - {label: API documentation, url: api/index.md}
---

## Services

<div class="cards" markdown>

- ### BiodiversityPMC

    Searches MEDLINE, PMC+, supplementary data, Plazi treatments and Zenodo records in one place, for life-science and biodiversity researchers, and shows the concepts annotated in each document.

    [Open<span class="visually-hidden"> BiodiversityPMC</span>](https://biodiversitypmc.sibils.org/) · [Documentation<span class="visually-hidden"> of BiodiversityPMC</span>](biodiversitypmc/index.md) · [API<span class="visually-hidden"> of BiodiversityPMC</span>](api/biodiversitypmc/index.md)

- ### Question-Answering

    Answers questions written in natural language from MEDLINE, PMC and Plazi documents, and shows the passages each answer comes from.

    [Open<span class="visually-hidden"> Question-Answering</span>](https://qa.sibils.org/) · [Documentation<span class="visually-hidden"> of Question-Answering</span>](qa/index.md) · [API<span class="visually-hidden"> of Question-Answering</span>](api/biodiversitypmc/qa.md)

- ### BiotXplorer

    Finds biotic interactions between taxa reported in the literature, such as “host of”, together with the passages that support each interaction.

    [Open<span class="visually-hidden"> BiotXplorer</span>](https://biotxplorer.sibils.org/) · [Documentation<span class="visually-hidden"> of BiotXplorer</span>](biotxplorer/index.md) · [API<span class="visually-hidden"> of BiotXplorer</span>](https://biotxplorer.sibils.org/api/)

- ### Variomes

    Ranks the literature about a genomic variant, or prioritises a list of variants, across MEDLINE, PMC, supplementary data and clinical trials, to support variant curation.

    [Open<span class="visually-hidden"> Variomes</span>](https://variomes.sibils.org/) · [Documentation<span class="visually-hidden"> of Variomes</span>](variomes/index.md) · [API<span class="visually-hidden"> of Variomes</span>](api/variomes/index.md)

- ### SynVar

    Generates the synonyms and normalised descriptions of a human variant at genome, transcript and protein level; Variomes uses them to find more of the literature about a variant.

    [Open<span class="visually-hidden"> SynVar</span>](https://synvar.sibils.org/) · [Documentation<span class="visually-hidden"> of SynVar</span>](synvar/index.md) · [API<span class="visually-hidden"> of SynVar</span>](api/synvar/index.md)

- ### Triage

    Ranks new publications every week for curation teams: CellTriage for Cellosaurus (MEDLINE and PMC), and DisTriage, ScaleBioMTriage and IpbesTriage for DisProt, island biodiversity and IPBES.

    [Open<span class="visually-hidden"> the Triage app</span>](https://triage.sibils.org/) · [Documentation<span class="visually-hidden"> of Triage</span>](celltriage/index.md) · [API<span class="visually-hidden"> of CellTriage</span>](api/celltriage/index.md)

- ### SPARQL endpoint

    Gives SPARQL access to an RDF version of the publications cited by SIB resources such as UniProtKB, Rhea, SwissLipids and Cellosaurus, and of their SIBiLS annotations, for federated queries.

    [Open<span class="visually-hidden"> the SPARQL endpoint</span>](https://sparql.sibils.org/) · [Documentation<span class="visually-hidden"> of the SPARQL endpoint</span>](sparql/index.md) · [API<span class="visually-hidden"> of the SPARQL endpoint</span>](api/sparql/index.md)

</div>

## What SIBiLS does

<div class="split" markdown>
<div markdown>

SIBiLS keeps a local copy of MEDLINE, PMC+ (PubMed Central and open-access articles from other publishers), PMC supplementary data, Plazi treatments and Zenodo records, updated daily, and annotates every new or updated document with concepts from reference vocabularies such as MeSH, the Gene Ontology, NCBI Taxonomy and ENVO. For each match it records the vocabulary, the concept identifier, the preferred term and the position in the text. The [Collections](collections/sibils_collections.md) and [Vocabularies](vocabularies.md) pages give the details.

### APIs

- [Fetch](api/biodiversitypmc/fetch.md) returns parsed and annotated documents for a list of identifiers (PMIDs, PMCIDs…), in JSON or BioC.
- [Search](api/biodiversitypmc/search.md) runs a free-text or Elasticsearch JSON query on one collection and returns ranked documents.
- [Question-Answering](api/biodiversitypmc/qa.md) answers a question written in natural language from MEDLINE, PMC and Plazi, with the documents each answer is based on.

The [API documentation](api/index.md) lists the APIs of every service.

</div>
<figure class="diagram" markdown>
![Diagram of the SIBiLS architecture. Full texts and supplementary data (pmc, suppdata), citations (medline) and treatments (plazi) are parsed, then mapped to biomedical vocabularies such as DrugBank, neXtProt and GO, with daily updates. Parsed content and mapped entities are stored in MongoDB and indexed in Elasticsearch. The Fetch API takes PMIDs or PMCIDs and returns parsed content and mapped entities in BioC JSON; the Customizable Search API takes a Lucene query and returns ranked documents.](assets/graphical_abstract.png){ loading=lazy width="720" height="540" }
<figcaption markdown>Architecture of SIBiLS, updated from the graphical abstract of the [2020 paper in *Nucleic Acids Research*](publications.md#ref-10_1093_nar_gkaa328). Current figures: [Collections](collections/sibils_collections.md) and [Vocabularies](vocabularies.md). [Full-size image](assets/graphical_abstract.png) (PNG, 283 kB).</figcaption>
</figure>
</div>

## Introduction video

<figure markdown>
<div class="video"><video controls preload="none" poster="assets/posters/introduction.jpg"><source src="https://candy.text-analytics.ch/Speech.mp4" type="video/mp4"><a href="https://candy.text-analytics.ch/Speech.mp4">Download the introduction video (MP4)</a></video></div>
<figcaption markdown>A presentation of SIBiLS and its services (2 min 45 s, MP4, 19.6 MB).</figcaption>
</figure>
