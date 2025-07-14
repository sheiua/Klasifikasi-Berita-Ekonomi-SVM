# parsers.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Contoh parser dummy untuk Antara News Lampung
def parse_portal_antara(keyword, start_date, end_date):
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime
    import time

    hasil = []
    page = 1
    visited_links = set()
    base_url = f"https://lampung.antaranews.com/search?q={keyword}&page="

    while True:
        url = base_url + str(page)
        print(f"[ANTARA] Mengambil halaman: {url}")

        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            # Ambil semua link artikel dari hasil pencarian
            links = soup.select("a[href^='/berita/']")
            if not links:
                print("[ANTARA] Tidak ada artikel ditemukan.")
                break

            for a in links:
                href = a["href"]
                full_link = "https://lampung.antaranews.com" + href

                if full_link in visited_links:
                    continue
                visited_links.add(full_link)

                try:
                    r_detail = requests.get(full_link, timeout=10)
                    artikel = BeautifulSoup(r_detail.text, "html.parser")

                    # Ambil isi artikel
                    isi_div = artikel.find("div", class_="post-content clearfix font17")
                    if isi_div:
                        teks = " ".join(p.get_text(strip=True) for p in isi_div.find_all("p"))
                    else:
                        teks = ""

                    # Ambil tanggal dari tag <time datetime="...">
                    time_tag = artikel.find("time")
                    if time_tag and time_tag.has_attr("datetime"):
                        try:
                            tanggal = datetime.strptime(time_tag["datetime"], "%Y-%m-%dT%H:%M:%S%z").date()
                        except:
                            tanggal = datetime.today().date()
                    else:
                        tanggal = datetime.today().date()

                    # Filter berdasarkan rentang tanggal
                    if start_date <= tanggal <= end_date:
                        hasil.append({
                            "link": full_link,
                            "tanggal": tanggal,
                            "teks": teks
                        })
                        print(f"[{len(hasil)}] {tanggal} - {full_link}")

                except Exception as e:
                    print(f"[ERROR] Gagal scraping artikel {full_link}: {e}")

                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Gagal ambil halaman {url}: {e}")
            break

        page += 1

    return hasil

