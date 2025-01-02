# camera.py

import cv2
import threading

class Camera:
    def __init__(self, video_source=0):
        self.video_source = video_source
        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened():
            raise RuntimeError("Không thể mở webcam")

        # Thiết lập các thuộc tính nếu cần
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.ret = False
        self.frame = None
        self.lock = threading.Lock()
        self.running = True

        # Bắt đầu luồng đọc khung hình
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            with self.lock:
                self.ret = ret
                self.frame = frame

    def get_frame(self):
        with self.lock:
            return self.ret, self.frame.copy() if self.frame is not None else (False, None)

    def __del__(self):
        self.running = False
        self.thread.join()
        if self.cap.isOpened():
            self.cap.release()
