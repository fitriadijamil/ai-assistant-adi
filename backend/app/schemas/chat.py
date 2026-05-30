from typing import Any

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ToolCallResult(BaseModel):
    tool: str
    result: dict[str, Any]


class ChatResponse(BaseModel):
    content: str
    tool_calls: list[ToolCallResult] = []


class ProposalRequest(BaseModel):
    client_name: str
    project_type: str
    location: str = ""
    camera_count: int
    resolution: str = "4MP"
    recording_days: int = 30
    requirements_text: str = ""
    selected_products: list[dict[str, Any]] = []
    brand: str = ""


class ProposalResponse(BaseModel):
    proposal_markdown: str
    storage_summary: dict[str, Any] | None = None
    bandwidth_summary: dict[str, Any] | None = None
    bom_data: dict[str, Any] | None = None
