
from .consts import CHUNK

import pyaudio
import wave


class SpeechPlayer:

    def __init__(self):
        self.audio = pyaudio.PyAudio()
    
    def close(self):
        self.audio.terminate()

    def play_speech(self, wave_path: str) -> bool:
        ret = False
        try:
            wf: wave.Wave_read = wave.open(wave_path, "rb")
            stream = self.audio.open(
                wf.getframerate(),
                wf.getnchannels(),
                self.audio.get_format_from_width(wf.getsampwidth()),
                output=True)
            data: bytes = wf.readframes(CHUNK)
            while data:
                stream.write(data)
                data: bytes = wf.readframes(CHUNK)
            stream.stop_stream()
            stream.close()
            ret = True
        except Exception as e:
            print(e)
        return ret
