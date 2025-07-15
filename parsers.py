import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

# Parser untuk Antara News Lampung
def parse_portal_antara(keyword, start_date, end_date):
    hasil = []
    page = 1
    visited_links = set()
    headers = {"User-Agent": "Mozilla/5.0"}

    if keyword:
        base_url = f"https://lampung.antaranews.com/search?q={keyword}&page="
    else:
        base_url = f"https://lampung.antaranews.com/terkini?page="

    while True:
        url = base_url + str(page)
        print(f"[ANTARA] Mengambil halaman: {url}")

        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            links = []
            for a in soup.select("a[href]"):
                href = a["href"]
                if href.startswith("/berita/"):
                    full_link = "https://lampung.antaranews.com" + href
                    links.append(full_link)
                elif href.startswith("https://lampung.antaranews.com/berita/"):
                    links.append(href)

            if not links:
                print("[ANTARA] Tidak ada artikel ditemukan.")
                break

            for full_link in links:
                if full_link in visited_links:
                    continue
                visited_links.add(full_link)

                try:
                    r_detail = requests.get(full_link, headers=headers, timeout=10)
                    artikel = BeautifulSoup(r_detail.text, "html.parser")

                    isi_div = artikel.find("div", class_="post-content clearfix font17")
                    teks = " ".join(p.get_text(strip=True) for p in isi_div.find_all("p")) if isi_div else ""

                    time_tag = artikel.find("time")
                    if time_tag and time_tag.has_attr("datetime"):
                        try:
                            tanggal = datetime.strptime(time_tag["datetime"], "%Y-%m-%dT%H:%M:%S%z").date()
                        except:
                            tanggal = datetime.today().date()
                    else:
                        tanggal = datetime.today().date()

                    if start_date <= tanggal <= end_date:
                        hasil.append({"link": full_link, "tanggal": tanggal, "teks": teks})
                        print(f"[{len(hasil)}] {tanggal} - {full_link}")

                except Exception as e:
                    print(f"[ERROR] Gagal scraping artikel {full_link}: {e}")

                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Gagal ambil halaman {url}: {e}")
            break

        page += 1

    return hasil

# Parser untuk Viva Lampung
def parse_portal_viva(keyword, start_date, end_date):
    hasil = []
    page = 1
    visited_links = set()
    headers = {"User-Agent": "Mozilla/5.0"}

    def parse_tanggal_viva(tanggal_str):
        bulan_indo = {
            'Januari': 'January', 'Februari': 'February', 'Maret': 'March', 'April': 'April',
            'Mei': 'May', 'Juni': 'June', 'Juli': 'July', 'Agustus': 'August',
            'September': 'September', 'Oktober': 'October', 'November': 'November', 'Desember': 'December'
        }
        for indo, eng in bulan_indo.items():
            tanggal_str = tanggal_str.replace(indo, eng)
        tanggal_str = tanggal_str.split("–")[0].strip()
        tanggal_str = " ".join(tanggal_str.split(",")[1:]).strip()
        return datetime.strptime(tanggal_str, "%d %B %Y").date()

    if keyword:
        base_url = f"https://lampung.viva.co.id/search?q={keyword}&page="
    else:
        base_url = f"https://lampung.viva.co.id/berita?page="

    while True:
        url = base_url + str(page)
        print(f"[VIVA] Mengambil halaman: {url}")

        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            links = ["https://lampung.viva.co.id" + a["href"] for a in soup.select("a[href^='/berita/']")]
            if not links:
                print("[VIVA] Tidak ada artikel lagi.")
                break

            for link in links:
                if link in visited_links:
                    continue
                visited_links.add(link)

                try:
                    res_artikel = requests.get(link, headers=headers, timeout=10)
                    soup_artikel = BeautifulSoup(res_artikel.text, "html.parser")

                    isi_div = soup_artikel.find("div", class_="article-detail-body")
                    teks = " ".join(p.get_text(strip=True) for p in isi_div.find_all("p")) if isi_div else ""

                    waktu_div = soup_artikel.find("div", class_="article-time")
                    tanggal = parse_tanggal_viva(waktu_div.get_text(strip=True)) if waktu_div else datetime.today().date()

                    if start_date <= tanggal <= end_date:
                        hasil.append({"link": link, "tanggal": tanggal, "teks": teks})
                        print(f"[{len(hasil)}] {tanggal} - {link}")

                except Exception as e:
                    print(f"[ERROR] Viva gagal proses {link}: {e}")

                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Viva gagal akses halaman {url}: {e}")
            break

        page += 1

    return hasil

