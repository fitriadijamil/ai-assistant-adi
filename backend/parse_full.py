import json, re, sys
sys.path.insert(0, '/tmp/xlvenv/lib/python3.14/site-packages')
import openpyxl

wb = openpyxl.load_workbook('/Users/macbookair/Desktop/MEI_2026_MD_HIVIEW_PRICELIST.xlsx', read_only=True, data_only=True)

def safe_int(v):
    if v is None: return None
    try: return int(float(str(v).replace(',','').strip()))
    except: return None

def clean(v):
    if v is None: return ''
    return str(v).strip()

def get_price(row, idx):
    return safe_int(row[idx]) if idx < len(row) else None

CATALOG_DIR = '/Users/macbookair/Desktop/ai-assistant-adi/backend/app/catalog'

# ============================================================
# PARSE ANALOG CAMERAS (C-SERIES CAM, D-SERIES CAM, H-SERIES CAM)
# ============================================================
analog_cameras = []
series_sheets = [('C-SERIES CAM', 'C'), ('D-SERIES CAM', 'D'), ('H-SERIES CAM', 'H')]

for sheet_name, seri_prefix in series_sheets:
    ws = wb[sheet_name]
    for row in ws.iter_rows(min_row=2, values_only=True):
        seri = clean(row[0]) if len(row) > 0 else ''
        tipe = clean(row[1]) if len(row) > 1 else ''
        lensa = clean(row[2]) if len(row) > 2 else ''
        gambar = clean(row[3]) if len(row) > 3 else ''
        resolusi = clean(row[4]) if len(row) > 4 else ''
        keterangan = clean(row[5]) if len(row) > 5 else ''
        msrp = safe_int(row[6]) if len(row) > 6 else None
        md = safe_int(row[7]) if len(row) > 7 else None
        non_md = safe_int(row[8]) if len(row) > 8 else None
        online = safe_int(row[9]) if len(row) > 9 else None

        if not tipe:
            continue

        entry = {
            "series": seri or f"{seri_prefix}-SERIES",
            "nama": f"Hiview {seri} {tipe}" if seri else f"Hiview {seri_prefix}-Series {tipe}",
            "tipe": tipe,
            "lensa": lensa,
            "resolusi": resolusi or "1080P",
            "keterangan": keterangan,
            "jenis": "Analog Camera",
            "brand": "Hiview",
            "harga_msrp": msrp,
            "harga_md": md,
            "harga_non_md": non_md,
            "harga_online": online,
            "sistem": "analog",
        }
        analog_cameras.append(entry)

print(f"Analog cameras: {len(analog_cameras)}")

with open(f'{CATALOG_DIR}/analog_cameras.json', 'w') as f:
    json.dump(analog_cameras, f, indent=2)

# ============================================================
# PARSE XVR (D-SERIES XVR, H-SERIES XVR)
# ============================================================
xvr_list = []

# D-SERIES XVR: TIPE(0), MODEL(1), CHANNEL(2), GAMBAR(3), KETERANGAN(4), MSRP(5), MD(6), NON MD(7), ONLINE(8)
ws = wb['D- SERIES XVR']
for row in ws.iter_rows(min_row=2, values_only=True):
    tipe = clean(row[0]) if len(row) > 0 else ''
    model = clean(row[1]) if len(row) > 1 else ''
    channel = clean(row[2]) if len(row) > 2 else ''
    gambar = clean(row[3]) if len(row) > 3 else ''
    keterangan = clean(row[4]) if len(row) > 4 else ''
    msrp = safe_int(row[5]) if len(row) > 5 else None
    md = safe_int(row[6]) if len(row) > 6 else None
    non_md = safe_int(row[7]) if len(row) > 7 else None
    online = safe_int(row[8]) if len(row) > 8 else None

    if not model:
        continue

    ch_num = 0
    ch_match = re.search(r'(\d+)\s*CHANNEL', channel, re.IGNORECASE)
    if ch_match:
        ch_num = int(ch_match.group(1))

    entry = {
        "nama": f"Hiview {model}",
        "tipe": model,
        "channel": ch_num,
        "channel_text": channel,
        "keterangan": keterangan,
        "jenis": "XVR (DVR Hybrid)",
        "brand": "Hiview",
        "harga_msrp": msrp,
        "harga_md": md,
        "harga_non_md": non_md,
        "harga_online": online,
        "series": "D-SERIES",
    }
    xvr_list.append(entry)

