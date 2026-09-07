import time

class VoiceProcessor:
    def __init__(self, wake_word="hey max"):
        self.wake_word = wake_word
        self.listening = False
        
    def start_listening(self, callback):
        self.listening = True
        
    def stop_listening(self):
        self.listening = False
        
    def speak(self, text):
        print(f"Voice: {text}")