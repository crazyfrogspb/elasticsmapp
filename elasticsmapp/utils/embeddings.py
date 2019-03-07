import base64

import numpy as np

import gensim.downloader as api

dfloat32 = np.dtype('>f4')
model = api.load("glove-twitter-50")
index2word_set = set(model.wv.index2word)
num_features = model.wv.vector_size


def decode_float_list(base64_string):
    bytes = base64.b64decode(base64_string)
    return np.frombuffer(bytes, dtype=dfloat32).tolist()


def encode_array(arr):
    base64_str = base64.b64encode(
        np.array(arr).astype(dfloat32)).decode("utf-8")
    return base64_str


def get_embedding(sentence):
    words = sentence.split()
    feature_vec = np.zeros((num_features, ), dtype='float32')
    n_words = 0
    for word in words:
        if word in index2word_set:
            n_words += 1
            feature_vec = np.add(feature_vec, model[word])
    if n_words > 0:
        feature_vec = np.divide(feature_vec, n_words)
    return encode_array(feature_vec)
