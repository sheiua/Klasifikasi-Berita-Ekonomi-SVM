# app.py

import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from parsers import parse_portal_antara, parse_portal_viva, parse_portal_lampost, parse_portal_radar, parse_portal_sinar

# ✅ Load model
model = joblib.load("model_svm_berita.pkl")

# ✅ UI
st.title("Berita Ekonomi Scraper & Klasifikasi")

# Pilih portal
portal = st.selectbox(
    "Pilih Portal Berita:",
    ["Antara News Lampung", "Viva Lampung", "Lampung POST", "Radar Lampung", "Sinar Lampung"]
)

# Input keyword
keyword = st.text_input("Masukkan keyword pencarian", value="ekonomi")

# Rentang tanggal
start_date = st.date_input("Tanggal mulai", value=pd.to_datetime("2025-07-01"))
end_date = st.date_input("Tanggal akhir", value=pd.to_datetime("2025-07-31"))

if st.button("Mulai Scraping & Klasifikasi"):
    st.info(f"Scraping berita dari {portal}...")

    if portal == "Antara News Lampung":
        hasil = parse_portal_antara(keyword, start_date, end_date)
    elif portal == "Viva Lampung":
        hasil = parse_portal_viva(keyword, start_date, end_date)
    elif portal == "Lampung POST":
        hasil = parse_portal_lampost(keyword, start_date, end_date)
    elif portal == "Radar Lampung":
        hasil = parse_portal_radar(keyword, start_date, end_date)
    elif portal == "Sinar Lampung":
        hasil = parse_portal_sinar(keyword, start_date, end_date)
    else:
        hasil = []

    if len(hasil) == 0:
        st.warning("Tidak ada data ditemukan.")
    else:
        # Convert ke DataFrame
        df = pd.DataFrame(hasil)

        # Prediksi kolom 'teks'
        df['label'] = model.predict(df['teks'])

        # Filter hanya Ekonomi (label = 1)
        df_ekonomi = df[df['label'] == 1]

        st.success(f"Jumlah berita ekonomi: {len(df_ekonomi)}")

        # Tampilkan tabel
        st.dataframe(df_ekonomi[['link', 'tanggal', 'teks']])

        # Download Excel
        output_file = "Berita_Ekonomi.xlsx"
        df_ekonomi.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button("📥 Download Hasil Berita Ekonomi", f, file_name="Berita_Ekonomi.xlsx")
