from OutProcess import OutProcess
import multiprocessing
import random
import time
import sys
import os
import pyaudio
from datetime import datetime


class OutManager:
    def __init__(self):
        self.threads = {}
        self.states = {}
        self.queue = multiprocessing.Queue()
        self.queue.put(self.states)

    def StartStreaming(self, url, device, devicename):
        for key in self.threads:
            if self.threads[key]["url"] == url:
                return key
        id = random.randint(1,65536)
        while id in self.threads:
            id = random.randint(1,65536)
        newprocess = OutProcess(url, device, self.queue, id)
        self.threads[id] = {"process": newprocess, "url": url, "device": device, "devicename": devicename}
        process = self.threads[id]["process"]
        process.start()
        return id
        
    def GetState(self, id):
        try:
            if id in self.threads:
                return self.states[id]
            else:
                return "closed"
        except:
            return "closed"

    def GetAllStates(self):
        toret = []
        for i in self.threads:
            info = {'id': i, "url": self.threads[i]["url"], "state": self.GetState(i), "devicename": self.threads[i]["devicename"], "stop": "/stopout/"+str(i)}
            toret.append(info)
        return toret

    def UpdateStates(self):
        try:
            self.states = self.queue.get()
            self.queue.put(self.states)
        except:
            pass

    def StopStreaming(self, id):
        try:
            self.threads[id]["process"].Shutdown()
            self.threads[id]["process"].join()
            del self.threads[id]
            time.sleep(1)
            return "shutdown"
        except:
            return "error"
        
    def GetAudioDevicesold(self):
        p = pyaudio.PyAudio()
        toret = []
        print("Available output devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxOutputChannels'] == 2:
                if "voice" not in info["name"].lower():
                    toret.append({"index": i, "name": info["name"]})
        p.terminate()
        return toret
    
    def GetAudioDevices(self):
        p = pyaudio.PyAudio()
        waveout_hostapi_index = None

        # Find WaveOut host API index
        for i in range(p.get_host_api_count()):
            hostapi_info = p.get_host_api_info_by_index(i)
            print(hostapi_info)
            if 'WASAPI' in hostapi_info['name'].upper():
                waveout_hostapi_index = i
                break

        if waveout_hostapi_index is None:
            print("WaveOut host API not found.")
            p.terminate()
            return []

        toret = []
        seen = set()

        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['hostApi'] == waveout_hostapi_index and info['maxInputChannels'] == 2:
                name = info['name']
                if "voice" not in name.lower() and name not in seen:
                    toret.append({"index": i, "name": name})
                    seen.add(name)

        p.terminate()
        return toret