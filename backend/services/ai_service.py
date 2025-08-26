import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
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
        # Try different models based on availability and quotas
        self.models = [
            'gemini-1.5-flash',  # Try the non-deprecated model first 
            'gemini-2.5-flash',  # Fallback to newer model
        ]
        self.current_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the best available model"""
        for model_name in self.models:
            try:
                self.model = genai.GenerativeModel(model_name)
                self.current_model = model_name
                print(f"✅ Initialized AI model: {model_name}")
                break
            except Exception as e:
                print(f"❌ Failed to initialize {model_name}: {e}")
                continue
        
        if not self.current_model:
            print("⚠️ No AI model available, will use fallback questions only")
            self.model = None
    
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
        Generate {question_count} {difficulty} level practice questions for {subject} based SPECIFICALLY on these NCERT curriculum units: {', '.join(topics)}.
        
        IMPORTANT REQUIREMENTS:
        - Each question MUST be directly related to the specific NCERT unit/chapter mentioned in the topics
        - Use concepts, formulas, examples, and terminology from the exact NCERT units provided
        - DO NOT generate generic questions - make them unit-specific
        - If the unit is "Real Numbers", ask about rational/irrational numbers, number line, etc.
        - If the unit is "Quadratic Equations", ask about solving quadratics, discriminant, roots, etc.
        - If the unit is "Nutrition in Plants", ask about photosynthesis, chlorophyll, stomata, etc.
        
        Question types to include: {types_str}
        
        For each question, provide:
        1. question_text: The actual question (MUST be specific to the NCERT unit)
        2. question_type: Type of question (mcq, short_answer, long_answer, numerical)
        3. options: For MCQ questions, provide 4 options as a list
        4. correct_answer: The correct answer
        5. explanation: Brief explanation connecting to the specific NCERT unit concepts
        6. topic: The exact NCERT unit name from the provided topics list
        
        Return as JSON array format. Each question must demonstrate understanding of the specific NCERT unit content.
        
        Example for NCERT unit "Real Numbers":
        [
            {{
                "question_text": "Which of the following is an irrational number?",
                "question_type": "mcq",
                "options": ["0.25", "√2", "3/4", "0.333..."],
                "correct_answer": "√2",
                "explanation": "√2 is irrational because it cannot be expressed as a ratio of two integers. From NCERT Real Numbers unit.",
                "topic": "Real Numbers"
            }}
        ]
        """
        
        try:
            # Check if AI model is available
            if not self.model or not self.current_model:
                print("⚠️ AI model not available, using fallback questions")
                return self._generate_fallback_questions(subject, topics, question_count)
            
            # Try AI generation with retry logic
            for attempt in range(2):  # Try twice with different models if needed
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
                    
                    # Cache the response only if successful
                    CacheUtils.cache_response(cache_key, json.dumps(questions))
                    print(f"✅ Generated {len(questions)} AI questions for {subject} - {', '.join(topics)}")
                    return questions
                
                except Exception as api_error:
                    error_message = str(api_error).lower()
                    
                    # Handle specific API errors
                    if "quota" in error_message or "429" in error_message:
                        print(f"⚠️ API quota exceeded for {self.current_model}, trying next model or fallback")
                        # Try next model if available
                        if attempt == 0 and len(self.models) > 1:
                            next_model = self.models[1] if self.current_model == self.models[0] else self.models[0]
                            try:
                                self.model = genai.GenerativeModel(next_model)
                                self.current_model = next_model
                                print(f"🔄 Switched to model: {next_model}")
                                continue  # Retry with new model
                            except:
                                pass
                        break  # Exit retry loop, use fallback
                    
                    elif "safety" in error_message or "block" in error_message:
                        print(f"⚠️ Content safety filter triggered for {', '.join(topics)}, adjusting prompt")
                        # Could implement prompt adjustment here
                        break
                    
                    elif "network" in error_message or "connection" in error_message:
                        print(f"⚠️ Network error, attempt {attempt + 1}/2")
                        if attempt == 0:
                            import time
                            time.sleep(1)  # Brief delay before retry
                            continue
                    
                    print(f"❌ AI generation error (attempt {attempt + 1}): {api_error}")
                    if attempt == 1:  # Last attempt
                        break
            
            print(f"🔄 AI generation failed, using NCERT-specific fallback questions for {', '.join(topics)}")
            return self._generate_fallback_questions(subject, topics, question_count)
        
        except Exception as e:
            print(f"AI generation failed: {e}")
            # Always return fallback questions if AI fails
            return self._generate_fallback_questions(subject, topics, question_count)
    
    def _generate_fallback_questions(self, subject: str, topics: List[str], question_count: int) -> List[Dict[str, Any]]:
        """Generate high-quality NCERT unit-specific fallback questions when AI service fails"""
        import uuid
        import random
        
        # NCERT unit-specific question banks with real curriculum content
        ncert_question_banks = {
            "math": {
                # Class 10 NCERT Units
                "Real Numbers": [
                    {
                        "question": "Which of the following is an irrational number?",
                        "options": ["0.25", "√2", "3/4", "22/7"],
                        "correct": "√2",
                        "explanation": "√2 cannot be expressed as a ratio of two integers, making it irrational."
                    },
                    {
                        "question": "What is the decimal expansion of a rational number?",
                        "options": ["Always terminating", "Always non-terminating", "Either terminating or non-terminating repeating", "Always infinite"],
                        "correct": "Either terminating or non-terminating repeating",
                        "explanation": "Rational numbers have decimal expansions that either terminate or repeat."
                    },
                    {
                        "question": "Every rational number is a real number. This statement is:",
                        "options": ["True", "False", "Sometimes true", "Cannot be determined"],
                        "correct": "True",
                        "explanation": "All rational numbers are part of the real number system."
                    },
                    {
                        "question": "The number π (pi) is:",
                        "options": ["Rational", "Irrational", "Integer", "Natural"],
                        "correct": "Irrational",
                        "explanation": "π is an irrational number as its decimal expansion is non-terminating and non-repeating."
                    },
                    {
                        "question": "Between any two rational numbers, there are:",
                        "options": ["No rational numbers", "Exactly one rational number", "Infinitely many rational numbers", "Only integers"],
                        "correct": "Infinitely many rational numbers",
                        "explanation": "The rational numbers are dense in the real numbers."
                    },
                    {
                        "question": "The decimal representation of 7/8 is:",
                        "options": ["0.875", "0.777...", "0.625", "0.888..."],
                        "correct": "0.875",
                        "explanation": "7 ÷ 8 = 0.875, which is a terminating decimal."
                    },
                    {
                        "question": "Which of the following is a rational number?",
                        "options": ["√3", "√5", "√16", "√7"],
                        "correct": "√16",
                        "explanation": "√16 = 4, which is a rational number (can be written as 4/1)."
                    },
                    {
                        "question": "The sum of a rational and an irrational number is:",
                        "options": ["Always rational", "Always irrational", "Sometimes rational", "Always an integer"],
                        "correct": "Always irrational",
                        "explanation": "The sum of a rational and irrational number is always irrational."
                    }
                ],
                "Quadratic Equations": [
                    {
                        "question": "What is the discriminant of x² - 4x + 3 = 0?",
                        "options": ["4", "16", "12", "-4"],
                        "correct": "4",
                        "explanation": "Discriminant = b² - 4ac = (-4)² - 4(1)(3) = 16 - 12 = 4"
                    },
                    {
                        "question": "If the discriminant of a quadratic equation is zero, the roots are:",
                        "options": ["Real and distinct", "Real and equal", "Complex", "Imaginary"],
                        "correct": "Real and equal",
                        "explanation": "When discriminant = 0, the quadratic has two equal real roots."
                    },
                    {
                        "question": "The roots of x² - 5x + 6 = 0 are:",
                        "options": ["2, 3", "1, 6", "-2, -3", "5, 6"],
                        "correct": "2, 3",
                        "explanation": "Factoring: (x-2)(x-3) = 0, so x = 2 or x = 3"
                    },
                    {
                        "question": "For the quadratic equation ax² + bx + c = 0, if a > 0 and discriminant > 0:",
                        "options": ["No real roots", "One real root", "Two real and distinct roots", "Two equal roots"],
                        "correct": "Two real and distinct roots",
                        "explanation": "Positive discriminant means two real and distinct roots."
                    },
                    {
                        "question": "The quadratic formula is used to find:",
                        "options": ["The vertex of parabola", "The roots of quadratic equation", "The y-intercept", "The axis of symmetry"],
                        "correct": "The roots of quadratic equation",
                        "explanation": "x = (-b ± √(b²-4ac))/2a gives the roots of ax² + bx + c = 0"
                    },
                    {
                        "question": "If one root of x² - 7x + k = 0 is 3, then k equals:",
                        "options": ["12", "10", "9", "4"],
                        "correct": "12",
                        "explanation": "Substituting x = 3: 9 - 21 + k = 0, so k = 12"
                    },
                    {
                        "question": "The sum of roots of 2x² - 7x + 3 = 0 is:",
                        "options": ["7/2", "-7/2", "3/2", "-3/2"],
                        "correct": "7/2",
                        "explanation": "Sum of roots = -b/a = -(-7)/2 = 7/2"
                    },
                    {
                        "question": "A quadratic equation has roots 2 and -3. The equation is:",
                        "options": ["x² + x - 6 = 0", "x² - x - 6 = 0", "x² + x + 6 = 0", "x² - x + 6 = 0"],
                        "correct": "x² + x - 6 = 0",
                        "explanation": "(x-2)(x+3) = x² + x - 6 = 0"
                    }
                ],
                "Polynomials": [
                    {
                        "question": "What is the degree of the polynomial 3x³ + 2x² - x + 5?",
                        "options": ["1", "2", "3", "5"],
                        "correct": "3",
                        "explanation": "The degree is the highest power of the variable, which is 3."
                    }
                ],
                "Triangles": [
                    {
                        "question": "In triangle ABC, if AB = AC, what type of triangle is it?",
                        "options": ["Scalene", "Isosceles", "Equilateral", "Right-angled"],
                        "correct": "Isosceles",
                        "explanation": "A triangle with two equal sides is called an isosceles triangle."
                    }
                ],
                "Coordinate Geometry": [
                    {
                        "question": "What is the distance between points (0,0) and (3,4)?",
                        "options": ["5", "7", "6", "4"],
                        "correct": "5",
                        "explanation": "Using distance formula: √[(3-0)² + (4-0)²] = √[9+16] = √25 = 5"
                    }
                ],
                "Introduction to Trigonometry": [
                    {
                        "question": "What is the value of sin 30°?",
                        "options": ["1/2", "√3/2", "1", "0"],
                        "correct": "1/2",
                        "explanation": "sin 30° = 1/2 is a fundamental trigonometric value."
                    }
                ]
            },
            "physics": {
                # Class 9 NCERT Units
                "Motion": [
                    {
                        "question": "What is the SI unit of velocity?",
                        "options": ["m/s²", "m/s", "km/h", "m"],
                        "correct": "m/s",
                        "explanation": "Velocity is measured in meters per second (m/s) in SI units."
                    }
                ],
                "Force and Laws of Motion": [
                    {
                        "question": "Newton's second law states that F = ?",
                        "options": ["mv", "ma", "mv²", "m/a"],
                        "correct": "ma",
                        "explanation": "Newton's second law: Force equals mass times acceleration (F = ma)."
                    }
                ],
                "Work and Energy": [
                    {
                        "question": "What is the unit of work?",
                        "options": ["Joule", "Watt", "Newton", "Pascal"],
                        "correct": "Joule",
                        "explanation": "Work is measured in Joules (J) in SI units."
                    }
                ],
                # Class 11 NCERT Units
                "Laws of Motion": [
                    {
                        "question": "According to Newton's first law, an object at rest will:",
                        "options": ["Always remain at rest", "Start moving automatically", "Remain at rest unless acted upon by external force", "Move with constant velocity"],
                        "correct": "Remain at rest unless acted upon by external force",
                        "explanation": "Newton's first law (law of inertia) states objects maintain their state unless external force acts."
                    }
                ],
                "Gravitation": [
                    {
                        "question": "What is the value of acceleration due to gravity on Earth?",
                        "options": ["9.8 m/s²", "10 m/s²", "8.9 m/s²", "9.0 m/s²"],
                        "correct": "9.8 m/s²",
                        "explanation": "The standard value of g (acceleration due to gravity) is 9.8 m/s²."
                    }
                ]
            },
            "chemistry": {
                # Class 9 NCERT Units
                "Matter in Our Surroundings": [
                    {
                        "question": "At what temperature does water boil at standard pressure?",
                        "options": ["50°C", "100°C", "150°C", "200°C"],
                        "correct": "100°C",
                        "explanation": "Water boils at 100°C (373 K) at standard atmospheric pressure."
                    }
                ],
                "Atoms and Molecules": [
                    {
                        "question": "What is Avogadro's number?",
                        "options": ["6.022 × 10²³", "6.022 × 10²²", "6.022 × 10²⁴", "6.022 × 10²¹"],
                        "correct": "6.022 × 10²³",
                        "explanation": "Avogadro's number is 6.022 × 10²³ particles per mole."
                    }
                ],
                # Class 10 NCERT Units
                "Acids, Bases and Salts": [
                    {
                        "question": "What is the pH of pure water?",
                        "options": ["6", "7", "8", "14"],
                        "correct": "7",
                        "explanation": "Pure water has a pH of 7, which is neutral."
                    },
                    {
                        "question": "A solution with pH less than 7 is:",
                        "options": ["Basic", "Acidic", "Neutral", "Alkaline"],
                        "correct": "Acidic",
                        "explanation": "Solutions with pH < 7 are acidic in nature."
                    },
                    {
                        "question": "Which indicator turns red in acidic solution?",
                        "options": ["Blue litmus", "Red litmus", "Phenolphthalein", "Methyl orange"],
                        "correct": "Blue litmus",
                        "explanation": "Blue litmus paper turns red in acidic solutions."
                    },
                    {
                        "question": "The process of neutralization produces:",
                        "options": ["Acid only", "Base only", "Salt and water", "Gas only"],
                        "correct": "Salt and water",
                        "explanation": "Acid + Base → Salt + Water is the neutralization reaction."
                    },
                    {
                        "question": "Hydrochloric acid is secreted by:",
                        "options": ["Liver", "Stomach", "Pancreas", "Kidney"],
                        "correct": "Stomach",
                        "explanation": "HCl is produced by gastric glands in the stomach for digestion."
                    },
                    {
                        "question": "What happens when acid reacts with metal carbonate?",
                        "options": ["Hydrogen gas is evolved", "Oxygen gas is evolved", "Carbon dioxide gas is evolved", "No reaction occurs"],
                        "correct": "Carbon dioxide gas is evolved",
                        "explanation": "Acid + Metal carbonate → Salt + Water + CO₂"
                    },
                    {
                        "question": "Baking soda is chemically known as:",
                        "options": ["Sodium carbonate", "Sodium bicarbonate", "Sodium chloride", "Sodium hydroxide"],
                        "correct": "Sodium bicarbonate",
                        "explanation": "Baking soda is sodium bicarbonate (NaHCO₃)."
                    },
                    {
                        "question": "Which acid is present in vinegar?",
                        "options": ["Citric acid", "Tartaric acid", "Acetic acid", "Lactic acid"],
                        "correct": "Acetic acid",
                        "explanation": "Vinegar contains acetic acid (CH₃COOH)."
                    }
                ],
                "Metals and Non-metals": [
                    {
                        "question": "Which of the following is the most reactive metal?",
                        "options": ["Iron", "Copper", "Sodium", "Gold"],
                        "correct": "Sodium",
                        "explanation": "Sodium is highly reactive and belongs to group 1 of the periodic table."
                    }
                ]
            },
            "biology": {
                # Class 9 NCERT Units
                "The Fundamental Unit of Life": [
                    {
                        "question": "What is the basic unit of life?",
                        "options": ["Tissue", "Cell", "Organ", "Atom"],
                        "correct": "Cell",
                        "explanation": "The cell is the basic structural and functional unit of all living organisms."
                    }
                ],
                "Tissues": [
                    {
                        "question": "Which tissue is responsible for movement in animals?",
                        "options": ["Epithelial", "Connective", "Muscular", "Nervous"],
                        "correct": "Muscular",
                        "explanation": "Muscular tissue contracts and relaxes to produce movement."
                    }
                ],
                # Class 10 NCERT Units
                "Life Processes": [
                    {
                        "question": "What is the process by which plants make their food?",
                        "options": ["Respiration", "Photosynthesis", "Transpiration", "Digestion"],
                        "correct": "Photosynthesis",
                        "explanation": "Photosynthesis is the process where plants convert sunlight, CO₂ and water into glucose."
                    }
                ],
                # Class 7 NCERT Units
                "Nutrition in Plants": [
                    {
                        "question": "Which part of the plant cell contains chlorophyll?",
                        "options": ["Nucleus", "Mitochondria", "Chloroplast", "Vacuole"],
                        "correct": "Chloroplast",
                        "explanation": "Chloroplasts contain chlorophyll, the green pigment essential for photosynthesis."
                    },
                    {
                        "question": "What is the process by which plants make their own food?",
                        "options": ["Respiration", "Photosynthesis", "Transpiration", "Digestion"],
                        "correct": "Photosynthesis",
                        "explanation": "Photosynthesis is the process where plants convert sunlight, CO₂ and water into glucose."
                    },
                    {
                        "question": "Which gas do plants absorb from the atmosphere during photosynthesis?",
                        "options": ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"],
                        "correct": "Carbon dioxide",
                        "explanation": "Plants absorb CO₂ from atmosphere and convert it into glucose during photosynthesis."
                    },
                    {
                        "question": "The tiny pores on leaves through which gas exchange occurs are called:",
                        "options": ["Stomata", "Chloroplasts", "Cells", "Tissues"],
                        "correct": "Stomata",
                        "explanation": "Stomata are tiny pores on leaves that allow gas exchange during photosynthesis."
                    },
                    {
                        "question": "Plants that make their own food are called:",
                        "options": ["Heterotrophs", "Autotrophs", "Parasites", "Saprophytes"],
                        "correct": "Autotrophs",
                        "explanation": "Autotrophs are organisms that can produce their own food through photosynthesis."
                    },
                    {
                        "question": "What do plants release as a by-product of photosynthesis?",
                        "options": ["Carbon dioxide", "Nitrogen", "Oxygen", "Water vapor"],
                        "correct": "Oxygen",
                        "explanation": "Oxygen is released as a by-product when plants convert CO₂ and water into glucose."
                    },
                    {
                        "question": "Which mineral is essential for the formation of chlorophyll?",
                        "options": ["Iron", "Magnesium", "Calcium", "Sodium"],
                        "correct": "Magnesium",
                        "explanation": "Magnesium is the central atom in the chlorophyll molecule."
                    },
                    {
                        "question": "The equation for photosynthesis is:",
                        "options": ["6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂", "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O", "CO₂ + H₂O → CH₄ + O₂", "None of these"],
                        "correct": "6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂",
                        "explanation": "This is the balanced equation for photosynthesis showing reactants and products."
                    }
                ]
            },
            "english": {
                # General literature questions for NCERT chapters
                "The Fun They Had": [
                    {
                        "question": "Who wrote 'The Fun They Had'?",
                        "options": ["Isaac Asimov", "R.K. Narayan", "Ruskin Bond", "Mark Twain"],
                        "correct": "Isaac Asimov",
                        "explanation": "'The Fun They Had' is a science fiction story by Isaac Asimov."
                    }
                ]
            }
        }
        
        # Find matching questions for the specific topics/units
        matched_questions = []
        
        for topic in topics:
            if subject in ncert_question_banks and topic in ncert_question_banks[subject]:
                unit_questions = ncert_question_banks[subject][topic]
                matched_questions.extend(unit_questions)
        
        # If no specific unit matches found, use generic fallback for subject
        if not matched_questions:
            # Use original fallback logic for unrecognized units
            generic_questions = self._get_generic_subject_questions(subject)
            matched_questions.extend(generic_questions)
        
        # Randomly select questions up to question_count
        selected_questions = random.sample(matched_questions, min(question_count, len(matched_questions)))
        
        # Format questions properly
        formatted_questions = []
        for i, q in enumerate(selected_questions):
            question_id = str(uuid.uuid4())[:8]
            formatted_question = {
                "id": question_id,
                "question_text": q["question"],
                "question_type": "mcq",
                "options": q["options"],
                "correct_answer": q["correct"],
                "explanation": q["explanation"],
                "topic": topics[0] if topics else subject,  # Use the first topic
                "subject": subject,
                "difficulty": "medium"
            }
            formatted_questions.append(formatted_question)
        
        return formatted_questions
    def _get_generic_subject_questions(self, subject: str) -> List[Dict[str, str]]:
        """Generate generic subject questions as fallback"""
        question_banks = {
            "math": {
                "algebra": [
                    {
                        "question": "Solve for x: 2x + 5 = 17",
                        "options": ["x = 6", "x = 12", "x = 11", "x = 7"],
                        "correct": "x = 6",
                        "explanation": "Subtract 5 from both sides: 2x = 12, then divide by 2: x = 6"
                    },
                    {
                        "question": "What is the slope of the line y = 3x - 4?",
                        "options": ["3", "-4", "4", "1/3"],
                        "correct": "3",
                        "explanation": "In y = mx + b form, m is the slope. Here m = 3."
                    },
                    {
                        "question": "Factor: x² - 9",
                        "options": ["(x + 3)(x - 3)", "(x + 9)(x - 1)", "(x - 3)²", "Cannot be factored"],
                        "correct": "(x + 3)(x - 3)",
                        "explanation": "This is a difference of squares: a² - b² = (a + b)(a - b)"
                    }
                ],
                "geometry": [
                    {
                        "question": "What is the area of a circle with radius 4?",
                        "options": ["16π", "8π", "4π", "32π"],
                        "correct": "16π",
                        "explanation": "Area = πr². With r = 4, Area = π(4)² = 16π"
                    },
                    {
                        "question": "In a right triangle, if one angle is 30°, what is the third angle?",
                        "options": ["60°", "90°", "45°", "120°"],
                        "correct": "60°",
                        "explanation": "Sum of angles in triangle = 180°. 90° + 30° + ? = 180°, so ? = 60°"
                    }
                ]
            },
            "physics": {
                "mechanics": [
                    {
                        "question": "What is Newton's first law of motion?",
                        "options": ["F = ma", "Objects in motion stay in motion unless acted upon by a force", "For every action there's an equal and opposite reaction", "E = mc²"],
                        "correct": "Objects in motion stay in motion unless acted upon by a force",
                        "explanation": "Newton's first law states that objects at rest stay at rest and objects in motion stay in motion unless acted upon by an unbalanced force."
                    },
                    {
                        "question": "If a car accelerates at 2 m/s² for 5 seconds, what is its change in velocity?",
                        "options": ["10 m/s", "2.5 m/s", "7 m/s", "0.4 m/s"],
                        "correct": "10 m/s",
                        "explanation": "Change in velocity = acceleration × time = 2 m/s² × 5 s = 10 m/s"
                    }
                ],
                "thermodynamics": [
                    {
                        "question": "What happens to the kinetic energy of gas molecules when temperature increases?",
                        "options": ["Increases", "Decreases", "Stays the same", "Becomes zero"],
                        "correct": "Increases",
                        "explanation": "Temperature is a measure of average kinetic energy of molecules. Higher temperature means higher kinetic energy."
                    }
                ]
            },
            "chemistry": {
                "organic": [
                    {
                        "question": "What is the molecular formula for methane?",
                        "options": ["CH₄", "C₂H₆", "CH₃OH", "CO₂"],
                        "correct": "CH₄",
                        "explanation": "Methane is the simplest hydrocarbon with one carbon atom bonded to four hydrogen atoms."
                    }
                ],
                "inorganic": [
                    {
                        "question": "What is the chemical symbol for gold?",
                        "options": ["Go", "Gd", "Au", "Ag"],
                        "correct": "Au",
                        "explanation": "Gold's symbol Au comes from its Latin name 'aurum'."
                    }
                ]
            },
            "biology": {
                "cell": [
                    {
                        "question": "What is the powerhouse of the cell?",
                        "options": ["Nucleus", "Mitochondria", "Ribosome", "Endoplasmic reticulum"],
                        "correct": "Mitochondria",
                        "explanation": "Mitochondria produce ATP (energy) for cellular processes, earning the nickname 'powerhouse of the cell'."
                    }
                ],
                "genetics": [
                    {
                        "question": "What does DNA stand for?",
                        "options": ["Deoxyribonucleic acid", "Deoxyribose nucleic acid", "Dinitrogen nucleic acid", "Dynamic nucleic acid"],
                        "correct": "Deoxyribonucleic acid",
                        "explanation": "DNA stands for Deoxyribonucleic acid, the molecule that carries genetic information."
                    }
                ]
            },
            "english": {
                "grammar": [
                    {
                        "question": "Which sentence is grammatically correct?",
                        "options": ["She don't like pizza", "She doesn't like pizza", "She didn't liked pizza", "She don't likes pizza"],
                        "correct": "She doesn't like pizza",
                        "explanation": "With singular third person subjects like 'she', use 'doesn't' not 'don't'."
                    }
                ],
                "literature": [
                    {
                        "question": "Who wrote 'Romeo and Juliet'?",
                        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
                        "correct": "William Shakespeare",
                        "explanation": "Romeo and Juliet is one of Shakespeare's most famous tragedies, written in the early part of his career."
                    }
                ]
            }
        }
        
        import uuid
        import random
        
        fallback_questions = []
        subject_lower = subject.lower()
        
        # Get subject-specific questions
        subject_bank = question_banks.get(subject_lower, {})
        
        # Use all questions from subject
        relevant_questions = []
        if subject_bank:
            for questions in subject_bank.values():
                relevant_questions.extend(questions)
        
        # Return the relevant questions
        return relevant_questions if relevant_questions else []
    
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
            # Check if the first message already contains requirements
            if duration_info and subjects_info:
                # User provided everything in first message, skip greeting
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
            
            # Otherwise, show greeting
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
        
        # Look for total duration patterns
        total_patterns = [
            r'(?:study|work|plan)\s+for\s+(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)',
            r'(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)\s+(?:total|overall|study|plan)',
            r'(\d+)\s*(?:minute|min|minutes|mins)\s+(?:total|overall|study|plan)',
            r'study\s+for\s+(\d+)\s*(?:minute|min|minutes|mins)',
            r'want\s+to\s+study\s+for\s+(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)',
            r'want\s+to\s+study\s+for\s+(\d+)\s*(?:minute|min|minutes|mins)'
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, message.lower())
            if match:
                duration = float(match.group(1))
                if 'hour' in pattern:
                    return int(duration * 60)
                else:
                    return int(duration)
        
        # Fallback: calculate total from individual subjects if no overall duration found
        subjects = self._extract_subjects_from_message(message)
        if subjects:
            return sum(subj["duration"] for subj in subjects)
        
        return None

    def _extract_subjects_from_message(self, message: str) -> Optional[List[Dict]]:
        """Extract subjects and their durations from message"""
        import re
        
        subjects = []
        
        # Enhanced patterns to handle various formats
        subject_patterns = [
            # "1 hour for math", "30 mins for physics"
            r'(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)\s+for\s+(math|mathematics|physics|chemistry|biology|english|history|geography|science)',
            r'(\d+)\s*(?:minute|min|minutes|mins)\s+for\s+(math|mathematics|physics|chemistry|biology|english|history|geography|science)',
            
            # "1 hour math", "30 mins physics"  
            r'(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)\s+(math|mathematics|physics|chemistry|biology|english|history|geography|science)',
            r'(\d+)\s*(?:minute|min|minutes|mins)\s+(math|mathematics|physics|chemistry|biology|english|history|geography|science)',
            
            # "math for 1 hour", "physics for 30 mins"
            r'(math|mathematics|physics|chemistry|biology|english|history|geography|science)\s+for\s+(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)',
            r'(math|mathematics|physics|chemistry|biology|english|history|geography|science)\s+for\s+(\d+)\s*(?:minute|min|minutes|mins)',
            
            # "math 1 hour", "physics 30 mins"
            r'(math|mathematics|physics|chemistry|biology|english|history|geography|science)\s+(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)',
            r'(math|mathematics|physics|chemistry|biology|english|history|geography|science)\s+(\d+)\s*(?:minute|min|minutes|mins)'
        ]
        
        # Process each pattern
        for pattern in subject_patterns:
            matches = re.findall(pattern, message.lower())
            for match in matches:
                if len(match) == 2:
                    try:
                        # Determine which element is duration and which is subject
                        if match[0].replace('.', '').isdigit():
                            # Duration first, subject second
                            duration_str = match[0]
                            subject = match[1]
                        else:
                            # Subject first, duration second
                            subject = match[0]
                            duration_str = match[1]
                        
                        # Convert duration to minutes
                        if 'hour' in pattern:
                            duration = int(float(duration_str) * 60)
                        else:
                            duration = int(duration_str)
                        
                        # Check if this subject already exists
                        existing_subject = None
                        for s in subjects:
                            if s["subject"] == subject:
                                existing_subject = s
                                break
                        
                        if existing_subject:
                            # Add to existing duration
                            existing_subject["duration"] += duration
                        else:
                            # Add new subject
                            subjects.append({
                                "subject": subject,
                                "duration": duration
                            })
                    except (ValueError, IndexError):
                        continue
        
        # Remove duplicates and clean up
        unique_subjects = []
        seen_subjects = set()
        for subject in subjects:
            if subject["subject"] not in seen_subjects:
                unique_subjects.append(subject)
                seen_subjects.add(subject["subject"])
            else:
                # Add duration to existing subject
                for us in unique_subjects:
                    if us["subject"] == subject["subject"]:
                        us["duration"] += subject["duration"]
                        break
        
        return unique_subjects if unique_subjects else None

    async def generate_pomodoro_study_plan(
        self,
        total_duration: int,
        subjects: List[Dict],
        preferred_start_time: Optional[str] = None,
        break_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate an optimized Pomodoro study plan"""
        from datetime import datetime
        
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
        
        # Create Pomodoro sessions - use current time if no preferred time specified
        if preferred_start_time:
            current_time = preferred_start_time
        else:
            # Use current time
            now = datetime.now()
            current_time = now.strftime("%H:%M")
        
        session_count = 0
        
        for subject_info in optimized_subjects:
            subject = subject_info["subject"]
            duration = subject_info["duration_minutes"]
            
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
                if remaining_time > 0 or session_count < sum(subj["duration_minutes"] // WORK_SESSION_DURATION + (1 if subj["duration_minutes"] % WORK_SESSION_DURATION > 0 else 0) for subj in optimized_subjects):
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

    async def generate_study_notes(
        self,
        subject: str,
        topic: str,
        grade_level: str
    ) -> str:
        """Generate comprehensive study notes for a given subject and topic"""
        
        prompt = f"""
        Generate comprehensive study notes for the following:
        
        Subject: {subject}
        Topic: {topic}
        Grade Level: {grade_level}
        
        Please create detailed, well-structured study notes in clean markdown format that include:
        1. Clear explanations of key concepts
        2. Important definitions and terminology
        3. Examples and illustrations where applicable
        4. Key formulas, equations, or processes (if relevant) - use LaTeX format for math: $inline$ or $$block$$
        5. Important facts and figures
        6. Memory aids or mnemonics
        7. Practice questions or self-assessment points
        8. Summary of main points
        
        FORMATTING REQUIREMENTS:
        - Use proper markdown headers (# ## ###)
        - Use bullet points with - or *
        - Use **bold** for important terms
        - Use *italic* for emphasis
        - Use LaTeX for math: $x^2$ for inline, $$x^2 + y^2 = z^2$$ for block equations
        - Use code blocks with ``` for code or special formatting
        - Use > for important notes or tips
        - Keep paragraphs well-spaced
        - Use numbered lists for steps
        
        Make sure the content is appropriate for {grade_level} grade level.
        Focus on making the content educational, engaging, and easy to understand.
        
        The notes should be comprehensive enough to serve as a complete study resource for this topic.
        Return ONLY the markdown content without any wrapper text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Clean up the content
            content = content.strip()
            
            # Remove any markdown code block wrappers if they exist
            if content.startswith('```markdown'):
                content = content[11:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Ensure we have substantive content
            if len(content) < 100:
                content = f"""# {topic}

## Overview
This is a comprehensive study guide for **{topic}** in {subject} for {grade_level} grade level.

## Key Concepts
- {topic} is an important concept in {subject}
- Understanding the fundamentals is crucial for success
- This topic builds upon previous knowledge in the subject

## Important Points
- Review class materials and textbooks for detailed information
- Practice problems and examples help reinforce learning
- Ask questions if concepts are unclear
- Connect this topic to real-world applications

## Study Tips
- Create visual aids and diagrams
- Form study groups for discussion
- Review regularly for better retention
- Use multiple learning resources

## Summary
**{topic}** is a fundamental concept in {subject} that requires careful study and practice. Focus on understanding the core principles and their applications.

> **Note:** This is a generated study guide. Please supplement with your textbook and class materials for complete understanding."""
            
            return content
            
        except Exception as e:
            print(f"Error generating study notes: {e}")
            # Return a fallback response
            return f"""# {topic}

## Overview
This is a comprehensive study guide for **{topic}** in {subject} for {grade_level} grade level.

## Key Concepts
- {topic} is an important concept in {subject}
- Understanding the fundamentals is crucial for success
- This topic builds upon previous knowledge in the subject

## Important Points
- Review class materials and textbooks for detailed information
- Practice problems and examples help reinforce learning
- Ask questions if concepts are unclear
- Connect this topic to real-world applications

## Study Tips
- Create visual aids and diagrams
- Form study groups for discussion
- Review regularly for better retention
- Use multiple learning resources

## Summary
**{topic}** is a fundamental concept in {subject} that requires careful study and practice. Focus on understanding the core principles and their applications.

> **Note:** This is a generated study guide. Please supplement with your textbook and class materials for complete understanding."""

    async def evaluate_answer_intelligently(
        self,
        question_text: str,
        question_type: str,
        student_answer: str,
        correct_answer: str,
        subject: str = "",
        topic: str = ""
    ) -> Dict[str, Any]:
        """Intelligently evaluate student answers using AI for short and long answers"""
        
        # For MCQ, use exact matching
        if question_type == "mcq":
            is_correct = student_answer.lower().strip() == correct_answer.lower().strip()
            return {
                "is_correct": is_correct,
                "explanation": "Multiple choice answer evaluated by exact matching.",
                "feedback": "Correct!" if is_correct else f"The correct answer is: {correct_answer}",
                "partial_credit": 1.0 if is_correct else 0.0
            }
        
        # For short and long answers, use AI evaluation
        prompt = f"""
        You are an expert teacher evaluating a student's answer. Please analyze the student's response and determine if it demonstrates understanding of the concept.

        Question: {question_text}
        Subject: {subject}
        Topic: {topic}
        
        Correct/Expected Answer: {correct_answer}
        Student's Answer: {student_answer}
        
        Please evaluate the student's answer and provide:
        1. Whether the answer is correct (True/False)
        2. A percentage score (0-100) representing how well the student understood the concept
        3. Constructive feedback explaining what was correct or incorrect
        4. If partially correct, explain what parts were right and what needs improvement
        
        Evaluation Criteria:
        - Focus on conceptual understanding rather than exact wording
        - Consider key concepts, main ideas, and critical details
        - Be fair but thorough in your assessment
        - For mathematical answers, check if the approach and final answer are correct
        - For written answers, evaluate if core concepts are demonstrated
        
        Respond in this exact JSON format:
        {{
            "is_correct": true/false,
            "score_percentage": 0-100,
            "feedback": "Detailed feedback for the student",
            "key_concepts_identified": ["concept1", "concept2"],
            "areas_for_improvement": ["area1", "area2"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                evaluation = json.loads(json_str)
                
                return {
                    "is_correct": evaluation.get("is_correct", False),
                    "explanation": evaluation.get("feedback", "Answer evaluated by AI"),
                    "feedback": evaluation.get("feedback", "Good effort!"),
                    "partial_credit": evaluation.get("score_percentage", 0) / 100.0,
                    "score_percentage": evaluation.get("score_percentage", 0),
                    "key_concepts_identified": evaluation.get("key_concepts_identified", []),
                    "areas_for_improvement": evaluation.get("areas_for_improvement", [])
                }
            else:
                # Fallback if JSON parsing fails
                return self._fallback_answer_evaluation(student_answer, correct_answer)
                
        except Exception as e:
            print(f"Error in AI answer evaluation: {e}")
            return self._fallback_answer_evaluation(student_answer, correct_answer)
    
    def _fallback_answer_evaluation(self, student_answer: str, correct_answer: str) -> Dict[str, Any]:
        """Fallback evaluation when AI fails"""
        student_lower = student_answer.lower().strip()
        correct_lower = correct_answer.lower().strip()
        
        # Simple similarity check
        if student_lower == correct_lower:
            return {
                "is_correct": True,
                "explanation": "Answer matches expected response.",
                "feedback": "Correct!",
                "partial_credit": 1.0,
                "score_percentage": 100
            }
        elif len(student_lower) > 0 and correct_lower in student_lower:
            return {
                "is_correct": True,
                "explanation": "Answer contains key concepts.",
                "feedback": "Good! Your answer includes the main concepts.",
                "partial_credit": 0.8,
                "score_percentage": 80
            }
        elif len(student_lower) > 0:
            return {
                "is_correct": False,
                "explanation": "Answer does not match expected response.",
                "feedback": f"Not quite right. The expected answer is: {correct_answer}",
                "partial_credit": 0.2,
                "score_percentage": 20
            }
        else:
            return {
                "is_correct": False,
                "explanation": "No answer provided.",
                "feedback": "Please provide an answer.",
                "partial_credit": 0.0,
                "score_percentage": 0
            }

    async def generate_smart_schedule_recommendation(
        self,
        subject: str,
        topics: List[str],
        score: float,
        difficulty: str,
        student_id: str
    ) -> Dict[str, Any]:
        """Generate intelligent scheduling recommendation based on performance"""
        
        # Determine base scheduling using spaced repetition principles
        now = datetime.utcnow()
        
        # Smart scheduling algorithm based on score
        if score >= 90:
            # Mastery level - longer interval
            days_to_add = 10 + (score - 90) * 0.4  # 10-14 days
            priority = "low"
            reason = f"Excellent performance ({score:.0f}%)! Long-term review to maintain mastery."
            estimated_improvement = "Maintain current level and strengthen long-term retention"
        elif score >= 80:
            # Good understanding - medium interval  
            days_to_add = 5 + (score - 80) * 0.5  # 5-10 days
            priority = "medium"
            reason = f"Good performance ({score:.0f}%). Medium-term review to strengthen understanding."
            estimated_improvement = "Expected to reach 85-95% with focused review"
        elif score >= 70:
            # Adequate understanding - shorter interval
            days_to_add = 3 + (score - 70) * 0.2  # 3-5 days
            priority = "medium"
            reason = f"Adequate performance ({score:.0f}%). Review needed to improve understanding."
            estimated_improvement = "Expected to reach 80-90% with dedicated practice"
        elif score >= 60:
            # Poor understanding - short interval
            days_to_add = 1 + (score - 60) * 0.2  # 1-3 days
            priority = "high"
            reason = f"Below expectations ({score:.0f}%). Quick review essential for improvement."
            estimated_improvement = "Expected to reach 70-80% with intensive review"
        else:
            # Very poor understanding - immediate review
            days_to_add = 0.5  # 12 hours
            priority = "high"
            reason = f"Needs immediate attention ({score:.0f}%). Urgent review required."
            estimated_improvement = "Focus on fundamentals to reach 60-70%"
        
        # Use AI to refine the recommendation
        prompt = f"""
        As an expert learning coach, analyze this student's practice test performance and recommend optimal scheduling:
        
        Subject: {subject}
        Topics: {', '.join(topics)}
        Score: {score:.1f}%
        Difficulty: {difficulty}
        Base recommendation: Review in {days_to_add:.1f} days
        
        Consider these factors:
        1. Spaced repetition principles for optimal retention
        2. Score-based urgency (lower scores need quicker review)
        3. Subject difficulty and complexity
        4. Student motivation and learning patterns
        
        Provide:
        1. Refined timing (adjust the {days_to_add:.1f} days if needed)
        2. 3-5 specific study tips for improvement
        3. Learning strategy recommendations
        
        Respond in JSON format:
        {{
            "timing_adjustment": 0.0,
            "study_tips": ["tip1", "tip2", "tip3"],
            "learning_strategy": "strategy description",
            "focus_areas": ["area1", "area2"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Try to extract JSON from the response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                ai_recommendation = json.loads(json_str)
                
                # Apply AI timing adjustment
                timing_adjustment = ai_recommendation.get("timing_adjustment", 0)
                final_days = max(0.25, days_to_add + timing_adjustment)  # Minimum 6 hours
                
                return {
                    "recommended_date": now + timedelta(days=final_days),
                    "priority": priority,
                    "reason": reason,
                    "study_tips": ai_recommendation.get("study_tips", self._get_default_study_tips(score)),
                    "estimated_improvement": estimated_improvement,
                    "learning_strategy": ai_recommendation.get("learning_strategy", "Review fundamentals and practice regularly"),
                    "focus_areas": ai_recommendation.get("focus_areas", topics)
                }
            else:
                # Fallback if JSON parsing fails
                return self._get_default_schedule_recommendation(now, days_to_add, priority, reason, estimated_improvement, score)
                
        except Exception as e:
            print(f"Error in AI schedule recommendation: {e}")
            return self._get_default_schedule_recommendation(now, days_to_add, priority, reason, estimated_improvement, score)

    def _get_default_schedule_recommendation(self, now, days_to_add, priority, reason, estimated_improvement, score):
        """Fallback scheduling recommendation"""
        return {
            "recommended_date": now + timedelta(days=days_to_add),
            "priority": priority,
            "reason": reason,
            "study_tips": self._get_default_study_tips(score),
            "estimated_improvement": estimated_improvement,
            "learning_strategy": "Focus on weak areas and practice regularly",
            "focus_areas": ["Review fundamentals", "Practice more problems"]
        }

    def _get_default_study_tips(self, score: float) -> List[str]:
        """Generate default study tips based on score"""
        if score >= 80:
            return [
                "Continue practicing to maintain mastery",
                "Try more challenging problems",
                "Teach concepts to others to reinforce learning",
                "Focus on application and real-world examples"
            ]
        elif score >= 60:
            return [
                "Review fundamental concepts thoroughly",
                "Practice similar problems daily",
                "Identify and work on specific weak areas",
                "Seek help from teachers or tutors if needed"
            ]
        else:
            return [
                "Start with basic concepts and build up",
                "Practice simple problems before complex ones",
                "Create concept maps and summary notes",
                "Schedule regular short study sessions",
                "Don't hesitate to ask for help"
            ]

    def _generate_study_tips(self, subjects: List[Dict]) -> List[str]:
        """Generate personalized study tips for study planner"""
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