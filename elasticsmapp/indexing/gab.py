import pandas as pd

import urlexpander
from elasticsmapp.utils.text_utils import WordSplitter, get_embedding
from urlextract import URLExtract

extractor = URLExtract()
wordsplitter = WordSplitter()


def preprocess_gab_post(post, calc_embeddings=False, urls_dict=None):
    if calc_embeddings:
        post['smapp_embedding'] = get_embedding(post['body'])
    post['smapp_urls'] = [urls_dict.get(url, url) for url in post['smapp_urls']]
    post['smapp_platform'] = 'reddit'
    post['smapp_username_split'] = wordsplitter.infer_spaces(
        post['user']['username'])

    attachment = post.get('attachment', {}).get('value')
    attachment_type = post.get('attachment', {}).get('type')
    if attachment is None:
        post.pop('attachment')
    if attachment_type == 'giphy':
        attachment['value'] = {}
        attachment['value']['image'] = attachment

    return post


def create_gab_actions(es, lines_json, tmp_filename, calc_embeddings=False, expand_urls=False):
    urls_dict = {}
    all_urls = []
    actions = []

    for post in lines_json:
        try:
            urls = extractor.find_urls(str(post['body']))
        except AttributeError:
            post['smapp_urls'] = []
            continue
        post['smapp_urls'] = urls
        all_urls.extend(urls)
    if expand_urls:
        expanded_urls = urlexpander.expand(all_urls,
                                           chunksize=1280,
                                           n_workers=64,
                                           cache_file=tmp_filename)
        urls_dict = dict(zip(all_urls, expanded_urls))
    for post_num, post in enumerate(lines_json):
        post = preprocess_gab_post(post, calc_embeddings, urls_dict)
        period = str(pd.to_datetime(
            post['created_utc'], unit='s').to_period('M'))
        index_name = f'smapp_gab_{period}'
        action = {
            "_index": index_name,
            "_type": '_doc',
            "_id": str(post['id']),
            "_source": post,
        }
        actions.append(action)

    return actions
