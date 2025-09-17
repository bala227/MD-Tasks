from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from seleniumbase import Driver

# -------------------------------
# URL Normalizer
# -------------------------------
def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path if parsed.path not in ("", "/") else ""
    normalized = urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))
    return normalized.rstrip("/")

# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(title="Fast Web Scraper with Cloudflare Bypass")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str
    pages: int

# -------------------------------
# Global Selenium Driver (persistent)
# -------------------------------
driver = None

def get_driver():
    global driver
    if driver is None:
        driver = Driver(uc=True, headless=True)  # Launch once
    return driver

# -------------------------------
# Try fast fetch first
# -------------------------------
def fetch_fast(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0 Safari/537.36"
        }
        resp = httpx.get(url, headers=headers, timeout=10)
        if resp.status_code == 200 and "<html" in resp.text.lower():
            return resp.text
    except Exception:
        return None
    return None

# -------------------------------
# Selenium fallback
# -------------------------------
def fetch_selenium(url):
    d = get_driver()
    d.get(url)
    d.wait_for_element("body", timeout=10)
    return d.page_source

# -------------------------------
# Extract info
# -------------------------------
def extract_page_info(url, html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else "No Title"
    summary = ""
    for meta in ["description", "og:description", "twitter:description"]:
        tag = soup.find("meta", attrs={"name": meta}) or soup.find("meta", attrs={"property": meta})
        if tag and tag.get("content"):
            summary = tag["content"].strip()
            break
    if not summary:
        p = soup.find("p")
        summary = p.get_text(strip=True) if p else "No summary"
    date = ""
    for meta in ["article:published_time", "date", "og:updated_time"]:
        tag = soup.find("meta", attrs={"name": meta}) or soup.find("meta", attrs={"property": meta})
        if tag and tag.get("content"):
            date = tag["content"].strip()
            break
    links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]
    return {
        "url": normalize_url(url),
        "title": title or "No Title",
        "date": date or "Not Given",
        "summary": summary or "Not Available",
        "links": links,
    }

# -------------------------------
# Main fetch (fast + fallback)
# -------------------------------
def fetch_page(url):
    html = fetch_fast(url)
    if not html:  # If blocked, fallback
        html = fetch_selenium(url)
    return extract_page_info(url, html)

# -------------------------------
# Crawl
# -------------------------------
def crawl_domain(seed_url, max_pages=10):
    parsed = urlparse(seed_url)
    domain = parsed.netloc
    visited, results, queue = set(), [], [normalize_url(seed_url)]
    while queue and len(results) < max_pages:
        url = normalize_url(queue.pop(0))
        if url in visited:
            continue
        visited.add(url)
        try:
            page_data = fetch_page(url)
            results.append(page_data)
            for link in page_data["links"]:
                if urlparse(link).netloc == domain:
                    normalized = normalize_url(link)
                    if normalized not in visited and normalized not in queue:
                        queue.append(normalized)
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
    return results

# -------------------------------
# FastAPI Routes
# -------------------------------
@app.post("/scrape")
def scrape(req: ScrapeRequest):
    data = crawl_domain(req.url, req.pages)
    if not data:
        raise HTTPException(status_code=400, detail="No data found")
    return {"message": "Scraping complete", "items": len(data), "data": data}
