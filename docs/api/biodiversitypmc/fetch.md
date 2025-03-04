# Biodiversity PMC documents and annotations fetch API

## Description

This API allows to retrieve annotated contents from a given collection. The input is a set of docids (up to 1,000 per request). The output is a set of parsed and annotated documents, in json and/or BioC formats.

## API endpoint

**URL**: [biodiversitypmc.sibils.org/api/fetch](https://biodiversitypmc.sibils.org/api/fetch)

**Mandatory input**: one collection (&col=), amongst "medline", "pmc", "plazi" and "suppdata"
**Mandatory input**: the list of requested document ids (&ids=). Docids are separated by commas.
**Optional input**: the output format (&format=) amongst "json" (default) or "BioC" (to come)

**Example**: fetch two PMIDs from MEDLINE
[https://biodiversitypmc.sibils.org/api/fetch?ids=14691011,25190367&col=medline](https://biodiversitypmc.sibils.org/api/fetch?ids=14691011,25190367&col=medline)

## Code sample

python script for demonstrating POST calls to the API

```python
import requests # not installed in default Python
import json

# PMIDs to fetch (limited to 1000)
pmids = "14691011,25190367"
collection = "medline"

# call with POST
url_API = "https://biodiversitypmc.sibils.org/api/fetch"
my_params = {"ids": pmids , "col": collection} # parameters dictionary
r = requests.post(url = url_API, data = my_params)

# get response and print in output
response = r.text
with open("SIBiLS_fetch.json","w",encoding="utf-8") as file:
   file.write(r.text)
```

## Output

Output is json and/OR BiOC [BioC](http://bioc.sourceforge.net/) formatted :

```json
{"documents": 
	[Array of documents corresponding to the query]
		{"infons": 
			[Array of PubMed like informations about the document]
		{"passages": 
			[Array of passages splitted from the document]
			{"infons": 
				[Array of informations relative to the passage]
				{"type": nature of the passage (e.g. "title", "abstract")
			{"text": the passage
			{"annotations": 
				[Array of annotations relative to the passage]
				{"text": concept annotated
				{"infons": 
					[Array of informations about each annotation]
					{"type": type of entity (text) matched
					{"source": terminology used
					{"source_id": ID from the terminology
					{"searchable_id": code(terminology)+";"+ source_id
					{"prefered_term": prefered_term extracted from the terminology
					{"sentence": sentence where the text is found
				{"locations":
					{"offset": start position of the text in the sentence
					{"length": length of the text annotated

```
