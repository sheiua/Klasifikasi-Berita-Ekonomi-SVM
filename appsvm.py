import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from text_preprocessor import TextPreprocessor
from parsers import parse_portal_antara

# ✅ Load model
@st.cache_resource
def load_model():
    return joblib.load("model_berita_svm1.pkl")

model = load_model()

# ✅ UI
st.title("📡 Scraper & Klasifikasi Berita Ekonomi Lampung")

# Pilih portal
portal = st.selectbox(
    "📰 Pilih Portal Berita:",
    ["Antara News Lampung"]  # Hanya aktifkan Antara dulu
)

# Input keyword (opsional)
keyword = st.text_input("🔍 Masukkan keyword pencarian (opsional):", value="")

# Rentang tanggal
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 Tanggal mulai", value=datetime(2024, 1, 1))
with col2:
    end_date = st.date_input("📅 Tanggal akhir", value=datetime(2024, 12, 31))

# Tombol aksi
if st.button("🚀 Mulai Scraping & Klasifikasi"):
    st.info(f"Scraping berita dari: **{portal}** ... Mohon tunggu ⏳")

    # Hanya Antara aktif sementara
    if portal == "Antara News Lampung":
        hasil = parse_portal_antara(
            keyword if keyword.strip() else None,
            start_date,
            end_date,
            max_pages=15  # Ubah sesuai kebutuhan
        )
    else:
        hasil = []

    # ✅ Cek hasil scraping
    if not hasil:
        st.warning("⚠️ Tidak ada artikel ditemukan dalam rentang waktu tersebut.")
        st.write("🔎 Tips: Coba perpanjang tanggal atau gunakan keyword.")
        st.stop()
    else:
        st.success(f"✅ Artikel ditemukan: {len(hasil)}")

    df = pd.DataFrame(hasil)
    st.subheader("📋 Hasil Scraping")
    st.dataframe(df[['tanggal', 'link']])

    if "teks" not in df.columns or df["teks"].isnull().all() or df["teks"].str.strip().eq("").all():
        st.error("❌ Semua teks kosong. Scraping gagal ambil isi artikel.")
        st.stop()

    # ✅ Prediksi label ekonomi
    df['label'] = model.predict(df['teks'])

    # Filter hanya ekonomi (label == 1)
    df_ekonomi = df[df['label'] == 1]

    st.success(f"💼 Jumlah berita bertopik ekonomi: {len(df_ekonomi)}")

    if not df_ekonomi.empty:
        st.dataframe(df_ekonomi[['tanggal', 'link', 'teks']])

        # Download Excel
        output_file = "Berita_Ekonomi.xlsx"
        df_ekonomi.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button(
                "📥 Download Excel Berita Ekonomi",
                f,
                file_name="Berita_Ekonomi.xlsx"
            )
