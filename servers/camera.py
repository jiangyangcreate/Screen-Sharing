import time
import cv2
from PIL import ImageGrab, Image
import threading
from io import BytesIO
from greenlet import getcurrent as get_ident

class CameraEvent(object):
    def __init__(self):
        self.events = {}

    def wait(self):
        ident = get_ident()
        if ident not in self.events:
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].is_set():
                event[0].set()
                event[1] = now
            else:
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        self.events[get_ident()][0].clear()


class BaseCamera(object):
    thread = None
    frame = None
    last_access = 0
    event = CameraEvent()

    def __init__(self):
        if BaseCamera.thread is None:
            BaseCamera.last_access = time.time()
            BaseCamera.thread = threading.Thread(target=self._thread)
            BaseCamera.thread.start()
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        BaseCamera.last_access = time.time()
        BaseCamera.event.wait()
        BaseCamera.event.clear()
        return BaseCamera.frame

    @staticmethod
    def frames():
        raise RuntimeError("Must be implemented by subclasses.")

    @classmethod
    def _thread(cls):
        print("Starting camera thread.")
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            BaseCamera.frame = frame
            BaseCamera.event.set()
            time.sleep(0)
            if time.time() - BaseCamera.last_access > 10:
                frames_iterator.close()
                print("Stopping camera thread due to inactivity.")
                break
        BaseCamera.thread = None


class Camera(BaseCamera):
    video_source = 0

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError("Error")
        while True:
            image = ImageGrab.grab()
            image = image.resize((1366, 750), Image.LANCZOS)
            output_buffer = BytesIO()
            image.save(output_buffer, format="JPEG", quality=100)
            frame = output_buffer.getvalue()
            yield frame