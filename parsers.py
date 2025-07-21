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

        print(f"🔗 Total link ditemukan: {len(links)}")
        return links

    def get_tanggal(soup):
        try:
            time_tag = soup.find("time", itemprop="datePublished")
            if time_tag and time_tag.has_attr("datetime"):
                raw = time_tag["datetime"]
                tanggal = raw.split(",")[1].strip().split(" ")[0:3]
                date_str = " ".join(tanggal)
                return datetime.strptime(date_str, "%d %b %Y").date()
        except Exception as e:
            print(f"[tanggal ERROR] {e}")
        return None

    def get_teks(soup):
        try:
            konten = soup.find('article', itemprop="articleBody")
            if not konten:
                return ""
            paragraphs = konten.find_all('p')
            isi = " ".join(p.get_text(strip=True) for p in paragraphs if "ads_antaranews" not in p.get("class", []))
            return isi.split("Baca juga:")[0]
        except Exception as e:
            print(f"[konten ERROR] {e}")
            return ""

    links = get_links()

    for i, link in enumerate(links):
        try:
            print(f"📄 Artikel ke-{i+1}")
            print(f"🔗 Link: {link}")
            r = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')

            tanggal = get_tanggal(soup)
            teks = get_teks(soup)

            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    continue

            judul = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Tanpa Judul"
            print(f"📅 Tanggal: {tanggal}")
            print(f"📛 Judul: {judul}")

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": teks
            })

            time.sleep(1)
        except Exception as e:
            print(f"[ERROR] Gagal scraping artikel: {e}")
            continue

    print(f"✅ Total artikel berhasil diambil: {len(results)}")
    return results

def parse_portal_viva(max_pages=5):
    base_url = "https://lampung.viva.co.id/berita?page="
    results = []

    for page in range(1, max_pages + 1):
        url = base_url + str(page)
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"Gagal mengakses halaman: {url}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            article_links = soup.find_all("a", class_="article-list-thumb-link")

            for link_tag in article_links:
                link = link_tag.get("href")
                if not link.startswith("http"):
                    link = "https://lampung.viva.co.id" + link

                try:
                    res = requests.get(link, timeout=10)
                    if res.status_code != 200:
                        continue

                    detail_soup = BeautifulSoup(res.text, "html.parser")

                    # Judul
                    title_tag = detail_soup.find("h1")
                    title = title_tag.get_text(strip=True) if title_tag else "Tidak ada judul"

                    # Isi konten
                    paragraphs = detail_soup.find_all("p")
                    isi = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

                    results.append({
                        "judul": title,
                        "link": link,
                        "isi": isi
                    })

                    time.sleep(1)  # agar tidak diblok

                except Exception as e:
                    print("Gagal mengambil detail artikel:", e)

        except Exception as e:
            print("Gagal membuka halaman utama:", e)

    return results

def parse_portal_lampost(start_date=None, end_date=None, max_pages=5):
    results = []
    abjad = ["a", "e", "i", "o", "u"]

    for huruf in abjad:
        for page in range(1, max_pages + 1):
            url = f"https://lampost.co/page/{page}/?s={huruf}"
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            articles = soup.select("div.card-content h2 a")

            if not articles:
                break

            for a in articles:
                link = a.get("href")
                judul = a.text.strip()
                isi, tanggal = get_isi_lampost(link)

                if not isi or not tanggal:
                    continue

                if start_date and tanggal < start_date: continue
                if end_date and tanggal > end_date: continue

                results.append({
                    "tanggal": tanggal.strftime("%Y-%m-%d"),
                    "judul": judul,
                    "link": link,
                    "isi": isi
                })

            time.sleep(1)
    return results

def get_isi_lampost(link):
    try:
        resp = requests.get(link)
        soup = BeautifulSoup(resp.text, "html.parser")

        konten = soup.select_one("div.detail-news-content") or soup.select_one("div.post-content")
        isi = konten.get_text(separator=" ", strip=True) if konten else ""

        tgl_tag = soup.find("time")
        if tgl_tag:
            tgl_str = tgl_tag.text.strip()
            try:
                tgl = datetime.strptime(tgl_str, "%A, %d %B %Y")
            except:
                tgl = None
        else:
            tgl = None

        return isi, tgl
    except:
        return "", None
