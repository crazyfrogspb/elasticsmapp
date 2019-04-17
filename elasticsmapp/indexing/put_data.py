import argparse
import json
import os
import os.path as osp
import tempfile
import warnings
from itertools import islice

import pandas as pd
from pandas.io.common import _get_handle

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsmapp.indexing.reddit import create_reddit_actions
from elasticsmapp.indexing.settings import config, index_settings
from elasticsmapp.indexing.twitter import create_twitter_actions


def create_index(es, index_name, platform):
    if not es.indices.exists(index=index_name):
        if platform == 'reddit':
            settings = index_settings.reddit
        elif platform == 'twitter':
            settings = index_settings.twitter
        es.indices.create(index=index_name, body=settings)


def put_data_from_json(server_name, index_name, platform, filename,
                       username, password, ignore_decoding_errors=False,
                       port=None, compression=None, chunksize=10000,
                       calc_embeddings=False, start_doc=0):
    es = Elasticsearch([{'host': server_name, 'port': port}],
                       http_auth=(username, password))
    create_index(es, index_name, platform)

    if compression is None:
        compression = osp.splitext(filename)[-1].replace('.', '')
    data, _ = _get_handle(filename, 'r', compression=compression)

    close = False
    done = 0
    tmp_file, tmp_filename = tempfile.mkstemp()
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
            try:
                lines_json = json.loads('[' + ','.join(lines_json) + ']')
            except json.decoder.JSONDecodeError as e:
                if ignore_decoding_errors:
                    warnings.warn(f'Decoding error for chunk {done}: {e}')
                    continue
            if platform == 'reddit':
                actions = create_reddit_actions(
                    lines_json, index_name, tmp_filename, calc_embeddings)
            elif platform == 'twitter':
                actions = create_twitter_actions(
                    lines_json, index_name, calc_embeddings)

            if actions:
                bulk(es, actions, request_timeout=config.request_timeout)
            done += chunksize
            if done % 1000 == 0:
                print(f"{done} documents processed")
        else:
            close = True

    data.close()
    os.close(tmp_file)


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
    parser.add_argument('--username', type=str, default=None)
    parser.add_argument('--password', type=str, default=None)
    parser.add_argument('--platform', type=str, default='reddit')
    parser.add_argument('--compression', type=str, default=None)
    parser.add_argument('--chunksize', type=int, default=10000)
    parser.add_argument('--calc_embeddings', action='store_true')
    parser.add_argument('--server_name', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--start_doc', type=int, default=0)
    parser.add_argument('--ignore_decoding_errors', action='store_true')

    args = parser.parse_args()
    args_dict = vars(args)

    put_data_from_json(**args_dict)
