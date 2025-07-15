import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

# DEBUG: Aktifkan mode debug scraping (True/False)
DEBUG_MODE = True

# Parser untuk Antara News Lampung
def parse_portal_antara(keyword, start_date, end_date):
    hasil = []
    page = 1
    visited_links = set()
    headers = {"User-Agent": "Mozilla/5.0"}

    if keyword:
        base_url = f"https://lampung.antaranews.com/search?q={keyword}&page="
    else:
        base_url = f"https://lampung.antaranews.com/terkini?page="

    while True:
        url = base_url + str(page)
        print(f"[ANTARA] Mengambil halaman: {url}")

        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            links = []
            for a in soup.select("a[href]"):
                href = a["href"]
                if href.startswith("/berita/"):
                    full_link = "https://lampung.antaranews.com" + href
                    links.append(full_link)
                elif href.startswith("https://lampung.antaranews.com/berita/"):
                    links.append(href)

            if not links:
                print("[ANTARA] Tidak ada artikel ditemukan.")
                break

            for full_link in links:
                if full_link in visited_links:
                    continue
                visited_links.add(full_link)

                try:
                    r_detail = requests.get(full_link, headers=headers, timeout=10)
                    artikel = BeautifulSoup(r_detail.text, "html.parser")

                    isi_div = artikel.find("div", class_="post-content clearfix font17")
                    teks = " ".join(p.get_text(strip=True) for p in isi_div.find_all("p")) if isi_div else ""

                    time_tag = artikel.find("time")
                    if time_tag and time_tag.has_attr("datetime"):
                        try:
                            tanggal = datetime.strptime(time_tag["datetime"], "%Y-%m-%dT%H:%M:%S%z").date()
                        except:
                            tanggal = datetime.today().date()
                    else:
                        tanggal = datetime.today().date()

                    if DEBUG_MODE:
                        print("[DEBUG] Link:", full_link)
                        print("[DEBUG] Tanggal:", tanggal)
                        print("[DEBUG] Teks potong:", teks[:80])

                    if start_date <= tanggal <= end_date:
                        hasil.append({"link": full_link, "tanggal": tanggal, "teks": teks})
                        print(f"[{len(hasil)}] {tanggal} - {full_link}")

                except Exception as e:
                    print(f"[ERROR] Gagal scraping artikel {full_link}: {e}")

                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Gagal ambil halaman {url}: {e}")
            break

        page += 1

    return hasil
