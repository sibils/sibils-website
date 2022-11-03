# SIBiLS PubMed central full-texts and annotations fetch API

## Description

This API allows to retrieve annotated contents from PMC Open Access. The input is a set of pmcids (up to 1,000 per request). The output is a set of parsed and annotated full-texts, in both JATS and BioC formats. Delivered and annotated fields include for example full texts, paragraphs provided with their hierarchical level in the document structure, or figure captions. Annotations are delivered with many features including the type of the mapped entity (drug, gene, disease...), the vocabulary used, the vocabulary unique identifier and preferred term, or the mapping characters offsets.


## API endpoint

**URL**: [candy.hesge.ch/SIBiLS/PMC/fetch.jsp](https://candy.hesge.ch/SIBiLS/PMC/fetch.jsp)

**Mandatory input**: the list of requested PMCIDs (&ids=). PMCIDs are separated by any non-digit character.

**Example**: fetch two PMCIDs: [candy.hesge.ch/SIBiLS/PMC/fetch.jsp?ids=PMC5805723,PMC3706742](https://candy.hesge.ch/SIBiLS/PMC/fetch.jsp?ids=PMC5805723,PMC3706742)

## Code sample

python script for demonstrating POST calls to the API

```python
import requests # not installed in default Python
import json

# PMIDs to fetch (limited to 1000)
pmcids = "PMC5805723,PMC3706742"

# call with POST
url_API = "https://candy.hesge.ch/SIBiLS/PMC/fetch.jsp"
my_params = {"ids": pmcids} # parameters dictionary
r = requests.post(url = url_API, params = my_params)

# get response and print in output file
response = r.text
with open("SIBiLS_PMC_fetch.json","w",encoding="utf-8") as file:
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
				{"section_title": section where passage (text) is found
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