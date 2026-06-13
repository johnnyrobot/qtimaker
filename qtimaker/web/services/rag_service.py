# -*- coding: utf-8 -*-
#
# RAG service using Gemini for question generation
#

import google.generativeai as genai
from typing import List, Dict, Any, Optional
from ..config import GEMINI_API_KEY, GEMINI_LLM_MODEL, GEMINI_EMBEDDING_MODEL
from .database.postgres import NeonPostgresService
from .database.neo4j import Neo4jService


class RAGService:
    """
    Hybrid RAG service combining:
    - Vector search in PostgreSQL (Neon) for semantic similarity
    - Graph traversal in Neo4j for concept relationships
    - Gemini for question generation and embeddings
    """
    
    def __init__(self):
        self.genai_client = None
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.genai_client = genai
        
        self.postgres = NeonPostgresService()
        self.neo4j = Neo4jService()
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Gemini embedding model.
        """
        if not self.genai_client:
            raise ValueError("Gemini API key not configured")
        
        embeddings = []
        for text in texts:
            embedding = await self._get_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text using Gemini.
        """
        if not self.genai_client:
            return [0.0] * 768  # Return placeholder if no API key
        
        try:
            # Use Gemini's embedding model
            result = self.genai_client.embed_content(
                model=GEMINI_EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 768
    
    async def extract_questions_from_document(self, document_id: str, 
                                            chunks: List[Dict[str, Any]],
                                            num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        Extract questions from document chunks using Gemini LLM.
        
        Process:
        1. Extract concepts from chunks
        2. Generate questions from chunks using Gemini
        3. Return formatted questions
        
        Note: Database storage (Neon/Neo4j) will be enabled when MCP is configured
        """
        if not self.genai_client:
            raise ValueError("Gemini API key not configured")
        
        print(f"Extracting {num_questions} questions from {len(chunks)} chunks")
        
        # Extract concepts from chunks using Gemini
        concepts = await self._extract_concepts(chunks)
        print(f"Extracted {len(concepts)} concepts")
        
        # Generate questions from chunks
        # Distribute questions across chunks
        questions = []
        questions_per_chunk = max(1, num_questions // len(chunks)) if chunks else 1
        remaining_questions = num_questions
        
        for i, chunk in enumerate(chunks):
            if remaining_questions <= 0:
                break
                
            # For the last chunk, generate all remaining questions
            if i == len(chunks) - 1:
                chunk_questions = await self._generate_questions_from_chunk(
                    chunk, concepts, num_questions=remaining_questions
                )
            else:
                chunk_questions = await self._generate_questions_from_chunk(
                    chunk, concepts, num_questions=questions_per_chunk
                )
            
            questions.extend(chunk_questions)
            remaining_questions -= len(chunk_questions)
            print(f"Generated {len(chunk_questions)} questions from chunk {i+1}/{len(chunks)}")
        
        return questions[:num_questions]  # Ensure we don't exceed requested number
    
    async def _extract_concepts(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract key concepts from document chunks using Gemini.
        """
        if not self.genai_client:
            return []
        
        try:
            # Combine chunks for concept extraction (limit to avoid token limits)
            combined_text = "\n\n".join([c.get("content", "") for c in chunks[:5]])[:3000]
            
            prompt = f"""Extract key educational concepts from this text. Return ONLY a JSON array.

Text:
{combined_text}

Return format (valid JSON only):
[{{"name": "Cell", "description": "Basic unit of life"}}, ...]
"""
            
            model = self.genai_client.GenerativeModel(GEMINI_LLM_MODEL)
            response = model.generate_content(prompt)
            
            # Parse JSON from response
            import json
            import re
            
            # Extract JSON from response
            text = response.text
            # Find JSON array in response
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                concepts = json.loads(match.group())
                return concepts
            
            return []
        except Exception as e:
            print(f"Error extracting concepts: {e}")
            return []
    
    async def _generate_questions_from_chunk(self, chunk: Dict[str, Any],
                                           concepts: List[Dict[str, Any]],
                                           num_questions: int = 2) -> List[Dict[str, Any]]:
        """
        Generate quiz questions from a document chunk using Gemini.
        """
        if not self.genai_client:
            return []
        
        try:
            content = chunk.get("content", "")[:3000]  # Use more content
            related_concepts = [c.get("name", "") for c in concepts[:5]]
            
            prompt = f"""Generate {num_questions} educational multiple-choice quiz questions from this content.

{"Key concepts: " + ", ".join(related_concepts) if related_concepts else ""}

Content:
{content}

Requirements:
- Create exactly {num_questions} questions
- Each question must have 4 answer choices
- Mark which choice is correct (0-3)
- Base questions directly on the content provided
- Include brief explanations

Return ONLY valid JSON (no markdown, no extra text):
{{
  "questions": [
    {{
      "question_text": "Based on the content, what...",
      "question_type": "multiple_choice",
      "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
      "correct_answer": 1,
      "explanation": "The content states that..."
    }}
  ]
}}
"""
            
            model = self.genai_client.GenerativeModel(GEMINI_LLM_MODEL)
            response = model.generate_content(prompt)
            
            # Parse JSON from response
            import json
            import re
            
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*$', '', text)
            
            # Find JSON object in response
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                result = json.loads(match.group())
                questions = result.get('questions', [])
                print(f"Gemini generated {len(questions)} questions")
                return questions
            
            print(f"Could not parse JSON from Gemini response: {text[:200]}")
            return []
        except Exception as e:
            print(f"Error generating questions from chunk: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def search_relevant_content(self, query: str, 
                                    document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant content using hybrid retrieval:
        - Vector search in PostgreSQL
        - Graph traversal in Neo4j for related concepts
        """
        # Generate query embedding
        query_embedding = await self.generate_embeddings([query])[0]
        
        # Vector search in PostgreSQL
        similar_chunks = await self.postgres.search_similar_chunks(query_embedding, limit=5)
        
        # Graph search for related concepts
        # TODO: Extract concepts from query and find related content
        
        return similar_chunks

