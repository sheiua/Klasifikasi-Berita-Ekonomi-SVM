# ==========================
# ✅ 1. Import Library
# ==========================
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
import os

# ==========================
# ✅ 2. Baca Data Excel
# ==========================
# Pastikan file 'hasil_label.xlsx' ada di folder yang sama
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
    TfidfVectorizer(max_features=5000),  # Batas fitur agar lebih cepat
    MultinomialNB()
)

model.fit(X, y)

print("✅ Model selesai dilatih!")

# ==========================
# ✅ 5. Simpan Model
# ==========================
model_filename = "model_berita.pkl"
joblib.dump(model, model_filename)
print(f"💾 Model berhasil disimpan ke: {os.path.abspath(model_filename)}")
