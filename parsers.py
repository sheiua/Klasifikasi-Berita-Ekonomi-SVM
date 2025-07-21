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
            konten = soup.find('article')
            if not konten:
                konten = soup.find('div', class_="content-detail")
            if not konten:
                print("[Parser Antara] ❌ Konten artikel tidak ditemukan.")
                return ""
            paragraphs = konten.find_all('p')
            isi = " ".join(p.get_text(strip=True) for p in paragraphs if not p.get("class"))
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

def parse_portal_viva(keyword=None, start_date=None, end_date=None, max_pages=10):
    results = []
    base_url = "https://lampung.viva.co.id/berita"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        cards = soup.find_all("div", class_="list-berita")
        for i, card in enumerate(cards):
            a = card.find("a", href=True)
            if not a:
                continue
            link = a["href"]
            if not link.startswith("http"):
                link = "https://lampung.viva.co.id" + link

            r = requests.get(link, headers=headers, timeout=10)
            artikel = BeautifulSoup(r.content, "html.parser")

            judul = artikel.find("h1").get_text(strip=True) if artikel.find("h1") else "Tanpa Judul"
            tanggal_tag = artikel.find("div", class_="date")
            tanggal = None
            if tanggal_tag:
                try:
                    tanggal = datetime.strptime(tanggal_tag.text.strip().split(" WIB")[0], "%A, %d %B %Y %H:%M").date()
                except:
                    pass

            isi_konten = artikel.find("div", class_="article-detail")
            isi = ""
            if isi_konten:
                isi = " ".join(p.get_text(strip=True) for p in isi_konten.find_all("p"))

            if start_date and end_date:
                if tanggal is None or not (start_date <= tanggal <= end_date):
                    continue

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })

            time.sleep(1)
    except Exception as e:
        print(f"[Viva ERROR] {e}")

    return results

def parse_portal_lampost(keyword=None, start_date=None, end_date=None, max_pages=10):
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for page in range(1, max_pages+1):
        url = f"https://lampost.co/page/{page}/?s={keyword}" if keyword else f"https://lampost.co/page/{page}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.content, 'html.parser')
            articles = soup.find_all('h2', class_='title')
            for art in articles:
                a = art.find('a', href=True)
                if not a:
                    continue
                link = a['href']
                r = requests.get(link, headers=headers, timeout=10)
                artikel = BeautifulSoup(r.content, 'html.parser')

                judul = artikel.find('h1').get_text(strip=True) if artikel.find('h1') else 'Tanpa Judul'
                tanggal = None
                time_tag = artikel.find('time')
                if time_tag:
                    try:
                        tanggal = datetime.strptime(time_tag.text.strip(), "%A, %d %B %Y %H:%M WIB").date()
                    except:
                        pass

                isi_konten = artikel.find('div', class_='content')
                isi = ""
                if isi_konten:
                    isi = " ".join(p.get_text(strip=True) for p in isi_konten.find_all("p"))

                if start_date and end_date:
                    if tanggal is None or not (start_date <= tanggal <= end_date):
                        continue

                results.append({
                    "judul": judul,
                    "link": link,
                    "tanggal": tanggal,
                    "isi": isi
                })

                time.sleep(1)
        except Exception as e:
            print(f"[Lampost ERROR] {e}")
            continue

    return results
