import streamlit as st
from dataclasses import dataclass
from typing import Literal

@dataclass
class Message:
    origin: Literal["human", "ai"]
    content: str

def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []

def simple_fitness_response(query):
    """Simple rule-based responses for fitness queries"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['workout', 'exercise', 'training']):
        return "I'd recommend starting with basic exercises like push-ups, squats, and planks. Always warm up before exercising and cool down afterward."
    
    elif any(word in query_lower for word in ['diet', 'nutrition', 'food']):
        return "A balanced diet includes proteins, healthy fats, complex carbohydrates, and plenty of vegetables. Stay hydrated and eat regular meals."
    
    elif any(word in query_lower for word in ['weight', 'lose', 'gain']):
        return "Weight management involves balancing calories in vs calories out. Combine regular exercise with proper nutrition for best results."
    
    elif any(word in query_lower for word in ['muscle', 'strength', 'build']):
        return "Building muscle requires progressive resistance training, adequate protein intake, and proper rest for recovery."
    
    else:
        return "I'm here to help with fitness, nutrition, and health questions. Please ask me about workouts, diet, or wellness topics!"

def chat_ui():
    initialize_session_state()
    st.title("Fitness AI Assistant")
    
    st.info("Simple fitness chatbot - Ask me about workouts, nutrition, or health!")

    # Chat Display
    for chat in st.session_state.history:
        if chat.origin == "human":
            st.markdown(f"**You:** {chat.content}")
        else:
            st.markdown(f"**AI:** {chat.content}")

    # Input form
    with st.form("chat_form"):
        user_input = st.text_input("Ask me about fitness, nutrition, or health:")
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input.strip():
            # Add user message
            st.session_state.history.append(Message("human", user_input))
            
            # Generate response
            response = simple_fitness_response(user_input)
            st.session_state.history.append(Message("ai", response))
            
            st.rerun()

if __name__ == "__main__":
    chat_ui()