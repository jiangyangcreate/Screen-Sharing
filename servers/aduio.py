import pyaudio


class Audio:
    def __init__(self):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.CHUNK = 1024
        self.bitsPerSample = 16
        self.audio = pyaudio.PyAudio()
        self.first_run = True
        self.wav_header = self.genHeader(self.RATE, self.bitsPerSample, self.CHANNELS)
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            input_device_index=1,
            frames_per_buffer=self.CHUNK,
        )

    def genHeader(self, sampleRate, bitsPerSample, channels):
        datasize = 2000 * 10**6
        o = bytes("RIFF", "ascii")
        o += (datasize + 36).to_bytes(4, "little")
        o += bytes("WAVE", "ascii")
        o += bytes("fmt ", "ascii")
        o += (16).to_bytes(4, "little")
        o += (1).to_bytes(2, "little")
        o += (channels).to_bytes(2, "little")
        o += (sampleRate).to_bytes(4, "little")
        o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4, "little")
        o += (channels * bitsPerSample // 8).to_bytes(2, "little")
        o += (bitsPerSample).to_bytes(2, "little")
        o += bytes("data", "ascii")
        o += (datasize).to_bytes(4, "little")
        return o

    def get_audio(self):
        data = self.stream.read(self.CHUNK)
        if self.first_run:
            self.first_run = False
            return self.wav_header + data
        return data
