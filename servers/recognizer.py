import speech_recognition as sr

class Recognizer:
    def __init__(self):
        self.language = "zh-CN"
        self.translator = "en-US"
        self.r = sr.Recognizer()
        self.source = sr.Microphone()
        self.audio = None
        self.text = None
    # 检测静音
    # timeout