import json
import os
from pathlib import Path

CONFIG_PATH = Path(os.path.dirname(__file__)) / "business_config.json"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_catalog_path(filename: str) -> Path:
    return Path(os.path.dirname(__file__)) / "catalog" / filename