# H-SERIES XVR: SERI(0), TIPE(1), LENSA(2), GAMBAR(3), KETERANGAN(4), MSRP(5), MD PRICE(6), NON MD PRICE(7), ONLINE PRICE(8)
ws = wb['H-SERIES XVR']
for row in ws.iter_rows(min_row=2, values_only=True):
    seri = clean(row[0]) if len(row) > 0 else ''
    model = clean(row[1]) if len(row) > 1 else ''
    channel = clean(row[2]) if len(row) > 2 else ''
    gambar = clean(row[3]) if len(row) > 3 else ''
    keterangan = clean(row[4]) if len(row) > 4 else ''
    msrp = safe_int(row[5]) if len(row) > 5 else None
    md = safe_int(row[6]) if len(row) > 6 else None
    non_md = safe_int(row[7]) if len(row) > 7 else None
    online = safe_int(row[8]) if len(row) > 8 else None

    if not model:
        continue

    ch_num = 0
    ch_match = re.search(r'(\d+)\s*CHANNEL', channel, re.IGNORECASE)
    if ch_match:
        ch_num = int(ch_match.group(1))

    entry = {
        "nama": f"Hiview {model}",
        "tipe": model,
        "channel": ch_num,
        "channel_text": channel,
        "keterangan": keterangan,
        "jenis": "XVR (DVR Hybrid)",
        "brand": "Hiview",
        "harga_msrp": msrp,
        "harga_md": md,
        "harga_non_md": non_md,
        "harga_online": online,
        "series": seri or "H-SERIES",
    }
    xvr_list.append(entry)

print(f"XVR: {len(xvr_list)}")

with open(f'{CATALOG_DIR}/xvr.json', 'w') as f:
    json.dump(xvr_list, f, indent=2)

# ============================================================
# PARSE NVR (NVR D-SERIES, NVR H- SERIES)
# ============================================================
nvr_list = []

def parse_channel(text):
    ch_match = re.search(r'(\d+)\s*CHANNEL', str(text), re.IGNORECASE)
    return int(ch_match.group(1)) if ch_match else 0

# NVR D-SERIES: SERI(0), TIPE(1), CHANNEL(2), GAMBAR(3), KETERANGAN(4), MSRP(5), MD(6), NON MD(7), ONLINE(8)
ws = wb['NVR D-SERIES']
for row in ws.iter_rows(min_row=2, values_only=True):
    seri = clean(row[0]) if len(row) > 0 else ''
    tipe = clean(row[1]) if len(row) > 1 else ''
    channel = clean(row[2]) if len(row) > 2 else ''
    gambar = clean(row[3]) if len(row) > 3 else ''
    keterangan = clean(row[4]) if len(row) > 4 else ''
    msrp = safe_int(row[5]) if len(row) > 5 else None
    md = safe_int(row[6]) if len(row) > 6 else None
    non_md = safe_int(row[7]) if len(row) > 7 else None
    online = safe_int(row[8]) if len(row) > 8 else None

    if not tipe:
        continue

    entry = {
        "nama": f"Hiview {tipe}",
        "tipe": "NVR",
        "model": tipe,
        "channel": parse_channel(channel),
        "keterangan": keterangan[:200] if keterangan else '',
        "brand": "Hiview",
        "series": "D-SERIES",
        "harga_msrp": msrp,
        "harga_md": md,
        "harga_non_md": non_md,
        "harga_online": online,
    }
    nvr_list.append(entry)

