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
    
def parse_portal_lampost(start_date=None, end_date=None, max_articles=50):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    base_url = "https://lampost.co/"
    results = []

    def get_homepage_links():
        try:
            print(f"🔄 Mengambil artikel dari homepage: {base_url}")
            res = requests.get(base_url, headers=headers, timeout=10)
            print(f"Status: {res.status_code}")
            if res.status_code != 200:
                return []

            soup = BeautifulSoup(res.content, "html.parser")
            cards = soup.select("div.card-body")
            links = []
            for card in cards:
                a = card.find("a", href=True)
                if a:
                    link = a["href"]
                    if not link.startswith("http"):
                        link = "https://lampost.co" + link
                    links.append(link)

            print(f"✅ Ditemukan {len(links)} link dari homepage")
            return links
        except Exception as e:
            print(f"[ERROR homepage] {e}")
            return []

    def get_detail(link):
        try:
            res = requests.get(link, headers=headers, timeout=10)
            if res.status_code != 200:
                return None
            soup = BeautifulSoup(res.content, "html.parser")

            # Ambil tanggal dari detail
            tanggal_tag = soup.find("div", class_="jeg_meta_date")
            tanggal = None
            if tanggal_tag:
                raw = tanggal_tag.get_text(strip=True)
                try:
                    tanggal_str = raw.split("-")[0].strip()  # e.g. "25/07/25"
                    tanggal = datetime.strptime(tanggal_str, "%d/%m/%y").date()
                except Exception as e:
                    print(f"❌ Error parsing tanggal: {e}")
                    tanggal = None

            if start_date and end_date:
                if tanggal is None:
                    print(f"⏩ Lewat (tidak ada tanggal): {link}")
                    return None
                if not (start_date <= tanggal <= end_date):
                    print(f"⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                    return None

            # Ambil isi
            konten = soup.select_one("div.single-post-content") or soup.select_one("div.content-berita")
            isi = ""
            if konten:
                paragraphs = konten.find_all("p")
                isi = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

            judul = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Tanpa Judul"

            return {
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            }
        except Exception as e:
            print(f"[ERROR detail] {e}")
            return None

    links = get_homepage_links()
    print("🚀 Mulai ambil detail artikel...\n")

    for i, link in enumerate(links):
        if i >= max_articles:
            break
        print(f"📄 Artikel ke-{i+1}: {link}")
        detail = get_detail(link)
        if detail:
            results.append(detail)
        time.sleep(0.5)

    print(f"\n🎯 Total artikel berhasil diambil: {len(results)}")
    return results
