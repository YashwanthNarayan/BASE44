import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from backend.utils.helpers import CacheUtils
from backend.models.user import Subject, DifficultyLevel, QuestionType

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AIService:
    """Service for AI-powered educational content generation"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_practice_questions(
        self,
        subject: Subject,
        topics: List[str],
        difficulty: DifficultyLevel,
        question_count: int = 5,
        question_types: Optional[List[QuestionType]] = None
    ) -> List[Dict[str, Any]]:
        """Generate practice questions using AI"""
        
        # Create cache key
        cache_key = CacheUtils.get_cache_key(
            f"practice_{subject}_{','.join(topics)}_{difficulty}_{question_count}_{question_types}",
            subject
        )
        
        # Check cache first
        cached_response = CacheUtils.get_cached_response(cache_key)
        if cached_response:
            try:
                import json
                return json.loads(cached_response)
            except:
                pass
        
        # Generate new questions
        types_str = ", ".join(question_types) if question_types else "MCQ, Short Answer, Long Answer, Numerical"
        
        prompt = f"""
        Generate {question_count} {difficulty} level practice questions for {subject} focusing on these topics: {', '.join(topics)}.
        
        Question types to include: {types_str}
        
        For each question, provide:
        1. question_text: The actual question
        2. question_type: Type of question (mcq, short_answer, long_answer, numerical)
        3. options: For MCQ questions, provide 4 options as a list
        4. correct_answer: The correct answer
        5. explanation: Brief explanation of the answer
        6. topic: Which topic this question covers
        
        Return as JSON array format. Ensure questions are appropriate for the difficulty level and educational.
        
        Example format:
        [
            {{
                "question_text": "What is the derivative of x²?",
                "question_type": "short_answer",
                "options": null,
                "correct_answer": "2x",
                "explanation": "Using the power rule, d/dx(x²) = 2x¹ = 2x",
                "topic": "Calculus"
            }}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Clean up the response to extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            # Parse and validate JSON
            import json
            questions = json.loads(content.strip())
            
            # Add IDs and metadata
            for i, question in enumerate(questions):
                question["id"] = f"q_{hash(str(question))}_{i}"
                question["subject"] = subject
                question["difficulty"] = difficulty
            
            # Cache the response
            CacheUtils.cache_response(cache_key, json.dumps(questions))
            
            return questions
        
        except Exception as e:
            print(f"AI generation failed: {e}")
            # Always return fallback questions if AI fails
            return self._generate_fallback_questions(subject, topics, question_count)
    
    async def generate_tutor_response(
        self,
        message: str,
        subject: Subject,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate AI tutor response"""
        
        cache_key = CacheUtils.get_cache_key(message, subject)
        cached_response = CacheUtils.get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        context_str = ""
        if context:
            context_str = f"Previous context: {context.get('learning_insights', [])} "
        
        prompt = f"""
        You are an expert {subject} tutor. A student has asked: "{message}"
        
        {context_str}
        
        Provide a helpful, educational response that:
        1. Directly answers their question
        2. Explains concepts clearly
        3. Gives examples if helpful
        4. Encourages further learning
        5. Is appropriate for their level
        
        Keep the response conversational and engaging, but educational.
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Cache the response
            CacheUtils.cache_response(cache_key, content)
            
            return content
        
        except Exception as e:
            return f"I apologize, but I'm having trouble generating a response right now. Could you please rephrase your question about {subject}?"
    
    async def generate_study_notes(
        self,
        subject: Subject,
        topic: str,
        grade_level: str
    ) -> str:
        """Generate comprehensive study notes"""
        
        cache_key = CacheUtils.get_cache_key(f"notes_{topic}_{grade_level}", subject)
        cached_response = CacheUtils.get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        prompt = f"""
        Create comprehensive study notes for {grade_level} grade students on the topic "{topic}" in {subject}.
        
        Structure the notes with:
        1. Introduction/Overview
        2. Key Concepts (with clear explanations)
        3. Important Formulas/Facts (if applicable)
        4. Examples
        5. Summary/Key Points to Remember
        
        Make the content appropriate for {grade_level} grade level, clear, and easy to understand.
        Use markdown formatting for better readability.
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Cache the response
            CacheUtils.cache_response(cache_key, content)
            
            return content
        
        except Exception as e:
            return f"# Study Notes: {topic}\n\nI apologize, but I'm unable to generate notes at the moment. Please try again later."
    
    def _generate_fallback_questions(
        self,
        subject: Subject,
        topics: List[str],
        question_count: int
    ) -> List[Dict[str, Any]]:
        """Generate simple fallback questions when AI fails"""
        fallback_questions = []
        
        # Better fallback questions based on subject and topics
        sample_questions = {
            "math": {
                "Algebra": "What is the value of x if 2x + 5 = 15?",
                "Geometry": "What is the area of a rectangle with length 5 and width 3?",
                "Trigonometry": "What is the value of sin(30°)?",
                "Calculus": "What is the derivative of x²?"
            },
            "physics": {
                "Mechanics": "What is Newton's first law of motion?",
                "Electricity": "What is Ohm's law?",
                "Waves": "What is the speed of light in vacuum?"
            },
            "chemistry": {
                "Atomic Structure": "What is the atomic number of carbon?",
                "Organic Chemistry": "What is the formula for methane?"
            },
            "biology": {
                "Cell Biology": "What is the powerhouse of the cell?",
                "Genetics": "What does DNA stand for?"
            },
            "english": {
                "Grammar": "What is a noun?",
                "Literature": "Who wrote Romeo and Juliet?"
            }
        }
        
        subject_questions = sample_questions.get(subject, {})
        
        for i in range(min(question_count, 5)):
            topic = topics[i % len(topics)] if topics else subject
            question_text = subject_questions.get(topic, f"What is an important concept in {topic}?")
            
            question = {
                "id": f"fallback_{subject}_{i}",
                "question_text": question_text,
                "question_type": "short_answer",
                "options": None,
                "correct_answer": f"Please study {topic} concepts in detail",
                "explanation": "This is a fallback question. AI service is temporarily unavailable.",
                "topic": topic,
                "subject": subject,
                "difficulty": "medium"
            }
            fallback_questions.append(question)
        
        return fallback_questions

# Global AI service instance
ai_service = AIService()