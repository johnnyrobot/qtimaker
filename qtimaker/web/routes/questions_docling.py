# -*- coding: utf-8 -*-
#
# SIMPLIFIED Question generation using Docling MCP + Gemini (NO DATABASES)
#

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
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
async def generate_questions_simple(request: QuestionGenerationRequest):
    """
    SIMPLIFIED: Generate questions using Docling MCP + Gemini directly.
    NO databases, NO complex RAG - just parse and generate.
    """
    try:
        # Find the document file
        doc_dir = UPLOAD_DIR / request.document_id
        if not doc_dir.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        files = list(doc_dir.glob("*"))
        if not files:
            raise HTTPException(status_code=404, detail="No file found")
        
        file_path = str(files[0])
        print(f"Processing: {file_path}")
        
        # STEP 1: Parse with Docling MCP
        from ... import mcp_docling_convert_document_into_docling_document, mcp_docling_export_docling_document_to_markdown
        
        # Convert document
        convert_result = mcp_docling_convert_document_into_docling_document(source=file_path)
        document_key = convert_result.get("document_key")
        
        if not document_key:
            raise HTTPException(status_code=500, detail="Failed to convert document with Docling")
        
        print(f"Docling document key: {document_key}")
        
        # Export to markdown
        markdown_result = mcp_docling_export_docling_document_to_markdown(document_key=document_key)
        content = markdown_result.get("markdown", "")
        
        if not content or len(content) < 100:
            raise HTTPException(status_code=500, detail="Document appears empty")
        
        print(f"Extracted content: {len(content)} characters")
        
        # STEP 2: Split into chunks (simple approach)
        chunks = split_into_chunks(content, chunk_size=2000)
        print(f"Split into {len(chunks)} chunks")
        
        # STEP 3: Generate questions with Gemini
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        all_questions = []
        questions_per_chunk = max(1, request.num_questions // len(chunks))
        
        for i, chunk in enumerate(chunks[:min(len(chunks), 10)]):  # Limit to 10 chunks to avoid timeouts
            if len(all_questions) >= request.num_questions:
                break
            
            remaining = request.num_questions - len(all_questions)
            num_to_generate = min(questions_per_chunk, remaining)
            
            chunk_questions = await generate_questions_from_text(chunk, num_to_generate)
            all_questions.extend(chunk_questions)
            print(f"Chunk {i+1}: Generated {len(chunk_questions)} questions")
        
        # Format for frontend
        formatted_questions = []
        for idx, q in enumerate(all_questions[:request.num_questions]):
            formatted_questions.append({
                "id": f"q{idx + 1}",
                "type": q.get("question_type", "multiple_choice"),
                "text": q.get("question_text", ""),
                "choices": q.get("choices", []),
                "correct_answer": q.get("correct_answer", 0),
                "explanation": q.get("explanation", "")
            })
        
        return JSONResponse({
            "document_id": request.document_id,
            "questions": formatted_questions,
            "total_generated": len(formatted_questions),
            "method": "docling_mcp",
            "message": f"Generated {len(formatted_questions)} questions from textbook content"
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


def split_into_chunks(text: str, chunk_size: int = 2000) -> List[str]:
    """Simple text chunking by paragraphs."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


async def generate_questions_from_text(text: str, num_questions: int) -> List[dict]:
    """Generate questions from text using Gemini."""
    try:
        prompt = f"""You are creating quiz questions for a Biology course.

Generate {num_questions} multiple-choice questions based ONLY on this content:

{text[:2500]}

Requirements:
- Create exactly {num_questions} questions
- Each must have 4 answer choices
- Mark correct answer (0-3)
- Base ONLY on the content above
- Include explanations

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question_text": "According to the text, what...",
      "question_type": "multiple_choice",
      "choices": ["A", "B", "C", "D"],
      "correct_answer": 1,
      "explanation": "The text states..."
    }}
  ]
}}
"""
        
        model = genai.GenerativeModel(GEMINI_LLM_MODEL)
        response = model.generate_content(prompt)
        
        text_response = response.text.strip()
        # Clean markdown formatting
        text_response = re.sub(r'```json\s*', '', text_response)
        text_response = re.sub(r'```\s*$', '', text_response)
        
        # Parse JSON
        match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return result.get('questions', [])
        
        return []
    except Exception as e:
        print(f"Gemini error: {e}")
        return []

