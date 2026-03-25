# Brand Guardian AI 🎯

## Overview

**Brand Guardian AI** is an end-to-end AI-powered compliance auditing system that analyzes video content against regulatory rules. It leverages Azure services, retrieval-augmented generation (RAG), and a modular workflow architecture to detect potential compliance violations in marketing or promotional videos.

---

##  Features

*  **Video Processing** via Azure Video Indexer
*  **Extracting transcript and ocr from the video** using Azure Video indexer
*  **AI-Powered Compliance Auditing** using LLMs
*  **Retrieval-Augmented Generation (RAG)** with Azure AI Cognitive Search
*  **Structured Compliance Reports** with severity levels
*  **FastAPI Backend** for Backend app construction
*  **Telemetry Integration** with Azure Monitor
*  **Workflow Orchestration** using LangGraph

---

##  Architecture

```
Client Request (Video URL)
        ↓
FastAPI Server (/audit)
        ↓
LangGraph Workflow
   ┌───────────────┐
   │ Indexer Node  │ → Extract transcript & OCR
   └───────────────┘
           ↓
   ┌───────────────┐
   │ Auditor Node  │ → RAG + LLM Analysis
   └───────────────┘
           ↓
Final Compliance Report
```

---

## Tech Stack

* **Backend Framework:** FastAPI
* **Workflow Engine:** LangGraph
* **LLM & Embeddings:** Azure OpenAI
* **Vector Store:** Azure Cognitive Search
* **Video Processing:** Azure Video Indexer
* **Telemetry:** Azure Monitor (Application Insights)
* **Language:** Python 3.10+


---

## Project Structure

```
.
├── backend/
│   ├── data/
│   ├── scripts/
│   │   └── indexer_document.py
│   ├── src/
│   │   ├── api/
│   │   │   ├── server.py
│   │   │   └── telemetry.py
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── nodes.py
|   |   |   ├── state.py
│   │   │   └── workflow.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── video_indexer.py
│   └── tests/
├── .env
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```



## ⚙️ Setup Instructions
### 3. Configure Environment Variables

Create a `.env` file with the following:

### .env setup
    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING=

    # Azure OpenAI (Chat)
    AZURE_OPENAI_CHAT_ENDPOINT=
    AZURE_OPENAI_CHAT_API_KEY=
    AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o

    # Azure OpenAI (Embeddings)
    AZURE_OPENAI_EMBED_ENDPOINT=
    AZURE_OPENAI_EMBED_API_KEY=
    AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small

    # API Version
    AZURE_OPENAI_API_VERSION=2024-12-01-preview

    # Azure Search
    AZURE_SEARCH_ENDPOINT=
    AZURE_SEARCH_API_KEY=
    AZURE_SEARCH_INDEX_NAME=

    # Azure Video Indexer
    AZURE_VI_ACCOUNT_ID=
    AZURE_VI_LOCATION=
    AZURE_SUBSCRIPTION_ID=
    AZURE_RESOURCE_GROUP=
    AZURE_VI_NAME=

    # Azure Monitoring
    APPLICATIONINSIGHTS_CONNECTION_STRING=

    # Langsmit Tracing
    LANGCHAIN_TRACING_V2= true
    LANGCHAIN_ENDPOINT=
    LANGCHAIN_API_KEY=
    LANGCHAIN_PROJECT = "brand-guardian-prod"


```
---

### Running the Project

### Run via CLI (Workflow Only)
### bash
python main.py


### Run FastAPI Server
###bash
uv run uvicorn backend.src.api.server:app --reload
```
---



## 📡 API Endpoints

### 1. Audit Video

**POST** `/audit`

#### Request

```json
{
  "video_url": "https://youtu.be/example"
}
```


#### Response
```json
{
  "session_id": "uuid",
  "video_id": "vid_xxxx",
  "status": "PASS | FAIL",
  "final_report": "Summary...",
  "compliance_results": [
    {
      "category": "Claim Validation",
      "severity": "CRITICAL",
      "description": "Violation details"
    }
  ]
}
```
---


##  Workflow Breakdown

### 1. Indexer Node

* Downloads video from YouTube
* Uploads to Azure Video Indexer
* Waits for processing
* Extracts:

  * Transcript
  * OCR text
  * Metadata

### 2. Auditor Node

* Combines transcript + OCR text
* Retrieves compliance rules from Azure Search
* Uses LLM to evaluate violations
* Outputs structured JSON report

---

##  Known Limitations

* Free-tier Azure Video Indexer may:

  * Be slow (queue delays)
  * Cause timeouts for longer videos
* Requires YouTube URLs (for now)
* LLM output parsing depends on strict JSON formatting



## 🧪 Example Output

```
Status: FAIL

[VIOLATIONS]
- CRITICAL: Misleading pricing claim

[Summary]
The advertisement contains misleading pricing information...
```


