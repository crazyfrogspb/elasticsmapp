class IndexSettings():
    reddit = {
        "settings": {
            "index.mapping.ignore_malformed": True,
            'number_of_shards': 4,
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
                            },
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "smapp_text": {
                        "type": "alias",
                        "path": "body"
                    },
                    "retrieved_on": {
                        "type": "date",
                        "format": "epoch_second"
                    },
                    "created_utc": {
                        "type": "date",
                        "format": "epoch_second"
                    },
                    "author_created_utc": {
                        "type": "date",
                        "format": "epoch_second"
                    },
                    "smapp_datetime": {
                        "type": "alias",
                        "path": "created_utc"
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
                    "smapp_embedding": {
                        "type": "binary",
                        "doc_values": True
                    },
                    "edited": {
                        "type": "boolean"
                    },
                    "author": {
                        "type": "text"
                    },
                    "smapp_username": {
                        "type": "alias",
                        "path": "author"
                    }
                }
            }
        }
    }

    twitter = {
        "settings": {
            "index.mapping.ignore_malformed": True,
            "number_of_shards": 4,
            "number_of_replicas": 1,
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
                    "place": {
                        "properties": {
                            "bounding_box": {
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
                            }
                        }
                    },
                    "user": {
                        "properties": {
                            "created_at": {
                                "type": "date",
                                "format": "EEE MMM dd HH:mm:ss Z YYYY"
                            },
                            "screen_name": {
                                "type": "text"
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
                            },
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "smapp_text": {
                        "type": "alias",
                        "path": "text"
                    },
                    "created_at": {
                        "type": "date",
                        "format": "EEE MMM dd HH:mm:ss Z YYYY"
                    },
                    "smapp_datetime": {
                        "type": "alias",
                        "path": "created_at"
                    },
                    "smapp_embedding": {
                        "type": "binary",
                        "doc_values": True
                    },
                    "smapp_username": {
                        "type": "alias",
                        "path": "user.screen_name"
                    }
                }
            }
        }
    }


class GlobalConfig():
    request_timeout = 30


index_settings = IndexSettings()
config = GlobalConfig()
