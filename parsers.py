import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

#Antara News
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
            raw = soup.find('meta', {'itemprop': 'datePublished'})['content']
            return datetime.strptime(raw, '%a, %d %b %Y %H:%M:%S %z').date()
        except:
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

#Viva Lampung
def parse_portal_viva(keyword=None, start_date=None, end_date=None, max_pages=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    def get_links():
        base_url = f"https://lampung.viva.co.id/search?q={keyword}&page=" if keyword else "https://lampung.viva.co.id/berita?page="
        links = []

        for page in range(1, max_pages + 1):
            url = base_url + str(page)
            print(f"🔎 Mengambil halaman: {url}")
            try:
                res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.content, 'html.parser')

                found = soup.find_all("a", class_="article-list-title")
                if not found:
                    print("🚫 Tidak ada artikel di halaman ini.")
                    break

                for a in found:
                    href = a.get("href")
                    if href and href.startswith("https://lampung.viva.co.id/berita/"):
                        links.append(href)
            except Exception as e:
                print(f"[ERROR] Gagal ambil halaman: {e}")
                continue

        print(f"✅ Total link ditemukan: {len(links)}")
        return links

    def parse_tanggal(soup):
        try:
            meta = soup.find("meta", {"property": "article:published_time"})
            if meta:
                date_str = meta["content"].split("T")[0]
                return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            pass

        try:
            waktu_div = soup.find("div", class_="article-time")
            if waktu_div:
                text = waktu_div.get_text(strip=True)
                parts = text.split("–")[0].split(",")
                if len(parts) > 1:
                    tanggal_text = parts[1].strip()
                    bulan_map = {
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
                    for indo, eng in bulan_map.items():
                        if indo in tanggal_text:
                            tanggal_text = tanggal_text.replace(indo, eng)
                            break
                    return datetime.strptime(tanggal_text, "%d %B %Y").date()
        except:
            pass

        return None

    def get_teks(soup):
        try:
            isi = soup.find("div", class_="article-detail-body")
            return isi.get_text(" ", strip=True) if isi else ""
        except:
            return ""

    result = []
    links = get_links()

    for i, link in enumerate(links):
        try:
            res = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(res.content, 'html.parser')

            tanggal = parse_tanggal(soup)
            teks = get_teks(soup)

            print(f"\n🔗 [{i+1}] {link}")
            print(f"📅 Tanggal: {tanggal}")
            print(f"📝 Teks (potong): {teks[:80]}...")

            if not tanggal or (start_date and end_date and not (start_date <= tanggal <= end_date)):
                print("⏭️ Lewat: Tidak valid atau di luar rentang tanggal")
                continue

            result.append({
                "link": link,
                "tanggal": tanggal,
                "teks": teks
            })

            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Gagal scraping artikel: {e}")
            continue

    return result
