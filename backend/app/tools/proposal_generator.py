import json
import logging
import math

import httpx

from app.config import settings
from app.tools.storage_calculator import storage_calculator_fn
from app.tools.bandwidth_calculator import bandwidth_calculator_fn
from app.tools.product_lookup import lookup_products_fn

logger = logging.getLogger(__name__)

PROPOSAL_SYSTEM_PROMPT = """Anda adalah Adi, AI Assistant Proposal Writer untuk adicctv.com.

Tugas Anda adalah menulis isi surat penawaran harga (BODY SAJA, tanpa header/kop surat).

Yang AKAN ANDA TULIS hanyalah:
- 1 paragraf pendek pengantar teknis (1-2 kalimat) yang menyebutkan jumlah kamera, resolusi, kebutuhan storage/bandwidth
- Kemudian tulis PERSIS: <!--BOM-->

JANGAN tulis header, kop surat, nomor surat, tanggal, perihal, kepada yth, syarat & ketentuan, atau penutup — semua itu sudah ditangani oleh sistem.

PANDUAN FORMAT:
- Bahasa Indonesia formal
- 1 paragraf pendek saja, lalu <!--BOM-->"""


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
    customer_attention: str = "",
    customer_address: str = "",
) -> dict:
    if not settings.openrouter_api_key:
        return {
            "proposal_markdown": "AI Assistant belum dikonfigurasi. Silakan atur OPENROUTER_API_KEY di file .env.",
            "storage_summary": None,
            "bandwidth_summary": None,
            "bom_data": None,
            "letter_info": None,
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

    best_camera = (camera_products.get("products") or [None])[0]
    best_nvr = (nvr_products.get("products") or [None])[0]

    all_hdd = hdd_products.get("products") or []
    all_hdd.sort(key=lambda x: x.get("kapasitas_tb", 0), reverse=True)
    best_hdd = None
    hdd_count = 1
    if all_hdd and recommended_hdd_tb:
        for h in all_hdd:
            cap = h.get("kapasitas_tb", 0)
            if cap > 0:
                count = math.ceil(recommended_hdd_tb / cap)
                best_hdd = h
                hdd_count = count
                break
    if not best_hdd and all_hdd:
        best_hdd = all_hdd[0]

    best_poe = (poe_products.get("products") or [None])[0]

    bom_items = []

    kategori_a = []
    kategori_b = []
    item_no = 0

    def add_item(deskripsi: str, tipe: str, qty: int, satuan: str, harga: int, cat: str):
        nonlocal item_no
        item_no += 1
        total = qty * harga
        entry = {"no": item_no, "deskripsi": deskripsi, "tipe": tipe, "qty": qty, "satuan": satuan, "harga": harga, "total": total}
        if cat == "A":
            kategori_a.append(entry)
        else:
            kategori_b.append(entry)
        return entry

    if best_camera:
        camera_price = best_camera.get("harga", 0) or 0
        add_item(
            f"Kamera {best_camera.get('nama', 'CCTV')} - {best_camera.get('resolusi', resolution)} ({best_camera.get('jenis', '')})",
            "IP Camera",
            camera_count, "Unit", camera_price, "A"
        )

    if best_nvr:
        nvr_price = best_nvr.get("harga", 0) or best_nvr.get("harga_estimasi", 0) or 0
        ch = best_nvr.get("channel", 0)
        if ch == 0 or ch >= camera_count:
            add_item(
                f"NVR {best_nvr.get('nama', '')} - {ch} Channel",
                "NVR Recorder",
                1, "Unit", nvr_price, "A"
            )

    if best_hdd:
        hdd_price = best_hdd.get("harga", 0) or 0
        hdd_cap = best_hdd.get("kapasitas_tb", 8)
        add_item(
            f"HDD {best_hdd.get('nama', 'Surveillance HDD')} - {hdd_cap}TB",
            "Storage",
            hdd_count, "Unit", hdd_price, "A"
        )

    if best_poe:
        poe_price = best_poe.get("harga", 0) or best_poe.get("harga_estimasi", 0) or 0
        add_item(
            f"PoE Switch {best_poe.get('nama', '')} - {best_poe.get('port', '?')} Port",
            "Switch",
            1, "Unit", poe_price, "A"
        )

    add_item(
        "Kabel UTP Cat6 + Konektor RJ45 + Aksesoris Instalasi",
        "Material",
        1, "Lot", 300000, "B"
    )

    total_a = sum(i["total"] for i in kategori_a)
    total_b = sum(i["total"] for i in kategori_b)
    total_bom = total_a + total_b

    bom_data = {"kategori_a": kategori_a, "kategori_b": kategori_b, "total_a": total_a, "total_b": total_b, "grand_total": total_bom}

    import datetime
    today = datetime.date.today()
    month_roman = {1:"I",2:"II",3:"III",4:"IV",5:"V",6:"VI",7:"VII",8:"VIII",9:"IX",10:"X",11:"XI",12:"XII"}
    bulan_romawi = month_roman[today.month]
    letter_number = f"001/SPH-ASS/{bulan_romawi}/{today.year}"

    letter_info = {
        "letter_number": letter_number,
        "date": today.strftime("%d %B %Y"),
        "customer_attention": customer_attention or "Yth. Bapak/Ibu",
        "customer_address": customer_address or "",
        "client_name": client_name,
        "project_type": project_type,
        "grand_total": total_bom,
    }

    user_prompt = f"""Tulis isi surat penawaran untuk proyek CCTV berikut:

DATA KLIEN:
- Nama: {client_name}
- Kepada Yth, Bapak/Ibu : {customer_attention or 'Yth. Bapak/Ibu'}
- Proyek: {project_type}
- Kamera: {camera_count} unit {resolution}
- Recording: {recording_days} hari
- Brand: {brand or 'Semua brand'}

HASIL KALKULASI:
- Storage/hari: {storage_result['daily_storage_gb']} GB
- Storage/bulan: {storage_result['monthly_storage_gb']} GB
- Rekomendasi HDD: {storage_result['recommended_hdd_tb']} TB
- Bandwidth: {bandwidth_result['total_bandwidth_mbps']} Mbps

Kebutuhan tambahan: {requirements_text or '(tidak ada)'}

TUGAS:
- Tulis 1 paragraf pendek pengantar teknis berdasarkan data di atas
- Kemudian tulis PERSIS: <!--BOM-->
- JANGAN tulis header/kop/nomor/tanggal/perihal/syarat/penutup"""

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
                "bom_data": bom_data,
                "letter_info": letter_info,
            }

    except httpx.TimeoutException:
        logger.error("Proposal generation timed out")
        return {
            "proposal_markdown": "Maaf, pembuatan proposal timeout. Silakan coba lagi dengan data yang lebih sederhana.",
            "storage_summary": storage_result,
            "bandwidth_summary": bandwidth_result,
            "bom_data": None,
            "letter_info": None,
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter returned {e.response.status_code}: {e.response.text}")
        return {
            "proposal_markdown": f"Maaf, terjadi kesalahan pada layanan AI (HTTP {e.response.status_code}). Silakan coba lagi.",
            "storage_summary": storage_result,
            "bandwidth_summary": bandwidth_result,
            "bom_data": None,
            "letter_info": None,
        }
    except Exception as e:
        logger.exception(f"Unexpected error in proposal generation: {e}")
        return {
            "proposal_markdown": "Maaf, terjadi kesalahan yang tidak terduga. Silakan coba lagi.",
            "storage_summary": storage_result,
            "bandwidth_summary": bandwidth_result,
            "bom_data": None,
            "letter_info": None,
        }
