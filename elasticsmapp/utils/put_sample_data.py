import json
from itertools import islice

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from pandas.io.common import _get_handle

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

settings = {
    "settings": {
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
                }
            }
        }
    }
}

if not es.indices.exists(index="reddit"):
    es.indices.create(index='reddit', body=settings)

chunksize = 100

data, _ = _get_handle('data/RC_2008-01.bz2', 'r', compression='bz2')

close = False
while not close:
    lines = list(islice(data, chunksize))
    if lines:
        lines_json = filter(None, map(lambda x: x.strip(), lines))
        lines_json = json.loads('[' + ','.join(lines_json) + ']')
        actions = [
            {
                "_index": "reddit",
                "_type": "comment",
                "_id": str(comment['id']),
                "_source": comment
            }
            for comment in lines_json
        ]
        bulk(es, actions)
    else:
        close = True

data.close()

# PANDAS
#documents = df_sample.to_dict(orient='records')
#bulk(es, documents, index='reddit', doc_type='test', raise_on_error=True)
