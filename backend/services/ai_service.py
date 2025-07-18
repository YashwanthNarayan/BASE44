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
    
    async def generate_study_planner_response(
        self,
        message: str,
        context: Optional[Dict] = None,
        student_id: str = None
    ) -> Dict[str, Any]:
        """Generate a response for the study planner bot"""
        
        # Analyze the message to understand study requirements
        message_lower = message.lower()
        
        # Check if message contains study duration and subjects
        duration_info = self._extract_duration_from_message(message)
        subjects_info = self._extract_subjects_from_message(message)
        
        # Determine conversation stage
        if not context:
            context = {"stage": "greeting", "requirements": {}}
        
        stage = context.get("stage", "greeting")
        requirements = context.get("requirements", {})
        
        # Generate appropriate response based on stage
        if stage == "greeting":
            response = """👋 Hello! I'm your Smart Study Planner bot! I'll help you create the perfect study schedule using the Pomodoro Technique.

🎯 **Here's what I can do for you:**
• Create personalized study schedules with 25-minute focus sessions
• Optimize subject ordering for maximum learning efficiency
• Include smart break activities to keep you refreshed
• Generate visual timelines for your study sessions

📝 **To get started, please tell me:**
1. **Total study time** you want (e.g., "2 hours", "90 minutes")
2. **Subjects and time** for each (e.g., "1 hour math, 30 minutes English")
3. **Any preferences** for break activities or timing

**Example:** "I want to study for 2 hours total - 1 hour math and 1 hour physics"

What would you like to study today?"""
            
            return {
                "response": response,
                "needs_input": True,
                "input_type": "requirements",
                "context": {"stage": "collecting_requirements", "requirements": {}},
                "suggested_actions": ["Tell me your study plan", "I need help with scheduling"]
            }
        
        elif stage == "collecting_requirements":
            # Parse the requirements
            if duration_info and subjects_info:
                # We have both duration and subjects
                requirements.update({
                    "total_duration": duration_info,
                    "subjects": subjects_info
                })
                
                # Generate confirmation response
                subjects_text = ", ".join([f"{subj['duration']} minutes {subj['subject']}" for subj in subjects_info])
                
                response = f"""Perfect! I understand you want to study for **{duration_info} minutes total** with these subjects:

📚 **Your Study Plan:**
{subjects_text}

⏱️ **I'll structure this using the Pomodoro Technique:**
• 25-minute focused study sessions
• 5-minute breaks between sessions
• Longer 15-minute breaks after every 4 sessions

🎯 **I'll optimize the order of subjects** for maximum learning efficiency and suggest refreshing break activities.

**Would you like me to generate your personalized study schedule now?**

Type "yes" to create your plan or tell me if you'd like to make any changes!"""
                
                return {
                    "response": response,
                    "needs_input": True,
                    "input_type": "confirmation",
                    "context": {"stage": "confirmation", "requirements": requirements},
                    "suggested_actions": ["Yes, create my plan!", "Let me make changes"]
                }
            
            elif duration_info:
                # We have duration but need subjects
                requirements["total_duration"] = duration_info
                
                response = f"""Great! I see you want to study for **{duration_info} minutes**.

📚 **Now, which subjects would you like to study?**

Please tell me how you'd like to divide your time. For example:
• "30 minutes math, 45 minutes English, 15 minutes history"
• "1 hour physics and 30 minutes chemistry"
• "Equal time for math and science"

What subjects do you want to focus on?"""
                
                return {
                    "response": response,
                    "needs_input": True,
                    "input_type": "subjects",
                    "context": {"stage": "collecting_requirements", "requirements": requirements},
                    "suggested_actions": ["List your subjects", "I need help choosing"]
                }
            
            elif subjects_info:
                # We have subjects but need total duration
                requirements["subjects"] = subjects_info
                total_subject_time = sum(subj["duration"] for subj in subjects_info)
                
                response = f"""Excellent! I see you want to study:
{", ".join([f"{subj['duration']} minutes {subj['subject']}" for subj in subjects_info])}

That's **{total_subject_time} minutes** of study time.

⏱️ **Including Pomodoro breaks, your total session will be about {total_subject_time + (total_subject_time // 25) * 5} minutes.**

Is this the total time you wanted to spend studying, or would you like to adjust anything?"""
                
                return {
                    "response": response,
                    "needs_input": True,
                    "input_type": "duration_confirmation",
                    "context": {"stage": "collecting_requirements", "requirements": requirements},
                    "suggested_actions": ["That's perfect!", "Let me adjust the time"]
                }
            
            else:
                # Need more information
                response = """I'd love to help you create the perfect study schedule! 

📋 **I need a bit more information:**

**Please tell me:**
1. **How long** do you want to study in total? (e.g., "2 hours", "90 minutes")
2. **What subjects** and how much time for each? (e.g., "1 hour math, 30 minutes English")

**Example:** "I want to study for 2 hours - 1 hour math and 1 hour physics"

What's your study goal for today?"""
                
                return {
                    "response": response,
                    "needs_input": True,
                    "input_type": "requirements",
                    "context": {"stage": "collecting_requirements", "requirements": requirements},
                    "suggested_actions": ["Tell me your study plan", "I need help planning"]
                }
        
        elif stage == "confirmation":
            if any(word in message_lower for word in ["yes", "create", "generate", "go", "proceed"]):
                # User confirmed, ready to generate plan
                return {
                    "response": "🎉 **Perfect! Generating your optimized study schedule now...**\n\nI'm creating a personalized Pomodoro plan with the perfect subject ordering and break activities for maximum learning efficiency!\n\n*Please wait while I optimize your schedule...*",
                    "needs_input": False,
                    "input_type": "generate_plan",
                    "context": {"stage": "generating", "requirements": requirements},
                    "suggested_actions": []
                }
            else:
                # User wants to make changes
                return {
                    "response": "No problem! Let's adjust your study plan.\n\n📝 **What would you like to change?**\n• The total study time?\n• The subjects or their durations?\n• Any specific preferences?\n\nJust tell me what you'd like to modify!",
                    "needs_input": True,
                    "input_type": "requirements",
                    "context": {"stage": "collecting_requirements", "requirements": {}},
                    "suggested_actions": ["Change subjects", "Adjust timing", "Start over"]
                }
        
        # Default fallback
        return {
            "response": "I'm here to help you create the perfect study schedule! Tell me what you'd like to study and for how long, and I'll create an optimized Pomodoro plan for you.",
            "needs_input": True,
            "input_type": "requirements",
            "context": {"stage": "collecting_requirements", "requirements": {}},
            "suggested_actions": ["Plan my study session", "Help me choose subjects"]
        }

    def _extract_duration_from_message(self, message: str) -> Optional[int]:
        """Extract total study duration from message"""
        import re
        
        # Look for hour patterns
        hour_pattern = r'(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)'
        hour_match = re.search(hour_pattern, message.lower())
        
        if hour_match:
            hours = float(hour_match.group(1))
            return int(hours * 60)
        
        # Look for minute patterns
        minute_pattern = r'(\d+)\s*(?:minute|min|minutes|mins)'
        minute_match = re.search(minute_pattern, message.lower())
        
        if minute_match:
            return int(minute_match.group(1))
        
        return None

    def _extract_subjects_from_message(self, message: str) -> Optional[List[Dict]]:
        """Extract subjects and their durations from message"""
        import re
        
        subjects = []
        
        # Common subject patterns
        subject_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)\s+(math|mathematics|physics|chemistry|biology|english|history|geography|science)',
            r'(\d+)\s*(?:minute|min|minutes|mins)\s+(math|mathematics|physics|chemistry|biology|english|history|geography|science)',
            r'(math|mathematics|physics|chemistry|biology|english|history|geography|science)\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)',
            r'(math|mathematics|physics|chemistry|biology|english|history|geography|science)\s+(?:for\s+)?(\d+)\s*(?:minute|min|minutes|mins)'
        ]
        
        for pattern in subject_patterns:
            matches = re.findall(pattern, message.lower())
            for match in matches:
                if len(match) == 2:
                    try:
                        if 'hour' in pattern:
                            if match[0].replace('.', '').isdigit():
                                # Duration first, subject second
                                duration = int(float(match[0]) * 60)
                                subject = match[1]
                            else:
                                # Subject first, duration second
                                subject = match[0]
                                duration = int(float(match[1]) * 60)
                        else:
                            if match[0].isdigit():
                                # Duration first, subject second
                                duration = int(match[0])
                                subject = match[1]
                            else:
                                # Subject first, duration second
                                subject = match[0]
                                duration = int(match[1])
                        
                        subjects.append({
                            "subject": subject,
                            "duration": duration
                        })
                    except ValueError:
                        continue
        
        return subjects if subjects else None

    async def generate_pomodoro_study_plan(
        self,
        total_duration: int,
        subjects: List[Dict],
        preferred_start_time: Optional[str] = None,
        break_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate an optimized Pomodoro study plan"""
        
        # Standard Pomodoro timings
        WORK_SESSION_DURATION = 25  # minutes
        SHORT_BREAK_DURATION = 5    # minutes
        LONG_BREAK_DURATION = 15    # minutes
        LONG_BREAK_INTERVAL = 4     # sessions
        
        sessions = []
        study_tips = []
        
        # Calculate total work time and available time
        total_work_time = sum(subj.duration_minutes for subj in subjects)
        
        # Convert Pydantic objects to dictionaries for processing
        subjects_dict = [subj.dict() for subj in subjects]
        
        # Optimize subject ordering using AI
        optimized_subjects = await self._optimize_subject_order(subjects_dict)
        
        # Create Pomodoro sessions
        current_time = preferred_start_time or "09:00"
        session_count = 0
        
        for subject_info in optimized_subjects:
            subject = subject_info["subject"]
            duration = subject_info["duration"]
            
            # Break subject time into 25-minute Pomodoro sessions
            remaining_time = duration
            
            while remaining_time > 0:
                # Create work session
                work_duration = min(WORK_SESSION_DURATION, remaining_time)
                session_count += 1
                
                work_session = {
                    "id": f"work_{session_count}",
                    "session_type": "work",
                    "subject": subject,
                    "duration_minutes": work_duration,
                    "start_time": current_time,
                    "end_time": self._add_minutes_to_time(current_time, work_duration),
                    "description": f"Focus on {subject} - Pomodoro #{session_count}",
                    "break_activity": None
                }
                sessions.append(work_session)
                
                current_time = work_session["end_time"]
                remaining_time -= work_duration
                
                # Add break if not the last session
                if remaining_time > 0 or session_count < sum(subj["duration"] // WORK_SESSION_DURATION + (1 if subj["duration"] % WORK_SESSION_DURATION > 0 else 0) for subj in optimized_subjects):
                    # Determine break type
                    if session_count % LONG_BREAK_INTERVAL == 0:
                        break_duration = LONG_BREAK_DURATION
                        break_activity = self._get_long_break_activity()
                    else:
                        break_duration = SHORT_BREAK_DURATION
                        break_activity = self._get_short_break_activity()
                    
                    break_session = {
                        "id": f"break_{session_count}",
                        "session_type": "break",
                        "subject": None,
                        "duration_minutes": break_duration,
                        "start_time": current_time,
                        "end_time": self._add_minutes_to_time(current_time, break_duration),
                        "description": f"Break time - {break_activity}",
                        "break_activity": break_activity
                    }
                    sessions.append(break_session)
                    
                    current_time = break_session["end_time"]
        
        # Generate study tips
        study_tips = self._generate_study_tips(optimized_subjects)
        
        return {
            "sessions": sessions,
            "tips": study_tips,
            "total_sessions": session_count,
            "estimated_completion": current_time
        }

    async def _optimize_subject_order(self, subjects: List[Dict]) -> List[Dict]:
        """Optimize the order of subjects for maximum learning efficiency"""
        
        # Use AI to determine optimal subject ordering
        prompt = f"""
        As an educational expert, optimize the order of these subjects for maximum learning efficiency:
        
        Subjects: {', '.join([f"{subj['subject']} ({subj['duration_minutes']} minutes)" for subj in subjects])}
        
        Consider these factors:
        1. Cognitive load and mental fatigue
        2. Subject difficulty and complexity
        3. Memory retention and spaced learning
        4. Alternating between different types of thinking (analytical vs creative)
        
        Return the subjects in optimal order with a brief explanation for each ordering choice.
        Focus on maximizing learning outcomes and minimizing mental fatigue.
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            # For now, use a simple heuristic while AI provides guidance
            # Alternate between different types of subjects
            analytical_subjects = ["math", "mathematics", "physics", "chemistry"]
            creative_subjects = ["english", "history", "geography", "biology"]
            
            analytical = [s for s in subjects if s["subject"].lower() in analytical_subjects]
            creative = [s for s in subjects if s["subject"].lower() in creative_subjects]
            
            # Alternate between analytical and creative
            optimized = []
            max_len = max(len(analytical), len(creative))
            
            for i in range(max_len):
                if i < len(analytical):
                    optimized.append(analytical[i])
                if i < len(creative):
                    optimized.append(creative[i])
            
            return optimized
            
        except Exception as e:
            print(f"Error optimizing subject order: {e}")
            return subjects

    def _add_minutes_to_time(self, time_str: str, minutes: int) -> str:
        """Add minutes to a time string (HH:MM format)"""
        from datetime import datetime, timedelta
        
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            new_time = time_obj + timedelta(minutes=minutes)
            return new_time.strftime("%H:%M")
        except:
            return time_str

    def _get_short_break_activity(self) -> str:
        """Get a short break activity suggestion"""
        activities = [
            "Stretch your body",
            "Take deep breaths",
            "Look away from screen",
            "Drink water",
            "Walk around",
            "Do neck exercises",
            "Practice mindfulness"
        ]
        import random
        return random.choice(activities)

    def _get_long_break_activity(self) -> str:
        """Get a long break activity suggestion"""
        activities = [
            "Go for a short walk",
            "Eat a healthy snack",
            "Do light exercises",
            "Listen to music",
            "Chat with a friend",
            "Step outside for fresh air",
            "Do some stretching"
        ]
        import random
        return random.choice(activities)

    def _generate_study_tips(self, subjects: List[Dict]) -> List[str]:
        """Generate personalized study tips"""
        tips = [
            "🎯 Stay focused during each 25-minute session - avoid distractions",
            "💧 Stay hydrated - keep a water bottle nearby",
            "📝 Take notes during study sessions to reinforce learning",
            "🧘 Use break time to relax and recharge your mind",
            "📱 Put your phone in another room during study sessions",
            "🎵 Try instrumental music or nature sounds for focus",
            "✅ Check off completed sessions for motivation",
            "🌟 Reward yourself after completing the full study plan"
        ]
        
        return tips[:4]  # Return top 4 tips

# Global AI service instance
ai_service = AIService()