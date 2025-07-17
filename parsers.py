import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def parse_portal_lampungpro(keyword=None, start_date=None, end_date=None, max_pages=15):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    base_url = "https://lampungpro.co/index.php?page=berita&halaman="
    hasil = []

    def get_links():
        links = []
        for page in range(1, max_pages + 1):
            url = base_url + str(page)
            print(f"[LAMPUNGPRO] Mengambil halaman: {url}")
            try:
                res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.content, 'html.parser')
                articles = soup.select("div.uk-width-expand a.font-normal")
                for a in articles:
                    href = a.get("href")
                    if href and href.startswith("http"):
                        links.append(href)
            except Exception as e:
                print(f"[ERROR] Gagal ambil halaman: {e}")
                continue
        return links

    def get_tanggal(soup):
        try:
            tag = soup.select_one("span.text-muted")
            if tag:
                raw = tag.get_text(strip=True)
                return datetime.strptime(raw, "%d-%m-%Y").date()
        except:
            pass
        return None

    def get_teks(soup):
        try:
            div = soup.select_one("div.uk-article")
            return div.get_text(" ", strip=True) if div else ""
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
            print(f"📅 Tanggal: {tanggal}")
            print(f"📝 Teks (potong): {teks[:100]}...")

            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print("⏭️ Lewat: Di luar rentang tanggal")
                    continue

            hasil.append({
                "link": link,
                "tanggal": tanggal,
                "teks": teks
            })

            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Gagal scraping artikel: {e}")
            continue

    return hasil
