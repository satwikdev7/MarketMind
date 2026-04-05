# MarketMind

MarketMind is an autonomous multi-agent competitive intelligence system built with LangGraph, Groq-hosted LLaMA 3 models, Tavily, ChromaDB, SQLite, APScheduler, and Streamlit. It automates the pipeline of web research, grounded analysis, and structured report generation across 11 industry verticals.

## What It Does

- Runs a stateful `Researcher -> Analyst -> Writer` agent pipeline using LangGraph
- Pulls live intelligence from Tavily, DuckDuckGo, RSS feeds, and web scraping
- Stores scraped knowledge in ChromaDB for retrieval-augmented generation
- Generates structured competitive landscape reports with Groq-hosted LLaMA 3 models
- Persists reports, schedules, run history, and graph checkpoints in SQLite
- Exposes manual report generation and recurring schedule management through Streamlit

## Implemented So Far

The project currently includes:

- Phase 0: environment setup and API smoke tests
- Phase 1: project foundation, config, schemas, database, utilities
- Phase 2: vertical registry with 11 industry configurations
- Phase 3: live search, RSS ingestion, scraping, and search orchestration
- Phase 4: RAG chunking, embeddings, Chroma persistence, and retrieval
- Phase 5: Groq client, prompt layer, JSON repair, and structured parsing
- Phase 6: isolated LangGraph agent nodes
- Phase 7: checkpointed LangGraph orchestration with retry/resume behavior
- Phase 8: Streamlit MVP for manual report generation
- Phase 9: APScheduler-based recurring report scheduling and run history

## Architecture

```text
User Query
  -> Researcher
     -> Tavily + DDGS + RSS + Scraper
     -> ChromaDB ingestion
  -> Router
     -> retry if research quality is low
  -> Analyst
     -> Chroma retrieval
     -> grounded competitive signals + SWOT
  -> Writer
     -> structured final report
     -> SQLite persistence
  -> Streamlit UI / Scheduled Runs
```

## Tech Stack

- Python 3.11
- LangGraph
- Groq + LLaMA 3.1 / 3.3
- Tavily
- DDGS
- BeautifulSoup + httpx
- ChromaDB
- sentence-transformers
- SQLite
- APScheduler
- Streamlit
- Pydantic v2

## Project Structure

```text
MarketMind/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── llm/
│   │   ├── models/
│   │   ├── rag/
│   │   ├── scheduler/
│   │   ├── tools/
│   │   ├── utils/
│   │   ├── verticals/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── data/
│   ├── scripts/
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

## Environment Setup

### 1. Create and activate the virtual environment

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
python --version
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `backend/.env.example` to `backend/.env` and fill in your keys.

Required:

```env
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## Local Validation Commands

Run these from `backend/` with the virtual environment active.

### Phase 0 and 1

```bash
PYTHONPATH=. python scripts/foundation_check.py
PYTHONPATH=. python scripts/smoke_groq.py
PYTHONPATH=. python scripts/smoke_tavily.py
```

### Phase 2 and 3

```bash
PYTHONPATH=. python scripts/phase2_registry_check.py
PYTHONPATH=. python scripts/phase3_search_check.py
```

### Phase 4 and 5

```bash
PYTHONPATH=. python scripts/phase4_rag_check.py
PYTHONPATH=. python scripts/phase5_llm_check.py
```

### Phase 6 and 7

```bash
PYTHONPATH=. python scripts/phase67_node_check.py
PYTHONPATH=. python scripts/phase67_graph_check.py
```

### Phase 8 and 9

```bash
PYTHONPATH=. python scripts/phase89_scheduler_check.py
```

## Running the App

Start the Streamlit app from `backend/`:

```bash
PYTHONPATH=. streamlit run app/main.py
```

Then open the local URL shown by Streamlit, usually:

- `http://localhost:8501`

## Streamlit Features

### New Report

- enter a competitive intelligence query
- choose one of the 11 verticals
- run the full agent pipeline
- view the generated report inline

### Scheduled Reports

- create recurring schedules using an hourly interval
- pause, resume, and delete schedules
- track last run and next run timestamps

### Run History

- inspect recent pipeline executions
- review recently generated reports from SQLite

## Supported Verticals

- technology
- healthcare
- finance
- retail
- energy
- automotive
- telecommunications
- pharmaceuticals
- real_estate
- logistics
- saas

## Important Notes

- ChromaDB persists data under `backend/data/chroma_db/`
- SQLite files are created under `backend/data/`
- LangGraph checkpoints are stored in SQLite and support interrupted-run resume
- The first embedding model load can take a little longer
- Hugging Face may warn about unauthenticated downloads for `sentence-transformers`; this does not block local development

## Current Limitations

- Export modules are scaffolded but not implemented yet
- Streamlit UI is currently focused on manual runs and basic schedule management
- Schedule creation currently uses interval-based recurring runs in the MVP UI
- Analyst grounding is improving, but profile quality still depends on retrieved source richness

## Resume-Aligned Summary

MarketMind demonstrates:

- stateful multi-agent orchestration with LangGraph
- checkpoint-backed execution using SQLite
- real-time competitive intelligence collection via Tavily, DDGS, RSS, and scraping
- RAG with ChromaDB and sentence-transformer embeddings
- structured report generation with Groq-hosted LLaMA 3 models
- autonomous recurring intelligence runs with APScheduler
- Streamlit-based interactive delivery
