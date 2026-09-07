import os
import streamlit as st
from typing import Literal
from dataclasses import dataclass

# Try to import optional dependencies
DEEPSEEK_AVAILABLE = False
SPEECH_RECOGNITION_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except (ImportError, UnicodeDecodeError, Exception):
    DOTENV_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    pass

try:
    from enhanced_deepseek_integration import get_fitness_response, enhanced_client
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False

# Check if DeepSeek is properly configured
if DEEPSEEK_AVAILABLE and DOTENV_AVAILABLE:
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        DEEPSEEK_AVAILABLE = False


@dataclass
class Message:
    origin: Literal["human", "ai"]
    content: str


def initialize_session_state():
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "history" not in st.session_state:
        st.session_state.history = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = "streamlit_user_" + str(hash(st.session_state.get("session_id", "default")))


# Voice Input using speech recognition
def voice_input():
    if not SPEECH_RECOGNITION_AVAILABLE:
        st.error(
            "Speech recognition is not available. Please run 'pip install SpeechRecognition pyaudio' to enable voice input."
        )
        return ""

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.write("Listening... Please speak now.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio_data = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            st.write("Recognizing...")
            text = recognizer.recognize_google(audio_data)
            st.success(f"You said: {text}")
            return text
    except sr.WaitTimeoutError:
        st.error("No speech detected within the time limit. Please try again.")
        return ""
    except sr.UnknownValueError:
        st.error("Sorry, I couldn't understand your voice. Please try again.")
        return ""
    except Exception as e:
        st.error(f"Error: {e}")
        return ""


def simple_fitness_response(query):
    """Expert trainer responses that sound natural and experienced"""
    query_lower = query.lower()
    
    # Workout and Exercise
    if any(word in query_lower for word in ['workout', 'exercise', 'training', 'routine']):
        if 'beginner' in query_lower:
            return "Alright, listen up. I've been training people for over 15 years, and here's what separates those who succeed from those who quit after 3 weeks: Start stupidly simple. Bodyweight squats, push-ups (wall or knee if you need to), and planks. That's it. Three days a week, focus on nailing the form. I don't care if you can only do 3 push-ups - do 3 perfect ones. Your ego will recover, but bad habits stick around forever. Trust me on this one."
        elif 'home' in query_lower:
            return "Home workouts? Brother, I've gotten clients absolutely shredded in their living rooms. Here's the deal - you don't need fancy equipment, you need intensity and consistency. Push-ups, squats, lunges, planks, mountain climbers. 20-30 minutes, 3-4 times a week. I had one client lose 35 pounds doing nothing but this routine. The secret sauce? Make every rep count. No half-assing it because nobody's watching."
        else:
            return "Here's my go-to formula that's never failed me: 5-minute warm-up to get the blood flowing, 20-30 minutes hitting the big compound movements - squats, push-ups, rows - then finish with whatever cardio doesn't make you want to die. Do this 3-4 times a week. Keep it simple, stay consistent, and the results will come. I promise you that."
    
    # Diet and Nutrition
    elif any(word in query_lower for word in ['diet', 'nutrition', 'food', 'eat', 'meal']):
        if 'protein' in query_lower:
            return "Protein is absolutely king, especially if you're serious about this. Aim for 1.6-2.2g per kg of body weight if you're training hard. Chicken breast, fish, eggs, Greek yogurt - stick to the basics that have been working for decades. Don't get caught up in the fancy stuff. I've seen too many people obsess over the perfect protein powder while eating like garbage the rest of the day. Hit your numbers with real food first."
        elif 'weight loss' in query_lower or 'lose weight' in query_lower:
            return "Fat loss comes down to one thing: eating less than you burn. Create a 300-500 calorie deficit, prioritize protein to keep your muscle, and lift weights so you don't end up skinny-fat. The magic isn't in some special diet - it's in being consistent day after day. I've watched people lose 50+ pounds just by tracking their food and staying in that deficit. It works, but you gotta stick with it."
        else:
            return "Nutrition doesn't need to be rocket science. Lean proteins, plenty of vegetables, some fruits, whole grains, and healthy fats. Eat real food that your great-grandmother would recognize. Control your portions, drink water, and stop eating when you're 80% full. That's literally 90% of it right there. The other 10% is just details that don't matter until you've mastered the basics."
    
    # Weight Management
    elif any(word in query_lower for word in ['weight', 'lose', 'gain', 'fat', 'calories']):
        if 'gain' in query_lower:
            return "Want to gain weight the right way? Eat 300-500 calories above maintenance, focus on nutrient-dense foods, and lift heavy things. Don't just stuff your face with pizza and call it bulking - you want to build muscle, not just get fat. I've seen too many guys go from skinny to skinny-fat because they thought eating everything in sight was the answer. Be smarter than that."
        else:
            return "Weight management is simple math: calories in versus calories out. Create the right deficit or surplus for your goals, be patient with the process, and stay consistent. The scale will follow eventually. But here's the thing - don't live and die by that number. I've had clients gain 5 pounds while dropping 2 dress sizes. Focus on how you feel and how your clothes fit."
    
    # Muscle Building
    elif any(word in query_lower for word in ['muscle', 'strength', 'build', 'gain muscle']):
        return "Building muscle? It all comes down to progressive overload. Every week, you need to challenge your muscles more than the week before - more weight, more reps, more sets, whatever. Eat enough protein (1.8-2.2g per kg), sleep 7-9 hours, and be patient. Muscle building is a marathon, not a sprint. I've been at this for decades, and the guys who succeed are the ones who show up consistently for months and years, not weeks."
    
    # Cardio
    elif any(word in query_lower for word in ['cardio', 'running', 'walking', 'cycling']):
        return "Cardio gets a bad rap, but it's fantastic for heart health and fat loss. Start with 150 minutes of moderate activity per week - that's just 20-25 minutes daily. Find something you actually enjoy, because consistency beats intensity every single time. I'd rather have you walk 20 minutes every day than run your ass off once a week and then skip the next two weeks because you're burnt out."
    
    # Recovery and Rest
    elif any(word in query_lower for word in ['rest', 'recovery', 'sleep', 'sore']):
        return "Recovery is where the magic actually happens. Your muscles don't grow during the workout - they grow during recovery. Sleep 7-9 hours, eat protein after your workouts, and take your rest days seriously. I've seen more people sabotage their progress by not recovering properly than by not training hard enough. Your body needs time to adapt and rebuild."
    
    # Motivation and Goals
    elif any(word in query_lower for word in ['motivation', 'goal', 'start', 'begin']):
        return "Here's the truth about motivation - it gets you started, but habits keep you going. Set small, achievable goals that you can actually hit. Track your progress, celebrate the wins, and don't beat yourself up over the setbacks. And remember this: you don't need to feel motivated to take action. Some of my best workouts happened when I didn't want to be there. Just show up."
    
    # General Health
    elif any(word in query_lower for word in ['health', 'healthy', 'wellness']):
        return "Health is actually pretty simple when you strip away all the noise: move your body regularly, eat real food most of the time, sleep well, manage your stress, and stay connected with people you care about. Don't overcomplicate it with the latest trends and fads. Small, consistent actions compound into massive results over time. I've seen it happen thousands of times."
    
    else:
        return "I'm here to help you crush your fitness goals, whatever they are. Whether you want to lose fat, build muscle, get stronger, or just feel better in your own skin - I've got the experience to guide you there. After training everyone from complete beginners to competitive athletes, I can tell you this: success comes down to consistency and patience. What's your biggest challenge right now? Let's tackle it together."

def on_click_callback(use_voice=False):
    try:
        if use_voice:
            human_prompt = voice_input()
        else:
            human_prompt = st.session_state.get("human_prompt", "")

        if human_prompt:
            if DEEPSEEK_AVAILABLE:
                try:
                    llm_response = get_fitness_response(st.session_state.user_id, human_prompt)
                except Exception as e:
                    # Fallback to simple responses if DeepSeek fails
                    llm_response = simple_fitness_response(human_prompt)
            else:
                # Use simple responses if no DeepSeek available
                llm_response = simple_fitness_response(human_prompt)

            st.session_state.history.append(Message("human", human_prompt))
            st.session_state.history.append(Message("ai", llm_response))
            st.session_state.token_count += len(llm_response.split())

            # Clear input
            st.session_state.human_prompt = ""
    except Exception as e:
        st.error(f"Error: {e}")


def chat_ui():
    if not DEEPSEEK_AVAILABLE:
        st.warning(
            "🤖 Advanced AI features unavailable. Using enhanced basic responses. "
            "Add DEEPSEEK_API_KEY to .env file for fine-tuned AI capabilities."
        )

    initialize_session_state()
    st.title("💪 Your Personal Trainer")
    
    if DEEPSEEK_AVAILABLE:
        st.success("✅ Enhanced AI with fine-tuned fitness knowledge active")
    else:
        st.info("💡 Using comprehensive built-in fitness knowledge")

    # Enhanced CSS for Chat UI
    custom_css = """
    <style>
        .chat-bubble {
            background-color: #f8f9fa;
            padding: 15px 20px;
            border-radius: 15px;
            margin-bottom: 15px;
            max-width: 80%;
            word-wrap: break-word;
            color: #333;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .user-bubble {
            background-color: #e3f2fd;
            margin-left: auto;
            border: 1px solid #bbdefb;
        }
        .ai-bubble {
            background-color: #f1f8e9;
            margin-right: auto;
            border: 1px solid #c8e6c9;
        }
        .chat-container {
            max-height: 400px;
            overflow-y: auto;
            padding: 10px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # Chat Display
    chat_placeholder = st.container()
    prompt_placeholder = st.form("chat-form")

    with chat_placeholder:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for i, chat in enumerate(st.session_state.history):
            if chat.origin == "human":
                st.markdown(f'<div class="chat-bubble user-bubble">**You:** {chat.content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble ai-bubble">**AI Coach:** {chat.content}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with prompt_placeholder:
        st.text_area("Ask me about fitness, nutrition, workouts, or health goals...", key="human_prompt", height=100, placeholder="Example: I'm a beginner and want to start working out at home. Can you help me create a plan?")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            submitted = st.form_submit_button("💬 Send Message", type="primary")
        with col2:
            if st.form_submit_button("🎤 Voice Input"):
                on_click_callback(use_voice=True)
        with col3:
            clear_chat = st.form_submit_button("🗑️ Clear Chat")
        
        if submitted:
            on_click_callback(use_voice=False)
        elif clear_chat:
            st.session_state.history = []
            st.session_state.token_count = 0
            st.rerun()

    # Display conversation stats
    if st.session_state.history:
        st.caption(f"💬 Conversation: {len([m for m in st.session_state.history if m.origin == 'human'])} messages | Tokens: {st.session_state.token_count}")
    
    # Quick action buttons
    st.markdown("**Quick Topics:**")
    col1, col2, col3, col4 = st.columns(4)
    
    quick_query = None
    with col1:
        if st.button("🏃 Workout Plans"):
            quick_query = "Can you create a beginner workout plan for me?"
    with col2:
        if st.button("🥗 Nutrition Guide"):
            quick_query = "What should I eat for muscle building?"
    with col3:
        if st.button("💪 Muscle Building"):
            quick_query = "How do I build muscle effectively?"
    with col4:
        if st.button("🔥 Weight Loss"):
            quick_query = "What's the best approach for weight loss?"
    
    # Process quick query if selected
    if quick_query:
        if DEEPSEEK_AVAILABLE:
            try:
                llm_response = get_fitness_response(st.session_state.user_id, quick_query)
            except Exception as e:
                llm_response = simple_fitness_response(quick_query)
        else:
            llm_response = simple_fitness_response(quick_query)
        
        st.session_state.history.append(Message("human", quick_query))
        st.session_state.history.append(Message("ai", llm_response))
        st.session_state.token_count += len(llm_response.split())
        st.rerun()


if __name__ == "__main__":
    chat_ui()