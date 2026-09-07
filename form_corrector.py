import cv2
import numpy as np
import tensorflow as tf
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FormFeedback:
    exercise_type: str
    correction_needed: bool
    feedback_message: str
    confidence: float

class FormCorrector:
    def __init__(self, model_path: str = 'form_correction_model.h5'):
        """Initialize form correction model and parameters.

        Args:
            model_path (str): Path to the TensorFlow model for form correction
        """
        try:
            self.model = tf.keras.models.load_model(model_path)
        except Exception as e:
            print(f"Error loading form correction model: {e}")
            self.model = None

        # Define exercise-specific angle thresholds
        self.angle_thresholds = {
            'push_up': {
                'elbow': (75, 165),  # Min/max angles for proper form
                'shoulder': (160, 180),
                'hip': (160, 180)
            },
            'squat': {
                'knee': (80, 140),
                'hip': (70, 170),
                'ankle': (60, 100)
            },
            'bicep_curl': {
                'elbow': (50, 160),
                'shoulder': (10, 30),
                'wrist': (160, 180)
            },
            'shoulder_press': {
                'elbow': (80, 170),
                'shoulder': (80, 180),
                'wrist': (160, 180)
            }
        }

    def calculate_joint_angles(self, landmarks: np.ndarray) -> Dict[str, float]:
        """Calculate relevant joint angles from pose landmarks.

        Args:
            landmarks (np.ndarray): Array of pose landmarks

        Returns:
            Dict[str, float]: Dictionary of joint angles
        """
        angles = {}
        
        # Calculate key joint angles based on landmark positions
        # Example for elbow angle:
        def get_angle(p1, p2, p3) -> float:
            angle = np.degrees(np.arctan2(p3[1]-p2[1], p3[0]-p2[0]) -
                             np.arctan2(p1[1]-p2[1], p1[0]-p2[0]))
            return angle + 360 if angle < 0 else angle

        # Right side angles
        angles['right_elbow'] = get_angle(
            landmarks[11],  # shoulder
            landmarks[13],  # elbow
            landmarks[15]   # wrist
        )
        
        angles['right_shoulder'] = get_angle(
            landmarks[13],  # elbow
            landmarks[11],  # shoulder
            landmarks[23]   # hip
        )

        angles['right_knee'] = get_angle(
            landmarks[23],  # hip
            landmarks[25],  # knee
            landmarks[27]   # ankle
        )

        # Left side angles (similar calculations)
        angles['left_elbow'] = get_angle(
            landmarks[12],
            landmarks[14],
            landmarks[16]
        )
        
        return angles

    def analyze_form(self, 
                     frame: np.ndarray,
                     landmarks: np.ndarray,
                     exercise_type: str) -> FormFeedback:
        """Analyze exercise form and provide feedback.

        Args:
            frame (np.ndarray): Video frame
            landmarks (np.ndarray): Pose landmarks
            exercise_type (str): Type of exercise being performed

        Returns:
            FormFeedback: Feedback about exercise form
        """
        angles = self.calculate_joint_angles(landmarks)
        thresholds = self.angle_thresholds.get(exercise_type)
        
        if not thresholds:
            return FormFeedback(
                exercise_type=exercise_type,
                correction_needed=False,
                feedback_message="Exercise type not recognized",
                confidence=0.0
            )

        # Analyze angles against thresholds
        feedback = []
        confidence = 1.0

        for joint, (min_angle, max_angle) in thresholds.items():
            right_angle = angles.get(f'right_{joint}')
            left_angle = angles.get(f'left_{joint}')

            if right_angle and (right_angle < min_angle or right_angle > max_angle):
                feedback.append(f"Adjust your right {joint} angle")
                confidence *= 0.8

            if left_angle and (left_angle < min_angle or left_angle > max_angle):
                feedback.append(f"Adjust your left {joint} angle")
                confidence *= 0.8

        # Generate feedback message
        if feedback:
            feedback_message = ". ".join(feedback)
            correction_needed = True
        else:
            feedback_message = "Good form!"
            correction_needed = False

        return FormFeedback(
            exercise_type=exercise_type,
            correction_needed=correction_needed,
            feedback_message=feedback_message,
            confidence=confidence
        )

    def visualize_feedback(self,
                          frame: np.ndarray,
                          feedback: FormFeedback) -> np.ndarray:
        """Visualize form feedback on the frame.

        Args:
            frame (np.ndarray): Video frame
            feedback (FormFeedback): Form feedback data

        Returns:
            np.ndarray: Frame with visualized feedback
        """
        # Add feedback text to frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (0, 0, 255) if feedback.correction_needed else (0, 255, 0)
        
        # Create background for text
        text_size = cv2.getTextSize(feedback.feedback_message, font, 1, 2)[0]
        cv2.rectangle(frame, 
                      (10, 30),
                      (10 + text_size[0], 30 + text_size[1] + 10),
                      (0, 0, 0),
                      cv2.FILLED)
        
        # Add text
        cv2.putText(frame,
                    feedback.feedback_message,
                    (10, 30 + text_size[1]),
                    font,
                    1,
                    color,
                    2,
                    cv2.LINE_AA)

        return frame