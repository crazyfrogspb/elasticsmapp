import argparse
import json
import os
import os.path as osp
import tempfile
import warnings
from itertools import islice

import pandas as pd
from pandas.io.common import _get_handle

import zstandard as zstd
from elasticsearch import Elasticsearch
from elasticsearch.client.ingest import IngestClient
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


def put_data_from_json(server_name, platform, filename,
                       username, password, ignore_decoding_errors=False,
                       port=None, compression='infer', chunksize=10000,
                       calc_embeddings=False, start_doc=0, collection=None,
                       skip_index_creation=False):
    es = Elasticsearch([{'host': server_name, 'port': port}],
                       http_auth=(username, password))
    p = IngestClient(es)
    p.put_pipeline(id='collection', body={
        'description': "Add collection name",
        'processors': [
            {"append": {"field": "smapp_collection",
                        "value": ["{{tmp_collection}}"],
                        "if": "ctx.platform == 'twitter'"}}
        ]
    })
    p.put_pipeline(id=f'{platform}_timeindex', body={
        'description': "Monthly date-time index naming",
        'processors': [
            {"date_index_name": {"field": "smapp_datetime",
                                 "index_name_prefix": f"smapp_{platform}_",
                                 "date_rounding": "M",
                                 "date_formats": ["EEE MMM dd HH:mm:ss Z YYYY", "UNIX", "ISO8601"],
                                 "index_name_format": "yyyy-MM"}}
        ]
    })

    if compression == 'zst':
        dctx = zstd.ZstdDecompressor()
        new_filename = osp.splitext(filename)[0] + '.json'
        with open(filename, 'rb') as ifh, open(new_filename, 'wb') as ofh:
            dctx.copy_stream(ifh, ofh, write_size=65536)
        compression = None
        filename = new_filename

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
                    lines_json, tmp_filename, calc_embeddings)
                date_field = 'created_utc'
            elif platform == 'twitter':
                actions = create_twitter_actions(
                    lines_json,  calc_embeddings, collection)
                date_field = 'created_at'
            for action in actions:
                if not skip_index_creation:
                    period = str(pd.to_datetime(
                        action['_source'][date_field]).to_period('M'))
                    create_index(es, f"smapp_{platform}_{period}", platform)

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

    parser.add_argument('--filename', type=str,
                        help='Path to file you want to index')
    parser.add_argument('--username', type=str, default=None,
                        help='Username for Elastic cluster')
    parser.add_argument('--password', type=str, default=None,
                        help='Password for Elastic cluster')
    parser.add_argument('--platform', type=str, default='reddit',
                        help='Name of the platform: reddit, twitter or gab')
    parser.add_argument('--compression', type=str, default='infer',
                        help='Compression of the file. It will be inferred from extension if None')
    parser.add_argument('--chunksize', type=int, default=100,
                        help='Size of the chunks to index data')
    parser.add_argument('--calc_embeddings', action='store_true',
                        help='If True, calculate embeddings for each document')
    parser.add_argument('--server_name', type=str, default='128.122.217.221')
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--start_doc', type=int, default=0)
    parser.add_argument('--ignore_decoding_errors', action='store_true')
    parser.add_argument('--collection', type=str, default=None)
    parser.add_argument('--skip_index_creation', action='store_true')

    args = parser.parse_args()
    args_dict = vars(args)

    put_data_from_json(**args_dict)
