import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from text_preprocessor import TextPreprocessor
from parsers import (
    parse_portal_antara,
    parse_portal_tribun
)

# ✅ Load model klasifikasi
@st.cache_resource
def load_model():
    return joblib.load("model_berita_svm1.pkl")

model = load_model()

# ✅ Judul aplikasi
st.title("📡 Scraper & Klasifikasi Berita Ekonomi Lampung")

# ✅ Pilih portal
portal = st.selectbox(
    "📰 Pilih Portal Berita:",
    ["Antara News Lampung", "Tribun Lampung"]  # Sesuaikan dengan key di parser_map
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
    st.info(f"🔄 Scraping berita dari {portal}... Mohon tunggu sebentar ⏳")

    # Mapping nama portal ke fungsi parser
    parser_map = {
        "Antara News Lampung": parse_portal_antara,
        "Tribun Lampung": parse_portal_tribun
    }

    parse_function = parser_map.get(portal)
    if not parse_function:
        st.error("❌ Parser untuk portal tidak ditemukan.")
        st.stop()

    hasil = parse_function(
        keyword if keyword.strip() else None,
        start_date,
        end_date,
        max_pages=15  # Kamu bisa ubah jumlah halaman jika ingin lebih banyak
    )

    if not hasil:
        st.warning("⚠️ Tidak ada artikel ditemukan dalam rentang waktu tersebut.")
        st.stop()

    df = pd.DataFrame(hasil)
    st.subheader("📋 Hasil Scraping")
    st.write(f"Jumlah artikel ditemukan: {len(df)}")
    st.dataframe(df[['tanggal', 'link']].head())

    # ✅ Cek kolom teks
    if "teks" not in df.columns or df["teks"].isnull().all() or df["teks"].str.strip().eq("").all():
        st.error("❌ Tidak ada isi artikel yang valid untuk diklasifikasi.")
        st.stop()

    # ✅ Klasifikasi ekonomi
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
