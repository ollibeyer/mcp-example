"""
Ollama MCP Client
Verbindet den SQLite-MCP-Server mit Ollama und ermöglicht natürlichsprachige DB-Abfragen.
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ollama

MODEL = "qwen2.5:7b-instruct"
SERVER_SCRIPT = str(__file__).replace("client.py", "server.py")
PYTHON = str(__file__).replace("client.py", ".venv/bin/python")


def mcp_tools_to_ollama(mcp_tools) -> list[dict]:
    """Konvertiert MCP-Tool-Definitionen in das Ollama-Tool-Format."""
    ollama_tools = []
    for tool in mcp_tools:
        props = {}
        required = []
        if tool.inputSchema and "properties" in tool.inputSchema:
            for name, schema in tool.inputSchema["properties"].items():
                props[name] = {
                    "type": schema.get("type", "string"),
                    "description": schema.get("description", ""),
                }
            required = tool.inputSchema.get("required", [])

        ollama_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                },
            },
        })
    return ollama_tools


async def run_chat(user_prompt: str):
    server_params = StdioServerParameters(
        command=PYTHON,
        args=[SERVER_SCRIPT],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools
            ollama_tools = mcp_tools_to_ollama(mcp_tools)

            messages = [{"role": "user", "content": user_prompt}]

            print(f"\n🤖 Modell: {MODEL}")
            print(f"❓ Frage: {user_prompt}\n")

            # Agentic loop: Ollama ruft Tools auf, bis eine finale Antwort kommt
            while True:
                response = ollama.chat(
                    model=MODEL,
                    messages=messages,
                    tools=ollama_tools,
                )
                msg = response.message

                if msg.tool_calls:
                    messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
                        {"id": tc.id if hasattr(tc, "id") else f"call_{i}",
                         "type": "function",
                         "function": {"name": tc.function.name, "arguments": tc.function.arguments or {}}}
                        for i, tc in enumerate(msg.tool_calls)
                    ]})

                    for i, tc in enumerate(msg.tool_calls):
                        tool_name = tc.function.name
                        tool_args = tc.function.arguments or {}
                        print(f"🔧 Tool aufgerufen: {tool_name}({tool_args})")

                        result = await session.call_tool(tool_name, tool_args)
                        tool_result = result.content[0].text if result.content else ""

                        messages.append({
                            "role": "tool",
                            "content": tool_result,
                        })
                else:
                    print(f"✅ Antwort:\n{msg.content}")
                    break


def main():
    prompts = [
        "Welche Tabellen gibt es in der Datenbank?",
        "Zeige mir alle Kunden aus Berlin.",
        "Welches Produkt wurde am häufigsten bestellt?",
    ]

    prompt = sys.argv[1] if len(sys.argv) > 1 else prompts[0]
    asyncio.run(run_chat(prompt))


if __name__ == "__main__":
    main()
