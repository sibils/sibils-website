---
description: >-
  Query the SIBiLS RDF with SPARQL: publications cited by SIB resources, with their structure and
  annotations, and example queries.
---

# SPARQL API

The SIBiLS SPARQL endpoint gives access to an RDF version of part of the SIBiLS content: the publications cited by SIB resources, with their structure and their annotations.
{ .lead }

<div class="facts" markdown>

Endpoint
:   `https://sparql.sibils.org/sparql` (`GET` or `POST`)

Quick start
:   [sparql.sibils.org](https://sparql.sibils.org/) · [SPARQL editor](https://sparql.sibils.org/sparql-editor) · [service help](https://sparql.sibils.org/sparql-service)

Ontology
:   [SIBiLS ontology](https://sparql.sibils.org/rdf-ontology) · [downloads](https://sparql.sibils.org/rdf-downloads)

Web application
:   [sparql.sibils.org](https://sparql.sibils.org/), described in [SPARQL endpoint](../../sparql/index.md)

Authentication
:   None

</div>

## Content

The RDF dataset contains the publications cited by SIB resources such as UniProtKB, Rhea, SwissLipids and Cellosaurus. Each publication is described with its metadata (title, abstract, journal, year, identifiers), its structure (sections, paragraphs, tables, figures, sentences) and its annotations: the concepts of the [SIBiLS vocabularies](../../vocabularies.md) found in its text, with their position.

On 22 November 2026, the endpoint held 302,817 publications: 261,874 from MEDLINE and 40,943 from PMC (example 1 below).

The [quick start site](https://sparql.sibils.org/) describes the dataset, the ontology, a dereferencing service for the RDF IRIs, a concept browser, and the files to download it into your own triple store. The [SPARQL editor](https://sparql.sibils.org/sparql-editor) has example queries and autocompletion.

## Namespaces

| Prefix | Namespace | Content |
|---|---|---|
| `sibilo:` | `https://purl.expasy.org/sibils/rdf/ontology/` | SIBiLS ontology: classes and properties |
| `sibils:` | `https://purl.expasy.org/sibils/rdf/data/` | Publications and their parts: `sibils:27228136` (PMID), `sibils:PMC8063106` (PMCID) |
| `sibilc:` | `https://purl.expasy.org/sibils/rdf/concept/` | Concepts: `sibilc:MeSH_D013987` |
| `sibilt:` | `https://purl.expasy.org/sibils/rdf/scheme/` | Vocabularies (concept schemes): `sibilt:MeSH`, `sibilt:NCIt` |

The data also uses standard vocabularies: FaBiO (`http://purl.org/spar/fabio/`) and PRISM for the publications, DoCO and DEO for their structure, Web Annotation (`http://www.w3.org/ns/oa#`) for the annotations, SKOS for the concepts, and Dublin Core terms.

!!! note "Former ontology"
    The files [sibils-ontology.html](sibils-ontology.html) and [sibils-ontology.ttl](sibils-ontology.ttl) on this site describe the former version of the ontology (namespace `http://sibils.org/rdf#`, July 2023). The endpoint no longer uses it: queries written for it return no results. Use the [current ontology](https://sparql.sibils.org/rdf-ontology).

## Sending a query

Send the query in the `query` parameter (`GET`, or `POST` form) or as the body of a `POST` with `Content-Type: application/sparql-query`. The `Accept` header selects the result format, for example `application/sparql-results+json` or `text/csv`.

=== "curl"

    ```bash
    curl -G 'https://sparql.sibils.org/sparql' \
      -H 'Accept: application/sparql-results+json' \
      --data-urlencode 'query=PREFIX fabio: <http://purl.org/spar/fabio/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT * WHERE {
      ?pub a fabio:JournalArticle ; fabio:hasPubMedId ?pmid ;
           fabio:hasPublicationYear ?year ; dcterms:title ?title
    } LIMIT 3'
    ```

    To run a query saved in a file: `--data-urlencode 'query@RQ_001.sparql'`.

=== "Python"

    ```python
    import requests  # pip install requests

    query = """
    PREFIX fabio: <http://purl.org/spar/fabio/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT * WHERE {
      ?pub a fabio:JournalArticle ; fabio:hasPubMedId ?pmid ;
           fabio:hasPublicationYear ?year ; dcterms:title ?title
    } LIMIT 3
    """
    r = requests.get("https://sparql.sibils.org/sparql", params={"query": query},
                     headers={"Accept": "application/sparql-results+json"}, timeout=120)
    r.raise_for_status()
    for row in r.json()["results"]["bindings"]:
        print(row["pmid"]["value"], row["year"]["value"], row["title"]["value"])
    ```

## Examples

The three queries below were run on 22 November 2026.

### Number of publications by collection and type

```sparql title="RQ_001.sparql"
PREFIX fabio: <http://purl.org/spar/fabio/>
PREFIX sibilo: <https://purl.expasy.org/sibils/rdf/ontology/>

SELECT ?collection ?publi_class (count(*) as ?count)
WHERE {
  ?publi sibilo:inCollection ?collection .
  ?publi a ?publi_class .
}
GROUP BY ?collection ?publi_class
ORDER BY ?collection DESC(?count)
```

The first three rows of each collection:

| `collection` | `publi_class` | `count` |
|---|---|---|
| medline | `fabio:JournalArticle` | 219,005 |
| medline | `fabio:ReportDocument` | 40,898 |
| medline | `fabio:Letter` | 1,119 |
| pmc | `fabio:JournalArticle` | 39,410 |
| pmc | `fabio:BriefReport` | 638 |
| pmc | `fabio:ReviewArticle` | 276 |

### Annotations of a given publication

```sparql title="RQ_002.sparql"
PREFIX sibilo: <https://purl.expasy.org/sibils/rdf/ontology/>
PREFIX sibils: <https://purl.expasy.org/sibils/rdf/data/>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX prism: <http://prismstandard.org/namespaces/basic/2.0/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT
  (str(?doi_value) as ?doi)
  (str(?notation) as ?cpt_id)
  (str(?scheme_label) as ?scheme)
  ?start
  (str(?exact) as ?token)
  ?part
  ?part_type
WHERE {
  VALUES ?publi { sibils:PMC8063106 }
  ?publi prism:doi ?doi_value .
  ?publi sibilo:hasAnnotation ?a .
  ?a oa:hasBody ?cpt .
  ?cpt skos:notation ?notation .
  ?cpt skos:inScheme / rdfs:label ?scheme_label .

  ?a oa:hasTarget ?trg .
  ?trg oa:hasSource ?part .
  ?part a ?part_type .

  ?trg oa:hasSelector ?sel .
  ?sel oa:start ?start .
  ?sel oa:exact ?exact .
}
ORDER BY ?part ?start ?exact
LIMIT 100
```

First rows of the result, without the `doi` column (`10.3389/fcell.2021.647130` in every row):

| `cpt_id` | `scheme` | `start` | `token` | `part` | `part_type` |
|---|---|---|---|---|---|
| AGROVOC:c_3804 | Agrovoc | 0 | Immunofluorescence | `sibils:PMC8063106_sen_100` | `doco:Sentence` |
| DM:ViDM25 | Detection methods | 0 | Immunofluorescence | `sibils:PMC8063106_sen_100` | `doco:Sentence` |
| ECO:0000007 | ECO - Evidence & Conclusion Ontology | 0 | Immunofluorescence | `sibils:PMC8063106_sen_100` | `doco:Sentence` |
| NCBI_Model:10090 | NCBI Taxonomy Models | 4 | mouse | `sibils:PMC8063106_sen_101` | `doco:Sentence` |
| AGROVOC:c_55c1fd21 | Agrovoc | 10 | oocytes | `sibils:PMC8063106_sen_101` | `doco:Sentence` |
| MeSH:D009865 | MeSH | 10 | oocytes | `sibils:PMC8063106_sen_101` | `doco:Sentence` |

### Diseases mentioned near ticks

NCIt diseases and disorders mentioned less than 30 characters away from a mention of ticks (MeSH D013987), in the same sentence or element of a publication:

```sparql title="RQ_003.sparql"
PREFIX sibilo: <https://purl.expasy.org/sibils/rdf/ontology/>
PREFIX sibilc: <https://purl.expasy.org/sibils/rdf/concept/>
PREFIX sibilt: <https://purl.expasy.org/sibils/rdf/scheme/>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT
  ?publi
  ?part
  (str(?word) as ?token)
  ?pos
  (str(?word2) as ?token2)
  ?pos2
  (str(?label2) as ?disease)
WHERE {
  # mentions of ticks
  ?publi sibilo:hasAnnotation ?a .
  ?a oa:hasBody sibilc:MeSH_D013987 .
  ?a oa:hasTarget ?trg .
  ?trg oa:hasSelector ?sel .
  ?sel oa:exact ?word .
  ?sel oa:start ?pos .
  ?trg oa:hasSource ?part .

  # NCIt concepts below "Disease or Disorder" (C2991), in the same part
  ?publi sibilo:hasAnnotation ?a2 .
  ?a2 oa:hasTarget ?trg2 .
  ?trg2 oa:hasSelector ?sel2 .
  ?sel2 oa:exact ?word2 .
  ?sel2 oa:start ?pos2 .
  ?trg2 oa:hasSource ?part .
  ?a2 oa:hasBody ?cpt2 .
  ?cpt2 skos:inScheme sibilt:NCIt .
  ?cpt2 sibilo:more_specific_than+ sibilc:NCIt_C2991 .
  ?cpt2 skos:prefLabel ?label2 .

  FILTER (abs(?pos2 - ?pos) < 30 && ?a != ?a2)
}
ORDER BY ?publi ?part ?pos
```

This query can take up to a minute. First rows of the result:

| `publi` | `token` | `token2` | `disease` |
|---|---|---|---|
| `sibils:10556719` | ticks | Q fever | Q Fever |
| `sibils:12885882` | tick | CCHF | Congo-Crimean Hemorrhagic Fever |
| `sibils:1312282` | tick | NS3 | Noonan Syndrome 3 |
| `sibils:15808943` | tick | fungal infection | Fungal Infection |

Annotations are not disambiguated by context, so some matches are wrong. In the third row, *NS3* is the nonstructural protein 3 of orbiviruses ("Comparison of the nonstructural protein, NS3, of tick-borne and insect-borne orbiviruses."), not Noonan syndrome 3.
