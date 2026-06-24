"""
SQLite MCP Server
Stellt Tools bereit, um eine SQLite-Datenbank abzufragen.
"""

import sqlite3
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

DB_PATH = Path(__file__).parent / "sample.db"

mcp = FastMCP("SQLite MCP Server")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def list_tables() -> str:
    """Listet alle Tabellen in der SQLite-Datenbank auf."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return json.dumps([row["name"] for row in rows])


@mcp.tool()
def describe_table(table_name: str) -> str:
    """
    Gibt das Schema einer Tabelle zurück (Spaltenname, Typ, NOT NULL, Default, PK).

    Args:
        table_name: Name der Tabelle
    """
    with get_connection() as conn:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    if not rows:
        return f"Tabelle '{table_name}' nicht gefunden."
    schema = [dict(row) for row in rows]
    return json.dumps(schema, ensure_ascii=False)


@mcp.tool()
def execute_query(sql: str) -> str:
    """
    Führt ein READ-ONLY SQL-Statement (SELECT) aus und gibt die Ergebnisse zurück.
    Schreiboperationen (INSERT, UPDATE, DELETE, DROP, …) werden abgelehnt.

    Args:
        sql: Das auszuführende SELECT-Statement
    """
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        return "Fehler: Nur SELECT-Statements sind erlaubt."

    try:
        with get_connection() as conn:
            rows = conn.execute(sql).fetchall()
        result = [dict(row) for row in rows]
        return json.dumps(result, ensure_ascii=False, default=str)
    except sqlite3.Error as e:
        return f"SQL-Fehler: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
