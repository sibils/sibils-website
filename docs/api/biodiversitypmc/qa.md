# Biodiversity PMC question answering API

## Description

This API allows sk questions in natural languages, and to obtain answers extracted from documents from a given collection. The input is a free text question. The output is a set of answers, ranked by scores, along with documents' snippet.

## API endpoint

**URL**: [biodiversitypmc.sibils.org/api/QA](https://biodiversitypmc.sibils.org/api/QA)

**Mandatory input**: one collection (&col=), amongst "medline" and "plazi"

**Mandatory input**: a question (&q=) in natural language

**Optional input**: the number of documents (&n=, default 5) to work with. Each documents asks ~5 seconds of processing.

**Example**: ask what diseases are transmitted by ticks ?
[https://biodiversitypmc.sibils.org/api/QA?q=What%20diseases%20are%20transmitted%20by%20ticks%20?&col=medline](https://biodiversitypmc.sibils.org/api/QA?q=What%20diseases%20are%20transmitted%20by%20ticks%20?&col=medline)


## Output

Output is json records of proposed answers.
