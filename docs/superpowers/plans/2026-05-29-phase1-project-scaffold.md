# Phase 1 — Project Scaffold + AI Chat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold both frontend and backend projects, establish core AI chat flow with tool registry foundation.

**Architecture:** Next.js App Router frontend → FastAPI backend → OpenRouter API. Chat history stored in frontend localStorage. Backend exposes `/api/chat` endpoint with tool calling support.

**Tech Stack:** Next.js 14, TailwindCSS + daisyUI, Python FastAPI, SQLite (ephemeral), OpenRouter (Gemini Flash), httpx for AI API calls.

---

### Task 1: Backend Scaffold

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/__init__.py`

- [ ] **Step 1: Create virtual environment and install dependencies**

Run:
```bash
cd /Users/macbookair/Desktop/ai-assistant-adi
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install fastapi==0.111.0 pydantic==2.7.4 uvicorn==0.30.1 sqlalchemy==2.0.31 httpx==0.27.0 python-dotenv==1.0.1
pip freeze > backend/requirements.txt
```

- [ ] **Step 2: Create `backend/app/__init__.py`**

Empty file.

- [ ] **Step 3: Create `backend/app/config.py`**

```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/adi.db")
```

- [ ] **Step 4: Create `backend/app/main.py`**

```python
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DATABASE_URL
from app.api.routes import router

app = FastAPI(title="AI Assistant Adi", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
```

- [ ] **Step 5: Create `.env` file**

```
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp
```

- [ ] **Step 6: Verify backend starts**

Run:
```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
```
Expected: Server starts on http://localhost:8000, `/health` returns `{"status": "ok"}`

---

### Task 2: Database Setup

**Files:**
- Create: `backend/app/db/__init__.py`
- Create: `backend/app/db/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/schemas/__init__.py`

- [ ] **Step 1: Create `backend/app/db/database.py`**

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/adi.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 2: Create empty `__init__.py` files**

```bash
touch backend/app/db/__init__.py backend/app/models/__init__.py backend/app/schemas/__init__.py
```

---

### Task 3: Schemas

**Files:**
- Create: `backend/app/schemas/chat.py`

- [ ] **Step 1: Create `backend/app/schemas/chat.py`**

```python
from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

class ToolCall(BaseModel):
    name: str
    arguments: dict

class ChatResponse(BaseModel):
    message: ChatMessage
    tool_calls: Optional[list[ToolCall]] = None
```

---

### Task 4: Tool Registry Foundation

**Files:**
- Create: `backend/app/tools/__init__.py`
- Create: `backend/app/tools/registry.py`

- [ ] **Step 1: Create `backend/app/tools/registry.py`**

```python
from typing import Any

class Tool:
    def __init__(self, name: str, description: str, input_schema: dict, fn: callable):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.fn = fn

    def to_openrouter_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }

    async def execute(self, **kwargs) -> Any:
        return await self.fn(**kwargs)

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def to_openrouter_tools(self) -> list[dict]:
        return [t.to_openrouter_tool() for t in self._tools.values()]

registry = ToolRegistry()
```

---

### Task 5: Storage Calculator Tool

**Files:**
- Create: `backend/app/tools/storage_calculator.py`

- [ ] **Step 1: Create `backend/app/tools/storage_calculator.py`**

```python
from app.tools.registry import Tool, registry

RESOLUTION_BITRATES = {
    "2MP": 4_000_000,
    "3MP": 6_000_000,
    "4MP": 8_000_000,
    "5MP": 10_000_000,
    "8MP": 16_000_000,
    "12MP": 24_000_000,
}

async def storage_calculator_fn(
    camera_count: int,
    resolution: str,
    fps: int = 30,
    recording_days: int = 30,
    bitrate: int | None = None,
) -> dict:
    if bitrate is None:
        bitrate = RESOLUTION_BITRATES.get(resolution.upper(), 8_000_000)

    daily_bytes = camera_count * bitrate * fps / 30 * 86400
    daily_gb = daily_bytes / (1024**3)
    monthly_gb = daily_gb * recording_days
    recommended_hdd = monthly_gb * 1.2

    return {
        "daily_storage_gb": round(daily_gb, 2),
        "monthly_storage_gb": round(monthly_gb, 2),
        "recommended_hdd_gb": round(recommended_hdd, 2),
        "recommended_hdd_tb": round(recommended_hdd / 1024, 1),
        "bitrate_used": bitrate,
    }

