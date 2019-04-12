import base64

import gensim.downloader as api
import numpy as np
from nltk.corpus import stopwords


dbig = np.dtype('>f8')
model = api.load("glove-twitter-25")
num_features = model.wv.vector_size
stopwords = set(stopwords.words('english'))


def decode_float_list(base64_string):
    bytes = base64.b64decode(base64_string)
    return np.frombuffer(bytes, dtype=dbig).tolist()


def encode_array(arr):
    base64_str = base64.b64encode(np.array(arr).astype(dbig)).decode("utf-8")
    return base64_str


def get_embedding(sentence, ignore_stopwords=True):
    words = sentence.lower().split()
    feature_vec = np.zeros((num_features, ), dtype='float32')
    n_words = 0
    for word in words:
        if word in model.vocab and word not in stopwords:
            n_words += 1
            feature_vec = np.add(feature_vec, model[word])
    if n_words > 0:
        feature_vec = np.divide(feature_vec, n_words)
    return encode_array(feature_vec)
