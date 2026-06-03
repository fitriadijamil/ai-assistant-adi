import json
import logging
import math
import re
import datetime

import httpx

from app.config import settings
from app.config_loader import load_config
from app.tools.storage_calculator import storage_calculator_fn
from app.tools.bandwidth_calculator import bandwidth_calculator_fn
from app.tools.product_lookup import lookup_products_fn
from app.tools.registry import Tool, registry

logger = logging.getLogger(__name__)

config = load_config()
business = config.get("business", {})
proposal_cfg = config.get("proposal", {})
contact_cfg = config.get("contact", {})
bank_cfg = config.get("bank_account", {})
cable_cfg = config.get("cable_prices", {})
project_types = config.get("project_types", [])
system_types = config.get("system_types", [])
sd_card_opts = config.get("sd_card_options", [])
accessories_pct = config.get("accessories_percentage", 25)
conduit_mult = config.get("conduit_multiplier", 1.5)

_terms_raw = proposal_cfg.get("terms", [])
_terms = [t.replace("{tax_label}", business.get("tax_label", "PPN")).replace("{tax_rate}", str(business.get("tax_rate", 11))) for t in _terms_raw]

_business_name = business.get("name", "Bisnis")
_business_url = contact_cfg.get("website", "")

MONTH_ROMAN = {1:"I",2:"II",3:"III",4:"IV",5:"V",6:"VI",7:"VII",8:"VIII",9:"IX",10:"X",11:"XI",12:"XII"}


def _get_jasa_harga(project_type: str) -> int:
    pt = project_type.lower()
    for pt_config in project_types:
        if pt_config.get("id", "").lower() == pt:
            return pt_config.get("installation_fee", 275000)
        for kw in pt_config.get("keywords", []):
            if kw in pt:
                return pt_config.get("installation_fee", 275000)
    return 275000


PROPOSAL_SYSTEM_PROMPT = f"""Anda adalah AI Assistant Proposal Writer untuk {_business_url}.

Tugas Anda: tulis 1 kalimat (maks 15 kata) menjelaskan proyek secara teknis.

JANGAN PERNAH menulis tabel BOM, header surat, nomor surat, tanggal, perihal, kepada yth, syarat & ketentuan, atau penutup. CUKUP tulis 1 paragraf saja.

PANDUAN FORMAT:
- Bahasa Indonesia formal
- Harga dalam rupiah, gunakan format angka dengan pemisah titik (contoh: 1.500.000)"""


