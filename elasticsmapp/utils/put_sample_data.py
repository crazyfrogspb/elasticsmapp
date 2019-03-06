import argparse
import json
from itertools import islice

import pandas as pd
from pandas.io.common import _get_handle
from tqdm import tqdm

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsmapp.utils.embeddings import get_embedding
from elasticsmapp.utils.settings import index_settings

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


def create_index(index_name, platform):
    if not es.indices.exists(index=index_name):
        if platform == 'reddit':
            settings = index_settings.reddit
        es.indices.create(index=index_name, body=settings)


def put_data_from_json(index_name, filename, post_type='comment', platform='reddit',
                       id_field='id', compression=None, chunksize=100,
                       calc_embeddings=True, text_field='body'):
    create_index(index_name, platform)
    data, _ = _get_handle(filename, 'r', compression=compression)

    close = False
    while not close:
        lines = list(islice(data, chunksize))
        if lines:
            lines_json = filter(None, map(lambda x: x.strip(), lines))
            lines_json = json.loads('[' + ','.join(lines_json) + ']')
            if calc_embeddings:
                for post_num, post in tqdm(enumerate(lines_json), desc='embedding'):
                    lines_json[post_num]['embedding_vector'] = get_embedding(
                        post[text_field])
            actions = [
                {
                    "_index": index_name,
                    "_type": post_type,
                    "_id": str(post[id_field]),
                    "_source": post
                }
                for post in lines_json
            ]
            bulk(es, actions)
        else:
            close = True

    data.close()


def put_data_from_pandas(csv_filename, index_name, post_type='comment', platform='reddit'):
    create_index(index_name, platform)
    df = pd.read_csv(csv_filename)
    documents = df.to_dict(orient='records')
    bulk(es, documents, index=index_name, doc_type=post_type, raise_on_error=True)


if __name__ == 'main':
    parser = argparse.ArgumentParser(description='Add data to index')

    parser.add_argument('--index_name', type=str)
    parser.add_argument('--filename', type=str)
    parser.add_argument('--post_type', type=str, default='comment')
    parser.add_argument('--platform', type=str, default='reddit')
    parser.add_argument('--id_field', type=str, default='id')
    parser.add_argument('--compression', type=str, default=None)
    parser.add_argument('--chunksize', type=int, default=100)
    parser.add_argument('--calc_embeddings', action='store_true')
    parser.add_argument('--text_field', type=str, default='body')

    args = parser.parse_args()
    args_dict = vars(args)

    put_data_from_json(**args_dict)
