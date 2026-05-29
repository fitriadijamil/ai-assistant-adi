import json
import logging

import httpx

from app.config import settings
from app.tools.storage_calculator import storage_calculator_fn
from app.tools.bandwidth_calculator import bandwidth_calculator_fn
from app.tools.product_lookup import lookup_products_fn

logger = logging.getLogger(__name__)

PROPOSAL_SYSTEM_PROMPT = """Anda adalah Adi, AI Assistant Proposal Writer untuk perusahaan CCTV & Security System.

Tugas Anda adalah membuat draft proposal teknis yang profesional dalam format markdown.

STRUKTUR PROPOSAL WAJIB:
1. **Executive Summary** — Ringkasan eksekutif tentang kebutuhan klien dan solusi yang ditawarkan
2. **Technical Overview** — Gambaran teknis termasuk hasil kalkulasi storage dan bandwidth
3. **Recommended Bill of Materials (BOM)** — Tabel produk yang direkomendasikan dengan harga estimasi
4. **Scope of Work (SOW)** — Lingkup pekerjaan instalasi dan konfigurasi
5. **Kesimpulan** — Penutup dan rekomendasi

PANDUAN:
- Gunakan bahasa Indonesia formal dan profesional
- Tabel BOM harus rapi menggunakan format markdown table
- Sertakan nomor dan harga estimasi dalam tabel BOM
- Jika ada data kalkulasi, sertakan dalam Technical Overview
- Jangan membuat spek palsu — jika tidak yakin, tulis "perlu konfirmasi lebih lanjut"
- Akhiri dengan catatan bahwa harga dapat berubah"""


async def generate_proposal(
    client_name: str,
    project_type: str,
    location: str,
    camera_count: int,
    resolution: str,
    recording_days: int,
    requirements_text: str,
    selected_products: list[dict],
) -> dict:
    if not settings.openrouter_api_key:
        return {
            "proposal_markdown": "AI Assistant belum dikonfigurasi. Silakan atur OPENROUTER_API_KEY di file .env.",
            "storage_summary": None,
            "bandwidth_summary": None,
        }

    storage_result = await storage_calculator_fn(
        camera_count=camera_count,
        resolution=resolution,
        fps=30,
        recording_days=recording_days,
    )

    bitrate = storage_result.get("bitrate_used_bps", 8_000_000)
    bandwidth_result = await bandwidth_calculator_fn(
        camera_count=camera_count,
        bitrate_per_camera=bitrate,
        simultaneous_streams=1,
    )

    camera_products = await lookup_products_fn(category="cameras", keyword=resolution)
    hdd_products = await lookup_products_fn(category="hdd")

    user_prompt = f"""Buatkan proposal teknis untuk proyek CCTV dengan data berikut:

## Data Klien
- Nama Klien: {client_name}
- Tipe Proyek: {project_type}
- Lokasi: {location or "(tidak disebutkan)"}
- Jumlah Kamera: {camera_count}
- Resolusi: {resolution}
- Durasi Recording: {recording_days} hari

## Kebutuhan Tambahan
{requirements_text or "(tidak ada kebutuhan tambahan)"}

## Hasil Kalkulasi Teknis
### Storage
- Kebutuhan per hari: {storage_result['daily_storage_gb']} GB
- Kebutuhan per bulan ({recording_days} hari): {storage_result['monthly_storage_gb']} GB
- Rekomendasi HDD: {storage_result['recommended_hdd_tb']} TB
- Bitrate per kamera: {bitrate} bps

### Bandwidth
- Total bandwidth: {bandwidth_result['total_bandwidth_mbps']} Mbps
- Rekomendasi switch: {bandwidth_result['recommendation']}

## Katalog Produk Tersedia
### Kamera ({resolution})
{json.dumps(camera_products.get('products', [])[:5], indent=2, ensure_ascii=False)}

### HDD Surveillance
{json.dumps(hdd_products.get('products', [])[:5], indent=2, ensure_ascii=False)}

## Produk yang Dipilih Langsung oleh User
{json.dumps(selected_products, indent=2, ensure_ascii=False) if selected_products else "(belum ada produk spesifik yang dipilih)"}

Susun proposal profesional berdasarkan data di atas."""

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": PROPOSAL_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"] or ""

            return {
                "proposal_markdown": content,
                "storage_summary": storage_result,
                "bandwidth_summary": bandwidth_result,
            }

    except httpx.TimeoutException:
        logger.error("Proposal generation timed out")
        return {
            "proposal_markdown": "Maaf, pembuatan proposal timeout. Silakan coba lagi dengan data yang lebih sederhana.",
            "storage_summary": storage_result,
            "bandwidth_summary": bandwidth_result,
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter returned {e.response.status_code}: {e.response.text}")
        return {
            "proposal_markdown": f"Maaf, terjadi kesalahan pada layanan AI (HTTP {e.response.status_code}). Silakan coba lagi.",
            "storage_summary": storage_result,
            "bandwidth_summary": bandwidth_result,
        }
    except Exception as e:
        logger.exception(f"Unexpected error in proposal generation: {e}")
        return {
            "proposal_markdown": "Maaf, terjadi kesalahan yang tidak terduga. Silakan coba lagi.",
            "storage_summary": storage_result,
            "bandwidth_summary": bandwidth_result,
        }
