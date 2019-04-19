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
    post['tmp_collection'] = collection
    post['smapp_username_split'] = wordsplitter.infer_spaces(
        post['user']['screen_name'])
    for i, hashtag in enumerate(post['entities']['hashtags']):
        post['entities']['hashtags'][i]['smapp_hashtag_split'] = wordsplitter.infer_spaces(
            hashtag['text'])

    return post


def create_twitter_actions(lines_json, calc_embeddings=False, collection=None):
    all_posts = []
    for post_num, post in enumerate(lines_json):
        post = preprocess_tweet(post, calc_embeddings, collection)
        all_posts.append(post)

    actions = [
        {
            "_op_type": "update",
            "_index": "placeholder",
            "_type": '_doc',
            "_id": str(post['id_str']),
            "doc": post,
            "pipeline": 'twitter',
            "doc_as_upsert": True
        }
        for post in all_posts
    ]

    return actions
