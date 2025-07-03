# Filter Berita Ekonomi

Aplikasi Streamlit untuk menyaring hanya berita ekonomi dari file Excel, berdasarkan klasifikasi SVM.

## Cara Jalankan

1. Upload file Excel.
2. Model akan memprediksi isi kolom "5. APA yang terjadi pada fenomena ekonomi yang ditemukan ?".
3. File output hanya berisi baris yang diklasifikasi sebagai berita ekonomi.

## Requirements

- Streamlit Cloud compatible
- Python 3.8+
- Lihat requirements.txt

## Jalankan lokal

```bash
pip install -r requirements.txt
streamlit run app.py
