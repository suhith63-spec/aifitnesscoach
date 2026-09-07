"""
DeepSeek R1 Integration for Fitness AI Trainer
Provides intelligent reasoning specifically for fitness and healthcare queries
"""

import os
import json
import requests
import streamlit as st
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

@dataclass
class QueryClassification:
    """Classification result for user queries"""
    is_fitness_healthcare: bool
    category: str  # 'exercise', 'nutrition', 'health', 'mental_health', 'form_correction', 'workout_planning'
    confidence: float
    reasoning: str

class DeepSeekReasoningEngine:
    """DeepSeek R1 reasoning engine for fitness and healthcare queries"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.fitness_keywords = {
            'exercise': [
                'exercise', 'workout', 'training', 'fitness', 'muscle', 'strength', 'cardio',
                'squat', 'push-up', 'pull-up', 'deadlift', 'bench press', 'bicep curl',
                'shoulder press', 'lunges', 'plank', 'burpees', 'running', 'cycling',
                'swimming', 'yoga', 'pilates', 'weightlifting', 'resistance training'
            ],
            'nutrition': [
                'diet', 'nutrition', 'calories', 'protein', 'carbohydrates', 'fat', 'vitamins',
                'meal plan', 'supplements', 'hydration', 'water', 'macros', 'micronutrients',
                'weight loss', 'weight gain', 'muscle building', 'recovery', 'pre-workout',
                'post-workout', 'healthy eating', 'food', 'eating'
            ],
            'health': [
                'health', 'medical', 'injury', 'pain', 'recovery', 'inflammation', 'stress',
                'sleep', 'heart rate', 'blood pressure', 'cholesterol', 'diabetes',
                'arthritis', 'back pain', 'knee pain', 'shoulder pain', 'physiotherapy',
                'rehabilitation', 'wellness', 'health check', 'symptoms'
            ],
            'mental_health': [
                'mental health', 'stress', 'anxiety', 'depression', 'motivation', 'mindfulness',
                'meditation', 'mental wellness', 'psychological', 'therapy', 'counseling',
                'emotional', 'mood', 'confidence', 'self-esteem', 'mental clarity'
            ],
            'form_correction': [
                'form', 'technique', 'posture', 'alignment', 'movement', 'proper form',
                'correct technique', 'body position', 'stance', 'grip', 'breathing',
                'range of motion', 'flexibility', 'mobility'
            ],
            'workout_planning': [
                'workout plan', 'training program', 'routine', 'schedule', 'progression',
                'periodization', 'volume', 'intensity', 'frequency', 'recovery time',
                'rest day', 'split', 'circuit', 'superset', 'drop set'
            ]
        }
        
        # System prompt for DeepSeek R1
        self.system_prompt = """You are a specialized AI reasoning assistant for fitness and healthcare. Your role is to:

1. ANALYZE user queries to determine if they are related to fitness, exercise, nutrition, health, or wellness
2. REASON through fitness-related problems with expert knowledge
3. PROVIDE detailed, evidence-based responses for fitness and healthcare topics
4. REJECT queries that are unrelated to fitness, health, exercise, or wellness

ACCEPT these types of queries:
- Exercise form and technique questions
- Workout planning and programming
- Nutrition and diet advice
- Health and wellness concerns
- Fitness goal setting and tracking
- Mental health related to fitness
- Injury prevention and recovery
- Equipment and training methods

REJECT these types of queries:
- General knowledge unrelated to fitness/health
- Personal problems not fitness-related
- Academic or professional questions outside fitness/health
- Entertainment, politics, or current events
- Technical programming or software questions

For each query, provide:
1. Clear reasoning about why it's relevant or irrelevant to fitness/health
2. If relevant: detailed, helpful response with actionable advice
3. If irrelevant: politely redirect to fitness/health topics

