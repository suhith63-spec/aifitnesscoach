import cv2
import numpy as np
import mediapipe as mp
import streamlit as st
import time
from enhanced_form_corrector import EnhancedFormCorrector
from typing import Optional, Tuple
import threading

class EnhancedExerciseTrainer:
    def __init__(self):
        """Enhanced exercise trainer with real-time form correction."""
        
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,  # Higher accuracy
            enable_segmentation=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Initialize form corrector
        self.form_corrector = EnhancedFormCorrector()
        
        # Exercise state
        self.current_exercise = None
        self.rep_count = 0
        self.session_start_time = None
        self.is_training = False
        
        # Performance metrics
        self.form_scores = []
        self.rep_times = []
        
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for better pose detection under various conditions."""
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Enhance contrast and brightness
        lab = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels and convert back
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        return enhanced
    
    def extract_pose_landmarks(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Extract pose landmarks with enhanced accuracy."""
        
        # Preprocess frame
        processed_frame = self.preprocess_frame(frame)
        
        # Get pose landmarks
        results = self.pose.process(processed_frame)
        
        if results.pose_landmarks:
            # Extract landmark coordinates
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append([landmark.x, landmark.y, landmark.z, landmark.visibility])
            
            return np.array(landmarks)
        
        return None
    
    def start_exercise_session(self, exercise_type: str):
        """Start a new exercise session."""
        
        self.current_exercise = exercise_type.lower().replace(' ', '_')
        self.rep_count = 0
        self.session_start_time = time.time()
        self.is_training = True
        self.form_scores = []
        self.rep_times = []
        
        # Voice announcement
        self.form_corrector.generate_voice_feedback(
            f"Starting {exercise_type} session. I'll guide your form in real-time."
        )
    
    def process_frame_realtime(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        """Process frame with real-time form analysis."""
        
        if not self.is_training or not self.current_exercise:
            return frame, {}
        
        # Extract pose landmarks
        landmarks = self.extract_pose_landmarks(frame)
        
        if landmarks is None:
            cv2.putText(frame, "No pose detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame, {}
        
        # Analyze form
        feedback = self.form_corrector.analyze_form_realtime(
            frame, landmarks, self.current_exercise
        )
        
        # Track repetitions
        rep_completed = self.form_corrector.track_rep_completion(
            feedback.joint_angles, self.current_exercise
        )
        
        if rep_completed:
            self.rep_count += 1
            self.form_scores.append(feedback.form_score)
            
            if len(self.rep_times) > 0:
                rep_time = time.time() - self.rep_times[-1]
            else:
                rep_time = time.time() - self.session_start_time
            
            self.rep_times.append(time.time())
        
        # Visualize feedback
        frame = self.form_corrector.visualize_enhanced_feedback(frame, feedback, landmarks)
        
        # Add session info
        self.add_session_info(frame)
        
        # Return metrics
        metrics = {
            'rep_count': self.rep_count,
            'form_score': feedback.form_score,
            'exercise': self.current_exercise,
            'feedback': feedback.feedback_message,
            'avg_form_score': np.mean(self.form_scores) if self.form_scores else 0
        }
        
        return frame, metrics
    
    def add_session_info(self, frame: np.ndarray):
        """Add session information to frame."""
        
        h, w = frame.shape[:2]
        
        # Session duration
        if self.session_start_time:
            duration = int(time.time() - self.session_start_time)
            minutes, seconds = divmod(duration, 60)
            
            cv2.putText(frame, f"Time: {minutes:02d}:{seconds:02d}", 
                       (w - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Rep count
        cv2.putText(frame, f"Reps: {self.rep_count}", 
                   (w - 200, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Average form score
        if self.form_scores:
            avg_score = np.mean(self.form_scores)
            cv2.putText(frame, f"Avg Score: {avg_score:.1f}%", 
                       (w - 200, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Exercise name
        cv2.putText(frame, f"Exercise: {self.current_exercise.replace('_', ' ').title()}", 
                   (w - 300, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def end_session(self) -> dict:
        """End exercise session and return summary."""
        
        if not self.is_training:
            return {}
        
        self.is_training = False
        duration = time.time() - self.session_start_time if self.session_start_time else 0
        
        summary = {
            'exercise': self.current_exercise,
            'total_reps': self.rep_count,
            'duration_minutes': duration / 60,
            'avg_form_score': np.mean(self.form_scores) if self.form_scores else 0,
            'best_form_score': max(self.form_scores) if self.form_scores else 0,
            'form_consistency': np.std(self.form_scores) if len(self.form_scores) > 1 else 0
        }
        
        # Voice summary
        self.form_corrector.generate_voice_feedback(
            f"Session complete! {self.rep_count} reps with {summary['avg_form_score']:.1f}% average form score."
        )
        
        return summary
    
    def get_exercise_instructions(self, exercise_type: str) -> str:
        """Get detailed exercise instructions."""
        
        instructions = {
            'push_up': """
            Push-Up Instructions:
            1. Start in plank position, hands shoulder-width apart
            2. Keep body in straight line from head to heels
            3. Lower body until chest nearly touches ground
            4. Push back up to starting position
            5. Keep core engaged throughout movement
            """,
            
            'squat': """
            Squat Instructions:
            1. Stand with feet shoulder-width apart
            2. Lower body by pushing hips back and bending knees
            3. Keep chest up and knees behind toes
            4. Descend until thighs parallel to ground
            5. Drive through heels to return to standing
            """,
            
            'bicep_curl': """
            Bicep Curl Instructions:
            1. Stand with feet hip-width apart, weights in hands
            2. Keep elbows close to your sides
            3. Curl weights up by contracting biceps
            4. Squeeze at the top, then slowly lower
            5. Keep wrists straight and core engaged
            """,
            
            'shoulder_press': """
            Shoulder Press Instructions:
            1. Stand with feet hip-width apart, weights at shoulder height
            2. Press weights straight up overhead
            3. Keep core tight and avoid arching back
            4. Lower weights back to shoulder height with control
            5. Maintain neutral wrist position
            """
        }
        
        return instructions.get(exercise_type.lower().replace(' ', '_'), 
                              "Instructions not available for this exercise.")

def create_enhanced_trainer_ui():
    """Create Streamlit UI for enhanced exercise trainer."""
    
    st.title("🏋️ Enhanced AI Exercise Trainer")
    st.markdown("Real-time form correction with voice feedback")
    
    # Initialize trainer
    if 'trainer' not in st.session_state:
        st.session_state.trainer = EnhancedExerciseTrainer()
    
    trainer = st.session_state.trainer
    
    # Exercise selection
    exercise_options = ["Push Up", "Squat", "Bicep Curl", "Shoulder Press"]
    selected_exercise = st.selectbox("Select Exercise:", exercise_options)
    
    # Show instructions
    with st.expander("Exercise Instructions"):
        st.text(trainer.get_exercise_instructions(selected_exercise))
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Start Session"):
            trainer.start_exercise_session(selected_exercise)
            st.success(f"Started {selected_exercise} session!")
    
    with col2:
        if st.button("End Session"):
            summary = trainer.end_session()
            if summary:
                st.json(summary)
    
    with col3:
        camera_enabled = st.checkbox("Enable Camera")
    
    # Camera feed
    if camera_enabled and trainer.is_training:
        stframe = st.empty()
        
        cap = cv2.VideoCapture(0)
        
        while trainer.is_training:
            ret, frame = cap.read()
            if not ret:
                st.error("Camera not accessible")
                break
            
            # Process frame
            processed_frame, metrics = trainer.process_frame_realtime(frame)
            
            # Display frame
            stframe.image(processed_frame, channels="BGR", use_column_width=True)
            
            # Display metrics
            if metrics:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Reps", metrics['rep_count'])
                with col2:
                    st.metric("Form Score", f"{metrics['form_score']:.1f}%")
                with col3:
                    st.metric("Avg Score", f"{metrics['avg_form_score']:.1f}%")
        
        cap.release()

if __name__ == "__main__":
    create_enhanced_trainer_ui()