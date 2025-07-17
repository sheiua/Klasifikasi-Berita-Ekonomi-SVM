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

def parse_portal_viva(keyword=None, start_date=None, end_date=None, max_pages=10):
    base_url = "https://lampung.viva.co.id/berita"
    results = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}" if page > 1 else base_url
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.select("div.col-md-8 div.card")

        if not articles:
            break

        for article in articles:
            try:
                link_tag = article.find("a", href=True)
                link = "https://lampung.viva.co.id" + link_tag["href"]
                tanggal_tag = article.select_one("div.card-body small.text-muted")
                tanggal_str = tanggal_tag.get_text(strip=True)
                # Contoh format tanggal: "Senin, 15 Juli 2024 | 10:00 WIB"
                tanggal = datetime.strptime(tanggal_str.split("|")[0].strip(), "%A, %d %B %Y")

                if start_date and tanggal.date() < start_date:
                    continue
                if end_date and tanggal.date() > end_date:
                    continue

                # Ambil isi artikel
                artikel_resp = requests.get(link, timeout=10)
                artikel_soup = BeautifulSoup(artikel_resp.text, "html.parser")
                isi_tag = artikel_soup.select_one("div.entry-content")
                isi = isi_tag.get_text(separator=" ", strip=True) if isi_tag else ""

                results.append({
                    "tanggal": tanggal.date().isoformat(),
                    "link": link,
                    "teks": isi
                })
            except Exception as e:
                continue  # Lewati error per artikel

        time.sleep(1)  # Hindari overloading server

    return results