# Parser untuk Lampung Post
def parse_portal_lampost(keyword, start_date, end_date):
    hasil = []
    page = 1
    visited_links = set()
    headers = {"User-Agent": "Mozilla/5.0"}

    def parse_tanggal(tanggal_str):
        bulan_indo = {
            'Januari': 'January', 'Februari': 'February', 'Maret': 'March', 'April': 'April',
            'Mei': 'May', 'Juni': 'June', 'Juli': 'July', 'Agustus': 'August',
            'September': 'September', 'Oktober': 'October', 'November': 'November', 'Desember': 'December'
        }
        for indo, eng in bulan_indo.items():
            tanggal_str = tanggal_str.replace(indo, eng)
        return datetime.strptime(tanggal_str, "%d %B %Y").date()

    while True:
        if keyword:
            url = f"https://lampost.co/page/{page}/?s={keyword}"
        else:
            url = f"https://lampost.co/page/{page}/"

        print(f"[LAMPOST] Mengambil halaman: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            links = [a["href"] for a in soup.select("a[href^='https://lampost.co/']") if "/page/" not in a["href"]]
            if not links:
                print("[LAMPOST] Tidak ada artikel ditemukan.")
                break

            for link in links:
                if link in visited_links:
                    continue
                visited_links.add(link)
                try:
                    r = requests.get(link, headers=headers, timeout=10)
                    soup_detail = BeautifulSoup(r.text, "html.parser")

                    isi = soup_detail.find("div", class_="detail-news-content")
                    teks = " ".join(p.get_text(strip=True) for p in isi.find_all("p")) if isi else ""

                    tanggal_div = soup_detail.find("div", class_="date")
                    if tanggal_div:
                        tanggal = parse_tanggal(tanggal_div.get_text(strip=True))
                    else:
                        tanggal = datetime.today().date()

                    if start_date <= tanggal <= end_date:
                        hasil.append({"link": link, "tanggal": tanggal, "teks": teks})
                        print(f"[{len(hasil)}] {tanggal} - {link}")

                except Exception as e:
                    print(f"[ERROR] Lampost gagal proses {link}: {e}")
                time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Lampost gagal akses {url}: {e}")
            break

        page += 1

    return hasil

# Parser untuk Radar Lampung
def parse_portal_radar(keyword, start_date, end_date):
    hasil = []
    offset = 0
    limit = 10
    visited_links = set()
    headers = {"User-Agent": "Mozilla/5.0"}

    def parse_tanggal(t):
        try:
            return datetime.strptime(t.strip(), "%A, %d %b %Y %H:%M WIB").date()
        except:
            return datetime.today().date()

    while True:
        if keyword:
            url = f"https://radarlampung.disway.id/search/kata/{offset}/{limit}/?c={keyword}&num="
        else:
            url = f"https://radarlampung.disway.id/search/kata/{offset}/{limit}/?num="

        print(f"[RADAR] Mengambil halaman: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = ["https://radarlampung.disway.id" + a["href"] for a in soup.select("a[href^='/read/']")]
            if not links:
                print("[RADAR] Tidak ada artikel ditemukan.")
                break

            for link in links:
                if link in visited_links:
                    continue
                visited_links.add(link)

                try:
                    r = requests.get(link, headers=headers, timeout=10)
                    soup_detail = BeautifulSoup(r.text, "html.parser")
                    isi = soup_detail.find("div", class_="article-paragraph")
                    teks = " ".join(p.get_text(strip=True) for p in isi.find_all("p")) if isi else ""
                    tanggal_div = soup_detail.find("div", class_="article-date")
                    tanggal = parse_tanggal(tanggal_div.get_text()) if tanggal_div else datetime.today().date()
                    if start_date <= tanggal <= end_date:
                        hasil.append({"link": link, "tanggal": tanggal, "teks": teks})
                        print(f"[{len(hasil)}] {tanggal} - {link}")
                except Exception as e:
                    print(f"[ERROR] Radar gagal proses {link}: {e}")
                time.sleep(1)
        except Exception as e:
            print(f"[ERROR] Radar gagal akses {url}: {e}")
            break

        offset += limit

    return hasil

# Parser untuk Sinar Lampung
def parse_portal_sinar(keyword, start_date, end_date):
    hasil = []
    page = 1
    visited_links = set()
    headers = {"User-Agent": "Mozilla/5.0"}

    def parse_tanggal_from_url(url):
        try:
            match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
            if match:
                y, m, d = match.groups()
                return datetime(int(y), int(m), int(d)).date()
        except:
            pass
        return datetime.today().date()

    while True:
        if keyword:
            url = f"https://sinarlampung.co/?s={keyword}&page={page}"
        else:
            url = f"https://sinarlampung.co/page/{page}/"

        print(f"[SINAR] Mengambil halaman: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("https://sinarlampung.co/202")]
            if not links:
                print("[SINAR] Tidak ada artikel lagi.")
                break
            for link in links:
                if link in visited_links:
                    continue
                visited_links.add(link)
                try:
                    res_detail = requests.get(link, headers=headers, timeout=10)
                    soup_detail = BeautifulSoup(res_detail.text, "html.parser")
                    konten_div = soup_detail.find("div", class_="td-post-content tagdiv-type")
                    teks = " ".join(p.get_text(strip=True) for p in konten_div.find_all("p")) if konten_div else ""
                    tanggal = parse_tanggal_from_url(link)
                    if start_date <= tanggal <= end_date:
                        hasil.append({"link": link, "tanggal": tanggal, "teks": teks})
                        print(f"[{len(hasil)}] {tanggal} - {link}")
                except Exception as e:
                    print(f"[ERROR] Sinar gagal proses artikel {link}: {e}")
                time.sleep(1)
        except Exception as e:
            print(f"[ERROR] Sinar gagal buka halaman {url}: {e}")
            break
        page += 1

    return hasil
