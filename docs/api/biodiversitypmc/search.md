# Biodiversity PMC customizable search API

## Description

This API allows to perform a fully customizable search for valuable annotated citations in a given collection. The power of SIBiLS is based on the efficiency of Elasticsearch engines, and on the rich Lucene query language, which allows to investigate a large panel of searching strategies. For example: basic search with keywords or entity identifiers (“ZBED1” or “NP_NX_O96006”), searches in specified fields (“title: ZBED1” or “annotations_str: genes”), boosting fields or query parts, Boolean, exploiting identified concepts or identified concept types...) The input is thus a Lucene json query. The output is the Elasticsearch ranked result set, ranked by relevance, in its native json format; for each retrieved citation (up to 10,000 per request), a relevance score and the indexed content are included.

## API endpoint

**URL**: [biodiversitypmc.sibils.org/api/search](https://biodiversitypmc.sibils.org/api/search)

**Mandatory input**: q OR jq: a query q in free text, which is interpreted by query analyzer, OR a Lucene json_query jq

**Mandatory input**: one collection (&col=), amongst "medline", "pmc", "plazi" and "suppdata"

**Optional input**: the number of requested documents (&n=, default 10, max 1000)

**Example**: simple search for MEDLINE (&col=) documents containing (&q=) Rhinolophus and Pangolin.

[biodiversitypmc.sibils.org/api/search?q=Rhinolophus%20and%20Pangolin&col=medline](https://biodiversitypmc.sibils.org/api/search?q=Rhinolophus%20and%20Pangolin&col=medline)

**Example**: customizable search (&jq) with a Lucene style json query

```json
{"query": {"bool" : {"must": {"match" : { "title" : "Digitoxin metabolism" }},"should" : {"match" : { "annotations_str" : "GO" }},"boost": 1}}}
```

**Query language**: JSON queries for Elasticsearch are described in [elastic.co](https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html)

## Code sample

A python script for demonstrating POST calls to the API, with multiple examples of Lucene style queries:

```python
import requests # not installed in default Python
import json

query = {}

# queries must be formatted in Lucene ElasticSearch style
# https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html

# here are different query types :

# MULTI_MATCH queries
# use it for searching in specific fields, with a general OR or AND

search_fields = ["title","abstract","keywords","mesh_terms"]
# you can use "title^3" for boosting by 3 scores in title
keywords = "BRCA2 cancer"
my_operator = "and" # default is "or"
my_type = "phrase" # use it for phrase matching (exact expression)

my_query = {
    "size": 20, # maximum amount of hits returned
    "from" : 0, # offset from the first result you want to fetch
    "query": {
        "multi_match" : {
            "query" : keywords,
            "fields" : search_fields
            #,"operator" : my_operator
            #,"type" = "phrase"
            }
        }
    }


# BOOLEAN queries
# The AND/OR/NOT operators can be used to fine tune the search queries.
# This is implemented in the search API as a bool query.
# The bool query accepts a must parameter (equivalent to AND),
# a must_not parameter (equivalent to NOT),
# and a should parameter (equivalent to OR).
# https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html

"""
# ex: ("EML4" OR "ALK" in title) AND ("Lung Cancer" in journal)
my_query = {
    "query": {
        "bool" : {
            "must" :[ # AND
                {
                    "bool" : {
                        "should" :[ # OR
                            {
                                "match" : {"title": "EML4"},
                                "match" : {"title": "ALK"}
                                }
                            ]
                        }
                    },
                {
                    "match" : {"journal": "Lung Cancer"}
                    }
                ]
            }
        }
    }
"""

# EXPLOITING ANNOTATIONS
# the annotations_str field can be exploited in order to search for
# concept types (drugs, genes, diseases), or concepts ids (gene
# P51587).

"""
# ex: records with identified BRCA2 (NX_P51587) and identified drugs
my_ids = "NP_NX_P51587"
my_types = "drugs"
my_operator = "and"

my_query = {
    "query": {
        "multi_match" : {
            "query" : my_ids + " " + my_types,
            "fields" : "annotations_str"
            ,"operator" : my_operator
            }
        }
    }
"""


# call
url_API = "https://biodiversitypmc.sibils.org/api/search"
my_json_query = json.dumps(my_query) # json to string
my_params = {"jq": my_json_query,col="pmc"} # parameters dictionary
r = requests.post(url = url_API, data = my_params)

# get response and print in output file
response = r.text
with open("SIBiLS_search.json","w",encoding="utf-8") as file:
   file.write(r.text)
```

## Output

Output is a native Elasticsearch response (json formatted), and includes retrieval scores for each document.
