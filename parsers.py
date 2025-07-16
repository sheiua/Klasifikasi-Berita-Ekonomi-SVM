import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import time
import pandas as pd

# Parser final debug-friendly untuk Antara News Lampung
def parse_portal_antara(keyword=None, start_date=None, end_date=None, max_pages=10):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    def get_links():
        base_url = f"https://lampung.antaranews.com/search?q={keyword}&page=" if keyword else "https://lampung.antaranews.com/terkini?page="
        links = []

        for page in range(1, max_pages + 1):
            url = base_url + str(page)
            print(f"🔎 Mengambil halaman: {url}")

            try:
                res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.content, 'html.parser')

                h3_tags = soup.find_all('h3')
                for h3 in h3_tags:
                    a = h3.find('a', href=True)
                    if a and 'berita' in a['href']:
                        link = a['href']
                        if not link.startswith("http"):
                            link = "https://lampung.antaranews.com" + link
                        links.append(link)

            except Exception as e:
                print(f"[ERROR] Gagal ambil halaman: {e}")
                continue

        print(f"✅ Total link ditemukan: {len(links)}")
        return links

    def get_tanggal(soup):
        try:
            raw = soup.find('meta', {'itemprop': 'datePublished'})['content']
            tanggal = datetime.strptime(raw, '%a, %d %b %Y %H:%M:%S %z').date()
            return tanggal
        except Exception as e:
            print(f"[WARN] Gagal parsing tanggal: {e}")
            return None

    def get_teks(soup):
        try:
            konten = soup.find('div', itemprop="articleBody")
            teks = konten.get_text(" ", strip=True).split("Baca juga:")[0]
            return teks
        except:
            return ""

    links = get_links()

    for i, link in enumerate(links):
        try:
            r = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')

            tanggal = get_tanggal(soup)
            teks = get_teks(soup)

            print(f"\n🔗 [{i+1}] {link}")
            print(f"📅 Ditemukan: {tanggal}")
            print(f"📅 Rentang: {start_date} s.d. {end_date}")

            # ✅ Filter tanggal aktif
            if start_date and end_date:
                if tanggal is None:
                    print("⏭️ Lewat: Tanggal kosong")
                    continue
                if not (start_date <= tanggal <= end_date):
                    print("⏭️ Lewat: Di luar rentang")
                    continue

            results.append({
                "link": link,
                "tanggal": tanggal,
                "teks": teks
            })

            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Gagal scraping artikel: {e}")
            continue

    print(f"✅ Total artikel sesuai tanggal: {len(results)}")
    return results
