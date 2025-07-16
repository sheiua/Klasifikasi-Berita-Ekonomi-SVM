import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from text_preprocessor import TextPreprocessor
from parsers import parse_portal_antara

# ✅ Load model klasifikasi
@st.cache_resource
def load_model():
    return joblib.load("model_berita_svm1.pkl")

model = load_model()

# ✅ Judul aplikasi
st.title("📡 Scraper & Klasifikasi Berita Ekonomi - Antara News Lampung")

# ✅ Pilih portal (sementara 1 dulu)
portal = st.selectbox(
    "📰 Pilih Portal Berita:",
    ["Antara News Lampung"]
)

# ✅ Keyword opsional
keyword = st.text_input("🔍 Masukkan keyword pencarian (opsional):", value="")

# ✅ Rentang tanggal
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 Tanggal mulai", value=datetime(2024, 1, 1))
with col2:
    end_date = st.date_input("📅 Tanggal akhir", value=datetime(2025, 12, 31))

# ✅ Tombol proses
if st.button("🚀 Mulai Scraping & Klasifikasi"):
    st.info("🔄 Mengambil dan memproses berita... Mohon tunggu beberapa saat ⏳")

    hasil = parse_portal_antara(
        keyword if keyword.strip() else None,
        start_date,
        end_date,
        max_pages=15  # Bisa kamu ubah sesuai kebutuhan
    )

    if not hasil:
        st.warning("⚠️ Tidak ada artikel ditemukan dalam rentang waktu tersebut. Coba gunakan keyword atau perpanjang rentang tanggal.")
        st.stop()

    df = pd.DataFrame(hasil)
    st.subheader("📋 Hasil Scraping")
    st.write(f"Jumlah artikel ditemukan: {len(df)}")
    st.dataframe(df[['tanggal', 'link']].head())

    # Cek isi teks
    if "teks" not in df.columns or df["teks"].isnull().all() or df["teks"].str.strip().eq("").all():
        st.error("❌ Tidak ada isi artikel yang valid untuk diklasifikasi.")
        st.stop()

    # ✅ Prediksi ekonomi (label 1)
    df['label'] = model.predict(df['teks'])
    df_ekonomi = df[df['label'] == 1]

    st.success(f"✅ Jumlah berita bertopik ekonomi: {len(df_ekonomi)}")

    if not df_ekonomi.empty:
        st.subheader("📄 Daftar Berita Ekonomi")
        st.dataframe(df_ekonomi[['tanggal', 'link', 'teks']])

        # ✅ Simpan Excel
        output_file = "Berita_Ekonomi.xlsx"
        df_ekonomi.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button(
                "📥 Download Excel Berita Ekonomi",
                f,
                file_name="Berita_Ekonomi.xlsx"
            )
