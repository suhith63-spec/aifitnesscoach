import os
import streamlit as st

# Try to import DeepSeek AI
DEEPSEEK_AVAILABLE = False
try:
    from dotenv import load_dotenv
    load_dotenv()
    from enhanced_deepseek_integration import get_mental_health_response, enhanced_client
    DEEPSEEK_AVAILABLE = True
except (ImportError, UnicodeDecodeError, Exception):
    DEEPSEEK_AVAILABLE = False

# Mixpanel Analytics
try:
    from mixpanel_analytics import analytics
    ANALYTICS_AVAILABLE = True
except Exception:
    ANALYTICS_AVAILABLE = False

# Check if DeepSeek is properly configured
if DEEPSEEK_AVAILABLE:
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        DEEPSEEK_AVAILABLE = False


def simple_mental_health_response(user_input):
    """Enhanced supportive responses for mental health queries"""
    input_lower = user_input.lower()
    
    if any(word in input_lower for word in ['stress', 'stressed', 'anxious', 'anxiety', 'worried', 'overwhelmed']):
        return "I understand you're feeling stressed. Here are some techniques that can help: 1) Deep breathing (4 counts in, 4 counts out), 2) Progressive muscle relaxation, 3) Take short breaks throughout the day, 4) Regular exercise, 5) Talk to someone you trust. Remember, it's okay to ask for help."
    
    elif any(word in input_lower for word in ['sad', 'depressed', 'down', 'low', 'hopeless']):
        return "I'm sorry you're feeling this way. Your feelings are valid and it's important to reach out for support. Consider: 1) Speaking with a mental health professional, 2) Connecting with trusted friends or family, 3) Engaging in activities you usually enjoy, 4) Getting some sunlight and fresh air. Remember, these feelings are temporary and help is available."
    
    elif any(word in input_lower for word in ['motivation', 'motivated', 'goals', 'purpose']):
        return "Building motivation can be challenging. Try: 1) Setting small, achievable daily goals, 2) Celebrating small wins, 3) Creating a routine, 4) Connecting with your 'why', 5) Breaking large tasks into smaller steps. Remember, progress isn't always linear - be patient with yourself."
    
    elif any(word in input_lower for word in ['sleep', 'tired', 'exhausted', 'insomnia']):
        return "Good sleep is crucial for mental health. Sleep hygiene tips: 1) Consistent sleep schedule, 2) Avoid screens 1 hour before bed, 3) Create a relaxing bedtime routine, 4) Keep bedroom cool and dark, 5) Limit caffeine after 2 PM, 6) Regular exercise (but not close to bedtime)."
    
    elif any(word in input_lower for word in ['lonely', 'alone', 'isolated', 'social']):
        return "Feeling lonely is more common than you might think. Consider: 1) Reaching out to old friends, 2) Joining clubs or groups with shared interests, 3) Volunteering in your community, 4) Taking classes, 5) Using technology to connect with others. Small social interactions can make a big difference."
    
    elif any(word in input_lower for word in ['confidence', 'self-esteem', 'worth', 'doubt']):
        return "Building self-confidence takes time. Try: 1) Practice self-compassion, 2) Focus on your strengths and achievements, 3) Set and accomplish small goals, 4) Challenge negative self-talk, 5) Surround yourself with supportive people. Remember, you are worthy of respect and kindness, especially from yourself."
    
    elif any(word in input_lower for word in ['exercise', 'workout', 'physical', 'activity']):
        return "Exercise is excellent for mental health! It releases endorphins, reduces stress, and improves mood. Start small: 1) 10-15 minute walks, 2) Stretching or yoga, 3) Dancing to favorite music, 4) Gardening, 5) Any movement you enjoy. The key is consistency, not intensity."
    
    else:
        return "Thank you for sharing with me. Remember that seeking help is a sign of strength, not weakness. If you're struggling, consider speaking with a mental health professional who can provide personalized support. You don't have to go through difficult times alone."

def get_deepseek_response(user_input, user_id="mental_health_user"):
    if not DEEPSEEK_AVAILABLE:
        return simple_mental_health_response(user_input)
    
    try:
        # Use the enhanced mental health handler
        response = get_mental_health_response(user_id, user_input)
        return response
    except Exception as e:
        # Fallback to simple response if API fails
        return simple_mental_health_response(user_input)


