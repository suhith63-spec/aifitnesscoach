import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import time
from typing import Dict, Tuple, Optional

class SimpleFormCorrector:
    def __init__(self):
        """Simple form corrector without voice features."""
        
        # Exercise rules for form analysis
        self.exercise_rules = {
            'push_up': {
                'angles': {'elbow': (70, 170), 'shoulder': (150, 180)},
                'feedback': {
                    'elbow_low': "Bend elbows more, aim for 90 degrees",
                    'elbow_high': "Lower body more, elbows too straight",
                    'shoulder_low': "Keep shoulders aligned over wrists"
                }
            },
            'squat': {
                'angles': {'knee': (70, 140), 'hip': (60, 170)},
                'feedback': {
                    'knee_low': "Don't squat too deep",
                    'knee_high': "Squat deeper, thighs parallel",
                    'hip_low': "Push hips back more"
                }
            },
            'bicep_curl': {
                'angles': {'elbow': (30, 160), 'shoulder': (0, 20)},
                'feedback': {
                    'elbow_movement': "Keep elbows at sides",
                    'shoulder_high': "Don't shrug shoulders"
                }
            }
        }
    
    def calculate_angle(self, p1, p2, p3):
        """Calculate angle between three points."""
        v1 = np.array(p1) - np.array(p2)
        v2 = np.array(p3) - np.array(p2)
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        return np.degrees(np.arccos(cos_angle))
    
    def analyze_form(self, landmarks, exercise_type):
        """Analyze exercise form and return feedback."""
        
        if len(landmarks) < 33:
            return {"form_score": 0, "feedback": "Pose not detected", "correction_needed": True}
        
        # Calculate key angles
        angles = {}
        angles['right_elbow'] = self.calculate_angle(landmarks[11], landmarks[13], landmarks[15])
        angles['left_elbow'] = self.calculate_angle(landmarks[12], landmarks[14], landmarks[16])
        angles['right_knee'] = self.calculate_angle(landmarks[23], landmarks[25], landmarks[27])
        angles['left_knee'] = self.calculate_angle(landmarks[24], landmarks[26], landmarks[28])
        
        # Get exercise rules
        rules = self.exercise_rules.get(exercise_type, {})
        if not rules:
            return {"form_score": 50, "feedback": "Exercise not supported", "correction_needed": False}
        
        # Analyze form
        form_score = 100.0
        feedback_messages = []
        
        angle_thresholds = rules.get('angles', {})
        feedback_texts = rules.get('feedback', {})
        
        # Check elbow angles
        if 'elbow' in angle_thresholds:
            min_angle, max_angle = angle_thresholds['elbow']
            avg_elbow = (angles['right_elbow'] + angles['left_elbow']) / 2
            
            if avg_elbow < min_angle:
                feedback_messages.append(feedback_texts.get('elbow_low', 'Adjust elbow angle'))
                form_score -= 20
            elif avg_elbow > max_angle:
                feedback_messages.append(feedback_texts.get('elbow_high', 'Adjust elbow angle'))
                form_score -= 20
        
        # Check knee angles for squats
        if exercise_type == 'squat' and 'knee' in angle_thresholds:
            min_angle, max_angle = angle_thresholds['knee']
            avg_knee = (angles['right_knee'] + angles['left_knee']) / 2
            
            if avg_knee < min_angle:
                feedback_messages.append(feedback_texts.get('knee_low', 'Adjust knee angle'))
                form_score -= 20
            elif avg_knee > max_angle:
                feedback_messages.append(feedback_texts.get('knee_high', 'Adjust knee angle'))
                form_score -= 20
        
        # Generate final feedback
        if feedback_messages:
            feedback = feedback_messages[0]
            correction_needed = True
        else:
            feedback = "Good form!"
            correction_needed = False
        
        return {
            "form_score": max(form_score, 0),
            "feedback": feedback,
            "correction_needed": correction_needed,
            "angles": angles
        }

