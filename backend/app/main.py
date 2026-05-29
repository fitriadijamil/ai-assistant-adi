import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

from app.tools import storage_calculator  # noqa: F401 — registers tools
from app.tools import bandwidth_calculator  # noqa: F401 — registers tools
from app.tools import product_lookup  # noqa: F401 — registers tools

app = FastAPI(
    title="AI Assistant Adi",
    description="AI-powered CCTV & Security System Assistant Backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
