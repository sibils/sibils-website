# Biodiversity PMC PMID to DOI API

## Description

This API retrieves Digital Object Identifiers (DOIs) associated with PubMed IDs (PMIDs) from MEDLINE. You can submit a batch of up to 1,000 PMIDs in a single request. The API returns a JSON response, with an array containing objects, where each object represents a PMID-DOI mapping. The doi field may be null if no DOI is found in MEDLINE for the given PMID. The warnings section indicates PMIDs that were not found in MEDLINE.

## API endpoint

**URL**: [biodiversitypmc.sibils.org/api/pmid2doi](https://biodiversitypmc.sibils.org/api/pmid2doi)

**Mandatory input**: the list of PMIDs (&pmids=). PMIDs are separated by commas.

**Example**: map PMIDs from MEDLINE
[https://biodiversitypmc.sibils.org/api/pmid2doi?pmids=38060177,14691011,456](https://biodiversitypmc.sibils.org/api/pmid2doi?pmids=38060177,14691011,456)

## Code sample

python script for demonstrating POST calls to the API

```python
import requests # not installed in default Python
import json

# PMIDs to fetch (limited to 1000)
pmids = "38060177,14691011,456"

# call with POST
url_API = "https://biodiversitypmc.sibils.org/api/pmid2doi"
my_params = {"pmids": pmids} # parameters dictionary
r = requests.post(url = url_API, data = my_params)

# get response and print in output
response = r.text
with open("SIBiLS_pmid2doi_mapping.json","w",encoding="utf-8") as file:
   file.write(r.text)
```

## Output

Output is json formatted :

```json
{
  "sibils_version": "v4.2.5.5",
  "success": true,
  "error": "",
  "warning": "", [Contains PMIDs that were not found in MEDLINE (text)]
  "collection": "medline",
  "mapping": [
    {
      "pmid": "14691011",
      "doi": "10.1210/en.2003-0985"
    },
    {
      "pmid": "38060177",
      "doi": "10.1007/978-1-0716-3577-3_2"
    },
    {
      "pmid": "456",
      "doi": null [MAY BE NULL]
    }
  ]
}
```
