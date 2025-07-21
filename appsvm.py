import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from text_preprocessor import TextPreprocessor
from parsers import (
    parse_portal_antara,
    parse_portal_viva,
    parse_portal_lampost
)

# ✅ Load model klasifikasi
@st.cache_resource
def load_model():
    return joblib.load("model_berita_svm1.pkl")

model = load_model()

st.title("📡 Scraper & Klasifikasi Berita Ekonomi Lampung")

# ✅ Pilih portal berita
portal = st.selectbox("📰 Pilih Portal Berita:", [
    "Antara News Lampung", 
    "Viva Lampung", 
    "Lampung Post"
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
        "support_date": False
    },
    "Lampung Post": {
        "func": parse_portal_lampost,
        "support_date": True
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
            hasil = parse_function(max_pages=10)
    except Exception as e:
        st.error(f"❌ Gagal scraping: {e}")
        st.stop()

    if not hasil:
        st.warning("⚠️ Tidak ada artikel ditemukan.")
        st.stop()

    df = pd.DataFrame(hasil)

    if not df.empty and "tanggal" in df.columns and parser_info["support_date"]:
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        df = df[(df['tanggal'] >= pd.to_datetime(start_date)) & (df['tanggal'] <= pd.to_datetime(end_date))]

    if df.empty:
        st.warning("⚠️ Tidak ada artikel ditemukan dalam rentang tanggal yang dipilih.")
        st.stop()

    st.subheader("📋 Hasil Scraping")
    st.write(f"Jumlah artikel ditemukan: {len(df)}")
    st.dataframe(df[['judul', 'link']] if 'judul' in df.columns else df[['link']])

    # ✅ Validasi kolom isi
    if "isi" not in df.columns:
        st.error("❌ Tidak ada kolom 'isi' dalam data.")
        st.stop()

    df = df[df['isi'].notnull() & df['isi'].str.strip().ne("")]
    df['isi'] = df['isi'].astype(str)

    if df.empty:
        st.error("❌ Tidak ada artikel dengan isi valid untuk klasifikasi.")
        st.stop()

    # ✅ Prediksi klasifikasi
    try:
        df['label'] = model.predict(df['isi'])
        st.write("🔍 Distribusi label:", pd.Series(df['label']).value_counts())
    except Exception as e:
        st.error(f"❌ Gagal melakukan klasifikasi: {e}")
        st.stop()

    df_ekonomi = df[df['label'] == 1]

    if df_ekonomi.empty:
        st.info("ℹ️ Tidak ada berita ekonomi yang terklasifikasi.")
        st.stop()

    st.success(f"✅ Jumlah berita ekonomi: {len(df_ekonomi)}")

    st.subheader("📄 Daftar Berita Ekonomi")
    st.dataframe(
        df_ekonomi[['judul', 'link', 'isi']] if 'judul' in df_ekonomi.columns 
        else df_ekonomi[['link', 'isi']]
    )

    # ✅ Unduh hasil
    output_file = "Berita_Ekonomi.xlsx"
    df_ekonomi.to_excel(output_file, index=False)

    with open(output_file, "rb") as f:
        st.download_button(
            "📥 Download Excel Berita Ekonomi",
            f,
            file_name="Berita_Ekonomi.xlsx"
        )
