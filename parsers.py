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

def parse_portal_viva(max_pages=5):
    base_url = "https://lampung.viva.co.id/berita?page="
    results = []

    for page in range(1, max_pages + 1):
        url = base_url + str(page)
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        article_links = soup.find_all("a", class_="article-list-thumb-link")

        for link_tag in article_links:
            link = link_tag.get("href")
            if not link.startswith("http"):
                link = "https://lampung.viva.co.id" + link
            try:
                res = requests.get(link, timeout=10)
                detail_soup = BeautifulSoup(res.text, "html.parser")
                title = detail_soup.find("h1").get_text(strip=True)
                paragraphs = detail_soup.find_all("p")
                isi = "\n".join(p.get_text(strip=True) for p in paragraphs)
                results.append({"judul": title, "link": link, "isi": isi})
                time.sleep(1)
            except:
                continue

    return results

def parse_portal_lampost(start_date=None, end_date=None, max_pages=5):
    results = []
    abjad = ["a", "e", "i", "o", "u"]

    for huruf in abjad:
        for page in range(1, max_pages + 1):
            url = f"https://lampost.co/page/{page}/?s={huruf}"
            try:
                resp = requests.get(url, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")
                articles = soup.select("div.jeg_postblock_content h3 a")

                if not articles:
                    break

                for a in articles:
                    link = a.get("href")
                    judul = a.text.strip()
                    isi, tanggal = get_isi_lampost(link)
                    if not isi or not tanggal:
                        continue

                    if start_date and tanggal.date() < start_date:
                        continue
                    if end_date and tanggal.date() > end_date:
                        continue

                    results.append({
                        "tanggal": tanggal.strftime("%Y-%m-%d"),
                        "judul": judul,
                        "link": link,
                        "isi": isi
                    })

                    time.sleep(1)
            except Exception as e:
                print(f"❌ Gagal ambil halaman {page}: {e}")
                continue
    return results

def get_isi_lampost(link):
    try:
        resp = requests.get(link)
        soup = BeautifulSoup(resp.text, "html.parser")

        konten = soup.select_one("div.detail-news-content") or soup.select_one("div.post-content")
        isi = konten.get_text(" ", strip=True) if konten else ""

        # Ambil tanggal dari halaman utama artikel
        tgl_tag = soup.select_one("div.jeg_meta_date a")
        tgl = None
        if tgl_tag:
            tgl_str = tgl_tag.text.strip()
            tgl_str = tgl_str.split("-")[0].strip()  # 🪓 Potong jam, ambil sebelum "-"
            try:
                tgl = datetime.strptime(tgl_str, "%d/%m/%y")  # Gunakan %y karena tahunnya 2 digit (25)
            except Exception as e:
                print("❌ Gagal parsing tanggal:", tgl_str, "->", e)

        return isi, tgl

    except Exception as e:
        print("❌ Gagal get isi:", e)
        return "", None