async def generate_proposal(
    client_name: str,
    project_type: str,
    location: str,
    camera_count_indoor: int = 0,
    camera_count_outdoor: int = 0,
    resolution: str = "4MP",
    system_type: str = "ip",
    recording_type: str = "full",
    recording_days: int = 30,
    selected_products: list[dict] | None = None,
    brand: str = "",
    kabel_utp_qty: int = 0,
    kabel_power_qty: int = 0,
    kabel_coaxial_qty: int = 0,
    use_pipa: bool = True,
    customer_attention: str = "",
    customer_address: str = "",
    sd_card_size: str = "",
) -> dict:
    if not settings.openrouter_api_key:
        return {
            "proposal_markdown": "AI Assistant belum dikonfigurasi. Silakan atur OPENROUTER_API_KEY di file .env.",
            "storage_summary": None,
            "bandwidth_summary": None,
            "bom_data": None,
            "letter_info": None,
        }

    total_cameras = camera_count_indoor + camera_count_outdoor
    if total_cameras < 1:
        total_cameras = 1

    recording_hours = 24 if recording_type == "full" else 12
    storage_result = await storage_calculator_fn(
        camera_count=total_cameras,
        resolution=resolution,
        fps=30,
        recording_days=recording_days,
        recording_type=recording_type,
    )

    bitrate = storage_result.get("bitrate_used_bps", 8_000_000)
    bandwidth_result = await bandwidth_calculator_fn(
        camera_count=total_cameras,
        bitrate_per_camera=bitrate,
        simultaneous_streams=1,
    )

    def fmt_price(val):
        if not val: return "0"
        return f"{val:,}".replace(",", ".")

    recommended_hdd_tb = storage_result.get('recommended_hdd_tb', 0)

    # --- BOM building ---
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

    # HDD lookup
    hdd_products = await lookup_products_fn(category="hdd")
    all_hdd = hdd_products.get("products") or []
    best_hdd = None
    hdd_count = 1
    if all_hdd and recommended_hdd_tb:
        best_waste = float('inf')
        best_cost = float('inf')
        for h in all_hdd:
            cap = h.get("kapasitas_tb", 0)
            price = h.get("harga", 0) or h.get("harga_estimasi", 0) or 0
            if cap <= 0:
                continue
            count = math.ceil(recommended_hdd_tb / cap)
            waste = (count * cap) - recommended_hdd_tb
            cost = count * price
            if waste < best_waste or (waste == best_waste and cost < best_cost):
                best_waste = waste
                best_cost = cost
                best_hdd = h
                hdd_count = count
    if not best_hdd and all_hdd:
        best_hdd = all_hdd[0]

    # Get relevant prices from config
    utp_price = cable_cfg.get("utp", {}).get("price_per_meter", 7500)
    power_price = cable_cfg.get("power", {}).get("price_per_meter", 17500)
    coaxial_price = cable_cfg.get("coaxial", {}).get("price_per_meter", 5250)
    conduit_price = cable_cfg.get("conduit", {}).get("price_per_unit", 12000)
    conduit_m_per_unit = cable_cfg.get("conduit", {}).get("meter_per_unit", 2.8)
    auto_utp_per_camera = cable_cfg.get("utp", {}).get("auto_per_camera", 30)

    is_analog = system_type == "analog"
    is_wireless = system_type == "wireless"

    if is_analog:
        analog_cameras = await lookup_products_fn(category="analog_cameras")
        xvr_products = await lookup_products_fn(category="xvr")
        psu_products = await lookup_products_fn(category="psu")

        best_camera = (analog_cameras.get("products") or [None])[0]
        best_xvr = None
        all_xvr = (xvr_products.get("products") or [])
        for x in all_xvr:
            xch = x.get("channel", 0)
            if xch == 0 or xch >= total_cameras:
                best_xvr = x
                break
        if not best_xvr and all_xvr:
            best_xvr = all_xvr[0]
        best_psu = (psu_products.get("products") or [None])[0]

        if best_xvr:
            ch = best_xvr.get("channel", 0)
            if ch:
                all_psu = psu_products.get("products") or []
                for p in all_psu:
                    if p.get("channel_count", 0) >= ch:
                        best_psu = p
                        break

        if best_camera:
            camera_price = best_camera.get("harga", 0) or 0
            camera_nama = best_camera.get('nama', 'CCTV')
            camera_res = best_camera.get('resolusi', '1080P')
            if camera_count_indoor > 0:
                add_item(f"Kamera Analog Indoor {camera_nama} ({camera_res})", "Analog Camera", camera_count_indoor, "Unit", camera_price, "A")
            if camera_count_outdoor > 0:
                add_item(f"Kamera Analog Outdoor {camera_nama} ({camera_res})", "Analog Camera", camera_count_outdoor, "Unit", camera_price, "A")

        if best_xvr:
            xvr_price = best_xvr.get("harga", 0) or 0
            ch = best_xvr.get("channel", 0)
            add_item(f"XVR {best_xvr.get('nama', '')} - {ch} Channel", "XVR Recorder", 1, "Unit", xvr_price, "A")

        if best_psu:
            psu_price = best_psu.get("harga", 0) or 0
            psu_ch = best_psu.get("channel_count", 0)
            add_item(f"Power Supply {psu_ch} Channel", "Power Supply", 1, "Unit", psu_price, "A")

        if best_hdd:
            hdd_price = best_hdd.get("harga", 0) or 0
            hdd_cap = best_hdd.get("kapasitas_tb", 8)
            add_item(f"HDD {best_hdd.get('nama', 'Surveillance HDD')} - {hdd_cap}TB", "Storage", hdd_count, "Unit", hdd_price, "A")

        cable_meter = total_cameras * auto_utp_per_camera
        if kabel_utp_qty and kabel_utp_qty > 0:
            cable_meter = kabel_utp_qty

        kabel_power_total_m = kabel_power_qty if kabel_power_qty and kabel_power_qty > 0 else 0
        kabel_coaxial_total_m = kabel_coaxial_qty if kabel_coaxial_qty and kabel_coaxial_qty > 0 else 0
        total_kabel_m = cable_meter + kabel_power_total_m + kabel_coaxial_total_m
        pipa_qty = math.ceil(total_kabel_m / conduit_m_per_unit) if use_pipa else 0

        jasa_base = _get_jasa_harga(project_type)
        jasa_harga = jasa_base if not use_pipa or pipa_qty == 0 else int(jasa_base * conduit_mult)

        add_item("Jasa Instalasi Kamera", "Lokal", total_cameras, "Titik", jasa_harga, "B")
        add_item("Kabel UTP Cat6", "Lokal", cable_meter, "M", utp_price, "B")

        if kabel_coaxial_total_m > 0:
            add_item("Kabel Coaxial RG59", "Lokal", kabel_coaxial_total_m, "M", coaxial_price, "B")
        if kabel_power_total_m > 0:
            add_item("Kabel Power", "Lokal", kabel_power_total_m, "M", power_price, "B")
        if pipa_qty > 0:
            add_item("Conduit", "Lokal", pipa_qty, "Btg", conduit_price, "B")

        dasar_aksesoris = (
            (total_cameras * jasa_harga)
            + (cable_meter * utp_price)
            + (kabel_coaxial_total_m * coaxial_price)
            + (kabel_power_total_m * power_price)
            + (pipa_qty * conduit_price)
        )
        aksesoris_harga = math.ceil(dasar_aksesoris * accessories_pct / 100)
        add_item("Aksesoris Instalasi (RJ45, Sock, Clamp, Flexible, Duct, Ties, Isolasi)", "Lokal", 1, "Lot", aksesoris_harga, "B")

    elif is_wireless:
        wireless_products = await lookup_products_fn(category="wireless_cameras", keyword=resolution)
        best_camera = (wireless_products.get("products") or [None])[0]

        if best_camera:
            camera_price = best_camera.get("harga", 0) or 0
            camera_nama = best_camera.get('nama', 'CCTV')
            camera_res = best_camera.get('resolusi', resolution)
            camera_jenis = best_camera.get('jenis', '')
            if camera_count_indoor > 0:
                add_item(f"Kamera WiFi Indoor {camera_nama} - {camera_res} ({camera_jenis})", "Wireless Camera", camera_count_indoor, "Unit", camera_price, "A")
            if camera_count_outdoor > 0:
                add_item(f"Kamera WiFi Outdoor {camera_nama} - {camera_res} ({camera_jenis})", "Wireless Camera", camera_count_outdoor, "Unit", camera_price, "A")

        if sd_card_size:
            sd_products = await lookup_products_fn(category="sd_cards", keyword=sd_card_size)
            best_sd = (sd_products.get("products") or [None])[0]
            if best_sd:
                sd_price = best_sd.get("harga", 0) or 0
                add_item(f"Micro SD {sd_card_size}", "Storage", total_cameras, "Unit", sd_price, "A")

        kabel_power_total_m = kabel_power_qty if kabel_power_qty and kabel_power_qty > 0 else 0
        pipa_qty = math.ceil(kabel_power_total_m / conduit_m_per_unit) if use_pipa and kabel_power_total_m > 0 else 0

        jasa_base = _get_jasa_harga(project_type)
        jasa_harga = jasa_base if not use_pipa or pipa_qty == 0 else int(jasa_base * conduit_mult)

        add_item("Jasa Instalasi Kamera", "Lokal", total_cameras, "Titik", jasa_harga, "B")
        if kabel_power_total_m > 0:
            add_item("Kabel Power", "Lokal", kabel_power_total_m, "M", power_price, "B")
        if pipa_qty > 0:
            add_item("Conduit", "Lokal", pipa_qty, "Btg", conduit_price, "B")

        dasar_aksesoris = (
            (total_cameras * jasa_harga)
            + (kabel_power_total_m * power_price)
            + (pipa_qty * conduit_price)
        )
        aksesoris_harga = math.ceil(dasar_aksesoris * accessories_pct / 100)
        add_item("Aksesoris Instalasi (RJ45, Sock, Clamp, Flexible, Duct, Ties, Isolasi)", "Lokal", 1, "Lot", aksesoris_harga, "B")

    else:
        # IP SYSTEM
        camera_products = await lookup_products_fn(category="cameras", keyword=resolution, brand=brand or None)
        nvr_products = await lookup_products_fn(category="nvr", brand="Hiview")
        poe_products = await lookup_products_fn(category="poe_switches")
        utp_products = await lookup_products_fn(category="cables", keyword="utp")

        best_camera = (camera_products.get("products") or [None])[0]
        all_nvr_products = nvr_products.get("products") or []
        best_nvr = None
        for p in all_nvr_products:
            ch = p.get("channel", 0)
            if ch == 0 or ch >= total_cameras:
                best_nvr = p
                break
        if not best_nvr and all_nvr_products:
            best_nvr = all_nvr_products[-1]
        best_poe = (poe_products.get("products") or [None])[0]
        best_utp = (utp_products.get("products") or [None])[0]

        if best_camera:
            camera_price = best_camera.get("harga", 0) or 0
            camera_nama = best_camera.get('nama', 'CCTV')
            camera_res = best_camera.get('resolusi', resolution)
            camera_jenis = best_camera.get('jenis', '')
            if camera_count_indoor > 0:
                add_item(f"Kamera Indoor {camera_nama} - {camera_res} ({camera_jenis})", "IP Camera", camera_count_indoor, "Unit", camera_price, "A")
            if camera_count_outdoor > 0:
                add_item(f"Kamera Outdoor {camera_nama} - {camera_res} ({camera_jenis})", "IP Camera", camera_count_outdoor, "Unit", camera_price, "A")

        if best_nvr:
            nvr_price = best_nvr.get("harga", 0) or best_nvr.get("harga_estimasi", 0) or 0
            ch = best_nvr.get("channel", 0)
            add_item(f"NVR {best_nvr.get('nama', '')} - {ch} Channel", "NVR Recorder", 1, "Unit", nvr_price, "A")

        if best_poe:
            poe_price = best_poe.get("harga", 0) or best_poe.get("harga_estimasi", 0) or 0
            add_item(f"PoE Switch {best_poe.get('nama', '')} - {best_poe.get('port', '?')} Port", "Switch", 1, "Unit", poe_price, "A")

        if best_hdd:
            hdd_price = best_hdd.get("harga", 0) or 0
            hdd_cap = best_hdd.get("kapasitas_tb", 8)
            add_item(f"HDD {best_hdd.get('nama', 'Surveillance HDD')} - {hdd_cap}TB", "Storage", hdd_count, "Unit", hdd_price, "A")

        cable_meter = total_cameras * auto_utp_per_camera
        if kabel_utp_qty and kabel_utp_qty > 0:
            cable_meter = kabel_utp_qty

        kabel_power_total_m = kabel_power_qty if kabel_power_qty and kabel_power_qty > 0 else 0
        kabel_coaxial_total_m = kabel_coaxial_qty if kabel_coaxial_qty and kabel_coaxial_qty > 0 else 0
        total_kabel_m = cable_meter + kabel_power_total_m + kabel_coaxial_total_m
        pipa_qty = math.ceil(total_kabel_m / conduit_m_per_unit) if use_pipa else 0

        jasa_base = _get_jasa_harga(project_type)
        jasa_harga = jasa_base if not use_pipa or pipa_qty == 0 else int(jasa_base * conduit_mult)

        add_item("Jasa Instalasi Kamera", "Lokal", total_cameras, "Titik", jasa_harga, "B")
        add_item(f"Kabel UTP Cat6" + (f" {best_utp.get('tipe', '')}" if best_utp else ""), "Lokal", cable_meter, "M", utp_price, "B")

        if kabel_coaxial_total_m > 0:
            add_item("Kabel Coaxial RG59", "Lokal", kabel_coaxial_total_m, "M", coaxial_price, "B")
        if kabel_power_total_m > 0:
            add_item("Kabel Power", "Lokal", kabel_power_total_m, "M", power_price, "B")
        if pipa_qty > 0:
            add_item("Conduit", "Lokal", pipa_qty, "Btg", conduit_price, "B")

        dasar_aksesoris = (
            (total_cameras * jasa_harga)
            + (cable_meter * utp_price)
            + (kabel_coaxial_total_m * coaxial_price)
            + (kabel_power_total_m * power_price)
            + (pipa_qty * conduit_price)
        )
        aksesoris_harga = math.ceil(dasar_aksesoris * accessories_pct / 100)
        add_item("Aksesoris Instalasi (RJ45, Sock, Clamp, Flexible, Duct, Ties, Isolasi)", "Lokal", 1, "Lot", aksesoris_harga, "B")

    total_a = sum(i["total"] for i in kategori_a)
    total_b = sum(i["total"] for i in kategori_b)
    total_bom = total_a + total_b

    bom_data = {"kategori_a": kategori_a, "kategori_b": kategori_b, "total_a": total_a, "total_b": total_b, "grand_total": total_bom}

    today = datetime.date.today()
    bulan_romawi = MONTH_ROMAN[today.month]
    letter_prefix = proposal_cfg.get("letter_number_prefix", "001/SPH/")
    letter_suffix = proposal_cfg.get("letter_number_suffix", "/{YEAR}").replace("{YEAR}", str(today.year))
    letter_number = f"{letter_prefix}{bulan_romawi}{letter_suffix}"

    letter_info = {
        "letter_number": letter_number,
        "date": today.strftime("%d %B %Y"),
        "customer_attention": customer_attention or "Yth. Bapak/Ibu",
        "customer_address": customer_address or "",
        "client_name": client_name,
        "project_type": project_type,
        "camera_count_indoor": camera_count_indoor,
        "camera_count_outdoor": camera_count_outdoor,
        "grand_total": total_bom,
        "_business_name": _business_name,
        "_business_url": _business_url,
        "_contact_wa": contact_cfg.get("whatsapp", ""),
        "_terms": _terms,
        "_bank": bank_cfg,
    }

    user_prompt = f"""Tulis 1 paragraf pengantar teknis untuk surat penawaran:

DATA KLIEN:
- Nama: {client_name}
- Kepada Yth, Bapak/Ibu : {customer_attention or 'Yth. Bapak/Ibu'}
- Proyek: {project_type}
- Kamera: {total_cameras} unit {resolution} ({camera_count_indoor} Indoor + {camera_count_outdoor} Outdoor)
- Recording: {recording_days} hari ({'24 jam/hari Full Recording' if recording_type == 'full' else '12 jam/hari Motion Detection'})
- Brand: {brand or 'Semua brand'}
- Sistem: {'Analog' if is_analog else 'Wireless' if is_wireless else 'IP'}

HASIL KALKULASI:
- Storage/hari: {storage_result['daily_storage_gb']} GB
- Storage/bulan: {storage_result['monthly_storage_gb']} GB
- Rekomendasi HDD: {storage_result['recommended_hdd_tb']} TB
- Bandwidth: {bandwidth_result['total_bandwidth_mbps']} Mbps

Kebutuhan tambahan: (tidak ada)

TUGAS:
- Tulis 1 kalimat pendek (maks 15 kata) sebagai pengantar teknis berdasarkan data di atas
- JANGAN tulis header/kop/nomor/tanggal/perihal/kepada/syarat/penutup
- JANGAN TULIS TABEL ATAU DAFTAR BOM APAPUN"""

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

            content = re.sub(r'\|[^\n]+\|[^\n]*(\n\|[-:| ]+\|)?', '', content)
            content = re.sub(r'\n{3,}', '\n\n', content.strip())

            content = content.strip() + "\n\n<!--BOM-->"

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


