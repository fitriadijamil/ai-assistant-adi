"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { sendChat, ChatMessage, ToolCallResult as ToolCallResultType } from "@/lib/api";
import ToolResultComponent from "@/components/ToolResult";

const INITIAL_MESSAGE: ChatMessage = {
  role: "assistant",
  content:
    "Halo! Saya Adi, AI Assistant CCTV & Security System Pre-Sales Engineering. Ada yang bisa saya bantu?",
};

interface MessageEx extends ChatMessage {
  tool_calls?: ToolCallResultType[];
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<MessageEx[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isLoading) return;

    const userMessage: MessageEx = { role: "user", content: text };
    const updated = [...messages, userMessage];
    setMessages(updated);
    setInput("");
    setIsLoading(true);

    try {
      const data = await sendChat(
        updated.map((m) => ({ role: m.role, content: m.content }))
      );
      const reply: MessageEx = { role: "assistant", content: data.content };
      if (data.tool_calls && data.tool_calls.length > 0) {
        reply.tool_calls = data.tool_calls;
      }
      setMessages((prev) => [...prev, reply]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            err instanceof Error
              ? `Error: ${err.message}`
              : "Maaf, terjadi kesalahan. Silakan coba lagi.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      <header className="text-center py-4 border-b border-base-300 mb-4">
        <h1 className="text-2xl font-bold">AI Assistant Adi</h1>
        <p className="text-sm text-base-content/60">
          CCTV & Security System Pre-Sales Engineering
        </p>
      </header>

      <div className="flex-1 overflow-y-auto space-y-4 px-2">
        {messages.map((msg, i) => (
          <div key={i}>
            <div
              className={`chat ${msg.role === "user" ? "chat-end" : "chat-start"}`}
            >
              <div className="chat-header text-xs mb-1">
                {msg.role === "user" ? "Anda" : "Adi"}
              </div>
              <div
                className={`chat-bubble ${
                  msg.role === "user"
                    ? "chat-bubble-primary"
                    : "chat-bubble-secondary"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
            {msg.tool_calls && msg.tool_calls.length > 0 && (
              <div className="ml-8 space-y-2 mb-4">
                {msg.tool_calls.map((tc, j) => (
                  <ToolResultComponent key={j} tool={tc.tool} result={tc.result} />
                ))}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="chat chat-start">
            <div className="chat-header text-xs mb-1">Adi</div>
            <div className="chat-bubble chat-bubble-secondary">
              <span className="loading loading-dots loading-sm" />
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="join w-full mt-4">
        <input
          className="input input-bordered join-item flex-1"
          placeholder="Tanya tentang CCTV, storage, troubleshooting..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="btn btn-primary join-item"
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="loading loading-spinner loading-sm" />
          ) : (
            "Kirim"
          )}
        </button>
      </form>
    </div>
  );
}
