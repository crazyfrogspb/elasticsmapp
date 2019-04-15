import argparse
import json
import tempfile
from itertools import islice

import pandas as pd
from pandas.io.common import _get_handle

import urlexpander
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsmapp.utils.embeddings import get_embedding
from elasticsmapp.utils.settings import config, index_settings
from urlextract import URLExtract

extractor = URLExtract()


def create_index(es, index_name, platform):
    if not es.indices.exists(index=index_name):
        if platform == 'reddit':
            settings = index_settings.reddit
        elif platform == 'twitter':
            settings = index_settings.twitter
        es.indices.create(index=index_name, body=settings)


def preprocess_reddit_post(post, calc_embeddings=False, urls_dict=None):
    post['edited'] = bool(post['edited'])
    if calc_embeddings:
        post['smapp_embedding'] = get_embedding(post['body'])
    post['smapp_urls'] = [urls_dict.get(url, url) for url in post['smapp_urls']]
    return post


def preprocess_tweet(post, calc_embeddings=False, urls_dict=None):
    text = post.get('full_text')
    if text is None:
        text = post.get('text', '')
    post['smapp_twitter_text'] = text
    if calc_embeddings:
        post['embedding_vector'] = get_embedding(text)
    post['smapp_urls'] = [urls_dict.get(url, url) for url in post['smapp_urls']]
    return post


def put_data_from_json(index_name, filename, platform='reddit',
                       id_field='id', compression=None, chunksize=10000,
                       calc_embeddings=False, server_name='localhost', port=9200,
                       start_doc=0, expand_urls=False):
    es = Elasticsearch([{'host': server_name, 'port': port}])
    create_index(es, index_name, platform)
    data, _ = _get_handle(filename, 'r', compression=compression)

    if platform == 'reddit':
        text_field = 'body'
    elif platform == 'twitter':
        text_field = 'full_text'

    tmp_file, tmp_filename = tempfile.mkstemp()
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
            urls_dict = {}
            all_urls = []
            for post in lines_json:
                text = post.get(text_field)
                if text is None:
                    text = post.get('text', '')
                urls = extractor.find_urls(text)
                post['smapp_urls'] = urls
                all_urls.extend(urls)
            all_urls = [url for url in all_urls if 'reddit.com' not in url]
            if expand_urls:
                expanded_urls = urlexpander.expand(all_urls,
                                                   chunksize=1280,
                                                   n_workers=64,
                                                   cache_file=tmp_filename)
                urls_dict = dict(zip(all_urls, expanded_urls))
            for post_num, post in enumerate(lines_json):
                if platform == 'reddit':
                    posts.append(preprocess_reddit_post(
                        post, calc_embeddings, urls_dict))
                elif platform == 'twitter':
                    posts.append(preprocess_tweet(
                        post, calc_embeddings, urls_dict))
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
    tmp_file.close()


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
    parser.add_argument('--chunksize', type=int, default=10000)
    parser.add_argument('--calc_embeddings', action='store_true')
    parser.add_argument('--server_name', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--start_doc', type=int, default=0)
    parser.add_argument('--expand_urls', action='store_true')

    args = parser.parse_args()
    args_dict = vars(args)

    put_data_from_json(**args_dict)
