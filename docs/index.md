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
# Search box of the hero (theme/home.html): a GET form to url?q=<text>, which
# the app runs when it loads (an empty q opens the app; not ?query=, which
# Question-Answering rewrites and then sends each API call twice). One field
# (label: its name, read by screen readers; the buttons say what it is for)
# and one button per target: the first one is the form's own address and
# Enter's; the others send the same field to their app (formaction). No
# JavaScript. Examples: the apps' own ("Show examples" in each app), one row
# per target (examples_label, then links to url?q=<example>), each kept to one
# line from 1024 px.
hero_search:
  param: q
  label: Search the literature or ask a question
  placeholder: Topic, species or question
  targets:
    - app: BiodiversityPMC
      url: "https://biodiversitypmc.sibils.org/"
      submit: Search
      examples_label: Search
      examples:
        - Halacarid mites
        - Ixodiphagus hookeri
    - app: Question-Answering
      url: "https://qa.sibils.org/"
      submit: Ask a question
      examples_label: Ask
      examples:
        - What diseases are associated with ticks?
---

<div class="band" markdown>

## Services

<div class="cards" markdown>

- ### Search the literature<span class="visually-hidden"> with</span> [BiodiversityPMC](https://biodiversitypmc.sibils.org/) { #biodiversitypmc .svc .svc-search }

    Searches MEDLINE, PMC+, supplementary data, Plazi treatments and Zenodo records in one place, for life-science and biodiversity researchers, and shows the concepts annotated in each document.

    <span class="card-links">[Documentation<span class="visually-hidden"> of BiodiversityPMC</span>](services/biodiversitypmc/index.md) · [API<span class="visually-hidden"> of BiodiversityPMC</span>](developers/biodiversitypmc/index.md)</span>

- ### Ask a question<span class="visually-hidden"> with</span> [Question-Answering](https://qa.sibils.org/) { #question-answering .svc .svc-question }

    Answers questions written in natural language from MEDLINE, PMC and Plazi documents, and shows the passages each answer comes from.

    <span class="card-links">[Documentation<span class="visually-hidden"> of Question-Answering</span>](services/qa/index.md) · [API<span class="visually-hidden"> of Question-Answering</span>](developers/qa/index.md)</span>

- ### Find biotic interactions<span class="visually-hidden"> with</span> [BiotXplorer](https://biotxplorer.sibils.org/) { #biotxplorer .svc .svc-interaction }

    Finds biotic interactions between taxa reported in the literature, such as “host of”, together with the passages that support each interaction.

    <span class="card-links">[Documentation<span class="visually-hidden"> of BiotXplorer</span>](services/biotxplorer/index.md) · [API<span class="visually-hidden"> of BiotXplorer</span>](developers/biotxplorer/index.md)</span>

- ### Rank literature on a variant<span class="visually-hidden"> with</span> [Variomes](https://variomes.sibils.org/) { #variomes .svc .svc-variant }

    Ranks the literature about a genomic variant, or prioritises a list of variants, across MEDLINE, PMC, supplementary data and clinical trials, to support variant curation.

    <span class="card-links">[Documentation<span class="visually-hidden"> of Variomes</span>](services/variomes/index.md) · [API<span class="visually-hidden"> of Variomes</span>](developers/variomes/index.md)</span>

- ### Generate variant synonyms<span class="visually-hidden"> with</span> [SynVar](https://synvar.sibils.org/) { #synvar .svc .svc-synonyms }

    Generates the synonyms and normalised descriptions of a human variant at genome, transcript and protein level; Variomes uses them to find more of the literature about a variant.

    <span class="card-links">[Documentation<span class="visually-hidden"> of SynVar</span>](services/synvar/index.md) · [API<span class="visually-hidden"> of SynVar</span>](developers/synvar/index.md)</span>

- ### Rank new MEDLINE papers<span class="visually-hidden"> with</span> [Triage](https://triage.sibils.org/) { #triage .svc .svc-triage }

    Four services rank the new MEDLINE publications of each week: CellTriage for Cellosaurus, DisTriage for DisProt (a prototype), ScaleBioMTriage for island biodiversity and IpbesTriage for IPBES.

    <span class="card-links">[Documentation<span class="visually-hidden"> of Triage</span>](services/triage/index.md) · [API<span class="visually-hidden"> of CellTriage</span>](developers/celltriage/index.md)</span>

- ### Run federated queries<span class="visually-hidden"> with the</span> [SPARQL endpoint](https://sparql.sibils.org/) { #sparql-endpoint .svc .svc-graph }

    Gives SPARQL access to an RDF version of the publications cited by SIB resources such as UniProtKB, Rhea, SwissLipids and Cellosaurus, and of their SIBiLS annotations, for federated queries.

    <span class="card-links">[Documentation<span class="visually-hidden"> of the SPARQL endpoint</span>](services/sparql/index.md) · [API<span class="visually-hidden"> of the SPARQL endpoint</span>](developers/sparql/index.md)</span>

</div>

</div>

## What SIBiLS does

<div class="split" markdown>
<div markdown>

SIBiLS keeps a local copy of MEDLINE, PMC+ (PubMed Central and open-access articles from other publishers), PMC supplementary data, Plazi treatments and Zenodo records, updated daily, and annotates every new or updated document with concepts from reference vocabularies such as MeSH, the Gene Ontology, NCBI Taxonomy and ENVO. For each match it records the vocabulary, the concept identifier, the preferred term and the position in the text. The [Collections](data/collections.md) and [Vocabularies](data/vocabularies.md) pages give the details.

### APIs

- [Fetch](developers/biodiversitypmc/fetch.md) returns parsed and annotated documents for a list of identifiers (PMIDs, PMCIDs…), in JSON or BioC.
- [Search](developers/biodiversitypmc/search.md) runs a free-text or Elasticsearch JSON query on one collection and returns ranked documents.
- [Question-Answering](developers/qa/index.md) answers a question written in natural language from MEDLINE, PMC and Plazi, with the documents each answer is based on.

[APIs of every service](developers/index.md){ .btn }

</div>
<figure class="diagram" markdown>
![Diagram of the SIBiLS architecture. Full texts and supplementary data (pmc, suppdata), citations (medline) and treatments (plazi) are parsed, then mapped to biomedical vocabularies such as DrugBank, neXtProt and GO, with daily updates. Parsed content and mapped entities are stored in MongoDB and indexed in Elasticsearch. The Fetch API takes PMIDs or PMCIDs and returns parsed content and mapped entities in BioC JSON; the Customizable Search API takes a Lucene query and returns ranked documents.](assets/graphical_abstract.png){ loading=lazy width="720" height="540" }
<figcaption markdown>Architecture of SIBiLS, updated from the graphical abstract of the [2020 paper in *Nucleic Acids Research*](publications.md#ref-10_1093_nar_gkaa328). Current figures: [Collections](data/collections.md) and [Vocabularies](data/vocabularies.md). [Full-size image](assets/graphical_abstract.png) (PNG, 283 kB).</figcaption>
</figure>
</div>

## Introduction video

<figure markdown>
<div class="video"><video controls preload="none" poster="assets/posters/introduction.jpg"><source src="https://candy.text-analytics.ch/Speech.mp4" type="video/mp4"><a href="https://candy.text-analytics.ch/Speech.mp4">Download the introduction video (MP4)</a></video></div>
<figcaption markdown>A presentation of SIBiLS and its services (2 min 45 s, MP4, 19.6 MB).</figcaption>
</figure>
