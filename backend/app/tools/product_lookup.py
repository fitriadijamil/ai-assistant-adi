import json
import os
from pathlib import Path

from app.tools.registry import Tool, registry

CATALOG_DIR = Path(os.path.dirname(__file__)).parent / "catalog"

CATALOG_FILES = {
    "cameras": CATALOG_DIR / "cameras.json",
    "nvr": CATALOG_DIR / "nvr.json",
    "poe_switches": CATALOG_DIR / "poe_switches.json",
    "hdd": CATALOG_DIR / "hdd.json",
}

HIVIEW_CATALOG_FILES = {
    "cameras": CATALOG_DIR / "hiview_cameras.json",
    "nvr": CATALOG_DIR / "hiview_nvr.json",
}


def _load_catalog(category: str) -> list[dict]:
    path = CATALOG_FILES.get(category)
    if not path or not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _load_hiview_catalog(category: str) -> list[dict]:
    path = HIVIEW_CATALOG_FILES.get(category)
    if not path or not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


async def lookup_products_fn(
    category: str,
    brand: str | None = None,
    keyword: str | None = None,
) -> dict:
    """Search product catalog by category with optional brand and keyword filters."""
    category = category.lower().replace("-", "_")
    products = _load_catalog(category)

    hiview_products = _load_hiview_catalog(category)

    if not products and not hiview_products:
        return {
            "category": category,
            "count": 0,
            "products": [],
            "note": f"Kategori '{category}' tidak ditemukan. Pilihan: cameras, nvr, poe_switches, hdd",
        }

    products = products + hiview_products

    if brand:
        products = [
            p
            for p in products
            if brand.lower() in p.get("brand", "").lower()
        ]

    if keyword:
        kw = keyword.lower()
        filtered = []
        search_fields = ["nama", "brand", "jenis", "tipe", "resolusi"]
        for p in products:
            for field in search_fields:
                if kw in p.get(field, "").lower():
                    filtered.append(p)
                    break
            else:
                if kw in str(p.get("fitur", [])).lower():
                    filtered.append(p)
        products = filtered

    sanitized = []
    for p in products:
        entry = {}
        for k, v in p.items():
            if k in ("harga_md", "harga_non_md", "harga_online"):
                continue
            if k == "harga_msrp":
                entry["harga"] = v
            elif k == "harga_estimasi":
                entry["harga"] = v
            else:
                entry[k] = v
        sanitized.append(entry)

    return {
        "category": category,
        "count": len(sanitized),
        "products": sanitized,
    }


product_lookup_tool = Tool(
    name="product_lookup",
    description="Cari produk CCTV dari katalog berdasarkan kategori, brand, dan kata kunci. Gunakan tool ini saat user menanyakan rekomendasi produk tertentu.",
    input_schema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Kategori produk. Pilihan: cameras, nvr, poe_switches, hdd. Hasil mencakup harga MSRP (field: harga).",
                "enum": ["cameras", "nvr", "poe_switches", "hdd"],
            },
            "brand": {
                "type": "string",
                "description": "Filter berdasarkan brand. Contoh: Hikvision, Dahua, Uniview, Ezviz, TP-Link, Imou, Hiview, Bardi, Hilook. Boleh dikosongkan.",
            },
            "keyword": {
                "type": "string",
                "description": "Kata kunci pencarian tambahan. Misal: '4MP', 'bullet', 'poe', 'entry level'. Mencocokkan nama, brand, fitur, jenis, dan tipe produk.",
            },
        },
        "required": ["category"],
    },
    fn=lookup_products_fn,
)

registry.register(product_lookup_tool)
