# SIBiLS MEDLINE citations and annotations fetch API

## Description

This API allows to retrieve annotated contents from MEDLINE. The input is a set of pmids (up to 1,000 per request). The output is a set of parsed and annotated citations, in both JATS and BioC formats. Delivered and annotated fields include for example abstracts, or MeSH terms. Annotations are delivered with many features including the type of the mapped entity (drug, gene, disease...), the vocabulary used, the vocabulary unique identifier and preferred term, or the mapping characters offsets.

## API endpoint

**URL**: [candy.hesge.ch/SIBiLS/MEDLINE/fetch.jsp](https://candy.hesge.ch/SIBiLS/MEDLINE/fetch.jsp)

**Mandatory input**: the list of requested PMIDs (&ids=). PMIDs are separated by any non-digit character.

**Example**: fetch two PMIDs
[https://candy.hesge.ch/SIBiLS/MEDLINE/fetch.jsp?ids=14691011,25190367](https://candy.hesge.ch/SIBiLS/MEDLINE/fetch.jsp?ids=14691011,25190367)

## Code sample

python script for demonstrating POST calls to the API

```json
import requests # not installed in default Python
import json

# PMIDs to fetch (limited to 1000)
pmids = "14691011,25190367"

# call with POST
url_API = "https://candy.hesge.ch/SIBiLS/MEDLINE/fetch.jsp"
my_params = {"ids": pmids} # parameters dictionary
r = requests.post(url = url_API, params = my_params)

# get response and print in output
response = r.text
with open("SIBiLS_MED_fetch.json","w",encoding="utf-8") as file:
   file.write(r.text)
```

## Output

Output is [BioC](http://bioc.sourceforge.net/) json formatted :

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