# NVR H- SERIES: SERI(0), TIPE(1), CHANNEL(2), GAMBAR(3), KETERANGAN(4), MSRP(5), MD(6), NON MD(7), ONLINE(8)
ws = wb['NVR H- SERIES']
for row in ws.iter_rows(min_row=2, values_only=True):
    seri = clean(row[0]) if len(row) > 0 else ''
    tipe = clean(row[1]) if len(row) > 1 else ''
    channel = clean(row[2]) if len(row) > 2 else ''
    gambar = clean(row[3]) if len(row) > 3 else ''
    keterangan = clean(row[4]) if len(row) > 4 else ''
    msrp = safe_int(row[5]) if len(row) > 5 else None
    md = safe_int(row[6]) if len(row) > 6 else None
    non_md = safe_int(row[7]) if len(row) > 7 else None
    online = safe_int(row[8]) if len(row) > 8 else None

    if not tipe:
        continue

    entry = {
        "nama": f"Hiview {tipe}",
        "tipe": "NVR",
        "model": tipe,
        "channel": parse_channel(channel),
        "keterangan": keterangan[:200] if keterangan else '',
        "brand": "Hiview",
        "series": "H-SERIES",
        "harga_msrp": msrp,
        "harga_md": md,
        "harga_non_md": non_md,
        "harga_online": online,
    }
    nvr_list.append(entry)

print(f"NVR: {len(nvr_list)}")

with open(f'{CATALOG_DIR}/hiview_nvr.json', 'w') as f:
    json.dump(nvr_list, f, indent=2)

# ============================================================
# PARSE PSU (from AKSESORIS)
# ============================================================
ws = wb['AKSESORIS']
psu_list = []

for row in ws.iter_rows(min_row=2, values_only=True):
    seri = clean(row[0]) if len(row) > 0 else ''
    tipe = clean(row[1]) if len(row) > 1 else ''
    gambar = clean(row[2]) if len(row) > 2 else ''
    keterangan = clean(row[3]) if len(row) > 3 else ''
    msrp = safe_int(row[4]) if len(row) > 4 else None
    md = safe_int(row[5]) if len(row) > 5 else None
    non_md = safe_int(row[6]) if len(row) > 6 else None
    online = safe_int(row[7]) if len(row) > 7 else None

    if not tipe:
        continue

    ch_count = 0
    ch_match = re.search(r'(\d+)\s*CH', seri, re.IGNORECASE)
    if ch_match:
        ch_count = int(ch_match.group(1))

    entry = {
        "nama": f"Hiview {seri} {tipe}" if seri else f"Hiview {tipe}",
        "tipe": tipe,
        "seri": seri,
        "keterangan": keterangan,
        "jenis": "Accessories",
        "brand": "Hiview",
        "channel_count": ch_count,
        "harga_msrp": msrp,
        "harga_md": md,
        "harga_non_md": non_md,
        "harga_online": online,
    }
    psu_list.append(entry)

print(f"PSU/Aksesoris: {len(psu_list)}")

with open(f'{CATALOG_DIR}/psu.json', 'w') as f:
    json.dump(psu_list, f, indent=2)

# ============================================================
# PARSE CABLES (from KABEL — coaxial only)
# ============================================================
ws = wb['KABEL']
cables = []

for row in ws.iter_rows(min_row=2, values_only=True):
    seri = clean(row[0]) if len(row) > 0 else ''
    tipe = clean(row[1]) if len(row) > 1 else ''
    gambar = clean(row[2]) if len(row) > 2 else ''
    keterangan = clean(row[3]) if len(row) > 3 else ''
    msrp = safe_int(row[4]) if len(row) > 4 else None
    md = safe_int(row[5]) if len(row) > 5 else None
    non_md = safe_int(row[6]) if len(row) > 6 else None
    online = safe_int(row[7]) if len(row) > 7 else None

    if not tipe:
        continue

    is_coaxial = 'coaxial' in seri.lower() or 'rg59' in tipe.lower() or 'rg6' in tipe.lower()
    is_utp = 'utp' in seri.lower() or 'cat' in tipe.lower()

    if not (is_coaxial or is_utp):
        continue

    entry = {
        "nama": f"{seri} {tipe}".strip(),
        "tipe": tipe,
        "seri": seri,
        "keterangan": keterangan[:200] if keterangan else '',
        "harga_msrp": msrp,
        "harga_md": md,
        "harga_non_md": non_md,
        "harga_online": online,
    }
    if is_coaxial:
        entry["jenis"] = "Coaxial Cable"
        entry["sistem"] = "analog"
    else:
        entry["jenis"] = "UTP Cable"
        entry["sistem"] = "ip"

    cables.append(entry)

print(f"Cables: {len(cables)}")

with open(f'{CATALOG_DIR}/cables.json', 'w') as f:
    json.dump(cables, f, indent=2)

print("\nDone! All files written.")
