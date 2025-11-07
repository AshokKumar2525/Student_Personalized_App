"""
Enhanced Gemini AI Content Generation Service
Generates structured educational content with integrated visuals
"""

import os
import json
import google.generativeai as genai
from typing import Dict, List, Any

class EnhancedGeminiContentService:
    """Service for generating structured educational content using Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini client"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        try:
            available_models = genai.list_models()
            model_names = [model.name for model in available_models]
            
            working_model = None
            preferred_models = [
                'models/gemini-2.0-flash',
                'models/gemini-2.0-flash-001',
                'models/gemini-flash-latest',
                'models/gemini-pro-latest',
            ]
            
            for model_name in preferred_models:
                if model_name in model_names:
                    working_model = model_name
                    break
            
            if working_model:
                self.model = genai.GenerativeModel(working_model)
                print(f"✅ Using Gemini model: {working_model}")
            else:
                self.model = None
                print("⚠️ No compatible Gemini models found")
                
        except Exception as e:
            print(f"⚠️ Error initializing Gemini: {e}")
            self.model = None
    
    def generate_enhanced_content(
        self,
        module_title: str,
        module_description: str
    ) -> Dict[str, Any]:
        """
        Generate enhanced structured educational content
        
        Returns:
            Dict containing:
            - concepts: Structured learning content with sub-topics
            - exercises: MCQ questions for knowledge assessment
            - practice_problems: Hands-on coding/implementation tasks
            - visuals: Integrated Mermaid diagrams and visual aids
        """
        try:
            if not self.model:
                print("⚠️ No Gemini model available, using fallback")
                return self._get_fallback_content(module_title)
                
            prompt = self._build_enhanced_prompt(module_title, module_description)
            
            print(f"🤖 Generating enhanced content for: {module_title}")
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8000,
                )
            )
            
            if not response.text:
                print("❌ Empty response from Gemini")
                return self._get_fallback_content(module_title)
                
            content = self._parse_ai_response(response.text)
            
            print(f"✅ Generated content with {len(content.get('concepts', []))} concepts")
            
            return content
            
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return self._get_fallback_content(module_title)
    
    def _build_enhanced_prompt(self, title: str, description: str) -> str:
        """Build comprehensive prompt for structured content"""
        return f"""Generate comprehensive educational content for this module:
                Title: {title}
                Description: {description}

                Create detailed, well-structured learning material following this EXACT format:

                ## 1. CONCEPTS (2-3 main concepts)
                Each concept should have this hierarchical structure:

                **Concept Structure:**
                - title: Clear, descriptive title
                - introduction: What is this concept? (2-3 sentences)
                - why_important: Why should learners care? (2-3 sentences)
                - sub_topics: Array of 3-5 sub-topics, each with:
                * sub_title: Clear sub-topic name
                * explanation: Detailed explanation (3-4 paragraphs)
                * visual_aid: Object containing:
                    - type: "mermaid" or "image_description"
                    - content: Mermaid syntax OR description for image search
                    - caption: Brief caption explaining the visual
                * code_example: (if applicable) Working code snippet with explanation
                * real_world_example: Concrete example from industry/daily life
                - implementation_guide: Step-by-step how to apply this concept
                - common_pitfalls: Array of common mistakes to avoid

                **Visual Aid Guidelines:**
                - Use Mermaid for: flowcharts, sequence diagrams, class diagrams, state diagrams
                - Use image_description for: photos, charts, metaphorical representations
                - Place visuals inline where most relevant, not at end

                ## 2. EXERCISES (5 MCQ questions - ONLY if topic is practical/testable)
                Each exercise should have:
                - question: Clear question text
                - options: Array of 4 options (A, B, C, D)
                - correct_answer: Letter of correct option
                - explanation: Why this answer is correct (2-3 sentences)
                - difficulty: "easy", "medium", or "hard"

                **EXCLUDE exercises for:**
                - Installation/setup topics
                - Pure configuration steps
                - Introduction/overview modules

                ## 3. PRACTICE PROBLEMS (3-4 problems - ONLY for implementation-focused topics)
                Each problem should have:
                - title: Descriptive problem title
                - description: What needs to be built/solved (2-3 paragraphs)
                - difficulty: "beginner", "intermediate", or "advanced"
                - type: "coding", "design", "analysis", or "implementation"
                - requirements: Array of specific requirements
                - hints: Array of 2-3 helpful hints (collapsible)
                - solution_approach: High-level approach without full solution
                - expected_output: What success looks like
                - code_template: (if coding) Starter code structure

                **EXCLUDE practice problems for:**
                - Theoretical concepts without coding
                - Basic setup/configuration
                - Introduction modules

                Return ONLY valid JSON with this EXACT structure:
                {{
                "concepts": [
                    {{
                    "title": "Concept Title",
                    "introduction": "What is this concept?",
                    "why_important": "Why it matters",
                    "sub_topics": [
                        {{
                        "sub_title": "Sub-topic Name",
                        "explanation": "Detailed explanation with multiple paragraphs",
                        "visual_aid": {{
                            "type": "mermaid",
                            "content": "graph TD\\n    A[Start] --> B[Process]",
                            "caption": "Visual explanation"
                        }},
                        "code_example": {{
                            "language": "python",
                            "code": "def example():\\n    pass",
                            "explanation": "What this code does"
                        }},
                        "real_world_example": "Industry application"
                        }}
                    ],
                    "implementation_guide": [
                        "Step 1: Do this",
                        "Step 2: Then this"
                    ],
                    "common_pitfalls": [
                        "Avoid doing X because Y"
                    ]
                    }}
                ],
                "exercises": [
                    {{
                    "question": "Question text?",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct_answer": "B",
                    "explanation": "Why B is correct",
                    "difficulty": "medium"
                    }}
                ],
                "practice_problems": [
                    {{
                    "title": "Build X Feature",
                    "description": "Detailed problem description",
                    "difficulty": "intermediate",
                    "type": "coding",
                    "requirements": ["Requirement 1", "Requirement 2"],
                    "hints": ["Hint 1", "Hint 2"],
                    "solution_approach": "High-level approach",
                    "expected_output": "What success looks like",
                    "code_template": "// Starter code"
                    }}
                ]
                }}

                CRITICAL RULES:
                1. Return ONLY JSON, no markdown, no extra text
                2. Ensure all JSON is properly formatted and valid
                3. Include visuals inline within sub-topics, not separate
                4. Make content comprehensive but clear
                5. Focus on practical understanding and application
                6. Only include exercises/practice for appropriate topics"""

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate AI response"""
        try:
            cleaned = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            elif cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            content = json.loads(cleaned)
            
            # Validate structure
            if 'concepts' not in content:
                raise ValueError("Missing concepts in response")
            
            return content
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response preview: {response_text[:500]}...")
            return self._get_fallback_content("")
    
    def _get_fallback_content(self, title: str) -> Dict[str, Any]:
        """Fallback content structure"""
        return {
            "concepts": [
                {
                    "title": f"Understanding {title}",
                    "introduction": f"This section introduces {title} and its fundamental concepts.",
                    "why_important": f"Learning {title} is essential for building modern applications and understanding industry standards.",
                    "sub_topics": [
                        {
                            "sub_title": "Core Principles",
                            "explanation": f"The core principles of {title} form the foundation of this technology. Understanding these principles helps you make informed decisions when implementing solutions.",
                            "visual_aid": {
                                "type": "mermaid",
                                "content": "graph LR\n    A[Input] --> B[Process]\n    B --> C[Output]",
                                "caption": "Basic workflow diagram"
                            },
                            "real_world_example": f"Industry applications of {title} include enterprise software and web platforms."
                        }
                    ],
                    "implementation_guide": [
                        "Start by understanding the basic concepts",
                        "Practice with simple examples",
                        "Build progressively complex projects"
                    ],
                    "common_pitfalls": [
                        "Avoid jumping to advanced topics too quickly",
                        "Don't skip fundamentals"
                    ]
                }
            ],
            "exercises": [
                {
                    "question": f"What is the primary purpose of {title}?",
                    "options": [
                        "A) To make development easier",
                        "B) To improve performance",
                        "C) To enhance user experience",
                        "D) All of the above"
                    ],
                    "correct_answer": "D",
                    "explanation": f"{title} serves multiple purposes in modern development.",
                    "difficulty": "easy"
                }
            ],
            "practice_problems": [
                {
                    "title": f"Implement Basic {title} Feature",
                    "description": f"Create a simple implementation demonstrating {title} concepts.",
                    "difficulty": "beginner",
                    "type": "coding",
                    "requirements": [
                        "Follow best practices",
                        "Include error handling",
                        "Add comments"
                    ],
                    "hints": [
                        "Start with the basic structure",
                        "Test incrementally"
                    ],
                    "solution_approach": "Begin with setup, implement core logic, then add enhancements.",
                    "expected_output": "Working implementation with proper structure"
                }
            ]
        }


# Singleton instance
_enhanced_gemini_service = None

def get_enhanced_gemini_service():
    """Get or create enhanced Gemini service instance"""
    global _enhanced_gemini_service
    if _enhanced_gemini_service is None:
        _enhanced_gemini_service = EnhancedGeminiContentService()
    return _enhanced_gemini_service