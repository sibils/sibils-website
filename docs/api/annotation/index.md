---
description: >-
  Annotate any text with the SIBiLS vocabularies, list the vocabularies and look up their concepts
  with the annotation and vocabularies (OTF) API.
---

# Annotation and vocabularies API

The annotation and vocabularies API, also called OTF ("on the fly"), annotates any text with the vocabularies that SIBiLS uses to annotate its collections, and gives access to the concepts of these vocabularies.
{ .lead }

<div class="facts" markdown>

Base URL
:   `https://biodiversitypmc.sibils.org/api/otf`

Interactive reference
:   [Swagger UI](https://biodiversitypmc.sibils.org/api/otf/) · [on this site](reference.md)

OpenAPI description
:   [biodiversitypmc.sibils.org/api/otf/openapi.json](https://biodiversitypmc.sibils.org/api/otf/openapi.json) (OpenAPI 3.1)

Live demo
:   [biodiversitypmc.sibils.org/api/otf/live/](https://biodiversitypmc.sibils.org/api/otf/live/)

Authentication
:   None

Examples checked
:   22 November 2026, SIBiLS release 5.1.5.10; versions and results change when the vocabularies are updated.

</div>

First request:

```bash
curl -G "https://biodiversitypmc.sibils.org/api/otf/annotations" \
  --data-urlencode "query=BRAF V600E mutations in melanoma treated with vemurafenib"
```

Use it to:

- annotate your own texts the same way as the documents of the SIBiLS collections, with the same vocabularies, identifiers and annotation fields as the [fetch API](../biodiversitypmc/fetch.md);
- list the vocabularies and their versions;
- look up a concept: preferred term, synonyms and link to its source database;
- find the concepts of a vocabulary from a few characters (autocomplete).

The vocabularies are described on the [Vocabularies](../../vocabularies.md) page. To look up the vocabularies and their concepts without code, use the <!-- sibils:terminology-browser -->.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/annotations` | Annotate a short text given in the `query` parameter |
| `POST` | `/annotations` | Annotate a text sent as the request body |
| `POST` | `/annotations/batch` | Annotate several texts in one request |
| `GET` | `/terminologies` | List the vocabularies with their version and description |
| `GET` | `/concept` | Get a concept: preferred term, synonyms, URL and vocabulary |
| `GET` | `/concept/url` | Get the URL of a concept in its source database, or redirect to it |
| `POST` | `/concept/terms/batch` | Get the preferred term, and optionally the synonyms, of several concepts |
| `GET` | `/concept/autocomplete` | Find concepts of one vocabulary from an identifier or the beginning of a term |
| `POST` | `/concept/preferred_term/batch` | Deprecated, use `/concept/terms/batch` |
| `GET` | `/metrics` | Service metrics in Prometheus text format |

A concept is identified by two values: its vocabulary, `concept_source` (the `source` query parameter), and its identifier in that vocabulary, `concept_id` (the `id` query parameter). The `concept_source` values are the keys returned by [`/terminologies`](#list-the-vocabularies) and are listed on the [Vocabularies](../../vocabularies.md) page.

## Annotate a text

### `GET /annotations`

For short texts, sent in the URL.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | yes | | Text to annotate |
| `split` | boolean | no | `true` | Split the text into sentences |

=== "curl"

    ```bash
    curl -G "https://biodiversitypmc.sibils.org/api/otf/annotations" \
      --data-urlencode "query=BRAF V600E mutations in melanoma treated with vemurafenib"
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    BASE = "https://biodiversitypmc.sibils.org/api/otf"
    text = "BRAF V600E mutations in melanoma treated with vemurafenib"

    r = requests.get(f"{BASE}/annotations", params={"query": text}, timeout=60)
    r.raise_for_status()
    result = r.json()["result"]
    for a in result["annotations"]:
        sentence = result["sentences"][a["sentence_number"]]
        span = sentence[a["start_index"]:a["end_index"]]
        print(span, a["concept_source"], a["concept_id"], a["preferred_term"])
    ```

The response contains the sentences of the text and the annotations found in them. The first of the 12 annotations is shown:

```json
{
  "sibils_version": "5.1.5.10",
  "success": true,
  "error": "",
  "warning": "",
  "result": {
    "annotations": [
      {
        "type": "disease",
        "concept_source": "ncit",
        "version": "26.02d",
        "concept_id": "C98342",
        "concept_form": "BRAF V600E",
        "preferred_term": "BRAF NP_004324.2:p.V600E",
        "nature": "synonym",
        "field": "annotation_str",
        "sentence_number": 0,
        "start_index": 0,
        "end_index": 10,
        "concept_length": 10,
        "evidence_code": "ECO_0000366",
        "provenance": "SIBILS",
        "provider": "SIB",
        "score": 0.5,
        "attributes": null,
        "concept_url": "https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&code=C98342"
      }
    ],
    "sentences": [
      "BRAF V600E mutations in melanoma treated with vemurafenib"
    ]
  }
}
```

All annotations of this example, sorted by position:

| Text | `concept_source` | `concept_id` | `preferred_term` | `nature` |
|------|------------------|--------------|------------------|----------|
| BRAF V600E | `ncit` | C98342 | BRAF NP_004324.2:p.V600E | synonym |
| BRAF | `nextprot` | NX_P15056 | BRAF | pref_term |
| BRAF | `uniprot_swissprot` | Q3USE9 | B-raf | pref_term |
| mutations | `covocbiomed` | BMV_95 | Mutation | synonym |
| melanoma | `mesh` | D008545 | Melanoma | pref_term |
| melanoma | `ncit` | C3224 | Melanoma | pref_term |
| melanoma | `agrovoc` | c_4713 | melanoma | pref_term |
| vemurafenib | `atc` | L01EC01 | vemurafenib | pref_term |
| vemurafenib | `chebi` | CHEBI:63637 | vemurafenib | pref_term |
| vemurafenib | `drugbank` | DB08881 | Vemurafenib | pref_term |
| vemurafenib | `mesh` | D000077484 | Vemurafenib | pref_term |
| vemurafenib | `pubchemmesh` | 42611257 | Vemurafenib | pref_term |

### `POST /annotations`

For longer texts, send the text as the request body, either as plain text or as a JSON string. Pass `split` in the query string.

=== "curl (plain text)"

    ```bash
    curl -X POST "https://biodiversitypmc.sibils.org/api/otf/annotations?split=true" \
      -H "Content-Type: text/plain" \
      --data-binary "BRAF V600E mutations in melanoma. Patients were treated with vemurafenib."
    ```

=== "curl (JSON string)"

    ```bash
    curl -X POST "https://biodiversitypmc.sibils.org/api/otf/annotations" \
      -H "Content-Type: application/json" \
      -d '"BRAF V600E mutations in melanoma. Patients were treated with vemurafenib."'
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    BASE = "https://biodiversitypmc.sibils.org/api/otf"
    text = "BRAF V600E mutations in melanoma. Patients were treated with vemurafenib."

    # plain text body
    r = requests.post(f"{BASE}/annotations", data=text.encode("utf-8"),
                      headers={"Content-Type": "text/plain"}, timeout=60)
    # or JSON string body, here without sentence splitting
    r = requests.post(f"{BASE}/annotations", json=text, params={"split": "false"}, timeout=60)
    r.raise_for_status()
    print(r.json()["result"]["sentences"])
    ```

With `split=true` (the default) this text gives two sentences, and the annotation of *vemurafenib* has `sentence_number` 1, `start_index` 27 and `end_index` 38, relative to the second sentence. With `split=false` the whole text is one sentence and the same annotation has offsets 61 and 72.

!!! warning "Always set the content type"
    Send the body with `Content-Type: text/plain` (curl `--data-binary`) or `Content-Type: application/json` (a JSON string). A form-encoded body is accepted but annotated as raw text: `curl -d 'query=...'` without a content type, or `requests.post(..., data={"query": ...})`, annotates the string `query=BRAF+V600E+...`.

With `Content-Type: application/json`, the body must be a JSON string, in double quotes. Unquoted text or a JSON object such as `{"query": "..."}` is rejected with HTTP 422.

### `POST /annotations/batch`

Annotates several texts in one request. Each item needs `text` and `split`; `split` has no default here.

=== "curl"

    ```bash
    curl -X POST "https://biodiversitypmc.sibils.org/api/otf/annotations/batch" \
      -H "Content-Type: application/json" \
      -d '{"requests": [{"text": "BRAF V600E mutations in melanoma.", "split": true},
                        {"text": "Rhinolophus and Pangolin", "split": true}]}'
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    BASE = "https://biodiversitypmc.sibils.org/api/otf"
    batch = {"requests": [
        {"text": "BRAF V600E mutations in melanoma.", "split": True},
        {"text": "Rhinolophus and Pangolin", "split": True},
    ]}
    r = requests.post(f"{BASE}/annotations/batch", json=batch, timeout=60)
    r.raise_for_status()
    for item in r.json()["results"]:
        print(len(item["annotations"]), "annotations in", item["sentences"])
    ```

`results` has one item per request, in the same order. Each item has the same `annotations` and `sentences` fields as `result` in `/annotations`. Annotations of the second text:

| Text | `concept_source` | `concept_id` | `preferred_term` | `nature` |
|------|------------------|--------------|------------------|----------|
| Rhinolophus | `ott` | 756634 | Rhinolophus | pref_term |
| Rhinolophus | `ncbitaxon_full` | 49442 | Rhinolophus | pref_term |
| Rhinolophus | `covocorganism` | SP_20 | Rhinolophus macrotis | synonym |
| Rhinolophus | `mesh` | D002685 | Chiroptera | synonym |
| Pangolin | `mesh` | D000086642 | Pangolins | synonym |
| Pangolin | `ott` | 644247 | Manis | synonym |
| Pangolin | `covocorganism` | SP_14 | Manidae | synonym |

### Annotation fields

| Field | Description |
|-------|-------------|
| `type` | Entity type of the vocabulary, for example `disease`, `drug`, `species` |
| `concept_source` | Vocabulary of the concept (`name_termino` in `/terminologies`) |
| `version` | Version of the vocabulary |
| `concept_id` | Identifier of the concept in the vocabulary |
| `concept_form` | Text that was matched |
| `preferred_term` | Preferred term of the concept |
| `nature` | `pref_term` if the preferred term matched, `synonym` if a synonym matched, `related-synonym` if a related synonym matched (as in GO and Uberon). Other values can occur |
| `field` | `annotation_str` for texts sent to this API; in documents returned by the fetch API, the document field, for example `title` |
| `sentence_number` | Index of the sentence in the `sentences` list, starting at 0 |
| `start_index`, `end_index` | Character offsets of the match in that sentence; `end_index` is exclusive, so `sentence[start_index:end_index]` equals `concept_form` |
| `concept_length` | Length of the match |
| `evidence_code` | Evidence & Conclusion Ontology code, for example `ECO_0000366` (evidence based on logical inference from automatic annotation used in automatic assertion) |
| `provenance`, `provider` | Origin of the annotation, for example `SIBILS` and `SIB` |
| `score` | Score of the annotation |
| `attributes` | Additional attributes, or `null` |
| `concept_url` | Experimental, only in this API. Page of the concept in its source database, or `null` when the vocabulary provides none |

The fields are those of the [fetch API](../biodiversitypmc/fetch.md#json-default), with one difference: here `sentence_number` is a list index (`result["sentences"][sentence_number]`), while in fetch output it starts at 1 and must be matched to `sentences[].sentence_number`.

### How texts are matched

- The text is matched against the preferred terms and synonyms of all vocabularies.
- One span can be annotated with several vocabularies (*melanoma* with MeSH, NCIt and AGROVOC), and annotations can overlap (*BRAF V600E* and *BRAF*).
- Matches are not disambiguated by context. A synonym can point to a broader concept: *Rhinolophus* is also annotated with MeSH D002685 *Chiroptera*. Filter on `concept_source` or `type` to keep the vocabularies you need.
- Annotations are not returned in text order. Sort them on `sentence_number`, then `start_index`.

## List the vocabularies

`GET /terminologies` returns all vocabularies, keyed by `concept_source`. The [Vocabularies](../../vocabularies.md) page is generated from this endpoint.

=== "curl"

    ```bash
    curl "https://biodiversitypmc.sibils.org/api/otf/terminologies"
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    r = requests.get("https://biodiversitypmc.sibils.org/api/otf/terminologies", timeout=60)
    r.raise_for_status()
    data = r.json()
    print("SIBiLS version:", data["sibils_version"])
    for source, t in sorted(data["terminologies"].items()):
        print(source, t["type"], t["version"], t["label"])
    ```

One entry of the response:

```json
"mesh": {
  "name_termino": "mesh",
  "label": "MeSH",
  "code": "mesh",
  "type": "mesh",
  "version": "2026",
  "date": "2026-03-21",
  "file_creation": "2026-05-04",
  "url": "https://www.nlm.nih.gov/databases/download/mesh.html",
  "description": "The Medical Subject Headings (MeSH), provided by the U.S. National Library of Medicine (NLM), is a controlled vocabulary thesaurus used for indexing articles for PubMed. In comparison with specialzed ontologies like the NCIt, MeSH is less granular and easily identified by Natural Language Processing thanks to synonyms.",
  "category": "Health",
  "subcategory": null
}
```

Fields of each entry:

| Field | Description |
|-------|-------------|
| `name_termino` | Vocabulary identifier: `concept_source` in annotations, `source` in the concept endpoints |
| `label` | Display name |
| `code` | Short code, shared by related vocabularies (for example `go` for the three GO aspects, `cov` for COVoc) |
| `type` | Entity type, copied to `type` in annotations |
| `version` | Version of the vocabulary, copied to `version` in annotations |
| `date` | Date SIBiLS took this version of the vocabulary from its source (YYYY-MM-DD); not the release date of the vocabulary |
| `file_creation` | Date the SIBiLS dictionary file was generated from the vocabulary (YYYY-MM-DD) |
| `url` | Home or download page of the vocabulary, or `null` |
| `description` | Description of the vocabulary, or `null` |
| `category`, `subcategory` | Grouping used on the Vocabularies page; `subcategory` can be `null` |

## Look up concepts

### `GET /concept`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | string | yes | Vocabulary (`concept_source`) |
| `id` | string | yes | Concept identifier, as written in the vocabulary |

Identifiers keep the form used by each vocabulary, for example `D008545` (MeSH), `CHEBI:63637` (ChEBI), `ECO:0000366` (ECO), `9606` (NCBI Taxonomy).

```bash
curl "https://biodiversitypmc.sibils.org/api/otf/concept?source=mesh&id=D008545"
```

Response:

```json
{
  "sibils_version": "5.1.5.10",
  "success": true,
  "error": "",
  "warning": "",
  "concept_id": "D008545",
  "url": "https://www.ncbi.nlm.nih.gov/mesh/?term=D008545",
  "terminology": {
    "name_termino": "mesh",
    "label": "MeSH",
    "code": "mesh",
    "type": "mesh",
    "version": "2026",
    "date": "2026-03-21",
    "file_creation": "2026-05-04",
    "url": "https://www.nlm.nih.gov/databases/download/mesh.html",
    "description": "The Medical Subject Headings (MeSH), provided by the U.S. National Library of Medicine (NLM), is a controlled vocabulary thesaurus used for indexing articles for PubMed. In comparison with specialzed ontologies like the NCIt, MeSH is less granular and easily identified by Natural Language Processing thanks to synonyms.",
    "category": "Health",
    "subcategory": null
  },
  "preferred_term": {"termino_term": "Melanoma", "nature": "pref_term", "evidence_code": "ECO_0000366", "provenance": "SIBILS"},
  "synonyms": [
    {"termino_term": "Melanomas", "nature": "synonym", "evidence_code": "ECO_0000366", "provenance": "SIBILS"},
    {"termino_term": "Malignant Melanoma", "nature": "synonym", "evidence_code": "ECO_0000366", "provenance": "SIBILS"},
    {"termino_term": "Malignant Melanomas", "nature": "synonym", "evidence_code": "ECO_0000366", "provenance": "SIBILS"},
    {"termino_term": "Melanoma, Malignant", "nature": "synonym", "evidence_code": "ECO_0000366", "provenance": "SIBILS"},
    {"termino_term": "Melanomas, Malignant", "nature": "synonym", "evidence_code": "ECO_0000366", "provenance": "SIBILS"}
  ]
}
```

`url` is `null` when the vocabulary provides no page for its concepts, for example COVoc.

### `GET /concept/url`

Same `source` and `id` parameters as `/concept`, plus `redirect`:

- `redirect=1` (default): HTTP 307 redirect to the page of the concept, with an empty body, for use in links, for example <https://biodiversitypmc.sibils.org/api/otf/concept/url?source=mesh&id=D008545>;
- `redirect=0`: JSON response with the URL.

```bash
curl "https://biodiversitypmc.sibils.org/api/otf/concept/url?source=mesh&id=D008545&redirect=0"
```

Response:

```json
{"sibils_version": "5.1.5.10", "success": true, "error": "", "warning": "", "url": "https://www.ncbi.nlm.nih.gov/mesh/?term=D008545"}
```

The endpoint returns HTTP 404 when the vocabulary is unknown or provides no concept page (for example COVoc). It does not check that the identifier exists: for an unknown identifier in a known vocabulary, such as `source=mesh&id=D999999999`, it returns a URL built from the vocabulary's pattern. Use [`/concept`](#get-concept) to check that a concept exists.

### `POST /concept/terms/batch`

Returns the preferred term, and the synonyms unless `include_synonyms` is `false`, of several concepts. `terms` is in the order of `concepts`; an unknown concept gives `null`.

=== "curl"

    ```bash
    curl -X POST "https://biodiversitypmc.sibils.org/api/otf/concept/terms/batch" \
      -H "Content-Type: application/json" \
      -d '{"concepts": [{"concept_source": "mesh", "concept_id": "D008545"},
                        {"concept_source": "ott", "concept_id": "756634"}],
           "include_synonyms": false}'
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    concepts = [
        {"concept_source": "mesh", "concept_id": "D008545"},
        {"concept_source": "ott", "concept_id": "756634"},
    ]
    r = requests.post("https://biodiversitypmc.sibils.org/api/otf/concept/terms/batch",
                      json={"concepts": concepts, "include_synonyms": False}, timeout=60)
    r.raise_for_status()
    for c, item in zip(concepts, r.json()["terms"]):
        print(c["concept_source"], c["concept_id"], item and item["preferred_term"]["termino_term"])
    ```

Response:

```json
{
  "sibils_version": "5.1.5.10",
  "success": true,
  "error": "",
  "warning": "",
  "terms": [
    {"preferred_term": {"termino_term": "Melanoma", "nature": "pref_term", "evidence_code": "ECO_0000366", "provenance": "SIBILS"}, "synonyms": []},
    {"preferred_term": {"termino_term": "Rhinolophus", "nature": "pref_term", "evidence_code": "ECO_0000366", "provenance": "SIBILS"}, "synonyms": []}
  ]
}
```

### `GET /concept/autocomplete`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | string | yes | Vocabulary (`concept_source`) |
| `text` | string | yes | Concept identifier, or the beginning of a term |

=== "curl"

    ```bash
    curl "https://biodiversitypmc.sibils.org/api/otf/concept/autocomplete?source=mesh&text=melan"
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    r = requests.get("https://biodiversitypmc.sibils.org/api/otf/concept/autocomplete",
                     params={"source": "mesh", "text": "melan"}, timeout=60)
    r.raise_for_status()
    print([(x["concept_id"], x["pref_term"]) for x in r.json()["results"]])
    ```

`text=melan` returns 10 MeSH concepts, starting with *Melanins* (D008543), *Melanoma* (D008545), *Melanosis* (D008548) and *Melanesia* (D008542).

- An identifier must match exactly: `text=D008545` returns *Melanoma* only.
- Terms are compared with the preferred terms and synonyms, ignoring case. `text=malignant melanoma` returns *Melanoma* (D008545) first, which has the synonym *Malignant Melanoma*.
- Results can include approximate matches: `text=pangolin` returns *Pangolins* and *Lanolin*.
- At most 10 concepts are returned.
- An unknown `source` returns an empty `results` list.

First result of `source=ncbitaxon_full&text=homo sap`:

```json
{
  "name_termino": "ncbitaxon_full",
  "type": "species",
  "version": "2026-05-04",
  "concept_id": "9606",
  "pref_term": "Homo sapiens",
  "termino_term": "Homo sapiens",
  "nature": "pref_term",
  "evidence_code": "ECO_0000366",
  "provenance": "SIBILS",
  "attributes": null,
  "concept_url": "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606&lvl=3"
}
```

### `POST /concept/preferred_term/batch`

Deprecated: use [`/concept/terms/batch`](#post-concepttermsbatch). It takes the same `concepts` list and returns only the preferred terms, for example `"preferred_terms": ["Melanoma", "Rhinolophus", null]`.

## Responses and errors {#response-format}

All endpoints return JSON, except `/metrics` (Prometheus text) and `/concept/url` with `redirect=1` (HTTP 307 redirect).

Every JSON response starts with these fields, followed by the result of the endpoint:

| Field | Description |
|-------|-------------|
| `sibils_version` | Version of SIBiLS, for example `5.1.5.10` |
| `success` | `true` if the request succeeded |
| `error` | Error message, empty on success |
| `warning` | Warning message, usually empty |

Errors use the same fields with `success` set to `false`. A missing or invalid parameter returns HTTP 422 with a message such as `RequestValidationError: query/query: Field required` (and `sibils_version` `1.0.0` in this case). An unknown concept returns HTTP 404:

```json
{"sibils_version": "5.1.5.10", "success": false, "error": "Concept mesh:D999999999 not found", "warning": ""}
```

## Metrics

`GET /metrics` returns request counters and sizes in the Prometheus text format, for monitoring.

## OpenAPI reference

The complete list of parameters and schemas is in the [reference](reference.md), rendered from the OpenAPI description, and in the service's own [Swagger UI](https://biodiversitypmc.sibils.org/api/otf/).
