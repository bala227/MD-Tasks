from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import asyncio
import csv
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# ==========================================
# 🔹 Helper: Normalize URLs
# ==========================================
def normalize_url(url: str) -> str:
    """Normalize URLs so https://example.com and https://example.com/ are the same."""
    parsed = urlparse(url)
    path = parsed.path if parsed.path not in ("", "/") else ""
    normalized = urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))
    return normalized.rstrip("/")

# ==========================================
# 🔹 FastAPI App
# ==========================================
app = FastAPI(title="Async Web Scraper")

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

# ==========================================
# 🔹 Fetch Page
# ==========================================
async def fetch_page(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Title
                title = soup.title.string.strip() if soup.title else ""

                # Summary
                summary = ""
                for meta_name in ["description", "og:description", "twitter:description"]:
                    tag = soup.find("meta", attrs={"name": meta_name}) or soup.find("meta", attrs={"property": meta_name})
                    if tag and tag.get("content"):
                        summary = tag["content"].strip()
                        break
                if not summary:
                    p = soup.find("p")
                    summary = p.get_text(strip=True) if p else ""

                # Date
                date = ""
                for meta_name in ["article:published_time", "date", "og:updated_time"]:
                    tag = soup.find("meta", attrs={"property": meta_name}) or soup.find("meta", attrs={"name": meta_name})
                    if tag and tag.get("content"):
                        date = tag["content"].strip()
                        break

                # Collect links
                links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]

                return {
                    "url": normalize_url(url),  # ✅ normalized
                    "title": title,
                    "date": date,
                    "summary": summary,
                    "links": links,
                }
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

# ==========================================
# 🔹 Crawl Domain
# ==========================================
async def crawl_domain(seed_url, max_pages=20):
    parsed_seed = urlparse(seed_url)
    domain = parsed_seed.netloc

    visited = set()
    results = []
    queue = [normalize_url(seed_url)]

    async with aiohttp.ClientSession() as session:
        while queue and len(results) < max_pages:
            url = normalize_url(queue.pop(0))
            if url in visited:
                continue
            visited.add(url)

            page_data = await fetch_page(session, url)
            if page_data:
                results.append(page_data)

                for link in page_data["links"]:
                    if urlparse(link).netloc == domain:
                        normalized_link = normalize_url(link)
                        if normalized_link not in visited:
                            queue.append(normalized_link)

    return results

# ==========================================
# 🔹 Save to CSV
# ==========================================
def save_to_csv(data, filename="scraped_data.csv"):
    if not data:
        return None
    keys = ["url", "title", "date", "summary"]
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in data:
            writer.writerow({k: row.get(k, "") for k in keys})
    return filepath

# ==========================================
# 🔹 FastAPI Endpoints
# ==========================================
@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    data = await crawl_domain(request.url, request.pages)
    if not data:
        raise HTTPException(status_code=400, detail="No data found")

    file_path = save_to_csv(data)
    return {"message": "Scraping complete", "csv_file": file_path, "items": len(data), "data": data}

@app.get("/download_csv")
async def download_csv():
    file_path = os.path.join(os.getcwd(), "scraped_data.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="CSV file not found")
    return FileResponse(file_path, media_type="text/csv", filename="scraped_data.csv")

# ==========================================
# 🔹 AsyncWebScraperAgent
# ==========================================
import httpx
import pandas as pd
import tldextract

class AsyncWebScraperAgent:
    def __init__(self, seed_url, max_pages=50, concurrency=10):
        self.seed_url = normalize_url(seed_url)
        self.visited = set()
        self.to_visit = asyncio.Queue()
        self.data = []
        self.max_pages = max_pages
        self.concurrency = concurrency

        # Extract domain info
        extracted = tldextract.extract(seed_url)
        self.domain = f"{extracted.domain}.{extracted.suffix}"

        # Add seed URL to queue
        self.to_visit.put_nowait(self.seed_url)

    def is_same_domain(self, url):
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"
        return domain == self.domain

    async def fetch_page(session, url):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Title
                    title = soup.title.string.strip() if soup.title else "Not given"

                    # Summary (meta tags or first <p>)
                    summary = None
                    for meta_name in ["description", "og:description", "twitter:description"]:
                        tag = soup.find("meta", attrs={"name": meta_name}) or soup.find("meta", attrs={"property": meta_name})
                        if tag and tag.get("content"):
                            summary = tag["content"].strip()
                            break
                    if not summary:
                        p = soup.find("p")
                        summary = p.get_text(strip=True) if p else "Not given"

                    # Date
                    date = None
                    for meta_name in ["article:published_time", "date", "og:updated_time"]:
                        tag = soup.find("meta", attrs={"property": meta_name}) or soup.find("meta", attrs={"name": meta_name})
                        if tag and tag.get("content"):
                            date = tag["content"].strip()
                            break
                    if not date:
                        date = "Not given"

                    # Collect links
                    links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]

                    return {
                        "url": normalize_url(url),
                        "title": title,
                        "date": date,
                        "summary": summary,
                        "links": links,
                    }
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None


    async def parse_page(self, url, html):
        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.string.strip() if soup.title else "Not given"

        description = soup.find("meta", attrs={"name": "description"})
        summary = description["content"].strip() if description else "Not given"

        date = soup.find("meta", attrs={"property": "article:published_time"})
        if not date:
            date = soup.find("time")
        date_text = (
            date["content"] if date and date.has_attr("content") else
            (date.text.strip() if date else "Not given")
        )

        # Collect links
        links = []
        for a in soup.find_all("a", href=True):
            full_link = normalize_url(urljoin(url, a["href"]))
            if self.is_same_domain(full_link) and full_link not in self.visited:
                links.append(full_link)
                await self.to_visit.put(full_link)

        self.data.append({
            "url": url,
            "title": title,
            "date": date_text,
            "summary": summary,
            "links": ";".join(links[:10]) if links else "Not given"
        })


    async def worker(self, client):
        while len(self.visited) < self.max_pages:
            try:
                url = await asyncio.wait_for(self.to_visit.get(), timeout=5.0)
                url = normalize_url(url)
            except asyncio.TimeoutError:
                return

            if url in self.visited:
                continue
            self.visited.add(url)

            html = await self.fetch_page(client, url)
            if html:
                await self.parse_page(url, html)

    async def crawl(self):
        async with httpx.AsyncClient(follow_redirects=True) as client:
            tasks = [asyncio.create_task(self.worker(client)) for _ in range(self.concurrency)]
            await asyncio.gather(*tasks)
        return self.data

    def save_csv(self, filename="output.csv"):
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False)
        return filename
