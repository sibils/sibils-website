# SPARQL

## Endpoint

[https://sibils.text-analytics.ch/sparql](https://sibils.text-analytics.ch/sparql)

## Ontologies

* [html format](https://sibils.text-analytics.ch/doc/api/sparql/ontology/sibils-ontology.html)
* [ttl format](https://sibils.text-analytics.ch/doc/api/sparql/ontology/sibils-ontology.ttl)

## Examples


### RQ_001 - Number of publications by type

```sparql
PREFIX : <http://sibils.org/rdf#>
select  ?publi_class (count(*) as ?count) where {
  ?s :hasPubMedCentralId ?o.
  ?s a ?publi_class.
} group by ?publi_class
```

### RQ_002 - Annotations of a given publication

```sparql
PREFIX : <http://sibils.org/rdf#>
PREFIX sibils: <http://sibils.org/rdf/data/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

select  (str(?doi) as ?doi) (str(?cpt_id) as ?cpt_id) (str(?scheme) as ?scheme) (str(?start) as ?start) (str(?token) as ?token) (str(?part) as ?section) (str(?part_type) as ?part_type)
where {
values ?publi { sibils:PMC2718325 }
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
# filter (?part_type != :Paragraph )
} 
order by ?part ?start ?token
LIMIT 100
```

### RQ_003 - Diseases associated to ticks in the same discourse element of a publication at a distance of less than 30 characters

```sparql
PREFIX : <http://sibils.org/rdf#>
PREFIX sibils: <http://sibils.org/rdf/data/>
PREFIX sibilc: <http://sibils.org/rdf/concept/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

select ?part (str(?word)  as ?token) ?pos (str(?word2) as ?token2) ?pos2 where {
?publi :hasAnnotation ?a .
  ?a :hasBody sibilc:MESH_MESH%7CD013987 .
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
?cpt2 skos:inScheme :NCI_Thesaurus_Disease.
#?cpt2 skos:inScheme :MESH_MESH
filter (abs(?pos2 - ?pos) < 30 && ?a !=?a2)
}
```
