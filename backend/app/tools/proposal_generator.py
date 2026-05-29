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
3. **Recommended Bill of Materials (BOM)** — Tabel produk yang direkomendasikan dengan harga
4. **Scope of Work (SOW)** — Lingkup pekerjaan instalasi dan konfigurasi
5. **Kesimpulan** — Penutup dan rekomendasi

PANDUAN FORMAT:
- Gunakan bahasa Indonesia formal dan profesional
- Tabel BOM gunakan format markdown table dengan kolom: No, Deskripsi Produk, Qty, Harga Satuan (IDR), Subtotal (IDR)
- Harga dalam rupiah, gunakan format angka dengan pemisah titik (contoh: 1.500.000)
- Selalu gunakan heading level 2 (##) untuk setiap section
- Gunakan tabel untuk BOM, jangan pakai bullet list
- Kalkulasi storage: tampilkan dalam format GB dengan 2 desimal, lalu konversi ke TB jika > 1000 GB
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
    brand: str = "",
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

    def fmt_price(val):
        if not val: return "0"
        return f"{val:,}".replace(",", ".")

    camera_products = await lookup_products_fn(category="cameras", keyword=resolution, brand=brand or None)
    hdd_products = await lookup_products_fn(category="hdd")
    nvr_products = await lookup_products_fn(category="nvr", brand=brand or None)
    poe_products = await lookup_products_fn(category="poe_switches")

    recommended_hdd_tb = storage_result.get('recommended_hdd_tb', 0)
    rec_hdd_count = max(1, round(recommended_hdd_tb / 8)) if recommended_hdd_tb else 1

    best_camera = (camera_products.get("products") or [None])[0]
    best_nvr = (nvr_products.get("products") or [None])[0]
    best_hdd = (hdd_products.get("products") or [None])[0]
    best_poe = (poe_products.get("products") or [None])[0]

    bom_items = []

    if best_camera:
        camera_price = best_camera.get("harga", 0) or 0
        bom_items.append({
            "no": 1, "deskripsi": f"Kamera {best_camera.get('nama', 'CCTV')} - {best_camera.get('resolusi', resolution)} ({best_camera.get('jenis', '')})",
            "qty": camera_count, "harga": camera_price, "subtotal": camera_count * camera_price
        })

    if best_nvr:
        nvr_price = best_nvr.get("harga", 0) or best_nvr.get("harga_estimasi", 0) or 0
        ch = best_nvr.get("channel", 0)
        if ch == 0 or ch >= camera_count:
            bom_items.append({
                "no": 2, "deskripsi": f"NVR {best_nvr.get('nama', '')} - {ch} Channel",
                "qty": 1, "harga": nvr_price, "subtotal": nvr_price
            })

    if best_hdd:
        hdd_price = best_hdd.get("harga_estimasi", 0) or 0
        hdd_cap = best_hdd.get("kapasitas_tb", 8)
        hdd_count = max(1, round(recommended_hdd_tb / hdd_cap)) if recommended_hdd_tb else 1
        bom_items.append({
            "no": 3, "deskripsi": f"HDD {best_hdd.get('nama', 'Surveillance HDD')} - {hdd_cap}TB",
            "qty": hdd_count, "harga": hdd_price, "subtotal": hdd_count * hdd_price
        })

    if best_poe:
        poe_price = best_poe.get("harga", 0) or best_poe.get("harga_estimasi", 0) or 0
        bom_items.append({
            "no": 4, "deskripsi": f"PoE Switch {best_poe.get('nama', '')} - {best_poe.get('port_count', '?')} Port",
            "qty": 1, "harga": poe_price, "subtotal": poe_price
        })

    bom_kabel_price = 300000
    bom_items.append({
        "no": 5, "deskripsi": "Kabel UTP Cat6 + Konektor RJ45 + Accessories",
        "qty": 1, "harga": bom_kabel_price, "subtotal": bom_kabel_price
    })

    total_bom = sum(item["subtotal"] for item in bom_items)

    bom_markdown_table = "| No | Deskripsi Produk | Qty | Harga Satuan (IDR) | Subtotal (IDR) |\n"
    bom_markdown_table += "|---|-----------------|-----|-------------------|----------------|\n"
    for i in bom_items:
        bom_markdown_table += f"| {i['no']} | {i['deskripsi']} | {i['qty']} | {fmt_price(i['harga'])} | {fmt_price(i['subtotal'])} |\n"

    user_prompt = f"""Buatkan proposal teknis untuk proyek CCTV dengan format markdown.

STRUKTUR:
## 1. Executive Summary
## 2. Technical Overview
## 3. Recommended Bill of Materials (BOM)
## 4. Scope of Work (SOW)
## 5. Kesimpulan

DATA KLIEN:
- Nama: {client_name}
- Proyek: {project_type}
- Lokasi: {location or "(tidak disebutkan)"}
- Kamera: {camera_count} unit {resolution}
- Recording: {recording_days} hari
- Brand: {brand or "Semua brand"}

HASIL KALKULASI:
- Storage/hari: {storage_result['daily_storage_gb']} GB
- Storage/bulan: {storage_result['monthly_storage_gb']} GB
- Rekomendasi HDD: {storage_result['recommended_hdd_tb']} TB
- Bandwidth: {bandwidth_result['total_bandwidth_mbps']} Mbps
- Rekomendasi Switch: {bandwidth_result['recommendation']}

Kebutuhan tambahan: {requirements_text or "(tidak ada)"}

TUGAS:
- Tulis section 1 (Executive Summary), 2 (Technical Overview), 4 (SOW), 5 (Kesimpulan)
- UNTUK SECTION 3 (BOM), COPY TABLE DI BAWAH INI PERSIS. JANGAN DIUBAH.

BOM TABLE (copy this exactly into section 3):
{bom_markdown_table}
**TOTAL: Rp {fmt_price(total_bom)}**

Gunakan bahasa Indonesia formal. Harga dalam Rupiah."""

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
