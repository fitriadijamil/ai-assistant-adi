import json
import os
from pathlib import Path

from app.tools.registry import Tool, registry
from app.config_loader import load_config, get_catalog_path

config = load_config()
catalog_config = config.get("catalog", {})
CATALOG_FILES = {}
for cat, filename in catalog_config.get("files", {}).items():
    CATALOG_FILES[cat] = get_catalog_path(filename)

HIVIEW_CATALOG_FILES = {}
for cat, filename in catalog_config.get("hiview_files", {}).items():
    HIVIEW_CATALOG_FILES[cat] = get_catalog_path(filename)

SEARCH_FIELDS = catalog_config.get("search_fields", ["nama", "brand"])
PRICE_FIELDS = catalog_config.get("price_fields", {})
HIDDEN_PRICE_FIELDS = catalog_config.get("hidden_price_fields", [])

ALL_CATEGORIES = list(CATEGORY_DISPLAY for CATEGORY_DISPLAY in CATALOG_FILES)


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
    category = category.lower().replace("-", "_")
    products = _load_catalog(category)
    hiview_products = _load_hiview_catalog(category)

    if not products and not hiview_products:
        return {
            "category": category,
            "count": 0,
            "products": [],
            "note": f"Kategori '{category}' tidak ditemukan. Pilihan: {', '.join(ALL_CATEGORIES)}",
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
        for p in products:
            for field in SEARCH_FIELDS:
                val = p.get(field)
                if val is not None and kw in str(val).lower():
                    filtered.append(p)
                    break
            else:
                fitur = p.get("fitur")
                if fitur is not None and kw in str(fitur).lower():
                    filtered.append(p)
        products = filtered

    sanitized = []
    msrp_key = PRICE_FIELDS.get("msrp")
    estimate_key = PRICE_FIELDS.get("estimate")
    for p in products:
        entry = {}
        for k, v in p.items():
            if k in HIDDEN_PRICE_FIELDS:
                continue
            if k == msrp_key:
                entry["harga"] = v
            elif k == estimate_key:
                entry["harga"] = v
            else:
                entry[k] = v
        sanitized.append(entry)

    return {
        "category": category,
        "count": len(sanitized),
        "products": sanitized,
    }


_business_name = config.get("business", {}).get("name", "Bisnis")
_brands = config.get("brands", [])

product_lookup_tool = Tool(
    name="product_lookup",
    description=f"Cari produk {_business_name} dari katalog berdasarkan kategori, brand, dan kata kunci.",
    input_schema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": f"Kategori produk: {', '.join(ALL_CATEGORIES)}. Hasil mencakup harga (field: harga).",
                "enum": ALL_CATEGORIES,
            },
            "brand": {
                "type": "string",
                "description": f"Filter berdasarkan brand. Contoh: {', '.join(_brands[:5])}. Boleh dikosongkan.",
            },
            "keyword": {
                "type": "string",
                "description": "Kata kunci pencarian tambahan. Mencocokkan nama, brand, fitur, jenis, dan tipe produk.",
            },
        },
        "required": ["category"],
    },
    fn=lookup_products_fn,
)

registry.register(product_lookup_tool)
