# -*- coding: utf-8 -*-
#
# Configuration for web interface
#

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_LLM_MODEL = "gemini-2.5-flash-lite"  # LLM for question generation
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"  # Embedding model for vector search

# Neon Database Configuration
NEON_PROJECT_NAME = "Canvas Quiz Maker"

# Neo4j Configuration (via MCP)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# Application paths
BASE_DIR = Path(__file__).parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Max upload size (100MB)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024

