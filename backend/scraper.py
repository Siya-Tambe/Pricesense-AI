import requests
from bs4 import BeautifulSoup
import re
import random
import time
from datetime import datetime
from urllib.parse import urlparse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

SUPPORTED_PLATFORMS = {
    "amazon":          "Amazon India",
    "flipkart":        "Flipkart",
    "myntra":          "Myntra",
    "croma":           "Croma",
    "reliancedigital": "Reliance Digital",
    "meesho":          "Meesho",
    "tatacliq":        "Tata CLiQ",
    "snapdeal":        "Snapdeal",
}

def detect_platform(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if "amazon" in domain: return "amazon"
    elif "flipkart" in domain: return "flipkart"
    elif "myntra" in domain: return "myntra"
    elif "croma" in domain: return "croma"
    elif "reliancedigital" in domain: return "reliancedigital"
    elif "meesho" in domain: return "meesho"
    elif "tatacliq" in domain: return "tatacliq"
    elif "snapdeal" in domain: return "snapdeal"
    else: return "unknown"

def get_platform_display_name(platform: str) -> str:
    return SUPPORTED_PLATFORMS.get(platform, platform.capitalize())

def get_headers() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
    }

def clean_price(price_text: str):
    if not price_text: return None
    cleaned = re.sub(r"[^\d.]", "", price_text.replace(",", ""))
    try:
        value = float(cleaned)
        if value < 1 or value > 10000000: return None
        return value
    except ValueError:
        return None

def scrape_amazon(url):
    time.sleep(random.uniform(1.5, 3.0))
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        name = None
        name_tag = soup.find("span", {"id": "productTitle"})
        if name_tag: name = name_tag.get_text(strip=True)
        price = None
        for tag, attrs in [("span", {"class": "a-price-whole"}), ("span", {"id": "priceblock_ourprice"}), ("span", {"class": "a-offscreen"})]:
            pt = soup.find(tag, attrs)
            if pt:
                price = clean_price(pt.get_text())
                if price: break
        thumbnail = None
        img = soup.find("img", {"id": "landingImage"})
        if img: thumbnail = img.get("src")
        return {"name": name, "price": price, "thumbnail": thumbnail, "platform": "amazon", "status": "success" if price else "price_not_found"}
    except Exception as e:
        return {"name": None, "price": None, "thumbnail": None, "platform": "amazon", "status": f"error: {str(e)}"}

def scrape_flipkart(url):
    time.sleep(random.uniform(1.5, 3.0))
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        name = None
        for tag, attrs in [("span", {"class": "VU-ZEz"}), ("span", {"class": "B_NuCI"}), ("h1", {"class": "yhB1nd"})]:
            nt = soup.find(tag, attrs)
            if nt: name = nt.get_text(strip=True); break
        price = None
        for tag, attrs in [("div", {"class": "Nx9bqj"}), ("div", {"class": "CEmiEU"}), ("div", {"class": "_30jeq3"})]:
            pt = soup.find(tag, attrs)
            if pt:
                price = clean_price(pt.get_text())
                if price: break
        thumbnail = None
        img = soup.find("img", {"class": "DByuf4"})
        if img: thumbnail = img.get("src")
        return {"name": name, "price": price, "thumbnail": thumbnail, "platform": "flipkart", "status": "success" if price else "price_not_found"}
    except Exception as e:
        return {"name": None, "price": None, "thumbnail": None, "platform": "flipkart", "status": f"error: {str(e)}"}

def scrape_myntra(url):
    time.sleep(random.uniform(1.5, 3.0))
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        name = None
        nt = soup.find("h1", {"class": "pdp-title"}) or soup.find("h1", {"class": "pdp-name"})
        if nt: name = nt.get_text(strip=True)
        price = None
        pt = soup.find("span", {"class": "pdp-price"}) or soup.find("strong", {"class": "pdp-discounted-price"})
        if pt: price = clean_price(pt.get_text())
        thumbnail = None
        img = soup.find("img", {"class": "image-grid-image"})
        if img: thumbnail = img.get("src")
        return {"name": name, "price": price, "thumbnail": thumbnail, "platform": "myntra", "status": "success" if price else "price_not_found"}
    except Exception as e:
        return {"name": None, "price": None, "thumbnail": None, "platform": "myntra", "status": f"error: {str(e)}"}

def scrape_croma(url):
    time.sleep(random.uniform(1.5, 3.0))
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        name = None
        nt = soup.find("h1", {"class": "pdp-title"}) or soup.find("h1")
        if nt: name = nt.get_text(strip=True)
        price = None
        pt = soup.find("span", {"class": "amount"}) or soup.find("div", {"class": "pdp-price"})
        if pt: price = clean_price(pt.get_text())
        thumbnail = None
        img = soup.find("img", {"class": "product-img"})
        if img: thumbnail = img.get("src")
        return {"name": name, "price": price, "thumbnail": thumbnail, "platform": "croma", "status": "success" if price else "price_not_found"}
    except Exception as e:
        return {"name": None, "price": None, "thumbnail": None, "platform": "croma", "status": f"error: {str(e)}"}

