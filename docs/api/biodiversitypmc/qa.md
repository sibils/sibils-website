---
description: >-
  The SIBiLS Question-Answering API answers questions written in natural language from MEDLINE,
  PMC and Plazi, and returns the documents each answer is based on.
---

# Question-Answering API

The Question-Answering (QA) API takes a question written in natural language and returns short answers, using documents from three SIBiLS collections: MEDLINE, PMC and Plazi. Each answer comes with the documents it is based on.
{ .lead }

<div class="facts" markdown>

Base URL
:   `https://qa.sibils.org/api`

Interactive reference
:   [Swagger UI](https://qa.sibils.org/api/) · [on this site](qa_reference.md)

OpenAPI description
:   [qa.sibils.org/api/openapi.json](https://qa.sibils.org/api/openapi.json) (OpenAPI 3.1)

Web application
:   [qa.sibils.org](https://qa.sibils.org/), described in [Question-Answering](../../qa/index.md)

Authentication
:   None

Examples checked
:   22 November 2026. Answers change with the collections and the models.

</div>

!!! note "The former endpoint has moved"
    `https://biodiversitypmc.sibils.org/api/QA` now returns HTTP 404. Use `https://qa.sibils.org/api/QA` with the same `q`, `col` and `n` parameters, or the recommended [`POST /qa`](#post-qa) endpoint. See [Migrating from the former endpoint](#migrating-from-the-former-endpoint).

First request:

```bash
curl -X POST https://qa.sibils.org/api/qa \
  -H 'Content-Type: application/json' \
  -d '{"question": "What diseases are transmitted by ticks?"}'
```

## Endpoints

All paths are relative to `https://qa.sibils.org/api`.

| Method | Path | Purpose |
|---|---|---|
| `POST` | [`/qa`](#post-qa) | Answer a question across the three collections (recommended) |
| `POST` | [`/qa/multi`](#post-qa-multi) | Same as `/qa`, without the response cache |
| `GET` | [`/QA`](#get-qa-legacy) | Answer a question in one collection, or in all three merged into one list; compatible with the former endpoint |
| `POST` | [`/batch`](#post-batch) | Answer several questions in one request (extractive mode) |
| `GET` | [`/fetch`](#get-fetch) | Proxy to the SIBiLS fetch API |
| `GET` | [`/health`](#service-status) | Service status and loaded models |
| `GET` | [`/retrieval-info`](#service-status) | Description of the retrieval components |

## How it works

The service uses retrieval-augmented generation (RAG): it first searches the literature for documents relevant to the question, then builds the answer from those documents only. Each answer can therefore be checked against its sources.

1. **Retrieval.** The question is sent as a keyword search (BM25) to the SIBiLS search engine, in each collection. With `retrieval=dense`, the service also runs a semantic search in a local vector index (FAISS, `sentence-transformers/all-MiniLM-L6-v2` embeddings, 2,398 documents according to [`GET /retrieval-info`](#service-status) on 22 November 2026). It merges both result lists with reciprocal rank fusion, then reorders them with a cross-encoder reranker.
2. **Filtering.** Only the most relevant documents are kept (`final_n`, 5 by default).
3. **Answer.** In `generative` mode, a large language model writes a short answer from the kept documents. In `extractive` mode, a BioBERT model copies the passage of a document that best answers the question and gives a confidence score.

[`GET /health`](#service-status) reports the models currently loaded. On 22 November 2026, these were Qwen3-8B (`Qwen/Qwen3-8B-FP8`) for generative mode and BioBERT (`ktrapeznikov/biobert_v1.1_pubmed_squad_v2`) for extractive mode.

Generative answers are written by a language model: check them against the documents listed in `docs`.

### Answer modes

| `mode` | Answer | `answer_score` |
|---|---|---|
| `generative` | A few sentences written by the language model from several documents. One answer per collection. | `null` |
| `extractive` | A span of text copied verbatim from one document. Its position in `doc_text` is given by `snippet_start` and `snippet_end`. Up to one answer per kept document. | BioBERT confidence, from 0 to 1 |
| `hybrid` | `POST /qa` and `/qa/multi`: legacy alias for `generative` with `dense` retrieval. `GET /QA` accepts it but currently returns no answers. | |

### Retrieval strategies

| `retrieval` | Method | Suited for |
|---|---|---|
| `sparse` | Keyword search (BM25) with the SIBiLS search engine | Exact terms, gene and drug names, acronyms |
| `dense` | Keyword search and semantic search, merged and reranked | Conceptual questions, synonyms, paraphrases |
| `rag` | Legacy alias for `dense` | |

The web application uses `sparse` retrieval with extractive mode and recommends `dense` retrieval with generative mode.

## Collections

| `col` | Collection | `docid` format |
|---|---|---|
| `medline` | MEDLINE abstracts | PMID, for example `22662624` |
| `pmc` | PubMed Central full-text articles, including the PMC+ subset | PMCID, for example `PMC5548484`; a DOI for PMC+ articles that are not in PMC, for example `10.1163/187529274X00113` |
| `plazi` | Plazi taxonomic treatments | Plazi treatment identifier, for example `03B187F0FFF5FFF10B4DA185FBE2D46C` |

The service supports `medline`, `pmc` and `plazi`. `POST /qa` always searches the three collections and returns one result block per collection. `GET /QA` and `POST /batch` accept `col` to search a single collection. `GET /QA` rejects other collections. `POST /batch` does not validate `col`: `suppdata` and `zenodo` also return answers, although the service does not list them as supported, and an unknown value returns HTTP 500 with the plain-text body `Internal Server Error`.

To retrieve a whole document from an answer, pass its `docid` and `doc_source` to the [fetch API](fetch.md).

## `POST /qa` {#post-qa}

Recommended endpoint. It answers one question in MEDLINE, PMC and Plazi, and returns the three result blocks ranked by relevance.

### Request body {#post-qa-request}

A JSON object (`Content-Type: application/json`):

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `question` | string | yes | | Question in natural language |
| `mode` | string | no | `generative` | `generative` or `extractive`, see [Answer modes](#answer-modes) |
| `retrieval` | string | no | `sparse` | `sparse` or `dense`, see [Retrieval strategies](#retrieval-strategies) |
| `retrieval_n` | integer | no | `10` | Documents retrieved from each collection before filtering, from 1 to 100. More documents can improve recall and increase processing time |
| `final_n` | integer | no | `5` | Documents kept after filtering and used to build the answers |
| `doc_refs` | array of strings | no | none | Answer from these documents instead of searching, see [Asking about specific documents](#asking-about-specific-documents) |
| `debug` | boolean | no | `false` | Add internal diagnostics in `debug_info` |
| `include_documents` | boolean | no | `false` | Meant to add the full document text in `doc_text`; currently `doc_text` is always returned, whatever this value |

`POST /qa` has no `col` field. To search a single collection, use [`GET /QA`](#get-qa-legacy) or [`POST /batch`](#post-batch).

### Example {#post-qa-example}

=== "curl"

    ```bash
    curl -X POST https://qa.sibils.org/api/qa \
      -H 'Content-Type: application/json' \
      -d '{"question": "What diseases are transmitted by ticks?"}'
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    response = requests.post(
        "https://qa.sibils.org/api/qa",
        json={"question": "What diseases are transmitted by ticks?"},
        timeout=120,
    )
    response.raise_for_status()
    result = response.json()

    for block in result["collection_results"]:
        print(block["rank"], block["collection"])
        for answer in block["answers"]:
            print("  ", answer["answer"])
            for doc in answer["docs"]:
                print("     ", doc["doc_source"], doc["docid"])
    ```

With the default settings (generative mode, sparse retrieval), this request took 3 to 7 seconds in our tests. Extractive mode is faster.

To get extractive answers with dense retrieval:

```json
{"question": "Which ticks transmit Lyme disease?", "mode": "extractive", "retrieval": "dense"}
```

On 22 November 2026, this request returned 26 documents and three extractive answers in each collection. With dense retrieval, some questions return no result at all: see [Errors](#errors).

### Response {#post-qa-response}

Excerpt of the response to the example above. Two of the three collection blocks are shown, and texts are shortened.

```json
{
  "question": "What diseases are transmitted by ticks?",
  "collection_results": [
    {
      "collection": "plazi",
      "rank": 1,
      "answers": [
        {
          "answer": "Based on the provided documents, several diseases are transmitted by ticks. These include bovine theileriasis, which is transmitted by *Haemaphysalis...",
          "answer_score": null,
          "docs": [
            {
              "docid": "03B187F0FFF5FFF10B4DA185FBE2D46C",
              "doc_source": "plazi",
              "doc_retrieval_score": 0.564,
              "doc_text": "Haemaphysalis longicornis Neumann 1901. The scrub tick, Haemaphysalis longicornis , a live...",
              "snippet_start": null,
              "snippet_end": null
            }
          ]
        }
      ],
      "mode_used": "generative",
      "debug_info": null
    },
    {
      "collection": "medline",
      "rank": 2,
      "answers": [
        {
          "answer": "Based on the provided documents, ticks transmit several diseases including Lyme disease, Rocky Mountain spotted fever, tick-borne encephalitis, and bo...",
          "answer_score": null,
          "docs": [
            {
              "docid": "3037808",
              "doc_source": "medline",
              "doc_retrieval_score": 0.507,
              "doc_text": "[Neurologic diseases transmitted by ticks].. Apart from causing various dermatological dis...",
              "snippet_start": null,
              "snippet_end": null
            }
          ]
        }
      ],
      "mode_used": "generative",
      "debug_info": null
    }
  ],
  "mode_used": "generative",
  "ndocs_retrieved": 30,
  "model": "qwen3-8b-fp8",
  "pipeline_time": 6.707,
  "unresolved_refs": null
}
```

Response fields:

| Field | Description |
|---|---|
| `question` | The question as submitted |
| `collection_results` | One block per collection, best first. A collection is left out when no document was retrieved from it |
| `collection_results[].collection` | `medline`, `pmc` or `plazi` |
| `collection_results[].rank` | `1` for the collection whose best document has the highest score |
| `collection_results[].answers` | Answers for this collection, best first (see the table below). Can be empty |
| `collection_results[].mode_used` | Mode used for this collection |
| `collection_results[].debug_info` | Diagnostics when `debug` is `true`, otherwise `null` |
| `mode_used` | Mode used, after resolving legacy aliases |
| `ndocs_retrieved` | Documents retrieved over all collections, before filtering |
| `model` | `biobert` in extractive mode, or the name of the generative model |
| `pipeline_time` | Processing time in seconds |
| `unresolved_refs` | Entries of `doc_refs` that were not found, otherwise `null` |

Each answer contains:

| Field | Description |
|---|---|
| `answer` | Answer text |
| `answer_score` | Extractive mode: confidence from 0 to 1. Generative mode: `null` |
| `docs` | Documents the answer is based on. Extractive mode: the document the span was copied from. Generative mode: the documents used for the answer |
| `docs[].docid` | PMID, PMCID (or a DOI for PMC+ articles) or Plazi treatment identifier |
| `docs[].doc_source` | Collection of the document |
| `docs[].doc_retrieval_score` | Relevance of the document to the question; higher is more relevant. Compare scores only within one response |
| `docs[].doc_text` | Text of the document, or of the passage the answer comes from (for example the title and abstract of a MEDLINE citation, or part of a Plazi treatment). In generative mode, limited to 800 characters |
| `docs[].snippet_start`, `docs[].snippet_end` | Extractive mode: character offsets of the answer in `doc_text`. Generative mode: `null` |

### Caching

Identical requests (same question, mode and retrieval parameters) received within 120 seconds are answered from a cache. Use [`POST /qa/multi`](#post-qa-multi) to force a new computation.

### Asking about specific documents

Set `doc_refs` to a list of PMIDs, PMCIDs, DOIs or title fragments to skip the search and answer from those documents only. The documents are grouped by collection and answered per collection.

```bash
curl -X POST https://qa.sibils.org/api/qa \
  -H 'Content-Type: application/json' \
  -d '{"question": "What diseases are transmitted by ticks?",
       "mode": "extractive",
       "doc_refs": ["22662624", "PMC5548484"]}'
```

!!! warning "Check the returned identifiers"
    References are looked up in SIBiLS. A reference that does not exist can be matched to an unrelated document instead of being listed in `unresolved_refs`. Compare the `docid` values in the response with the references you sent.

With `doc_refs`, `doc_retrieval_score` uses another scale than in a normal search (values above 10 were observed).

## `POST /qa/multi` {#post-qa-multi}

Same request body and same response as [`POST /qa`](#post-qa), but the [cache](#caching) is not used: each call runs the whole pipeline, including a new generation in generative mode. Prefer `POST /qa` unless you need a fresh result.

## `POST /batch` {#post-batch}

Answers several questions in one request. Retrieval runs in parallel for all questions. This endpoint always uses extractive mode; for generative answers, call [`POST /qa`](#post-qa) once per question.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `questions` | array of strings | yes | | Questions, at least one |
| `col` | string | no | all | `medline`, `pmc` or `plazi`. Not validated: `suppdata` and `zenodo` also return answers, and other values return HTTP 500, see [Collections](#collections) |
| `retrieval_n` | integer | no | `10` | Documents retrieved per question, from 1 to 100 |
| `final_n` | integer | no | `5` | Documents kept per question after filtering |

```bash
curl -X POST https://qa.sibils.org/api/batch \
  -H 'Content-Type: application/json' \
  -d '{"questions": ["What diseases are transmitted by ticks?",
                     "What parasites are treated with ivermectin?"],
       "col": "medline",
       "retrieval_n": 5}'
```

The response contains one result per question, in the order of `questions`, and their number in `count`. Each result has the same format as the [`GET /QA` response](#get-qa-response), without the `debug_info` and `documents` fields. Excerpt (first answer of each result, texts shortened):

```json
{
  "results": [
    {
      "sibils_version": "biomoqa-2.0",
      "success": true,
      "error": "",
      "question": "What diseases are transmitted by ticks?",
      "collection": "medline",
      "model": "biobert",
      "ndocs_requested": 5,
      "ndocs_returned_by_SIBiLS": 5,
      "answers": [
        {
          "answer": "rickettsial pathogens and endosymbionts",
          "answer_score": 0.7987,
          "docs": [
            {
              "docid": "39914231",
              "doc_source": "medline",
              "doc_retrieval_score": 0.472,
              "doc_text": "Exploring endosymbionts and pathogens in Rhipicephalus sangu...",
              "snippet_start": 255,
              "snippet_end": 294
            }
          ]
        }
      ],
      "mode_used": "extractive",
      "pipeline_time": 1.914,
      "transformed_query": null
    },
    {
      "sibils_version": "biomoqa-2.0",
      "success": true,
      "error": "",
      "question": "What parasites are treated with ivermectin?",
      "collection": "medline",
      "model": "biobert",
      "ndocs_requested": 5,
      "ndocs_returned_by_SIBiLS": 5,
      "answers": [
        {
          "answer": "O. volvulus",
          "answer_score": 0.3202,
          "docs": [
            {
              "docid": "17989786",
              "doc_source": "medline",
              "doc_retrieval_score": 0.741,
              "doc_text": "ears, and recently there have been reports of poor parasitol...",
              "snippet_start": 341,
              "snippet_end": 352
            }
          ]
        }
      ],
      "mode_used": "extractive",
      "pipeline_time": 3.401,
      "transformed_query": null
    }
  ],
  "count": 2
}
```

## Service status

`GET /health` returns the service status and the loaded models. `ready` is `false` while the models are loading.

```bash
curl https://qa.sibils.org/api/health
```

Response:

```json
{
  "status": "healthy",
  "features": {
    "hybrid_retrieval": true,
    "cross_encoder_reranking": true,
    "relevance_filtering": true,
    "sentence_citations": true,
    "cpu_inference": true
  },
  "ready": true,
  "config": {
    "generative_model": "Qwen/Qwen3-8B-FP8",
    "extractive_model": "ktrapeznikov/biobert_v1.1_pubmed_squad_v2",
    "inference_mode": "gpu",
    "use_vllm": true
  }
}
```

`GET /retrieval-info` returns a JSON description of the retrieval components: keyword search with SIBiLS, the local semantic index, and how their results are merged.

## Errors

A request without a required field is rejected with HTTP 422 and a description of the problem, in the FastAPI format (not the `success` and `error` fields of the other SIBiLS APIs):

```bash
curl -X POST https://qa.sibils.org/api/qa -H 'Content-Type: application/json' -d '{}'
```

Response:

```json
{"detail": [{"type": "missing", "loc": ["body", "question"], "msg": "Field required", "input": {}}]}
```

`GET /QA` reports processing errors in the response body, with HTTP 200, `success` set to `false` and a message in `error`. For example, `col=suppdata` returns `"error": "Invalid collection 'suppdata'. Valid: medline, plazi, pmc"`. `POST /batch` does not validate `col`: an unknown collection returns HTTP 500 with the plain-text body `Internal Server Error`, see [Collections](#collections).

`POST /qa` and `/qa/multi` can return HTTP 200 with an empty `collection_results`, `ndocs_retrieved` 0 and an empty `model`. On 22 November 2026, this happened with `dense` retrieval for the question *What diseases are transmitted by ticks?*, which `sparse` retrieval answers. Check `ndocs_retrieved`, and retry with `sparse` retrieval when it is 0.

Generative answers over many documents can take several seconds: set a client timeout of at least 60 seconds.

## Legacy endpoints and migration {#legacy}

### `GET /QA` (legacy) {#get-qa-legacy}

Kept for compatibility with the former endpoint `https://biodiversitypmc.sibils.org/api/QA`. It returns a single list of answers instead of one block per collection. Use [`POST /qa`](#post-qa) for new code.

#### Parameters {#get-qa-parameters}

| Parameter | Required | Default | Description |
|---|---|---|---|
| `q` | yes | | Question in natural language |
| `col` | no | all | `medline`, `pmc` or `plazi`. When omitted, the three collections are searched and their answers are merged into one list (`collection` is then `medline+plazi+pmc`) |
| `n` | no | `10` | Documents retrieved from each collection |
| `mode` | no | `extractive` | `extractive` or `generative`, see [Answer modes](#answer-modes). `hybrid` is accepted but currently returns no answers on this endpoint |

The default mode is `extractive` here, and `generative` for `POST /qa`.

#### Example {#get-qa-example}

=== "URL"

    [https://qa.sibils.org/api/QA?q=What%20diseases%20are%20transmitted%20by%20ticks%3F&col=medline](https://qa.sibils.org/api/QA?q=What%20diseases%20are%20transmitted%20by%20ticks%3F&col=medline)

=== "curl"

    ```bash
    curl -G https://qa.sibils.org/api/QA \
      --data-urlencode 'q=What diseases are transmitted by ticks?' \
      --data-urlencode 'col=medline'
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    response = requests.get(
        "https://qa.sibils.org/api/QA",
        params={"q": "What diseases are transmitted by ticks?", "col": "medline"},
        timeout=120,
    )
    response.raise_for_status()
    result = response.json()

    if not result["success"]:
        raise RuntimeError(result["error"])
    for answer in result["answers"]:
        doc = answer["docs"][0]
        print(f'{answer["answer_score"]:.2f}  {answer["answer"]}  ({doc["doc_source"]} {doc["docid"]})')
    ```

This request took about 1 second in our tests.

#### Response {#get-qa-response}

Excerpt (one of the five answers, text shortened):

```json
{
  "sibils_version": "biomoqa-2.0",
  "success": true,
  "error": "",
  "question": "What diseases are transmitted by ticks?",
  "collection": "medline",
  "model": "biobert",
  "ndocs_requested": 10,
  "ndocs_returned_by_SIBiLS": 10,
  "answers": [
    {
      "answer": "Lyme disease and tickborne-encephalitis",
      "answer_score": 0.6484,
      "docs": [
        {
          "docid": "22662624",
          "doc_source": "medline",
          "doc_retrieval_score": 0.476,
          "doc_text": "[Diseases transmitted by ticks locally and abroad].. This article provides a brief overvie...",
          "snippet_start": 166,
          "snippet_end": 205
        }
      ]
    }
  ],
  "mode_used": "extractive",
  "pipeline_time": 1.02,
  "transformed_query": null,
  "debug_info": null,
  "documents": null
}
```

Response fields:

| Field | Description |
|---|---|
| `sibils_version` | Version of the QA service, for example `biomoqa-2.0` |
| `success`, `error` | `success` is `false` and `error` contains a message when the request could not be processed (for example an unknown collection) |
| `question` | The question as submitted |
| `collection` | Collection searched, or `medline+plazi+pmc` when `col` is omitted |
| `model` | `biobert` in extractive mode, or the name of the generative model |
| `ndocs_requested` | Value of `n` |
| `ndocs_returned_by_SIBiLS` | Documents retrieved, summed over collections when `col` is omitted |
| `answers` | Answers, best first, with the same structure as in [`POST /qa`](#post-qa-response). Can be empty even when `success` is `true` |
| `mode_used` | Value of `mode`, as given (`hybrid` is not resolved) |
| `pipeline_time` | Processing time in seconds |
| `transformed_query`, `debug_info`, `documents` | Not used by this endpoint (`null`) |

### `GET /fetch` {#get-fetch}

Forwards its query parameters unchanged to the SIBiLS fetch API and returns its response. It exists for the document viewer of the web application. For direct use, call the [BiodiversityPMC fetch API](fetch.md), which takes the same parameters.

Example: [https://qa.sibils.org/api/fetch?col=medline&ids=22662624](https://qa.sibils.org/api/fetch?col=medline&ids=22662624)

### Migrating from the former endpoint {#migrating-from-the-former-endpoint}

Replace the host. The parameters `q`, `col` and `n` keep their meaning.

| Item | Former endpoint | Current endpoint |
|---|---|---|
| URL | `https://biodiversitypmc.sibils.org/api/QA` (now HTTP 404) | `https://qa.sibils.org/api/QA` |
| `col` | Required: `medline` or `plazi` | Optional: `medline`, `pmc` or `plazi`; all three when omitted |
| `n` | Default 5 | Default 10. Pass `n=5` to keep the former number of documents |
| `mode` | Not available | `extractive` (default) or `generative` |

Former:

```text
https://biodiversitypmc.sibils.org/api/QA?q=What%20diseases%20are%20transmitted%20by%20ticks%20?&col=medline
```

Current:

```text
https://qa.sibils.org/api/QA?q=What%20diseases%20are%20transmitted%20by%20ticks%20?&col=medline
```

For new code, use [`POST /qa`](#post-qa), which searches the three collections in one request.

## Web application

[qa.sibils.org](https://qa.sibils.org/) is a web application for the same service, described in [Question-Answering](../../qa/index.md). A search can be shared with its URL, which contains the parameters `q`, `col`, `mode`, `retrieval` and `qa_size` (number of documents, 1 to 5), for example:

[https://qa.sibils.org/?q=What%20diseases%20are%20transmitted%20by%20ticks%20%3F&col=medline&mode=generative&retrieval=dense&qa_size=5](https://qa.sibils.org/?q=What%20diseases%20are%20transmitted%20by%20ticks%20%3F&col=medline&mode=generative&retrieval=dense&qa_size=5)

## OpenAPI reference

The [OpenAPI reference](qa_reference.md) page embeds the interactive reference of this API, generated from its OpenAPI description, where requests can be tried.
