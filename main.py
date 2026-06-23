"""
Filename: main.py
Description: Completely free, independent, API-keyless asynchronous 
             web search and content retrieval pipeline for AI contexts.
Author: Shamim Rabby (https://github.com/ShamimRabby)
"""

import asyncio
import logging
import re
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from bs4 import BeautifulSoup

# Setup production logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("IndependentSearchPlugin")

app = FastAPI(
    title="Independent AI Web-Search & Retrieval Middleware",
    description="100% free and open-source RAG proxy microservice without any external API dependencies.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str = Field(..., description="The query string to look up on the live web.")
    max_results: Optional[int] = Field(3, ge=1, le=5, description="Number of source pages to deep scrape concurrently.")

class TextDocument(BaseModel):
    title: str
    url: str
    snippet: str
    extracted_text: str

class PluginResponse(BaseModel):
    status: str
    query: str
    injected_system_prompt: str
    raw_extracted_documents: List[TextDocument]

async def free_web_search(query: str, max_results: int) -> List[Dict[str, str]]:
    """
    Executes an API-keyless lookup using DuckDuckGo HTML/JSON endpoints.
    Returns clean links, titles, and snippets.
    """
    # DuckDuckGo Lite endpoint (clean, light markup script, no JS needed)
    search_url = "https://html.duckduckgo.com/html/"
    payload = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            logger.info(f"Executing open-source search lookup for: '{query}'")
            response = await client.post(search_url, data=payload, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Search source returned response code: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            search_hits = []

            # Extract structural query blocks from elements
            links = soup.find_all("a", class_="result__url")
            titles = soup.find_all("a", class_="result__snippet")
            
            for index, link_el in enumerate(soup.find_all("div", class_="result__body")):
                if len(search_hits) >= max_results:
                    break
                
                title_a = link_el.find("a", class_="result__snippet")
                url_a = link_el.find("a", class_="result__url")
                snippet_div = link_el.find("get" or "div", class_="result__snippet")
                
                if title_a and url_a:
                    actual_url = url_a.get("href", "").strip()
                    # Clean internal redirected wrapper parameters if any
                    if "/l/?kh=-1&uddg=" in actual_url:
                        actual_url = actual_url.split("uddg=")[1].split("&")[0]
                        actual_url = actual_url.replace("%3A", ":").replace("%2F", "/")

                    search_hits.append({
                        "title": title_a.get_text().strip(),
                        "url": actual_url,
                        "snippet": snippet_div.get_text().strip() if snippet_div else ""
                    })

            return search_hits
        except Exception as e:
            logger.error(f"Search indexing compilation failure: {e}")
            return []

async def pull_and_sanitize_html(url: str) -> str:
    """
    Locally parses a remote website, strips out junk DOM parameters, 
    and converts the core text content into clean markdown context strings.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            logger.info(f"Locally pulling and parsing markup strings from target: {url}")
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return ""

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Scrape away performance blocking and irrelevant script tags
            for structural_junk in soup(["script", "style", "nav", "header", "footer", "form", "sidebar", "noscript"]):
                structural_junk.decompose()

            # Isolate text layers
            raw_text = soup.get_text(separator=" ")
            
            # Clean up spacing anomalies using regex parsing loops
            lines = (line.strip() for line in raw_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = "\n".join(chunk for chunk in chunks if chunk)
            
            # Bound context limits to keep context window usage low
            return clean_text[:3500]
        except Exception as e:
            logger.warning(f"Unable to safely scrape or index url text data [{url}]: {e}")
            return ""

@app.post("/v1/search-internet", response_model=PluginResponse, status_code=status.HTTP_200_OK)
async def unified_independent_search(request: SearchRequest):
    """
    Universal API Endpoint: Finds and scrapes live pages, then injects 
    the text context directly into a ready-to-use LLM system prompt blueprint.
    """
    try:
        # Step 1: Run free web lookup indexer
        discovered_assets = await free_web_search(request.query, request.max_results)
        
        if not discovered_assets:
            logger.warning("No tracking elements successfully returned from lookup.")
            context_accumulator = "Zero verified web indices were found for this query parameter."
            response_documents = []
        else:
            logger.info(f"Located {len(discovered_assets)} sources. Launching concurrent local parsing blocks...")
            
            # Step 2: Concurrently scrape and isolate clean text from all targets
            scraping_routines = [pull_and_sanitize_html(site['url']) for site in discovered_assets]
            scraped_contents = await asyncio.gather(*scraping_routines)

            context_frames = []
            response_documents = []

            for index, site in enumerate(discovered_assets):
                clean_scraped_text = scraped_contents[index]
                # Fallback to the search snippet if the web page rejects scraping
                final_text_asset = clean_scraped_text if clean_scraped_text.strip() else site['snippet']

                response_documents.append(TextDocument(
                    title=site['title'],
                    url=site['url'],
                    snippet=site['snippet'],
                    extracted_text=final_text_asset
                ))

                context_frames.append(
                    f"### Verified Grounding Source [{index + 1}]:\n"
                    f"Title Link: {site['title']}\n"
                    f"URL Reference Address: {site['url']}\n"
                    f"Extracted Context:\n{final_text_asset}\n"
                    f"--------------------------------------------------\n"
                )
            
            context_accumulator = "\n".join(context_frames)

        # Step 3: Automatically generate the system context injection layout
        engineered_system_prompt = (
            "You are an advanced AI assistant equipped with real-time web retrieval tools. "
            "Analyze the verified facts provided below to construct a detailed answer to the user query.\n\n"
            "Strict Constraints:\n"
            "1. Ground all answers firmly within the provided source blocks. Do not speculate or extrapolate.\n"
            "2. Cite each factual assertion using standard inline hyperlinks matching this format: [Source Title](URL).\n"
            "3. If the data is empty or irrelevant, state clearly that the answer cannot be found online.\n\n"
            f"=== START LIVE INTERNET CONTEXT ===\n"
            f"{context_accumulator}\n"
            f"=== END LIVE INTERNET CONTEXT ===\n\n"
            f"User Objective Query: {request.query}"
        )

        return PluginResponse(
            status="Success",
            query=request.query,
            injected_system_prompt=engineered_system_prompt,
            raw_extracted_documents=response_documents
        )

    except Exception as runtime_error:
        logger.critical(f"Critical operational breakdown: {runtime_error}")
        raise HTTPException(status_code=500, detail="Internal context processing failure.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