def scrape_reliancedigital(url):
    time.sleep(random.uniform(1.5, 3.0))
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        name = None
        for tag, attrs in [("h1", {"class": "pdp__title"}), ("h1", {"class": "product-title"}), ("h1", {})]:
            nt = soup.find(tag, attrs)
            if nt: name = nt.get_text(strip=True); break
        price = None
        for tag, attrs in [("span", {"class": "final-price"}), ("div", {"class": "pdp__offerPrice"}), ("span", {"class": "pdp__offerPrice"}), ("span", {"class": "price"})]:
            pt = soup.find(tag, attrs)
            if pt:
                price = clean_price(pt.get_text())
                if price: break
        thumbnail = None
        img = soup.find("img", {"class": "image-zoom__image"})
        if img: thumbnail = img.get("src")
        return {"name": name, "price": price, "thumbnail": thumbnail, "platform": "reliancedigital", "status": "success" if price else "price_not_found"}
    except Exception as e:
        return {"name": None, "price": None, "thumbnail": None, "platform": "reliancedigital", "status": f"error: {str(e)}"}

def scrape_meesho(url):
    time.sleep(random.uniform(2.0, 4.0))
    try:
        headers = get_headers()
        headers["Referer"] = "https://www.meesho.com/"
        response = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(response.text, "html.parser")
        name = None
        for tag, attrs in [("h1", {"class": "sc-eDvSVe"}), ("h1", {})]:
            nt = soup.find(tag, attrs)
            if nt:
                text = nt.get_text(strip=True)
                if len(text) > 5: name = text; break
        price = None
        for tag, attrs in [("h4", {"class": "sc-eDvSVe"}), ("span", {"class": "price"})]:
            pt = soup.find(tag, attrs)
            if pt:
                price = clean_price(pt.get_text())
                if price: break
        if not price:
            for script in soup.find_all("script", {"type": "application/json"}):
                content = script.get_text()
                for pattern in [r'"price"\s*:\s*(\d+)', r'"mrp"\s*:\s*(\d+)']:
                    m = re.search(pattern, content)
                    if m: price = float(m.group(1)); break
                if price: break
        thumbnail = None
        img = soup.find("img", {"class": "sc-fHCHyC"})
        if img: thumbnail = img.get("src")
        return {"name": name, "price": price, "thumbnail": thumbnail, "platform": "meesho", "status": "success" if price else "price_not_found"}
    except Exception as e:
        return {"name": None, "price": None, "thumbnail": None, "platform": "meesho", "status": f"error: {str(e)}"}

def scrape_tatacliq(url):
    time.sleep(random.uniform(1.5, 3.0))
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        name = None
        for tag, attrs in [("h1", {"class": "pdp-e-i-head"}), ("h1", {})]:
            nt = soup.find(tag, attrs)
            if nt: name = nt.get_text(strip=True); break
        price = None
        for tag, attrs in [("span", {"class": "pdp-e-i-plain-price"}), ("span", {"class": "pdp-price"})]:
            pt = soup.find(tag, attrs)
            if pt:
                price = clean_price(pt.get_text())
                if price: break
        thumbnail = None
        img = soup.find("img", {"class": "pdp-e-i-img"})
        if img: thumbnail = img.get("src")
        return {"name": name, "price": price, "thumbnail": thumbnail, "platform": "tatacliq", "status": "success" if price else "price_not_found"}
    except Exception as e:
        return {"name": None, "price": None, "thumbnail": None, "platform": "tatacliq", "status": f"error: {str(e)}"}

def scrape_snapdeal(url):
    time.sleep(random.uniform(1.5, 3.0))
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        name = None
        nt = soup.find("h1", {"class": "pdp-e-i-head"}) or soup.find("span", {"itemprop": "name"})
        if nt: name = nt.get_text(strip=True)
        price = None
        for tag, attrs in [("span", {"id": "selling-price-id"}), ("span", {"class": "payBlkBig"}), ("div", {"class": "price-val"})]:
            pt = soup.find(tag, attrs)
            if pt:
                price = clean_price(pt.get_text())
                if price: break
        thumbnail = None
        img = soup.find("img", {"id": "product-image"})
        if img: thumbnail = img.get("src")
        return {"name": name, "price": price, "thumbnail": thumbnail, "platform": "snapdeal", "status": "success" if price else "price_not_found"}
    except Exception as e:
        return {"name": None, "price": None, "thumbnail": None, "platform": "snapdeal", "status": f"error: {str(e)}"}

def scrape_product(url: str) -> dict:
    platform = detect_platform(url)
    scrapers = {
        "amazon": scrape_amazon, "flipkart": scrape_flipkart,
        "myntra": scrape_myntra, "croma": scrape_croma,
        "reliancedigital": scrape_reliancedigital, "meesho": scrape_meesho,
        "tatacliq": scrape_tatacliq, "snapdeal": scrape_snapdeal,
    }
    if platform == "unknown":
        return {"name": None, "price": None, "thumbnail": None, "platform": "unknown", "status": "unsupported_platform"}
    result = scrapers[platform](url)
    result["scraped_at"] = datetime.utcnow()
    return result