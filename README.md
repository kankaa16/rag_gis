# GeoRAG 

# An AI-powered geospatial decision support system built for water resource planning and management. The platform combines Retrieval-Augmented Generation (RAG), geographic information systems (GIS), and deterministic analytics to provide accurate insights about water bodies, infrastructure suitability, and location-specific queries.

Designed for government and planning use cases, the system minimizes hallucinations by combining semantic retrieval with structured geographic data and rule-based reasoning.

## Features

### Hybrid Retrieval Architecture

* Combines FAISS vector search, structured geographic datasets, and rule-based reasoning.
* Routes queries through the most suitable retrieval pipeline instead of relying solely on LLM generation.

### Geospatial Intelligence

* Supports location-aware querying over water resource datasets.
* Retrieves contextual information about lakes, reservoirs, and other water bodies.

### Deterministic Analytics

* Numerical and ranking-based questions are answered using Pandas-driven data processing.
* Ensures accurate results for queries involving area, depth, capacity, and comparative analysis.

### Engineering Suitability Analysis

* Evaluates the suitability of water bodies for infrastructure such as dams and anicuts using predefined engineering constraints.
* Combines geographic attributes with domain-specific rules.

### Voice-Enabled Interaction

* Native Speech-to-Text and Text-to-Speech integration using browser APIs.
* Enables natural conversational access to geographic information.

### Intelligent Query Handling

* Fuzzy matching for geographic entities and location names.
* Improves retrieval quality by handling spelling variations and user input errors.

---

## System Architecture

1. User submits a text or voice query.
2. FastAPI backend processes and classifies the request.
3. Query router selects the appropriate pipeline:

   * Semantic Retrieval (FAISS)
   * Structured Geographic Data Retrieval
   * Deterministic Analytics Engine
   * Engineering Suitability Engine
4. Retrieved information is combined into a grounded context.
5. Gemini generates a final response based on verified data.
6. Results are displayed in the React dashboard and optionally delivered through voice output.

---

## Tech Stack

### Frontend

* React.js
* Vite
* Native Web Speech API

### Backend

* FastAPI
* Python
* Uvicorn

### AI & Data Layer

* Google Gemini
* FAISS Vector Database
* Text Embeddings
* Structured Geographic Knowledge Base
* Pandas

---

## Key Learnings

* Retrieval-Augmented Generation (RAG)
* Vector databases and semantic search
* Geospatial data processing
* FastAPI backend development
* AI system reliability and hallucination reduction
* Hybrid retrieval architectures
* Rule-based reasoning systems

---

## Future Improvements

* Multi-region geospatial support
* Real-time GIS map integration
* Satellite imagery analysis
* Advanced engineering recommendation models
* Multi-agent planning workflows

## Use Case

This platform was developed as part of a geospatial AI initiative focused on supporting water resource planning and decision-making through reliable, retrieval-grounded AI systems.
