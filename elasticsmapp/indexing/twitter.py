import pandas as pd

from elasticsearch.exceptions import NotFoundError
from elasticsmapp.utils.text_utils import WordSplitter, get_embedding

wordsplitter = WordSplitter()


def preprocess_tweet(post, calc_embeddings=False, collection=None):
    text = post.get('full_text')
    if text is None:
        text = post.get('text', '')
    else:
        post.pop('full_text')
    post['text'] = text
    if calc_embeddings:
        post['smapp_embedding'] = get_embedding(text)

    urls = []
    for url in post['entities']['urls']:
        urls.append(url['expanded_url'])
    post['smapp_urls'] = urls

    if 'retweeted_status' in post:
        post['smapp_retweeted_user_screen_name'] = post['retweeted_status']['user']['screen_name']
        post['smapp_retweeted_user_id_str'] = post['retweeted_status']['user']['id_str']
        post.pop('retweeted_status')
    if 'quoted_status' in post:
        post['smapp_quoted_user_screen_name'] = post['quoted_status']['user']['screen_name']
        post['smapp_quoted_user_id_str'] = post['quoted_status']['user']['id_str']
        post.pop('quoted_status')

    post['smapp_platform'] = 'twitter'
    if collection is None:
        collection = 'not_specified'
    post['smapp_collection'] = [collection]
    post['smapp_username_split'] = wordsplitter.infer_spaces(
        post['user']['screen_name'])
    for i, hashtag in enumerate(post['entities']['hashtags']):
        post['entities']['hashtags'][i]['smapp_hashtag_split'] = wordsplitter.infer_spaces(
            hashtag['text'])

    return post


def create_twitter_actions(es, lines_json, calc_embeddings=False, collection=None):
    all_posts = []
    for post_num, post in enumerate(lines_json):
        post = preprocess_tweet(post, calc_embeddings, collection)
        period = str(pd.to_datetime(post['created_at']).to_period('M'))
        index_name = f'smapp_twitter_{period}'
        if es.indices.exists(index=index_name):
            try:
                post_old = es.get(index_name, '_doc', post['id_str'])['_source']
                post['smapp_collection'].extend(post_old['smapp_collection'])
                post['smapp_collection'] = list(set(post['smapp_collection']))
            except NotFoundError:
                pass
        all_posts.append(post)

    actions = [
        {
            "_index": "placeholder",
            "_type": '_doc',
            "_id": str(post['id_str']),
            "_source": post,
            "pipeline": 'twitter'
        }
        for post in all_posts
    ]

    return actions
