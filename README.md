# AI Assistant Adi

**AI-powered CCTV & Security System Pre-Sales Engineering Assistant.**

Internal tool untuk pre-sales engineer, teknisi CCTV, dan tim sales. Membantu rekomendasi produk, kalkulasi teknis, troubleshooting, dan pembuatan proposal proyek.

---

## Fitur

- **AI Chat Assistant** — Tanya apa saja tentang CCTV, NVR, PoE switch, storage, troubleshooting
- **Storage Calculator** — Hitung kebutuhan HDD berdasarkan jumlah kamera, resolusi, FPS, durasi rekam
- **Bandwidth Calculator** — Hitung kebutuhan bandwidth jaringan dan rekomendasi switch
- **Product Recommendations** — Cari produk dari katalog 9 brand (Hikvision, Dahua, Uniview, dll)
- **Proposal Generator** — Buat draft proposal proyek CCTV profesional dalam format markdown
- **Tool Calling** — AI secara otomatis memanggil kalkulator dan katalog saat dibutuhkan

---

## Tech Stack

| Layer | Teknologi | Deployment |
|---|---|---|
| Frontend | Next.js 16 + TailwindCSS v4 + daisyUI 5 | Vercel (free) |
| Backend | Python 3.12 + FastAPI | Render (free tier) |
| Database | SQLite (MVP), arsitektur siap migrasi ke PostgreSQL | Ephemeral (Render free) |
| AI Provider | OpenRouter (default: Google Gemini Flash) | API eksternal |

---

## Project Structure

```
ai-assistant-adi/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py           # API endpoints (/api/chat, /api/proposals, /api/tools)
│   │   ├── catalog/
│   │   │   ├── cameras.json        # 20 produk kamera
│   │   │   ├── nvr.json            # 8 NVR
│   │   │   ├── poe_switches.json   # 9 PoE switch
│   │   │   └── hdd.json            # 9 HDD surveillance
│   │   ├── config.py               # Pydantic BaseSettings
│   │   ├── db/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── models/
│   │   ├── prompts/
│   │   │   └── system_prompt.py    # Identitas AI Assistant Adi
│   │   ├── schemas/
│   │   │   └── chat.py             # Pydantic request/response models
│   │   ├── services/
│   │   │   └── ai_service.py       # OpenRouter integration + tool calling
│   │   └── tools/
│   │       ├── registry.py         # Tool registry pattern
│   │       ├── storage_calculator.py
│   │       ├── bandwidth_calculator.py
│   │       ├── product_lookup.py
│   │       └── proposal_generator.py
│   ├── render.yaml                 # Render Blueprint config
│   ├── requirements.txt
│   └── .env                        # Local environment
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # Root layout + sidebar navigation
│   │   │   ├── page.tsx            # Chat Assistant (home)
│   │   │   └── proposal-generator/
│   │   │       └── page.tsx        # Proposal Generator page
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx   # Chat UI with daisyUI bubbles
│   │   │   └── ToolResult.tsx      # Tool call result cards
│   │   └── lib/
│   │       └── api.ts              # API client (chat + proposals)
│   ├── vercel.json
│   └── package.json
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-05-29-ai-assistant-adi-design.md
│       └── plans/
│           └── 2026-05-29-phase1-project-scaffold.md
└── README.md
```

---

## Panduan Menjalankan Secara Lokal

### Prasyarat

- Python 3.12+
- Node.js 20+
- npm
- OpenRouter API key ([daftar gratis](https://openrouter.ai))

### 1. Backend

```bash
cd backend

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env .env.local
# Edit .env.local — isi OPENROUTER_API_KEY dengan key kamu

# Jalankan server
uvicorn app.main:app --reload --port 8000
```

Backend berjalan di `http://localhost:8000`. Cek health: `GET http://localhost:8000/health`

### 2. Frontend

```bash
cd frontend
npm install

# Setup environment (optional — default ke localhost:8000)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# Jalankan development server
npm run dev
```

Frontend berjalan di `http://localhost:3000`.

### 3. Testing

Buka `http://localhost:3000` dan kirim pesan ke Adi:
- "Rekomendasi CCTV untuk gudang 500m2"
- "Hitung storage untuk 32 kamera 4MP selama 30 hari"
- "Rekomendasi NVR untuk 16 kamera"

---

## Panduan Deployment

### Frontend → Vercel

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

Set environment variable di Vercel dashboard:
- `NEXT_PUBLIC_API_URL` → `https://[your-backend].onrender.com/api`

### Backend → Render (Free Tier)

Cara 1: Render Blueprint (recommended)

1. Push project ke GitHub
2. Di Render Dashboard → New → Blueprint
3. Pilih repo → Render membaca `backend/render.yaml` otomatis
4. Set `OPENROUTER_API_KEY` sebagai secret environment variable

Cara 2: Manual Web Service

1. Di Render Dashboard → New → Web Service
2. Pilih repo, set:
   - **Name:** `ai-assistant-adi-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Tambahkan environment variables:
   - `OPENROUTER_API_KEY` (secret)
   - `OPENROUTER_MODEL` → `google/gemini-2.0-flash-exp`
   - `CORS_ORIGINS` → `["https://[your-frontend].vercel.app"]`
4. Pilih **Free** plan → Deploy

**Catatan:** Render free tier melakukan spin-down setelah 15 menit tidak digunakan. Koneksi pertama setelah idle akan memakan waktu ~30 detik (cold start). Vercel `maxDuration: 30` sudah dikonfigurasi untuk mengakomodasi ini.

---

## API Endpoints

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/chat` | Kirim pesan ke AI Assistant |
| GET | `/api/tools` | Daftar tools yang tersedia |
| POST | `/api/tools/storage-calculator` | Kalkulasi storage (direct) |
| POST | `/api/tools/bandwidth-calculator` | Kalkulasi bandwidth (direct) |
| POST | `/api/proposals/generate` | Generate proposal proyek |

---

## Brands Tersedia di Katalog

Hikvision, Dahua, Uniview, Ezviz, Hiview, Bardi, TP-Link Tapo, Imou, Hilook

Katalog produk dalam format JSON di `backend/app/catalog/` — mudah diedit tanpa perlu deploy ulang backend.

---

## Engineering Notes

- **Storage:** Chat history disimpan di frontend localStorage. Backend SQLite bersifat sementara (ephemeral disk Render).
- **Token Optimization:** Product lookup menggunakan filter gate — AI hanya mendapat produk relevan, bukan seluruh katalog.
- **Tool System:** Semua kalkulasi dilewatkan ke tool registry, bukan di-generate oleh AI (mencegah hallucination).
- **Minimal Dependencies:** Tidak ada Kubernetes, microservices, Redis, atau RabbitMQ.

---

## Lisensi

Proprietary — Internal tool.