Always maintain a professional, supportive tone focused on helping users achieve their fitness and health goals."""

    def classify_query(self, query: str) -> QueryClassification:
        """Classify if a query is fitness/healthcare related"""
        query_lower = query.lower()
        
        # Check for fitness/healthcare keywords
        categories_found = []
        total_score = 0
        
        for category, keywords in self.fitness_keywords.items():
            category_score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    category_score += 1
                    total_score += 1
            
            if category_score > 0:
                categories_found.append((category, category_score))
        
        # Calculate confidence based on keyword matches
        confidence = min(total_score / 5.0, 1.0)  # Normalize to 0-1
        
        # Additional checks for relevance
        fitness_context_indicators = [
            'how to', 'what is', 'should i', 'can i', 'help with', 'advice on',
            'improve', 'increase', 'decrease', 'better', 'best way', 'tips for'
        ]
        
        has_context = any(indicator in query_lower for indicator in fitness_context_indicators)
        if has_context and total_score > 0:
            confidence = min(confidence + 0.2, 1.0)
        
        is_fitness_healthcare = confidence >= 0.3  # Threshold for acceptance
        primary_category = max(categories_found, key=lambda x: x[1])[0] if categories_found else 'general'
        
        reasoning = f"Query contains {total_score} fitness/health keywords across {len(categories_found)} categories. "
        reasoning += f"Primary category: {primary_category}. "
        reasoning += "Query appears fitness/health related." if is_fitness_healthcare else "Query does not appear to be fitness/health related."
        
        return QueryClassification(
            is_fitness_healthcare=is_fitness_healthcare,
            category=primary_category,
            confidence=confidence,
            reasoning=reasoning
        )

    def reason_about_query(self, query: str, classification: QueryClassification) -> str:
        """Use DeepSeek R1 to reason about fitness/healthcare queries"""
        if not classification.is_fitness_healthcare:
            return self._get_rejection_response(query, classification)
        
        try:
            # Prepare the request for DeepSeek R1
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Enhanced prompt for fitness reasoning
            user_prompt = f"""
Query Category: {classification.category}
User Query: {query}

Please provide a comprehensive, evidence-based response that includes:

1. **Immediate Answer**: Direct response to the user's question
2. **Detailed Reasoning**: Step-by-step explanation of why this advice is appropriate
3. **Safety Considerations**: Any important safety notes or contraindications
4. **Practical Implementation**: Specific, actionable steps the user can take
5. **Additional Context**: Relevant background information that helps the user understand
6. **Follow-up Suggestions**: Related topics or next steps the user might consider

Focus on being practical, safe, and encouraging while maintaining scientific accuracy.
"""
            
            data = {
                "model": "deepseek-reasoner",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return self._get_fallback_response(query, classification)
                
        except Exception as e:
            st.error(f"Error calling DeepSeek API: {str(e)}")
            return self._get_fallback_response(query, classification)

    def _get_rejection_response(self, query: str, classification: QueryClassification) -> str:
        """Generate a polite rejection response for non-fitness queries"""
        return f"""
I'm a specialized fitness and healthcare AI assistant. Your query about "{query}" doesn't appear to be related to fitness, exercise, nutrition, health, or wellness.

**I can help you with:**
- Exercise form and technique questions
- Workout planning and programming  
- Nutrition and diet advice
- Health and wellness concerns
- Fitness goal setting and tracking
- Mental health related to fitness
- Injury prevention and recovery

Please feel free to ask me anything about fitness, health, or wellness - I'm here to help you achieve your health goals! 💪
"""

    def _get_fallback_response(self, query: str, classification: QueryClassification) -> str:
        """Fallback response when DeepSeek API is unavailable"""
        category_responses = {
            'exercise': "I'd be happy to help with exercise-related questions! However, I'm experiencing technical difficulties with my reasoning engine. Please try asking about specific exercises, form corrections, or workout routines.",
            'nutrition': "I can assist with nutrition and diet questions! Unfortunately, my advanced reasoning system is temporarily unavailable. Feel free to ask about meal planning, supplements, or dietary goals.",
            'health': "I'm designed to help with health and wellness questions! My reasoning engine is currently offline, but I can still provide general guidance on health topics.",
            'mental_health': "I support mental health and wellness! While my advanced reasoning is temporarily unavailable, I can still offer encouragement and basic guidance.",
            'form_correction': "I specialize in exercise form and technique! My reasoning system is currently offline, but I can still help with basic form questions.",
            'workout_planning': "I can help design workout plans and training programs! My advanced reasoning is temporarily unavailable, but I can still provide workout guidance."
        }
        
        return category_responses.get(
            classification.category,
            "I'm a fitness and healthcare AI assistant, but my advanced reasoning system is currently unavailable. Please try asking about fitness, health, or wellness topics!"
        )

    def enhance_exercise_analysis(self, exercise_data: Dict) -> str:
        """Use DeepSeek R1 to provide enhanced analysis of exercise performance"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
