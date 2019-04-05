class IndexSettings():
    reddit = {
        "settings": {
            "index.mapping.ignore_malformed": True,
            'number_of_shards': 2,
            'number_of_replicas': 1,
            "analysis": {
                "analyzer": {
                    "english_exact": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "_doc": {
                "properties": {
                    "body": {
                        "type": "text",
                        "analyzer": "english",
                        "fields": {
                            "exact": {
                                "type": "text",
                                "analyzer": "english_exact"
                            }
                        }
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
                "analyzer": {
                    "english_exact": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "_doc": {
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
                        "analyzer": "english",
                        "fields": {
                            "exact": {
                                "type": "text",
                                "analyzer": "english_exact"
                            }
                        }
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
