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
                    print(f"⚠️ Tidak ada artikel di page {page} untuk huruf '{huruf}'")
                    continue

                for a in articles:
                    link = a.get("href")
                    judul = a.text.strip()
                    isi, tanggal = get_isi_lampost(link)

                    if not isi or not tanggal:
                        print(f"⛔ Lewat karena isi/tanggal kosong: {judul}")
                        continue

                    # Filter tanggal
                    if start_date and tanggal.date() < start_date:
                        print("⏩ Lewat karena sebelum rentang:", tanggal.date(), "| Rentang:", start_date, "-", end_date)
                        continue
                    if end_date and tanggal.date() > end_date:
                        print("⏩ Lewat karena setelah rentang:", tanggal.date(), "| Rentang:", start_date, "-", end_date)
                        continue

                    print("✅ Disimpan:", tanggal.date(), "| Judul:", judul)

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
        resp = requests.get(link, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Gunakan selector yang benar-benar ada
        konten = soup.select_one("div.content-inner")
        isi = konten.get_text(" ", strip=True) if konten else ""
        if not isi:
            print(f"⚠️ Tidak ditemukan isi untuk: {link}")

        # Ambil tanggal
        tgl_tag = soup.select_one("div.jeg_meta_date a")
        tgl = None
        if tgl_tag:
            tgl_str_full = tgl_tag.text.strip()
            print("🗓️ Ditemukan tanggal (mentah):", tgl_str_full)
            tgl_str = tgl_str_full.split("-")[0].strip()

            try:
                tgl = datetime.strptime(tgl_str, "%d/%m/%y")
            except Exception as e:
                print("❌ Gagal parsing tanggal:", tgl_str, "->", e)

        return isi, tgl

    except Exception as e:
        print("❌ Gagal ambil isi:", e)
        return "", None

def parse_portal_radarlampung(start_date=None, end_date=None, max_pages=5):
    results = []
    for page in range(1, max_pages + 1):
        if page == 1:
            url = "https://radarlampung.disway.id/"
        else:
            url = f"https://radarlampung.disway.id/page/{page}"

        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("div.media-heading a")

            if not links:
                print(f"⚠️ Tidak ada artikel di halaman {page}")
                continue

            for a in links:
                link = a.get("href")
                judul = a.text.strip()
                isi, tanggal = get_isi_radarlampung(link)

                if not isi or not tanggal:
                    print(f"⛔ Lewat karena isi/tanggal kosong: {judul}")
                    continue

                # Filter tanggal
                if start_date and tanggal.date() < start_date:
                    print("⏩ Lewat karena sebelum rentang:", tanggal.date())
                    continue
                if end_date and tanggal.date() > end_date:
                    print("⏩ Lewat karena setelah rentang:", tanggal.date())
                    continue

                print("✅ Disimpan:", tanggal.date(), "| Judul:", judul)

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


def get_isi_radarlampung(link):
    try:
        resp = requests.get(link, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Ambil isi konten utama
        konten = soup.select_one("div.entry-content")
        isi = konten.get_text(" ", strip=True) if konten else ""

        if not isi:
            print(f"⚠️ Tidak ditemukan isi: {link}")

        # Ambil tanggal dari <span class="date">
        tgl_tag = soup.select_one("span.date")
        tgl = None
        if tgl_tag:
            tgl_str_raw = tgl_tag.text.strip()  # Contoh: "Minggu 20-07-2025, 20:17 WIB"
            print("🗓️ Ditemukan tanggal (mentah):", tgl_str_raw)
            
            # Ekstrak hanya bagian tanggal: 20-07-2025
            match = re.search(r"\d{2}-\d{2}-\d{4}", tgl_str_raw)
            if match:
                try:
                    tgl = datetime.strptime(match.group(), "%d-%m-%Y")
                except Exception as e:
                    print("❌ Gagal parsing tanggal:", match.group(), "->", e)

        return isi, tgl

    except Exception as e:
        print("❌ Gagal ambil isi artikel:", e)
        return "", None
