# NYC Landmarks Research Agent

An AI-powered agent designed to generate in-depth, accurate, and engaging research reports about New York City landmarks.

The agent combines:
- ✅ Semantic search over landmark PDF reports via CoreDataStore Vector API
- ✅ Structured metadata retrieval via CoreDataStore Landmark API
- ✅ Image integration (modern and historical photos)
- ✅ Research-grade report generation powered by Azure OpenAI Service (GPT-4 or GPT-3.5)

---

## Project Goals

- Build an intelligent agent that can answer questions about NYC landmarks with deep factual grounding.
- Combine structured data (names, addresses, designation dates) with unstructured knowledge (historical narratives from reports).
- Deliver detailed, human-like research reports including modern and 1940s imagery.

---

## Architecture Overview

```
User Query
   ↓
Landmark Metadata API   →   Fetch structured facts (name, year, architect, photos)
Vector Database API     →   Fetch semantic passages from PDF reports
Azure OpenAI LLM        →   Synthesize full report
```

- **Metadata API:** https://api.coredatastore.com
- **Vector Search API:** https://vector-db.coredatastore.com
- **Photo URLs:** Provided via metadata API responses
- **LLM:** Azure OpenAI Service (GPT-4 preferred)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/stuartshay/nyc-landmarks-research-agent.git
cd nyc-landmarks-research-agent
```

### 2. Set up Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file at the project root:

```
OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com
VECTOR_DB_API_URL=https://vector-db.coredatastore.com
LANDMARK_METADATA_API_URL=https://api.coredatastore.com
NYC_API_TOKEN=your-nyc-open-data-token (optional, future use)
```

### 4. Running the App

```bash
uvicorn src.main:app --reload
```

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to access interactive Swagger documentation.

---

## Project Structure

```
src/
├── clients/
│   ├── vectorstore_client.py
│   └── landmark_metadata_client.py
├── services/
│   └── landmark_service.py
├── memory_store.py
├── utils.py
├── config.py
├── main.py
tests/
├── (unit tests here)
```

---

## Core External Services

| Service                             | URL                                                                              | Purpose                                                                   |
| :---------------------------------- | :------------------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| CoreDataStore Landmark Metadata API | https://api.coredatastore.com/swagger/index.html                                 | Fetch structured landmark data (architect, designation date, photo links) |
| CoreDataStore Vector Search API     | https://vector-db.coredatastore.com/docs                                         | Perform semantic searches over PDF report text                            |
| Azure OpenAI Service                | [Azure OpenAI Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/) | LLM for report generation                                                 |

---

## Next Steps

- [ ] Scaffold `clients/` and `services/`
- [ ] Create basic test scripts to validate API calls
- [ ] Build first simple Chain: Metadata + Report Chunks → LLM → Research Report
- [ ] Set up session memory
- [ ] Prepare for containerization and cloud deployment

---

## Status

🚧 **Active Development** — Phase 1 (Infrastructure + API Integration)

---

## License

MIT License (to be added)
