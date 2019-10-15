class IndexSettings():
    reddit = {
        "settings": {
            "index.mapping.ignore_malformed": True,
            'number_of_shards': 12,
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
                        "format": "epoch_second||strict_date_optional_time"
                    },
                    "author_created_utc": {
                        "type": "date",
                        "format": "epoch_second||strict_date_optional_time"
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
                        "type": "dense_vector",
                        "dims": 100
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
            "number_of_shards": 12,
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
                                "format": "EEE MMM dd HH:mm:ss ZZZZZ YYYY||strict_date_optional_time"
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
                        "format": "EEE MMM dd HH:mm:ss Z YYYY||strict_date_optional_time"
                    },
                    "smapp_datetime": {
                        "type": "alias",
                        "path": "created_at"
                    },
                    "smapp_embedding": {
                        "type": "dense_vector",
                        "dims": 100
                    },
                    "smapp_username": {
                        "type": "alias",
                        "path": "user.screen_name"
                    }
                }
            }
        }
    }

    gab = {
        "settings": {
            "index.mapping.ignore_malformed": True,
            'number_of_shards': 12,
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
                    "created_utc": {
                        "type": "date",
                        "format": "epoch_second||strict_date_optional_time"
                    },
                    "retrieved_utc": {
                        "type": "date",
                        "format": "epoch_second||strict_date_optional_time"
                    },
                    "revised_utc": {
                        "type": "date",
                        "format": "epoch_second||strict_date_optional_time"
                    },
                    "smapp_datetime": {
                        "type": "alias",
                        "path": "created_utc"
                    },
                    "user": {
                        "properties": {
                            "username": {
                                "type": "text"
                            }
                        }
                    },
                    "score": {
                        "type": "integer"
                    },
                    "like_count": {
                        "type": "integer"
                    },
                    "dislike_count": {
                        "type": "integer"
                    },
                    "reply_count": {
                        "type": "integer"
                    },
                    "repost_count": {
                        "type": "integer"
                    },
                    "smapp_username": {
                        "type": "alias",
                        "path": "user.username"
                    }
                }
            }
        }
    }


class GlobalConfig():
    request_timeout = 30


index_settings = IndexSettings()
config = GlobalConfig()
