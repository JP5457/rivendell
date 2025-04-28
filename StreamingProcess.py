import multiprocessing
from datetime import datetime
import requests
import sys
import shutil
import os
import subprocess
import pyaudio
import numpy as np
import time

class StreamingProcess(multiprocessing.Process):
    def __init__(self, url, device, queue, id):
        super().__init__()
        self.url = url
        self.device = device
        self.state = "closed"
        self.queue = queue
        self.id = id
        self.exit = multiprocessing.Event()

    def play_stream_ffmpeg(self, stream_url, device_index=None):
        # FFmpeg command to decode audio to 16-bit PCM at 44100 Hz stereo
        ffmpeg_cmd = [
            'ffmpeg', '-i', stream_url,
            '-f', 's16le',
            '-acodec', 'pcm_s16le',
            '-ac', '2',              # stereo
            '-ar', '48000',          
            '-'
        ]

        try:
            print(f"Starting FFmpeg for stream: {stream_url}")
            ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

            audio = pyaudio.PyAudio()
            stream = audio.open(format=pyaudio.paInt16,
                                channels=2,
                                rate=48000,
                                output=True,
                                output_device_index=device_index,
                                frames_per_buffer=1024)

            while True:
                data = ffmpeg_proc.stdout.read(4096)
                states = self.queue.get()
                states[self.id] = "streaming"
                self.queue.put(states)
                if not data:
                    break
                if self.exit.is_set():
                    break
                stream.write(data)
        except Exception as e:
            print("Error playing stream:", e)
        finally:
            try:
                stream.stop_stream()
                stream.close()
                ffmpeg_proc.kill()
                audio.terminate()
            except:
                pass
        
    def run(self):
        print("running")
        while not self.exit.is_set():
            states = self.queue.get()
            states[self.id] = "paused"
            self.queue.put(states)
            try:
                self.play_stream_ffmpeg(self.url, self.device)
            except:
                pass

    def Shutdown(self):
        print("Shutdown initiated")
        self.exit.set()

if __name__ == "__main__":
    url = input("Enter Icecast stream URL: ").strip()
    streamprocess = StreamingProcess("http://audio.ury.org.uk/jukebox", 13, 1, 1)
    print("start")
    streamprocess.start()
    print("waiting 20")
    time.sleep(20)
    streamprocess.Shutdown()
    print("finished")
    