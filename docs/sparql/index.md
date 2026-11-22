---
description: >-
  The SIBiLS SPARQL endpoint gives access to MEDLINE and PMC publications cited by SIB
  resources, with their structure and the concepts annotated in their text.
---

# SPARQL endpoint

The SIBiLS SPARQL endpoint gives access to SIBiLS RDF: MEDLINE and PMC publications cited by SIB resources, with their structure and the concepts annotated in their text.
{ .lead }

[Open the SPARQL endpoint site](https://sparql.sibils.org/){ .btn .btn-primary }
[SPARQL editor](https://sparql.sibils.org/sparql-editor){ .btn }
[API documentation](../api/sparql/index.md){ .btn }

<div class="facts" markdown>

Web application
:   [sparql.sibils.org](https://sparql.sibils.org/) (quick start, ontology, downloads) and the [SPARQL editor](https://sparql.sibils.org/sparql-editor)

API
:   SPARQL service at `https://sparql.sibils.org/sparql` (GET or POST), see the [SPARQL API](../api/sparql/index.md)

Data
:   MEDLINE and PMC publications cited by SIB resources such as UniProtKB, Rhea, SwissLipids and Cellosaurus, with their annotations

Output
:   SPARQL results (for example JSON or CSV); the RDF dataset can also be downloaded in Turtle format

Reference
:   No dedicated publication; see Caucheteur et al., Database 2026 [@caucheteur2026sibils]

</div>

## What it does

The SIBiLS SPARQL endpoint lets you query a subset of annotated MEDLINE and PMC publications. For each publication, the RDF describes its text and structure (title, sections, paragraphs and so on) and its annotations: each annotation links a concept to the publication and to its location (title, keywords, abstract, or a sentence of the full text when available). The [ontology page](https://sparql.sibils.org/rdf-ontology) documents the model.

The publications are those cited by SIB resources such as UniProtKB, Rhea, SwissLipids and Cellosaurus. These resources have their own SPARQL endpoints, so federated queries can connect curated statements with the content of the publications that support them. On 22 November 2026, the endpoint described 302,817 publications: 261,874 MEDLINE records and 40,943 PMC full texts, as counted with this query:

```sparql title="count-publications.sparql"
PREFIX sibilo: <https://purl.expasy.org/sibils/rdf/ontology/>
SELECT ?collection (count(distinct ?publi) as ?n)
WHERE { ?publi sibilo:inCollection ?collection }
GROUP BY ?collection
```

The [SIBiLS RDF site](https://sparql.sibils.org/) also offers a Concept Hopper to browse the data model, a dereferencing service, the [downloads](https://sparql.sibils.org/rdf-downloads) of the full dataset, and a [SPARQL editor](https://sparql.sibils.org/sparql-editor) with example queries. If you are not familiar with SPARQL, the quick start suggests the [Expasy GPT chatbot](https://www.expasy.org/chat) to help write queries.

## Video

A presentation of the SPARQL endpoint, recorded in 2023 (4 min 51 s, QuickTime, 183 MB). Some addresses and namespaces shown in it have changed since; the current ones are on the [ontology page](https://sparql.sibils.org/rdf-ontology).

<div class="video"><video controls preload="none" poster="../assets/posters/sparql.jpg" aria-label="SIBiLS SPARQL endpoint video"><source src="https://candy.text-analytics.ch/sibils-sparql.mov" type="video/mp4"><a href="https://candy.text-analytics.ch/sibils-sparql.mov">Download the SPARQL video</a> (QuickTime, 183 MB).</video></div>

## API

See the [SPARQL API](../api/sparql/index.md) page for programmatic access to `https://sparql.sibils.org/sparql`. The [SPARQL service page](https://sparql.sibils.org/sparql-service) of the SIBiLS RDF site gives curl and Python examples.

!!! cite "How to cite"
    There is no dedicated publication for the SPARQL endpoint. Please cite SIBiLS:

    - Gobeill J, Caucheteur D, Michel PA, Mottin L, Pasche E, Ruch P (2020). SIB Literature Services: RESTful customizable search engines in biomedical literature, enriched with automatically mapped biomedical concepts. *Nucleic Acids Research* 48(W1):W12–W16. [doi:10.1093/nar/gkaa328](https://doi.org/10.1093/nar/gkaa328) · [PMID 32379317](https://pubmed.ncbi.nlm.nih.gov/32379317/)
    - Caucheteur D, Flament A, Gobeill J, Pasche E, Michel PA, Mottin L, Liyanapathirana J, Mottaz A, Ruch P (2026). Enhancing the SIB Literature Services (SIBiLS) with annotations to support biocuration. *Database* 2026:baag034. [doi:10.1093/database/baag034](https://doi.org/10.1093/database/baag034) · [PMID 42768721](https://pubmed.ncbi.nlm.nih.gov/42768721/)
