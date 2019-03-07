class IndexSettings():
    reddit = {
        "settings": {
            "index.mapping.ignore_malformed": True,
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
                    "created_utc": {
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
                        "doc_values": True
                    },
                    "edited": {
                        "type": "boolean"
                    }
                }
            }
        }
    }

    twitter = {
        "settings": {
            "index.mapping.ignore_malformed": True,
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
            "tweet": {
                "properties": {
                    "coordinates": {
                        "properties": {
                            "coordinates": {
                                "type": "geo_point"
                            },
                            "type": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                    }
                                }
                            }
                        }
                    },
                    "text": {
                        "type": "text",
                        "analyzer": "custom_lowercase_stemmed"
                    },
                    "created_at": {
                        "type": "date",
                        "format": "EEE MMM dd HH:mm:ss Z YYYY"
                    },
                    "embedding_vector": {
                        "type": "binary",
                        "doc_values": True
                    }
                }
            }
        }
    }


class GlobalConfig():
    request_timeout = 30


index_settings = IndexSettings()
config = GlobalConfig()
