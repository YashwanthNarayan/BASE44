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
        self.model = genai.GenerativeModel('gemini-2.5-flash')  # Updated to current model
    
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
        context: Optional[Dict] = None,
        use_cache: bool = True
    ) -> str:
        """Generate an educational tutor response with step-by-step guidance"""
        
        # Only cache non-contextual responses
        if use_cache and not context:
            cache_key = CacheUtils.get_cache_key(f"tutor_{message[:50]}", subject)
            cached_response = CacheUtils.get_cached_response(cache_key)
            if cached_response:
                return cached_response
        
        # Analyze student's learning pattern from conversation history
        learning_analysis = self._analyze_learning_pattern(context)
        
        # Build conversation context with learning insights
        conversation_context = ""
        if context and context.get('conversation_history'):
            conversation_context = "\n\nPrevious conversation context:\n"
            for i, exchange in enumerate(context['conversation_history'][-3:]):
                conversation_context += f"Student: {exchange.get('user', '')}\n"
                conversation_context += f"Teacher: {exchange.get('assistant', '')}\n\n"
        
        # Determine if this is a direct question asking for an answer or if they need guidance
        question_type = self._classify_question_type(message)
        
        prompt = f"""You are an experienced and patient {subject.value} teacher (not a chatbot) having a one-on-one tutoring session with a student. Your role is to GUIDE learning, not just provide answers.

STUDENT'S QUESTION: "{message}"

LEARNING PATTERN ANALYSIS: {learning_analysis}

{conversation_context}

TEACHING APPROACH:
{self._get_teaching_approach(question_type)}

YOUR RESPONSE MUST:
1. 🎯 **Understand First**: Ask clarifying questions if the problem/concept isn't clear
2. 📚 **Assess Knowledge**: Check what the student already knows about this topic
3. 🔍 **Guide Discovery**: Lead them to discover answers through questions and hints
4. 📝 **Step-by-Step**: Break complex problems into smaller, manageable steps
5. 💡 **Encourage Thinking**: Ask "What do you think happens next?" or "Why might that be?"
6. ✅ **Check Understanding**: Ensure they understand each step before moving forward
7. 🌟 **Build Confidence**: Praise their thinking process and effort
8. 🔗 **Connect Concepts**: Relate to what they've learned before

TEACHING STYLE:
- Use Socratic method (guide through questions)
- Give hints rather than direct answers
- Encourage the student to explain their thinking
- Adapt your language to their level of understanding
- Be patient and supportive
- Celebrate small wins and progress

FORBIDDEN:
- Don't just give the final answer
- Don't solve the entire problem for them
- Don't use overly technical language without explanation
- Don't move too fast without checking understanding

Remember: You're a teacher who wants students to LEARN and UNDERSTAND, not just get the right answer."""
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Only cache responses without context
            if use_cache and not context:
                CacheUtils.cache_response(cache_key, content)
            
            return content
        
        except Exception as e:
            print(f"Error generating tutor response: {e}")
            return f"I'm having a technical issue right now. Let's try again - what {subject.value} concept would you like to explore together?"

    def _analyze_learning_pattern(self, context: Optional[Dict]) -> str:
        """Analyze student's learning pattern from conversation history"""
        if not context or not context.get('conversation_history'):
            return "New student - no learning pattern data available yet."
        
        history = context['conversation_history']
        if len(history) < 2:
            return "Early in conversation - observing learning style."
        
        # Analyze patterns
        patterns = []
        
        # Check if student asks for direct answers vs shows work
        direct_answer_requests = sum(1 for exchange in history 
                                   if any(phrase in exchange.get('user', '').lower() 
                                         for phrase in ['what is', 'give me', 'tell me', 'answer is']))
        
        if direct_answer_requests > len(history) * 0.6:
            patterns.append("tends to seek direct answers rather than understanding process")
        else:
            patterns.append("shows interest in understanding the process")
        
        # Check question complexity
        question_lengths = [len(exchange.get('user', '')) for exchange in history]
        avg_length = sum(question_lengths) / len(question_lengths)
        
        if avg_length > 100:
            patterns.append("asks detailed, thoughtful questions")
        elif avg_length < 30:
            patterns.append("asks brief questions - may need encouragement to elaborate")
        
        # Check if they build on previous responses
        if len(history) > 2:
            last_exchanges = history[-2:]
            if any(ref in last_exchanges[-1].get('user', '').lower() 
                   for ref in ['but', 'however', 'also', 'what about', 'then']):
                patterns.append("builds on previous discussions - good critical thinking")
        
        return f"Learning pattern observed: {', '.join(patterns) if patterns else 'Still observing learning style'}"

    def _classify_question_type(self, message: str) -> str:
        """Classify the type of question the student is asking"""
        message_lower = message.lower()
        
        # Direct answer seeking
        if any(phrase in message_lower for phrase in [
            'what is', 'what are', 'give me', 'tell me', 'answer is', 
            'solve this', 'find the', 'calculate'
        ]):
            return "direct_answer"
        
        # Conceptual understanding
        elif any(phrase in message_lower for phrase in [
            'why', 'how does', 'explain', 'understand', 'concept', 
            'difference between', 'what happens when'
        ]):
            return "conceptual"
        
        # Problem-solving help
        elif any(phrase in message_lower for phrase in [
            'stuck on', 'help with', 'not sure how', 'confused about',
            'having trouble', 'don\'t know'
        ]):
            return "problem_solving"
        
        # Process/method questions
        elif any(phrase in message_lower for phrase in [
            'how to', 'steps', 'method', 'approach', 'way to'
        ]):
            return "process"
        
        else:
            return "general"

    def _get_teaching_approach(self, question_type: str) -> str:
        """Get specific teaching approach based on question type"""
        approaches = {
            "direct_answer": """
            🚫 AVOID giving direct answers. Instead:
            - Ask what they already know about this topic
            - Guide them to think through the problem step by step
            - Use hints and leading questions
            - Example: Instead of "The answer is X", ask "What do you think the first step should be?"
            """,
            
            "conceptual": """
            💡 CONCEPTUAL TEACHING:
            - Use analogies and real-world examples
            - Build from what they already know
            - Ask them to explain their current understanding first
            - Guide them to discover the concept through questions
            """,
            
            "problem_solving": """
            🔧 PROBLEM-SOLVING GUIDANCE:
            - First understand what exactly they're stuck on
            - Break the problem into smaller parts
            - Guide them through each step without solving it for them
            - Ask "What would happen if...?" questions
            """,
            
            "process": """
            📋 PROCESS TEACHING:
            - Break down the method into clear steps
            - Have them explain each step back to you
            - Use examples to illustrate each step
            - Check understanding before moving to next step
            """,
            
            "general": """
            🎯 GENERAL TEACHING:
            - Start by understanding what they need help with
            - Assess their current knowledge level
            - Adapt your approach based on their response
            """
        }
        
        return approaches.get(question_type, approaches["general"])
    
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