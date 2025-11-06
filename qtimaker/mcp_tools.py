# -*- coding: utf-8 -*-
#
# MCP tool wrappers for async use
#

"""
Wrapper functions for MCP tools that can be called from FastAPI async routes.
This bridges the MCP synchronous calls with the async web framework.
"""


async def convert_document(file_path: str) -> str:
    """
    Convert document using Docling MCP.
    
    Returns:
        document_key for the converted document
    """
    # Import the actual MCP tool function
    # Since MCP tools are sync, we just call them directly
    from . import mcp_docling_convert_document_into_docling_document
    
    result = mcp_docling_convert_document_into_docling_document(source=file_path)
    return result.get("document_key", "")


async def export_markdown(document_key: str) -> str:
    """
    Export Docling document to markdown.
    
    Returns:
        Markdown content as string
    """
    from . import mcp_docling_export_docling_document_to_markdown
    
    result = mcp_docling_export_docling_document_to_markdown(document_key=document_key)
    return result.get("markdown", "")

