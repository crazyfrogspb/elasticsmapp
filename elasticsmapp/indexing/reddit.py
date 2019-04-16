import urlexpander
from urlextract import URLExtract

from elasticsmapp.utils.embeddings import get_embedding

extractor = URLExtract()


def preprocess_reddit_post(post, calc_embeddings=False, urls_dict=None):
    post['edited'] = bool(post['edited'])
    if calc_embeddings:
        post['smapp_embedding'] = get_embedding(post['body'])
    post['smapp_urls'] = [urls_dict.get(url, url) for url in post['smapp_urls']]
    post['smapp_platform'] = 'reddit'

    return post


def create_reddit_actions(lines_json, index_name, tmp_filename, calc_embeddings=False):
    urls_dict = {}
    all_urls = []
    posts = []

    for post in lines_json:
        urls = extractor.find_urls(post['body'])
        post['smapp_urls'] = urls
        all_urls.extend(urls)
    all_urls = [url for url in all_urls if 'reddit.com' not in url]
    expanded_urls = urlexpander.expand(all_urls,
                                       chunksize=1280,
                                       n_workers=64,
                                       cache_file=tmp_filename)
    urls_dict = dict(zip(all_urls, expanded_urls))
    for post_num, post in enumerate(lines_json):
        posts.append(preprocess_reddit_post(
            post, calc_embeddings, urls_dict))

    actions = [
        {
            "_index": index_name,
            "_type": '_doc',
            "_id": str(post['id']),
            "_source": post
        }
        for post in posts
    ]

    return actions
