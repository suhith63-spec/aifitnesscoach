import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import os
from elevenlabs import generate, stream, set_api_key
import threading
import time

# Initialize ElevenLabs
api_key = os.getenv("ELEVENLABS_API_KEY")
if api_key:
    set_api_key(api_key)

class VoiceTrainer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.last_voice_time = 0
        
    def speak(self, text):
        if time.time() - self.last_voice_time < 3:  # 3 second cooldown
            return
        try:
            audio = generate(text=text, voice="Arnold", model="eleven_monolingual_v1")
            threading.Thread(target=lambda: stream(audio), daemon=True).start()
            self.last_voice_time = time.time()
        except:
            pass
    
    def analyze_form(self, landmarks, exercise):
        if len(landmarks) < 33:
            return {"score": 0, "feedback": "No pose detected"}
        
        # Calculate elbow angle
        right_elbow = self.calculate_angle(landmarks[11], landmarks[13], landmarks[15])
        left_elbow = self.calculate_angle(landmarks[12], landmarks[14], landmarks[16])
        avg_elbow = (right_elbow + left_elbow) / 2
        
        if exercise == "push_up":
            if avg_elbow < 70:
                self.speak("Bend your elbows more, aim for ninety degrees")
                return {"score": 60, "feedback": "Bend elbows more"}
            elif avg_elbow > 170:
                self.speak("Lower your body more, get closer to the ground")
                return {"score": 60, "feedback": "Lower body more"}
            else:
                return {"score": 100, "feedback": "Perfect form!"}
        
        elif exercise == "squat":
            right_knee = self.calculate_angle(landmarks[23], landmarks[25], landmarks[27])
            left_knee = self.calculate_angle(landmarks[24], landmarks[26], landmarks[28])
            avg_knee = (right_knee + left_knee) / 2
            
            if avg_knee < 70:
                self.speak("Don't squat too deep, stop at ninety degrees")
                return {"score": 60, "feedback": "Too deep"}
            elif avg_knee > 140:
                self.speak("Squat deeper, get your thighs parallel to the ground")
                return {"score": 60, "feedback": "Squat deeper"}
            else:
                return {"score": 100, "feedback": "Perfect squat!"}
        
        return {"score": 80, "feedback": "Good form"}
    
    def calculate_angle(self, p1, p2, p3):
        v1 = np.array(p1) - np.array(p2)
        v2 = np.array(p3) - np.array(p2)
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

def main():
    st.title("🎤 ElevenLabs Voice Fitness Trainer")
    
    if not api_key:
        st.error("❌ ElevenLabs API key not found. Check your .env file.")
        return
    
    if 'trainer' not in st.session_state:
        st.session_state.trainer = VoiceTrainer()
    
    trainer = st.session_state.trainer
    
    exercise = st.selectbox("Exercise:", ["Push Up", "Squat"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start Voice Training"):
            trainer.speak(f"Starting {exercise} with voice feedback")
            st.success("Voice training started!")
    
    with col2:
        camera_enabled = st.checkbox("📹 Enable Camera")
    
    if camera_enabled:
        cap = cv2.VideoCapture(0)
        stframe = st.empty()
        
        if not cap.isOpened():
            st.error("❌ Camera not accessible")
            return
        
        while camera_enabled:
            ret, frame = cap.read()
            if not ret:
                break
                
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = trainer.pose.process(rgb_frame)
            frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                trainer.mp_drawing.draw_landmarks(frame, results.pose_landmarks, trainer.mp_pose.POSE_CONNECTIONS)
                
                landmarks = [[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark]
                analysis = trainer.analyze_form(landmarks, exercise.lower().replace(' ', '_'))
                
                # Add score bar
                score = analysis['score']
                bar_width = int(300 * (score / 100))
                cv2.rectangle(frame, (10, 10), (310, 40), (50, 50, 50), -1)
                color = (0, 255, 0) if score > 80 else (0, 165, 255) if score > 60 else (0, 0, 255)
                cv2.rectangle(frame, (10, 10), (10 + bar_width, 40), color, -1)
                
                cv2.putText(frame, f"Score: {score}%", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, analysis['feedback'], (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            else:
                cv2.putText(frame, "No pose detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            stframe.image(frame, channels="BGR", use_column_width=True)
            
            # Break if camera disabled
            if not st.session_state.get('camera_enabled', True):
                break
        
        cap.release()

if __name__ == "__main__":
    main()