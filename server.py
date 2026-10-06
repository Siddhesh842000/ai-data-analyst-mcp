from mcp.server.fastmcp import FastMCP
import sqlite3
import json
import os

# Initialize the MCP Server
mcp = FastMCP("Data Analyst MCP")

# Absolute path to the database to ensure it works regardless of where it's launched
DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")

@mcp.tool()
def get_database_schema() -> str:
    """Get the schema of all tables in the database. Use this first to understand the data structure."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query sqlite_master to get the CREATE TABLE statements
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema = ""
    for name, sql in tables:
        if name != "sqlite_sequence":  # Skip internal sqlite tables
            schema += f"Table: {name}\nSchema:\n{sql}\n\n"
            
    conn.close()
    return schema

@mcp.tool()
def execute_read_query(query: str) -> str:
    """Execute a read-only SQL SELECT query and return the results as JSON."""
    # Strict security check: Only allow SELECT queries
    if not query.strip().upper().startswith("SELECT"):
        return "Error: Security violation. Only SELECT queries are allowed."
        
    try:
        conn = sqlite3.connect(DB_PATH)
        # Configure connection to return dictionaries instead of tuples
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to a list of dictionaries
        result = [dict(row) for row in rows]
        conn.close()
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error executing query: {str(e)}"

if __name__ == "__main__":
    # Start the MCP server using standard input/output (the default for MCP)
    mcp.run()
