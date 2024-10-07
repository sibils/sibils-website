# SPARQL

## Endpoint

[https://sparql.sibils.org](https://sparql.sibils.org/)

## Ontologies
* [HTML format](sibils-ontology.html)
* [TTL format](sibils-ontology.ttl)

## Examples


### Number of publications by type

```sparql title="RQ_001.sparql"
PREFIX : <http://sibils.org/rdf#>
SELECT 
  ?publi_class (count(*) as ?count)
WHERE {
  ?s :hasPubMedCentralId ?o.
  ?s a ?publi_class.
}
GROUP BY ?publi_class
```

### Annotations of a given publication

```sparql title="RQ_002.sparql"
PREFIX : <http://sibils.org/rdf#>
PREFIX sibils: <http://sibils.org/rdf/data/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT
  (str(?doi) as ?doi)
  (str(?cpt_id) as ?cpt_id)
  (str(?scheme) as ?scheme)
  (str(?start) as ?start)
  (str(?token) as ?token)
  (str(?part) as ?section)
  (str(?part_type) as ?part_type)
WHERE {
  VALUES ?publi { sibils:PMC2196267 }
  ?publi :doi ?doi.
  ?publi :hasAnnotation ?a .
  ?a :hasBody ?cpt .
  ?cpt skos:notation ?cpt_id .
  ?cpt skos:inScheme / rdfs:label ?scheme .

  ?a :hasTarget ?trg.
  ?trg :hasSource ?part.
  ?part a ?part_type .

  ?trg :hasSelector ?sel .
  ?sel :start ?start.
  ?sel :exact ?token.
  # FILTER (?part_type != :Paragraph )
}
ORDER BY ?part ?start ?token
LIMIT 100
```

### Diseases associated to ticks in the same discourse element of a publication at a distance of less than 30 characters

```sparql title="RQ_003.sparql"
PREFIX : <http://sibils.org/rdf#>
PREFIX sibils: <http://sibils.org/rdf/data/>
PREFIX sibilc: <http://sibils.org/rdf/concept/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT
  ?part
  (str(?word)  as ?token)
  ?pos
  (str(?word2) as ?token2)
  ?pos2
WHERE {
  ?publi :hasAnnotation ?a .
  ?a :hasBody sibilc:Mesh_St%7CD013987 .
  ?a :hasTarget ?trg .
  ?trg :hasSelector ?sel .
  ?sel :exact ?word.
  ?sel :start ?pos .
  ?trg :hasSource ?part.

  ?publi :hasAnnotation ?a2 .
  ?a2 :hasTarget ?trg2.
  ?trg2 :hasSelector ?sel2 .
  ?sel2 :exact ?word2.
  ?sel2 :start ?pos2 .
  ?trg2 :hasSource ?part.
  ?a2 :hasBody ?cpt2.
  ?cpt2 skos:inScheme :Ncit_St.

 FILTER (abs(?pos2 - ?pos) < 30 && ?a != ?a2)
}
```