def mental_health_ui():
    st.title("🧘 Mental Health Support Assistant")
    
    if DEEPSEEK_AVAILABLE:
        st.success("✅ Enhanced AI with specialized mental health support active")
    else:
        st.info("💬 Using comprehensive built-in mental health support responses")
        st.warning("⚠️ Add DEEPSEEK_API_KEY to .env file for enhanced AI capabilities")
        
    st.write(
        "I'm here to listen and provide support for your mental wellness journey. Feel free to share your thoughts."
    )
    
    st.info(
        "**Important**: This is not a replacement for professional mental health care. "
        "If you're experiencing a mental health crisis, please contact a mental health professional or crisis hotline immediately."
    )

    # Initialize session state for mental health chat
    if "mental_health_history" not in st.session_state:
        st.session_state.mental_health_history = []
    if "mental_health_user_id" not in st.session_state:
        st.session_state.mental_health_user_id = "mental_health_" + str(hash("mental_session"))

    # Display chat history
    for message in st.session_state.mental_health_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Support Bot:** {message['content']}")

    # Input form
    with st.form("mental_health_form"):
        user_input = st.text_area("What's on your mind today?", height=100)
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input.strip():
            # Add user message to history
            st.session_state.mental_health_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get AI response
            response = get_deepseek_response(user_input, st.session_state.mental_health_user_id)
            
            # Track interaction
            if ANALYTICS_AVAILABLE:
                try:
                    user_id = st.session_state.user['user_id'] if 'user' in st.session_state else "guest"
                    analytics.track_event(user_id, "Mental Health Chat", {
                        "input_length": len(user_input),
                        "has_deepseek": DEEPSEEK_AVAILABLE
                    })
                except Exception:
                    pass
            
            # Add AI response to history
            st.session_state.mental_health_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Rerun to show new messages
            st.rerun()

    # Quick topic buttons and clear chat
    st.markdown("**🚀 Quick Support Topics:**")
    col1, col2, col3, col4 = st.columns(4)
    
    quick_topic = None
    with col1:
        if st.button("😰 Anxiety Help"):
            quick_topic = "I'm feeling anxious and need some coping strategies"
    with col2:
        if st.button("😔 Feeling Down"):
            quick_topic = "I'm feeling sad and need some support"
    with col3:
        if st.button("💪 Motivation"):
            quick_topic = "I'm struggling with motivation and need encouragement"
    with col4:
        if st.button("😴 Sleep Issues"):
            quick_topic = "I'm having trouble sleeping and it's affecting my mental health"
    
    # Process quick topic if selected
    if quick_topic:
        st.session_state.mental_health_history.append({
            "role": "user",
            "content": quick_topic
        })
        
        with st.spinner("🤔 Thinking of the best way to support you..."):
            response = get_deepseek_response(quick_topic, st.session_state.mental_health_user_id)
            
            # Track quick topic
            if ANALYTICS_AVAILABLE:
                try:
                    user_id = st.session_state.user['user_id'] if 'user' in st.session_state else "guest"
                    analytics.track_event(user_id, "Mental Health Quick Topic", {
                        "topic": quick_topic[:30] + "...",
                        "has_deepseek": DEEPSEEK_AVAILABLE
                    })
                except Exception:
                    pass
        
        st.session_state.mental_health_history.append({
            "role": "assistant",
            "content": response
        })
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.mental_health_history = []
        st.rerun()

    # Mental health resources
    with st.expander("Mental Health Resources"):
        st.markdown("""
        **Emergency Resources:**
        - National Suicide Prevention Lifeline: 988
        - Crisis Text Line: Text HOME to 741741
        
        **Professional Help:**
        - Consider speaking with a licensed therapist or counselor
        - Your primary care doctor can provide referrals
        - Many employers offer Employee Assistance Programs (EAP)
        
        **Self-Care Tips:**
        - Regular exercise and physical activity
        - Adequate sleep (7-9 hours per night)
        - Mindfulness and meditation practices
        - Social connections and support systems
        """)


if __name__ == "__main__":
    mental_health_ui()