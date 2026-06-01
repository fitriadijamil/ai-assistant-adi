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

export interface LetterInfo {
  letter_number: string;
  date: string;
  customer_attention: string;
  customer_address: string;
  client_name: string;
  project_type: string;
  camera_count_indoor: number;
  camera_count_outdoor: number;
  grand_total: number;
}

export interface ProposalRequest {
  client_name: string;
  project_type: string;
  location: string;
  camera_count_indoor: number;
  camera_count_outdoor: number;
  resolution: string;
  system_type: string;
  recording_type: string;
  recording_days: number;
  selected_products: Record<string, unknown>[];
  brand: string;
  kabel_utp_qty: number;
  kabel_power_qty: number;
  kabel_coaxial_qty: number;
  use_pipa: boolean;
  customer_attention: string;
  customer_address: string;
  sd_card_size: string;
}

export interface BomItem {
  no: number;
  deskripsi: string;
  tipe: string;
  qty: number;
  satuan: string;
  harga: number;
  total: number;
}

export interface BomData {
  kategori_a: BomItem[];
  kategori_b: BomItem[];
  total_a: number;
  total_b: number;
  grand_total: number;
}

export interface ProposalResponse {
  proposal_markdown: string;
  storage_summary: Record<string, unknown> | null;
  bandwidth_summary: Record<string, unknown> | null;
  bom_data: BomData | null;
  letter_info: LetterInfo | null;
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
