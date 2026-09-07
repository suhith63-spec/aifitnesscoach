import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
from pymongo import MongoClient

@dataclass
class UserInteraction:
    user_id: str
    query: str
    response: str
    category: str
    timestamp: datetime
    context_data: Dict

class FitnessContentFilter:
    """Filter to ensure only fitness and health related content is processed"""
    
    FITNESS_KEYWORDS = {
        'exercise', 'workout', 'fitness', 'training', 'gym', 'muscle', 'strength',
        'cardio', 'running', 'cycling', 'swimming', 'yoga', 'pilates', 'crossfit',
        'bodybuilding', 'powerlifting', 'weightlifting', 'calisthenics', 'hiit',
        'nutrition', 'diet', 'protein', 'calories', 'macros', 'supplements',
        'health', 'wellness', 'recovery', 'sleep', 'hydration', 'stretching',
        'flexibility', 'mobility', 'injury', 'rehabilitation', 'physical therapy',
        'mental health', 'stress', 'anxiety', 'depression', 'motivation',
        'goal setting', 'progress tracking', 'body composition', 'weight loss',
        'weight gain', 'muscle building', 'fat loss', 'endurance', 'performance'
    }
    
    MENTAL_HEALTH_KEYWORDS = {
        'mental health', 'stress', 'anxiety', 'depression', 'mood', 'emotional',
        'wellbeing', 'mindfulness', 'meditation', 'therapy', 'counseling',
        'self-care', 'motivation', 'confidence', 'self-esteem', 'burnout',
        'work-life balance', 'relationships', 'coping', 'resilience'
    }
    
    def is_fitness_related(self, text: str) -> bool:
        """Check if text is fitness/health related"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.FITNESS_KEYWORDS)
    
    def is_mental_health_related(self, text: str) -> bool:
        """Check if text is mental health related"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.MENTAL_HEALTH_KEYWORDS)
    
    def categorize_query(self, text: str) -> str:
        """Categorize the query type"""
        if self.is_mental_health_related(text):
            return "mental_health"
        elif self.is_fitness_related(text):
            return "fitness"
        else:
            return "general"

