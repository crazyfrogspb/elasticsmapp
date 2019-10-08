import os.path as osp
import re
import string
from math import log

import gensim.downloader as api
import numpy as np
from gensim.models.keyedvectors import KeyedVectors
from nltk.corpus import stopwords

dbig = np.dtype('>f8')
try:
    model = KeyedVectors.load_word2vec_format("glove-twitter-100.txt", binary=False)
except FileNotFoundError:
    print('File not found, attempting to download')
    model = api.load("glove-twitter-100")

num_features = model.wv.vector_size
stopwords = set(stopwords.words('english'))

DATA_PATH = osp.join(osp.dirname(osp.dirname(
    osp.dirname(osp.realpath(__file__)))), osp.join('data'))


def get_embedding(sentence, ignore_stopwords=True):
    sentence = re.sub('[' + string.punctuation + ']', '', sentence)
    words = sentence.lower().split()
    feature_vec = np.zeros((num_features,), dtype='float32')
    n_words = 0
    for word in words:
        if word in model.vocab and (not ignore_stopwords or word not in stopwords):
            n_words += 1
            feature_vec = np.add(feature_vec, model[word])
    if n_words > 0:
        feature_vec = np.divide(feature_vec, n_words)
    feature_vec = list(feature_vec)
    return [round(float(elem), 3) for elem in feature_vec]


class WordSplitter:
    def __init__(self):
        file = osp.join(DATA_PATH, 'wordsfreq_wiki2.txt')
        with open(file) as f:
            self._words = f.read().split()
        self._wordcost = dict((k, log((i + 1) * log(len(self._words))))
                              for i, k in enumerate(self._words))
        self._maxword = max(len(x) for x in self._words)

    def infer_spaces(self, text):
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
