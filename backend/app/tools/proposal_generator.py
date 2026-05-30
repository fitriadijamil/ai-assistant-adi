import json
import logging
import math

import httpx

from app.config import settings
from app.tools.storage_calculator import storage_calculator_fn
from app.tools.bandwidth_calculator import bandwidth_calculator_fn
from app.tools.product_lookup import lookup_products_fn

logger = logging.getLogger(__name__)

PROPOSAL_SYSTEM_PROMPT = """Anda adalah Adi, AI Assistant Proposal Writer untuk perusahaan CCTV & Security System PT. Adi Sukses Sejahtera.

Tugas Anda adalah membuat SURAT PENAWARAN HARGA (proposal penawaran) dalam format formal bahasa Indonesia.

STRUKTUR SURAT PENAWARAN WAJIB:
1. **KOP SURAT** — Gunakan header: "PT. ADI SUKSES SEJAHTERA" (subtitle: CCTV & Security System Specialist)
   Alamat: Komplek Perkantosa Kenari Permai Blok C No. 14 - Jl. Raya Curug Agung, Cimanggis - Depok
   Telp/WA: 085156044200
   Email: info@adicctv.com | Website: adicctv.com
   (Tampilkan sebagai teks biasa, bukan markdown table)
2. **Nomor & Tanggal Surat** — Nomor surat otomatis: 001/SPH-ASS/{MONTH_ROMAN}/2026. Tanggal adalah hari ini.
3. **Perihal** — "Penawaran Harga Sistem CCTV [project_type] untuk [client_name]"
4. **Data Customer** — Kepada Yth: [customer_attention], [customer_address]
5. **Isi Penawaran**:
   a. Latar Belakang
   b. Spesifikasi Teknis (gunakan data kalkulasi storage & bandwidth)
   c. Bill of Materials (BOM) — tulis PERSIS: <!--BOM-->
   d. Ketentuan:
      - Harga sudah termasuk PPN 11%
      - Harga sudah termasuk ongkos kirim area Jabodetabek
      - Harga belum termasuk instalasi dan konfigurasi (jika terpisah)
   e. **Syarat & Ketentuan**:
      - Pembayaran: Transfer Bank ke rekening BCA 6080473271 a/n Fitriadi Jamil
      - Garansi Produk: 1 tahun
      - Garansi Instalasi: 1 bulan
      - Pengiriman: 1-2 minggu setelah PO diterima
      - Masa berlaku penawaran: 14 hari
6. **Penutup** — Tanda tangan: Hormat kami, PT. Adi Sukses Sejahtera, Fitriadi Jamil (Director)

PANDUAN FORMAT:
- Gunakan bahasa Indonesia formal dan profesional
- Harga dalam rupiah, gunakan format angka dengan pemisah titik (contoh: 1.500.000)
- JANGAN menulis tabel BOM — cukup tulis <!--BOM--> di bagian BOM
- Kalkulasi storage: tampilkan dalam format GB/TB
- Jika ada data kalkulasi, sertakan dalam Spesifikasi Teknis
- Jangan membuat spek palsu — jika tidak yakin, tulis "perlu konfirmasi lebih lanjut"""


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

    user_prompt = f"""Buatkan Surat Penawaran Harga untuk proyek CCTV. Gunakan data berikut:

DATA PERUSAHAAN:
- Nama: PT. Adi Sukses Sejahtera
- Alamat: Komplek Perkantosa Kenari Permai Blok C No. 14 - Jl. Raya Curug Agung, Cimanggis - Depok
- Telp/WA: 085156044200
- Email: info@adicctv.com
- Website: adicctv.com

NOMOR SURAT: {letter_number}
TANGGAL: {today.strftime('%d %B %Y')}

DATA KLIEN:
- Nama: {client_name}
- Kepada Yth: {customer_attention or 'Yth. Bapak/Ibu'}
- Alamat: {customer_address or '(tidak disebutkan)'}
- Proyek: {project_type}
- Lokasi: {location or '(tidak disebutkan)'}
- Kamera: {camera_count} unit {resolution}
- Recording: {recording_days} hari
- Brand: {brand or 'Semua brand'}

HASIL KALKULASI:
- Storage/hari: {storage_result['daily_storage_gb']} GB
- Storage/bulan: {storage_result['monthly_storage_gb']} GB
- Rekomendasi HDD: {storage_result['recommended_hdd_tb']} TB
- Bandwidth: {bandwidth_result['total_bandwidth_mbps']} Mbps
- Rekomendasi Switch: {bandwidth_result['recommendation']}

Kebutuhan tambahan: {requirements_text or '(tidak ada)'}

TUGAS:
- Buat surat penawaran sesuai STRUKTUR yang sudah ditentukan di system prompt
- Tulis perihal: "Penawaran Harga Sistem {project_type} untuk {client_name}"
- UNTUK BAGIAN BOM (Bill of Materials), TULIS PERSIS: <!--BOM-->
- JANGAN TULIS TABEL ATAU KONTEN APAPUN DI BAGIAN BOM. CUKUP TULIS <!--BOM-->
- Gunakan bahasa Indonesia formal"""

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
