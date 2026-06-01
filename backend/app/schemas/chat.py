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
    camera_count_indoor: int = 0
    camera_count_outdoor: int = 0
    resolution: str = "4MP"
    system_type: str = "ip"
    recording_type: str = "full"
    recording_days: int = 30
    selected_products: list[dict[str, Any]] = []
    brand: str = ""
    kabel_utp_qty: int = 0
    kabel_power_qty: int = 0
    kabel_coaxial_qty: int = 0
    use_pipa: bool = True
    customer_attention: str = ""
    customer_address: str = ""
    sd_card_size: str = ""


class ProposalResponse(BaseModel):
    proposal_markdown: str
    storage_summary: dict[str, Any] | None = None
    bandwidth_summary: dict[str, Any] | None = None
    bom_data: dict[str, Any] | None = None
    letter_info: dict[str, Any] | None = None
