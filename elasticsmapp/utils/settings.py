class IndexSettings():
    reddit = {
        "settings": {
            "index.mapping.ignore_malformed": "true",
            'number_of_shards': 1,
            'number_of_replicas': 0,
            "analysis": {
                "filter": {
                    "custom_english_stemmer": {
                        "type": "stemmer",
                        "name": "english"
                    }
                },
                "analyzer": {
                    "custom_lowercase_stemmed": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "custom_english_stemmer"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "comment": {
                "properties": {
                    "body": {
                        "type": "text",
                        "analyzer": "custom_lowercase_stemmed"
                    },
                    "retrieved_on": {
                        "type": "date",
                        "format": "epoch_second"
                    },
                    "created_utc:": {
                        "type": "date",
                        "format": "epoch_second"
                    },
                    "score": {
                        "type": "integer"
                    },
                    "downs": {
                        "type": "integer"
                    },
                    "ups": {
                        "type": "integer"
                    },
                    "embedding_vector": {
                        "type": "binary",
                        "doc_values": "true"
                    },
                    "edited": {
                        "type": "boolean"
                    }
                }
            }
        }
    }


index_settings = IndexSettings()
