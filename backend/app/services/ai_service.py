import json
import logging

import httpx

from app.config import settings
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.tools.registry import registry

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    pass


class AIError(Exception):
    pass


async def chat_with_tools(messages: list[dict]) -> dict:
    if not settings.openrouter_api_key:
        return {
            "content": "AI Assistant belum dikonfigurasi. Silakan atur OPENROUTER_API_KEY di file .env.",
            "tool_calls": [],
        }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    tools = registry.to_openrouter_tools()

    payload = {
        "model": settings.openrouter_model,
        "messages": full_messages,
        "tools": tools if tools else None,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            msg = choice["message"]

            if msg.get("tool_calls"):
                return await _handle_tool_calls(client, full_messages, msg, headers)

            return {
                "content": msg.get("content") or "",
                "tool_calls": [],
            }

    except httpx.TimeoutException:
        logger.error("OpenRouter request timed out")
        return {
            "content": "Maaf, permintaan ke AI Assistant timeout. Silakan coba lagi.",
            "tool_calls": [],
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter returned {e.response.status_code}: {e.response.text}")
        return {
            "content": f"Maaf, terjadi kesalahan pada layanan AI (HTTP {e.response.status_code}). Silakan coba lagi.",
            "tool_calls": [],
        }
    except Exception as e:
        logger.exception(f"Unexpected error in chat_with_tools: {e}")
        return {
            "content": "Maaf, terjadi kesalahan yang tidak terduga. Silakan coba lagi.",
            "tool_calls": [],
        }


async def _handle_tool_calls(
    client: httpx.AsyncClient,
    full_messages: list[dict],
    msg: dict,
    headers: dict,
) -> dict:
    tool_results = []
    paired_results = []
    for tc in msg["tool_calls"]:
        tool = registry.get(tc["function"]["name"])
        if tool:
            try:
                args = json.loads(tc["function"]["arguments"])
                result = await tool.execute(**args)
            except Exception as e:
                logger.error(f"Tool {tc['function']['name']} failed: {e}")
                result = {"error": str(e)}
            tool_results.append({"tool": tc["function"]["name"], "result": result})
            paired_results.append({"tool_call_id": tc["id"], "tool_name": tc["function"]["name"], "result": result})

    full_messages.append(msg)
    for pr in paired_results:
        full_messages.append({
            "role": "tool",
            "tool_call_id": pr["tool_call_id"],
            "content": json.dumps(pr["result"]),
        })

    payload = {
        "model": settings.openrouter_model,
        "messages": full_messages,
    }

    resp2 = await client.post(
        f"{settings.openrouter_base_url}/chat/completions",
        headers=headers,
        json=payload,
    )
    resp2.raise_for_status()
    data2 = resp2.json()
    final_msg = data2["choices"][0]["message"]

    return {
        "content": final_msg.get("content") or "",
        "tool_calls": tool_results,
    }
