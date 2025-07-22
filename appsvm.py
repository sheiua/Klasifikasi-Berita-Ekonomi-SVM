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
import inspect  # ✅ Untuk cek parameter parser

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
    ["Antara News Lampung", "Viva Lampung", "Lampung Post"]
)

# ✅ Rentang tanggal
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 Tanggal mulai", value=datetime(2024, 1, 1))
with col2:
    end_date = st.date_input("📅 Tanggal akhir", value=datetime(2025, 12, 31))

# ✅ Tombol proses
if st.button("🚀 Mulai Scraping & Klasifikasi"):
    st.info(f"🔄 Scraping berita dari {portal}... Mohon tunggu sebentar ⏳")

    # Mapping portal ke fungsi
    parser_map = {
        "Antara News Lampung": parse_portal_antara,
        "Viva Lampung": parse_portal_viva,
        "Lampung Post": parse_portal_lampost
    }

    parse_function = parser_map.get(portal)
    if not parse_function:
        st.error("❌ Parser untuk portal tidak ditemukan.")
        st.stop()

    # ✅ Konversi tanggal datetime -> date jika perlu
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    # ✅ Cek parameter fungsi parser
    sig = inspect.signature(parse_function)
    args = sig.parameters
    kwargs = {}

    if 'max_pages' in args:
        kwargs['max_pages'] = 30
    if 'max_articles' in args:
        kwargs['max_articles'] = 31
    if 'start_date' in args:
        kwargs['start_date'] = start_date
    if 'end_date' in args:
        kwargs['end_date'] = end_date

    # Debug parameter
    st.text(f"⏳ Parameter dikirim ke parser: {kwargs}")

    # 🔄 Panggil parser
    try:
        hasil = parse_function(**kwargs)
    except Exception as e:
        st.error(f"❌ Gagal memanggil parser: {e}")
        st.stop()

    if not hasil:
        st.warning("⚠️ Tidak ada artikel ditemukan.")
        st.stop()

    df = pd.DataFrame(hasil)
    st.subheader("📋 Hasil Scraping")
    st.write(f"Jumlah artikel ditemukan: {len(df)}")
    if 'tanggal' in df.columns:
        st.dataframe(df[['tanggal', 'link']].head())
    else:
        st.dataframe(df[['link']].head())

    for i, item in enumerate(hasil):
    st.write(f"{i+1}. {item.get('judul')} | tanggal: {item.get('tanggal')} | isi panjang: {len(item.get('isi', ''))}")

    # ✅ Validasi isi teks artikel
    if "isi" not in df.columns or df["isi"].isnull().all() or df["isi"].str.strip().eq("").all():
        st.error("❌ Tidak ada isi artikel yang valid untuk diklasifikasi.")
        st.stop()

    # ✅ Klasifikasi
    df['label'] = model.predict(df['isi'])
    df_ekonomi = df[df['label'] == 1]

    st.success(f"✅ Jumlah berita bertopik ekonomi: {len(df_ekonomi)}")

    if not df_ekonomi.empty:
        st.subheader("📄 Daftar Berita Ekonomi")
        st.dataframe(df_ekonomi[['link', 'isi']])

        # ✅ Download Excel
        output_file = "Berita_Ekonomi.xlsx"
        df_ekonomi.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button(
                "📥 Download Excel Berita Ekonomi",
                f,
                file_name="Berita_Ekonomi.xlsx"
            )
