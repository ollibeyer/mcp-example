# MCP Ollama Server

A simple Model Context Protocol (MCP) server that enables natural language database queries by combining Ollama's language models with SQLite database access.

## Overview

This project demonstrates how to build an MCP server that exposes SQLite database operations as tools, which can then be called by an AI language model (Ollama) through an agentic loop. Users can ask natural language questions about their database, and the system will automatically determine which SQL queries to execute and return human-readable results.

## How It Works

The system consists of two main components:

1. **Server** (`server.py`): An MCP server that provides tools for interacting with a SQLite database
2. **Client** (`client.py`): An MCP client that connects to Ollama and uses the server's tools to answer natural language queries

The flow:
1. User asks a natural language question
2. Client sends question to Ollama with available MCP tools
3. Ollama determines which tools to call and generates tool arguments
4. Client executes tools via MCP server
5. Results are fed back to Ollama for response generation
6. Final answer is displayed to the user

## Features

- **MCP Server Tools**:
  - `list_tables()`: Lists all tables in the SQLite database
  - `describe_table(table_name)`: Returns the schema of a specific table
  - `execute_query(sql)`: Executes read-only SQL SELECT statements (write operations are blocked for safety)

- **Natural Language Interface**: Ask questions in German or English about your database

- **Agentic Loop**: The AI model automatically chains tool calls to answer complex questions

- **Safety**: Write operations are blocked; only SELECT queries are allowed

## Requirements

- Python 3.8+
- Ollama (running locally or accessible remotely)
- A local SQLite database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ollibeyer/mcp-example.git
cd mcp-example
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure Ollama is running with the required model:
```bash
ollama pull qwen2.5:7b-instruct
ollama serve
```

## Usage

Run the client with a natural language query:

```bash
python client.py "Welche Tabellen gibt es in der Datenbank?"
```

Or run with a custom query:
```bash
python client.py "Zeige mir alle Kunden aus Berlin."
```

Some example queries:
- "Welche Tabellen gibt es in der Datenbank?" (What tables are in the database?)
- "Zeige mir alle Kunden aus Berlin." (Show me all customers from Berlin.)
- "Welches Produkt wurde am häufigsten bestellt?" (Which product was ordered most frequently?)

## Configuration

Edit the following variables in `client.py` to customize:

- `MODEL`: The Ollama model to use (default: `qwen2.5:7b-instruct`)
- `SERVER_SCRIPT`: Path to the server script
- `PYTHON`: Path to the Python executable in the virtual environment

Edit `server.py` to change:

- `DB_PATH`: Path to your SQLite database (default: `sample.db` in the same directory)

## Database

The project includes a sample SQLite database (`sample.db`) with example tables. You can replace it with your own database or modify the `DB_PATH` in `server.py`.

## Development

To extend this project:

1. Add new tools to `server.py` using the `@mcp.tool()` decorator
2. Optionally customize the tool-to-Ollama conversion in `client.py`
3. Experiment with different Ollama models

## License

This is an example project. Feel free to use, modify, and extend it for your own purposes.

## References

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Ollama](https://ollama.ai/)
- [SQLite](https://www.sqlite.org/)
