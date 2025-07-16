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
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    def get_links():
        base_url = f"https://lampung.viva.co.id/search?q={keyword}&page=" if keyword else "https://lampung.viva.co.id/berita?page="
        links = []

        for page in range(1, max_pages + 1):
            url = base_url + str(page)
            print(f"🔎 Mengambil halaman: {url}")

            try:
                res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')

                new_links = [a_tag['href'] for a_tag in soup.find_all('a', class_='article-list-title')
                             if a_tag['href'].startswith('https://lampung.viva.co.id/')]
                links.extend(new_links)

                if not new_links:
                    break

            except Exception as e:
                print(f"[ERROR] Gagal ambil halaman {url}: {e}")
                break

        print(f"✅ Total link ditemukan: {len(links)}")
        return list(set(links))  # hapus duplikat

    def get_tanggal(soup):
        try:
            meta_tag = soup.find('meta', {'property': 'article:published_time'})
            date_content = meta_tag['content'].split(' ')[0]
            return datetime.strptime(date_content, '%Y-%m-%d').date()
        except:
            return None

    def get_teks(soup):
        try:
            paragraphs = soup.find_all('p')
            return " ".join(p.get_text(strip=True) for p in paragraphs)
        except:
            return ""

    links = get_links()

    for i, link in enumerate(links):
        try:
            r = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')

            tanggal = get_tanggal(soup)
            if not tanggal:
                continue
            if start_date and end_date and not (start_date <= tanggal <= end_date):
                continue

            teks = get_teks(soup)

            print(f"\n🔗 [{i+1}] {link}")
            print(f"📅 Tanggal: {tanggal}")
            print(f"📝 Teks (potong): {teks[:100]}...")

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

