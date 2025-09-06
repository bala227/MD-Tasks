import httpx
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import tldextract

class AsyncWebScraperAgent:
    def __init__(self, seed_url, max_pages=50, concurrency=10):
        self.seed_url = seed_url
        self.visited = set()
        self.to_visit = asyncio.Queue()
        self.data = []
        self.max_pages = max_pages
        self.concurrency = concurrency

        # Extract domain info
        extracted = tldextract.extract(seed_url)
        self.domain = f"{extracted.domain}.{extracted.suffix}"

        # Add seed URL to queue
        self.to_visit.put_nowait(seed_url)

    def is_same_domain(self, url):
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"
        return domain == self.domain

    async def fetch_page(self, client, url):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = await client.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
        return None

    async def parse_page(self, url, html):
        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.string.strip() if soup.title else "N/A"

        description = soup.find("meta", attrs={"name": "description"})
        summary = description["content"].strip() if description else "N/A"

        date = soup.find("meta", attrs={"property": "article:published_time"})
        if not date:
            date = soup.find("time")
        date_text = date["content"] if date and date.has_attr("content") else (date.text.strip() if date else "N/A")

        # Collect links
        links = []
        for a in soup.find_all("a", href=True):
            full_link = urljoin(url, a["href"])
            if self.is_same_domain(full_link) and full_link not in self.visited:
                links.append(full_link)
                await self.to_visit.put(full_link)

        self.data.append({
            "url": url,
            "title": title,
            "date": date_text,
            "summary": summary,
            "links": ";".join(links[:10])
        })

    async def worker(self, client):
        while len(self.visited) < self.max_pages:
            try:
                url = await asyncio.wait_for(self.to_visit.get(), timeout=5.0)
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
