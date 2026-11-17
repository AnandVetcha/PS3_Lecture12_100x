"""Part 2: the same tool on the sheet's side, as an MCP server.  Run: python mcp_server.py
The steps are in README.md."""
import csv, io, socket
from typing import Annotated
import requests
import pandas as pd
from fastmcp import FastMCP

SHEET_URL = 'https://docs.google.com/spreadsheets/d/1nNmMTIbEFn1xzN7S9_QHRyomYBSUc9sK1xab5WqjKOk/edit?gid=0#gid=0'
mcp = FastMCP('ACME')

@mcp.tool
def get_project_list(
    sheet_url: Annotated[str | None, "Optional Google Sheet URL. Omit or pass null to use the ACME projects spreadsheet."] = SHEET_URL,
) -> list[str]:
    """Get the list of current working projects at ACME."""
    if sheet_url is None:
        sheet_url = SHEET_URL
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    worksheet_index = sheet_url.split('gid=')[1].split('#')[0]
    df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={worksheet_index}')
    return df['Project'].unique().tolist()

@mcp.tool
def get_block_list_in_a_project(
    project: Annotated[str, "Project name"],
    sheet_url: Annotated[str | None, "Optional Google Sheet URL. Omit or pass null to use the ACME projects spreadsheet."] = SHEET_URL,
) -> list[str]:
    """Get the list of blocks in a specific project at ACME."""
    if sheet_url is None:
        sheet_url = SHEET_URL
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    worksheet_index = sheet_url.split('gid=')[1].split('#')[0]
    df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={worksheet_index}')
    return df[df['Project'] == project]['Block'].unique().tolist()

@mcp.tool
def get_block_leakage_in_a_project(
    project: Annotated[str, "Project name"],
    block: Annotated[str, "Block name"],
    sheet_url: Annotated[str | None, "Optional Google Sheet URL. Omit or pass null to use the ACME projects spreadsheet."] = SHEET_URL,
) -> float:
    """Get the total leakage power in watts of a specific block in a specific project at ACME."""
    if sheet_url is None:
        sheet_url = SHEET_URL
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    worksheet_index = sheet_url.split('gid=')[1].split('#')[0]
    df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={worksheet_index}')
    return float(df[(df['Project'] == project) & (df['Block'] == block)]['Leakage Power (W)'].sum())

@mcp.tool
def get_block_transistor_width_in_a_project(
    project: Annotated[str, "Project name"],
    block: Annotated[str, "Block name"],
    sheet_url: Annotated[str | None, "Optional Google Sheet URL. Omit or pass null to use the ACME projects spreadsheet."] = SHEET_URL,
) -> float:
    """Get the total transistor width in micrometers of a specific block in a specific project at ACME."""
    if sheet_url is None:
        sheet_url = SHEET_URL
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    worksheet_index = sheet_url.split('gid=')[1].split('#')[0]
    df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={worksheet_index}')
    return float(df[(df['Project'] == project) & (df['Block'] == block)]['Transistor Width (um)'].sum())

@mcp.tool
def get_block_high_leakage_transistor_percentage_usage_in_a_project(
    project: Annotated[str, "Project name"],
    block: Annotated[str, "Block name"],
    sheet_url: Annotated[str | None, "Optional Google Sheet URL. Omit or pass null to use the ACME projects spreadsheet."] = SHEET_URL,
) -> float:
    """Get the width-weighted high leakage transistor percentage usage of a specific block in a specific project at ACME."""
    if sheet_url is None:
        sheet_url = SHEET_URL
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    worksheet_index = sheet_url.split('gid=')[1].split('#')[0]
    df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={worksheet_index}')
    block_df = df[(df['Project'] == project) & (df['Block'] == block)]
    width = pd.to_numeric(block_df['Transistor Width (um)'], errors='coerce')
    high_leaky_transistor_percentage = pd.to_numeric(block_df['High Leakage Transistor%'].astype(str).str.strip().str.rstrip('%'), errors='coerce')
    high_leakage_transistors_percentage = float((width * high_leaky_transistor_percentage).sum()/width.sum())
    return high_leakage_transistors_percentage

# Any app can now reach it at http://localhost:8000/mcp
if __name__ == "__main__":
    if socket.socket().connect_ex(("127.0.0.1", 8000)) == 0:
        raise SystemExit("Port 8000 is already in use, probably by a server you started earlier. "
                         "Stop it with Ctrl+C in its terminal, or run: kill $(lsof -t -i:8000)")
    mcp.run(transport="http", port=8000)