storage_calculator_tool = Tool(
    name="storage_calculator",
    description="Calculate HDD storage requirements for CCTV cameras",
    input_schema={
        "type": "object",
        "properties": {
            "camera_count": {"type": "integer", "description": "Number of cameras"},
            "resolution": {"type": "string", "description": "Camera resolution (2MP, 4MP, 8MP, etc)"},
            "fps": {"type": "integer", "description": "Frames per second (default 30)"},
            "recording_days": {"type": "integer", "description": "Number of recording days (default 30)"},
            "bitrate": {"type": "integer", "description": "Optional custom bitrate in bps"},
        },
        "required": ["camera_count", "resolution"],
    },
    fn=storage_calculator_fn,
)

registry.register(storage_calculator_tool)
```

---

### Task 6: Bandwidth Calculator Tool

**Files:**
- Create: `backend/app/tools/bandwidth_calculator.py`

- [ ] **Step 1: Create `backend/app/tools/bandwidth_calculator.py`**

```python
from app.tools.registry import Tool, registry

async def bandwidth_calculator_fn(
    camera_count: int,
    bitrate_per_camera: int,
    simultaneous_streams: int = 1,
) -> dict:
    total_bandwidth = camera_count * bitrate_per_camera * simultaneous_streams
    total_mbps = total_bandwidth / 1_000_000

    if total_mbps < 100:
        recommendation = "100Mbps switch sufficient"
    elif total_mbps < 1000:
        recommendation = "1Gbps switch recommended"
    else:
        recommendation = "10Gbps uplink required"

    return {
        "total_bandwidth_mbps": round(total_mbps, 2),
        "total_bandwidth_gbps": round(total_mbps / 1000, 3),
        "recommendation": recommendation,
    }

bandwidth_calculator_tool = Tool(
    name="bandwidth_calculator",
    description="Calculate network bandwidth requirements",
    input_schema={
        "type": "object",
        "properties": {
            "camera_count": {"type": "integer", "description": "Number of cameras"},
            "bitrate_per_camera": {"type": "integer", "description": "Bitrate per camera in bps"},
            "simultaneous_streams": {"type": "integer", "description": "Number of simultaneous streams (default 1)"},
        },
        "required": ["camera_count", "bitrate_per_camera"],
    },
    fn=bandwidth_calculator_fn,
)

registry.register(bandwidth_calculator_tool)
```

---

### Task 7: AI Service — OpenRouter Integration

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/ai_service.py`

- [ ] **Step 1: Create `backend/app/services/ai_service.py`**

```python
import json
import httpx
from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL
from app.tools.registry import registry

SYSTEM_PROMPT = """You are a senior CCTV pre-sales engineer. You help with:
- CCTV, NVR, PoE switch recommendations
- Storage and bandwidth calculations
- Troubleshooting guidance
- Proposal generation

You have access to tools for storage/bandwidth calculations and product lookup.
Use them when appropriate. Be concise, technical, and practical.

Supported brands: Hikvision, Dahua, Uniview, Ezviz, Hiview, Bardi, TP-Link Tapo, Imou, Hilook."""

async def chat_with_tools(messages: list[dict]) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    tools = registry.to_openrouter_tools()

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": full_messages,
        "tools": tools if tools else None,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        choice = data["choices"][0]
        msg = choice["message"]

        if msg.get("tool_calls"):
            tool_results = []
            for tc in msg["tool_calls"]:
                tool = registry.get(tc["function"]["name"])
                if tool:
                    args = json.loads(tc["function"]["arguments"])
                    result = await tool.execute(**args)
                    tool_results.append({"tool": tc["function"]["name"], "result": result})

            full_messages.append(msg)
            for tr in tool_results:
                full_messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(tr["result"]),
                })

            payload["messages"] = full_messages
            payload.pop("tools", None)

            resp2 = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp2.raise_for_status()
            data2 = resp2.json()
            final_msg = data2["choices"][0]["message"]
            return {
                "content": final_msg["content"],
                "tool_calls": tool_results,
            }

        return {
            "content": msg["content"],
            "tool_calls": [],
        }
```

