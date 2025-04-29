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

class OutProcess(multiprocessing.Process):
    def __init__(self, url, device, queue, id):
        super().__init__()
        self.url = url
        self.device = device
        self.state = "closed"
        self.queue = queue
        self.id = id
        self.exit = multiprocessing.Event()

    def out_stream(self, stream_url, device):
        p = pyaudio.PyAudio()

        device_index = int(device)

        # Open audio input stream
        stream = p.open(format=pyaudio.paInt16,
                        channels=2,
                        rate=48000,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=1024)

        print("Starting stereo audio stream...")

        # Prepare ffmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 's16le',
            '-ac', str(2),
            '-ar', str(48000),
            '-i', '-',
            '-acodec', 'libvorbis',
            '-content_type', 'audio/ogg',
            '-f', 'ogg',
            stream_url
        ]

        # Launch ffmpeg subprocess
        process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
        states = self.queue.get()
        states[self.id] = "streaming"
        self.queue.put(states)
        try:
            while not self.exit.is_set():
                data = stream.read(1024)
                process.stdin.write(data)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            process.stdin.close()
            process.wait()
        
    def run(self):
        print("running")
        while not self.exit.is_set():
            states = self.queue.get()
            states[self.id] = "paused"
            self.queue.put(states)
            try:
                self.out_stream(self.url, self.device)
            except:
                pass

    def Shutdown(self):
        print("Shutdown initiated")
        self.exit.set()

    