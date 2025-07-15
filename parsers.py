import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from dateutil import parser

# ====================
# 1. Antara News Lampung
# ====================
def parse_portal_antara(keyword, start_date, end_date):
    hasil = []
    page = 1
    base_url = f"https://lampung.antaranews.com/search?q={keyword}&page="

    while True:
        url = base_url + str(page)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.select("a[href^='/berita/']")
        if not links:
            break

        for a in links:
            link = "https://lampung.antaranews.com" + a["href"]

            try:
                res_artikel = requests.get(link)
                soup_artikel = BeautifulSoup(res_artikel.text, "html.parser")

                isi_div = soup_artikel.find("div", class_="post-content clearfix font17")
                teks = " ".join(p.get_text(strip=True) for p in isi_div.find_all("p")) if isi_div else ""

                time_tag = soup_artikel.find("time")
                if time_tag:
                    tanggal = parser.parse(time_tag.get_text(strip=True)).date()
                else:
                    tanggal = datetime.today().date()

                if start_date <= tanggal <= end_date:
                    hasil.append({
                        "link": link,
                        "tanggal": tanggal,
                        "teks": teks
                    })
            except:
                pass

            time.sleep(1)

        page += 1

    return hasil

# ====================
# 2. Viva Lampung
# ====================
def parse_portal_viva(keyword, start_date, end_date):
    hasil = []
    page = 1
    visited_links = set()
    base_url = f"https://lampung.viva.co.id/search?q={keyword}&page="

    def parse_tanggal_viva(tanggal_str):
        try:
            return parser.parse(tanggal_str).date()
        except:
            return datetime.today().date()

    while True:
        url = base_url + str(page)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.select("a[href^='/berita/']")
        if not links:
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

                isi_div = soup_artikel.find("div", class_="article-detail-body")
                teks = " ".join(p.get_text(strip=True) for p in isi_div.find_all("p")) if isi_div else ""

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
            except:
                pass

            time.sleep(1)

        page += 1

    return hasil

# ====================
# 3. Lampung Post
# ====================
def parse_portal_lampost(keyword, start_date, end_date):
    hasil = []
    page = 1
    base_url = f"https://lampost.co/page/{page}/?s={keyword}"

    while True:
        url = f"https://lampost.co/page/{page}/?s={keyword}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.select("h2.entry-title > a")
        if not links:
            break

        for a in links:
            link = a["href"]
            try:
                res_artikel = requests.get(link)
                soup_artikel = BeautifulSoup(res_artikel.text, "html.parser")

                isi_div = soup_artikel.find("div", class_="td-post-content tagdiv-type")
                teks = " ".join(p.get_text(strip=True) for p in isi_div.find_all("p")) if isi_div else ""

                tanggal_tag = soup_artikel.find("time", class_="entry-date updated td-module-date")
                if tanggal_tag:
                    tanggal = parser.parse(tanggal_tag.get_text(strip=True)).date()
                else:
                    tanggal = datetime.today().date()

                if start_date <= tanggal <= end_date:
                    hasil.append({
                        "link": link,
                        "tanggal": tanggal,
                        "teks": teks
                    })
            except:
                pass

            time.sleep(1)

        page += 1

    return hasil

# ====================
# 4. Radar Lampung
# ====================
def parse_portal_radar(keyword, start_date, end_date):
    hasil = []
    offset = 0
    limit = 10
    base_url = "https://radarlampung.disway.id/search/kata/{offset}/{limit}/?c={keyword}&num="

    while True:
        url = base_url.format(offset=offset, limit=limit, keyword=keyword)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        articles = soup.select("a.card-title")
        if not articles:
            break

        for a in articles:
            link = "https://radarlampung.disway.id" + a["href"]

            try:
                res_detail = requests.get(link)
                soup_detail = BeautifulSoup(res_detail.text, "html.parser")

                isi = soup_detail.find("div", class_="article-content")
                teks = " ".join(p.get_text(strip=True) for p in isi.find_all("p")) if isi else ""

                tanggal_div = soup_detail.find("div", class_="article-date")
                if tanggal_div:
                    tanggal = parser.parse(tanggal_div.get_text(strip=True)).date()
                else:
                    tanggal = datetime.today().date()

                if start_date <= tanggal <= end_date:
                    hasil.append({
                        "link": link,
                        "tanggal": tanggal,
                        "teks": teks
                    })
            except:
                pass

            time.sleep(1)

        offset += limit

    return hasil

# ====================
# 5. Sinar Lampung
# ====================
def parse_portal_sinar(keyword, start_date, end_date):
    hasil = []
    page = 1
    base_url = f"https://sinarlampung.co/?s={keyword}&page="

    while True:
        url = base_url + str(page)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.select("h2.entry-title > a")
        if not links:
            break

        for a in links:
            link = a["href"]

            try:
                res_artikel = requests.get(link)
                soup_artikel = BeautifulSoup(res_artikel.text, "html.parser")

                isi_div = soup_artikel.find("div", class_="td-post-content tagdiv-type")
                teks = " ".join(p.get_text(strip=True) for p in isi_div.find_all("p")) if isi_div else ""

                tanggal_tag = soup_artikel.find("time", class_="entry-date updated td-module-date")
                if tanggal_tag:
                    tanggal = parser.parse(tanggal_tag.get_text(strip=True)).date()
                else:
                    tanggal = datetime.today().date()

                if start_date <= tanggal <= end_date:
                    hasil.append({
                        "link": link,
                        "tanggal": tanggal,
                        "teks": teks
                    })
            except:
                pass

            time.sleep(1)

        page += 1

    return hasil
