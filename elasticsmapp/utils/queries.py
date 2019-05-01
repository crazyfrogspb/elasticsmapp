import http.client
import os

import pandas as pd
from dotenv import find_dotenv, load_dotenv

from elasticsearch import Elasticsearch
from elasticsmapp.utils.text_utils import get_embedding

load_dotenv(find_dotenv())

es = Elasticsearch([{'host': os.getenv('ES_SERVER'), 'port': None}], http_auth=(
    os.getenv('ES_USERNAME'), os.getenv('ES_PASSWORD')))
http.client._MAXHEADERS = 10000


def find_similar_documents(sentence, date, platform='reddit', size=10):
    fields = ['hits.hits._id', 'hits.hits._source.smapp_platform']
    if platform == 'reddit':
        fields.extend(['hits.hits._source.body', 'hits.hits._source.subreddit',
                       'hits.hits._source.created_utc', 'hits.hits._source.score'])
    elif platform == 'twitter':
        fields.extend(['hits.hits._source.text',
                       'hits.hits._source.user.screen_name', 'hits.hits._source.created_at'])
    elif platform == 'gab':
        fields.extend(['hits.hits._source.body',
                       'hits.hits._source.created_utc', 'hits.hits._source.user.username'])
    period = str(pd.to_datetime(date, format='%d/%m/%Y').to_period('M'))
    index_name = f'smapp_{platform}_{period}'
    if not es.indices.exists(index=index_name):
        return 400, 'Index does not exists'
    embedding_vector = get_embedding(sentence)
    query = {'query': {
        "function_score": {
            "query": {"range": {"created_utc": {"gte": date, "lte": date, "format": "dd/MM/yyyy"}}},
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
    return 200, es.search(index=index_name, doc_type='_doc', body=query, filter_path=fields)
