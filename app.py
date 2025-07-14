import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from parsers import (
    parse_portal_antara,
    parse_portal_viva,
    parse_portal_lampost,
    parse_portal_radar,
    parse_portal_sinar
)

# ✅ Load model
@st.cache_resource
def load_model():
    return joblib.load("model_svm_berita.pkl")

model = load_model()

# ✅ UI
st.title("📡 Scraper & Klasifikasi Berita Ekonomi Lampung")

# Pilih portal
portal = st.selectbox(
    "📰 Pilih Portal Berita:",
    ["Antara News Lampung", "Viva Lampung", "Lampung POST", "Radar Lampung", "Sinar Lampung"]
)

# Input keyword
keyword = st.text_input("🔍 Masukkan keyword pencarian:", value="ekonomi")

# Rentang tanggal
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 Tanggal mulai", value=datetime(2025, 7, 1))
with col2:
    end_date = st.date_input("📅 Tanggal akhir", value=datetime(2025, 7, 31))

# Tombol aksi
if st.button("🚀 Mulai Scraping & Klasifikasi"):
    st.info(f"Scraping berita dari: **{portal}** ... Mohon tunggu ⏳")

    # Mapping portal ke fungsi parser
    parser_map = {
        "Antara News Lampung": parse_portal_antara,
        "Viva Lampung": parse_portal_viva,
        "Lampung POST": parse_portal_lampost,
        "Radar Lampung": parse_portal_radar,
        "Sinar Lampung": parse_portal_sinar
    }

    parse_function = parser_map.get(portal)
    hasil = parse_function(keyword, start_date, end_date) if parse_function else []

    if not hasil:
        st.warning("⚠️ Tidak ada artikel ditemukan dalam rentang waktu tersebut.")
    else:
        # Convert ke DataFrame
        df = pd.DataFrame(hasil)

        # Pastikan kolom teks ada
        if "teks" not in df.columns or df["teks"].isnull().all():
            st.error("❌ Tidak bisa klasifikasi karena tidak ada teks artikel.")
        else:
            # Prediksi label
            df['label'] = model.predict(df['teks'])

            # Filter hanya ekonomi (label == 1)
            df_ekonomi = df[df['label'] == 1]

            st.success(f"✅ Jumlah berita bertopik ekonomi: {len(df_ekonomi)}")

            if not df_ekonomi.empty:
                # Tampilkan
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
