# -*- coding: utf-8 -*-
#
# SIMPLIFIED: Docling MCP + Gemini (NO pre-filled content, NO databases)
#

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel
from pathlib import Path
from ..config import UPLOAD_DIR, GEMINI_API_KEY, GEMINI_LLM_MODEL
import google.generativeai as genai
import re
import json

router = APIRouter(prefix="/api/questions", tags=["questions"])


class QuestionGenerationRequest(BaseModel):
    document_id: str
    num_questions: int = 10
    question_types: List[str] = ["multiple_choice"]


@router.post("/generate")
async def generate_questions_with_docling(request: QuestionGenerationRequest):
    """
    Generate questions using Docling MCP to parse PDF + Gemini to generate questions.
    Real-time parsing, no pre-filled content!
    """
    try:
        # Find uploaded file
        doc_dir = UPLOAD_DIR / request.document_id
        if not doc_dir.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        files = list(doc_dir.glob("*"))
        if not files:
            raise HTTPException(status_code=404, detail="No file found")
        
        file_path = str(files[0])
        print(f"\n{'='*60}")
        print(f"GENERATING {request.num_questions} QUESTIONS FROM REAL PDF")
        print(f"File: {Path(file_path).name}")
        print(f"{'='*60}\n")
        
        # STEP 1: Parse PDF with Docling MCP
        print("Step 1: Parsing PDF with Docling MCP...")
        content = await parse_with_docling_mcp(file_path)
        
        if not content or len(content) < 100:
            raise HTTPException(status_code=500, detail="Could not extract content from PDF")
        
        print(f"✓ Docling extracted {len(content)} characters\n")
        
        # STEP 2: Generate questions with Gemini
        print(f"Step 2: Generating {request.num_questions} questions with Gemini AI...")
        
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set in .env file")
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Split into chunks
        chunks = split_text_simple(content, size=3000)
        print(f"Split into {len(chunks)} chunks")
        
        # Generate questions from chunks - ensuring we get the exact number requested
        all_questions = []
        chunks_to_use = min(len(chunks), 10)  # Use up to 10 chunks
        questions_per_chunk = max(2, request.num_questions // chunks_to_use)
        
        # Add a buffer - request more than needed since Gemini might generate fewer
        target_with_buffer = int(request.num_questions * 1.3)  # Request 30% more
        
        for i, chunk in enumerate(chunks[:chunks_to_use]):
            if len(all_questions) >= target_with_buffer:
                break
            
            remaining = target_with_buffer - len(all_questions)
            num_to_gen = min(questions_per_chunk + 1, remaining)  # Request 1 extra per chunk
            
            print(f"  Chunk {i+1}/{chunks_to_use}: Requesting {num_to_gen} questions...")
            chunk_questions = await generate_with_gemini(chunk, num_to_gen)
            all_questions.extend(chunk_questions)
            print(f"    → Got {len(chunk_questions)} questions (total so far: {len(all_questions)})")
        
        # If we still don't have enough, generate more from the last chunk
        if len(all_questions) < request.num_questions and chunks:
            shortage = request.num_questions - len(all_questions)
            print(f"  → Generating {shortage} more questions to reach target...")
            extra_q = await generate_with_gemini(chunks[0], shortage)
            all_questions.extend(extra_q)
            print(f"    → Got {len(extra_q)} more questions (total: {len(all_questions)})")
        
        # Format for frontend
        formatted = []
        for idx, q in enumerate(all_questions[:request.num_questions]):
            formatted.append({
                "id": f"q{idx + 1}",
                "type": q.get("question_type", "multiple_choice"),
                "text": q.get("question_text", ""),
                "choices": q.get("choices", []),
                "correct_answer": q.get("correct_answer", 0),
                "explanation": q.get("explanation", "")
            })
        
        print(f"\n✅ SUCCESS: Generated {len(formatted)} questions from Biology textbook\n")
        
        return JSONResponse({
            "document_id": request.document_id,
            "questions": formatted,
            "total_generated": len(formatted),
            "method": "docling_mcp_gemini",
            "message": f"Generated {len(formatted)} questions from your Biology textbook"
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"\n❌ ERROR:\n{error_details}\n")
        raise HTTPException(status_code=500, detail=str(e))


async def parse_with_docling_mcp(file_path: str) -> str:
    """
    Parse PDF using Docling Python library (NOT PyPDF2).
    Returns the full markdown content extracted from the PDF.
    """
    print(f"  → Parsing with Docling: {Path(file_path).name}")
    
    try:
        from docling.document_converter import DocumentConverter
        
        # Initialize Docling converter
        converter = DocumentConverter()
        print(f"  → Docling converter initialized")
        
        # Convert the document
        print(f"  → Converting PDF to structured format...")
        result = converter.convert(file_path)
        
        # Export to markdown
        print(f"  → Exporting to markdown...")
        markdown_content = result.document.export_to_markdown()
        
        print(f"  → ✓ Extracted {len(markdown_content)} characters from PDF")
        
        return markdown_content
        
    except ImportError as e:
        print(f"  ❌ Docling not installed: {e}")
        print(f"  → Run: pip install docling")
        raise Exception("Docling library not installed. Run: pip install docling")
    except Exception as e:
        print(f"  ❌ Docling parsing error: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Docling failed to parse PDF: {str(e)}")


def split_text_simple(text: str, size: int = 3000) -> List[str]:
    """Split text into manageable chunks."""
    if len(text) <= size:
        return [text]
    
    chunks = []
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    current = ""
    
    for para in paragraphs:
        if len(current) + len(para) + 2 < size:
            current += para + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = para + "\n\n"
    
    if current:
        chunks.append(current.strip())
    
    return chunks if chunks else [text]


async def generate_with_gemini(text: str, num: int) -> List[dict]:
    """Generate questions using Gemini AI - with retry if fewer questions returned."""
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            prompt = f"""You are creating Biology quiz questions from a textbook.

Generate EXACTLY {num} multiple-choice questions based on this textbook content:

---
{text[:3000]}
---

IMPORTANT: You MUST generate {num} questions. Do not generate fewer.

Requirements:
- Create EXACTLY {num} questions (no more, no less)
- Each must have 4 answer choices
- Mark which choice is correct (index 0-3)
- Base all questions directly on the textbook content above
- Include brief explanations citing the text

Return ONLY valid JSON (no markdown, no extra text):
{{
  "questions": [
    {{
      "question_text": "According to the textbook, what...",
      "question_type": "multiple_choice",
      "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
      "correct_answer": 1,
      "explanation": "The text states that..."
    }}
  ]
}}
"""
            
            model = genai.GenerativeModel(GEMINI_LLM_MODEL)
            response = model.generate_content(prompt)
            
            # Parse response
            text_resp = response.text.strip()
            text_resp = re.sub(r'```json\s*', '', text_resp)
            text_resp = re.sub(r'```\s*', '', text_resp)
            
            match = re.search(r'\{.*\}', text_resp, re.DOTALL)
            if match:
                data = json.loads(match.group())
                questions = data.get('questions', [])
                
                # If we got fewer than requested and have retries left, try again
                if len(questions) < num and attempt < max_retries - 1:
                    print(f"    ⚠️ Only got {len(questions)}/{num}, retrying...")
                    continue
                
                return questions
            
            return []
        except Exception as e:
            print(f"    Gemini error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return []
    
    return []


@router.get("")
async def list_questions():
    return {"questions": [], "message": "No persistence - questions generated on demand"}


@router.get("/{question_id}")
async def get_question(question_id: str):
    raise HTTPException(status_code=404, detail="Not implemented")
