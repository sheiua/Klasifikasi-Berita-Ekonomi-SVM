import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

#Antara News
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
            raw = soup.find('meta', {'itemprop': 'datePublished'})['content']
            return datetime.strptime(raw, '%a, %d %b %Y %H:%M:%S %z').date()
        except:
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

#Viva Lampung
def parse_portal_viva(keyword=None, start_date=None, end_date=None, max_pages=10):
    base_url = "https://lampung.viva.co.id/news?page={page}"
    headers = {"User-Agent": "Mozilla/5.0"}
    hasil = []
    visited_links = set()

    def get_tanggal(soup):
        try:
            meta = soup.find('meta', {'property': 'article:published_time'})
            if meta and 'content' in meta.attrs:
                tanggal_str = meta['content'].split('T')[0]  # format: 2024-07-15T07:30:00Z
                return datetime.strptime(tanggal_str, "%Y-%m-%d").date()
        except:
            pass
        return None

    def get_isi(soup):
        try:
            body = soup.find("div", class_="article-detail-body")
            if body:
                return " ".join(p.get_text(strip=True) for p in body.find_all("p"))
        except:
            pass
        return ""

    for page in range(1, max_pages + 1):
        url = base_url.format(page=page)
        print(f"[VIVA] Mengambil halaman: {url}")

        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            artikel_list = soup.select("a.article-list-title")

            if not artikel_list:
                print("[VIVA] Tidak ada artikel di halaman ini.")
                break

            for a in artikel_list:
                link = a.get("href")
                if not link.startswith("http"):
                    link = "https://lampung.viva.co.id" + link
                if link in visited_links:
                    continue
                visited_links.add(link)

                try:
                    detail = requests.get(link, headers=headers, timeout=10)
                    soup_detail = BeautifulSoup(detail.text, "html.parser")

                    tanggal = get_tanggal(soup_detail)
                    teks = get_isi(soup_detail)

                    if not tanggal or not teks:
                        continue

                    if start_date and end_date:
                        if not (start_date <= tanggal <= end_date):
                            continue

                    hasil.append({
                        "link": link,
                        "tanggal": tanggal,
                        "teks": teks
                    })
                    print(f"[{len(hasil)}] {tanggal} - {link}")
                    time.sleep(1)

                except Exception as e:
                    print(f"[ERROR] Gagal ambil detail: {e}")
                    continue

        except Exception as e:
            print(f"[ERROR] Gagal akses halaman: {e}")
            break

    return hasil
