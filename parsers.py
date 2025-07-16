import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

# DEBUG: Aktifkan mode debug scraping (True/False)
DEBUG_MODE = True

# Parser untuk Antara News Lampung
def parse_portal_antara(keyword, start_date, end_date):
    from bs4 import BeautifulSoup
    import requests
    from datetime import datetime
    import time

    hasil = []
    headers = {"User-Agent": "Mozilla/5.0"}

    # STEP 1: Ambil semua link pencarian
    def get_links(keyword, max_pages=15):
        base_url = f"https://lampung.antaranews.com/search?q={keyword}&page="
        links = []
        for page in range(1, max_pages + 1):
            url = base_url + str(page)
            try:
                res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.content, 'html.parser')
                h3_tags = soup.find_all('h3', limit=10)
                for h3 in h3_tags:
                    a = h3.find('a', href=True)
                    if a and 'berita' in a['href']:
                        links.append(a['href'])
            except Exception as e:
                print(f"[ERROR] Gagal ambil halaman {url}: {e}")
                break
        return links

    # STEP 2: Kelas parser artikel
    class AntaraScraper:
        def get_tanggal(self, soup):
            try:
                raw = soup.find('meta', {'itemprop': 'datePublished'})['content']
                return datetime.strptime(raw, '%a, %d %b %Y %H:%M:%S %z').date()
            except:
                return None

        def get_content(self, soup):
            try:
                isi = soup.find('div', itemprop="articleBody").get_text(" ", strip=True)
                return isi.split("Baca juga:")[0]
            except:
                return ""

    links = get_links(keyword)
    scraper = AntaraScraper()

    for link in links:
        try:
            res = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(res.content, 'html.parser')
            tanggal = scraper.get_tanggal(soup)
            if not tanggal:
                continue
            if not (start_date <= tanggal <= end_date):
                continue

            teks = scraper.get_content(soup)
            hasil.append({
                "link": link,
                "tanggal": tanggal,
                "teks": teks
            })
            print(f"[{len(hasil)}] {tanggal} - {link}")

            time.sleep(1)
        except Exception as e:
            print(f"[ERROR] Gagal scrape {link}: {e}")
            continue

    return hasil