async def proposal_generator_chat_tool(
    client_name: str,
    project_type: str,
    camera_count_indoor: int = 2,
    camera_count_outdoor: int = 2,
    resolution: str = "4MP",
    system_type: str = "ip",
    location: str = "",
) -> dict:
    """Simplified proposal generator for chat — returns summary + total."""
    result = await generate_proposal(
        client_name=client_name,
        project_type=project_type,
        location=location,
        camera_count_indoor=camera_count_indoor,
        camera_count_outdoor=camera_count_outdoor,
        resolution=resolution,
        system_type=system_type,
    )
    if result.get("bom_data") and result.get("letter_info"):
        total = result["bom_data"]["grand_total"]
        letter = result["letter_info"]
        return {
            "summary": f"Proposal untuk {client_name} ({project_type}): Total Rp {total:,}".replace(",", "."),
            "grand_total": total,
            "letter_number": letter["letter_number"],
            "camera_count": camera_count_indoor + camera_count_outdoor,
            "storage_tb": result["storage_summary"]["recommended_hdd_tb"],
        }
    return {"error": "Gagal membuat proposal", "detail": result.get("proposal_markdown", "")}


proposal_generator_tool = Tool(
    name="proposal_generator",
    description="Generate a price proposal / surat penawaran for a CCTV project. Call this when user asks to create a proposal, surat penawaran, or price quote.",
    input_schema={
        "type": "object",
        "properties": {
            "client_name": {
                "type": "string",
                "description": "Nama klien / perusahaan",
            },
            "project_type": {
                "type": "string",
                "description": "Tipe proyek: rumah, kantor, gudang, pabrik, sekolah, parkir, toko, gedung, rs",
            },
            "camera_count_indoor": {
                "type": "integer",
                "description": "Jumlah kamera indoor (default 2)",
            },
            "camera_count_outdoor": {
                "type": "integer",
                "description": "Jumlah kamera outdoor (default 2)",
            },
            "resolution": {
                "type": "string",
                "description": "Resolusi kamera: 2MP, 4MP, 8MP (default 4MP)",
            },
            "system_type": {
                "type": "string",
                "description": "Tipe sistem: ip, analog, wireless (default ip)",
            },
            "location": {
                "type": "string",
                "description": "Lokasi proyek (opsional)",
            },
        },
        "required": ["client_name", "project_type"],
    },
    fn=proposal_generator_chat_tool,
)

registry.register(proposal_generator_tool)
