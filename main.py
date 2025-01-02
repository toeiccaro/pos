# main.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import cv2
from src.api.camera import Camera
import subprocess

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Khởi tạo camera với video source là webcam (0 là webcam mặc định)
camera = Camera(video_source=0, rtsp_output_url="rtsp://localhost:8554/live.sdp")

def generate_frames():
    """
    Tạo các khung hình từ webcam để phát trực tuyến qua HTTP
    """
    while True:
        ret, frame = camera.get_frame()
        if not ret:
            continue
        # Mã hóa khung hình thành JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        # Gửi khung hình đến RTSP stream
        camera.send_frame_to_rtsp(frame)
        # Định dạng theo chuẩn multipart
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/webcam", response_class=HTMLResponse)
async def index(request: Request):
    """
    Trang chủ hiển thị video từ webcam
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/export_camera")
async def video_feed():
    """
    Endpoint phát trực tiếp video từ webcam qua HTTP
    """
    return StreamingResponse(generate_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")

# @app.get("/rtsp_feed")
# async def rtsp_feed():
#     """
#     Endpoint phát ra video qua RTSP, API khác có thể gọi vào đây
#     """
#     rtsp_url = "rtsp://localhost:8554/live.sdp"  # Địa chỉ RTSP đã được phát từ OpenCV

#     # Sử dụng FFmpeg để phát video từ FastAPI stream tới RTSP
#     try:
#         # Kiểm tra nếu FFmpeg chưa chạy, khởi động FFmpeg để phát video qua RTSP
#         ffmpeg_process = subprocess.Popen(
#             ["ffmpeg", "-i", "http://localhost:8000/video_feed", "-f", "rtsp", rtsp_url],
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE
#         )
#         return {"rtsp_url": rtsp_url}
#     except Exception as e:
#         return {"error": f"Failed to start RTSP stream: {e}"}
