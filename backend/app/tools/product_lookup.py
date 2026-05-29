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


def _load_catalog(category: str) -> list[dict]:
    path = CATALOG_FILES.get(category)
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

    if not products:
        return {
            "category": category,
            "count": 0,
            "products": [],
            "note": f"Kategori '{category}' tidak ditemukan. Pilihan: cameras, nvr, poe_switches, hdd",
        }

    if brand:
        products = [
            p
            for p in products
            if brand.lower() in p.get("brand", "").lower()
        ]

    if keyword:
        kw = keyword.lower()
        filtered = []
        for p in products:
            if kw in p.get("nama", "").lower():
                filtered.append(p)
                continue
            if kw in p.get("brand", "").lower():
                filtered.append(p)
                continue
            if kw in str(p.get("fitur", [])).lower():
                filtered.append(p)
                continue
            if kw in p.get("jenis", "").lower():
                filtered.append(p)
                continue
            if kw in p.get("tipe", "").lower():
                filtered.append(p)
                continue
        products = filtered

    return {
        "category": category,
        "count": len(products),
        "products": products,
    }


product_lookup_tool = Tool(
    name="product_lookup",
    description="Cari produk CCTV dari katalog berdasarkan kategori, brand, dan kata kunci. Gunakan tool ini saat user menanyakan rekomendasi produk tertentu.",
    input_schema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Kategori produk. Pilihan: cameras, nvr, poe_switches, hdd. Wajib diisi.",
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
