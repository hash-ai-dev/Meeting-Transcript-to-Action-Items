import whisper
import os
import torch

class Transcriber:
    def __init__(self, model_size="base"):
        print(f"Loading Whisper model: {model_size}...")
        # Check for GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        try:
            self.model = whisper.load_model(model_size, device=device)
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e
        print("Whisper model loaded.")

    def transcribe(self, audio_path):
        if not os.path.exists(audio_path):
            return ""
            
        print(f"Transcribing {audio_path}...")
        try:
            result = self.model.transcribe(audio_path)
            text = result["text"].strip()
            return text
        except Exception as e:
            print(f"Transcribing error: {e}")
            return ""
