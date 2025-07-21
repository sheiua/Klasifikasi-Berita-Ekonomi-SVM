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

def get_detail_lampost(link):
    try:
        r = requests.get(link, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")

        # Ambil tanggal
        tgl_raw = soup.find("div", class_="jeg_meta_date")
        tanggal = None
        if tgl_raw:
            raw_text = tgl_raw.text.strip().split("–")[0].strip()
            try:
                tanggal = datetime.strptime(raw_text, "%d %B %Y").date()
            except:
                pass

        # Ambil isi artikel
        isi_konten = soup.find("div", class_="entry-content")
        isi = isi_konten.get_text(separator="\n").strip() if isi_konten else ""

        return tanggal, isi
    except Exception as e:
        print(f"❌ Gagal ambil detail: {link}, error: {e}")
        return None, ""

def parse_portal_lampost(keyword='a', start_date=None, end_date=None, max_pages=3):
    from datetime import datetime
    from urllib.parse import urljoin
    import requests
    from bs4 import BeautifulSoup

    def get_detail_lampost(link):
        try:
            r = requests.get(link, timeout=10)
            soup = BeautifulSoup(r.content, "html.parser")

            tgl_raw = soup.find("div", class_="jeg_meta_date")
            tanggal = tgl_raw.text.strip().split("–")[0].strip() if tgl_raw else None

            isi_konten = soup.find("div", class_="entry-content")
            isi = isi_konten.get_text(separator="\n").strip() if isi_konten else None

            return tanggal, isi
        except Exception as e:
            print(f"❌ Gagal ambil detail: {link}, error: {e}")
            return None, None

    base_url = "https://lampost.co/page/{}?s={}"
    hasil = []

    for page in range(1, max_pages + 1):
        url = base_url.format(page, keyword)
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, "html.parser")
            list_artikel = soup.find_all("h3", class_="jeg_post_title")

            if not list_artikel:
                print(f"Tidak ada artikel di halaman {page}")
                continue

            for artikel in list_artikel:
                a_tag = artikel.find("a")
                if not a_tag:
                    continue
                judul = a_tag.text.strip()
                link = urljoin(url, a_tag["href"])
                tanggal_str, isi = get_detail_lampost(link)

                if tanggal_str:
                    try:
                        tanggal_dt = datetime.strptime(tanggal_str, "%d %B %Y").date()
                        if start_date and tanggal_dt < start_date:
                            continue
                        if end_date and tanggal_dt > end_date:
                            continue
                    except Exception as e:
                        print(f"❌ Format tanggal salah: {tanggal_str}, error: {e}")
                        continue

                hasil.append({
                    "tanggal": tanggal_str,
                    "judul": judul,
                    "isi": isi,
                    "link": link
                })
        except Exception as e:
            print(f"❌ Gagal ambil halaman {page}: {e}")

    return hasil