---

### Task 8: API Routes

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/routes.py`

- [ ] **Step 1: Create `backend/app/api/routes.py`**

```python
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ToolCall
from app.services.ai_service import chat_with_tools
from app.tools.registry import registry

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        result = await chat_with_tools(messages)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools")
async def list_tools():
    return {"tools": [{"name": t.name, "description": t.description} for t in registry.list_tools()]}

@router.post("/tools/storage-calculator")
async def storage_calculator(camera_count: int, resolution: str, fps: int = 30, recording_days: int = 30):
    tool = registry.get("storage_calculator")
    return await tool.execute(camera_count=camera_count, resolution=resolution, fps=fps, recording_days=recording_days)

@router.post("/tools/bandwidth-calculator")
async def bandwidth_calculator(camera_count: int, bitrate_per_camera: int, simultaneous_streams: int = 1):
    tool = registry.get("bandwidth_calculator")
    return await tool.execute(camera_count=camera_count, bitrate_per_camera=bitrate_per_camera, simultaneous_streams=simultaneous_streams)
```

---

### Task 9: Frontend Scaffold + Chat UI

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/next.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/src/app/layout.tsx`
- Create: `frontend/src/app/globals.css`
- Create: `frontend/src/app/page.tsx`
- Create: `frontend/src/lib/api.ts`

- [ ] **Step 1: Scaffold Next.js project**

Run:
```bash
cd /Users/macbookair/Desktop/ai-assistant-adi
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --no-import-alias
cd frontend
npm install daisyui@latest
```

- [ ] **Step 2: Configure `tailwind.config.ts` for daisyUI**

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: { extend: {} },
  plugins: [require("daisyui")],
};
export default config;
```

- [ ] **Step 3: Create `frontend/src/lib/api.ts`**

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

export async function sendChat(messages: Message[]) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  if (!res.ok) throw new Error("API error");
  return res.json();
}
```

- [ ] **Step 4: Create `frontend/src/app/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 5: Create `frontend/src/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Assistant Adi — CCTV Pre-Sales Tool",
  description: "AI-powered CCTV & Security System Assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-base-200">{children}</body>
    </html>
  );
}
```

- [ ] **Step 6: Create `frontend/src/app/page.tsx`**

```tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { sendChat, Message } from "@/lib/api";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Halo! Saya Adi, AI Assistant CCTV Pre-Sales Engineering. Ada yang bisa saya bantu?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEnd = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: "user", content: input };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChat(
        updated.filter((m) => m.role !== "system")
      );
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.content },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Maaf, terjadi error. Coba lagi." },
      ]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      <header className="text-center py-4">
        <h1 className="text-2xl font-bold">AI Assistant Adi</h1>
        <p className="text-sm text-base-content/60">CCTV & Security System Pre-Sales Engineering</p>
      </header>
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`chat ${m.role === "user" ? "chat-end" : "chat-start"}`}>
            <div className={`chat-bubble ${m.role === "user" ? "chat-bubble-primary" : ""}`}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat chat-start">
            <div className="chat-bubble"><span className="loading loading-dots loading-sm"></span></div>
          </div>
        )}
        <div ref={chatEnd} />
      </div>
      <div className="join w-full">
        <input
          className="input input-bordered join-item flex-1"
          placeholder="Tanya tentang CCTV, storage, troubleshooting..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={loading}
        />
        <button className="btn btn-primary join-item" onClick={handleSend} disabled={loading}>
          Kirim
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 7: Create `frontend/vercel.json`**

```json
{
  "framework": "nextjs",
  "maxDuration": 30
}
```

---

### Task 10: Render Deployment Config

**Files:**
- Create: `backend/render.yaml`
- Create: `backend/Dockerfile`

- [ ] **Step 1: Create `backend/render.yaml`**

```yaml
services:
  - type: web
    name: ai-assistant-adi-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false
      - key: OPENROUTER_MODEL
        value: google/gemini-2.0-flash-exp
```

- [ ] **Step 2: Check requirements.txt has pinned versions**

Make sure `backend/requirements.txt` contains:
```
fastapi==0.111.0
pydantic==2.7.4
uvicorn==0.30.1
sqlalchemy==2.0.31
httpx==0.27.0
python-dotenv==1.0.1
```
