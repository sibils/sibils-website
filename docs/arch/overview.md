# Architecture

## Data processing

``` mermaid
graph TD
    TERM[(Terminologies)] --> TERM_CONV[Convert terminologies to JSON]
    TERM_CONV --> TERM_JSON[(JSON files)]

    subgraph Plazi pushes new files
        PLAZI[(SIB FTP)] --> PLAZI_CONV[Scan new file and convert Plazi XML files]
    end
    PLAZI_CONV --> PLAZI_MONGO[(MongoDB collection Plazi)]

    subgraph Yearly
        MEDLINE_Y[(MEDLINE dump)] --> MEDLINE_CONV_Y[Convert JATS to JSON]
    end
    subgraph Weekly
        MEDLINE_W[(MEDLINE weekly update)] --> MEDLINE_CONV_W[Convert JATS to JSON]
    end
    MEDLINE_CONV_W --> |Update existing DB| MEDLINE_MONGO[(MongoDB collection Medline)]
    MEDLINE_CONV_Y --> |Update everything| MEDLINE_MONGO


    TERM_JSON --> ANNOTATIONS[Annotated each passage]
    PLAZI_MONGO --> ANNOTATIONS
    MEDLINE_MONGO --> ANNOTATIONS

    ANNOTATIONS --> ANNOTATIONS_MONGO[(Annotations)]

    ANNOTATIONS_MONGO --> TO_ES[Index MongoDB content into ElasticSearch]

    TO_ES --> ANNOTATIONS_ES[(ElasticSearch)]

    click TERM_CONV "../terminologies/"
    click PLAZI_CONV "../datasource_parsing/"
    click MEDLINE_CONV_Y "../datasource_parsing/"
    click MEDLINE_CONV_W "../datasource_parsing/"
    click ANNOTATIONS "../annotations/"
    click TO_ES "../elasticsearch/"
```

## Viewers

...