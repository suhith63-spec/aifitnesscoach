import cv2
import numpy as np
import threading
import time
from typing import Optional, Tuple
from voice_processor import VoiceProcessor

class ExerciseCoach:
    def __init__(self):
        """Initialize the AI exercise coach with voice and form correction capabilities."""
        self.voice_processor = VoiceProcessor(wake_word="hey max")
        # self.form_corrector = FormCorrector()  # Disabled for now
        self.current_exercise: Optional[str] = None
        self.rep_count = 0
        self.last_feedback_time = 0
        self.feedback_cooldown = 3.0  # Seconds between voice feedback
        
        # Start voice processing in a separate thread
        self.voice_processor.start_listening(self.handle_voice_command)

    def handle_voice_command(self, command: str):
        """Process voice commands during workout.

        Args:
            command (str): Transcribed voice command
        """
        command = command.lower()
        
        if "how many" in command and "reps" in command:
            self.voice_processor.speak(f"You have completed {self.rep_count} repetitions")
        
        elif "what exercise" in command:
            if self.current_exercise:
                self.voice_processor.speak(f"You are currently doing {self.current_exercise}")
            else:
                self.voice_processor.speak("No exercise is currently selected")
        
        elif "stop" in command:
            self.voice_processor.speak("Stopping exercise tracking")
            self.stop()

    def provide_form_feedback(self, feedback_message: str):
        """Provide voice feedback about exercise form.

        Args:
            feedback_message (str): Feedback message to convert to speech
        """
        current_time = time.time()
        if current_time - self.last_feedback_time >= self.feedback_cooldown:
            self.voice_processor.speak(feedback_message)
            self.last_feedback_time = current_time

    def process_frame(self, frame: np.ndarray, landmarks: np.ndarray) -> Tuple[np.ndarray, str]:
        """Process a video frame and provide real-time feedback.

        Args:
            frame (np.ndarray): Video frame to process
            landmarks (np.ndarray): Pose landmarks from MediaPipe

        Returns:
            Tuple[np.ndarray, str]: Processed frame and feedback message
        """
        if self.current_exercise is None:
            return frame, "No exercise selected"

        # Simple feedback for now
        feedback_message = f"Tracking {self.current_exercise}"
        return frame, feedback_message

    def start_exercise(self, exercise_type: str):
        """Start tracking a new exercise.

        Args:
            exercise_type (str): Type of exercise to track
        """
        self.current_exercise = exercise_type
        self.rep_count = 0
        self.voice_processor.speak(f"Starting {exercise_type} tracking. Say 'Hey Max' for assistance.")

    def increment_reps(self):
        """Increment repetition counter and provide feedback."""
        self.rep_count += 1
        if self.rep_count % 5 == 0:  # Provide feedback every 5 reps
            self.voice_processor.speak(f"Great job! You've completed {self.rep_count} repetitions")

    def stop(self):
        """Stop exercise tracking and cleanup resources."""
        self.voice_processor.stop_listening()
        self.current_exercise = None
        self.rep_count = 0