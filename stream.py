import subprocess
import pyaudio
import numpy as np

def list_output_devices():
    p = pyaudio.PyAudio()
    print("Available output devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxOutputChannels'] > 0:
            print(f"{i}: {info['name']}")
    p.terminate()

def play_stream_ffmpeg(stream_url, device_index=None):
    # FFmpeg command to decode audio to 16-bit PCM at 44100 Hz stereo
    ffmpeg_cmd = [
        'ffmpeg', '-i', stream_url,
        '-f', 's16le',
        '-acodec', 'pcm_s16le',
        '-ac', '2',              # stereo
        '-ar', '44100',          # 44.1kHz sample rate
        '-'
    ]

    try:
        print(f"Starting FFmpeg for stream: {stream_url}")
        ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=2,
                            rate=44100,
                            output=True,
                            output_device_index=device_index,
                            frames_per_buffer=1024)

        print("Streaming audio... Press Ctrl+C to stop.")
        while True:
            data = ffmpeg_proc.stdout.read(4096)
            if not data:
                break
            stream.write(data)

    except KeyboardInterrupt:
        print("\nStream stopped by user.")
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

if __name__ == "__main__":
    url = input("Enter Icecast stream URL: ").strip()
    list_output_devices()
    dev = input("Enter output device index (or leave blank for default): ").strip()
    device_index = int(dev) if dev else None
    while True:
        try:
            play_stream_ffmpeg(url, device_index)
        except:
            pass
