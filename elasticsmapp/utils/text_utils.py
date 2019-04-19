import base64
import os.path as osp
import re
from math import log

import numpy as np

import gensim.downloader as api
from nltk.corpus import stopwords

dbig = np.dtype('>f8')
model = api.load("glove-twitter-25")
num_features = model.wv.vector_size
stopwords = set(stopwords.words('english'))

DATA_PATH = osp.join(osp.dirname(osp.dirname(
    osp.realpath(__file__))), osp.join('data'))


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


class WordSplitter:
    def __init__(self):
        file = osp.join(DATA_PATH, 'wordsfreq_wiki2.txt')
        with open(file) as f:
            self._words = f.read().split()
        self._wordcost = dict((k, log((i + 1) * log(len(self._words))))
                              for i, k in enumerate(self._words))
        self._maxword = max(len(x) for x in self._words)

    def _infer_spaces(self, text):
        # Infer location of spaces in hashtags
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)

        def best_match(i):
            # Find the best match for the first i characters
            # assuming costs has been built for the first (i-1) characters
            candidates = enumerate(reversed(cost[max(0, i - self._maxword):i]))
            return min((c + self._wordcost.get(text[i - k - 1:i],
                                               9e999), k + 1) for k, c in candidates)

        cost = [0]
        for i in range(1, len(text) + 1):
            cur_cost, k = best_match(i)
            cost.append(cur_cost)

        out = []
        i = len(text)
        while i > 0:
            cur_cost, k = best_match(i)
            assert cur_cost == cost[i]
            out.append(text[i - k:i])
            i -= k

        return list(reversed(out))
