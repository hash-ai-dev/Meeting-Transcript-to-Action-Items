import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
import time
import os
import queue

class AudioRecorder:
    def __init__(self, sample_rate=16000, chunk_duration=30):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration # Seconds per chunk
        self.recording = False
        self.frames = []
        self.audio_queue = queue.Queue() # Queue to pass filenames to Transcriber
        self.thread = None
        
        # Ensure temp directory exists
        self.temp_dir = os.path.join(os.path.dirname(__file__), "temp_audio")
        os.makedirs(self.temp_dir, exist_ok=True)

    def start(self):
        if self.recording:
            return
        self.recording = True
        self.frames = []
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.start()
        print("Recording started...")

    def stop(self):
        if not self.recording:
            return
        self.recording = False
        if self.thread:
            self.thread.join()
        print("Recording stopped.")

    def _record_loop(self):
        # We record in small blocks and append to a buffer
        # When buffer exceeds chunk_duration, we save to file
        
        start_time = time.time()
        current_chunk = []
        
        # Callback for sounddevice
        def callback(indata, frames, time, status):
            if status:
                print(status)
            current_chunk.append(indata.copy())

        with sd.InputStream(samplerate=self.sample_rate, channels=1, callback=callback):
            while self.recording:
                sd.sleep(1000) # Sleep 1 second
                
                # Check if we have enough data for a chunk
                duration = time.time() - start_time
                if duration >= self.chunk_duration:
                    self._save_chunk(current_chunk)
                    current_chunk = []
                    start_time = time.time()
            
            # Save remaining data
            if current_chunk:
                self._save_chunk(current_chunk)

    def _save_chunk(self, chunk_data):
        if not chunk_data:
            return
            
        filename = os.path.join(self.temp_dir, f"chunk_{int(time.time())}.wav")
        # Concatenate all blocks in the chunk
        data = np.concatenate(chunk_data, axis=0)
        
        # Convert to 16-bit PCM for generic compatibility
        data_int16 = (data * 32767).astype(np.int16)
        
        wav.write(filename, self.sample_rate, data_int16)
        print(f"Saved audio chunk: {filename}")
        self.audio_queue.put(filename)

    def get_next_audio_file(self):
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return None
