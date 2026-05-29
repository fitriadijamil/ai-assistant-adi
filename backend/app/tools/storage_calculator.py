from app.tools.registry import Tool, registry

RESOLUTION_BITRATES = {
    "2MP": 4_000_000,
    "3MP": 6_000_000,
    "4MP": 8_000_000,
    "5MP": 10_000_000,
    "8MP": 16_000_000,
    "12MP": 24_000_000,
}


async def storage_calculator_fn(
    camera_count: int,
    resolution: str,
    fps: int = 30,
    recording_days: int = 30,
    bitrate: int | None = None,
) -> dict:
    if bitrate is None:
        bitrate = RESOLUTION_BITRATES.get(resolution.upper(), 8_000_000)

    daily_bytes = camera_count * bitrate * (fps / 30) * 86400
    daily_gb = daily_bytes / (1024**3)
    monthly_gb = daily_gb * recording_days
    recommended_hdd_gb = monthly_gb * 1.2

    return {
        "daily_storage_gb": round(daily_gb, 2),
        "monthly_storage_gb": round(monthly_gb, 2),
        "recommended_hdd_gb": round(recommended_hdd_gb, 2),
        "recommended_hdd_tb": round(recommended_hdd_gb / 1024, 1),
        "bitrate_used_bps": bitrate,
    }


storage_calculator_tool = Tool(
    name="storage_calculator",
    description="Calculate HDD storage requirements for CCTV cameras based on resolution, frame rate, and recording duration.",
    input_schema={
        "type": "object",
        "properties": {
            "camera_count": {
                "type": "integer",
                "description": "Number of cameras",
            },
            "resolution": {
                "type": "string",
                "description": "Camera resolution (2MP, 4MP, 8MP, etc)",
            },
            "fps": {
                "type": "integer",
                "description": "Frames per second (default 30)",
            },
            "recording_days": {
                "type": "integer",
                "description": "Number of recording days (default 30)",
            },
            "bitrate": {
                "type": "integer",
                "description": "Optional custom bitrate in bps",
            },
        },
        "required": ["camera_count", "resolution"],
    },
    fn=storage_calculator_fn,
)

registry.register(storage_calculator_tool)
