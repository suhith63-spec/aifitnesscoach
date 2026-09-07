import streamlit as st
import os
from datetime import datetime, timedelta
from deepseek_fitness_ai import FitnessAIAssistant, DatabaseManager
import json
import sqlite3

class EnhancedFitnessChatbot:
    """Enhanced chatbot using DeepSeek R1 with fitness filtering"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        # Initialize with environment variable or default
        api_key = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key-here")
        self.ai_assistant = FitnessAIAssistant(api_key)
        
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "user_id" not in st.session_state:
            st.session_state.user_id = "default_user"
        if "current_mode" not in st.session_state:
            st.session_state.current_mode = "fitness"
    
    def create_user_profile(self):
        """Create or update user profile"""
        st.sidebar.header("👤 User Profile")
        
        with st.sidebar.expander("Profile Settings", expanded=False):
            name = st.text_input("Name", value="")
            age = st.number_input("Age", min_value=13, max_value=100, value=25)
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0)
            fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
            goals = st.text_area("Fitness Goals", placeholder="e.g., Weight loss, Muscle gain, General fitness")
            
            if st.button("Save Profile"):
                self.save_user_profile(name, age, weight, height, fitness_level, goals)
                st.success("Profile saved!")
    
    def save_user_profile(self, name, age, weight, height, fitness_level, goals):
        """Save user profile to MongoDB"""
        self.db_manager.db.users.update_one(
            {'user_id': st.session_state.user_id},
            {'$set': {
                'name': name,
                'age': age,
                'weight': weight,
                'height': height,
                'fitness_level': fitness_level,
                'goals': goals,
                'created_at': datetime.now()
            }},
            upsert=True
        )
    
    def display_chat_history(self):
        """Display chat history with improved styling"""
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    if "category" in message:
                        st.caption(f"Category: {message['category']}")
    
    def handle_special_queries(self, query: str) -> str:
        """Handle special fitness queries with database integration"""
        query_lower = query.lower()
        
        # Workout schedule queries
        if any(word in query_lower for word in ["workout", "schedule", "tomorrow", "today", "plan"]):
            if "tomorrow" in query_lower:
                return self.ai_assistant.get_workout_schedule(st.session_state.user_id, "tomorrow")
            elif "today" in query_lower:
                return self.ai_assistant.get_workout_schedule(st.session_state.user_id, "today")
        
        # Progress tracking queries
        if any(word in query_lower for word in ["progress", "tracking", "improvement", "results"]):
            return self.get_progress_summary()
        
        # Diet/nutrition queries
        if any(word in query_lower for word in ["diet", "nutrition", "meal", "calories", "macros"]):
            return self.get_nutrition_advice(query)
        
        return None
    
    def get_progress_summary(self) -> str:
        """Get user's progress summary from MongoDB"""
        results = list(self.db_manager.db.progress_tracking.find(
            {'user_id': st.session_state.user_id}
        ).sort('timestamp', -1).limit(10))
        
        if not results:
            return "No progress data found. Start tracking your workouts and measurements to see your progress!"
        
        summary = "📊 **Your Recent Progress:**\n\n"
        for doc in results:
            timestamp_str = doc['timestamp'].strftime('%Y-%m-%d')
            summary += f"• {doc['metric_type']}: {doc['metric_value']} ({timestamp_str})\n"
        
        return summary
    
    def get_nutrition_advice(self, query: str) -> str:
        """Get personalized nutrition advice from MongoDB"""
        user_profile = self.db_manager.db.users.find_one(
            {'user_id': st.session_state.user_id}
        )
        
        if user_profile:
            context = f"User profile: {user_profile.get('weight')}kg, {user_profile.get('height')}cm, {user_profile.get('age')} years old, Goals: {user_profile.get('goals')}"
            return self.ai_assistant.deepseek_client.generate_response(query, context)
        
        return self.ai_assistant.deepseek_client.generate_response(query)
    
    def add_sample_workout_plan(self):
        """Add sample workout plan to MongoDB"""
        sample_plan = {
            "plan_id": f"{st.session_state.user_id}_sample",
            "user_id": st.session_state.user_id,
            "plan_name": "Beginner Full Body",
            "exercises": ["Push-ups", "Squats", "Planks", "Lunges", "Mountain Climbers"],
            "schedule": {
                "Monday": ["Push-ups", "Squats"],
                "Wednesday": ["Planks", "Lunges"],
                "Friday": ["Mountain Climbers", "Push-ups"]
            },
            "created_at": datetime.now()
        }
        
        self.db_manager.db.workout_plans.update_one(
            {'plan_id': sample_plan['plan_id']},
            {'$set': sample_plan},
            upsert=True
        )
    
    def run_chatbot_ui(self):
        """Main chatbot UI"""
        st.set_page_config(
            page_title="Forever Fit",
            page_icon="💪",
            layout="wide"
        )
        
        self.initialize_session_state()
        
        # Header
        st.title("💪 Forever Fit - DeepSeek R1 Powered")
        st.markdown("Your personalized fitness and mental health assistant")
        
        # Sidebar
        self.create_user_profile()
        
        # Mode selection
        st.sidebar.header("🎯 Assistant Mode")
        mode = st.sidebar.radio(
            "Choose mode:",
            ["Fitness Coach", "Mental Health Support", "Nutrition Advisor"]
        )
        st.session_state.current_mode = mode.lower().replace(" ", "_")
        
        # Quick actions
        st.sidebar.header("⚡ Quick Actions")
        if st.sidebar.button("📅 Today's Workout"):
            response = self.ai_assistant.get_workout_schedule(st.session_state.user_id, "today")
            st.session_state.chat_history.append({"role": "assistant", "content": response, "category": "fitness"})
            st.rerun()
        
        if st.sidebar.button("📊 Progress Summary"):
            response = self.get_progress_summary()
            st.session_state.chat_history.append({"role": "assistant", "content": response, "category": "progress"})
            st.rerun()
        
        if st.sidebar.button("🍎 Nutrition Tips"):
            response = self.get_nutrition_advice("Give me general nutrition tips for my goals")
            st.session_state.chat_history.append({"role": "assistant", "content": response, "category": "nutrition"})
            st.rerun()
        
        if st.sidebar.button("➕ Add Sample Workout"):
            self.add_sample_workout_plan()
            st.sidebar.success("Sample workout plan added!")
        
        # Main chat interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display chat history
            chat_container = st.container()
            with chat_container:
                self.display_chat_history()
            
            # Chat input
            user_input = st.chat_input("Ask me anything about fitness, nutrition, or mental health...")
            
            if user_input:
                # Add user message to history
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Process query
                with st.spinner("Thinking..."):
                    # Check for special queries first
                    special_response = self.handle_special_queries(user_input)
                    
                    if special_response:
                        response = special_response
                        category = "special"
                    elif st.session_state.current_mode == "mental_health_support":
                        response = self.ai_assistant.handle_mental_health_query(st.session_state.user_id, user_input)
                        category = "mental_health"
                    else:
                        response, category = self.ai_assistant.process_query(st.session_state.user_id, user_input)
                
                # Add assistant response to history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": response, 
                    "category": category
                })
                
                st.rerun()
        
        with col2:
            # Statistics panel
            st.subheader("📈 Statistics")
            
            # Chat statistics
            total_messages = len(st.session_state.chat_history)
            user_messages = len([m for m in st.session_state.chat_history if m["role"] == "user"])
            
            st.metric("Total Messages", total_messages)
            st.metric("Your Questions", user_messages)
            
            # Category breakdown
            categories = {}
            for message in st.session_state.chat_history:
                if message["role"] == "assistant" and "category" in message:
                    cat = message["category"]
                    categories[cat] = categories.get(cat, 0) + 1
            
            if categories:
                st.subheader("📊 Topics Discussed")
                for category, count in categories.items():
                    st.write(f"• {category.title()}: {count}")
            
            # Clear chat button
            if st.button("🗑️ Clear Chat", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()

def main():
    """Main function to run the enhanced chatbot"""
    chatbot = EnhancedFitnessChatbot()
    chatbot.run_chatbot_ui()

if __name__ == "__main__":
    main()