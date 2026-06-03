import logging

from fastapi import APIRouter, HTTPException

from app.config_loader import load_config
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ProposalRequest,
    ProposalResponse,
    ToolCallResult,
)
from app.services.ai_service import chat_with_tools
from app.tools.proposal_generator import generate_proposal
from app.tools.registry import registry

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        result = await chat_with_tools(messages)

        return ChatResponse(
            content=result["content"],
            tool_calls=[ToolCallResult(**tc) for tc in result["tool_calls"]],
        )
    except Exception as e:
        logger.exception(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/proposals/generate", response_model=ProposalResponse)
async def proposals_generate(request: ProposalRequest):
    try:
        result = await generate_proposal(
            client_name=request.client_name,
            project_type=request.project_type,
            location=request.location,
            camera_count_indoor=request.camera_count_indoor,
            camera_count_outdoor=request.camera_count_outdoor,
            resolution=request.resolution,
            system_type=request.system_type,
            recording_type=request.recording_type,
            recording_days=request.recording_days,
            selected_products=request.selected_products,
            brand=request.brand,
            kabel_utp_qty=request.kabel_utp_qty,
            kabel_power_qty=request.kabel_power_qty,
            kabel_coaxial_qty=request.kabel_coaxial_qty,
            use_pipa=request.use_pipa,
            customer_attention=request.customer_attention,
            customer_address=request.customer_address,
            sd_card_size=request.sd_card_size,
        )
        return ProposalResponse(
            proposal_markdown=result["proposal_markdown"],
            storage_summary=result.get("storage_summary"),
            bandwidth_summary=result.get("bandwidth_summary"),
            bom_data=result.get("bom_data"),
            letter_info=result.get("letter_info"),
        )
    except Exception as e:
        logger.exception(f"Proposal endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tools")
async def list_tools():
    return {
        "tools": [
            {"name": t.name, "description": t.description}
            for t in registry.list_tools()
        ]
    }


@router.post("/tools/storage-calculator")
async def storage_calculator(
    camera_count: int,
    resolution: str,
    fps: int = 30,
    recording_days: int = 30,
):
    tool = registry.get("storage_calculator")
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return await tool.execute(
        camera_count=camera_count,
        resolution=resolution,
        fps=fps,
        recording_days=recording_days,
    )


@router.post("/tools/bandwidth-calculator")
async def bandwidth_calculator(
    camera_count: int,
    bitrate_per_camera: int,
    simultaneous_streams: int = 1,
):
    tool = registry.get("bandwidth_calculator")
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return await tool.execute(
        camera_count=camera_count,
        bitrate_per_camera=bitrate_per_camera,
        simultaneous_streams=simultaneous_streams,
    )


@router.get("/config")
async def get_config():
    return load_config()


@router.post("/debug/nvidia-test")
async def debug_nvidia_test():
    import httpx
    from app.config import settings

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 10,
    }
    url = f"{settings.openrouter_base_url}/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            t0 = __import__("time").time()
            resp = await client.post(url, headers=headers, json=payload)
            elapsed = __import__("time").time() - t0
            return {
                "url": url,
                "model": settings.openrouter_model,
                "status": resp.status_code,
                "elapsed_sec": round(elapsed, 2),
                "response_text": resp.text[:500],
            }
    except Exception as e:
        return {
            "url": url,
            "model": settings.openrouter_model,
            "error": str(e),
        }
