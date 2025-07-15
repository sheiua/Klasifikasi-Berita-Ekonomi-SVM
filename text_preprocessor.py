# text_preprocessor.py

import re
from sklearn.base import BaseEstimator, TransformerMixin
import nltk

try:
    from nltk.corpus import stopwords
    stopwords.words("indonesian")  # coba akses dulu
except LookupError:
    nltk.download("stopwords")
    from nltk.corpus import stopwords

stopwords_id = set(stopwords.words("indonesian"))

class TextPreprocessor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.apply(self.clean_text)

    def clean_text(self, text):
        text = str(text).lower()
        text = re.sub(r"[^a-zA-Z\s]", "", text)
        text = " ".join(word for word in text.split() if word not in stopwords_id)
        return text