# Contoh parser dummy untuk Viva Lampung
def parse_portal_viva(keyword, start_date, end_date):
    from bs4 import BeautifulSoup
    import requests
    from datetime import datetime
    import time

    hasil = []
    page = 1
    visited_links = set()

    base_url = f"https://lampung.viva.co.id/search?q={keyword}&page="

    def parse_tanggal_viva(tanggal_str):
        # Format: "Senin, 08 Juli 2024 – 13:11 WIB"
        bulan_indo = {
            'Januari': 'January',
            'Februari': 'February',
            'Maret': 'March',
            'April': 'April',
            'Mei': 'May',
            'Juni': 'June',
            'Juli': 'July',
            'Agustus': 'August',
            'September': 'September',
            'Oktober': 'October',
            'November': 'November',
            'Desember': 'December'
        }
        for indo, eng in bulan_indo.items():
            if indo in tanggal_str:
                tanggal_str = tanggal_str.replace(indo, eng)
                break
        # Ambil bagian tanggalnya saja
        tanggal_str = tanggal_str.split("–")[0].strip()  # buang waktu WIB
        tanggal_str = " ".join(tanggal_str.split(",")[1:]).strip()  # hapus hari

        return datetime.strptime(tanggal_str, "%d %B %Y").date()

    while True:
        url = base_url + str(page)
        print(f"[VIVA] Mengambil halaman: {url}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.select("a[href^='/berita/']")
        if not links:
            print("[VIVA] Tidak ada artikel lagi.")
            break

        for a in links:
            href = a["href"]
            link = "https://lampung.viva.co.id" + href

            if link in visited_links:
                continue
            visited_links.add(link)

            try:
                res_artikel = requests.get(link)
                soup_artikel = BeautifulSoup(res_artikel.text, "html.parser")

                # Isi artikel
                isi_div = soup_artikel.find("div", class_="article-detail-body")
                if isi_div:
                    teks = " ".join(p.get_text(strip=True) for p in isi_div.find_all("p"))
                else:
                    teks = ""

                # Tanggal
                waktu_div = soup_artikel.find("div", class_="article-time")
                if waktu_div:
                    tanggal = parse_tanggal_viva(waktu_div.get_text(strip=True))
                else:
                    tanggal = datetime.today().date()

                if start_date <= tanggal <= end_date:
                    hasil.append({
                        "link": link,
                        "tanggal": tanggal,
                        "teks": teks
                    })
                    print(f"[{len(hasil)}] {tanggal} - {link}")

            except Exception as e:
                print(f"[ERROR] Viva gagal proses {link}: {e}")

            time.sleep(1)

        page += 1

    return hasil

# Contoh parser dummy untuk Lampung POST
def parse_portal_lampost(keyword, start_date, end_date):
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime
    import time

    hasil = []
    page = 1
    visited_links = set()

    def parse_tanggal_lampost(tanggal_str):
        # Contoh: "Senin, 08 Juli 2024 13:45 WIB"
        bulan_indo = {
            'Januari': 'January',
            'Februari': 'February',
            'Maret': 'March',
            'April': 'April',
            'Mei': 'May',
            'Juni': 'June',
            'Juli': 'July',
            'Agustus': 'August',
            'September': 'September',
            'Oktober': 'October',
            'November': 'November',
            'Desember': 'December'
        }
        for indo, eng in bulan_indo.items():
            if indo in tanggal_str:
                tanggal_str = tanggal_str.replace(indo, eng)
                break
        # Ambil tanggal saja tanpa waktu
        tanggal_parts = tanggal_str.split(" ")
        if len(tanggal_parts) >= 4:
            tanggal_str = " ".join(tanggal_parts[1:4])  # ambil: 08 Juli 2024
        else:
            return datetime.today().date()
        return datetime.strptime(tanggal_str, "%d %B %Y").date()

    while True:
        url = f"https://lampost.co/page/{page}/?s={keyword}"
        print(f"[LAMPOST] Mengambil halaman: {url}")

        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            # Cari semua link artikel dari hasil pencarian
            links = [a["href"] for a in soup.find_all("a", href=True)
                     if a["href"].startswith("https://lampost.co/") and "/page/" not in a["href"]]

            if not links:
                print("[LAMPOST] Tidak ada artikel lagi.")
                break

            for link in links:
                if link in visited_links:
                    continue
                visited_links.add(link)

                try:
                    detail_res = requests.get(link, timeout=10)
                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")

                    # Ambil isi artikel
                    isi = detail_soup.find("div", class_="detail-news-content")
                    if isi:
                        teks = " ".join(p.get_text(strip=True) for p in isi.find_all("p"))
                    else:
                        teks = ""

                    # Ambil tanggal
                    tanggal_div = detail_soup.find("div", class_="date")
                    if tanggal_div:
                        tanggal_text = tanggal_div.get_text(strip=True)
                        tanggal = parse_tanggal_lampost(tanggal_text)
                    else:
                        tanggal = datetime.today().date()

                    if start_date <= tanggal <= end_date:
                        hasil.append({
                            "link": link,
                            "tanggal": tanggal,
                            "teks": teks
                        })
                        print(f"[{len(hasil)}] {tanggal} - {link}")

                except Exception as e:
                    print(f"[ERROR] Gagal proses artikel {link}: {e}")

                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Gagal ambil halaman pencarian {url}: {e}")
            break

        page += 1

    return hasil

# Contoh parser dummy untuk Radar Lampung
def parse_portal_radar(keyword, start_date, end_date):
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime
    import time

    hasil = []
    offset = 0
    limit = 10
    visited_links = set()

    def parse_tanggal_radar(tanggal_str):
        # Contoh: Jumat, 12 Jul 2024 10:30 WIB
        try:
            return datetime.strptime(tanggal_str, "%A, %d %b %Y %H:%M %Z").date()
        except:
            try:
                # Fallback tanpa timezone
                return datetime.strptime(tanggal_str, "%A, %d %b %Y %H:%M").date()
            except:
                return datetime.today().date()

    while True:
        url = f"https://radarlampung.disway.id/search/kata/{offset}/{limit}/?c={keyword}&num="
        print(f"[RADAR] Mengambil halaman: {url}")

        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            # Cari semua link artikel
            articles = soup.select("a[href^='/read/']")
            if not articles:
                print("[RADAR] Tidak ada artikel ditemukan.")
                break

            for a in articles:
                href = a["href"]
                link = "https://radarlampung.disway.id" + href

                if link in visited_links:
                    continue
                visited_links.add(link)

                try:
                    detail = requests.get(link, timeout=10)
                    soup_detail = BeautifulSoup(detail.text, "html.parser")

                    isi = soup_detail.find("div", class_="article-paragraph")
                    if isi:
                        teks = " ".join(p.get_text(strip=True) for p in isi.find_all("p"))
                    else:
                        teks = ""

                    tanggal_div = soup_detail.find("div", class_="article-date")
                    if tanggal_div:
                        tanggal_text = tanggal_div.get_text(strip=True)
                        tanggal = parse_tanggal_radar(tanggal_text)
                    else:
                        tanggal = datetime.today().date()

                    if start_date <= tanggal <= end_date:
                        hasil.append({
                            "link": link,
                            "tanggal": tanggal,
                            "teks": teks
                        })
                        print(f"[{len(hasil)}] {tanggal} - {link}")

                except Exception as e:
                    print(f"[ERROR] Gagal proses {link}: {e}")

                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Gagal akses {url}: {e}")
            break

        offset += limit

    return hasil

# Contoh parser dummy untuk Sinar Lampung
def parse_portal_sinar(keyword, start_date, end_date):
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime
    import time
    import re

    hasil = []
    page = 1
    visited_links = set()

    def parse_tanggal_from_url(url):
        # URL format: https://sinarlampung.co/YYYY/MM/DD/slug-berita
        try:
            match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
            if match:
                y, m, d = match.groups()
                return datetime(int(y), int(m), int(d)).date()
        except:
            pass
        return datetime.today().date()

    while True:
        url = f"https://sinarlampung.co/?s={keyword}&page={page}"
        print(f"[SINAR] Mengambil halaman: {url}")

        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            links = [a["href"] for a in soup.find_all("a", href=True)
                     if a["href"].startswith("https://sinarlampung.co/202")]

            if not links:
                print("[SINAR] Tidak ada artikel lagi.")
                break

            for link in links:
                if link in visited_links:
                    continue
                visited_links.add(link)

                try:
                    res_detail = requests.get(link, timeout=10)
                    soup_detail = BeautifulSoup(res_detail.text, "html.parser")

                    konten_div = soup_detail.find("div", class_="td-post-content tagdiv-type")
                    if konten_div:
                        teks = " ".join(p.get_text(strip=True) for p in konten_div.find_all("p"))
                    else:
                        teks = ""

                    tanggal = parse_tanggal_from_url(link)

                    if start_date <= tanggal <= end_date:
                        hasil.append({
                            "link": link,
                            "tanggal": tanggal,
                            "teks": teks
                        })
                        print(f"[{len(hasil)}] {tanggal} - {link}")

                except Exception as e:
                    print(f"[ERROR] Gagal scraping artikel {link}: {e}")

                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Gagal buka pencarian {url}: {e}")
            break

        page += 1

    return hasil
