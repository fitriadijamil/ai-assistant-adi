# AI Assistant Adi — Design Document

## Overview
A professional web-based AI Assistant for CCTV & security system pre-sales engineering. Used internally by pre-sales engineers, technicians, and sales teams. Future roadmap includes customer-facing portal.

## Tech Stack
- **Frontend:** Next.js (App Router) + TailwindCSS + daisyUI, deployed to Vercel
- **Backend:** Python FastAPI, deployed to Render (free tier)
- **Database:** SQLite (MVP), architected for PostgreSQL migration
- **AI Provider:** OpenRouter (model configurable via env, default Gemini Flash)

## Brands Supported
Hikvision, Dahua, Uniview, Ezviz, Hiview, Bardi, TP-Link Tapo, Imou, Hilook

## Project Structure
```
/ai-assistant-adi
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx          # Chat Assistant (default)
│   │   │   ├── storage-calculator/
│   │   │   └── proposal-generator/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── ToolResult.tsx
│   │   └── lib/
│   │       └── api.ts
│   ├── vercel.json
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── ai_service.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── registry.py
│   │   │   ├── storage_calculator.py
│   │   │   ├── bandwidth_calculator.py
│   │   │   └── product_lookup.py
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   └── system_prompt.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── chat.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── database.py
│   │   └── catalog/
│   │       ├── cameras.json
│   │       ├── nvr.json
│   │       ├── poe_switches.json
│   │       └── hdd.json
│   ├── requirements.txt
│   ├── render.yaml
│   └── Dockerfile
└── README.md
```

## MVP Features

### 1. AI Chat Assistant
- Professional chat interface with message history
- Integrates with OpenRouter API (configurable model)
- Tool-calling support via lightweight registry
- System prompt engineering for CCTV pre-sales expertise

### 2. Storage Calculator (Tool)
Calculates HDD requirements based on:
- Camera count, resolution, codec, FPS, recording days, bitrate
- Outputs: recommended HDD size, daily/monthly storage

### 3. Bandwidth Calculator (Tool)
Calculates network bandwidth based on:
- Camera count, bitrate, simultaneous streams
- Outputs: estimated bandwidth, uplink recommendations

### 4. Product Recommendation
- Rule-based engine using JSON product catalogs
- Categories: cameras, NVR, PoE switches, HDD
- Editable JSON files for easy maintenance

### 5. Proposal Generator
- Input: client name, project type, location, camera count, requirements
- Output: executive summary, recommended solution, SOW, technical overview

### 6. Troubleshooting Mode
AI-assisted guidance for common issues:
camera offline, IP conflict, PoE problems, video loss, HDD failure, network instability, remote viewing

## Tool System
Lightweight tool registry with:
- name, description, input_schema, execute function
- AI runtime discovers, invokes, and passes results to conversation
- Initial tools: storage_calculator, bandwidth_calculator, product_lookup

## API Endpoints
- `POST /api/chat` — Send message, get AI response (with tool calling)
- `GET /api/tools` — List available tools
- `POST /api/tools/storage-calculator` — Direct tool access
- `POST /api/tools/bandwidth-calculator` — Direct tool access
- `GET /api/products` — List product catalog (with optional filters)
- `POST /api/proposals/generate` — Generate proposal draft

## Build Phases
1. **Phase 1:** Project scaffold, backend + frontend setup, AI chat endpoint
2. **Phase 2:** Tool registry, storage calculator, bandwidth calculator
3. **Phase 3:** Product catalog, recommendation engine
4. **Phase 4:** Proposal generator
5. **Phase 5:** UI refinement, deployment prep, documentation

## Key Engineering Rules
- Minimal dependencies
- Clean readable code
- No Kubernetes, microservices, Redis, RabbitMQ
- Environment-based configuration
- Basic logging and error handling
- Simple local development setup

## Technical Mitigations

### 1. Shared Calculation Library (Frontend ↔ AI Tools)
Calculation logic (storage, bandwidth) lives in a **single shared module** on the backend (`app/tools/`). Both the standalone calculator pages and the AI tool-calling path invoke the **same Python functions**. Frontend standalone pages call dedicated API endpoints that wrap these functions — no duplicate formulas.

### 2. Render Free Tier — Ephemeral Disk Mitigation
Render free tier uses ephemeral storage — SQLite resets on deploy/sleep.

**MVP strategy:** Chat history stored in `localStorage` on the frontend. Each `POST /api/chat` call sends full conversation context as payload. SQLite on backend used only for non-critical internal state. Future Phase: migrate to PostgreSQL (Neon.tech or Supabase).

### 3. Cross-Catalog Key Connectors
Product JSONs include relational keys:
- `cameras.json`: `"poe": true`, `"max_resolution": "4MP"`, `"power_watt": 7`, `"brand": "hikvision"`
- `nvr.json`: `"max_decoding": "4MP"`, `"channel_count": 16`, `"poe_budget_watt": 150`
- `poe_switches.json`: `"power_budget_watt": 240`, `"poe_standard": "802.3af"`

AI recommendation engine validates compatibility across catalogs before suggesting.

### 4. OpenRouter Token Optimization
`product_lookup.py` acts as a **filter gate** — AI must call the tool with specific filters (brand, category). The tool returns only relevant products, not the entire catalog. Prevents token waste from dumping all JSON into context.

### 5. Deployment Config Notes
- `vercel.json`: Set `maxDuration: 30` to handle Render cold start latency
- `requirements.txt`: Pin versions — `fastapi==0.111.0`, `pydantic==2.7.4`, `uvicorn==0.30.1`, `sqlalchemy==2.0.31`, `httpx==0.27.0`