Based on the following exercise analysis data, provide comprehensive feedback:

Exercise Data: {json.dumps(exercise_data, indent=2)}

Please provide:
1. **Performance Analysis**: Overall assessment of the exercise execution
2. **Form Assessment**: Specific feedback on technique and form
3. **Improvement Recommendations**: Actionable advice for better performance
4. **Safety Notes**: Any potential risks or safety considerations
5. **Progression Suggestions**: How to advance or modify the exercise
6. **Motivational Feedback**: Encouraging and supportive comments

Focus on being constructive, specific, and encouraging while maintaining safety as the top priority.
"""
            
            data = {
                "model": "deepseek-reasoner",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.6,
                "max_tokens": 800
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return "Exercise analysis completed, but advanced reasoning feedback is currently unavailable."
                
        except Exception as e:
            return f"Exercise analysis completed. Advanced feedback temporarily unavailable: {str(e)}"

    def enhance_diet_recommendations(self, user_profile: Dict, dietary_goals: str) -> str:
        """Use DeepSeek R1 to provide enhanced diet recommendations"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
User Profile: {json.dumps(user_profile, indent=2)}
Dietary Goals: {dietary_goals}

Please provide comprehensive dietary recommendations including:

1. **Macro Distribution**: Optimal protein, carbs, and fat ratios
2. **Meal Timing**: When to eat for optimal results
3. **Food Recommendations**: Specific foods and portion sizes
4. **Hydration Strategy**: Water intake recommendations
5. **Supplement Suggestions**: If any supplements might be beneficial
6. **Meal Planning**: Practical meal prep and planning tips
7. **Progress Tracking**: How to monitor dietary success
8. **Adjustments**: When and how to modify the plan

Consider the user's profile, goals, and provide evidence-based recommendations.
"""
            
            data = {
                "model": "deepseek-reasoner",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1200
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return "Diet analysis completed, but advanced reasoning recommendations are currently unavailable."
                
        except Exception as e:
            return f"Diet analysis completed. Advanced recommendations temporarily unavailable: {str(e)}"


def initialize_deepseek_reasoning() -> Optional[DeepSeekReasoningEngine]:
    """Initialize DeepSeek reasoning engine if API key is available"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.warning("DeepSeek API key not found. Advanced reasoning features will be limited.")
        return None
    
    try:
        return DeepSeekReasoningEngine(api_key)
    except Exception as e:
        st.error(f"Failed to initialize DeepSeek reasoning engine: {str(e)}")
        return None


# Fitness query validation patterns
FITNESS_PATTERNS = [
    r'\b(exercise|workout|training|fitness|muscle|strength|cardio)\b',
    r'\b(diet|nutrition|calories|protein|supplement|meal)\b',
    r'\b(health|wellness|injury|recovery|pain|sleep)\b',
    r'\b(form|technique|posture|alignment|breathing)\b',
    r'\b(routine|program|plan|schedule|progression)\b',
    r'\b(weight|lose|gain|build|tone|burn)\b',
    r'\b(rep|set|rest|warm|up|cool|down)\b',
    r'\b(gym|equipment|machine|free|weight|bodyweight)\b'
]

def is_fitness_query(query: str) -> bool:
    """Quick check if query contains fitness-related terms"""
    query_lower = query.lower()
    return any(re.search(pattern, query_lower) for pattern in FITNESS_PATTERNS)
