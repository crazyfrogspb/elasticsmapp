import pandas as pd

from elasticsmapp.utils.text_utils import WordSplitter, get_embedding

wordsplitter = WordSplitter()


def preprocess_tweet(post, calc_embeddings=False, collection=None):
    truncated = post.get('truncated', False)
    if truncated:
        post['text'] = post['extended_tweet']['full_text']
        if 'extended_entities' in post['extended_tweet']:
            post['extended_tweet']['entities'].update(
                post['extended_tweet']['extended_entities'])
        post['entities'] = post['extended_tweet']['entities']
        post['display_text_range_extended'] = post['extended_tweet']['display_text_range']
        post.pop('extended_tweet')
    elif 'full_text' in post:
        post['text'] = post['full_text']
        post.pop('full_text')
    if calc_embeddings:
        post['smapp_embedding'] = get_embedding(post['text'])

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

    if '_id' in post:
        post.pop('_id')

    return post


def create_twitter_actions(es, lines_json, calc_embeddings=False, collection=None):
    if collection is None:
        collection = 'not_specified'
    actions = []
    for post_num, post in enumerate(lines_json):
        post = preprocess_tweet(post, calc_embeddings, collection)
        period = str(pd.to_datetime(post['created_at']).to_period('M'))
        index_name = f'smapp_twitter_{period}'
        action = {
            "_op_type": "update",
            "_index": index_name,
            "_type": "_doc",
            "_id": post['id_str'],
            "_source": {
                "script": {
                    "lang": "painless",
                    "inline": "if (!ctx._source.smapp_collection.contains(params.collection)) {ctx._source.smapp_collection.add(params.collection)}",
                    "params": {"collection": collection}
                },
                "upsert": post
            }
        }
        actions.append(action)
    return actions
