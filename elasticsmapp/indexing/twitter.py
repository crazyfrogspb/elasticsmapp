from elasticsmapp.utils.embeddings import get_embedding


def preprocess_tweet(post, calc_embeddings=False):
    text = post.get('full_text')
    if text is None:
        text = post.get('text', '')
    else:
        post.pop('full_text')
    post['text'] = text
    if calc_embeddings:
        post['embedding_vector'] = get_embedding(text)

    urls = []
    for url in post['entities']['urls']:
        urls.append(url['expanded_url'])
    post['smapp_urls'] = urls

    return post


def create_twitter_actions(lines_json, index_name, calc_embeddings=False):
    posts = []
    for post_num, post in enumerate(lines_json):
        post = preprocess_tweet(post, calc_embeddings)
        posts.append(post)

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
