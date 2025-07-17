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
    base_url = "https://lampungpro.co/index.php?page=berita&halaman="
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    def get_links():
        links = []
        for page in range(1, max_pages + 1):
            url = base_url + str(page)
            print(f"📄 Halaman: {url}")
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code != 200:
                    continue
                soup = BeautifulSoup(res.content, 'html.parser')
                a_tags = soup.find_all("a", href=True, class_="font-normal")
                if not a_tags:
                    print("⛔ Tidak ada artikel di halaman ini.")
                    break
                for a in a_tags:
                    link = a['href']
                    if not link.startswith("http"):
                        link = "https://lampungpro.co" + link
                    links.append(link)
            except Exception as e:
                print(f"[ERROR] Gagal ambil halaman: {e}")
                continue
        print(f"📰 Total artikel ditemukan: {len(links)}")
        return links

    def get_tanggal(soup):
        try:
            waktu = soup.find("span", class_="post-date")
            raw = waktu.get_text(strip=True)
            tanggal_bersih = raw.split(",")[-1].strip()
            tanggal_obj = datetime.strptime(tanggal_bersih, "%d %B %Y").date()
            return tanggal_obj
        except Exception as e:
            print("Tanggal tidak ditemukan:", e)
            return None

    def get_teks(soup):
        try:
            isi = soup.find("div", class_="post-content")
            return isi.get_text(" ", strip=True)
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


