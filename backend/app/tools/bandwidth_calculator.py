from app.tools.registry import Tool, registry


async def bandwidth_calculator_fn(
    camera_count: int,
    bitrate_per_camera: int,
    simultaneous_streams: int = 1,
) -> dict:
    total_bandwidth = camera_count * bitrate_per_camera * simultaneous_streams
    total_mbps = total_bandwidth / 1_000_000

    if total_mbps < 100:
        recommendation = "100Mbps switch sufficient"
    elif total_mbps < 1000:
        recommendation = "1Gbps switch recommended"
    else:
        recommendation = "10Gbps uplink required"

    return {
        "total_bandwidth_mbps": round(total_mbps, 2),
        "total_bandwidth_gbps": round(total_mbps / 1000, 3),
        "recommendation": recommendation,
    }


bandwidth_calculator_tool = Tool(
    name="bandwidth_calculator",
    description="Calculate network bandwidth requirements for CCTV camera streams.",
    input_schema={
        "type": "object",
        "properties": {
            "camera_count": {
                "type": "integer",
                "description": "Number of cameras",
            },
            "bitrate_per_camera": {
                "type": "integer",
                "description": "Bitrate per camera in bps",
            },
            "simultaneous_streams": {
                "type": "integer",
                "description": "Number of simultaneous streams (default 1)",
            },
        },
        "required": ["camera_count", "bitrate_per_camera"],
    },
    fn=bandwidth_calculator_fn,
)

registry.register(bandwidth_calculator_tool)
