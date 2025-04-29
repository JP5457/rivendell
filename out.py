import pyaudio
import subprocess


# Audio stream config
FORMAT = pyaudio.paInt16
CHANNELS = 2               # Stereo
RATE = 48000
CHUNK = 1024

def list_input_devices(p):
    print("\nAvailable audio input devices:")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] == 2:
            print(f"  [{i}] {dev['name']}")

def main():
    p = pyaudio.PyAudio()
    list_input_devices(p)

    device_index = int(input("\nEnter the device index to use: "))

    # Open audio input stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK)

    print("Starting stereo audio stream...")

    # Prepare ffmpeg command
    ffmpeg_cmd = [
        'ffmpeg',
        '-f', 's16le',
        '-ac', str(CHANNELS),
        '-ar', str(RATE),
        '-i', '-',
        '-acodec', 'libvorbis',
        '-content_type', 'audio/ogg',
        '-f', 'ogg',
        ICECAST_URL
    ]

    # Launch ffmpeg subprocess
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    try:
        while True:
            data = stream.read(CHUNK)
            process.stdin.write(data)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        process.stdin.close()
        process.wait()

if __name__ == "__main__":
    main()
