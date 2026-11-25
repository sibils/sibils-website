---
description: >-
  Map PMIDs to DOIs or PMCIDs, and DOIs to PMIDs, up to 1,000 ids per request, with the
  BiodiversityPMC API.
---

# Identifier mapping

These endpoints retrieve the Digital Object Identifiers (DOIs) or PubMed Central identifiers (PMCIDs) associated with PubMed identifiers (PMIDs), and the PMIDs associated with DOIs, from the SIBiLS copy of MEDLINE. You can submit up to 1,000 ids in a single request.
{ .lead }

| Endpoint | Input | Output pairs |
|---|---|---|
| `/pmid2doi` | `pmids` | `pmid`, `doi` |
| `/pmid2pmcid` | `pmids`, optional `col` | `pmid`, `pmcid` |
| `/doi2pmid` | `dois` | `pmid`, `doi` |

<div class="facts" markdown>

Reference
:   [OpenAPI reference](reference.md) · [Swagger UI](https://biodiversitypmc.sibils.org/api/)

Examples checked
:   22 November 2026, SIBiLS release 5.1.5.10

</div>

The response contains a `mapping` array, with one object per id found. The `doi` (or `pmcid`) field is `null` when no DOI (or PMCID) is found for a PMID. The `warning` field lists the ids that were not found in the SIBiLS copy of MEDLINE (`missing ids:...`); they are not in `mapping`. `/pmid2pmcid` with `col=pmc` is an exception, see [PMIDs to PMCIDs](#pmids-to-pmcids). The order of `mapping` can differ from the order of the input ids.

## PMIDs to DOIs

`GET` or `POST` `https://biodiversitypmc.sibils.org/api/pmid2doi`
{ .endpoint }

| Parameter | Required | Description |
|---|---|---|
| `pmids` | yes | PMIDs separated by commas without spaces, up to 1,000 |

Example:

[https://biodiversitypmc.sibils.org/api/pmid2doi?pmids=38060177,14691011,456](https://biodiversitypmc.sibils.org/api/pmid2doi?pmids=38060177,14691011,456)

=== "curl"

    ```bash
    curl 'https://biodiversitypmc.sibils.org/api/pmid2doi' \
      --data-urlencode 'pmids=38060177,14691011,456'
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    # PMIDs to map (up to 1,000), separated by commas
    pmids = "38060177,14691011,456"

    # call with POST
    url = "https://biodiversitypmc.sibils.org/api/pmid2doi"
    r = requests.post(url, data={"pmids": pmids}, timeout=60)

    result = r.json()
    if not result["success"]:
        raise RuntimeError(result["error"])
    for item in result["mapping"]:
        print(item["pmid"], item["doi"])

    with open("SIBiLS_pmid2doi_mapping.json", "w", encoding="utf-8") as file:
        file.write(r.text)
    ```

Output:

```json
{
  "sibils_version": "v5.1.5.10",
  "success": true,
  "error": "",
  "warning": "",
  "mapping": [
    {"pmid": "14691011", "doi": "10.1210/en.2003-0985"},
    {"pmid": "38060177", "doi": "10.1007/978-1-0716-3577-3_2"},
    {"pmid": "456", "doi": null}
  ]
}
```

PMID 456 is in MEDLINE but has no DOI, so its `doi` is `null`.

## PMIDs to PMCIDs

`GET` or `POST` `https://biodiversitypmc.sibils.org/api/pmid2pmcid`
{ .endpoint }

| Parameter | Required | Default | Description |
|---|---|---|---|
| `pmids` | yes | | PMIDs separated by commas without spaces, up to 1,000 |
| `col` | no | `medline` | `medline` or `pmc`. With `pmc`, the PMIDs are searched in PMC records instead of MEDLINE records, and PMIDs that are not found in PMC are left out of `mapping` without being listed in `warning` |

Example with MEDLINE:

[https://biodiversitypmc.sibils.org/api/pmid2pmcid?pmids=32379317,37002680](https://biodiversitypmc.sibils.org/api/pmid2pmcid?pmids=32379317,37002680)

Example with PMC:

[https://biodiversitypmc.sibils.org/api/pmid2pmcid?pmids=32379317,37002680&col=pmc](https://biodiversitypmc.sibils.org/api/pmid2pmcid?pmids=32379317,37002680&col=pmc)

=== "curl"

    ```bash
    curl 'https://biodiversitypmc.sibils.org/api/pmid2pmcid' \
      --data-urlencode 'pmids=32379317,37002680'
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    # PMIDs to map (up to 1,000), separated by commas
    pmids = "32379317,37002680"

    # call with POST; add "col": "pmc" to search PMC records
    url = "https://biodiversitypmc.sibils.org/api/pmid2pmcid"
    r = requests.post(url, data={"pmids": pmids}, timeout=60)

    result = r.json()
    if not result["success"]:
        raise RuntimeError(result["error"])
    for item in result["mapping"]:
        print(item["pmid"], item["pmcid"])

    with open("SIBiLS_pmid2pmcid_mapping.json", "w", encoding="utf-8") as file:
        file.write(r.text)
    ```

Output:

```json
{
  "sibils_version": "v5.1.5.10",
  "success": true,
  "error": "",
  "warning": "",
  "collection": "medline",
  "mapping": [
    {"pmid": "32379317", "pmcid": "PMC7319474"},
    {"pmid": "37002680", "pmcid": "PMC10066029"}
  ]
}
```

## DOIs to PMIDs

`GET` or `POST` `https://biodiversitypmc.sibils.org/api/doi2pmid`
{ .endpoint }

| Parameter | Required | Description |
|---|---|---|
| `dois` | yes | DOIs separated by commas without spaces, up to 1,000 |

DOIs are matched case-sensitively, as stored in MEDLINE: `10.1210/en.2003-0985` is found, `10.1210/EN.2003-0985` is not.

Example:

[https://biodiversitypmc.sibils.org/api/doi2pmid?dois=10.1210/en.2003-0985,10.1007/978-1-0716-3577-3_2](https://biodiversitypmc.sibils.org/api/doi2pmid?dois=10.1210/en.2003-0985,10.1007/978-1-0716-3577-3_2)

=== "curl"

    ```bash
    curl 'https://biodiversitypmc.sibils.org/api/doi2pmid' \
      --data-urlencode 'dois=10.1210/en.2003-0985,10.1007/978-1-0716-3577-3_2'
    ```

=== "Python"

    ```python
    import requests  # pip install requests

    # DOIs to map (up to 1,000), separated by commas
    dois = "10.1210/en.2003-0985,10.1007/978-1-0716-3577-3_2"

    url = "https://biodiversitypmc.sibils.org/api/doi2pmid"
    r = requests.post(url, data={"dois": dois}, timeout=60)

    result = r.json()
    if not result["success"]:
        raise RuntimeError(result["error"])
    for item in result["mapping"]:
        print(item["doi"], item["pmid"])
    ```

Output:

```json
{
  "sibils_version": "v5.1.5.10",
  "success": true,
  "error": "",
  "warning": "",
  "mapping": [
    {"pmid": "38060177", "doi": "10.1007/978-1-0716-3577-3_2"},
    {"pmid": "14691011", "doi": "10.1210/en.2003-0985"}
  ]
}
```
