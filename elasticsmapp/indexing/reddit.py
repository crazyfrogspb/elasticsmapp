import urlexpander
from elasticsmapp.utils.text_utils import WordSplitter, get_embedding
from urlextract import URLExtract

extractor = URLExtract()
wordsplitter = WordSplitter()


def preprocess_reddit_post(post, calc_embeddings=False, urls_dict=None):
    post['edited'] = bool(post['edited'])
    if calc_embeddings:
        post['smapp_embedding'] = get_embedding(post['body'])
    post['smapp_urls'] = [urls_dict.get(url, url) for url in post['smapp_urls']]
    post['smapp_platform'] = 'reddit'
    post['smapp_username_split'] = wordsplitter.infer_spaces(post['author'])

    return post


def create_reddit_actions(lines_json, tmp_filename, calc_embeddings=False, expand_urls=False):
    urls_dict = {}
    all_urls = []
    posts = []

    for post in lines_json:
        try:
            urls = extractor.find_urls(str(post['body']))
        except AttributeError:
            post['smapp_urls'] = []
            continue
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
        posts.append(preprocess_reddit_post(
            post, calc_embeddings, urls_dict))

    actions = [
        {
            "_index": "placeholder",
            "_type": '_doc',
            "_id": str(post['id']),
            "_source": post,
            "pipeline": 'reddit',
            "_op_type": "update",
            "doc_as_upsert" : True
        }
        for post in posts
    ]

    return actions
