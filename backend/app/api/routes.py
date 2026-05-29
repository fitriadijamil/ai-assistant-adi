import logging

from fastapi import APIRouter, HTTPException

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
            camera_count=request.camera_count,
            resolution=request.resolution,
            recording_days=request.recording_days,
            requirements_text=request.requirements_text,
            selected_products=request.selected_products,
            brand=request.brand,
        )
        return ProposalResponse(
            proposal_markdown=result["proposal_markdown"],
            storage_summary=result.get("storage_summary"),
            bandwidth_summary=result.get("bandwidth_summary"),
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