class SimpleExerciseTrainer:
    def __init__(self):
        """Simple exercise trainer with form correction."""
        
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.form_corrector = SimpleFormCorrector()
        
        # Training state
        self.is_training = False
        self.current_exercise = None
        self.rep_count = 0
        self.session_start_time = None
        self.form_scores = []
    
    def start_session(self, exercise_type):
        """Start exercise session."""
        self.current_exercise = exercise_type.lower().replace(' ', '_')
        self.is_training = True
        self.rep_count = 0
        self.session_start_time = time.time()
        self.form_scores = []
    
    def end_session(self):
        """End exercise session."""
        if not self.is_training:
            return {}
        
        self.is_training = False
        duration = time.time() - self.session_start_time if self.session_start_time else 0
        
        return {
            'exercise': self.current_exercise,
            'total_reps': self.rep_count,
            'duration_minutes': duration / 60,
            'avg_form_score': np.mean(self.form_scores) if self.form_scores else 0
        }
    
    def process_frame(self, frame):
        """Process frame and return analysis."""
        
        if not self.is_training:
            return frame, {}
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose
        results = self.pose.process(rgb_frame)
        
        # Convert back to BGR
        frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            # Draw pose landmarks
            self.mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            # Extract landmarks
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append([landmark.x, landmark.y, landmark.z])
            
            # Analyze form
            form_analysis = self.form_corrector.analyze_form(landmarks, self.current_exercise)
            
            # Add form score to history
            self.form_scores.append(form_analysis['form_score'])
            
            # Add text overlay
            self.add_overlay(frame, form_analysis)
            
            # Return metrics
            metrics = {
                'rep_count': self.rep_count,
                'form_score': form_analysis['form_score'],
                'feedback': form_analysis['feedback'],
                'avg_form_score': np.mean(self.form_scores) if self.form_scores else 0
            }
            
            return frame, metrics
        
        else:
            cv2.putText(frame, "No pose detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame, {}
    
    def add_overlay(self, frame, form_analysis):
        """Add form analysis overlay to frame."""
        
        h, w = frame.shape[:2]
        
        # Form score bar
        score = form_analysis['form_score']
        bar_width = int(300 * (score / 100))
        
        # Background bar
        cv2.rectangle(frame, (10, 10), (310, 40), (50, 50, 50), -1)
        
        # Score bar (color based on score)
        color = (0, 255, 0) if score > 80 else (0, 165, 255) if score > 60 else (0, 0, 255)
        cv2.rectangle(frame, (10, 10), (10 + bar_width, 40), color, -1)
        
        # Score text
        cv2.putText(frame, f"Form Score: {score:.1f}%", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Feedback message
        feedback_color = (0, 0, 255) if form_analysis['correction_needed'] else (0, 255, 0)
        cv2.putText(frame, form_analysis['feedback'], (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, feedback_color, 2)
        
        # Session info
        if self.session_start_time:
            duration = int(time.time() - self.session_start_time)
            minutes, seconds = divmod(duration, 60)
            cv2.putText(frame, f"Time: {minutes:02d}:{seconds:02d}", 
                       (w - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Reps: {self.rep_count}", 
                   (w - 200, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def main():
    st.set_page_config(page_title="Enhanced Fitness Trainer", layout="wide")
    
    st.title("🏋️ Enhanced Fitness AI Trainer")
    st.markdown("*Real-time form correction without voice dependencies*")
    
    # Initialize trainer
    if 'trainer' not in st.session_state:
        st.session_state.trainer = SimpleExerciseTrainer()
    
    trainer = st.session_state.trainer
    
    # Sidebar controls
    st.sidebar.title("🎯 Exercise Controls")
    
    # Exercise selection
    exercise_options = ["Push Up", "Squat", "Bicep Curl"]
    selected_exercise = st.sidebar.selectbox("Select Exercise:", exercise_options)
    
    # Control buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🚀 Start", key="start_btn"):
            trainer.start_session(selected_exercise)
            st.success(f"Started {selected_exercise}!")
    
    with col2:
        if st.button("⏹️ Stop", key="stop_btn"):
            summary = trainer.end_session()
            if summary:
                st.sidebar.json(summary)
    
    # Camera toggle
    camera_enabled = st.sidebar.checkbox("📹 Enable Camera")
    
    # Instructions
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Instructions")
    st.sidebar.info(f"""
    1. Select an exercise
    2. Click Start
    3. Enable camera
    4. Follow the real-time feedback
    5. Click Stop when done
    """)
    
    # Main content area
    if camera_enabled and trainer.is_training:
        st.markdown("### 📺 Live Exercise Analysis")
        
        # Create columns for video and metrics
        col1, col2 = st.columns([3, 1])
        
        with col1:
            video_placeholder = st.empty()
        
        with col2:
            metrics_placeholder = st.empty()
        
        # Camera processing
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("❌ Camera not accessible")
            return
        
        frame_count = 0
        
        while trainer.is_training and camera_enabled:
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Failed to read camera")
                break
            
            # Process every 2nd frame for performance
            if frame_count % 2 == 0:
                processed_frame, metrics = trainer.process_frame(frame)
                
                # Display video
                video_placeholder.image(processed_frame, channels="BGR", use_column_width=True)
                
                # Display metrics
                if metrics:
                    with metrics_placeholder.container():
                        st.metric("🔢 Reps", metrics['rep_count'])
                        
                        form_score = metrics['form_score']
                        st.metric("📊 Form Score", f"{form_score:.1f}%")
                        
                        avg_score = metrics['avg_form_score']
                        st.metric("📈 Average", f"{avg_score:.1f}%")
                        
                        # Feedback
                        if metrics['feedback']:
                            if "Good" in metrics['feedback']:
                                st.success(f"✅ {metrics['feedback']}")
                            else:
                                st.warning(f"⚠️ {metrics['feedback']}")
            
            frame_count += 1
            
            # Break if session ended
            if not trainer.is_training:
                break
        
        cap.release()
    
    elif not trainer.is_training:
        st.info("👆 Select an exercise and click Start to begin training")
    
    elif not camera_enabled:
        st.info("📹 Enable camera to see live analysis")

if __name__ == "__main__":
    main()