class DatabaseManager:
    """MongoDB Atlas manager for user data and interactions"""
    
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
        self.db = self.client[os.getenv("MONGODB_DATABASE", "fitness_ai")]
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            self.db.interactions.create_index([("user_id", 1), ("timestamp", -1)])
            self.db.workout_plans.create_index([("user_id", 1), ("created_at", -1)])
            self.db.mental_health_sessions.create_index([("user_id", 1), ("timestamp", -1)])
            self.db.progress_tracking.create_index([("user_id", 1), ("timestamp", -1)])
        except:
            pass  # Indexes might already exist
    
    def save_interaction(self, interaction: UserInteraction):
        """Save user interaction to MongoDB"""
        self.db.interactions.insert_one({
            'user_id': interaction.user_id,
            'query': interaction.query,
            'response': interaction.response,
            'category': interaction.category,
            'context_data': interaction.context_data,
            'timestamp': interaction.timestamp
        })
    
    def get_user_context(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent user interactions from MongoDB"""
        interactions = self.db.interactions.find(
            {'user_id': user_id}
        ).sort('timestamp', -1).limit(limit)
        
        return [
            {
                'query': doc['query'],
                'response': doc['response'],
                'category': doc['category'],
                'context_data': doc.get('context_data', {}),
                'timestamp': doc['timestamp']
            }
            for doc in interactions
        ]
    
    def get_workout_plan(self, user_id: str, date: str = None) -> Optional[Dict]:
        """Get user's workout plan from MongoDB"""
        plan = self.db.workout_plans.find_one(
            {'user_id': user_id},
            sort=[('created_at', -1)]
        )
        
        if plan:
            return {
                'plan_name': plan['plan_name'],
                'exercises': plan.get('exercises', []),
                'schedule': plan.get('schedule', {})
            }
        return None

class DeepSeekR1Client:
    """Client for DeepSeek R1 API integration"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_response(self, prompt: str, context: str = "", max_tokens: int = 1000) -> str:
        """Generate response using DeepSeek R1"""
        try:
            # Simplified message format for DeepSeek
            if context:
                full_prompt = f"Context: {context}\n\nQuery: {prompt}"
            else:
                full_prompt = prompt
                
            payload = {
                "model": "deepseek-chat",  # Use deepseek-chat instead of deepseek-r1
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful fitness and health assistant. Provide helpful advice about exercise, nutrition, and wellness."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return "Sorry, I couldn't generate a response. Please try again."
            else:
                if response.status_code == 402:
                    return "I'm currently using basic responses due to API limitations. I can still help with fitness, nutrition, and wellness questions using my built-in knowledge!"
                elif response.status_code == 401:
                    return "I'm currently using basic responses due to authentication issues. I can still help with fitness and health questions!"
                else:
                    error_msg = f"API Error {response.status_code}"
                    try:
                        error_detail = response.json()
                        if "error" in error_detail:
                            error_msg += f": {error_detail['error'].get('message', 'Unknown error')}"
                    except:
                        pass
                    return "I'm currently using basic responses. I can still help with fitness, nutrition, and wellness questions!"
                
        except Exception as e:
            return "I'm currently using basic responses due to technical limitations. I can still help with fitness, nutrition, and wellness questions!"

class FitnessAIAssistant:
    """Main AI Assistant class integrating all components"""
    
    def __init__(self, deepseek_api_key: str):
        self.content_filter = FitnessContentFilter()
        self.db_manager = DatabaseManager()
        self.deepseek_client = DeepSeekR1Client(deepseek_api_key)
    
    def process_query(self, user_id: str, query: str) -> Tuple[str, str]:
        """Process user query with filtering and context awareness"""
        
        # Filter content
        category = self.content_filter.categorize_query(query)
        
        if category == "general":
            return ("I'm specialized in fitness, health, nutrition, and mental wellness. "
                   "Please ask me questions related to these topics, and I'll be happy to help!"), category
        
        # Get user context
        user_context = self.db_manager.get_user_context(user_id)
        context_str = self._build_context_string(user_context, user_id)
        
        # Generate response using DeepSeek R1
        response = self.deepseek_client.generate_response(query, context_str)
        
        # Save interaction
        interaction = UserInteraction(
            user_id=user_id,
            query=query,
            response=response,
            category=category,
            timestamp=datetime.now(),
            context_data={"user_context_length": len(user_context)}
        )
        self.db_manager.save_interaction(interaction)
        
        return response, category
    
    def _build_context_string(self, user_context: List[Dict], user_id: str) -> str:
        """Build context string from user history and data"""
        context_parts = []
        
        # Add recent interactions
        if user_context:
            context_parts.append("Recent conversation history:")
            for ctx in user_context[:5]:  # Last 5 interactions
                context_parts.append(f"Q: {ctx['query'][:100]}...")
                context_parts.append(f"A: {ctx['response'][:100]}...")
        
        # Add workout plan if available
        workout_plan = self.db_manager.get_workout_plan(user_id)
        if workout_plan:
            context_parts.append(f"Current workout plan: {workout_plan['plan_name']}")
            context_parts.append(f"Exercises: {', '.join(workout_plan['exercises'][:5])}")
        
        return "\n".join(context_parts)
    
    def get_workout_schedule(self, user_id: str, date: str = "tomorrow") -> str:
        """Get workout schedule for specific date"""
        workout_plan = self.db_manager.get_workout_plan(user_id)
        
        if not workout_plan:
            return "You don't have a workout plan set up yet. Would you like me to help you create one?"
        
        # Process date and return schedule
        schedule = workout_plan.get('schedule', {})
        if date.lower() in ['tomorrow', 'today']:
            # Simple logic - in real implementation, you'd parse actual dates
            return f"Your {date} workout: {', '.join(workout_plan['exercises'][:3])}"
        
        return f"Your workout plan includes: {', '.join(workout_plan['exercises'])}"
    
    def handle_mental_health_query(self, user_id: str, query: str) -> str:
        """Handle mental health specific queries"""
        context = self.db_manager.get_user_context(user_id)
        mental_health_context = [ctx for ctx in context if ctx['category'] == 'mental_health']
        
        context_str = f"Mental health conversation history: {len(mental_health_context)} previous sessions"
        
        # Add mental health specific system prompt
        enhanced_query = f"""
        As a mental health support assistant, provide empathetic and helpful guidance.
        Previous sessions: {len(mental_health_context)}
        Current query: {query}
        """
        
        response = self.deepseek_client.generate_response(enhanced_query, context_str)
        
        # Save mental health session to MongoDB
        self.db_manager.db.mental_health_sessions.insert_one({
            'user_id': user_id,
            'session_notes': query,
            'recommendations': response,
            'timestamp': datetime.now()
        })
        
        return response

# Example usage and testing
if __name__ == "__main__":
    # Initialize the assistant (you'll need to add your DeepSeek API key)
    assistant = FitnessAIAssistant("your-deepseek-api-key-here")
    
    # Test queries
    test_queries = [
        "What's my workout plan for tomorrow?",
        "I'm feeling stressed about my fitness goals",
        "Can you help me with my diet plan?",
        "What's the weather like today?",  # Should be filtered out
    ]
    
    user_id = "test_user_123"
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response, category = assistant.process_query(user_id, query)
        print(f"Category: {category}")
        print(f"Response: {response}")
        print("-" * 50)