import cv2
import numpy as np
import tensorflow as tf
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
import time
import threading
from elevenlabs import generate, stream, set_api_key
import os

@dataclass
class FormFeedback:
    exercise_type: str
    correction_needed: bool
    feedback_message: str
    voice_command: str
    confidence: float
    joint_angles: Dict[str, float]
    form_score: float

class EnhancedFormCorrector:
    def __init__(self, model_path: str = 'final_forthesis_bidirectionallstm_and_encoders_exercise_classifier_model.h5'):
        """Enhanced form corrector with real-time feedback and voice commands."""
        
        # Load BiLSTM model
        try:
            self.model = tf.keras.models.load_model(model_path)
        except Exception as e:
            print(f"Model loading error: {e}")
            self.model = None
        
        # Initialize ElevenLabs
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if api_key:
            set_api_key(api_key)
        
        # Legendary-Level Exercise Rules with Expert Feedback
        self.exercise_rules = {
            'push_up': {
                'angles': {
                    'elbow': (70, 170),
                    'shoulder': (150, 180),
                    'hip': (160, 180),
                    'knee': (170, 180)
                },
                'feedback': {
                    'elbow_low': "Go deeper! Chest to floor!",
                    'elbow_high': "Lock out those arms at the top!",
                    'hip_low': "Don't let those hips sag! Core tight!",
                    'shoulder_low': "Shoulders over wrists! Stay stacked!"
                }
            },
            'squat': {
                'angles': {
                    'knee': (70, 140),
                    'hip': (60, 170),
                    'ankle': (50, 100),
                    'back': (160, 180)
                },
                'feedback': {
                    'knee_low': "Too deep! Protect your knees!",
                    'knee_high': "Lower! Thighs parallel to the ground!",
                    'hip_low': "Sit back! Weight in your heels!",
                    'back_low': "Chest up! Proud posture!"
                }
            },
            'bicep_curl': {
                'angles': {
                    'elbow': (30, 160),
                    'shoulder': (0, 20),
                    'wrist': (160, 180)
                },
                'feedback': {
                    'elbow_movement': "Lock those elbows to your sides! No swinging!",
                    'shoulder_high': "Relax your shoulders! Isolate the biceps!",
                    'wrist_bent': "Wrists straight! Grip it hard!"
                }
            },
            'shoulder_press': {
                'angles': {
                    'elbow': (80, 180),
                    'shoulder': (80, 180),
                    'wrist': (160, 180)
                },
                'feedback': {
                    'elbow_low': "Push all the way up! Full extension!",
                    'shoulder_unstable': "Control the weight! Core engaged!",
                    'wrist_bent': "Knuckles to the ceiling! Strong wrists!"
                }
            }
        }
        
        # Voice feedback cooldown
        self.last_voice_time = 0
        self.voice_cooldown = 3.0
        
        # Form tracking
        self.form_history = []
        self.rep_count = 0

    def calculate_enhanced_angles(self, landmarks: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive joint angles with improved accuracy."""
        
        def angle_3d(p1, p2, p3):
            """Calculate 3D angle between three points."""
            v1 = np.array(p1) - np.array(p2)
            v2 = np.array(p3) - np.array(p2)
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            return np.degrees(np.arccos(cos_angle))
        
        angles = {}
        
        # Right side angles
        angles['right_elbow'] = angle_3d(landmarks[11], landmarks[13], landmarks[15])
        angles['right_shoulder'] = angle_3d(landmarks[13], landmarks[11], landmarks[23])
        angles['right_knee'] = angle_3d(landmarks[23], landmarks[25], landmarks[27])
        angles['right_hip'] = angle_3d(landmarks[11], landmarks[23], landmarks[25])
        
        # Left side angles
        angles['left_elbow'] = angle_3d(landmarks[12], landmarks[14], landmarks[16])
        angles['left_shoulder'] = angle_3d(landmarks[14], landmarks[12], landmarks[24])
        angles['left_knee'] = angle_3d(landmarks[24], landmarks[26], landmarks[28])
        angles['left_hip'] = angle_3d(landmarks[12], landmarks[24], landmarks[26])
        
        # Spine alignment
        angles['spine'] = angle_3d(landmarks[11], landmarks[23], landmarks[25])
        
        return angles

    def analyze_exercise_phase(self, angles: Dict[str, float], exercise: str) -> str:
        """Determine exercise phase (up/down/hold) for better feedback."""
        
        if exercise == 'push_up':
            elbow_angle = (angles.get('right_elbow', 0) + angles.get('left_elbow', 0)) / 2
            if elbow_angle < 100:
                return 'down'
            elif elbow_angle > 150:
                return 'up'
            else:
                return 'transition'
                
        elif exercise == 'squat':
            knee_angle = (angles.get('right_knee', 0) + angles.get('left_knee', 0)) / 2
            if knee_angle < 110:
                return 'down'
            elif knee_angle > 150:
                return 'up'
            else:
                return 'transition'
        
        return 'unknown'

    def generate_voice_feedback(self, feedback_message: str):
        """Generate voice feedback using ElevenLabs."""
        current_time = time.time()
        if current_time - self.last_voice_time < self.voice_cooldown:
            return
        
        try:
            audio = generate(
                text=feedback_message,
                voice="Arnold",
                model="eleven_monolingual_v1"
            )
            
            # Play audio in separate thread
            def play_audio():
                stream(audio)
            
            threading.Thread(target=play_audio, daemon=True).start()
            self.last_voice_time = current_time
            
        except Exception as e:
            print(f"Voice generation error: {e}")

    def analyze_form_realtime(self, frame: np.ndarray, landmarks: np.ndarray, exercise_type: str) -> FormFeedback:
        """Real-time form analysis with comprehensive feedback."""
        
        angles = self.calculate_enhanced_angles(landmarks)
        rules = self.exercise_rules.get(exercise_type, {})
        
        if not rules:
            return FormFeedback(
                exercise_type=exercise_type,
                correction_needed=False,
                feedback_message="Exercise not supported",
                voice_command="",
                confidence=0.0,
                joint_angles=angles,
                form_score=0.0
            )
        
        # Analyze form
        corrections = []
        form_score = 100.0
        phase = self.analyze_exercise_phase(angles, exercise_type)
        
        angle_thresholds = rules.get('angles', {})
        feedback_messages = rules.get('feedback', {})
        
        # Check each joint angle
        for joint, (min_angle, max_angle) in angle_thresholds.items():
            right_angle = angles.get(f'right_{joint}')
            left_angle = angles.get(f'left_{joint}')
            
            # Check right side
            if right_angle:
                if right_angle < min_angle:
                    corrections.append(feedback_messages.get(f'{joint}_low', f"Adjust right {joint}"))
                    form_score -= 15
                elif right_angle > max_angle:
                    corrections.append(feedback_messages.get(f'{joint}_high', f"Adjust right {joint}"))
                    form_score -= 15
            
            # Check left side
            if left_angle:
                if left_angle < min_angle:
                    corrections.append(feedback_messages.get(f'{joint}_low', f"Adjust left {joint}"))
                    form_score -= 15
                elif left_angle > max_angle:
                    corrections.append(feedback_messages.get(f'{joint}_high', f"Adjust left {joint}"))
                    form_score -= 15
        
        # Check symmetry
        for joint in ['elbow', 'knee', 'shoulder']:
            right_angle = angles.get(f'right_{joint}')
            left_angle = angles.get(f'left_{joint}')
            
            if right_angle and left_angle:
                asymmetry = abs(right_angle - left_angle)
                if asymmetry > 20:
                    corrections.append(f"Balance both sides, {joint} asymmetry detected")
                    form_score -= 10
        
        # Generate feedback
        if corrections:
            feedback_message = corrections[0]  # Primary correction
            voice_command = f"Correction: {feedback_message}"
            correction_needed = True
        else:
            # Random encouraging phrases for "Legendary" feel
            encouragements = [
                "Perfect form! Keep going!",
                "That's it! Feel the burn!",
                "Solid rep! You're crushing it!",
                "Light weight, baby!",
                "Excellent control!",
                "Stay strong! Looking legendary!"
            ]
            import random
            feedback_message = f"{random.choice(encouragements)} {phase.title()} phase"
            voice_command = random.choice(encouragements)
            correction_needed = False
        
        # Generate voice feedback for corrections
        if correction_needed and form_score < 70:
            self.generate_voice_feedback(voice_command)
        
        return FormFeedback(
            exercise_type=exercise_type,
            correction_needed=correction_needed,
            feedback_message=feedback_message,
            voice_command=voice_command,
            confidence=min(form_score / 100.0, 1.0),
            joint_angles=angles,
            form_score=max(form_score, 0.0)
        )

    def visualize_enhanced_feedback(self, frame: np.ndarray, feedback: FormFeedback, landmarks: np.ndarray) -> np.ndarray:
        """Enhanced visualization with joint angles and form score."""
        
        # Draw pose landmarks
        self.draw_pose_landmarks(frame, landmarks)
        
        # Form score bar
        score_width = int(300 * (feedback.form_score / 100))
        cv2.rectangle(frame, (10, 10), (310, 40), (50, 50, 50), -1)
        
        score_color = (0, 255, 0) if feedback.form_score > 80 else (0, 165, 255) if feedback.form_score > 60 else (0, 0, 255)
        cv2.rectangle(frame, (10, 10), (10 + score_width, 40), score_color, -1)
        
        cv2.putText(frame, f"Form Score: {feedback.form_score:.1f}%", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Feedback message
        y_pos = 100
        for i, line in enumerate(feedback.feedback_message.split('. ')):
            color = (0, 0, 255) if feedback.correction_needed else (0, 255, 0)
            cv2.putText(frame, line, (10, y_pos + i * 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Joint angles display
        angle_y = 200
        for joint, angle in feedback.joint_angles.items():
            cv2.putText(frame, f"{joint}: {angle:.1f}°", (10, angle_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            angle_y += 20
        
        return frame

    def draw_pose_landmarks(self, frame: np.ndarray, landmarks: np.ndarray):
        """Draw pose landmarks and connections."""
        
        # Define connections
        connections = [
            (11, 13), (13, 15),  # Right arm
            (12, 14), (14, 16),  # Left arm
            (11, 12),            # Shoulders
            (11, 23), (12, 24),  # Torso
            (23, 24),            # Hips
            (23, 25), (25, 27),  # Right leg
            (24, 26), (26, 28)   # Left leg
        ]
        
        h, w = frame.shape[:2]
        
        # Draw connections
        for start, end in connections:
            if start < len(landmarks) and end < len(landmarks):
                start_point = (int(landmarks[start][0] * w), int(landmarks[start][1] * h))
                end_point = (int(landmarks[end][0] * w), int(landmarks[end][1] * h))
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)
        
        # Draw landmarks
        for i, landmark in enumerate(landmarks):
            x, y = int(landmark[0] * w), int(landmark[1] * h)
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

    def track_rep_completion(self, angles: Dict[str, float], exercise: str) -> bool:
        """Track repetition completion based on movement patterns."""
        
        phase = self.analyze_exercise_phase(angles, exercise)
        
        # Simple rep counting logic
        if len(self.form_history) > 10:
            recent_phases = [self.analyze_exercise_phase(h, exercise) for h in self.form_history[-10:]]
            
            # Look for complete cycle: up -> down -> up
            if (recent_phases[-3:] == ['up', 'down', 'up'] or 
                recent_phases[-3:] == ['down', 'up', 'down']):
                self.rep_count += 1
                self.generate_voice_feedback(f"Rep {self.rep_count} completed!")
                return True
        
        self.form_history.append(angles)
        return False