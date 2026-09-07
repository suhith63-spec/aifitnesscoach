import os
import time
import threading
import queue
from typing import Optional
import pygame
import io

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

class LowLatencyVoice:
    def __init__(self):
        self.client = None
        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.last_speak_time = 0
        self.min_interval = 2.0  # Minimum seconds between voice outputs
        
        # Initialize pygame mixer for low-latency audio
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Initialize ElevenLabs
        if ELEVENLABS_AVAILABLE:
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if api_key:
                self.client = ElevenLabs(api_key=api_key)
                self.voice_settings = VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.8,
                    style=0.2,
                    use_speaker_boost=True
                )
        
        # Start audio playback thread
        self.playback_thread = threading.Thread(target=self._audio_playback_worker, daemon=True)
        self.playback_thread.start()
    
    def speak(self, text: str, voice_id: str = "pNInz6obpgDQGcFmaJgB"):
        """Queue text for immediate speech synthesis and playback"""
        if not self.client or not self._can_speak():
            return
        
        # Queue for immediate processing
        self.audio_queue.put((text, voice_id))
        self.last_speak_time = time.time()
    
    def _can_speak(self) -> bool:
        """Check if enough time has passed since last speech"""
        return (time.time() - self.last_speak_time) >= self.min_interval
    
    def _audio_playback_worker(self):
        """Background worker for audio synthesis and playback"""
        while True:
            try:
                text, voice_id = self.audio_queue.get(timeout=1)
                
                # Generate audio with optimized settings for speed
                audio_data = self.client.generate(
                    text=text,
                    voice=voice_id,
                    voice_settings=self.voice_settings,
                    model="eleven_turbo_v2"  # Fastest model
                )
                
                # Convert to pygame-compatible format and play immediately
                audio_io = io.BytesIO(audio_data)
                pygame.mixer.music.load(audio_io)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Voice error: {e}")

# Global voice instance
voice_coach = LowLatencyVoice() if ELEVENLABS_AVAILABLE else None

def quick_feedback(exercise: str, rep_count: int, form_score: int, feedback: str):
    """Provide immediate voice feedback with minimal latency"""
    if not voice_coach:
        return
    
    if form_score > 85:
        voice_coach.speak(f"Perfect {exercise} {rep_count}!")
    elif form_score > 70:
        voice_coach.speak(f"Good rep {rep_count}. {feedback}")
    else:
        voice_coach.speak(f"Fix form: {feedback}")