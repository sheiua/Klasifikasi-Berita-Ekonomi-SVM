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

            if tanggal is None:
                print("⚠️ Tanggal tidak ditemukan, gunakan fallback hari ini.")
                tanggal = datetime.today().date()

            if start_date and end_date and not (start_date <= tanggal <= end_date):
                print("⏭️ Lewat: Tidak valid atau di luar rentang tanggal")
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
def parse_portal_lampungpro(keyword=None, start_date=None, end_date=None, max_pages=10):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    for page in range(1, max_pages + 1):
        url = f"https://lampungpro.co/search/{keyword or ''}?page={page}"
        print(f"[LAMPUNGPRO] Mengambil halaman: {url}")

        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.content, "html.parser")
            cards = soup.find_all("div", class_="col-md-4")

            for card in cards:
                a = card.find("a", href=True)
                if not a:
                    continue
                link = a["href"]
                if not link.startswith("http"):
                    link = "https://lampungpro.co" + link

                try:
                    detail = requests.get(link, headers=headers, timeout=10)
                    soup_detail = BeautifulSoup(detail.content, "html.parser")

                    # Tanggal
                    tanggal_div = soup_detail.find("div", class_="news-date")
                    if tanggal_div:
                        tanggal_text = tanggal_div.get_text(strip=True)
                        tanggal = datetime.strptime(tanggal_text, "%d %B %Y").date()
                    else:
                        tanggal = None

                    # Konten
                    konten_div = soup_detail.find("div", class_="news-content")
                    teks = konten_div.get_text(" ", strip=True) if konten_div else ""

                    if tanggal and start_date <= tanggal <= end_date:
                        results.append({
                            "link": link,
                            "tanggal": tanggal,
                            "teks": teks
                        })
                        print(f"[{len(results)}] {tanggal} - {link}")

                    time.sleep(1)

                except Exception as e:
                    print(f"[ERROR] Gagal akses artikel {link}: {e}")

        except Exception as e:
            print(f"[ERROR] Gagal akses halaman pencarian: {e}")
            continue

    return results

