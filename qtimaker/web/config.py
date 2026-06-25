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

# Application paths
BASE_DIR = Path(__file__).parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Max upload size (100MB)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024

