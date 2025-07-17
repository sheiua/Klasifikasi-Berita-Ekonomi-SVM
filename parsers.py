import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def parse_portal_antara(keyword=None, start_date=None, end_date=None, max_pages=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
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

        return links

    def get_tanggal(soup):
        try:
            tag = soup.find("meta", {"property": "article:published_time"})
            if tag:
                raw = tag["content"].split("T")[0]  # Format: '2024-12-27T...'
                return datetime.strptime(raw, "%Y-%m-%d").date()
        except:
            pass
        return None

    def get_teks(soup):
        try:
            konten = soup.find('div', itemprop="articleBody")
            return konten.get_text(" ", strip=True).split("Baca juga:")[0]
        except:
            return ""

    links = get_links()

    for i, link in enumerate(links):
        try:
            r = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')

            tanggal = get_tanggal(soup)
            teks = get_teks(soup)

            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
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

    return results

def parse_portal_tribun(keyword=None, start_date=None, end_date=None, max_pages=10):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    base_url = f"https://lampung.tribunnews.com/search?q={keyword}&page=" if keyword else "https://lampung.tribunnews.com/index-news.html?page="
    hasil = []

    def get_links():
        links = []
        for page in range(1, max_pages + 1):
            url = base_url + str(page)
            print(f"[TRIBUN] Mengambil halaman: {url}")
            try:
                r = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(r.content, 'html.parser')
                articles = soup.select("div.gsc-thumbnail-inside a.gs-title")
                for a in articles:
                    href = a.get("href")
                    if href and href.startswith("https://lampung.tribunnews.com"):
                        links.append(href)
            except Exception as e:
                print(f"[ERROR] Gagal ambil halaman: {e}")
                continue
        return links

    def get_tanggal_from_url(url):
        try:
            match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day)).date()
        except:
            pass
        return None

    def get_teks(soup):
        try:
            konten = soup.find("div", itemprop="articleBody")
            if not konten:
                konten = soup.find("div", class_="side-article txt-article multi-fontsize")
            return konten.get_text(" ", strip=True) if konten else ""
        except:
            return ""

    links = get_links()

    for i, link in enumerate(links):
        try:
            r = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            tanggal = get_tanggal_from_url(link)
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
