# ==========================
# ✅ 1. Import Library
# ==========================
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# ==========================
# ✅ 2. Baca Data Langsung
# ==========================
# Pastikan file 'hasil_label.xlsx' sudah diunggah ke Colab
df = pd.read_excel('hasil_label.xlsx')

print("📊 Contoh data:")
print(df.head())
print(df.columns)

# ==========================
# ✅ 3. Bersihkan Data Kosong
# ==========================
kolom_teks = '5. APA yang terjadi pada fenomena ekonomi yang ditemukan ?'
kolom_label = 'Label'

df_clean = df.dropna(subset=[kolom_teks, kolom_label])

print(f"Data awal: {df.shape}")
print(f"Data bersih: {df_clean.shape}")

X = df_clean[kolom_teks].fillna('')
y = df_clean[kolom_label]

# ==========================
# ✅ 4. Buat Pipeline & Latih Model
# ==========================
model = make_pipeline(
    TfidfVectorizer(max_features=5000),  # Batas fitur agar cepat
    MultinomialNB()
)

model.fit(X, y)

print("✅ Model selesai dilatih!")

# ==========================
# ✅ 5. Simpan & Unduh Model
# ==========================
joblib.dump(model, "model_berita.pkl")

# Untuk download otomatis di Google Colab
from google.colab import files
files.download("model_berita.pkl")
