import http.client

from elasticsearch import Elasticsearch
from elasticsmapp.utils.embeddings import get_embedding

es = Elasticsearch([{'host': '192.168.0.71', 'port': None}])
http.client._MAXHEADERS = 10000


def find_similar_documents(sentence, subreddit, index_name='reddit', size=100):
    embedding_vector = get_embedding(sentence)
    query = {'query': {
        "function_score": {
            "query": {"range": {"created_utc": {"gte": "01/10/2018", "lte": "01/10/2018", "format": "dd/MM/yyyy"}}},
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

    return es.search(index=index_name, doc_type='_doc', body=query)
