# parsers.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Contoh parser dummy untuk Antara News Lampung
def parse_portal_antara(keyword, start_date, end_date):
    hasil = []
    base_url = f"https://lampung.antaranews.com/search?q={keyword}&page="
    for page in range(1, 3):  # Ambil 2 halaman contoh
        url = base_url + str(page)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        # Contoh dummy selector (HARUS kamu sesuaikan!)
        links = soup.find_all("a", href=True)

        for a in links:
            link = a["href"]
            if not link.startswith("http"):
                link = "https://lampung.antaranews.com" + link

            # GET isi artikel
            res = requests.get(link)
            artikel = BeautifulSoup(res.text, "html.parser")

            # Ambil teks isi artikel (contoh dummy)
            teks = " ".join([p.get_text() for p in artikel.find_all("p")])

            # Dummy tanggal publish
            tanggal = datetime.today().date()

            # Filter rentang tanggal
            if start_date <= tanggal <= end_date:
                hasil.append({"link": link, "tanggal": tanggal, "teks": teks})

    return hasil

# Contoh parser dummy untuk Viva Lampung
def parse_portal_viva(keyword, start_date, end_date):
    hasil = []
    base_url = f"https://lampung.viva.co.id/search?q={keyword}&page="
    for page in range(1, 3):
        url = base_url + str(page)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.find_all("a", href=True)

        for a in links:
            link = a["href"]
            if not link.startswith("http"):
                link = "https://lampung.viva.co.id" + link

            res = requests.get(link)
            artikel = BeautifulSoup(res.text, "html.parser")
            teks = " ".join([p.get_text() for p in artikel.find_all("p")])
            tanggal = datetime.today().date()

            if start_date <= tanggal <= end_date:
                hasil.append({"link": link, "tanggal": tanggal, "teks": teks})

    return hasil

# Contoh parser dummy untuk Lampung POST
def parse_portal_lampost(keyword, start_date, end_date):
    hasil = []
    base_url = f"https://lampost.co/page/1/?s={keyword}"
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, "html.parser")

    links = soup.find_all("a", href=True)

    for a in links:
        link = a["href"]
        if not link.startswith("http"):
            link = "https://lampost.co" + link

        res = requests.get(link)
        artikel = BeautifulSoup(res.text, "html.parser")
        teks = " ".join([p.get_text() for p in artikel.find_all("p")])
        tanggal = datetime.today().date()

        if start_date <= tanggal <= end_date:
            hasil.append({"link": link, "tanggal": tanggal, "teks": teks})

    return hasil

# Contoh parser dummy untuk Radar Lampung
def parse_portal_radar(keyword, start_date, end_date):
    hasil = []
    base_url = f"https://radarlampung.disway.id/search/kata/0/10/?c={keyword}&num="
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, "html.parser")

    links = soup.find_all("a", href=True)

    for a in links:
        link = a["href"]
        if not link.startswith("http"):
            link = "https://radarlampung.disway.id" + link

        res = requests.get(link)
        artikel = BeautifulSoup(res.text, "html.parser")
        teks = " ".join([p.get_text() for p in artikel.find_all("p")])
        tanggal = datetime.today().date()

        if start_date <= tanggal <= end_date:
            hasil.append({"link": link, "tanggal": tanggal, "teks": teks})

    return hasil

# Contoh parser dummy untuk Sinar Lampung
def parse_portal_sinar(keyword, start_date, end_date):
    hasil = []
    base_url = f"https://sinarlampung.co/?s={keyword}&page="
    for page in range(1, 3):
        url = base_url + str(page)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.find_all("a", href=True)

        for a in links:
            link = a["href"]
            if not link.startswith("http"):
                link = "https://sinarlampung.co" + link

            res = requests.get(link)
            artikel = BeautifulSoup(res.text, "html.parser")
            teks = " ".join([p.get_text() for p in artikel.find_all("p")])
            tanggal = datetime.today().date()

            if start_date <= tanggal <= end_date:
                hasil.append({"link": link, "tanggal": tanggal, "teks": teks})

    return hasil
