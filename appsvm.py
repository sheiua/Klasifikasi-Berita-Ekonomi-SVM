import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from text_preprocessor import TextPreprocessor
from parsers import (
    parse_portal_antara,
    parse_portal_viva,
    parse_portal_lampost,
    parse_portal_lampungpro
)

# ✅ Load model klasifikasi
@st.cache_resource
def load_model():
    return joblib.load("model_berita_svm1.pkl")

model = load_model()

st.title("📡 Scraper & Klasifikasi Berita Ekonomi Lampung")

portal = st.selectbox("📰 Pilih Portal Berita:", [
    "Antara News Lampung", 
    "Viva Lampung", 
    "Lampung Post",
    "Lampungpro"
])

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 Tanggal mulai", value=datetime(2024, 1, 1))
with col2:
    end_date = st.date_input("📅 Tanggal akhir", value=datetime(2025, 12, 31))

# ✅ Mapping fungsi parser
parser_map = {
    "Antara News Lampung": {
        "func": parse_portal_antara,
        "support_date": True
    },
    "Viva Lampung": {
        "func": parse_portal_viva,
        "support_date": False  # tidak support start_date, end_date
    },
    "Lampung Post": {
        "func": parse_portal_lampost,
        "support_date": True
    },
    "Lampungpro": {
        "func": parse_portal_lampungpro,
        "support_date": True  # karena kita filter saat scraping
    }
}

if st.button("🚀 Mulai Scraping & Klasifikasi"):
    st.info(f"🔄 Scraping berita dari {portal}...")

    parser_info = parser_map[portal]
    parse_function = parser_info["func"]

    try:
        if parser_info["support_date"]:
            hasil = parse_function(
                max_pages=10,
                start_date=start_date,
                end_date=end_date
            )
        else:
            hasil = parse_function(max_pages=10)  # Tanpa start_date/end_date
    except Exception as e:
        st.error(f"❌ Gagal scraping: {e}")
        st.stop()

    if not hasil:
        st.warning("⚠️ Tidak ada artikel ditemukan.")
        st.stop()

    df = pd.DataFrame(hasil)

    if not df.empty and "tanggal" in df.columns and parser_info["support_date"]:
        # Kalau support tanggal, filter ulang berdasarkan input user
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        df = df[(df['tanggal'] >= pd.to_datetime(start_date)) & (df['tanggal'] <= pd.to_datetime(end_date))]

    if df.empty:
        st.warning("⚠️ Tidak ada artikel ditemukan dalam rentang tanggal yang dipilih.")
        st.stop()

    st.subheader("📋 Hasil Scraping")
    st.write(f"Jumlah artikel ditemukan: {len(df)}")
    st.dataframe(df[['judul', 'link']] if 'judul' in df.columns else df[['link']])

    # ❗ Pastikan kolom 'isi' ada
    if "isi" not in df.columns or df["isi"].isnull().all() or df["isi"].str.strip().eq("").all():
        st.error("❌ Tidak ada isi artikel valid untuk klasifikasi.")
        st.stop()

    df['label'] = model.predict(df['isi'])
    df_ekonomi = df[df['label'] == 1]

    st.success(f"✅ Jumlah berita ekonomi: {len(df_ekonomi)}")

    if not df_ekonomi.empty:
        st.subheader("📄 Daftar Berita Ekonomi")
        st.dataframe(df_ekonomi[['judul', 'link', 'isi']] if 'judul' in df_ekonomi.columns else df_ekonomi[['link', 'isi']])

        output_file = "Berita_Ekonomi.xlsx"
        df_ekonomi.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button(
                "📥 Download Excel Berita Ekonomi",
                f,
                file_name="Berita_Ekonomi.xlsx"
            )
