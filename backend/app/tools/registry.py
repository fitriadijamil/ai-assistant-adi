from typing import Any, Callable


class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict,
        fn: Callable[..., Any],
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.fn = fn

    def to_openrouter_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }

    async def execute(self, **kwargs: Any) -> Any:
        return await self.fn(**kwargs)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def to_openrouter_tools(self) -> list[dict]:
        return [t.to_openrouter_tool() for t in self._tools.values()]


registry = ToolRegistry()
