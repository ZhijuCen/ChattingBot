
from .consts import SAMPLE_RATE, CHANNELS, CHUNK, FORMAT

import pyaudio
import numpy as np

import wave
from hashlib import sha384
from pathlib import Path
from typing import List, Tuple


class SpeechRecoder:

    def __init__(self, save_dir: Path, volume_threshold: float = 0.3) -> None:
        self.save_dir = save_dir.absolute()
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.volume_threshold = volume_threshold

        self.audio = pyaudio.PyAudio()
        self.frames: List[bytes] = list()
        self.stream: pyaudio.Stream = None
    
    def open_stream(self):
        if self.stream is None:
            self.stream = self.audio.open(
                SAMPLE_RATE, CHANNELS, FORMAT,
                input=True, frames_per_buffer=CHUNK)
        elif self.stream.is_stopped():
            self.start_stream()
    
    def pause_stream(self):
        """When to pause stream: playing music or speech."""
        if self.stream is not None:
            self.stream.stop_stream()
    
    def start_stream(self):
        if self.stream is not None:
            self.stream.start_stream()
    
    def close(self):
        if self.stream is not None:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
    
    def append_frame(self) -> bool:
        ret = False
        if self.stream is not None and self.stream.is_active():
            frame = list()
            for _ in range(0, int(SAMPLE_RATE / CHUNK * 0.5)):
                data = self.stream.read(CHUNK)
                frame.append(data)
            frame_full = b"".join(frame)
            frame_array = np.frombuffer(frame_full, dtype=np.int16)
            if np.max(np.abs(frame_array)) >= \
                    self.volume_threshold * np.iinfo(np.int16).max:
                self.frames.append(frame_full)
                ret = True
        return ret
    
    def try_save_speech(self) -> Tuple[bool, str]:
        flag = False
        fpath = str()
        if self.frames:
            data = b"".join(self.frames)
            fname = sha384(data).hexdigest()
            fpath = str(self.save_dir / f"{fname}.wav")
            wf: wave.Wave_write = wave.open(fpath, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(data)
            wf.close()
            self.frames.clear()
            flag = True
        return flag, fpath
