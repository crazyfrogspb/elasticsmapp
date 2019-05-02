import http.client
import os

import pandas as pd

from elasticsearch import Elasticsearch
from elasticsmapp.utils.text_utils import get_embedding

es = Elasticsearch([{'host': os.getenv('ES_SERVER'), 'port': None}], http_auth=(
    os.getenv('ES_USERNAME'), os.getenv('ES_PASSWORD')))
http.client._MAXHEADERS = 10000
FIELDS = ['hits.hits._id', 'hits.hits._source.smapp_platform',
          'hits.hits._score', 'hits.hits._source.body', 'hits.hits._source.subreddit',
          'hits.hits._source.created_utc', 'hits.hits._source.score', 'hits.hits._source.text',
          'hits.hits._source.user.screen_name', 'hits.hits._source.created_at',
          'hits.hits._source.user.username']


def find_similar_documents(sentence, date_start, date_end, platforms=['reddit', 'twitter', 'gab'], size=10):
    indices = []
    for date in [date_start, date_end]:
        for platform in platforms:
            period = str(pd.to_datetime(
                date_start, format='%m/%d/%Y').to_period('M'))
            index_name = f'smapp_{platform}_{period}'
            if es.indices.exists(index=index_name):
                indices.append(index_name)
    if not indices:
        return None
    indices = ','.join(indices)
    embedding_vector = get_embedding(sentence)
    query = {'query': {
        "function_score": {
            "query": {"range": {"created_utc": {"gte": date_start, "lte": date_end, "format": "MM/dd/yyyy"}}},
            "boost_mode": "replace",
            "functions": [
                {
                    "script_score": {
                        "script": {
                            "source": "staysense",
                            "lang": "fast_cosine",
                            "params": {
                                "field": "smapp_embedding",
                                "cosine": True,
                                "encoded_vector": embedding_vector
                            }
                        }
                    }
                }
            ]
        }
    },
        "size": size
    }
    return 200, es.search(index=indices, doc_type='_doc', body=query, filter_path=FIELDS, request_timeout=60)
