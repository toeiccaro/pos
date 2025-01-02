# src/api/camera.py
import cv2

class Camera:
    def __init__(self, video_source=0, rtsp_output_url="rtsp://localhost:8554/live.sdp"):
        self.video_source = video_source
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise Exception(f"Cannot open video source {video_source}")
        
        # RTSP Output Stream setup (Sử dụng OpenCV để phát video qua RTSP)
        self.rtsp_output_url = rtsp_output_url
        fourcc = cv2.VideoWriter_fourcc(*"H264")
        self.out = cv2.VideoWriter(self.rtsp_output_url, fourcc, 20.0, (640, 480))
    
    def get_frame(self):
        """
        Lấy một khung hình từ video source
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        return ret, frame
    
    def send_frame_to_rtsp(self, frame):
        """
        Gửi khung hình đến RTSP stream.
        """
        if frame is not None:
            self.out.write(frame)
    
    def release(self):
        """
        Giải phóng tài nguyên khi không sử dụng nữa
        """
        self.cap.release()
        self.out.release()
