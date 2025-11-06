# -*- coding: utf-8 -*-
#
# Quiz generation routes
#

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import tempfile
from pathlib import Path
from ...qti import QTI
from ...quiz import Quiz
from ...config import Config


router = APIRouter(prefix="/api/quiz", tags=["quiz"])


class Question(BaseModel):
    id: str
    type: str
    text: str
    choices: Optional[List[str]] = None
    correct_answer: Optional[int] = None
    explanation: Optional[str] = None


class QuizGenerationRequest(BaseModel):
    title: str
    description: Optional[str] = None
    questions: List[Question]  # Full question data, not just IDs
    qti_version: str = "1.2"  # Always use 1.2 for Canvas compatibility
    shuffle_answers: bool = False
    show_correct_answers: bool = True


@router.post("/generate")
async def generate_quiz(request: QuizGenerationRequest):
    """
    Generate a QTI quiz from selected questions.
    """
    # Always use QTI 1.2 (most reliable for Canvas)
    request.qti_version = "1.2"
    
    if not request.questions or len(request.questions) == 0:
        raise HTTPException(status_code=400, detail="No questions provided")
    
    print(f"\n{'='*60}")
    print(f"GENERATING QTI QUIZ: {request.title}")
    print(f"Questions: {len(request.questions)}")
    print(f"{'='*60}\n")
    
    # Create quiz text from selected questions
    quiz_text = f"Quiz title: {request.title}\n"
    if request.description:
        quiz_text += f"Quiz description: {request.description}\n"
    
    if request.shuffle_answers:
        quiz_text += "Shuffle answers: true\n"
    else:
        quiz_text += "Shuffle answers: false\n"
        
    if not request.show_correct_answers:
        quiz_text += "Show correct answers: false\n"
    
    quiz_text += "\n"
    
    # Add selected questions from the frontend
    for idx, question in enumerate(request.questions, start=1):
        q_type = question.type
        q_text = question.text
        
        print(f"  Question {idx}: {q_text[:60]}...")
        
        # Add a unique title to each question to prevent duplicate detection
        # when questions have identical content. The title ensures each question
        # is unique even if the question text and choices are identical.
        quiz_text += f"Title: Question {idx} (ID: {question.id})\n"
        
        if q_type in ['multiple_choice', 'true_false']:
            # Multiple choice and True/False format
            quiz_text += f"{idx}. {q_text}\n"
            if question.choices:
                for i, choice in enumerate(question.choices):
                    # Mark correct answer with asterisk
                    prefix = '*' if i == question.correct_answer else ''
                    letter = chr(97 + i)  # a, b, c, d
                    quiz_text += f"{prefix}{letter}) {choice}\n"
        elif q_type == 'short_answer':
            # Short answer format - uses asterisk (*) for answers
            quiz_text += f"{idx}. {q_text}\n"
            quiz_text += f"*   {question.explanation or 'answer'}\n"
        elif q_type == 'essay':
            # Essay format - question followed by underscores
            quiz_text += f"{idx}. {q_text}\n"
            quiz_text += "____\n"
            
        quiz_text += "\n"
    
    print(f"\nGenerated quiz text with {len(request.questions)} questions")
    print(f"Quiz text length: {len(quiz_text)} characters\n")
    
    # Parse and generate QTI
    config = Config()
    config.load()
    
    try:
        quiz = Quiz(quiz_text, config=config)
        qti = QTI(quiz, qti_version=request.qti_version)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            qti_path = Path(tmp.name)
            qti.save(qti_path)
        
        return FileResponse(
            str(qti_path),
            media_type="application/zip",
            filename=f"{request.title.replace(' ', '_')}.zip"
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}\n{error_details}")


@router.get("/questions/bank")
async def get_question_bank(status: Optional[str] = "approved"):
    """
    Get all approved questions for question bank selection.
    """
    # TODO: Query approved questions from database
    return {"questions": []}

