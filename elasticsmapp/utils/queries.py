from elasticsearch import Elasticsearch
from elasticsmapp.utils.embeddings import get_embedding

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


def find_similar_documents(sentence, index_name='reddit', post_type='comment'):
    embedding_vector = get_embedding(sentence)
    query = {
        "function_score": {
            "boost_mode": "replace",
            "functions": [
                {
                    "script_score": {
                        "script": {
                          "source": "staysense",
                          "lang": "fast_cosine",
                          "params": {
                              "field": "embeddedVector",
                              "cosine": "true",
                              "encoded_vector": embedding_vector
                          }
                        }
                    }
                }
            ]
        }
    }
    return es.search(index=index_name, doc_type=post_type, body=query)
