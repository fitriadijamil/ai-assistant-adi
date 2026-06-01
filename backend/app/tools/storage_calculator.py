from app.tools.registry import Tool, registry

RESOLUTION_BITRATES = {
    # H.265 Medium quality @ 30fps (based on Seagate calculator)
    "2MP": 1_700_000,
    "3MP": 2_550_000,
    "4MP": 3_400_000,
    "5MP": 4_250_000,
    "8MP": 6_800_000,
    "12MP": 10_200_000,
}


async def storage_calculator_fn(
    camera_count: int,
    resolution: str,
    fps: int = 30,
    recording_days: int = 30,
    recording_type: str = "full",
    bitrate: int | None = None,
) -> dict:
    if bitrate is None:
        bitrate = RESOLUTION_BITRATES.get(resolution.upper(), 3_400_000)

    hours_per_day = 24 if recording_type == "full" else 12

    total_bits = camera_count * bitrate * (fps / 30) * hours_per_day * 3600 * recording_days
    total_bytes = total_bits / 8
    total_gb = total_bytes / (1000 ** 3)
    daily_gb = total_gb / recording_days

    return {
        "daily_storage_gb": round(daily_gb, 2),
        "monthly_storage_gb": round(total_gb, 2),
        "recommended_hdd_gb": round(total_gb, 2),
        "recommended_hdd_tb": round(total_gb / 1000, 2),
        "bitrate_used_bps": bitrate,
    }


storage_calculator_tool = Tool(
    name="storage_calculator",
    description="Calculate HDD storage requirements for CCTV cameras (H.265)",
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
            "recording_type": {
                "type": "string",
                "description": "Recording type: 'full' (24h/day) or 'motion' (12h/day)",
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
