from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import asyncio
import csv
import os

app = FastAPI(title="Async Web Scraper")

# ✅ Input model
class ScrapeRequest(BaseModel):
    url: str
    max_pages: int = 20  # limit for crawling


# ✅ Extract details from a single page
async def fetch_page(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Title
                title = soup.title.string.strip() if soup.title else ""

                # Summary (check multiple sources)
                summary = ""
                for meta_name in ["description", "og:description", "twitter:description"]:
                    tag = soup.find("meta", attrs={"name": meta_name}) or soup.find("meta", attrs={"property": meta_name})
                    if tag and tag.get("content"):
                        summary = tag["content"].strip()
                        break
                if not summary:
                    # fallback: first paragraph text
                    p = soup.find("p")
                    summary = p.get_text(strip=True) if p else ""

                # Date (check multiple possible meta tags)
                date = ""
                for meta_name in ["article:published_time", "date", "og:updated_time"]:
                    tag = soup.find("meta", attrs={"property": meta_name}) or soup.find("meta", attrs={"name": meta_name})
                    if tag and tag.get("content"):
                        date = tag["content"].strip()
                        break

                # Collect links
                links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]

                return {
                    "url": url,
                    "title": title,
                    "date": date,
                    "summary": summary,
                    "links": links,
                }
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None


# ✅ Crawl inside the same domain
async def crawl_domain(seed_url, max_pages=20):
    parsed_seed = urlparse(seed_url)
    domain = parsed_seed.netloc

    visited = set()
    results = []
    queue = [seed_url]

    async with aiohttp.ClientSession() as session:
        while queue and len(results) < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)

            page_data = await fetch_page(session, url)
            if page_data:
                results.append(page_data)

                # keep only links inside the same domain
                for link in page_data["links"]:
                    if urlparse(link).netloc == domain and link not in visited:
                        queue.append(link)

    return results


# ✅ Save results to CSV
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


# ✅ API endpoint
@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    data = await crawl_domain(request.url, request.max_pages)
    if not data:
        raise HTTPException(status_code=400, detail="No data found")

    file_path = save_to_csv(data)
    return {"message": "Scraping complete", "csv_file": file_path, "items": len(data)}
