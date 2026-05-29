export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ToolCallResult {
  tool: string;
  result: Record<string, unknown>;
}

export interface SendChatResponse {
  content: string;
  tool_calls: ToolCallResult[];
}

export interface ProposalRequest {
  client_name: string;
  project_type: string;
  location: string;
  camera_count: number;
  resolution: string;
  recording_days: number;
  requirements_text: string;
  selected_products: Record<string, unknown>[];
  brand: string;
}

export interface ProposalResponse {
  proposal_markdown: string;
  storage_summary: Record<string, unknown> | null;
  bandwidth_summary: Record<string, unknown> | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function sendChat(
  messages: ChatMessage[]
): Promise<SendChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json();
}

export async function generateProposal(
  data: ProposalRequest
): Promise<ProposalResponse> {
  const res = await fetch(`${API_BASE}/proposals/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json();
}
