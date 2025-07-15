import re
from sklearn.base import BaseEstimator, TransformerMixin
from nltk.corpus import stopwords
import nltk

# ✅ Download stopwords jika belum ada
nltk.download('stopwords')
stopwords_id = set(stopwords.words('indonesian'))

class TextPreprocessor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.apply(self.clean_text)

    def clean_text(self, text):
        text = str(text).lower()
        text = re.sub(r"[^a-zA-Z\s]", "", text)  # Hapus angka dan tanda baca
        text = " ".join(word for word in text.split() if word not in stopwords_id)
        return text
