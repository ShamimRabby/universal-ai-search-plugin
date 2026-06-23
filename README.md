# Universal Open-Source Web Search & Context Retrieval Plugin

An enterprise-grade, 100% independent, and completely free **Asynchronous RAG (Retrieval-Augmented Generation) Middleware** engine. This microservice bypasses proprietary search engines and subscription-based extraction APIs—allowing any application or local AI model to perform deep internet lookups, clean active pages, and extract grounded facts without requiring any third-party API keys.

Developed by [@ShamimRabby](https://github.com/ShamimRabby).

## 🚀 Core Mechanics

- **Zero-API Dependency**: Employs structural open-source scraping protocols to execute search lookups and scrape data completely free of charge.
- **Local DOM Parsing Engine**: Leverages HTML structural maps to isolate relevant text blocks, removing cookies, ads, trackers, and navigation lists on your machine.
- **Async Execution Matrix**: Utilizes Python's `asyncio` and `httpx` connection pooling to search and scan multiple distinct domains in parallel under 2 seconds.
- **Universal Local/Cloud Routing**: Formats gathered context natively into clean text layouts ready to be passed to local LLMs (Ollama, LocalAI) or any cloud model array.

## 🛠️ Architecture Pipeline

```text
[User Natural Prompt] ──► [Intent Processor]
                                │
                                ▼
                   [DuckDuckGo Native Lookup] (Free / No Token)
                                │
                                ▼
               [Parallel Local DOM Text Scraper] (BS4 / Pure Text)
                                │
                                ▼
              [Contextually Injected Output Payload] ──► [To Any local/Cloud LLM]
```

📋 Installation & Prerequisites
Make sure you have Python 3.9 or higher installed locally.

1. Clone the Workspace
```text
git clone https://github.com/ShamimRabby/universal-ai-search-plugin.git
cd universal-ai-search-plugin
```
2. Install Free Open-Source Libraries
```text
pip install -r requirements.txt
```
3. Run the Microservice
```text
python main.py
```
The localized REST API will activate instantly at http://127.0.0.1:8000.

🧪 Interactive API Sandbox
FastAPI automatically mounts interactive API testing dashboards. Once running, access:
👉 http://127.0.0.1:8000/docs

Open the /v1/search-internet route, hit "Try it out", alter the query value to test real-time searches, and evaluate the JSON output data.

🤝 Contribution
Feel free to open issues or pull requests to improve structural scraping stability! Developed with precision by [@ShamimRabby](https://github.com/ShamimRabby).
