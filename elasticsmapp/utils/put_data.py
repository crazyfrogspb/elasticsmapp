import argparse
import json
from itertools import islice

import pandas as pd
from pandas.io.common import _get_handle

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsmapp.utils.embeddings import get_embedding
from elasticsmapp.utils.settings import config, index_settings


def create_index(es, index_name, platform):
    if not es.indices.exists(index=index_name):
        if platform == 'reddit':
            settings = index_settings.reddit
        elif platform == 'twitter':
            settings = index_settings.twitter
        es.indices.create(index=index_name, body=settings)


def preprocess_reddit_post(post, calc_embeddings=False, text_field='body'):
    post['edited'] = bool(post['edited'])
    if calc_embeddings:
        post['embedding_vector'] = get_embedding(post[text_field])
    return post


def preprocess_tweet(post, calc_embeddings=False, text_field='text'):
    if calc_embeddings:
        post['embedding_vector'] = get_embedding(post[text_field])
    return post


def put_data_from_json(index_name, filename, platform='reddit',
                       id_field='id', compression=None, chunksize=100,
                       calc_embeddings=True, text_field='body',
                       server_name='localhost', port=9200, start_doc=0):
    es = Elasticsearch([{'host': server_name, 'port': port}])
    create_index(es, index_name, platform)
    data, _ = _get_handle(filename, 'r', compression=compression)

    close = False
    done = 0
    while done + chunksize < start_doc and not close:
        lines = list(islice(data, chunksize))
        if lines:
            done += chunksize
            if done % 1000 == 0:
                print(f"{done} documents processed")
        else:
            close = True
    while not close:
        lines = list(islice(data, chunksize))

        if lines:
            lines_json = filter(None, map(lambda x: x.strip(), lines))
            lines_json = json.loads('[' + ','.join(lines_json) + ']')
            posts = []
            for post_num, post in enumerate(lines_json):
                if platform == 'reddit':
                    posts.append(preprocess_reddit_post(
                        post, calc_embeddings, text_field))
                elif platform == 'twitter':
                    posts.append(preprocess_tweet(
                        post, calc_embeddings, text_field))
            actions = [
                {
                    "_index": index_name,
                    "_type": '_doc',
                    "_id": str(post[id_field]),
                    "_source": post
                }
                for post in posts
            ]
            if actions:
                bulk(es, actions, request_timeout=config.request_timeout)
            done += chunksize
            if done % 1000 == 0:
                print(f"{done} documents processed")
        else:
            close = True

    data.close()


def put_data_from_pandas(es, csv_filename, index_name, platform='reddit'):
    create_index(index_name, platform)
    df = pd.read_csv(csv_filename)
    documents = df.to_dict(orient='records')
    bulk(es, documents, index=index_name,
         doc_type='_doc', raise_on_error=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add data to index')

    parser.add_argument('--index_name', type=str)
    parser.add_argument('--filename', type=str)
    parser.add_argument('--platform', type=str, default='reddit')
    parser.add_argument('--id_field', type=str, default='id')
    parser.add_argument('--compression', type=str, default=None)
    parser.add_argument('--chunksize', type=int, default=100)
    parser.add_argument('--calc_embeddings', action='store_true')
    parser.add_argument('--text_field', type=str, default='body')
    parser.add_argument('--server_name', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--start_doc', type=int, default=0)

    args = parser.parse_args()
    args_dict = vars(args)

    put_data_from_json(**args_dict)
