# -*- coding: utf-8 -*-
#
# MCP Bridge: Makes MCP tools callable from FastAPI
#
# This module provides a bridge between FastAPI async routes and MCP tools.
# MCP tools are called through subprocess to avoid async/context issues.
#

import subprocess
import json
from typing import Dict, Any
from pathlib import Path


def call_docling_convert(file_path: str) -> str:
    """
    Call Docling MCP to convert a document.
    Returns document_key.
    """
    # For now, this is a placeholder
    # The actual MCP integration requires Cursor's MCP client
    # which isn't available in the FastAPI runtime context
    
    # TODO: Implement via:
    # 1. MCP server HTTP API if available
    # 2. Subprocess call to a script that has MCP access
    # 3. Direct integration when MCP Python client is available
    
    return ""


def call_docling_export(document_key: str) -> str:
    """
    Call Docling MCP to export markdown.
    Returns markdown content.
    """
    # Placeholder for MCP integration
    return ""


# For now, we'll have to use PyPDF2 as a fallback
# The proper MCP integration requires architectural changes
# that are beyond the scope of the FastAPI app itself

